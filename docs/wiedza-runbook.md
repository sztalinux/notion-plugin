# System wiedzy – runbook

Instrukcja krok po kroku: jak odtworzyć system wiedzy od zera, jak działa na co dzień i co robić, gdy coś przestaje działać.
Mapa całości i decyzje: `docs/system-wiedzy.md`; polecenia i komunikaty: `plugins/dom-budowa/skills/wiedza/references/`
(`indeks.md`, `indeks-awarie.md`, `indeks-jakosc.md`, `karty.md`). Ten plik jest ogólny – **ścieżki prywatne, nazwy kanałów, adres
prywatnego repo kopii i terminy konkretnych tokenów** są poza repo, w lokalnym README inwestora (`README-lokalne.md` w katalogu planów).
Wszystkie polecenia uruchamiaj na Macu z katalogu repo, o ile nie napisano inaczej.

Zasady, które obowiązują w każdej sekcji:
- Wartości tokenów i haseł **nigdy** nie trafiają do rozmowy, notatki, Dziennika, commita ani pliku w repo (repo jest publiczne).
  Tokeny leżą w pliku sekretów (`.dom/sekrety.env` w folderze budowy, tryb 600, format `ZMIENNA=wartość`) i – token odczytu – na stronie
  Notion „🔑 Asystent – dostęp”. Token, który przeszedł przez rozmowę lub log, uznaj za ujawniony: wystaw nowy, unieważnij stary.
- Notion jest jedynym źródłem prawdy. Indeks, karty i migawka są kopiami, które da się odtworzyć; nie poprawiaj ich ręcznie w SQLite.
- Treści bazy wiedzy nie wypisuj do rozmów ani logów; w raportach tylko liczby, numery WI/ZRD/SP i kody kart.

## Szybki spis objawów

| Objawem jest | Idź do |
|---|---|
| Telefon: „indeks niedostępny” | 5.3 |
| Telefon: „karty brak w tej kopii” albo stare dane | 5.3, 5.4 |
| Przeglądy Dziennika nie chodzą (brak linii „🤖”, puste logi) | 5.1 |
| Konektor Notion zniknął w rozmowie albo „NOTION: brak logowania” | 5.2 |
| `stan` pokazuje „kopia aktualna: nie”, stare daty, wiersze usunięte w Notion wciąż widać | 5.4 |
| Wyszukiwanie po zmianie modelu embeddingów dziwne | 5.5 |
| Karta na telefonie ma stare tezy albo brakuje nowych | 5.6 |
| Pytanie z telefonu (tryb głęboki) bez odpowiedzi | 5.7 |
| Token wygasa albo wygasł (HTTP 401/403, „Bad credentials”) | 5.8 |
| Komunikat `[wiedza]` albo `[jakosc]`, którego nie znasz | 3 |

## 1. Odtworzenie od zera (nowy komputer, utracony folder, nowe konto)

Co jest w repo (kod, procedury) wraca z `git clone`. Czego w repo nie ma, trzeba odtworzyć albo przywrócić z kopii zapasowej: sekrety,
dane indeksu, definicje kart, zbiory oceny, prywatne repo kopii, automaty launchd, kolejkę nocną.

1. **Repo i środowisko.** Sklonuj repo do `<folder budowy>/AI/dom` (folder budowy to dwa poziomy wyżej; inna lokalizacja – zmienna `DOM_HUB`).
   `git config core.hooksPath .githooks`; autor commitów: imię albo login i e-mail `…@users.noreply.github.com`. Python 3 (3.9 wystarcza,
   tylko biblioteka standardowa w `tools/wiedza*.py`), `pip3 install --user openpyxl pypdf` dla `dokumenty.py`. Lista słów zakazanych w repo:
   `<folder budowy>/.dom/zakazane-w-repo.txt` (po jednym w linii; odtwórz ją z danych osób i firm projektu).
2. **Notion – integracja tylko do odczytu.** Utwórz integrację z uprawnieniem „Read content” i udostępnij jej stronę DOM (cztery bazy wiedzy
   oraz Notatnik budowy i zadania dla migawki). Zapisy robi wyłącznie asystent przez serwer MCP Notion, nie ta integracja.
3. **Plik sekretów** `.dom/sekrety.env` (tryb 600). Klucze (bez wartości):
   - `NOTION_TOKEN` – odczyt Notion przez API (`sync`, `migawka.py`);
   - `GITHUB_REPO` – `właściciel/repo` prywatnego repo kopii (nazwa, nie sekret);
   - `GITHUB_TOKEN_SYNC` – zapis kopii; używa go tylko Mac;
   - `GITHUB_TOKEN_SEARCH` – odczyt kopii w czacie na telefonie;
   - `GITHUB_TOKEN_PYTANIA` – zapis pytań trybu głębokiego z telefonu (tylko ta ścieżka repo; w pliku dostępu, sekcja „Tryb głęboki”).
   Najmniejsze możliwe uprawnienia: tokeny GitHub drobnoziarniste, jedno repo (kopii), odczyt (`SEARCH`) albo zapis zawartości (`SYNC`, `PYTANIA`).
