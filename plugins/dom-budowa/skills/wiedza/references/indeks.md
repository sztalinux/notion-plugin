# Indeks wiedzy – jak używać

Cel: znaleźć w Bazie wiedzy informacje, tematy i sprzeczności szybko, bez przeszukiwania Notion (jest wolne i limitowane).
Indeks to lokalna kopia czterech baz (SQLite FTS5), tylko do odczytu. Notion zostaje jedynym źródłem prawdy i jedynym
miejscem zapisu – nigdy nie zapisuj wiedzy do indeksu. Trzy kanały dostępu mają różne polecenia; wybierz swój.
Ten plik opisuje polecenia. **Jak szukać i odpowiadać na pytanie** (karta wiedzy, kilka sformułowań, głębokość, cały temat,
Notatnik, forma odpowiedzi) – `pytanie-do-bazy.md`; czym są karty i jak Mac je utrzymuje – `karty.md`.

## Claude Code – sesja interaktywna w repo

Indeks odświeża się na żądanie – pozycją „Indeks wiedzy” z listy startowej Claude Code albo poleceniem `sync` poniżej; bez tego bywa
nieaktualny. Polecenia uruchamiaj z katalogu repo:
- `python3 tools/wiedza.py szukaj "przerwa robocza płyta" [--etap "Stan zero"] [--limit 12]` – wpisz 2–4 słowa
  treściowe, bez zdania i spójników („czy”, „jak”, „na” program i tak odrzuci). Końcówki fleksyjne program przycina sam,
  więc „drenażu” znajdzie też „drenaż” (wyżej stoją informacje z dokładnie wpisaną formą). `drena*` (prefiks)
  i „fraza w cudzysłowie” zostają dokładnie takie, jak wpisano. Gdy do wszystkich słów pasuje mniej niż 12 widocznych
  informacji, program dopisuje pod nimi pasujące do części słów (nie przy zapytaniu z samych słów wypełniających) –
  przy pytaniach z 3+ słowami to zwykły przypadek. Nagłówek mówi wtedy „(dopasowanie częściowe od pozycji k)”,
  a `--json` – `"czesciowe": true` i `"pelnych": n` (k = n + 1; n = ile informacji ma wszystkie słowa, 0 = żadna).
  Dopisane linie idą od pasujących do największej liczby słów; traktuj je jak wskazówkę i nie opieraj na nich
  odpowiedzi bez przeczytania tezy. Mało pełnych trafień (`pelnych` 0–2) → zapytaj krócej, o jedno pojęcie naraz
  (np. „przemarzanie”, potem „posadowienie”). Domyślnie pomija Nieaktualne i Ciekawostki (z licznikiem);
  `--ciekawostki` pokaże też je. Zero linii wyniku po filtrach to nie brak wiedzy – zobacz liczniki `pominięto`
  i rozluźnij filtr. Przy 3+ słowach nagłówek podaje też poziomy dopełnienia: ile linii pasuje do co najmniej połowy
  słów, ile do któregokolwiek (`--json`: pole `poziom`).
- Kilka sformułowań naraz: `szukaj "woda przy ławie" "drenaż opaskowy" "odwodnienie fundamentu"` – każde szukane
  osobno, wyniki połączone bez powtórzeń (wyżej te, które znalazło kilka sformułowań); przy linii `WI-n [1,3]` –
  numery sformułowań, które ją znalazły. Jedno zapytanie działa jak dotąd.
- `--krotko` – zwarta linia (domyślnie 25 linii, ok. 1/3 długości pełnej):
  `WI-n · Istotność · Etap · [Status, gdy nie „Nowe”] · teza (do 220 zn.) · T: tematy (do 3) · źr: ZRD-n typ autora/wiarygodność [· Notatnik] · SP-n · 💬`.
  Bez tytułów źródeł, „Kto”, linków i treści komentarza – gdy ich potrzebujesz (reguła niezależności źródeł,
  `wiedza`, A.5; komentarz inwestora 💬, sekcja H), uruchom pełne `szukaj` albo otwórz stronę w Notion. Otwarte SP
  niesione tylko przez dalsze trafienia – same numery w jednej linii. Przy jednym zapytaniu linie pasujące do pojedynczego
  słowa odpadają, gdy pełnych trafień i trafień „co najmniej połowa słów” jest razem 12 lub więcej.
  Pod trafieniami sekcja „Podobne do trafień (po znaczeniu)”: do 8 linii `WI-n ≈WI-m` – informacje bliskie znaczeniem
  trafieniu WI-m (jednemu z 5 pierwszych), także opisane innymi słowami albo z innego tematu. To podpowiedź:
  przeczytaj tezę, zanim ją uwzględnisz – bywa o sąsiednim zagadnieniu. Brak sekcji = kopia bez list podobnych
  albo nic nie przekracza progu.
