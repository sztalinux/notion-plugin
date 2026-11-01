# Pulpit – obieg krok po kroku

Uzupełnienie `SKILL.md`. Skrypty i schematy są w prywatnym repo pulpitu (`<repo pulpitu>`, README: sekcje „Pull” i „Push”).

## Stany prośby (`meta/prosba`)

Przycisk „Odśwież” na stronie zapisuje prośbę (`stan: nowa`, kiedy, z którego urządzenia) i podaje polecenie do wklejenia
w Claude Code. Procedura prowadzi ją dalej: `nowa` → `w toku` (krok 0; kto, kiedy) → `wykonana` (krok 5) albo `błąd` (z powodem).
Prośba w stanie `w toku` starsza niż 30 minut = prawdopodobnie przerwany obieg: zapytaj inwestora, zanim zaczniesz nowy.
Blokada plikiem `.dom/pulpit/sync.lock` (katalog tworzony `mkdir`, atomowo) chroni przed dwoma obiegami naraz.

## Kolekcje bazy strony (krok 1)

| Kolekcja | Klucz dokumentu | Pola |
|---|---|---|
| `decyzje` | `NT-n` | `wybor`, `notatka`, `kto`, `zmieniono`, `sync`, `wersja_notion`, `konflikt` |
| `rozb` | `NT-n` | `status` (otwarte / zgłoszone / wyjaśnione), `notatka`, `kto`, `zmieniono`, `sync`, `wersja_notion`, `konflikt` |
| `zadania` | id strony TASKS | `zrobione`, `zmieniono`, `sync`, `wersja_notion`, `konflikt` |
| `kroki` | id strony Harmonogramu | `status`, `zmieniono`, `sync`, `wersja_notion`, `konflikt` |
| `checklista` | id strony Checklisty budowy | `zrobione`, `zmieniono`, `sync`, `wersja_notion`, `konflikt` |
| `spotkania` | `<rola>-<data>` | `notatka`, `zmieniono`, `sync` |
| `meta` | `sync`, `prosba` | czas, stan, kto |

- Zrzut ma postać `{"pobrano": <czas ISO>, "kolekcje": {<kolekcja>: {<klucz>: {<pola>}}}}`. Kolekcja pusta albo nieistniejąca =
  pusty obiekt. Przepisz pola dokumentów bez zmian i bez dopisywania – to wiernie zrzut, nie interpretacja.
- Rekord jest **roboczy**, gdy `zmieniono` > `sync` albo `sync` = null. Rekord z `sync` ≥ `zmieniono` skrypt pomija („bez zmian”).
- Wynik zapisz w całości przed krokiem 2 (atomowo: plik tymczasowy, potem podmiana), żeby przerwany odczyt nie zostawił
  połowicznego `stan.json`.

## Push (krok 2)

Wyjście `pulpit_push.py` (bez `--dry-run`): JSON `{"czas", "tryb", "liczby", "wyniki": [{klucz, kolekcja, wynik, powod, sync,
wersja_notion, konflikt, zmiany}]}`; `wynik` = `zapisano` | `konflikt` | `pominieto` | `blad`. Kod wyjścia 1 = błąd pozycji
albo złe wejście (konflikt błędem nie jest).

Po zapisie ustaw w bazie strony dla każdej pozycji z wynikiem `zapisano`: `sync` = wartość z wyniku (to `zmieniono` wypchniętej
wersji, nie zegar – dzięki temu edycja zrobiona na stronie w trakcie obiegu zostaje robocza), `wersja_notion` = wartość z wyniku.
Dla `konflikt` – wpisz obiekt `konflikt`. Pozycje `pominieto` i `blad` zostaw bez zmian i wymień w raporcie (powód z wyniku).

Co trafia do Notion (i tylko to; strony skrypt nigdy nie zakłada ani nie usuwa):