4. **Prywatne repo kopii.** Załóż **prywatne** repo (program odmówi publikacji do publicznego), wpisz je w `GITHUB_REPO`. Wgraj do niego workflow
   trybu głębokiego i runner (pliki z katalogu automatów – lokalizacja w `README-lokalne.md`), dodaj sekret repo `CLAUDE_CODE_OAUTH_TOKEN`
   (długoterminowy token Claude Code, wystawiony poleceniem `claude setup-token`).
5. **Ollama i model.** Zainstaluj Ollamę, `ollama pull bge-m3`; konfiguracja opcjonalna w `.dom/sens.json` (`{"zrodlo": "ollama", "model": "bge-m3"}`,
   `"zrodlo": "brak"` wyłącza odciski). Bez Ollamy wszystko działa po słowach.
6. **Pierwszy indeks.** `python3 tools/wiedza.py sync --pelny` (kilka minut; zbuduje `.dom/wiedza/wiedza.sqlite`), potem
   `python3 tools/wiedza_sens.py przelicz` (odciski i listy podobnych, ok. 3 minuty) i `python3 tools/wiedza.py stan` – liczniki muszą się zgadzać
   z Notion (informacje, tematy, źródła, SP).
7. **Karty.** Dane kart (`definicje.json`, `wzorzec.json`, `pytania.json`, `tagi-z12.json`, `karty.json`, `oceny.json`) leżą w `.dom/wiedza/karty/` poza repo
   i **muszą wrócić z kopii zapasowej** – z samego repo ich nie odtworzysz (definicje to prawdziwe pytania inwestora). Po przywróceniu:
   `python3 tools/wiedza_karty.py definicje --sprawdz`, `python3 tools/wiedza_karty.py zapisz`. Bez kopii karty buduje się od nowa: definicje (kod, etap,
   nazwa, opis, przykładowe pytania) → `taguj` (karty czynności) → `zbuduj` → `ocen --zastosuj` → `pomiar --zapisz` (gdy karta ma wzorzec) → `zapisz --publikuj`.
   To kosztuje USD i limit tygodnia (koszty w `koszt.json` katalogu kart); nie zaczynaj, gdy limit tygodnia jest blisko progu.
8. **Publikacja.** `python3 tools/wiedza.py publikuj --wymus` (pierwsza publikacja do świeżego repo; samo `publikuj` nic nie wyśle, gdy dane się nie zmieniły).
   `python3 tools/migawka.py` – migawka Notatnika i zadań. `python3 tools/wiedza.py stan` ma pokazać „kopia aktualna: tak”.
9. **Strona dostępu i test z telefonu.** Wpisz na stronie „🔑 Asystent – dostęp” `GITHUB_REPO`, token odczytu i jego datę ważności; plik dostępu
   do projektu „Dom” odśwież. Test: na telefonie, w rozmowie z pluginami, zadaj pięć pytań (jedno wąskie, jedno szerokie, jedno o stan spraw z migawki,
   jedno o rzecz, której baza nie zna, jedno złożone) i sprawdź: odpowiedź cytuje numery WI, nagłówek karty podaje pokrycie, zasięg mówi, czego brak.
10. **Automaty launchd** (przeglądy Dziennika, kopia dla telefonu): sekcja 5.1; wcześniej zaloguj lokalny serwer MCP Notion
    (`claude mcp add --transport http --scope user notion https://mcp.notion.com/mcp`, potem `claude` → `/mcp` → `notion` → logowanie).
11. **Pluginy i projekt na claude.ai.** Marketplace `sztalinux/notion-plugin` → zainstaluj `ja` i `dom-budowa`; instrukcje projektu „Dom” z `python3 tools/build.py`
    (`dist/claude-ai-projekt/instrukcje.md`). Odświeżenie wersji: `plugins/ja/skills/rozwoj-harnessu/references/claude-ai-projekt.md`.
12. **Nocna kolejka** (poza repo): kopia katalogu kolejki z kopii zapasowej, `python3 kolejka_zdrowie.py` ma dać „SPRAWNA”. Jej ścieżki i start – `README-lokalne.md`.

## 2. Codzienny i nocny workflow