- `--sens` (tylko Mac, gdy działa Ollama) – ranking po słowach łączony z rankingiem po znaczeniu zapytania; łapie
  informacje opisane innymi słowami niż pytanie. Bez Ollamy nagłówek mówi „sens: niedostępny – same słowa” i wynik
  jest zwykłym `szukaj`.
- `python3 tools/wiedza.py temat "NAZWA"` – stan wiedzy tematu, Kluczowe i otwarte SP; `--lista` – wszystkie widoczne
  informacje tematu (Kluczowe, Ważne, pozostałe; Ciekawostki z `--ciekawostki`), zwykle z `--krotko`;
  `python3 tools/wiedza.py etap "Stan zero" --czesc 1` – cała wiedza etapu: tezy Kluczowe i Ważne etapu i „Cała budowa”
  pogrupowane tematami (linia `WI-n · Istotność · [Status] · pełna teza · [Notatnik] · SP-n · 💬`, bez źródeł), potem
  Kluczowe z innych etapów (z Etapem w linii) i otwarte SP etapu; `--kontrola` dokłada Ważne rodzaju Kontrola / odbiór
  i Kolejność prac z innych etapów; `--czesc k` pokazuje k-tą część po ok. 25 tys. znaków (nagłówek: liczba tez, znaków, części,
  „dalej --czesc k+1”), bez `--czesc` całość naraz (Claude Code, do pliku). Część nazwy etapu wystarcza; niejednoznaczna →
  lista etapów. Poziom „cały etap” (`pytanie-do-bazy.md`, pkt 3) tylko w Claude Code na Macu – na telefonie karta wiedzy (niżej);
  `duplikaty [--od RRRR-MM-DD]` – kandydaci na duplikaty: pary z list podobnych od progu 0,84 (`--sens`; bez list –
  po słowach, `--slowa` wymusza słowa). Podobieństwo nie odróżnia duplikatu od informacji bliskiej tematem (ok. 1 na 10 par to
  duplikat) – każdą parę oceń sam, zanim zaproponujesz scalenie; `stan` – liczniki, daty, stan list podobnych i kart (linia
  `karty: n (pytania a, czynności b) · zbudowano <data>` albo `karty: brak`).
- `python3 tools/wiedza.py karty [--rodzaj pytanie|czynnosc] [--etap NAZWA]` – spis kart wiedzy (gotowych wyborów tez do typowych pytań;
  `karty.md`) pod nagłówkami `## Karty pytań` i `## Karty czynności`, po linii na kartę (pola, nie kolumny):
  `kod · etap · nazwa · tez N (K n)[ +m ciek.][ +r więcej] · ~N tys. zn. · k cz.[ · pokrycie X% / K Y%] · opis[ · np. „przykładowe pytanie”]` – pokrycie
  tylko zmierzone, `+r więcej` = tezy rozszerzenia (pokrewne, poza rdzeniem; `karta KOD --wiecej`), przykładowe pytanie tylko karta pytań; `tez 0 (K 0) · ~0 tys. zn. · 0 cz.` = karta jeszcze niezbudowana. `karty --do "A" "B" "C"`
  zamiast spisu drukuje `## Dopasowanie do pytania (trafień w karcie / N)` (N ≤ 60 pierwszych trafień szukania): do 12 kart, najlepsza pierwsza
  (wg wagi trafień – wyższe pozycje wyniku ważą więcej – nie zawsze wg liczby), każda jako `trafień n/N · <linia karty jak wyżej>`; potem
  `trafienia poza wszystkimi kartami: m – WI-…` (do 15 numerów, dalej „… (+k)”) i `## Pozostałe karty` z samymi kodami; gdy żadna karta nie
  ma trafień: „żadna karta nie ma trafień – użyj szukaj”. Nagłówek (`# indeks: stan … · karty: n (pytania a, czynności b) · zbudowano …`)
  przypomina, by wybierać karty do ok. 75 tys. znaków razem.
