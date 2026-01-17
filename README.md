# Dokumentacja Projektu 

# 1. Wstęp
Projekt ten stanowi implementację prototypu systemu SCADA służącego do monitorowania i wizualizacji przepływu cieczy w układzie kaskadowym. Aplikacja została opracowana w języku Python z wykorzystaniem biblioteki graficznej PyQt5.

# 2. Charakterystyka Funkcjonalna
System realizuje symulację procesu technologicznego obejmującego cztery zbiorniki oraz układ pomp i rurociągów. Główne funkcjonalności obejmują:

- Monitorowanie w czasie rzeczywistym Dynamiczna wizualizacja poziomów cieczy oraz stanu pracy urządzeń wykonawczych (pomp).
- Dwuekranowy interfejs operatora:
  * Moduł Wizualizacji: Graficzny schemat z animacją procesów.
  * Moduł Diagnostyki: Precyzyjne odczyty cyfrowe oraz rejestr zdarzeń systemowych.
- Zautomatyzowana logika przepływu:
    * Uzależnienie pracy Pompy P1 od dostępności cieczy w zbiorniku Z1.
    * Warunkowe uruchomienie Pompy P2 po przekroczeniu progu bezpieczeństwa (35%) w zbiorniku Z2.
    * Symulacja spływu grawitacyjnego do zbiornika Z4.

 # 3. Jakość kodu: 
- Zgodnie z zasadą czystego kodu, definicje stylów wizualnych zostały wyodrębnione do zewnętrznego arkusza "style.qss".
- Wykorzystano mechanizm flag binarnych do monitorowania przejść stanów procesowych. Eliminuje to powtarzanie się komunikatów w oknie alertów.
- Proces sterowany jest zegarem systemowym o częstotliwości odświeżania 20 Hz, co zapewnia płynność animacji i stabilność obliczeń.

# 4. Struktura Projektu
* main.py – Główny moduł aplikacji zawierający definicje klas obiektów, logikę sterowania oraz konfigurację interfejsu.
* style.qss – Arkusz stylów definiujący warstwę wizualną aplikacji (kolorystyka, typografia, style widżetów).
* README.md – Dokumentacja techniczna projektu.

# 5. Wymagania i Uruchomienie
Do poprawnego działania aplikacji wymagane jest środowisko Python 3.x oraz biblioteka PyQt5. Pliki style.ssq oraz main.py muszą znajdować się w tym samym folderze

# 6. Logika sterowania
Sercem aplikacji jest metoda logika_procesu, działająca w pętli zamkniętej, wykonującej się co 50ms. W każdym cyklu system wykonuje następujące operacje:
-Pobranie aktualnych wartości poziomów z obiektów klasy Zbiornik.
-Weryfikacja warunków logicznych dla pracy pomp.
-Aktualizacja stanów obiektów graficznych i zmiennych procesowych.
-Przekazanie zdarzeń do modułu rejestracji, o ile nastąpiła zmiana stanu urządzenia.
-Wymuszenie odświeżenia warstwy prezentacji.

# Autor: 
Filip Rostek; 
Automatyka, Robotyka i Systemy Sterowania,
Wydział Elektrotechniki i Automatyki
