# Zdjęcia z budowy, dokumenty z telefonu i kopia dokumentów – jak to działa (dla agentów i inwestora)

Zdjęcia z telefonu trafiają na Dysk Google do folderów kroków budowy, z datą zrobienia w nazwie i śladem w Dzienniku
budowy. Papierowe faktury, WZ i wpisy kierownika fotografowane telefonem trafiają do folderów dokumentów. Dokumenty
z Maca mają kopię na Dysku. Aplikacja Dysku na Macu i konektor Dysku przyspieszają, ale nic od nich nie zależy
(sekcja 5 – tryby pracy). Wdrożenie: POM-1 (specyfikacja z 10.11.2026 w Notion, „💡 Pomysły na rozwój”).

Gdzie co jest opisane:
- procedury dla agenta: `dziennik` (ślad w Dzienniku budowy), `dokumenty` (dokumenty z telefonu, kopia),
  `etap` B (lista ujęć przed zakryciem), `harmonogram` (folder nowego kroku), `zakupy` (dokumenty dostawy),
  `budowa` (linia w przeglądzie dnia), `przeglad-tygodnia` (zdjęcia tygodnia, zaległości);
- narzędzia: `tools/zdjecia.py` (plan rozłożenia, dziennik ruchów, cofanie, ślad), `tools/kopia.py` (kopia
  dokumentów) – biblioteka standardowa Pythona 3.9, testy `tools/test_zdjecia.py`, `tools/test_kopia.py`;
- dane robocze (poza repo): `<folder budowy>/.dom/zdjecia/` (kroki.json, dysk.json z identyfikatorami folderów Dysku,
  plany, ruchy.jsonl, blokada) i `.dom/kopia/stan.json`.

## 1. Zasady (obowiązują każdego agenta, w każdym kanale)

1. **Nic nie kasuj i nic nie nadpisuj** – na Dysku ani w folderze budowy. Przenoś. Kosz tylko na wyraźne polecenie
   inwestora. Duplikat → `_Archiwum/Duplikaty/`, pusty folder po rozłożeniu → `_Archiwum/Puste foldery/`.
2. **Nie ruszaj pliku w trakcie wgrywania**: zmieniony mniej niż 15 minut temu albo folder z takim plikiem → następny
   przebieg (skrypt robi to sam).
3. **Nie zgaduj kroku.** Pewne dopasowanie → przenieś. Dwa możliwe kroki albo żaden → zostaje w `_nowe`, pytanie
   z propozycją (komunikat 🔔). Temat spoza kroków (np. przyłącza) → folder tematu obok etapów.
4. **Każdy ruch do dziennika ruchów** (`zdjecia.py zapisz-ruchy`) – skąd, dokąd, kiedy, kto. Na nim stoi „cofnij ostatnie
   rozłożenie”.
5. **Ponowny przebieg nic nie zmienia**: plik z prefiksem daty nie dostaje drugiego, rozłożony folder znika z `_nowe`.
6. **Ślad w Notion dopiero po udanym ruchu pliku.** Nieudany zapis do Notion nie cofa ruchu – ślad ponawiasz przy
   następnym przebiegu (plan zostaje w `.dom/zdjecia/`).
7. **Konektor niedostępny, odmowa uprawnień albo błąd** → nie próbuj innej drogi w tej samej sesji; komunikat 🔔
   (`wpisy/references/pytania.md`, C; klucz `zdjecia` albo `kopia`).
8. **Prywatność**: nie opisuj osób widocznych na zdjęciach; zdjęć nie wstawiaj do artefaktów, repo ani treści wpisów
   Dziennika (decyzja inwestora 10.11.2026 – w Dzienniku tylko link folderu i liczba). Identyfikatory i adresy Dysku
   tylko w `.dom/` i w Notion.