| Z bazy strony | Do Notion |
|---|---|
| decyzja z `wybor` | Notatnik: Status „Ustalone”, Typ „Decyzja”, Notatka (jedno zdanie), w treści dopisek: wariant, dlaczego, kto, data |
| decyzja bez wyboru, z notatką | tylko dopisek w treści |
| rozbieżność | Notatnik: Status wg pulpitu + dopisek z datą |
| zadanie `zrobione` | TASKS: Status DONE |
| krok | Harmonogram: Status |
| punkt checklisty | Checklista budowy: Zrobione |
| `spotkania/*`, sprzeczności SP | **nic** – oznaczone „⏳ do czatu” |

### Konflikty

Skrypt porównuje czas ostatniej edycji strony w Notion z `wersja_notion` rekordu. Strona nowsza = konflikt: nic nie zapisuje,
wypisuje stan z Notion i stan roboczy. Notion zaokrągla czas edycji do minuty – zmiana w tej samej minucie co pull nie jest
wykrywana (dlatego pull robi się tuż przed push, a nie dzień wcześniej).

1. Pokaż inwestorowi dla każdego konfliktu: co jest w Notion (pola), co zaznaczył na stronie, kiedy zmieniono. Zapytaj: „zostaje
   moje” czy „zostaje Notion”.
2. „Zostaje moje” → w bazie strony ustaw `wersja_notion` = wersja z konfliktu, wyczyść `konflikt`, uruchom push ponownie
   (z `--tylko <kolekcja>` dla jednej kolekcji).
3. „Zostaje Notion” → ustaw rekord w bazie strony tak jak w Notion (z pull-u po kroku 3) i `sync` = `zmieniono`, wyczyść `konflikt`.
4. Bezobsługowo albo brak odpowiedzi → zostaw rekord roboczy z polem `konflikt` (strona pokaże „rozstrzygnij w czacie”),
   wpisz do raportu (⏳). Reszta obiegu idzie dalej.

Nieznana wartość statusu, brak `wersja_notion` i brak wersji w `dane.json` (→ „zrób pull”), strona z innej bazy, w koszu albo
z innym numerem NT – skrypt pomija pozycję z powodem. Nie obchodź tego ręcznym zapisem do Notion.

## Pull (krok 3)

`python3 tools/pulpit_pull.py` – deterministyczny, tylko odczyt Notion; zapis dopiero po walidacji schematem, atomowo.
Raport: liczby rekordów i **braki** (bez etapu, bez źródła, bez NT, baza niewidoczna dla tokenu). Braki przepisz do ⏳ – nie
uzupełniaj ich w `dane.json` ręcznie (plik jest generowany). `--sprawdz` waliduje sam plik bez Notion.

## Publikacja i log (krok 5)

- Publikuj `dist/pulpit.html`; adres pulpitu bierz z `.dom/pulpit/adresy.md`. Odpowiedź publikacji (wersja) wpisz do `meta/sync`.
- `meta/sync`: `{czas, wersja_strony, wyzwalacz, liczby}`. `meta/prosba`: stan `wykonana`, `kiedy_wykonano`, `kto`.
- Linia w `.dom/pulpit/sync-log.jsonl` (jedna linia JSON, dopisywana; push dopisuje własną linię sam, więc ta jest linią
  całego obiegu): `{"czas", "skrypt": "pulpit", "tryb": "pelny|podglad", "wyzwalacz": "recznie|przycisk", "zapisano",
  "konflikt", "pominieto", "do_czatu", "blad", "rekordy_pull", "wersja_strony", "testy": "ok|czerwone|nie_uruchomiono"}`.
- Po awarii w środku: `dane.json` i strona poprzednie zostają, blokada do zdjęcia, prośba `błąd` z powodem.

## Czego procedura nie robi

- Nie czyta bazy strony ani nie publikuje poza sesją interaktywną.
- Nie tworzy stron w Notion i niczego nie usuwa.
- Nie rozstrzyga sprzeczności SP ani nie zapisuje notatek ze spotkań – to `wiedza` w czacie.
- Nie zmienia kodu pulpitu (to praca w prywatnym repo, osobne zadanie).