**Dzień (samo):** launchd uruchamia szybki przebieg Dziennika co godzinę (8:05–22:05, plus 22:30); każdy przebieg zaczyna od trzech kroków przygotowania:
`wiedza.py sync --publikuj --cicho` (indeks z Notion i kopia dla telefonu), `migawka.py --cicho` (Notatnik i zadania), `wiedza_karty.py aktualizuj --cicho --publikuj`
(nowe tezy → karty). Wieczorny przegląd o 22:45, tygodniowy w niedzielę wieczorem. Gdy nic nowego – przebieg kończy się bez zapisów.

**Sesja Claude Code w repo:** lista wyboru na starcie, domyślnie nic (`CLAUDE.md`). „Indeks wiedzy” = `sync --publikuj --cicho` + `wiedza_jakosc.py przypomnij --cicho`.
Po zapisie wiedzy do Notion w sesji interaktywnej: `python3 tools/wiedza.py sync --publikuj`.

**Noc (inwestor uruchamia):** strona kolejki (start – `README-lokalne.md`) → zaznaczenie filmów i artykułów → polecenie do terminala. Kolejka przerabia pozycje
(tezy → porównanie z całym tematem → zapis do Notion), po każdej odświeża indeks, co N-te pytanie robi kontrolę wyrywkową, na końcu publikuje kopię i uruchamia
obserwatora oraz sędziego. Limit tygodnia pilnuje ustawienie `tydzien_stop`. Rano: raport „W pigułce” każdej pozycji w zakładce Przerobione.

**Telefon:** pytanie → karta (`karty --do`, `karta KOD`), odpowiedź z numerami WI i „Na czym się opieram”; zapis, gdy w rozmowie brak Notion → „📥 Skrzynka”
(przebieg godzinowy przenosi wpisy do Notion i odpowiada w okienku pod wpisem, gdy czegoś brakuje).

## 3. Komunikaty `[wiedza]`, `[jakosc]`, `[karty]`

- `[wiedza] …` i `✗ …` z `tools/wiedza.py`, `wiedza_sens.py`, `migawka.py` – tabela z działaniami: `references/indeks-awarie.md`.
- `[jakosc] alarmy jakości wyszukiwania …` – po zmianie szukania nie wydawaj zmiany bez wyjaśnienia; bez zmiany kodu zobacz `stan` i ostatni `sync`;
  `[jakosc] obserwator nie działa: Typ` – uruchom `python3 tools/wiedza_jakosc.py raport` i przeczytaj błąd; opis i progi alarmów: `references/indeks-jakosc.md`.
- `[karty] …` z `tools/wiedza_karty.py` (kody wyjścia: 0 sukces, 1 błąd, 3 stop na budżecie albo limicie – stan zapisany, wznowienie tym samym poleceniem,
  gotowe porcje z cache):
  - „trwa inny przebieg kart (karty.json zajęty)” – inny przebieg trzyma blokadę; poczekaj albo sprawdź, czy proces żyje (`pgrep -fl wiedza_karty`);
  - „limit tygodnia n% ≥ --stop-tydzien” / „okno 5-godzinne wyczerpane” – poczekaj na odnowienie limitu, nie ponawiaj na siłę;
  - „porcje z błędem … uruchom ponownie” – błędy są w `karty.json` (pole `bledy`); powtórzenie tego samego polecenia dokończy tylko braki;
  - „indeks zajęty (sync albo publikacja) – zapis w następnym przebiegu” – nic do zrobienia, zapis dogoni następny `aktualizuj`;
  - „--publikuj niedozwolone przy WIEDZA_KARTY_POLECENIE” – zmienna testowa zostawiona w środowisku; usuń ją.
- Prefiks przy ostrzeżeniu o limicie czasu startu (`110 s`) i „publikacja odłożona”: `indeks-awarie.md`.

## 4. Jak mierzyć i jak czytać liczby

Zasada ogólna: **porównuj na tym samym stanie bazy** (baza zmienia się co noc i po scalaniach) – wariant bazowy i nowy tego samego dnia, raportuj różnicę.