9. **Zdjęcia oglądaj tylko w trzech sytuacjach**: luźne pliki bez folderu, których nie da się przypisać po dniu;
   kontrola ujęć przed zakryciem (miara, ostrość, komplet); wyszukiwanie na prośbę. Najwyżej 10 zdjęć na przebieg.
10. **Pierwsze uruchomienie każdego nowego polecenia – na sucho**: plan ruchów do zatwierdzenia przez inwestora; dopiero
    po „ok” wykonanie. Do odwołania dotyczy to też każdego przebiegu bez inwestora (sekcja 6).

## 2. Układ na Dysku (`Mój dysk/Dom`) i na Macu

```
Dom/
  Zdjęcia/
    _nowe/                       skrzynka z telefonu: luźne pliki albo foldery z nazwą („zbrojenie z miarą”, „faktura …”)
    <Etap>/<NN Krok>/            folder kroku z Harmonogramu (link w polu „Zdjęcia” kroku); pliki RRRR-MM-DD_oryginał
      przed zakryciem/           zdjęcia z miarą
    <Temat>/                     zdjęcia spoza kroków (przyłącza, działka)
  Projekty/ Dokumenty/ Umowy/ Faktury/RRRR/ Wyceny/ Materiały/ Koszty/ Media/     kopia z Maca (źródło: Mac)
  Dostawy/<Etap>/                WZ, deklaracje, karty produktów, etykiety
  Dziennik budowy KB/            zdjęcia wpisów kierownika
  _Kopie/                        paczki z datą (kopia drogą ręczną)
  _Archiwum/                     duplikaty, puste foldery, stare wersje, pliki usunięte na Macu, stary układ Dysku
```

Mac (folder budowy): te same foldery dokumentów, `_Przychodzące/` (skrzynka na dokumenty), `_Na Dysk/` (paczki
do wgrania), `Wiedza…`, `AI/` i `.dom/` – trzy ostatnie nigdy nie idą na Dysk. `Zdjęcia/` na Macu tylko w trybach
z aplikacją albo AirDropem (kopia lokalna, gdy jest miejsce na dysku).

Źródło: dla zdjęć – Dysk; dla dokumentów – Mac. Żywy arkusz „Kosztorys budowy” zostaje tam, gdzie jest.

## 3. Rozkładanie zdjęć – reguły `tools/zdjecia.py`

**Data zrobienia** (dzień zawsze wg czasu polskiego, także po północy): EXIF (tylko lokalnie, `mdls`) → nazwa pliku
z telefonu (`PXL_RRRRMMDD_GGMMSS` – czas UTC; `IMG_`/`VID_`/`RRRRMMDD_GGMMSS`, komunikatory „RRRR-MM-DD at …” – czas
lokalny) → data wgrania (`createdTime` Dysku, UTC) z `~` w prefiksie: `RRRR-MM-DD~_nazwa` = „data wg wgrania”.
Gdy później wyjdzie dokładna data (aplikacja, EXIF), skrypt poprawia `~` na nią. Zdjęcie z komunikatora albo zrzut
ekranu zwykle nie ma daty zrobienia – inwestor wgrywa oryginały z galerii.

**Nazwa pliku**: `RRRR-MM-DD_<oryginalna nazwa>`; plik z prefiksem zostaje bez zmian. Ta sama nazwa i rozmiar w folderze
docelowym → duplikat do `_Archiwum/Duplikaty/`; ta sama nazwa, inny rozmiar → dopisek `_2`, `_3`. (Konektor nie podaje
sumy kontrolnej – porównanie po nazwie i rozmiarze.)

**Folder w `_nowe`** – po nazwie, w tej kolejności:
1. słowa dokumentu → dokument (sekcja 4): faktura, paragon, rachunek, korekta · dziennik KB, dziennik budowy, wpis
   kierownika · protokół · WZ, deklaracja, karta, etykieta, atest, dostawa;
2. numer kroku („03”, „krok 3”) albo słowa z nazwy kroku (bez polskich znaków, wielkość liter bez znaczenia) – remis
   albo brak → pytanie; słowa „przed zakryciem”, „z miarą”, „przed zalaniem”, „przed zasypką”, „przed betonowaniem”
   → podfolder `przed zakryciem/`;
