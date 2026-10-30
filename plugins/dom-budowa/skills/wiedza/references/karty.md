# Karty wiedzy – gotowy wybór tez do typowych pytań

Cel: czat na telefonie nie szuka tez sam – czyta **kartę**, czyli listę numerów WI wybranych z góry do rodziny pytań. Wybór robi Mac,
offline, mocnym modelem, który czyta CAŁĄ bazę w małych porcjach (porcje omijają straty, jakie model ma przy bardzo długim kontekście);
wynik leży w tym samym pliku `wiedza.sqlite`, który telefon już pobiera. Powód: sam czat widzi przy pytaniach szerokich ok. 60% trafnych tez, a poziom
„cały etap” (330–390 tys. znaków) przerasta okno rozmowy – w teście z telefonu 28.10.2026 przeczytał w całości 3 z 16 części.
Jak czat korzysta z kart: `pytanie-do-bazy.md`, pkt 2; polecenia `karty` i `karta`: `indeks.md`.

## Dwa rodzaje kart

- **Karta pytań** (dziś ok. 15) – rodzina pytań, np. „Betonowanie”, „Materiały na stan zero”, „Kontrola robót i zamknięcie stanu zero”.
  Rdzeń 150–270 tez (50–90 tys. znaków, 2–4 części) i rozszerzenie – tezy pokrewne (`karta KOD --wiecej`). Tezy wybrał model na Macu
  w dwóch krokach: wybór inkluzywny (cała baza, porcje po ok. 160 tez, dwa przebiegi w różnej kolejności, suma – 300–1000 tez) i ocena
  ścisła każdej z nich (2 = konieczna, 1 = pokrewna, 0 = nie dotyczy): rdzeń = ocena 2 plus najlepsze z oceny 1 wg trafień szukania, do
  200 tez; rozszerzenie = reszta z oceną 1; karty z wzorcem mają w rdzeniu także wszystkie trafne tezy wzorca. **Pokrycie jest mierzone** (`pomiar --zapisz`) i widać je w nagłówku karty (do pomiaru: „pokrycie: niemierzone”).
- **Karta czynności** (dziś 68) – jedna czynność, np. „Betonowanie płyty”, „Zasypka i zagęszczanie”, „Drenaż i studzienki”. Tezy otagowane
  czynnością przez model na Macu, zwykle 10–60 tez, karta mała. **Pokrycie niemierzone** („tagi modelu”). Służy pytaniom wąskim
  i nietypowym – czat bierze 2–4 karty naraz.

Karty mają kody ASCII (np. `stan-zero-zamkniecie`, `betonowanie-plyty`). Aktualną listę daje wyłącznie `karty` – definicje się zmieniają,
więc nie przepisuj jej do procedur ani do rozmów.

## Gdzie leżą dane

Definicje kart (kod, etap, nazwa, opis, przykładowe pytania – `definicje.json`) i dane pomiarowe leżą **poza repo**, w `.dom/wiedza/karty/`:
repo jest publiczne, a przykładowe pytania i wzorzec pomiaru to prawdziwe pytania inwestora i numery tez z jego bazy. W repo jest tylko
kod (`tools/wiedza_karty.py`, `tools/wiedza.py`) i ta procedura. Gotowe karty są w tabelach pliku `wiedza.sqlite` (meta `karty_zbudowano` –
data ostatniego zapisu) i jadą do czatu razem z publikacją indeksu.

## Polecenia Maca (tylko Claude Code: `python3 tools/wiedza_karty.py …`)

- `definicje [--sprawdz]` – definicje kart; `--sprawdz` kontroluje ich poprawność.
- `importuj-tagi`, `taguj` – tagi czynności tez (dla kart czynności).
- `zbuduj [--karty KOD,…] [--przebiegi 2]` – wybór tez do kart pytań modelem Sonnet: cała baza w porcjach po ok. 110 tez, dwa przebiegi
  w różnej kolejności, suma (to, co jeden przebieg pominął, łapie drugi). Wywołania idą przez cache; na końcu koszt w USD; przy limicie
  tygodnia model się zatrzymuje – dokończ po jego odnowieniu, nie ponawiaj na siłę.
- ocena ścisła po `zbuduj` (rdzeń ≤ 200 tez + rozszerzenie) – dziś skrypt poza narzędziem (katalog planów na Macu, `ocen_karty.py
  --zastosuj D`), do włączenia do `wiedza_karty.py`; bez niej `zbuduj` zostawia karty za duże dla telefonu (300–1000 tez).