| Pomiar | Polecenie / miejsce | Co znaczy wynik |
|---|---|---|
| Obserwator (stałe zbiory pytań i znanych wierszy) | `python3 tools/wiedza_jakosc.py zloty`, `raport` | success@12, MRR, P@12; alarm = spadek względem poprzedniego przebiegu i bazy. Po dużych zmianach bazy `zloty --odnowa`; zmiany przyjęte przez inwestora `--ustaw-baze` |
| Przypadek „tego nie znalazł” | `wiedza_jakosc.py dodaj "pytanie" --powinno WI-12,WI-40` | od teraz każda strata to alarm |
| Sędzia LLM | `wiedza_jakosc.py sedzia` (na sucho), `--wyslij` (zużywa tokeny) | ocena sensu wyników 0/1/2; zgodność z oceną ręczną liczona regułą „trafny” ↔ 2 |
| Ocena ręczna | `wiedza_jakosc.py reczna --n 30` (tylko inwestor, w terminalu; 30–45 min) | punkt odniesienia dla sędziego; raz po większej zmianie szukania |
| Porównanie z Notion | `wiedza_jakosc.py notion`, `pokaz` | przybliżenie dawnej drogi, nie wyszukiwarka MCP |
| Pokrycie kart | `wiedza_karty.py pomiar [--dopelnienie] [--zapisz] [--brakujace]` | odsetek trafnych tez wzorca na karcie (K = tylko Kluczowe); to miara wobec jednego wzorca, nie „prawdy absolutnej” |
| Odpowiedź czatu (pomiar „Z1”) | narzędzie oceny czatu poza repo, zamrożony zestaw pytań i wzorca w katalogu jakości | recall@widziane, długość wyniku, kompletność odpowiedzi od początku do końca; wariant bazowy zawsze obok nowego |
| Kontrola wyrywkowa, mini-audyt, trend czatu | zakładki Kontrola i Indeks strony kolejki; mini-audyt co miesiąc | kontrola – trafność indeksu vs Notion; mini-audyt – ile powiązań z istniejącą wiedzą uwzględniono przy zapisie nowych źródeł |

Czytanie: 1) liczba bez porównania niczego nie znaczy; 2) pogorszenie na zamrożonym zestawie = nie wydawaj zmiany, zgłoś; 3) „pokrycie: niemierzone” to nie błąd, tylko brak
pomiaru; 4) zbiory oceny zawierają wiersze, które wypadły z bazy (Nieaktualne, scalone) – po scalaniu spodziewany alarm KI, wtedy `zloty --odnowa` i odnotuj w raporcie.
Koszty: sędzia, mini-audyt i budowa kart zużywają limit tygodnia konta; sprawdź stan limitu przed dużym pomiarem.

## 5. Awarie i co robić

### 5.1 Automat launchd nie działa

Objaw: brak nowych linii „🤖” w Dzienniku, puste albo stare logi, „kopia aktualna: nie” od rana, brak przebiegów w `launchctl list`.

1. **Czy załadowane:** `launchctl list | grep pl.dom` – mają być `pl.dom.przeglad-szybki`, `-wieczorny`, `-tygodniowy` (kolumny: PID, ostatni kod wyjścia, etykieta).
   Brak – załaduj: `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/<plist>`; po zmianie pliku najpierw `launchctl bootout gui/$(id -u)/<etykieta>`.
2. **Co mówi log:** w `<folder budowy>/.dom/automaty/` – `<tryb>-RRRR-MM-DD.log` (start, kod wyjścia, czas, koszt), `stan.json` (ostatni start, koniec, kod, koszt na tryb),
   `launchd-<tryb>.log` (surowe wyjście launchd). Kod wyjścia: **0** ok; **1** błąd przebiegu; **2** brak logowania MCP notion (linia „NOTION: brak logowania” → 5.2);
   **3** przekroczony limit czasu; **4** brak sieci (przed startem sprawdzane: hosty Notion, API modelu i stan `claude mcp get notion`; szybki kończy od razu i ponawia za godzinę,
   wieczorny i tygodniowy ponawiają co 5 min do 45 min).
3. **„Operation not permitted” w `launchd-<tryb>.log`:** macOS (TCC) odmawia stubowi `/usr/bin/python3` dostępu do plików w Dokumentach. W plistach `ProgramArguments` musi
   zaczynać się od pełnej ścieżki Pythona z frameworka Command Line Tools:
   `/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3`, a `Python.app` z tego frameworka musi mieć „Pełny dostęp do dysku”
   (Ustawienia systemowe → Prywatność i ochrona). Po aktualizacji Command Line Tools sprawdź, czy ścieżka i wersja (3.x) wciąż istnieją i czy dostęp nadal jest nadany.
   Test: tymczasowy plist, który wykonuje `-c "open('<ścieżka skryptu>')"`.
4. **Czy Mac spał:** launchd z `StartCalendarInterval` nie uruchamia zadań w uśpieniu; pominięte uruchomienia scala w jedno po wybudzeniu. Mac wyłączony w porze zadania –
   przebieg przepada (wpisy poczekają na następny). Wieczorny po przegapionej porze uruchom ręcznie: `python3 <katalog automatów>/przeglad.py wieczorny`.
