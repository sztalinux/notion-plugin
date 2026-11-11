# Kopie zapasowe – plan i kontrola (POM-21)

Dla inwestora i agentów. Cel: na pytanie „co stracę, jeśli jutro padnie Mac, konto Google, Notion albo dostęp do
asystenta” odpowiedź brzmi „nic ważnego”. Ten dokument mówi, **co** ma kopię, **gdzie** i **jak często**. Stan
sprawdza `tools/kopie.py`. Kopia dokumentów na Dysk ma osobny opis: `docs/zdjecia-i-kopia.md`, 7.

Stan wdrożenia (11.11.2026): plan, kontrola i wpięcie w przegląd tygodnia są gotowe. Kopie robi inwestor ręcznie, według
rytmu z sekcji 4. Asystent tylko sprawdza i przypomina. Czynności asystenta, które czekają na decyzje inwestora, opisuje
sekcja 7.

## 1. Zasady

- **Trzy kopie, dwa nośniki, jedna poza Makiem.** Gdy coś żyje tylko na Macu albo tylko w jednej usłudze, nie ma kopii.
- **Asystent niczego nie wysyła sam.** Nie instaluje programów, nie zmienia ustawień systemu, nie wysyła folderu `.dom`
  ani sekretów do żadnej chmury. Przygotowuje polecenia i sprawdza stan, a kopię robi inwestor.
- **Dysk zewnętrzny jest zaszyfrowany** (Finder → prawy klik na dysku → „Zaszyfruj”, albo Narzędzie dyskowe przy
  formatowaniu, APFS zaszyfrowany). Trafiają na niego `.dom` i pamięć asystenta, a zgubiony dysk nie może ich ujawnić.
- **`.dom` nie trafia na Dysk Google.** Trzyma karty, indeksy, stan automatów i plik z sekretami, dlatego kopia idzie
  tylko na dysk zewnętrzny. Zaszyfrowane archiwum na Dysku to osobna decyzja (sekcja 7).
- **Sekrety nie leżą nigdzie w jawnej postaci.** Tokeny i hasła trzymaj w menedżerze haseł. Token, który przeszedł przez
  rozmowę z AI, wymień.
- **Kopia, której nikt nie otworzył, nie jest kopią.** Raz na kwartał zrób próbę odtworzenia (sekcja 4).

## 2. Trzy warstwy

1. **Dysk zewnętrzny – wszystko, co jest na Macu.** Obejmuje folder budowy razem z `.dom`, `AI` i źródłami wiedzy,
   pamięć asystenta (katalog `memory` projektu w `~/.claude/projects/`) oraz pliki automatów launchd (`~/Library/LaunchAgents/pl.dom.*`).
   Podłączaj go raz w tygodniu. Time Machine wchodzi w plan tylko na komputerze prywatnym. Na komputerze zarządzanym przez
   organizację wymaga zgody IT, a i tak obejmowałby cudzy sprzęt, więc wystarczy ręczna kopia folderów.
2. **Chmura dla tego, co do niej pasuje.**
   - Dokumenty budowy: Dysk Google, `kopia.py` (paczka albo aplikacja).
   - Zdjęcia: źródło na Dysku.
   - Kod: GitHub. Każdy katalog `AI/*` z żywym kodem to prywatne repozytorium, a kontrola pilnuje, żeby nic nie zostało
     niewypchnięte. Katalogi z archiwum (plany, raporty, wyniki nocnych prób) nie potrzebują repozytorium. Wystarczy im
     dysk zewnętrzny.
3. **Eksport usług, które mają jedną kopię.**
   - Notion: raz w miesiącu ręczny eksport całego obszaru (Ustawienia → Eksport, Markdown i CSV, z podstronami). Asystent
     tego nie uruchomi, może tylko przypomnieć.
   - Arkusz kosztorysu: automat wieczorny co dzień zapisuje kopię wartości (`Koszty/Kosztorys_google.json`). Raz w
     miesiącu pobierz też plik xlsx z formułami.
   - Artefakty claude.ai: kod pulpitu jest w repozytorium, a dane pulpitu w `.dom` (warstwa 1).

## 3. Pozycje i progi kontroli