3. temat z listy tematów (`kroki.json`, pole `tematy`) → `Zdjęcia/<Temat>/`;
4. nic → zostaje w `_nowe`, pytanie.

**Luźne pliki w `_nowe`**: w Dzienniku budowy z dnia zrobienia jest dokładnie jeden krok → ten krok; nie ma wpisu albo
są dwa kroki → zostają, pytanie z propozycją (w sesji z inwestorem możesz obejrzeć zdjęcie – zasada 9).

**Kroki** (`.dom/zdjecia/kroki.json`, zapisuje asystent przed każdym planem):

```json
{"etap": "<bieżący etap>", "kroki": [{"nazwa": "<Krok z Harmonogramu>", "folder": "Zdjęcia/<etap>/<Krok>"}],
 "tematy": ["<temat>"], "dni": {"RRRR-MM-DD": ["<Krok>"]}}
```

`kroki` – wiersze Harmonogramu bieżącego etapu (i poprzedniego, dopóki ma niezrobione kroki); `folder` = ścieżka folderu,
do którego prowadzi pole „Zdjęcia” kroku (nazwa folderu zostaje, choć krok zmieni nazwę – wiąże je link). `dni` – wpisy
Dziennika budowy z ostatnich 30 dni: Data → relacja „Krok harmonogramu” (gdy pusta – pole Krok dopasowane do nazwy kroku).
`tematy` – podfoldery `Zdjęcia/` niebędące etapami.

## 4. Dokumenty z telefonu (faktury papierowe, WZ, wpisy kierownika)

| Rodzaj | Dokąd | Nazwa |
|---|---|---|
| faktura, paragon, korekta | `Faktury/RRRR/` | `RRRR-MM-DD_sprzedawca_numer` (data wystawienia; nieczytelna → data zdjęcia); kolejne strony `_s2`, `_s3`; korekta `_korekta` |
| WZ, deklaracja, karta produktu, etykieta, atest | `Dostawy/<Etap>/` | `RRRR-MM-DD_co_dostawca` (WZ bez dostawcy → `_dostawca-nieznany`) |
| wpis kierownika | `Dziennik budowy KB/` | `RRRR-MM-DD_strona-n` |
| protokół | `Umowy/Protokoły/` | `RRRR-MM-DD_czego` |

- Skrypt planuje folder i nazwę tymczasową `RRRR-MM-DD_<oryginał>`; sprzedawcę, numer i datę wystawienia uzupełniasz po
  odczycie (w Claude Code obejrzyj plik; przez konektor `read_file_content` – tekst ze zdjęcia może nie wyjść, PDF tak).
  Niepewne → zostaw nazwę tymczasową i pytanie 🔔. Ta sama faktura wgrana drugi raz (ta sama nazwa po odczycie i rozmiar)
  → duplikat. Skan PDF zamiast zdjęcia – te same reguły.
- **Źródłem dokumentów jest Mac.** Z aplikacją Dysku plik trafia do folderu na Macu i wraca na Dysk kopią (sekcja 7).
  Bez aplikacji przenosisz go konektorem od razu do `Dom/<folder>` na Dysku i dopisujesz do „do pobrania na Maca”
  w komunikacie kopii (inwestor pobiera; Mac dociągnie sam, gdy aplikacja zacznie działać).
- **Faktura nie tworzy wydatku** (decyzja inwestora 10.11.2026): zdjęcie trafia tylko do `Faktury/`. Wydatek inwestor
  zapisuje jak dotąd albo prosi o to wprost (`koszty`, B).
- WZ i dokumenty dostawy: link pliku w polu „Dokumenty dostawy” wiersza 🧱 Zakupy budowy (`zakupy`) i w polu „Dokumenty
  z dnia” wpisu Dziennika budowy.