5. **Próba ręczna:** `python3 <katalog automatów>/przeglad.py --sprawdz` (przebieg bez Notion: ma wypisać „notion MCP: zalogowany” i odpowiedź `OK`).
6. **Kopia dla telefonu mimo to świeża?** `python3 tools/wiedza.py sync --publikuj` i `python3 tools/migawka.py` ręcznie; `wiedza_karty.py aktualizuj --publikuj`. Zadania na claude.ai nie
   mogą jednocześnie chodzić (dublowanie) – gdy launchd działa, zaplanowane zadania claude.ai wyłączone.
7. **Wyłączenie jednego automatu:** `launchctl bootout gui/$(id -u)/<etykieta>`; zmiana godzin: edytuj `StartCalendarInterval` w pliku plist, skopiuj do `~/Library/LaunchAgents/`, bootout + bootstrap.
8. **Lokalny automat trybu głębokiego (`pl.dom.pytania`)** jest zapasowy (primary: GitHub Actions, 5.7); nie musi być załadowany.

### 5.2 Konektor Notion zniknął

Są trzy niezależne drogi do Notion – rozróżnij, która nie działa:

| Droga | Kto jej używa | Objaw | Naprawa |
|---|---|---|---|
| Token integracji (API, `NOTION_TOKEN`) | `sync`, `migawka.py`, kontrola nocna | `[wiedza] … HTTP 401/403`, w migawce „niedostępna” | integracja usunięta albo strona nieudostępniona integracji → udostępnij stronę DOM; token wygasł → 5.8 |
| Lokalny serwer MCP `notion` (Mac) | automaty launchd, nocna kolejka (zapisy), sesje Claude Code | kod 2, „NOTION: brak logowania” | `claude` → `/mcp` → `notion` → logowanie w przeglądarce; `claude mcp get notion` ma pokazać połączenie; brak serwera: `claude mcp add --transport http --scope user notion https://mcp.notion.com/mcp` |
| Konektor „Notion” na claude.ai | czat na telefonie i w przeglądarce | w rozmowie brak narzędzi Notion („not connected”), konektor wyłączony albo zablokowany przez organizację | patrz niżej |

Konektor na claude.ai zniknął albo jest zablokowany: **to nie jest powód do odmowy**. Asystent (zasada 13 w `budowa`, zasada 11 w `ja`) przechodzi w tryb bez Notion:
wiedza z indeksu (karty, `szukaj`), Notatnik i zadania z migawki (`migawka.md`), a każdy zapis (notatka, dziennik, zadanie, wiedza) do dokumentu „📥 Skrzynka” słowami, bez pól Notion;
przebieg godzinowy na Macu przenosi go do Notion. Co zrobić: sprawdź w ustawieniach claude.ai, czy konektor jest włączony i zalogowany (po zmianie hasła lub polityki organizacji logowanie
trzeba powtórzyć); jeśli organizacja go blokuje – zostaw tryb bez Notion i automaty launchd (5.1). Zaplanowane zadania claude.ai wyłączone, gdy ich pracę robi launchd.
Po powrocie konektora Skrzynkę opróżnia przebieg godzinowy (albo „przerób skrzynkę” w rozmowie).

### 5.3 Telefon mówi „indeks niedostępny” (albo „brak w tej kopii”)

Czat zgłasza to, gdy nie pobierze `wiedza.sqlite` i `wiedza.py` z prywatnego repo kopii. Idź po kolei:

1. **Na Macu:** `python3 tools/wiedza.py stan` – czy jest plik, `publikacja:` (data ostatniej wysyłki) i `kopia aktualna: tak/nie`. Nie: `python3 tools/wiedza.py publikuj --teraz`;
   po odtworzeniu repo kopii `publikuj --wymus`. Błąd HTTP 401/403/404 przy publikacji → token `GITHUB_TOKEN_SYNC` (5.8) albo zła nazwa w `GITHUB_REPO`; 301 – repo przemianowane,
   wpisz nową nazwę; „repo nie jest prywatne” – popraw (nie publikuj do publicznego).
2. **Czy czat ma dostęp:** token odczytu (`GITHUB_TOKEN_SEARCH`) wygasł, został unieważniony albo strona „🔑 Asystent – dostęp” ma starą wartość → odnów wg 5.8 i zaktualizuj stronę
   oraz plik dostępu w projekcie „Dom”. Czat na claude.ai musi mieć wyjście do sieci do GitHuba (ustawienie konta).
3. **Czy czat czyta stronę dostępu:** bez narzędzi Notion w rozmowie wartości bierze z pliku „🔑 Dostęp asystenta” w wiedzy projektu „Dom” (rozmowa w projekcie); poza projektem i bez Notion
   poproś o rozmowę w projekcie.
