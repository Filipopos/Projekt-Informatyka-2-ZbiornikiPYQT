import pytest
import sys
from PyQt5.QtWidgets import QApplication
from komponenty import Zbiornik
from main import AplikacjaScada


#Tworzy instancję QApplication wymaganą przez PyQt5
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


#Dostarcza obiekt do każdego testu
@pytest.fixture
def zbiornik_testowy():
    z = Zbiornik(0, 0, "Testowy")
    z.poziom = 10.0
    z.temp = 20.0
    return z


# PARAMETRYZACJA: Testuje różne scenariusze jednym kodem
@pytest.mark.parametrize("temp_zrodla, step, oczekiwana_temp", [
    (20.0, 5.0, 20.0),  # Przypadek 1: Ta sama temperatura
    (80.0, 10.0, 50.0),  # Przypadek 2: Mieszanie pół na pół
    (100.0, 0.0, 20.0)  # Przypadek 3: Brak dolania
])
def test_mieszania_temperatury(qapp, zbiornik_testowy, temp_zrodla, step, oczekiwana_temp):
    app = AplikacjaScada()
    app.mieszaj_temp(zbiornik_testowy, temp_zrodla, step)
    #wynik przyblizony, żeby błędy w zaokrągleniach nie wyrzucąły błędów
    assert zbiornik_testowy.temp == pytest.approx(oczekiwana_temp, rel=1e-2)