## 5. Tryby pracy (droga zapasowa)

| Tryb | Zdjęcia | Dokumenty z telefonu | Kopia dokumentów |
|---|---|---|---|
| 1. Aplikacja Dysku i konektor | skrypt lokalnie (`zdjecia.py rozloz`) na folderze Dysku, EXIF z pliku | jak zdjęcia, do folderu na Macu | `kopia.py aplikacja` |
| 2. Bez aplikacji (**stan od 10.11.2026** – aplikacja nie startuje na służbowym Macu, sprawa u IT) | konektor w rozmowie: lista → `zdjecia.py plan` → ruchy konektorem; data z nazwy albo `~` | konektor do `Dom/<folder>` na Dysku | `kopia.py paczka` → inwestor wgrywa folder do `Dom/_Kopie` |
| 3. Bez konektora | skrypt lokalnie, gdy jest aplikacja; inaczej jak 4 | jak zdjęcia | aplikacja albo paczka |
| 4. Bez obu | czeka (nic nie ginie) albo: inwestor pobiera `_nowe` z przeglądarki jako zip do `Zdjęcia/_nowe` na Macu, `zdjecia.py rozloz`, wynik wraca paczką | jak zdjęcia | paczka |
| 5. Bez Dysku | AirDrop/kabel do `Zdjęcia/_nowe` na Macu, `zdjecia.py rozloz`, kopia na dysk zewnętrzny | jak zdjęcia | dysk zewnętrzny |

Wykrywanie trybu kopii: lokalny folder Dysku w `~/Library/CloudStorage/GoogleDrive-*/…/Dom` albo zmienna `DYSK_DOM`;
brak → paczka. Czat i telefon bez konektora nie czytają dokumentów z Dysku – „prośba o dokument” jak dotąd (`dokumenty`).

## 6. Co wolno w którym kanale

| Kanał | Rozkładanie zdjęć | Dokumenty z telefonu | Kopia | Ślad w Notion |
|---|---|---|---|---|
| Claude Code z folderem budowy | tak – plan, zatwierdzenie, ruchy konektorem lub skryptem | tak (z odczytem pliku) | tak (`kopia.py`) | tak |
| Czat / telefon z konektorem Dysku | tylko plan słowami i ruchy po „ok” inwestora; bez skryptu reguły z sekcji 3 stosujesz ręcznie, ruchy wpisujesz do komunikatu 🔔 „do zapisania w dzienniku ruchów” | tak, bez wydatku | nie | tak |
| Czat bez konektora | nie – powiedz, gdzie wgrać (sekcja 9) | nie | nie | nie |
| Przebieg bez inwestora (automat, zaplanowane zadanie) | **na razie nie** – nie wiadomo, czy ma konektor Dysku (test T9); tylko licznik „w `_nowe` czeka n” w przeglądzie, jeśli konektor jest | nie | `kopia.py stan --cicho` (sama informacja) | nie |
| Inne AI | tylko odczyt reguł i podpowiedź, gdzie wgrać | nie | nie | nie |

## 7. Kopia dokumentów Mac → Dysk – `tools/kopia.py`

- Lista dozwolona: Projekty, Dokumenty, Umowy, Faktury, Wyceny, Materiały, Koszty, Media, Dostawy, Dziennik budowy KB.
  Nigdy: `.dom`, `AI`, `Wiedza…`, `_Przychodzące`, `_Do claude.ai`, `_Na Dysk`, `Zdjęcia`, pliki ukryte, tymczasowe,
  blokady biurowe, `Kosztorys_google.json` (kopia żywego arkusza, nadpisywana co wieczór).
- Stan: `.dom/kopia/stan.json` – potwierdzone pliki (ścieżka, rozmiar, sha256). Punktem wyjścia była pierwsza paczka
  z 10.11.2026 (41 plików, wgrana i rozłożona tego samego wieczoru).