| Klucz | Co | Gdzie kopia | Termin | Skąd kontrola wie |
|---|---|---|---|---|
| `dokumenty` | dokumenty budowy | Dysk (`Dom/_Kopie`) | ⚠, gdy są zmiany od kopii, a kopia ma ponad 7 dni | `.dom/kopia/stan.json` + porównanie plików (`kopia.py`) |
| `repo:<katalog>` | każdy katalog w `AI/` | GitHub | bez zaległości | git: zdalne repo, niewypchnięte commity, niezacommitowane pliki (bez `fetch`) |
| `kosztorys` | kopia wartości arkusza | Mac → dysk zewnętrzny | 2 dni | data pliku `Koszty/Kosztorys_google.json` |
| `dysk-zewnetrzny` | warstwa 1 w całości | dysk zewnętrzny | 7 dni | rejestr potwierdzeń |
| `notion` | eksport Notion | dysk zewnętrzny | 30 dni | rejestr potwierdzeń |
| `kosztorys-xlsx` | plik xlsx arkusza | dysk zewnętrzny | 30 dni | rejestr potwierdzeń |
| `zdjecia` | trzecia kopia zdjęć z Dysku | dysk zewnętrzny | 30 dni | rejestr potwierdzeń |
| `proba-odtworzenia` | próba odtworzenia | – | 90 dni | rejestr potwierdzeń |
| `sekrety` | sekrety w menedżerze haseł, tokeny z rozmów wymienione | menedżer haseł | raz | rejestr potwierdzeń |
| `time-machine`, `miejsce` | informacja: Time Machine, wolne miejsce na Macu (⚠ poniżej 15 GB) | – | – | `tmutil destinationinfo`, `df` |

Katalog `AI/*` bez zdalnego repozytorium jest ✓, gdy kopia `dysk-zewnetrzny` jest aktualna. Kopia na dysku zewnętrznym
nie zastępuje pushu: niewypchnięte commity zostają ⚠.

Rejestr potwierdzeń to plik `<folder budowy>/.dom/kopie-zapasowe.json` w postaci `{"pozycja": "RRRR-MM-DD"}`. Zapisuje go
wyłącznie `kopie.py potwierdz`.

## 4. Rytm inwestora

- **Co tydzień (dysk zewnętrzny):** skopiuj trzy rzeczy w Finderze albo w Terminalu. Polecenie poniżej tylko dopisuje i
  nadpisuje pliki, niczego na dysku nie usuwa:
  ```
  mkdir -p "/Volumes/<dysk>/Kopia-Dom/Dom" "/Volumes/<dysk>/Kopia-Dom/pamiec-asystenta" "/Volumes/<dysk>/Kopia-Dom/launchd"
  rsync -a --exclude '.DS_Store' --exclude 'sekrety.env' "<folder budowy>/" "/Volumes/<dysk>/Kopia-Dom/Dom/"
  rsync -a ~/.claude/projects/<projekt folderu budowy>/memory/ "/Volumes/<dysk>/Kopia-Dom/pamiec-asystenta/"
  rsync -a ~/Library/LaunchAgents/pl.dom.* "/Volumes/<dysk>/Kopia-Dom/launchd/"
  ```
  Plik z sekretami jest pominięty, bo sekrety wracają z menedżera haseł. Potem powiedz w Claude Code na Macu
  „zrobiłem kopię na dysk”. Asystent uruchomi `python3 tools/kopie.py potwierdz dysk-zewnetrzny`.
- **Co tydzień (Dysk):** „zrób kopię dokumentów” (`dokumenty`, kopia Mac → Dysk).
- **Co miesiąc:** zrób trzy rzeczy, a potem napisz w Claude Code na Macu „zrobiłem eksport Notion / xlsx / zdjęcia”, żeby asystent wpisał
  `potwierdz notion` (`kosztorys-xlsx`, `zdjecia`):
  - eksport Notion: Ustawienia → Eksport → cały obszar, Markdown i CSV. Plik zip trafia na dysk zewnętrzny do
    `Kopia-Dom/Notion/RRRR-MM/`;
  - plik xlsx arkusza kosztorysu: Plik → Pobierz → Microsoft Excel, do `Kopia-Dom/Kosztorys/`;
  - zdjęcia z Dysku: Google Takeout albo pobranie folderu `Dom/Zdjęcia` w przeglądarce, do `Kopia-Dom/Zdjęcia/`.
- **Co kwartał:** próba odtworzenia. Otwórz z dysku zewnętrznego trzy losowe dokumenty, jedną stronę z eksportu Notion
  i plik xlsx. Potem `potwierdz proba-odtworzenia`.
- **Raz:** przenieś sekrety do menedżera haseł i wymień tokeny, które przeszły przez rozmowy. Potem `potwierdz sekrety`.

## 5. Kontrola – `tools/kopie.py`

```
python3 tools/kopie.py stan             # tabela: ✓ / ⚠ / ✗ / ℹ, gdzie leży kopia, z kiedy, co zalega
python3 tools/kopie.py stan --cicho     # jedna linia „[kopie] ✓ n · ⚠ n (…) · ✗ n (…)”; nic, gdy wszystko aktualne
python3 tools/kopie.py stan --json      # dla przeglądu
python3 tools/kopie.py potwierdz <pozycja> [RRRR-MM-DD]
```