4. **„Karty: brak w tej kopii”:** kopia sprzed zbudowania kart albo bez nich – na Macu `python3 tools/wiedza_karty.py zapisz --publikuj`. Starszy `wiedza.py` nie zna polecenia `karty`
   (błąd „invalid choice”) – `publikuj --wymus` wyśle świeży `wiedza.py` razem z indeksem. Do tego czasu czat idzie drogą zapasową (`szukaj`, poziomy).
5. **Stare dane:** daty w kopii są informacyjne – bez nowych danych nie ma nowej publikacji. Starsze niż doba przy działających automatach to sygnał do 5.1.

### 5.4 Indeks się rozjechał z Notion

Objawy: wiersz usunięty w Notion wciąż jest w wynikach; `stan` – `zbudowano` starsze niż 7 dni albo `ostatni pełny sync` starszy niż 14 dni; liczniki różnią się od Notion;
„kopia aktualna: nie”; alarm obserwatora tuż po dużych zmianach bazy.

1. `python3 tools/wiedza.py stan` (liczniki, daty, stan list podobnych i kart).
2. `python3 tools/wiedza.py sync --pelny` – pełny listing i usunięcie wierszy nieobecnych w Notion (zwykły `sync` pobiera tylko zmiany; pełny idzie sam co 7 dni).
3. `python3 tools/wiedza.py publikuj --teraz` (bez odstępu 60 min).
4. Odciski i podobne: `python3 tools/wiedza_sens.py stan`, brak lub zaległości → `python3 tools/wiedza_sens.py przelicz`. Wymaga działającej Ollamy.
5. Karty: `python3 tools/wiedza_karty.py aktualizuj --publikuj` (nowe tezy) albo `zapisz --publikuj` (stan kart → indeks po przebudowie indeksu).
6. Sprawdzenie: `python3 tools/wiedza_jakosc.py zloty`; alarm po scaleniu/archiwizacji wierszy zbioru kontrolnego jest spodziewany → `zloty --odnowa`.
7. Uszkodzony plik: `indeks-awarie.md`, sekcja „Uszkodzony indeks” (`sync` odkłada zepsuty plik i buduje od nowa).
8. Bardzo duża historia kopii (`stan`: ostrzeżenie ok. 500 MB) – `publikuj --reset` (jeden commit zastępuje historię; starych wersji nie odzyskasz).

### 5.5 Przeliczenie odcisków po zmianie modelu

Odciski leżą w `.dom/wiedza/wektory.sqlite`, listy podobnych w tabeli `podobne` indeksu. Po zmianie modelu (np. innego niż `bge-m3`):

1. `ollama pull <model>`, zmień `"model"` w `.dom/sens.json`.
2. `python3 tools/wiedza_sens.py przelicz` – odciski liczone innym modelem są liczone od nowa (ok. kilku minut), listy podobnych też; `--pelny` buduje od nowa tylko listy podobnych z istniejących odcisków. W trakcie `szukaj --sens` nie jest wiarygodne.
3. `python3 tools/wiedza_sens.py stan` – model i liczba odcisków mają się zgadzać z liczbą informacji.
4. `python3 tools/wiedza.py publikuj --teraz` – nowe listy podobnych jadą do kopii czatu.
5. Zmierz: `wiedza_jakosc.py zloty` i pomiar odpowiedzi czatu (4) – przed i po tego samego dnia. Karty nie zależą od odcisków (wybiera je model Claude), więc ich nie przebudowuj.
6. Wyłączenie odcisków: `"zrodlo": "brak"` – szukanie po słowach działa jak dotąd, sekcja „Podobne” znika.

### 5.6 Karty są nieaktualne albo źle wyglądają

- **Brakuje nowych tez na karcie:** przebieg godzinowy dołącza je przy najbliższym `aktualizuj`; do tego czasu są w „Dopełnieniu z szukania”. Ręcznie: `python3 tools/wiedza_karty.py aktualizuj --publikuj`.
- **Karta za duża na telefon (więcej niż ok. 75 tys. znaków, więcej niż 3–4 części):** `python3 tools/wiedza_karty.py ocen --karty KOD --zastosuj`, potem `pomiar --zapisz`
  i `zapisz --publikuj`. `ocen` ocenia tylko tezy bez oceny (oceny w `oceny.json`), więc ponowne uruchomienie kosztuje tylko nowe tezy; przed zastosowaniem tworzy kopię `karty.json.przed-ocena`.