- `kopia.py stan` – tryb, data potwierdzonej kopii, liczba zmian, paczki czekające na wgranie.
- **Tryb paczki**: `kopia.py paczka` (na sucho) → `kopia.py paczka --wykonaj` składa `_Na Dysk/RRRR-MM-DD/` (nowe,
  zmienione, przeniesione pliki + `SPIS.txt` z usuniętymi). Inwestor przeciąga ten folder w przeglądarce do `Dom/_Kopie`
  i mówi „wgrałem kopię” → `kopia.py wgrane`. Niewgrana paczka → następna zawiera też jej zmiany (porównanie zawsze
  z potwierdzonym stanem). `wgrane` znaczy tylko „paczka jest na Dysku” – kopia
  już istnieje, nawet nierozłożona. Rozłożenie konektorem jest opcjonalne i jak każdy ruch – najpierw lista „co, skąd,
  dokąd” (z `SPIS.txt` paczki) do zatwierdzenia, identyfikatory z `dysk.json`: zmieniony plik – poprzednia wersja do
  `_Archiwum/RRRR-MM-DD/`, usunięty na Macu – do `_Archiwum`, przeniesiony – przenieś. Ta sama paczka wgrana dwa razy →
  druga kopia do `_Archiwum/Duplikaty/`. Pliki dodane konektorem prosto na Dysk (dokumenty z telefonu bez aplikacji)
  wymień w komunikacie 🔔 z kluczem `kopia` jako „do pobrania na Maca”.
- **Tryb aplikacji**: `kopia.py aplikacja [--wykonaj]` – kopiuje do lokalnego folderu Dysku według tych samych reguł,
  pliki tylko na Dysku wypisuje do pobrania na Maca. Plik zmieniony po obu stronach → obie wersje (Dysk do `_Archiwum`)
  i komunikat. Arkusze i dokumenty Google nie mają pliku na Macu – zostają tylko na Dysku.
- Kontrola Dysku: lista z konektora (ścieżki) → `kopia.py sprawdz-dysk <lista.json>` – na Dysku nie może być `.dom`,
  `AI`, `.git` ani plików z sekretami.
- Kopia `.dom/` (dane asystenta i sekrety) nie idzie na Dysk – osobny pomysł o kopiach zapasowych (Time Machine albo
  dysk zewnętrzny).

## 8. Przepływy krok po kroku (Claude Code)

**Pierwsze uruchomienie / brak `.dom/zdjecia/dysk.json`** (zapisz go, zanim cokolwiek przeniesiesz):
`search_files` z `title = 'Dom'` i `mimeType = 'application/vnd.google-apps.folder'` (folder w `root`) → jego dzieci
(`parentId = '<id Dom>'`) → `Zdjęcia` → dzieci `Zdjęcia` (`_nowe`, etapy, tematy) → dzieci etapów (foldery kroków).
Format: `{"foldery": {"Zdjęcia": "<id>", "Zdjęcia/_nowe": "<id>", "Zdjęcia/<Etap>/<Krok>": "<id>", "Faktury": "<id>", …}}`
– klucz = ścieżka od `Dom`, wartość = identyfikator. Każdy folder utworzony albo przeniesiony konektorem dopisz/popraw
od razu. Brak `kroki.json` → zbuduj go (sekcja 3); bez kroków plan zostawia wszystko w `_nowe`.

**„rozłóż zdjęcia”** (tryb 2):
1. `python3 tools/zdjecia.py stan` (blokada? ostatni przebieg?). Odśwież `.dom/zdjecia/kroki.json` z Harmonogramu
   i Dziennika budowy (sekcja 3).
