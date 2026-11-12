# Dziennik budowy w Notion – schemat

Stan: obowiązuje od 1.0.0. Baza pod stroną DOM.

## Baza „Dziennik budowy” – `collection://cc113d57-3eaa-4f52-80f6-e4b39a4b4c92`

| Pole | Typ | Wartości / uwagi |
|---|---|---|
| Wpis | tytuł | `RRRR-MM-DD – <etap> – <krok w 3 słowach>` |
| Data | data | dzień na budowie |
| Etap | select | jak w Notatniku: Projekt i formalności, Stan zero, SSO, Deweloperski, Wykończenie, Teren i ogród, Cała budowa |
| Krok | tekst | np. „zbrojenie ścian piwnicy”, „murowanie parteru – ściana wschodnia” |
| Kto | multi-select | Ekipa, Ja, Kierownik budowy, Geotechnik, Geodeta, Instalator, Dostawa, Inspektor / urząd |
| Ekipa – osób | liczba | |
| Godziny własne | liczba | praca inwestora tego dnia |
| Pogoda | tekst | temperatura, opady, wiatr – ważne przy betonie, murowaniu, zasypce |
| Zrobione | tekst | konkretnie, z miejscem (oś, ściana, kondygnacja) |
| Dostawy | tekst | co, ile, od kogo, nr WZ; kwoty idą do kolejki „💸 Wydatki → arkusz” (`koszty` B) |
| Problemy / usterki | tekst | co, gdzie, zdjęcie, ustalona reakcja |
| Ustalenia z ekipą | tekst | kto, co, do kiedy – jeśli trwałe → Notatnik |
| Roboty dodatkowe | tekst | co, cena netto/brutto, czy uzgodnione na piśmie |
| Zdjęcia | tekst | `<łącznie> zdj.: <NN Krok> (<n>) <link folderu na Dysku>; …` – liczba na początku (pulpit); od dom-budowa 3.11.0 |
| Krok harmonogramu | relacja → Harmonogram (zwrotna „Dziennik budowy”) | kroki, których dotyczy dzień i w których przybyły zdjęcia |
| Ujęcia przed zakryciem | tekst | które ujęcia z listy `etap` B są w `przed zakryciem/`, których brakuje |
| Przed zakryciem OK | checkbox | tylko przy komplecie ujęć z miarą dla elementów, które ten krok zakrywa |
| Dokumenty z dnia | tekst | linki do faktur, WZ, wpisów KB z tego dnia (`dziennik/references/zdjecia-i-kopia.md`, 4) |
| Powiązane | relacja → Notatnik budowy | wpisy, które powstały z tego dnia |
| Zadania | relacja → TASKS | usterki / rzeczy do zrobienia |
| Dodano | czas utworzenia | auto |

## Widoki na stronie DOM

- „📓 Ostatnie 7 dni” (filtr Data od tygodnia wstecz, sortowanie malejąco) – do przeglądu tygodnia.
- „⚠️ Otwarte problemy” (Problemy / usterki niepuste, sortowanie po Dacie malejąco).
- „🧮 Godziny własne” (suma per Etap, do porównania „sam vs ekipa”) – nie utworzony: narzędzie nie obsługuje
  agregacji w widoku; sumę podaj w odpowiedzi z zapytania (procedura `dziennik`, sekcja C).

## Plan zapisu (minimum zatwierdzeń)

1. Dziennik – jedno wywołanie (wpis z relacjami ustawianymi od strony dziennika).
2. Notatnik – jedno wywołanie ze wszystkimi ustaleniami/pytaniami/ryzykami dnia.
3. TASKS – jedno wywołanie z usterkami i terminami.
Kwoty: strony w kolejce „💸 Wydatki → arkusz” (`koszty`, sekcja B) – do arkusza dopisuje je automat; inwestor niczego nie wkleja.