- **Tezy „czekają na ocenę”** (komunikat `aktualizuj`): wpis zostaje w rdzeniu jak przed oceną i zostanie oceniony przy następnym przebiegu; `ocen` załatwia zaległości od ręki.
- **Podział albo nowa karta:** zmiana definicji w `definicje.json` → `definicje --sprawdz` → `zbuduj --karty KOD` → `ocen --karty KOD --zastosuj` → `pomiar --zapisz` → `zapisz --publikuj`.
  Przed `zbuduj` sprawdź limit tygodnia i zaproponuj kartę inwestorowi.
- **Karty z kopii zapasowej a indeks:** `zapisz` nadpisuje tabele kart w indeksie z `karty.json` i definicji; nie poprawiaj ich ręcznie w SQLite.

### 5.7 Tryb głęboki bez odpowiedzi

1. Czat zostawił pytanie? W repo kopii: `pytania/<ID>.json`; odpowiedź: `odpowiedzi/<ID>.md`; znacznik pracy: `odpowiedzi/<ID>.w-toku` z polem `krok` („w kolejce”, „wybór tez”, „odpowiedź”, „czeka na limit”).
2. Zakładka Actions repo kopii: uruchomienie `tryb-gleboki` (po każdym zapisie do `pytania/` i co kilka godzin dla pytań czekających na limit); czerwone = błąd; ręcznie „Run workflow”.
3. Typowe przyczyny: sekret `CLAUDE_CODE_OAUTH_TOKEN` wygasł lub unieważniony (kroki w logu kończą się błędem logowania) → wystaw nowy token Claude Code i podmień sekret; limit konta (krok „czeka na limit”,
   pytanie wraca przy następnym uruchomieniu); token zapisu pytań (`GITHUB_TOKEN_PYTANIA`) wygasł (telefon dostaje kod inny niż 201 → „tryb głęboki niedostępny”).
4. Zapasowo: lokalny skrypt Maca (`pytania.py`) – `--sprawdz`, potem `--pytanie "…"`; odpowiedź ląduje w katalogu automatów. Nie usuwaj z repo samej odpowiedzi – pytanie bez `<ID>.md` zostanie policzone od nowa.

### 5.8 Token wygasa albo wygasł

Co mówią dokumenty o terminach: **token odczytu kopii (`GITHUB_TOKEN_SEARCH`) wystawiono na 90 dni; odnów go z zapasem co najmniej dwóch tygodni** (konkretna data jest na stronie „🔑 Asystent – dostęp”,
w `indeks-awarie.md` i w lokalnym README). Dla pozostałych tokenów dokumentacja **nie podaje terminu ważności** – nie zakładaj, że są bezterminowe: sprawdź ważność w ustawieniach GitHub, Notion albo
Claude Code i wpisz przypomnienie w kalendarzu, a datę zanotuj w lokalnym README (nie w repo).

| Token / sekret | Gdzie leży | Kto używa | Objaw wygaśnięcia | Odnowienie |
|---|---|---|---|---|
| `GITHUB_TOKEN_SEARCH` | `.dom/sekrety.env` + strona „🔑 Asystent – dostęp” + plik dostępu w projekcie „Dom” | czat na telefonie (odczyt kopii) | czat: „indeks niedostępny”; HTTP 401 przy pobraniu | wystaw nowy, tylko odczyt, jedno repo; wpisz w `sekrety.env` i na stronie dostępu (jedyne dozwolone miejsce poza plikiem); odśwież plik dostępu w projekcie; unieważnij stary |
| `GITHUB_TOKEN_SYNC` | `.dom/sekrety.env` | Mac (publikacja kopii, migawka) | `[wiedza] … HTTP 401/403` przy `publikuj` | wystaw nowy (zapis do repo kopii), podmień, unieważnij stary, `publikuj --teraz` |
| `GITHUB_TOKEN_PYTANIA` | `.dom/sekrety.env` + sekcja „Tryb głęboki” pliku dostępu | telefon (zapis pytania) | czat: „tryb głęboki niedostępny (kod 401/403)” | wystaw nowy (zapis do repo kopii), podmień w obu miejscach, odśwież plik dostępu, unieważnij stary |
| `NOTION_TOKEN` | `.dom/sekrety.env` | `sync`, `migawka.py`, kontrola | `sync`: błąd 401; migawka „niedostępna” | integracja tylko do odczytu: utwórz nową, udostępnij jej stronę DOM, podmień wartość, usuń starą |
| MCP `notion` (logowanie OAuth, Mac) | konto Claude Code na Macu | automaty launchd, kolejka, sesje | kod 2, „NOTION: brak logowania” | 5.2 |
| `CLAUDE_CODE_OAUTH_TOKEN` | sekret repo kopii (GitHub Actions) | tryb głęboki | workflow czerwony na kroku modelu | nowy token Claude Code (`claude setup-token`), podmień sekret |
| Logowanie `claude` na Macu | konto Claude Code | automaty, sędzia, karty, kolejka | przebiegi kończą się błędem logowania, kod 1 | `claude` → zaloguj ponownie |

