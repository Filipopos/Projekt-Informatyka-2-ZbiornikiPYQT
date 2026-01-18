# Dokumentacja Projektu 

# 1. Wstęp
Projekt ten stanowi implementację prototypu systemu SCADA służącego do monitorowania i wizualizacji przepływu cieczy. Aplikacja została opracowana w języku Python z wykorzystaniem biblioteki graficznej PyQt5 oraz biblioteki pytest.

# 2. Charakterystyka Funkcjonalna
System realizuje symulację procesu technologicznego obejmującego cztery zbiorniki oraz układ pomp, rurociągów zaworu i grzałki. Główne funkcjonalności obejmują:

- Symulacja fizyczna(mieszanie temperatur, 
- Monitorowanie w czasie rzeczywistym Dynamiczna wizualizacja poziomów cieczy oraz stanu pracy urządzeń wykonawczych (pomp).
- Dwuekranowy interfejs operatora:
  * Moduł Wizualizacji: Graficzny schemat z animacją procesów.
  * Moduł Diagnostyki: Precyzyjne odczyty cyfrowe oraz rejestr zdarzeń systemowych.
- Zautomatyzowana i ręczną logikaę przepływu:
  * Tryb Auto: Algorytm zarządza przepływem w oparciu o progi bezpieczeństwa
  * Tryb Manualny: Pozwala na ręczne wymuszanie stanów urządzeń przez operatora z zachowaniem blokad bezpieczeństwa.

 # 3. Jakość kodu: 
- Zgodnie z zasadą czystego kodu, projekt został podzielony na niezależne moduły: "style.qss", "main.py", "widok_glowny.py", "komponenty.py" oraz "test_procesu.py".
- Wykorzystano mechanizm flag binarnych do monitorowania przejść stanów procesowych. Eliminuje to powtarzanie się komunikatów w oknie alertów.
- Proces sterowany jest zegarem systemowym o częstotliwości odświeżania 20 Hz, co zapewnia płynność animacji i stabilność obliczeń.

# 4. Struktura Projektu
* main.py: Zarządzanie logiką procesu, obsługa zdarzeń i sterowanie interfejsem.
* widok_glowny.py: Definicja makiety graficznej i kompozycja elementów.
* komponenty.py: Klasy obiektowe urządzeń wykonawczych (Zbiorniki, Pompy, Zawory) z własną logiką rysowania.
* style.qss: Zewnętrzny arkusz stylów oparty na czcionce **Arial**, oddzielający warstwę wizualną od logicznej.
* test_procesu.py: Klasa odpowiedzialna za przeprowadzenie testów mechaniki odpowiedzialnej za mieszanie wody w zbiornikach

# 5. Testowanie Oprogramowania (pytest)
Zgodnie z wymaganiami akademickimi, aplikacja została poddana testom jednostkowym z wykorzystaniem frameworka "pytest". Dokumentacja testowa obejmuje:
* Mechanizm Fixtures: Wykorzystanie dekoratorów "@pytest.fixture" do izolacji danych i dostarczania "czystych" obiektów przed każdym testem.
* Parametryzacja: Automatyczna weryfikacja wielu scenariuszy mieszania temperatur przy użyciu "@pytest.mark.parametrize".
* Weryfikacja Stanu: Testowanie logiki (np. czy temperatura nie przekracza zadanych granic).

# 5. Wymagania i Uruchomienie
Do poprawnego działania aplikacji wymagane jest środowisko Python 3.14, biblioteka PyQt5 oraz pytest. Pliki style.ssq, main.py, widok_glowny.py, komponenty.py oraz test_procesy.py muszą znajdować się w tym samym folderze.

# 6. Logika sterowania
Sercem aplikacji jest metoda logika_procesu, działająca w pętli zamkniętej, wykonującej się co 50ms. W każdym cyklu system wykonuje następujące operacje:
-Pobranie aktualnych wartości poziomów z obiektów klasy Zbiornik.
-Weryfikacja warunków logicznych dla pracy pomp, grzałki oraz zaworu.
-Aktualizacja stanów obiektów graficznych i zmiennych procesowych.
-Przekazanie zdarzeń do modułu rejestracji, o ile nastąpiła zmiana stanu urządzenia.
-Wymuszenie odświeżenia warstwy prezentacji.

# Autor: 
Filip Rostek; 
Automatyka, Robotyka i Systemy Sterowania,
Wydział Elektrotechniki i Automatyki