2. Konektor: `search_files` z `parentId` folderu `_nowe` (z `dysk.json`); narzędzie nie schodzi w głąb samo – wywołaj
   je osobno dla każdego podfolderu (`mimeType` folderu w wynikach). Do tego pliki folderów docelowych, do których coś
   może trafić (duplikaty). Pole rozmiaru w wynikach to `fileSize` (tekst – zamień na liczbę). Zapisz listę w
   `.dom/zdjecia/lista-<data>.json`: `nowe` – `id`, `nazwa` (title), `folder` (ścieżka od `_nowe`, "" luzem), `rozmiar`
   (fileSize), `utworzono` (createdTime), `zmieniono` (modifiedTime); `istniejace` – `folder` (ścieżka od `Dom`),
   `nazwa`, `rozmiar`.
3. `python3 tools/zdjecia.py plan --lista <lista>` → plan i pytania. Pokaż inwestorowi listę ruchów (zasada 10);
   po „ok” wykonaj.
4. Ruchy konektorem: `update_file` z `fileId`, `parentId` folderu docelowego (z `dysk.json`) i `title` = nowa nazwa –
   jedno wywołanie. Brak folderu docelowego → `create_file` z `title`, `parentId` i
   `contentMimeType = 'application/vnd.google-apps.folder'`; identyfikator dopisz do `dysk.json`. Pusty folder z `_nowe` → `_Archiwum/Puste
   foldery`. Błąd → zatrzymaj się (zasada 7).
5. `python3 tools/zdjecia.py zapisz-ruchy <plan> --kto konektor --tylko <id wykonanych, po przecinku>`.
6. `python3 tools/zdjecia.py slad <plan>` → ślad w Dzienniku budowy (sekcja 10, `dziennik` E).
7. Pytania z planu → jeden komunikat 🔔 z kluczem `zdjecia` (aktualizowany, nie powielany).

**„wgrałem fakturę”** – jak wyżej (folder „faktura …” w `_nowe` albo luzem), potem odczyt i nazwa wg sekcji 4; bez
wydatku (o wydatek zapytaj jednym zdaniem – inwestor może chcieć go zapisać; wtedy `koszty` B).
**„gdzie są zdjęcia zbrojenia”** – dopasuj krok w Harmonogramie (kilka pasuje → wymień je z linkami) i podaj link z pola
„Zdjęcia” oraz liczbę plików (`search_files` z `parentId` folderu; osobno `przed zakryciem/`). Pole puste → folder z
`dysk.json` albo `search_files` z `title contains '<słowo z kroku>'` i `mimeType` folderu. Dzień: data `RRRR-MM-DD`
w wyszukiwarce Dysku albo wpis Dziennika budowy z tego dnia. Zdjęć nie otwieraj bez prośby (zasada 9). **„zrób kopię dokumentów”** – `kopia.py stan` → `paczka` (na sucho) →
`paczka --wykonaj` → instrukcja dla inwestora (sekcja 9, pkt 6). `kopia.py stan` podaje tryb „aplikacja”, gdy istnieje
lokalny folder Dysku – dopóki inwestor nie potwierdzi, że aplikacja działa (stan od 10.11.2026: nie działa), używaj paczki,
nie `kopia.py aplikacja`.
**„aplikacja Dysku nie działa”** – nic do naprawiania po stronie asystenta (Mac służbowy, MDM – sprawa dla IT inwestora;
nie obchodź zabezpieczeń, nie przeinstalowuj). Potwierdź jednym zdaniem, że wszystko działa dalej: zdjęcia – wgrywanie
z telefonu i „rozłóż zdjęcia” konektorem (tryb 2), kopia – paczka; zapytaj, co zrobić teraz.
**„cofnij ostatnie rozłożenie”** – `zdjecia.py cofnij` wypisuje odwrotny plan ostatniego niecofniętego przebiegu
(`.dom/zdjecia/cofniecie.json`). Pokaż go i po „ok” wykonaj: najpierw foldery (z `_Archiwum/Puste foldery` z powrotem do
`_nowe`; identyfikator folderu wyszukaj po nazwie w archiwum), potem pliki (`fileId` z planu, `parentId` z `dysk.json` –
popraw w nim ścieżki przeniesionych folderów, `title` = dawna nazwa). Lokalnie: `cofnij --wykonaj`. Po konektorze:
`cofnij --zrobione` (oznacza przebieg jako cofnięty – kolejne „cofnij” weźmie wcześniejszy). Ślad w Notion popraw ręcznie
(liczby i linki).