- `python3 tools/wiedza.py karta KOD [KOD2 …] --pytanie "A" "B" "C" --czesc k` – treść karty w częściach po ok. 25 tys. znaków (kilka kodów =
  suma bez powtórzeń). Nagłówek: `# indeks: stan … · karta: kod „Nazwa” · tez N (Kluczowe n, Ważne m)[ (+c ciekawostek – --ciekawostki)] · znaków N tys.
  · części n · <pokrycie>[ · dopełnienie d] · część k/n – dalej --czesc k+1` (ostatnia część: `część n/n (ostatnia)`). `<pokrycie>` to `pokrycie X%
  trafnych / Y% Kluczowych (wobec wzorca <data> (<ID wzorca>, …)[; z dopełnieniem Z%])` albo `pokrycie: niemierzone` (karta czynności: `… (karta
  czynności – tagi modelu)`; karta pytań – także po `zbuduj`, dopóki `pomiar --zapisz` nie zapisze pokrycia); kilka kart o różnym pokryciu –
  `kod: …; kod2: …`. Sekcje: `## Kluczowe (n)` – wszystkie Kluczowe karty, na początku; `## <temat> – Ważne (n)` wg tematów (część zaczynająca się
  w środku sekcji powtarza jej nagłówek z „(c.d.)”); `## Ciekawostki (n)` – domyślnie na końcu karty (`--bez-ciekawostek` ukrywa); `## Dopełnienie z szukania (n)` – do 20 trafień
  szukania dla A/B/C spoza karty albo `## Dopełnienie z szukania: brak – szukanie nic nie dodaje do karty`; `## Otwarte sprzeczności (n)`. Karta
  bez tez: `tez 0 (Kluczowe 0, Ważne 0)` i „karta pusta – użyj szukaj / temat / etap” (z `--pytanie` – sama sekcja dopełnienia). `--wiecej` drukuje rozszerzenie karty
  zamiast rdzenia (tezy pokrewne; nagłówek rdzenia podaje „rozszerzenie: +n tez pokrewnych (karta KOD --wiecej, …)”) – czytaj po rdzeniu,
  na „więcej” / „rozwiń”. Nieznany kod:
  `✗ karta „kod”: nie ma takiej karty – podobne: …` (bez podobnych: „spis kart: karty”), kod wyjścia 1. Kiedy i jak z tego korzystać –
  `pytanie-do-bazy.md`, pkt 2.
- `python3 tools/wiedza.py zrodla WI-12 WI-34 …` albo `zrodla --temat "NAZWA"` – źródła podanych tez (albo wszystkich widocznych
  tez tematu) pogrupowane: „Nasze rozmowy i notatki” (forma Telefon / Spotkanie / Notatki własne albo typ autora „Nasz projektant /
  wykonawca”) osobno, potem wg typu autora (Kierownik / inspektor, Twórca / popularyzator, Niezależny wykonawca, Producent, Inny).
  Linia: `ZRD-n „tytuł” · Kto · typ autora · wiarygodność · forma · data · link · tezy: WI-…`; w grupie najpierw źródła wielu tez.
  Nagłówek: liczba tez i źródeł, tezy bez źródła, numery spoza indeksu. Do sekcji „📚 Na czym się opieram” i listy materiałów
  (`budowa/references/na-czym-sie-opieram.md`) – karta drukuje tezy bez źródeł.
- `python3 tools/migawka.py` – migawka Notatnika budowy i TASKS (otwarte wpisy) do `.dom/wiedza/migawka.md` i do kopii
  dla czatu w prywatnym repo (Notion tylko odczyt tokenem integracji; obie bazy muszą być udostępnione integracji, inaczej
  w pliku stoi „niedostępna”). Uruchamia ją przebieg godzinowy na Macu; ręcznie po zmianach w Notatniku, gdy telefon ma je
  widzieć od razu.
- Odciski znaczenia liczy `sync` na Macu na końcu, po publikacji, gdy działa Ollama z modelem bge-m3 (nowe i zmienione
  informacje, potem listy podobnych; z `--cicho` najwyżej 20 s, reszta przy następnym sync; nowe listy trafiają do
  kopii czatu z następną publikacją). Ollama wyłączona → krok pominięty po cichu,
  wszystko inne działa jak dotąd. Pierwsze pełne liczenie (ok. 3 min) albo po zmianie modelu:
  `python3 tools/wiedza_sens.py przelicz`; `python3 tools/wiedza_sens.py stan` – czy Ollama działa i ile odcisków.
