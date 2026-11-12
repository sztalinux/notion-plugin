# Indeks wiedzy – awarie i odnowienia

Cel: gdy indeks, jego kopia dla czatu albo token przestają działać, znajdź komunikat, wykonaj naprawę i wróć do pracy
bez zgadywania. Polecenia uruchamiaj na Macu, z katalogu repo. Użycie na co dzień: `indeks.md`.

## Co oznaczają komunikaty `[wiedza]`

| Komunikat | Znaczenie | Co zrobić |
|---|---|---|
| `✗ indeks uszkodzony – uruchom sync (na Macu)` | polecenie odczytu trafiło na zepsuty plik | `python3 tools/wiedza.py sync`; do tego czasu czytaj Notion |
| `[wiedza] indeks uszkodzony – odłożony …, budowa od nowa pełnym sync` | sync sam zastąpił zepsuty plik | nic; sprawdź `stan` po zakończeniu |
| `[wiedza] sync nie zmieścił się w limicie czasu startu (110 s, …) – nic nie zapisano` | start sesji ma budżet 110 s na pobór i publikację | uruchom `sync` ręcznie, bez `--cicho` |
| `[wiedza] publikacja: … odłożone – wysyłka nie mieści się w limicie czasu startu` | duży plik nie zmieścił się w budżecie startu | `python3 tools/wiedza.py publikuj --teraz` |
| `✗ GITHUB_REPO wskazuje repo, które nie jest prywatne – publikacja wstrzymana …` | kopia zawiera dane osób trzecich, więc nie trafi do publicznego repo | popraw `GITHUB_REPO` albo ustaw repo jako prywatne |
| błąd HTTP 301 przy publikacji | repo przemianowano lub przeniesiono | wpisz nową nazwę w `GITHUB_REPO` |
| `! historia prywatnego repo ponad 500 MB – uruchom publikuj --reset …` | historia kopii urosła | sekcja „Reset historii” |
| `! indeks z innym zestawem tabel – tabele od nowa, pełny sync` | zestaw obiektów w pliku różni się od obecnego schematu (np. po aktualizacji `wiedza.py` albo po ręcznie dodanym widoku lub tabeli) – tabele zbudowane od nowa | nic; to nie błąd, następny sync jest pełny |
| `✗ <plik>: plik nie jest indeksem wiedzy – nie nadpisuję go` | plik nie ma znacznika indeksu (obca baza; nowa wersja schematu tego nie wywołuje) | sekcja „Obcy plik” |
| `! <plik>: nie da się ustawić uprawnień 600 – ustaw ręcznie` | plik w `.dom/wiedza/` należy do innego użytkownika (np. utworzony przez `sudo`); sync działa dalej | `sudo chown` na swojego użytkownika, potem `chmod 600` (katalog: `700`) |
| ostrzeżenie o uprawnieniach `sekrety.env` | grupa lub inni mają dostęp do pliku z tokenami | `chmod 600` na tym pliku |

Zajęta blokada oznacza, że inny sync już działa – pod `--cicho` program milczy, a wystarczy poczekać. Brak komunikatu
w worktree też jest zamierzony: `sync --cicho` nic tam nie robi.

## Uszkodzony indeks

1. Uruchom `python3 tools/wiedza.py sync` – domyślny plik zostanie odłożony jako `wiedza.sqlite.uszkodzony-RRRRMMDD-GGMMSS`
   (program trzyma dwa najnowsze) i zbudowany od nowa pełnym sync.
2. Sprawdź `python3 tools/wiedza.py stan`; po `sync --publikuj` kopia dla czatu dostaje czysty plik. Nowy plik ma puste listy
   podobnych („listy podobnych: 0 wierszy”) – odbuduj je `python3 tools/wiedza_sens.py przelicz --pelny` (sam `przelicz` ich nie odtworzy).
3. Kasuj odłożone pliki dopiero, gdy nie potrzebujesz ich do diagnozy – zawierają dane z Bazy wiedzy.

## Odnowienie tokenów

Wartości trzymaj wyłącznie w `.dom/sekrety.env` (hub; `chmod 600`), w formacie `ZMIENNA=wartość`, bez cudzysłowów.
**Nigdy nie wklejaj wartości do rozmowy, notatki, Dziennika, commita ani pliku w repo** – repo jest publiczne,
a historia rozmów nie jest miejscem na sekrety.

- `NOTION_TOKEN` – integracja Notion udostępniona stronie DOM: odczyt, a w bazie 💸 Wydatki także zmiana treści (`wydatki.py`). Utwórz nową integrację z odczytem i zmianą treści,
  udostępnij jej stronę DOM, podmień wartość w `sekrety.env`, usuń starą integrację.