- `pomiar [--dopelnienie] [--zapisz] [--brakujace]` – pokrycie wobec wzorca; `--zapisz` zapisuje je do stanu (do nagłówka karty trafia z `zapisz`,
  a `zbuduj` je zeruje); pozostałe flagi: `pomiar --help`.
- `zapisz [--publikuj]` – wyniki doboru (`karty.json`) do SQLite; `--publikuj` wysyła kopię dla czatu.
- `aktualizuj [--cicho] [--publikuj]` – nowe tezy → tagi czynności i ocena względem każdej karty pytań → zapis → publikacja.

## Pokrycie – co znaczy i czego nie znaczy

Pokrycie karty pytań to odsetek tez uznanych za trafne we **wzorcu** (598 tez dla 10 pytań inwestora, wzorzec z 28.10.2026), który karta
zawiera – osobno dla wszystkich trafnych i dla samych Kluczowych. Nagłówek karty podaje je tak: „pokrycie X% trafnych / Y% Kluczowych
(wobec wzorca <data> (<ID wzorca>, …))”; bez pomiaru – „pokrycie: niemierzone” (karta czynności: „… (karta czynności – tagi modelu)”;
karta pytań – także po `zbuduj`, dopóki `pomiar --zapisz` nie zapisze pokrycia). To miara wobec tego jednego wzorca, nie „prawdy
absolutnej”: tezy dodane po 28.10.2026 wzorzec nie ocenia (do kart wchodzą przez ocenę modelu w `aktualizuj`, ale ich pokrycia nie da się
zmierzyć), a pytanie spoza dziesięciu może potrzebować tez, których wzorzec nie zna. Dlatego czat podaje pokrycie w zasięgu odpowiedzi
(miara zaufania inwestora) i nie czyta braku w karcie jako braku w bazie.
Średnie pokrycie kart pytań (pomiar 29.10.2026): 68% samym wyborem modelu (rdzeń do ok. 200 tez; z rozszerzeniem `--wiecej` 89%), a rdzeń kart dla 10 pytań inwestora uzupełniony wzorcem – 100%; Kluczowych 88% (z rozszerzeniem 91%, po uzupełnieniu wzorcem 100%).

## Utrzymanie

- **Automat:** co godzinę na Macu automat (skrypt poza repo) uruchamia `aktualizuj` z publikacją. Po zapisie wiedzy wystarczy
  `sync --publikuj` – nowe tezy dołączy najbliższy przebieg, a do tego czasu widać je w „Dopełnieniu z szukania”, o ile pasują do
  sformułowań pytania.
- **Nowa karta pytań:** (1) dopisz wpis w `definicje.json` (m.in. kod ASCII, etap, nazwa, opis, przykładowe pytania) i uruchom `definicje --sprawdz`;
  (2) `zbuduj --karty KOD`; (3) `pomiar --zapisz`, gdy karta ma wzorzec; (4) `zapisz --publikuj`. `zbuduj` kosztuje (dwa przebiegi modelu przez
  całą bazę, USD i limit tygodnia) – zaproponuj kartę inwestorowi (nazwa, rodzina pytań), zanim ją zbudujesz.
- **Kiedy dodać kartę pytań:** pytanie inwestora powtarza się albo żadna karta pytań nie pasuje, a pytanie jest szerokie (czat składa je
  z kart czynności albo „trafienia poza wszystkimi kartami” > 15); pytanie, które poszło trybem głębokim (`tryb-gleboki.md`), to kandydat
  na nową kartę pytań. Wąskie pytanie o fakt zostaw szukaniu. Powód: karta pytań to koszt budowy i pomiaru, a kilkanaście kart wystarcza,
  gdy każda ma wyraźną rodzinę pytań.

## Czego nie robić

- Nie zapisuj kart do Notion: Notion jest źródłem prawdy tez, karty to indeks (jak `wiedza.sqlite`), odtwarzany z bazy i definicji.
- Nie wypisuj treści tez w raportach z `zbuduj`, `pomiar` i `aktualizuj` – tylko liczby (kody kart, liczby tez, pokrycie, koszt).
- Nie poprawiaj kart ręcznie w SQLite: `zapisz` nadpisuje je z `karty.json`; popraw definicję i zbuduj ponownie.
- Nie uruchamiaj poleceń Maca z czatu (`zbuduj`, `aktualizuj`, `zapisz`, `sync`); po zapisie wiedzy napisz: „karty dogonią przy
  najbliższym przebiegu na Macu”.
- Nie podawaj pokrycia z pamięci ani jako gwarancji kompletności – tylko z nagłówka karty.