Zasady odnowienia: wartość wpisujesz **tylko** do `sekrety.env` i – dla tokenów czatu – na stronie dostępu; nie wklejasz do rozmowy. Wystawiony token, który przeszedł przez rozmowę, log albo
zrzut ekranu, uznaj za ujawniony i wymień. Nowy token ma najmniejsze możliwe uprawnienia (jedno repo, odczyt tam, gdzie wystarczy). Szczegóły i kroki: `references/indeks-awarie.md`, „Odnowienie tokenów”.

### 5.9 Inne

- **Skrzynka zalega** (pozycje bez śladu w „Przetworzone”): uruchom przebieg godzinowy ręcznie (`przeglad.py szybki`) albo w rozmowie „przerób skrzynkę”; niejasne wpisy czekają we „Wpisach” z okienkiem ❓.
- **Nocna kolejka nie rusza po przerwie:** `python3 kolejka_zdrowie.py` (kod 0 = sprawna; **uwaga:** naprawia dane kolejki i może przywracać pliki z kopii – uruchamiaj, gdy kolejka nie pracuje:
  `pgrep -fl "kolejka_run|kanal_do_notion|kurs_do_notion"`). Kolejka sama nie sprawdza logowania MCP notion ani sieci przed startem – przed nocą wykonaj `claude mcp get notion`.
- **Prywatność:** zablokowany commit przez hook (`pre-commit`, `commit-msg`, `pre-push`) znaczy, że w diffie jest coś z listy zakazanych; usuń dane z pliku, nie omijaj hooka (`--no-verify` zabronione).
  Dane, które trafiły na GitHuba, nie wracają – zatrzymaj się i poinformuj inwestora.

## 6. Słowniczek

| Pojęcie | Znaczenie |
|---|---|
| **WI-n** | informacja (teza) w bazie Informacje; atomowa, z pochodzeniem i Istotnością (Kluczowe, Ważne, pozostałe, Ciekawostka) |
| **ZRD-n** | źródło (film, artykuł, rozmowa, dokument) z typem autora, konfliktem interesów i wiarygodnością |
| **SP-n** | sprzeczność w Rejestrze sprzeczności (czeka na decyzję inwestora albo rozstrzygnięta) |
| **Indeks** | lokalna kopia baz wiedzy w jednym pliku SQLite (FTS5), tylko do odczytu; `wiedza.sqlite` |
| **Kopia dla czatu** | indeks, `wiedza.py` i migawka w prywatnym repo; telefon pobiera je tokenem odczytu |
| **Odcisk (znaczenia)** | wektor liczbowy tezy policzony lokalnie modelem embeddingów (Ollama, bge-m3); pozwala szukać po sensie |
| **Podobne** | lista najbliższych znaczeniowo tez dla każdej tezy, policzona na Macu i wysłana do kopii (telefon nie liczy odcisków) |
| **Karta** | gotowy wybór tez (lista WI) do rodziny pytań (karta pytań: rdzeń + rozszerzenie) albo do czynności (karta czynności: tagi) |
| **Rdzeń / rozszerzenie** | rdzeń: ocena 2 plus najlepsze oceny 1 do 200 tez; rozszerzenie (`karta KOD --wiecej`): reszta pokrewnych |
| **Pokrycie** | jaka część trafnych tez wzorca jest na karcie (K – tylko Kluczowe); miara wobec jednego wzorca |
| **Wzorzec** | zamrożony zestaw trafnych tez dla pytań inwestora, do którego mierzy się pokrycie i recall |
| **Obserwator** | `wiedza_jakosc.py zloty`: stałe zbiory pytań i znanych wierszy z alarmem przy regresji szukania |
| **Sędzia** | model Claude bez narzędzi oceniający sens wyników (0/1/2) |
| **Tryb głęboki** | odpowiedź na pytanie złożone oparta na całej bazie, liczona poza telefonem (Actions albo Mac) |
| **Migawka** | otwarte wpisy Notatnika i zadania w jednym pliku Markdown dla czatu bez Notion |
| **Skrzynka** | dokument Claude „📥 Skrzynka” – zapisy z telefonu, gdy Notion w czacie nie działa |
| **Etap porównania** | nocny krok kolejki: każda nowa teza porównywana z całym tematem przed zapisem (powtórzenie, potwierdzenie, uzupełnienie, sprzeczność, nowa) |
