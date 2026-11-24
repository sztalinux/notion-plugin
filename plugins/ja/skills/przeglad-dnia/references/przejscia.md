# Przejścia po wdrożeniu ja 1.19.0 (idempotentne)

Przebieg nie wie, który jest „pierwszy po wdrożeniu” – warunek przejścia sprawdza stan stron w Notion. Dopóki warunek nie
jest spełniony, przebieg wykonuje przejście, a na końcu wpisuje znacznik. Po znaczniku przejście się nie powtarza.

## 1.1 Stare źródła wpisów → „📝 Wpisy” (tylko nocny przebieg)

- **Zrobione**, gdy w toggle „Jak używać” strony „📓 Dziennik” stoi zdanie „Piszesz we 📝 Wpisach”.
- **Wykonaj**, gdy zdania brak: raz przerób stare źródła – bloki 1. poziomu Dziennika (poza „Jak używać”, nagłówkami i stałymi
  podstronami) oraz strony z widgetu na najwyższym poziomie Private spoza listy stałych stron (`ja/references/notion-mapa.md`;
  🔒 Prywatne nie otwieraj) – przenosząc je do „📝 Wpisów” jako zwykłe wpisy (blok → na koniec treści Wpisów; strona → jej
  treść jako blok, strona pod „🗃 Przetworzone podstrony”). Wpisy te przetwarzasz normalnie (`wpisy`, kroki 2–7) w tym samym
  przebiegu albo w następnym.
- **Znacznik:** po przeniesieniu wszystkiego dopisz w „Jak używać” zdanie „Piszesz we 📝 Wpisach”. Brak narzędzia do listy stron
  prywatnych → przenieś tylko bloki Dziennika, znacznik wpisz mimo to (przejście nie powtarza się) i dodaj blok 🔔 `przejscie-widget`:
  „nie odczytałem stron z widgetu – sprawdź, czy na najwyższym poziomie Private nie zostały nowe wpisy”.

## 1.2 Sekcja „❓ Czeka na Twoją odpowiedź” → 🔔 (tylko nocny przebieg)

- **Zrobione**, gdy sekcja zawiera wyłącznie zdanie „Pytania są teraz we 📝 Wpisach (🔔)”.
- **Wykonaj**, gdy sekcja ma inne pozycje: przenieś każdą otwartą pozycję do „🔔 Komunikaty asystenta” jako blok 🔔
  (`wpisy/references/pytania.md`, C.7) z zachowaniem zaznaczeń i dopisków oraz klucza (`KS-…`, `RES-n`); w bloku dopisz
  „zastosuję w nocnym przeglądzie”. Klucz brakujący: luki w zadaniach `luki-zadan-<dd.mm>`, porządki tygodnia `porzadki-<RRRR-Www>`, pozostałe `stare-<dd.mm>`.
- **Znacznik:** po przeniesieniu wszystkiego zostaw w sekcji jedno zdanie „Pytania są teraz we 📝 Wpisach (🔔)” (sekcję usuwa
  przejście 1.3). Szybki przebieg tego przejścia **nie robi**.

## 1.3 Usunięcie sekcji „❓ Czeka na Twoją odpowiedź” (tylko nocny przebieg)

- **Zrobione**, gdy w Dzienniku nie ma nagłówka „❓ Czeka na Twoją odpowiedź” – brak sekcji jest znacznikiem.
- **Wykonaj**, gdy sekcja zawiera wyłącznie zdanie-znacznik 1.2: usuń nagłówek razem z tym zdaniem w tej samej edycji
  Dziennika co linia „🤖” (`przeglad-dnia`, B.9; `wpisy`, krok 7). Sekcja z innymi pozycjami → najpierw 1.2, usunięcie
  w następnym przebiegu. Warunek nie liczy dni – sekcja nie ma własnej daty, a znacznik 1.2 stoi od migracji.