- `python3 tools/wiedza_karty.py <polecenie>` (tylko Mac, Claude Code) buduje, mierzy i utrzymuje karty: `definicje`, `importuj-tagi`,
  `taguj`, `zbuduj`, `pomiar`, `aktualizuj`, `zapisz`. Karty leżą w tabelach pliku `wiedza.sqlite` i jadą do czatu z publikacją
  indeksu; definicje i dane pomiarowe są poza repo (`.dom/wiedza/karty/`). `aktualizuj` uruchamia co godzinę automat na Macu.
  Opis poleceń, pokrycia i dodawania kart – `karty.md`.

Linia wyniku: `WI-n · Istotność · Etap · Status · teza · T: tematy · ZRD-n „tytuł” (Kto: …; typ autora; wiarygodność) · SP-n · link`.
- Segment `Kto` jest obowiązkowy: bez niego nie zastosujesz reguły „ten sam autor to nie potwierdzenie” (`wiedza`, A.5).
- Marker `ustalenie w Notatniku` w miejscu źródła: informacja nie ma źródła w bazie Źródeł, opiera się na ustaleniu
  zapisanym w Notatniku budowy. Otwórz je z linku w wierszu, zanim oprzesz na niej decyzję – indeks nie niesie więcej.
- `💬 komentarz inwestora:` na końcu linii to pole „Mój komentarz” – czytaj je i reaguj wg `wiedza`, sekcja H.
- Sekcja „Otwarte sprzeczności w trafieniach” zbiera SP ze wszystkich trafień. SP z dopiskiem „(tylko w dalszych
  trafieniach)” nie niesie żadna pokazana linia – otwórz je z linku albo zwiększ `--limit`.

Czytaj Notion (stronę z linku) mimo wyniku z indeksu, gdy:
- potrzebujesz szczegółów (Szczegóły, Fragment), podejmujesz decyzję albo zaraz zapisujesz wiedzę;
- indeks jest niedostępny (brak pliku, stara wersja schematu – wtedy `python3 tools/wiedza.py sync`) – wróć do dotychczasowej drogi;
- data stanu (nagłówek wyniku `# indeks: stan …` i `stan`) jest starsza niż 24 h – podaj ją w odpowiedzi.

Po zapisie wiedzy do Notion w sesji interaktywnej uruchom `python3 tools/wiedza.py sync --publikuj` (indeks i kopia dla czatu).

## Czat/telefon i zaplanowane zadania na claude.ai

Tu nie ma `tools/` ani repo. Przeczytaj raz na rozmowę stronę Notion „🔑 Asystent – dostęp” (`3fcf5982-09e7-810e-aaca-f2b582438924`)
i wstaw jej pola w miejsce `<GITHUB_REPO>` i `<TOKEN>`. Nigdy nie zapisuj tokena w odpowiedzi, notatce ani pliku.
Brak narzędzi Notion w rozmowie → te same pola z pliku „🔑 Dostęp asystenta” w wiedzy projektu „Dom” (rozmowa w projekcie);
poza projektem i bez Notion poproś inwestora o rozmowę w projekcie „Dom”. Pola trybu głębokiego (`GITHUB_REPO` i token zapisu) są
w sekcji „Tryb głęboki” tego samego pliku dostępu – protokół: `tryb-gleboki.md`.

```
test -s /tmp/wiedza.sqlite || curl -sf -H "Authorization: Bearer <TOKEN>" -H "Accept: application/vnd.github.raw" -o /tmp/wiedza.sqlite https://api.github.com/repos/<GITHUB_REPO>/contents/wiedza.sqlite
test -s /tmp/wiedza.py || curl -sf -H "Authorization: Bearer <TOKEN>" -H "Accept: application/vnd.github.raw" -o /tmp/wiedza.py https://api.github.com/repos/<GITHUB_REPO>/contents/wiedza.py
python3 /tmp/wiedza.py karty --do "przerwa robocza" "przerwa w betonowaniu" "szew roboczy" --db /tmp/wiedza.sqlite
```

Potem treść wybranej karty, osobnym wywołaniem na każdą część (`--czesc 1`, `--czesc 2` …; kod z listy kart, `betonowanie-plyty` to przykład),
każde poprzedzone tymi samymi dwiema liniami `test -s …`:

```
python3 /tmp/wiedza.py karta betonowanie-plyty --pytanie "przerwa robocza" "przerwa w betonowaniu" "szew roboczy" --czesc 1 --db /tmp/wiedza.sqlite
```