**Zdjęcia z dnia albo tygodnia**: każdy plik zaczyna się od daty, więc data w wyszukiwarce Dysku (albo Findera) pokazuje
wszystkie zdjęcia dnia ze wszystkich folderów; wpis Dziennika budowy z dnia ma linki do folderów kroków; przegląd tygodnia
ma sekcję „Zdjęcia tygodnia”. Na Macu z kopią lokalną `zdjecia.py wg-dni` buduje `Zdjęcia/_wg dni/RRRR-MM-DD/`
z dowiązaniami.

## 9. Jak tego używać (dla inwestora)

1. Zdjęcia robisz zwykłym aparatem.
2. Tego samego dnia: Dysk → `Dom/Zdjęcia` → folder kroku albo nowy folder w `_nowe` z nazwą, co na nich jest
   („zbrojenie płyty z miarą”). Zawsze oryginały z galerii, nie przez komunikator.
3. Faktura papierowa, WZ, wpis kierownika: zdjęcie do `_nowe`, najlepiej w folderze „faktura …”, „WZ …”, „dziennik KB”.
4. Powiedz w Claude Code „rozłóż zdjęcia” (przebiegi automatyczne jeszcze tego nie robią). Pytania i problemy pojawiają
   się we „📝 Wpisach” pod 🔔.
5. Szukanie: Dysk → Zdjęcia → etap → krok; Dziennik budowy → dzień → link; data w wyszukiwarce Dysku.
6. Kopia dokumentów bez aplikacji: przeciągnij folder z datą z `_Na Dysk` (Mac) do `Dom/_Kopie` (Dysk w przeglądarce)
   i napisz „wgrałem kopię”.

## 10. Ślad w Notion

- **Dziennik budowy** (wpis z dnia zrobienia, nie wgrania; brak → wpis minimalny: data, etap, krok, zdjęcia; dwa wpisy
  z jednego dnia → ten z pasującym krokiem, inaczej pierwszy):
  - „Zdjęcia” = `<łącznie> zdj.: <NN Krok> (<n>) <link folderu>; …` – liczba na początku (czyta ją pulpit budowy);
  - „Krok harmonogramu” = relacja do kroków, w których przybyły zdjęcia;
  - „Ujęcia przed zakryciem” = które ujęcia z listy `etap` B są, których brakuje (zdjęcia w `przed zakryciem/`);
    „Przed zakryciem OK” – tylko przy komplecie;
  - „Dokumenty z dnia” = linki plików z sekcji 4.
- **Harmonogram**: pole „Zdjęcia” (adres folderu kroku) – ustawiane przy tworzeniu folderu.
- **🧱 Zakupy budowy**: „Dokumenty dostawy” = link WZ / karty.

## 11. Przypadki brzegowe – jak są obsłużone

