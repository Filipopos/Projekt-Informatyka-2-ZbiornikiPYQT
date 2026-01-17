import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QSlider, QLabel, QGroupBox, QFrame,
                             QStackedWidget, QListWidget, QListWidgetItem, QLCDNumber)
from PyQt5.QtCore import Qt, QTimer, QPointF, QDateTime
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QBrush

#style interfejsu
def load_stylesheet(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
            return f.read()

class Pompa:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kat = 0
        self.czy_pracuje = False

    def draw(self, painter):
        painter.save()
        painter.translate(self.x, self.y)
        painter.setPen(QPen(Qt.gray, 2))
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawEllipse(-20, -20, 40, 40)

        if self.czy_pracuje:
            self.kat += 20

        painter.rotate(self.kat)
        painter.setPen(QPen(Qt.white, 3))
        painter.drawLine(0, -15, 0, 15)
        painter.drawLine(-15, 0, 15, 0)
        painter.restore()


class Rura:
    def __init__(self, punkty):
        self.punkty = [QPointF(p[0], p[1]) for p in punkty]
        self.czy_plynie = False

    def draw(self, painter):
        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)

        painter.setPen(QPen(QColor(60, 60, 60), 10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(path)

        if self.czy_plynie:
            painter.setPen(QPen(QColor(0, 140, 255), 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(path)


class Zbiornik:
    def __init__(self, x, y, nazwa):
        self.x = x
        self.y = y
        self.w = 70
        self.h = 110
        self.nazwa = nazwa
        self.poziom = 0.0

    def draw(self, painter):
        if self.poziom > 0.1:
            h_c = (self.h - 4) * (self.poziom / 100.0)
            painter.setBrush(QBrush(QColor(0, 100, 200, 200)))
            painter.setPen(Qt.NoPen)
            painter.drawRect(int(self.x + 2), int(self.y + self.h - h_c - 2), int(self.w - 4), int(h_c))

        painter.setPen(QPen(Qt.lightGray, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.x, self.y, self.w, self.h)
        painter.drawText(self.x, self.y - 10, self.nazwa)
        painter.drawText(self.x + 5, self.y + self.h + 20, f"{max(0, int(self.poziom))}%")


class WidokScada(QFrame):
    def __init__(self):
        super().__init__()
        self.z1 = Zbiornik(50, 100, "Zbiornik Z1")
        self.z2 = Zbiornik(220, 100, "Zbiornik Z2")
        self.z3 = Zbiornik(390, 100, "Zbiornik Z3")
        self.z4 = Zbiornik(600, 350, "Zbiornik Z4")
        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4]

        self.p1 = Pompa(175, 155)
        self.p2 = Pompa(345, 155)

        self.r1 = Rura([(120, 155), (220, 155)])
        self.r2 = Rura([(290, 155), (390, 155)])
        self.r3 = Rura([(460, 155), (530, 155), (530, 300), (635, 300), (635, 350)])

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        self.r1.draw(p)
        self.r2.draw(p)
        self.r3.draw(p)
        self.p1.draw(p)
        self.p2.draw(p)
        for z in self.zbiorniki:
            z.draw(p)


class AplikacjaScada(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zbiorniki-projekt Informatyka")

        try:
            style = load_stylesheet("style.qss")
            self.setStyleSheet(style)
        except Exception as e:
            print(f"Blad wczytywania stylu: {e}")

        self.running = False

        # Flagi do wyswietlacza
        self.p1_czy_wczesniej_chodzila = False
        self.p2_czy_wczesniej_chodzila = False
        self.z1_czy_byl_juz_alarm = False

        self.init_ui()
        self.timer = QTimer()
        #za każdym minięciem 50ms wywołuje funkcję logika_procesu
        self.timer.timeout.connect(self.logika_procesu)
    def init_ui(self):
        vbox = QVBoxLayout(self)

        # Przelaczanie pomiadzy oknami
        nav = QHBoxLayout()
        self.btn_ekran1 = QPushButton("WIZUALIZACJA")
        self.btn_ekran1.setObjectName("nav_active")
        self.btn_ekran2 = QPushButton("DIAGNOSTYKA")

        self.btn_ekran1.clicked.connect(lambda: self.zmien_strone(0))
        self.btn_ekran2.clicked.connect(lambda: self.zmien_strone(1))

        nav.addWidget(self.btn_ekran1)
        nav.addWidget(self.btn_ekran2)
        nav.addStretch()
        vbox.addLayout(nav)
        #aby jedna strona byla ukryta pod druga
        self.stack = QStackedWidget()

        # Strona 1 - Widok graficzny
        self.page1 = QWidget()
        l1 = QHBoxLayout(self.page1)
        self.v_scada = WidokScada()
        l1.addWidget(self.v_scada, 4)

        ctrl = QVBoxLayout()
        self.sliders = []
        for i in range(4):
            ctrl.addWidget(QLabel(f"Poziom Z{i + 1}:"))
            s = QSlider(Qt.Horizontal)
            s.setRange(0, 100)
            #aktualizacja wody w zbiornikach jeszcze przed uruchomieniem symulacji
            s.valueChanged.connect(self.aktualizuj_z_suwakow)
            self.sliders.append(s)
            ctrl.addWidget(s)

        self.btn_start = QPushButton("START")
        self.btn_start.clicked.connect(self.start_stop)
        ctrl.addWidget(self.btn_start)
        ctrl.addStretch()
        l1.addLayout(ctrl, 1)

        # Strona 2 - Diagnostyka
        self.page2 = QWidget()
        l2 = QHBoxLayout(self.page2)

        self.lcds = []
        lcd_box = QVBoxLayout()
        lcd_box.addWidget(QLabel("<h1>ODCZYTY [%]</h1>"))
        for i in range(4):
            lcd = QLCDNumber()
            lcd.setDigitCount(5)
            lcd.setMinimumHeight(50)
            self.lcds.append(lcd)
            lcd_box.addWidget(lcd)
        l2.addLayout(lcd_box, 1)

        self.list_logs = QListWidget()
        l2.addWidget(self.list_logs, 2)

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        vbox.addWidget(self.stack)

    def zmien_strone(self, i):
        self.stack.setCurrentIndex(i)
        if i == 0:
            self.btn_ekran1.setObjectName("nav_active")
            self.btn_ekran2.setObjectName("")
        else:
            self.btn_ekran1.setObjectName("")
            self.btn_ekran2.setObjectName("nav_active")
        try:
            style = load_stylesheet("style.qss")
            self.setStyleSheet(style)
        except Exception as e:
            print(f"Blad wczytywania stylu: {e}")

    def aktualizuj_z_suwakow(self):
        if not self.running:
            for i, z in enumerate(self.v_scada.zbiorniki):
                z.poziom = self.sliders[i].value()
                self.lcds[i].display(z.poziom)
            self.v_scada.update()

    def start_stop(self):
        self.running = not self.running
        if self.running:
            self.btn_start.setText("STOP")
            self.timer.start(50)
            self.dodaj_wiadomosc("--- START SYMULACJI ---", "#00ff00")
        else:
            self.btn_start.setText("START")
            self.timer.stop()
            self.dodaj_wiadomosc("--- STOP SYMULACJI ---", "#ffaa00")

    def dodaj_wiadomosc(self, tekst, kolor="#ffffff"):
        czas = QDateTime.currentDateTime().toString("hh:mm:ss")
        item = QListWidgetItem(f"[{czas}] {tekst}")
        item.setForeground(QColor(kolor))
        self.list_logs.insertItem(0, item)

    def logika_procesu(self):
        v = self.v_scada
        step = 0.5

        # Z1 -> Z2
        pompuj1 = v.z1.poziom > 0 and v.z2.poziom < 100
        if pompuj1:
            v.z1.poziom -= step
            v.z2.poziom += step

        v.p1.czy_pracuje = pompuj1
        v.r1.czy_plynie = pompuj1

        if pompuj1 and not self.p1_czy_wczesniej_chodzila:
            self.dodaj_wiadomosc("Pompa P1: Rozpoczęto pompowanie")
            self.p1_czy_wczesniej_chodzila = True
        elif not pompuj1 and self.p1_czy_wczesniej_chodzila:
            self.dodaj_wiadomosc("Pompa P1: Zatrzymano")
            self.p1_czy_wczesniej_chodzila = False

        if v.z1.poziom <= 0 and not self.z1_czy_byl_juz_alarm:
            self.dodaj_wiadomosc("ALARM: Zbiornik Z1 jest pusty!", "#ff0000")
            self.z1_czy_byl_juz_alarm = True
        elif v.z1.poziom > 0:
            self.z1_czy_byl_juz_alarm = False

        # Z2 -> Z3
        pompuj2 = v.z2.poziom > 35 and v.z3.poziom < 100
        if pompuj2:
            v.z2.poziom -= step
            v.z3.poziom += step

        v.p2.czy_pracuje = pompuj2
        v.r2.czy_plynie = pompuj2

        if pompuj2 and not self.p2_czy_wczesniej_chodzila:
            self.dodaj_wiadomosc("Pompa P2: Rozpoczęto pompowanie(>35%)")
            self.p2_czy_wczesniej_chodzila = True
        elif not pompuj2 and self.p2_czy_wczesniej_chodzila:
            self.dodaj_wiadomosc("Pompa P2: Zatrzymano")
            self.p2_czy_wczesniej_chodzila = False

        # Z3 -> Z4 (grawitacja)
        plynie = v.z3.poziom > 0 and v.z4.poziom < 100
        if plynie:
            v.z3.poziom -= step
            v.z4.poziom += step

        v.r3.czy_plynie = plynie

        # Aktualizacja odczytów
        for i, z in enumerate(v.zbiorniki):
            self.lcds[i].display(round(max(0, z.poziom), 1))

        v.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AplikacjaScada()
    win.showMaximized()
    sys.exit(app.exec_())