- `GITHUB_REPO` – `właściciel/repo` prywatnego repo kopii (to nazwa, nie sekret).
- `GITHUB_TOKEN_SYNC` – zapis kopii do tego repo; używa go tylko Mac. Wystaw nowy, podmień w `sekrety.env`, unieważnij stary.
- `GITHUB_TOKEN_SEARCH` – odczyt kopii w czacie; ważny do 2027-01-14, więc odnów przed tą datą. Wystaw nowy token
  tylko do odczytu, najlepiej z dostępem do jednego repo kopii. Zapisz go w `sekrety.env` i wklej w polu strony „🔑 Asystent – dostęp”
  w Notion – to jedyne dozwolone miejsce poza `sekrety.env`. Potem unieważnij stary. Bez tego czat zgłosi „indeks niedostępny”.

## Odtworzone lub przeniesione prywatne repo

- Repo skasowane i założone na nowo, to samo `GITHUB_REPO` → `python3 tools/wiedza.py publikuj --wymus`. Samo `publikuj`
  nie wyśle nic, bo dane się nie zmieniły; `--wymus` wysyła plik indeksu i README mimo to.
- Repo przemianowane (HTTP 301) → wpisz nową nazwę w `GITHUB_REPO`, potem `publikuj --wymus`.
- Nigdy nie ustawiaj repo kopii jako publicznego – indeks zawiera pola osób trzecich. Program odmówi publikacji do publicznego repo.

## Reset historii

Każda publikacja dokłada commit z plikiem SQLite, więc historia rośnie. Gdy `stan` pokazuje ostrzeżenie o 500 MB
(`stan --json`: pole `historia_mb`), uruchom `python3 tools/wiedza.py publikuj --reset`. Jeden commit bez rodzica (bieżące drzewo
z podmienionymi czterema plikami – workflow trybu głębokiego, `narzedzia/`, `pytania/`, `odpowiedzi/` i migawka zostają)
zastępuje całą historię gałęzi domyślnej (wymuszenie). Starych wersji pliku nie odzyskasz – i o to chodzi.
Na pustym repo (bez żadnego commita) `--reset` kończy się błędem HTTP 409 z Git Data API – pierwszą publikację
zrób zwykłym `publikuj`.

## Obcy plik

Indeks nosi znacznik w nagłówku SQLite. Program przebudowuje każdy plik ze znacznikiem, także po zmianie schematu
w nowej wersji `wiedza.py` (ostrzeżenie `! indeks w schemacie …, wymagany …`, potem pełny sync) – to nie jest awaria.
Indeks zbudowany przed wprowadzeniem znacznika dostaje go przy pierwszym sync, bez przebudowy. Pliku bez znacznika,
który nie jest takim indeksem, program nigdy nie nadpisuje.
- `--db` wskazuje obcy plik → zmień ścieżkę na nowy plik w istniejącym katalogu. Katalog, którego nie ma, daje
  `✗ --db: katalog … nie istnieje – nic nie utworzono`.
- Komunikat przy domyślnym `.dom/wiedza/wiedza.sqlite` (plik podmieniony, np. z kopii innej bazy) → przenieś go
  poza `.dom/wiedza/` i uruchom `python3 tools/wiedza.py sync` – zbuduje indeks od nowa z Notion.

## Debugowanie

Komunikaty celowo nie niosą wartości pól, tylko typ błędu i linię. Przy ręcznym uruchomieniu włącz pełny ślad:
`WIEDZA_DEBUG=1 python3 tools/wiedza.py sync`. Ślad może zawierać fragmenty danych – nie wklejaj go do notatek ani do repo.
Ślad pojawia się tylko w terminalu i bez `--cicho`, więc zmienna ustawiona na stałe nie trafi do wyjścia listy startowej ani nocnych skryptów.

## Uprawnienia i dane

- Katalog indeksu ma uprawnienia 0700, a plik indeksu, blokada i kopie 0600 – nie zmieniaj tego; `sync` i `publikuj`
  przywracają je same przy domyślnej ścieżce (pliku z `--db` nie ruszają).
- Indeks zawiera pola osób trzecich (Kto, Z kim, Mój komentarz). Kopia żyje tylko w prywatnym repo; nie udostępniaj
  pliku `wiedza.sqlite`, jego kopii ani wyników `szukaj` poza rozmową z inwestorem.

## Znane ograniczenie

Wiersze relacji źródeł lub sprzeczności usuniętych w Notion znikają z wyników po cichu, a usunięte wiersze – dopiero przy
pełnym sync (automatycznie co 7 dni albo `sync --pelny`).