| Przypadek | Obsługa | Test |
|---|---|---|
| brak daty zrobienia (komunikator, zrzut) | data wgrania z `~` | `test_brak_daty_w_pliku_data_wgrania` |
| zdjęcia wgrane kilka dni po zrobieniu | ślad do wpisu z dnia zrobienia | `test_slad_i_pole` |
| zdjęcie po północy, czas Dysku w UTC | dzień wg czasu polskiego | `test_pixel_utc_na_polski` |
| filmy, para zdjęcie + film, HEIC | ten sam folder co zdjęcia; HEIC jak JPEG | `test_film_razem_ze_zdjeciem`, `test_img_lokalny` |
| seria, ten sam plik dwa razy | ta sama nazwa i rozmiar → `_Archiwum/Duplikaty`; inna treść → `_2` | `test_duplikat_i_kolizja`, `test_dwa_takie_same_w_jednym_przebiegu` |
| polskie znaki zapisane na dwa sposoby (NFC/NFD), spacja na końcu nazwy, znaki niedozwolone | porównanie po normalizacji; nazwy czyszczone | `test_nfd_nazwa`, `test_spacja_na_koncu` |
| folder kroku przemianowany ręcznie, krok przemianowany | wiąże link w polu „Zdjęcia”; `kroki.json` bierze ścieżkę z linku | – (sprawdza agent) |
| krok podzielony / połączony / usunięty / bez numeru, nowy etap | nowy krok → nowy folder przy najbliższym przebiegu; dopasowanie po słowach; stary folder zostaje | `test_slowa_bez_polskich_znakow` |
| dwa możliwe kroki albo żaden | zostaje, pytanie | `test_remis_nie_zgaduje`, `test_zaden` |
| zdjęcia prywatne wgrane przez pomyłkę | brak dopasowania → zostają z pytaniem | `test_prywatne_zostaja` |
| zdjęcie dokumentu w folderze zdjęć i odwrotnie | słowa folderu decydują; luźne – agent ogląda (zasada 9) | `test_faktura` |
| brak wpisu Dziennika z dnia; dwa wpisy z dnia | luźne czekają z pytaniem; ślad: wpis minimalny / pasujący | `test_luzem_brak_wpisu_dnia` |
| inwestor sam przeniósł zdjęcia | skrypt pomija brakujące źródło; konektor – plik nie jest już w `_nowe` | `test_rozloz_cofnij` |
| wgrywanie trwa | folder czeka do następnego przebiegu | `test_wgrywanie_trwa` |
| ponowny przebieg | bez zmian | `test_ponowny_przebieg_bez_zmian` |
| skrypt i konektor naraz | blokada `.dom/zdjecia/blokada.json` (2 h) | `test_blokada` |
| przebieg przerwany w połowie | `zapisz-ruchy --tylko` zapisuje wykonane; reszta planu przy następnym | – |
| Notion nie odpowiada | ruch zostaje, ślad przy następnym przebiegu (plan w `.dom/zdjecia/`) | – |
| faktura na kilku zdjęciach, korekta, nieczytelna data, WZ bez dostawcy, PDF | sekcja 4 | – (agent) |
| pliki tymczasowe, blokady biurowe | pomijane | `test_pliki_tymczasowe_pomijane`, `test_nigdy` |
| plik zmieniony po obu stronach | obie wersje, Dysk do `_Archiwum`, komunikat | `test_aplikacja_archiwizuje_nie_kasuje` |
| plik usunięty ręcznie na Dysku | wraca z Maca przy kopii | – |
| arkusze i dokumenty Google | tylko na Dysku | – |
| brak miejsca na Macu | kopia lokalna zdjęć wyłączona (dziś: dysk zajęty w 97%) | – |
| paczka niewgrana; ta sama wgrana dwa razy | następna zawiera wcześniejsze zmiany; druga kopia do `_Archiwum` | `test_paczka_tylko_dozwolone_i_kolejna_zawiera_niewgrane` |
| `.dom`, `AI`, sekrety na Dysku | nigdy w kopii; kontrola listy konektora | `test_sprawdz_liste` |

## 12. Testy i stan wdrożenia

Testy na żywo (specyfikacja POM-1, sekcja 10): T1 zapis konektorem – zaliczony 10.11.2026. T2/T3 (aplikacja Dysku,
dostęp automatu) – czekają na działającą aplikację. T4–T8 i T9 (czy przebieg bez inwestora ma konektor Dysku) – do zrobienia
przy pierwszych zdjęciach. Do czasu T9 przebiegi automatyczne nie rozkładają zdjęć (sekcja 6).
Kryteria odbioru (20 zdjęć trzema sposobami, faktura, zmieniony PDF, próba bez aplikacji, kontrola Dysku, liczby plików)
– przy pierwszym dniu z dużą liczbą zdjęć, z inwestorem.
