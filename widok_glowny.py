from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QPainter
from komponenty import Zbiornik, Pompa, Rura, Grzalka, Zawor

class WidokScada(QFrame):
    def __init__(self):
        super().__init__()
        self.z1 = Zbiornik(60, 100, "Zbiornik Z1")
        self.z2 = Zbiornik(380, 100, "Zbiornik Z2")
        self.z3 = Zbiornik(700, 100, "Zbiornik Z3")
        self.z4 = Zbiornik(1000, 480, "Zbiornik Z4")
        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4]

        self.p1 = Pompa(300, 230)
        self.p2 = Pompa(620, 230)
        self.grzalka = Grzalka(410, 370)
        self.zawor = Zawor(1080, 370)

        self.r1 = Rura([(220, 230), (380, 230)])
        self.r2 = Rura([(540, 230), (700, 230)])
        self.r3 = Rura([(860, 230), (1080, 230), (1080, 480)])

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        self.r1.draw(p)
        self.r2.draw(p)
        self.r3.draw(p)
        self.p1.draw(p)
        self.p2.draw(p)
        self.grzalka.draw(p)
        self.zawor.draw(p)
        for z in self.zbiorniki:
            z.draw(p)