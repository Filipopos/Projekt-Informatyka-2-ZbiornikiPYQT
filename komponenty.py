# komponenty.py
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QBrush, QFont

class Zawor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.czy_otwarty = False

    def draw(self, painter):
        painter.save()
        painter.translate(self.x, self.y)
        painter.setPen(QPen(Qt.gray, 3))
        kolor = QColor(0, 255, 0) if self.czy_otwarty else QColor(255, 0, 0)
        painter.setBrush(QBrush(kolor))
        path = QPainterPath()
        path.moveTo(-25, -20)
        path.lineTo(25, 20)
        path.lineTo(25, -20)
        path.lineTo(-25, 20)
        path.closeSubpath()
        painter.drawPath(path)
        painter.restore()

class Grzalka:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.czy_grzeje = False

    def draw(self, painter):
        painter.save()
        painter.translate(self.x, self.y)
        painter.setPen(QPen(Qt.gray, 3))
        kolor_grzania = QColor(255, 0, 0) if self.czy_grzeje else QColor(80, 80, 80)
        painter.setBrush(QBrush(kolor_grzania))
        painter.drawRect(0, 0, 100, 25)
        painter.restore()

class Pompa:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kat = 0
        self.czy_pracuje = False

    def draw(self, painter):
        painter.save()
        painter.translate(self.x, self.y)
        painter.setPen(QPen(Qt.gray, 3))
        painter.setBrush(QBrush(QColor(40, 40, 40)))
        painter.drawEllipse(-35, -35, 70, 70)
        if self.czy_pracuje:
            self.kat += 20
        painter.rotate(self.kat)
        painter.setPen(QPen(Qt.white, 4))
        painter.drawLine(0, -30, 0, 30)
        painter.drawLine(-30, 0, 30, 0)
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
        painter.setPen(QPen(QColor(60, 60, 60), 20, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(path)
        if self.czy_plynie:
            painter.setPen(QPen(QColor(0, 140, 255), 12, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(path)

class Zbiornik:
    def __init__(self, x, y, nazwa):
        self.x = x
        self.y = y
        self.w = 160
        self.h = 260
        self.nazwa = nazwa
        self.poziom = 0.0
        self.temp = 20.0

    def draw(self, painter):
        if self.poziom > 0.1:
            h_c = (self.h - 4) * (self.poziom / 100.0)
            painter.setBrush(QBrush(QColor(0, 100, 200, 200)))
            painter.setPen(Qt.NoPen)
            painter.drawRect(int(self.x + 2), int(self.y + self.h - h_c - 2), int(self.w - 4), int(h_c))
        painter.setPen(QPen(Qt.lightGray, 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.x, self.y, self.w, self.h)
        font = QFont('Arial', 12, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.x, self.y - 15, self.nazwa)
        painter.drawText(self.x + 5, self.y + self.h + 25, f"{max(0, int(self.poziom))}% | {round(self.temp, 1)}°C")