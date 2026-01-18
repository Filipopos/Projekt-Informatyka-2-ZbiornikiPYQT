import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QSlider, QLabel, QGroupBox,
                             QStackedWidget, QListWidget, QListWidgetItem, QLCDNumber, QCheckBox)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QColor

from widok_glowny import WidokScada


def load_stylesheet(file_path):
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Błąd odczytu pliku stylu: {e}")
        return ""


class AplikacjaScada(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zbiorniki - Projekt Informatyka")

        # Wczytanie stylu
        self.odswiez_styl()

        self.running = False
        self.tryb_auto = True

        # Flagi stanów
        self.p1_czy_wczesniej_chodzila = False
        self.p2_czy_wczesniej_chodzila = False
        self.grzalka_czy_wczesniej_chodzila = False
        self.zawor_czy_wczesniej_otwarty = False
        self.z1_czy_byl_juz_alarm = False
        self.z2_czy_byl_alarm_temp = False

        self.interf_uz()

        # Zegar procesu
        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_procesu)

    def odswiez_styl(self):
        styl = load_stylesheet("style.qss")
        self.setStyleSheet(styl)

    def interf_uz(self):
        vbox = QVBoxLayout(self)

        # Górne menu
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

        self.stack = QStackedWidget()

        # --- STRONA 1: WIZUALIZACJA I STEROWANIE ---
        self.page1 = QWidget()
        l1 = QHBoxLayout(self.page1)
        self.v_scada = WidokScada()
        l1.addWidget(self.v_scada, 5)

        ctrl = QVBoxLayout()

        # Wybór trybu
        self.check_auto = QCheckBox("TRYB AUTOMATYCZNY")
        self.check_auto.setChecked(True)
        self.check_auto.stateChanged.connect(self.przestaw_tryb)
        ctrl.addWidget(self.check_auto)

        # Przyciski manualne
        self.group_reczny = QGroupBox("Panel Manualny")
        self.group_reczny.setEnabled(False)
        reczny_layout = QVBoxLayout()
        self.btn_p1 = QPushButton("Pompa P1")
        self.btn_p1.setCheckable(True)
        self.btn_p2 = QPushButton("Pompa P2")
        self.btn_p2.setCheckable(True)
        self.btn_grzalka = QPushButton("Grzałka")
        self.btn_grzalka.setCheckable(True)
        self.btn_zawor = QPushButton("Zawór Z3-Z4")
        self.btn_zawor.setCheckable(True)
        reczny_layout.addWidget(self.btn_p1)
        reczny_layout.addWidget(self.btn_p2)
        reczny_layout.addWidget(self.btn_grzalka)
        reczny_layout.addWidget(self.btn_zawor)
        self.group_reczny.setLayout(reczny_layout)
        ctrl.addWidget(self.group_reczny)

        # Sekcja suwaków
        ctrl.addWidget(QLabel("PARAMETRY POCZĄTKOWE"))
        self.sliders = []
        for i in range(4):
            ctrl.addWidget(QLabel(f"Ustaw Poziom Z{i + 1} [%]:"))
            s = QSlider(Qt.Horizontal)
            s.setRange(0, 100)
            s.valueChanged.connect(self.aktualizuj_z_suwakow)
            self.sliders.append(s)
            ctrl.addWidget(s)

        self.btn_start = QPushButton("URUCHOM SYSTEM")
        self.btn_start.clicked.connect(self.start_stop)
        ctrl.addWidget(self.btn_start)
        ctrl.addStretch()
        l1.addLayout(ctrl, 1)

        # --- STRONA 2: DIAGNOSTYKA I LOGI ---
        self.page2 = QWidget()
        l2 = QHBoxLayout(self.page2)
        self.lcds = []
        lcd_box = QVBoxLayout()
        lcd_box.addWidget(QLabel("<h1>ODCZYT CZUJNIKÓW</h1>"))
        for i in range(4):
            lcd_box.addWidget(QLabel(f"Poziom Z{i + 1} [%]"))
            lcd = QLCDNumber()
            lcd.setDigitCount(5)
            lcd.setMinimumHeight(45)
            self.lcds.append(lcd)
            lcd_box.addWidget(lcd)

        lcd_box.addWidget(QLabel("Temp. Z2 [°C]"))
        self.lcd_t2 = QLCDNumber()
        self.lcd_t2.setDigitCount(5)
        self.lcd_t2.setMinimumHeight(45)
        lcd_box.addWidget(self.lcd_t2)

        lcd_box.addWidget(QLabel("Temp. Z4 [°C]"))
        self.lcd_t4 = QLCDNumber()
        self.lcd_t4.setDigitCount(5)
        self.lcd_t4.setMinimumHeight(45)
        lcd_box.addWidget(self.lcd_t4)

        l2.addLayout(lcd_box, 1)
        self.list_logs = QListWidget()
        l2.addWidget(self.list_logs, 2)

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        vbox.addWidget(self.stack)

    def przestaw_tryb(self):
        self.tryb_auto = self.check_auto.isChecked()
        self.group_reczny.setEnabled(not self.tryb_auto)
        self.dodaj_wiadomosc(f"Zmiana trybu: {'AUTO' if self.tryb_auto else 'RĘCZNY'}")

    def zmien_strone(self, i):
        self.stack.setCurrentIndex(i)
        self.btn_ekran1.setObjectName("nav_active" if i == 0 else "")
        self.btn_ekran2.setObjectName("nav_active" if i == 1 else "")
        self.odswiez_styl()

    def aktualizuj_z_suwakow(self):
        if not self.running:
            for i, z in enumerate(self.v_scada.zbiorniki):
                z.poziom = self.sliders[i].value()
                z.temp = 20.0
                self.lcds[i].display(z.poziom)
            self.v_scada.update()

    def start_stop(self):
        self.running = not self.running
        self.btn_start.setText("ZATRZYMAJ SYSTEM" if self.running else "URUCHOM SYSTEM")
        if self.running:
            self.timer.start(50)
            self.dodaj_wiadomosc("--- SYSTEM URUCHOMIONY ---", "#00ff00")
        else:
            self.timer.stop()
            self.dodaj_wiadomosc("--- SYSTEM ZATRZYMANY ---", "#ffaa00")

    def dodaj_wiadomosc(self, tekst, kolor="#ffffff"):
        czas = QDateTime.currentDateTime().toString("hh:mm:ss")
        item = QListWidgetItem(f"[{czas}] {tekst}")
        item.setForeground(QColor(kolor))
        self.list_logs.insertItem(0, item)

    def mieszaj_temp(self, z_cel, temp_zrodla, step):
        if z_cel.poziom + step > 0:
            z_cel.temp = ((z_cel.poziom * z_cel.temp) + (step * temp_zrodla)) / (z_cel.poziom + step)

    def logika_procesu(self):
        v = self.v_scada
        step = 0.5

        # CHŁODZENIE PASYWNE
        for z in v.zbiorniki:
            if z.temp > 20.0:
                z.temp -= 0.025
            if z.temp < 20.0:
                z.temp = 20.0

        #PRZEPŁYW Z1 -> Z2 (Pompa P1)
        pompuj1 = v.z1.poziom > 0 and v.z2.poziom < 100
        if not self.tryb_auto:
            pompuj1 = pompuj1 and self.btn_p1.isChecked()
        if pompuj1:
            self.mieszaj_temp(v.z2, v.z1.temp, step)
            v.z1.poziom -= step
            v.z2.poziom += step

        v.p1.czy_pracuje = v.r1.czy_plynie = pompuj1
        if pompuj1 != self.p1_czy_wczesniej_chodzila:
            self.dodaj_wiadomosc(f"Pompa P1: {'START' if pompuj1 else 'STOP'}")
            self.p1_czy_wczesniej_chodzila = pompuj1

        #GRZAŁKA Z2
        if v.z2.temp >= 90 and not self.z2_czy_byl_alarm_temp:
            self.dodaj_wiadomosc("ALARM: Z2 osiągnął 90°C! Blokada grzania.", "#ff0000")
            self.z2_czy_byl_alarm_temp = True
        elif v.z2.temp < 85 and self.z2_czy_byl_alarm_temp:
            self.dodaj_wiadomosc("Info: Temperatura Z2 < 85°C. Grzanie odblokowane.", "#aaaaff")
            self.z2_czy_byl_alarm_temp = False

        if self.tryb_auto:
            chce_grzac = v.z2.poziom > 40 and not self.z2_czy_byl_alarm_temp
        else:
            chce_grzac = self.btn_grzalka.isChecked() and v.z2.poziom > 40 and not self.z2_czy_byl_alarm_temp

        v.grzalka.czy_grzeje = chce_grzac
        if chce_grzac:
            v.z2.temp += 0.4
        if chce_grzac != self.grzalka_czy_wczesniej_chodzila:
            self.dodaj_wiadomosc(f"Grzałka: {'START' if chce_grzac else 'STOP'}", "#ff5555")
            self.grzalka_czy_wczesniej_chodzila = chce_grzac

        # 3. PRZEPŁYW Z2 -> Z3 (Pompa P2)
        pompuj2 = v.z2.poziom > (35 if self.tryb_auto else 0) and v.z3.poziom < 100
        if not self.tryb_auto:
            pompuj2 = v.z2.poziom > 0 and v.z3.poziom < 100 and self.btn_p2.isChecked()
        if pompuj2:
            self.mieszaj_temp(v.z3, v.z2.temp, step)
            v.z2.poziom -= step
            v.z3.poziom += step

        v.p2.czy_pracuje = v.r2.czy_plynie = pompuj2
        if pompuj2 != self.p2_czy_wczesniej_chodzila:
            self.dodaj_wiadomosc(f"Pompa P2: {'START' if pompuj2 else 'STOP'}")
            self.p2_czy_wczesniej_chodzila = pompuj2

        # 4. ZAWÓR I PRZEPŁYW Z3 -> Z4
        if self.tryb_auto:
            v.zawor.czy_otwarty = v.z3.poziom > 10
        else:
            v.zawor.czy_otwarty = self.btn_zawor.isChecked()

        if v.zawor.czy_otwarty != self.zawor_czy_wczesniej_otwarty:
            self.dodaj_wiadomosc(f"Zawór: {'OTWARTY' if v.zawor.czy_otwarty else 'ZAMKNIĘTY'}", "#aaaaff")
            self.zawor_czy_wczesniej_otwarty = v.zawor.czy_otwarty

        plynie = v.z3.poziom > 0 and v.z4.poziom < 100 and v.zawor.czy_otwarty
        if plynie:
            self.mieszaj_temp(v.z4, v.z3.temp, step)
            v.z3.poziom -= step
            v.z4.poziom += step
        v.r3.czy_plynie = plynie

        # ALARM PUSTEGO ZBIORNIKA
        if v.z1.poziom <= 0 and not self.z1_czy_byl_juz_alarm:
            self.dodaj_wiadomosc("ALARM: Z1 jest pusty!", "#ff0000")
            self.z1_czy_byl_juz_alarm = True
        elif v.z1.poziom > 0:
            self.z1_czy_byl_juz_alarm = False

        # AKTUALIZACJA INTERFEJSU
        for i, z in enumerate(v.zbiorniki):
            self.lcds[i].display(round(max(0, z.poziom), 1))

        self.lcd_t2.display(round(v.z2.temp, 1))
        self.lcd_t4.display(round(v.z4.temp, 1))
        v.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AplikacjaScada()
    win.showMaximized()
    sys.exit(app.exec_())