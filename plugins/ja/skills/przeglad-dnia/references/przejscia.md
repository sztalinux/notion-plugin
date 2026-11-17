# Przejścia po wdrożeniu ja 1.19.0 (idempotentne)

Przebieg nie wie, który jest „pierwszy po wdrożeniu” – warunek przejścia sprawdza stan stron w Notion. Dopóki warunek nie
jest spełniony, przebieg wykonuje przejście, a na końcu wpisuje znacznik. Po znaczniku przejście się nie powtarza.

## 1.1 Stare źródła wpisów → „📝 Wpisy” (przebieg szybki i nocny)

- **Zrobione**, gdy w toggle „Jak używać” strony „📓 Dziennik” stoi zdanie „Piszesz we 📝 Wpisach”.
- **Wykonaj**, gdy zdania brak: raz przerób stare źródła – bloki 1. poziomu Dziennika (poza „Jak używać”, nagłówkami i stałymi
  podstronami) oraz strony z widgetu na najwyższym poziomie Private spoza listy stałych stron (`ja/references/notion-mapa.md`;
  🔒 Prywatne nie otwieraj) – przenosząc je do „📝 Wpisów” jako zwykłe wpisy (blok → na koniec treści Wpisów; strona → jej
  treść jako blok, strona pod „🗃 Przetworzone podstrony”). Wpisy te przetwarzasz normalnie (`wpisy`, kroki 2–7) w tym samym
  przebiegu albo w następnym.
- **Znacznik:** po przeniesieniu wszystkiego dopisz w „Jak używać” zdanie „Piszesz we 📝 Wpisach”. Brak narzędzia do listy stron
  prywatnych → przenieś tylko bloki Dziennika, zdania jeszcze nie wpisuj i odnotuj „widget – brak odczytu” w linii „🤖”.

## 1.2 Sekcja „❓ Czeka na Twoją odpowiedź” → 🔔 (tylko nocny przebieg)

- **Zrobione**, gdy sekcja zawiera wyłącznie zdanie „Pytania są teraz we 📝 Wpisach (🔔)”.
- **Wykonaj**, gdy sekcja ma inne pozycje: przenieś każdą otwartą pozycję do „🔔 Komunikaty asystenta” jako blok 🔔
  (`wpisy/references/pytania.md`, C.7) z zachowaniem zaznaczeń i dopisków oraz klucza (`KS-…`, `RES-n`); w bloku dopisz
  „zastosuję w nocnym przeglądzie”. Pozycje bez klucza (luki w zadaniach) – klucz `luki-zadan-<dd.mm>`.
- **Znacznik:** po przeniesieniu wszystkiego zostaw w sekcji jedno zdanie „Pytania są teraz we 📝 Wpisach (🔔)” (sekcję usuwa
  dopiero faza 6, po 7 dniach bez nowych pozycji). Szybki przebieg tego przejścia **nie robi**.