- Pierwsze wywołanie robi wszystko: pobiera tylko brakujące pliki (`test -s`) i uruchamia `karty --do`. Jak wybrać karty i czytać
  części – `pytanie-do-bazy.md`, pkt 2. Droga zapasowa (poziomy szybko / normalnie / dokładnie), gdy `karty` zgłosi „brak w tej
  kopii” albo pytanie jest wąskim faktem: `python3 /tmp/wiedza.py szukaj "A" "B" "C" --krotko --limit 100 --db /tmp/wiedza.sqlite` – pkt 3.
- Pozostałe polecenia (`temat`, `zrodla`, `duplikaty`, `stan`) i flagi (kilka sformułowań w jednym `szukaj`, `--krotko`
  z sekcją podobnych, `temat --lista`) mają ten sam kształt co w Claude Code, z `--db /tmp/wiedza.sqlite`. `etap --czesc k` też działa,
  ale poziom „cały etap” jest tylko dla Maca (`pytanie-do-bazy.md`, pkt 3). `--sens` tu nie działa (brak Ollamy) – daje zwykły wynik po słowach.
- `migawka.md` (ta sama droga pobrania: `test -s /tmp/migawka.md || curl … /contents/migawka.md`) – otwarte wpisy Notatnika
  budowy i zadania TASKS, odświeżane co godzinę przez przebieg na Macu (`tools/migawka.py`). Czytaj, gdy Notion w rozmowie
  nie działa (`pytanie-do-bazy.md`, pkt 5); data stanu w pierwszej linii pliku idzie do zasięgu odpowiedzi.
- Katalog `/tmp` bywa pusty w kolejnej wiadomości – `test -s` pobierze pliki ponownie (stronę dostępu masz już przeczytaną,
  nie czytaj jej drugi raz).
- Brak strony, tokena, sieci albo błąd pobrania → napisz „indeks niedostępny” i czytaj Notion bezpośrednio.
- Nie uruchamiaj `sync` ani `publikuj`. Po zapisie wiedzy napisz wprost: „indeks dogoni przy najbliższym sync na Macu”.
- Daty w kopii podawaj informacyjnie: bez nowych danych nie ma nowej publikacji, więc starsza data nie jest alarmem.

## Przebieg nocny (skrypty `claude -p`)

Katalog roboczy jest neutralny, hooków repo nie ma. Uruchamiaj wyłącznie `szukaj`, `temat`, `duplikaty` i `stan`,
przez bezwzględną ścieżkę `tools/wiedza.py` podaną w prompcie skryptu. Nigdy `sync` ani `publikuj` – sync po każdym filmie
robi skrypt. Notion przeszukuj tylko wtedy, gdy indeks nie odpowiada na pytanie. W nocy jedno zapytanie w cudzysłowie na
wywołanie i linia pełna – bez kilku zapytań naraz i bez `--krotko`: reguła niezależności potrzebuje „Kto”, a kontrola
nocna odtwarza tylko pierwsze zapytanie i czyta nagłówek pojedynczego `szukaj`.

## Ograniczenia kopii

- Kopia bez tabel kart (sprzed 2.13.0) albo bez zapisanych kart → `karty` i `karta` drukują „# karty: brak w tej kopii indeksu – użyj szukaj /
  temat / etap” (kod wyjścia 0; `stan`: „karty: brak”), a stary `wiedza.py` nie zna polecenia (błąd „invalid choice: 'karty'”). To stara kopia,
  nie błąd rozmowy: przejdź na drogę zapasową (`pytanie-do-bazy.md`, pkt 3); na Macu odświeży ją `python3 tools/wiedza_karty.py zapisz
  --publikuj` albo najbliższy `aktualizuj`. Karty pokazują stan z ostatniego zapisu (`stan`: „karty: … zbudowano <data>”) – nowsze tezy widać
  w dopełnieniu z szukania.
- Wiersze usunięte w Notion znikają z indeksu przy pełnym sync (automatycznie co 7 dni albo `sync --pelny`) – do tego czasu
  sprawdź w Notion informację, na której opierasz decyzję.
- `stan`: `zbudowano` starsze niż 7 dni albo `ostatni pełny sync` starszy niż 14 dni → uruchom `sync --pelny` ręcznie;
  `kopia aktualna: nie` → `python3 tools/wiedza.py publikuj --teraz` (samo `publikuj` bywa odłożone przez odstęp 60 min).
- Awarie, odnowienie tokenów, odtworzone repo kopii i komunikaty `[wiedza]` → `references/indeks-awarie.md`; jakość
  wyszukiwania, log zapytań, alarmy `[jakosc]` (tylko Claude Code) → `references/indeks-jakosc.md`.