`stan` tylko czyta:
- nie zapisuje stanu `kopia.py`;
- nie robi `git fetch`, a gita czyta bez blokad, więc nie przeszkadza równoległym sesjom;
- nie montuje dysku Time Machine;
- z `.dom` nie czyta treści.

Kod wyjścia to 0 także wtedy, gdy są ⚠ i ✗, bo to wynik kontroli. Kod 1 oznacza błąd narzędzia. Testy:
`python3 tools/test_kopie.py`.

**Gdzie widać wynik:**
- przegląd tygodnia (`przeglad-tygodnia-osobisty`, linia „Kopie”);
- pozycje ⚠ i ✗ z terminem trafiają jako jeden komunikat 🔔 `kopie-zapasowe` do „📝 Wpisów” (`wpisy/references/pytania.md`, C).

Jeśli automat tygodniowy nie ma uprawnienia do polecenia, przegląd pisze „Kopie: niesprawdzone”. Uprawnienie dodaje
inwestor (sekcja 7). Przebiegi automatów nie wpisują potwierdzeń: kopię ręczną potwierdza się w Claude Code na Macu,
nie odpowiedzią pod komunikatem 🔔.

**Bez konektora:** kontrola działa lokalnie, bez Notion i Google. Komunikat 🔔 wymaga Notion. Bez niego wynik widać
w odpowiedzi przeglądu i w `kopie.py stan`.

## 6. Odtworzenie – co gdzie szukać

- **Mac padł albo został wyczyszczony:**
  1. Folder budowy, `.dom` i katalogi `AI` skopiuj z dysku zewnętrznego.
  2. Repozytoria sklonuj z GitHuba.
  3. Dokumenty uzupełnij z Dysku (`Dom/_Kopie`, nowsze niż kopia na dysku zewnętrznym).
  4. Automaty: skopiuj pliki `pl.dom.*` z powrotem do `~/Library/LaunchAgents/` i załaduj je `launchctl` (instrukcja
     w README repozytorium automatów).
  5. Sekrety odtwórz z menedżera haseł.
- **Utrata konta Google:**
  - arkusz: ostatni xlsx i dzienna kopia wartości JSON;
  - zdjęcia: kopia miesięczna;
  - dokumenty: Mac i dysk zewnętrzny.
- **Utrata Notion:** eksport miesięczny. Wiedza dodatkowo jest w indeksie na Macu (`.dom`, odczyt `tools/wiedza.py`).
- **Utrata dostępu do asystenta:** procedury są w publicznym repozytorium, a dane w Notion, w arkuszu i w folderze budowy.
  Każde inne AI czyta `AGENTS.md`.

## 7. Decyzje inwestora

Przyjęte nocą 11.11.2026 jako bezpieczniejsza opcja, do potwierdzenia:
1. **Dysk zewnętrzny, zaszyfrowany,** to główna kopia warstwy 1. Do czasu zakupu albo podłączenia kontrola pokazuje ✗ `dysk-zewnetrzny`.
2. **Time Machine** nie jest częścią planu, dopóki Mac nie jest prywatny. Zostaje ręczna kopia folderów na dysk
   zewnętrzny.
3. **Archiwum `.dom` tylko na dysku zewnętrznym**, nigdy na Dysku Google, także zaszyfrowane. Skrypt szyfrowanego
   archiwum powstanie dopiero po decyzji o miejscu i haśle.
4. **Terminy:**
   - dysk zewnętrzny co 7 dni;
   - eksport Notion, xlsx kosztorysu i zdjęcia co 30 dni;
   - próba odtworzenia co 90 dni;
   - kopia dokumentów na Dysk: ⚠, gdy są zmiany od kopii, a potwierdzona kopia ma ponad 7 dni.
5. **Ślad kopii ręcznych:** potwierdzenie w rejestrze (`kopie.py potwierdz`), a nie wyszukiwanie plików eksportu na dyskach.
6. **Katalogi `AI/*` z archiwum** (plany, raporty, wyniki prób) nie dostają repozytorium. Chroni je dysk zewnętrzny.

Do zrobienia przez inwestora (asystent nie ma do tego narzędzi albo zgody):
- zaszyfrowany dysk zewnętrzny i pierwsza kopia;
- wypchnięcie zaległych commitów w repozytoriach `AI/*` (lista w `kopie.py stan`);
- uprawnienie `Bash(python3 tools/kopie.py stan:*)` w liście narzędzi automatu przeglądu w repozytorium automatów;
- pierwszy eksport Notion;
- sekrety do menedżera haseł i wymiana tokenów.
