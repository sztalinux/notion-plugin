# notion-plugin – harness AI do Notion: budowa domu i sprawy osobiste

Procedury i zasady, według których asystenci AI (Claude, Gemini, Codex…) pracują z Notion inwestora. Dwa pluginy:

- **`ja`** – jeden Dziennik w Notion na wszystko (emocje, praca, dziecko, zadania, suplementy, budowa), rozkładanie wpisów
  według bazy „🧭 Obszary Dziennika”, zadania, nocny przegląd dnia, rozwój harnessu;
- **`dom-budowa`** – budowa domu: oferty, koszty, notatki, wiedza, dokumenty, etapy, dziennik budowy, harmonogram, zakupy.

> **Dla człowieka:** jak używać całego systemu, reguły, „co się stanie, gdy…”, utrzymanie i odtworzenie od zera – strona
> Notion „📘 Instrukcja obsługi” (pod 📌 DASHBOARD; kopia offline `AI/Instrukcja obsługi.md` w folderze budowy, odświeżana
> raz w miesiącu). To README opisuje repo i szczegóły techniczne.

Repozytorium mówi tylko **jak** pracować. Dane są w Notion, liczby w arkuszu Google „Kosztorys budowy” (wydatki trafiają tam z Notion przez kolejkę – `docs/wydatki-arkusz.md`), dokumenty w folderze budowy na komputerze.

> **Repo jest publiczne.** Nie trafiają tu żadne dane osobowe ani dane projektu (imiona domowników, nazwiska, firmy, adres,
> działki, telefony, e-maile, kwoty, notatki, treść wpisów). Pilnują tego `tools/build.py` i hook `.githooks/pre-commit`
> – ale przed każdym commitem i tak przejrzyj `git diff`.

## Struktura

```
Dom/                              ← folder budowy (centrum dokumentów, poza gitem)
  _Przychodzące/                  ← tu wrzucasz nowe pliki od projektantów i wykonawców
  _Do claude.ai/                  ← paczka (generowana): przewodnik po dokumentach → wiedza projektu „Dom” na claude.ai (kopia awaryjna)
  Zdjęcia/                        ← zdjęcia z budowy – źródłem jest Dysk Google (Dom/Zdjęcia/<etap>/<krok>/), plugins/dom-budowa/skills/dziennik/references/zdjecia-i-kopia.md
  _Na Dysk/                       ← paczki kopii dokumentów do wgrania na Dysk (tools/kopia.py)
  .dom/                           ← indeks dokumentów, stan wgrania, lista słów zakazanych w repo
    wiedza/                       ← dane indeksu wiedzy (.dom/wiedza/) – poza repo, nigdy w git
  … foldery tematyczne (projekt, konstrukcja, instalacje, wyceny…)
  AI/dom/                         ← to repozytorium
    CLAUDE.md, AGENTS.md, GEMINI.md   ← punkty wejścia agentów
    .claude-plugin/marketplace.json   ← repo jest marketplace'em dla claude.ai (dwa pluginy)
    plugins/ja/skills/                ← procedury osobiste (Dziennik, zadania, emocje, dziecko, suple, przegląd dnia, harness)
    plugins/dom-budowa/skills/        ← procedury budowy
    .claude/skills/, .agents/skills/  ← dowiązania na każdy skill obu pluginów (odtwarza tools/build.py)
    .claude/settings.json             ← zezwolenia (hooków startowych nie ma – na starcie sesji jedna linia stanu: CLAUDE.md)
    .githooks/                        ← pre-commit (pliki, indeks, autor), commit-msg (wiadomość), pre-push (każdy wysyłany commit, nazwy gałęzi i tagów)
    tools/build.py                    ← walidacja (w tym dane osobowe) + dowiązania skilli + paczki dist/ (po jednej na plugin)
    tools/dokumenty.py                ← indeks folderu budowy i paczka dla claude.ai
    tools/teczka.py                   ← teczka etapu / transzy do banku: składa dokumenty etapu w Teczki/<Etap>/ ze spisem braków (etap D; testy test_teczka.py)
    tools/zdjecia.py, tools/kopia.py  ← rozkładanie zdjęć i dokumentów z telefonu, kopia dokumentów Mac → Dysk (plugins/dom-budowa/skills/dziennik/references/zdjecia-i-kopia.md; testy test_*.py)
    tools/kopie.py                    ← kontrola kopii zapasowych: co ma kopię, gdzie i z kiedy, tylko odczyt (docs/kopie-zapasowe.md; test_kopie.py)
    tools/wiedza.py                   ← indeks Bazy wiedzy (SQLite FTS5 z Notion, tylko do odczytu)
    tools/budzet/                     ← budżet domowy: wpisy (wpis.py) i paragony ze zdjęcia (paragon.py) od razu w arkuszu (arkusz_budzetu.py, docs/budzet-arkusz.md), import wyciągów, Allegro i listy → strona decyzji → Transakcje, kontrola arkusza (procedura budzet; dane poza repo w .dom/budzet)
    tools/wydatki.py                  ← kolejka wydatków / wycen / planów z Notion → arkusz Google, gotówka po miesiącach (docs/wydatki-arkusz.md)
    tools/pomysly_wersje.py           ← wersje z CHANGELOG (gałąź main) dla POM-n (kontrola „status pomysłu ↔ wdrożenie” w przeglądzie tygodnia; test_pomysly_wersje.py)
    docs/                             ← opisy systemów dla człowieka: wiedza (mapa, runbook, rejestr decyzji), wydatki → arkusz, budżet → arkusz
```

## Jak to działa

```
Telefon / czat ── poprawka sposobu pracy ──► Notion „🤖 Zmiany asystenta” (Zasady) (obowiązuje od razu)
                                                   │
Claude Code (komputer; na starcie linia stanu, bez pytań) ◄──┘
   ├─ „Dokumenty budowy” (tools/dokumenty.py): skan folderu budowy → przewodnik na stronie Notion (+ kopia awaryjna `_Do claude.ai/`)
   ├─ „Indeks wiedzy” (tools/wiedza.py sync --publikuj --cicho): odświeża indeks Bazy wiedzy z Notion i publikuje kopię dla czatu
   │    (plik indeksu ponad ok. 13 MB nie mieści się w limicie 110 s – od razu: tools/wiedza.py publikuj --teraz)
   ├─ klasyfikuje nowe dokumenty (procedura `dokumenty`)
   └─ wdraża zmiany harnessu → wersja → commit → push ──► GitHub sztalinux/notion-plugin
                                                               │ ręczne odświeżenie pluginów (claude-ai-projekt.md)
claude.ai (telefon, czat, Cowork) ◄── pluginy ja + dom-budowa ─┘   (każda rozmowa, bez projektu)
   ├─ projekt „Dom” – tylko kontener dokumentów budowy (wgrywasz paczkę ręcznie, opcjonalnie)
   └─ bez Notion (blokada organizacji) → zapisy do „📥 Skrzynki” (Claude Docs)

Mac (launchd, `AI/automaty/przeglad.py`, poza repo) ── co godzinę 8–22, w nocy (2:00), w niedzielę:
   ├─ `claude -p` + MCP Notion: Skrzynka i 📓 Dziennik → Notion (przegląd dnia, tygodnia)
   ├─ po przebiegu `tools/wydatki.py`: kolejka „💸 Wydatki → arkusz” → arkusz Google „Kosztorys budowy”
   ├─ po przebiegu `tools/budzet/arkusz_budzetu.py`: wydatki z wpisów → arkusz Google „Budżet domowy” (w nocy kontrola wpis ↔ wiersz)
   └─ problem, który trwa (przebieg nieudany lub nieuruchomiony, logowanie MCP, błąd skryptu) → `stan.json` →
      następny udany przebieg → „🔔 Komunikaty asystenta” we „📝 Wpisach”; większe sprawy → baza „🤖 Zmiany asystenta” (Rodzaj Usterka; naprawa na polecenie „zrób ZP-n” w Claude Code)
```

## Konektory i drogi zapasowe

Zasada (`AGENTS.md`): rozwiązanie oparte na konektorze działa dalej bez niego, choćby wolniej; gdy się nie da – stoi tu
z ⚠ i inwestor o tym wie.

| Konektor | Do czego | Gdy go zabraknie |
|---|---|---|
| Notion MCP (Claude Code, przebiegi `claude -p` na Macu) | przetwarzanie Dziennika, zapisy do Notion | ⚠ brak pełnego zapasu: wpisy czekają we „Wpisach” i Skrzynce (nic nie ginie), przebieg kończy się kodem 2 „NOTION: brak logowania” (problem czeka w `stan.json`; po zalogowaniu pierwszy udany przebieg zostawia tylko ślad „ustąpiło” w „Przetworzone” Dziennika, bez bloku 🔔 – w trakcie widać go wyłącznie w logu; brak wykryty w samym przebiegu – blok 🔔 do następnego przebiegu); skrypty z tokenem (indeks wiedzy, migawka, wydatki → arkusz) działają dalej |
| Notion na claude.ai | zablokowany przez organizację | Skrzynka, migawka i indeks wiedzy (`budowa`, zasada 13) |
| Claude Docs („📥 Skrzynka”) | zapisy z telefonu bez Notion | wpis wprost w „📝 Wpisach” (pod 📓 Dziennikiem) w aplikacji Notion |
| Google Sheets / Drive + strona decyzji (artefakt, procedura `budzet`) | budżet domowy: odczyt Transakcji, zapis wierszy, decyzje inwestora | wynik `przenies.py` (`miesiace/RRRR-MM-zapis.json`) wkleja się ręcznie; decyzje można podać w czacie zamiast na stronie |
| Notion MCP – zdjęcie paragonu we „📝 Wpisach” (`tools/budzet/paragon.py pobierz`, procedura `budzet`) | pobranie zdjęcia paragonu do `.dom/budzet/paragony/` i rozpisanie w przebiegu | sesja Claude Code: inwestor wkleja zdjęcie w rozmowę, rozpisanie tym samym `paragon.py rozpisz`; przebieg zostawia 🔔 |
| Apps Script arkusza „Budżet domowy” (`tools/budzet/arkusz_budzetu.py`) | wydatki z wpisów od razu w Transakcjach, przypięcie płatności z wyciągu | wpisy czekają w pliku miesiąca; zamknięcie miesiąca dopisuje brakujące wiersze po ID, przypięcia – konektorem albo ręcznie (`docs/budzet-arkusz.md`, 4) |
| Google Sheets / Drive | liczby z żywego arkusza, zmiany układu, nowy etap kosztorysu w sesji (`koszty` C.7) | kopia `Kosztorys_google.json` (Apps Script z sekretem), eksport od inwestora, `wydatki.py migruj` (`docs/wydatki-arkusz.md`; nowy etap – operacja `wstaw`); nowa pozycja w istniejącym etapie nie zależy od konektora (Apps Script) |
| Google Drive (zdjęcia, dokumenty z telefonu, kopia) | rozkładanie `Zdjęcia/_nowe` (sesja i przegląd nocny na Macu), odczyt dokumentów z Dysku na czacie | skrypt lokalnie (z aplikacją Dysku albo po pobraniu `_nowe` / AirDropie), kopia paczką przez przeglądarkę, „prośba o dokument” jak dotąd; wgrywanie z telefonu działa zawsze (`plugins/dom-budowa/skills/dziennik/references/zdjecia-i-kopia.md`, 5) |
| Notion – „📘 Książka domu” (procedura `ksiazka-domu`) | rozdziały etapów, „gdzie co biegnie” | szkic rozdziału jako Markdown w folderze budowy (`Książka domu/`), punkty z telefonu przez Skrzynkę; ostatni eksport PDF i zdjęcia na Dysku działają bez Notion i bez asystenta |
| Atlassian MCP (Jira, przebiegi na Macu – zakładka 💼 planu dnia) | zgłoszenia przypisane do inwestora, zmiany od wczoraj | commity i PR-y ze skryptu lokalnego (`.dom/praca/dzien.json`) i lista WORK – plan pracy bez statusów Jiry, w 📊 linia „Jira – brak odczytu” |
| Blender MCP (model 3D, procedura `model-3d`) | przebudowa modelu w otwartym Blenderze, zrzuty widoku na żywo | Blender bez okna: `Blender -b -P narzedzia/buduj.py -- --zapisz` i `narzedzia/rendery.py` w folderze modelu – ten sam model (suma kontrolna w `model/raport.json`), podgląd jako obrazy w `podglad/`; bez Blendera w ogóle zostaje kontrola danych `narzedzia/sprawdz.py` i zapisany plik sceny |
| Notion – „🏠 Poprawki modelu 3D” (procedura `model-3d`) | lista poprawek do modelu wpisywana przez inwestora | plik `POPRAWKI.md` w folderze modelu albo poprawki podyktowane w rozmowie |
| Artifact / ArtifactData (pulpit budowy, Claude Code) | publikacja pulpitu, odczyt zaznaczeń inwestora (procedura `pulpit`) | ⚠ brak zapasu dla samej strony pulpitu: nie odświeża się, a nowych zaznaczeń nie da się odczytać; nic nie ginie – źródłem prawdy jest Notion (Notatnik, Harmonogram, Checklista), decyzje wpisuje się tam wprost |

## Procedury

**Plugin `ja`**

| Procedura | Kiedy | Co robi |
|---|---|---|
| `ja` | każda rozmowa o dniu, zadaniach, emocjach, dziecku, Dzienniku, harnessie | kontekst, zasady, mapa procedur, skrzynka zmian |
| `wpisy` | „przerób dziennik”, luźne notatki naraz | rozpoznaje obszar wg bazy „🧭 Obszary Dziennika”, przekazuje do procedury, niejasne → pytanie w okienku pod wpisem w „📝 Wpisy”; problemy bez wpisu (automaty, 💸) → „🔔 Komunikaty asystenta” na górze „Wpisów” |
| `emocje` | „czułem…”, „dziś w pracy…”, „podsumuj emocje” | Wpisy emocji, Dziennik produktywności, podsumowania na prośbę |
| `zadania` | „muszę…”, „zrobiłem X”, „co mam jutro” | wspólna TASKS z polem Obszar; zmiana statusu z Dziennika; pole Deadline: ☑ = termin twardy, puste = orientacyjny (po dacie nie jest zaległością) |
| `dziecko` | obserwacja, „porozmawiać z nią o…”, prezent, zalecenie | strona dziecka w sekcjach |
| `suple` | „kończy się…”, „kupiłem…”, przerwa | baza Suple: Buy, Status, Last break |
| `przeglad-dnia` | co godzinę (tryb szybki) i w nocy (2:00) – automat na Macu / „przegląd dnia” | szybki: nowe wpisy na bieżąco, pusto = koniec bez zapisów; nocny (klucz techniczny `wieczorny`): podsumowanie dnia, zmiany w zadaniach (także ręczne) z uzupełnieniem pustych kolumn i plan dnia na stronie „☀️ Dziś” w zakładkach (przegląd, budowa, prywatne, praca, wczoraj; historia w „📆 Przeglądy dzienne”), przegląd dnia budowy osobno na DOM, kontrola spójności (zadanie budowy ↔ krok Harmonogramu, zakup ↔ zadanie „Kupić X”, suplement wstrzymany z Buy – tylko pytania 🔔, zmiana dopiero po Twoim ☑; zadanie rozmowy ↔ temat do przegadania i status pomysłu ↔ wdrożenie sprawdza raz w tygodniu przegląd tygodnia); rozkminka („przygotuj mi…”, „jakie pytania…”) tylko na prośbę we wpisie |
| `przeglad-tygodnia-osobisty` | raz w tygodniu – automat na Macu / „przegląd tygodnia” | sprawy osobiste w liczbach, zadania po terminie (tylko z Deadline), najbliższy tydzień, porządki w Dzienniku, kontrola spójności rozmów i pomysłów; uruchamia przegląd budowy i linkuje do niego |
| `rozwoj-harnessu` | „zapamiętaj na przyszłość”, nowa procedura, „mam pomysł…”, „zrób POM-n”, „zrób ZP-n” | skrzynka zmian w Notion → wdrożenie do repo; pomysły → analiza → wdrożenie na polecenie; „🤖 Zmiany asystenta” (Rodzaj Usterka) – sprawy, których przebieg nie załatwi |

**Plugin `dom-budowa`**

| Procedura | Kiedy | Co robi |
|---|---|---|
| `budowa` | każda rozmowa o budowie | kontekst, zasady, mapa procedur, luźne wpisy o budowie, część budowlana przeglądu dnia |
| `oferta` | oferta / wycena / rozmowa z ekipą | rozbicie, zakres 01–13, zgodność z projektem, porównanie, pytania; „sam czy ekipa”; zakres do umowy |
| `koszty` | wydatek, faktura, cena dostawcy, „planuję wydać…”, „ile wydaliśmy” | kolejka „💸 Wydatki → arkusz” → arkusz Google (wydatki, Cennik, plan pozycji); plan / umówione / wydane; błędy → komunikat 🔔 we Wpisach; transze; gotówka po miesiącach („ile gotówki potrzebuję w …”) |
| `notatka` | „zapisz”, „ustaliliśmy”, „decyzja” | Notatnik budowy, TASKS (Obszar Dom), „Do zamknięcia” |
| `analiza-techniczna` | projekt, rysunek, umowa, pytanie techniczne, „jak to zrobić samemu” | [projekt]/[szacunek]/[opinia], pytania do projektanta, instrukcja pracy własnej |
| `wiedza` | transkrypcja, artykuł, „dzwoniłem do…”, „SP-n: …”, „co wiemy o…” | Baza wiedzy, sprzeczności (ADR), odczyt stanu wiedzy; szukanie i duplikaty przez indeks `tools/wiedza.py` |
| `dokumenty` | nowe pliki, „wgrałem”, „gdzie jest…” | folder budowy, indeks, paczka dla claude.ai, przewodnik w Notion |
| `etap` | „zaczynamy etap”, „jutro betonowanie”, odbiór, usterki | plan etapu, bramki „bez odwrotu”, protokół odbioru |
| `ksiazka-domu` | odbiór etapu, „zapisz w książce domu…”, „gdzie biegnie…”, „gdzie nie wiercić” | „📘 Książka domu” w Notion: rozdział po każdym odebranym etapie, „gdzie co biegnie” (punkty z miarą, strefy nie wiercić / nie kopać), przeglądy, spis dokumentów; PDF – na razie eksport z Notion |
| `dziennik` | „dziś na budowie…”, zdjęcia, godziny własne, roboty dodatkowe | Dziennik budowy w Notion, przekazanie kosztów/zadań |
| `harmonogram` | „ekipa wchodzi…”, „przesuwamy…”, „czekam na…”, „co mnie czeka” | harmonogram w Notion (oś czasu), terminy pochodne (zamówienia, bramki, ludzie), przesunięcia |
| `pulpit` | „zsynchronizuj pulpit”, „odśwież pulpit”, „pokaż, co by się zmieniło” (tylko Claude Code) | obieg pulpitu budowy: zaznaczenia ze strony → Notion (statusy, decyzje), świeże dane z Notion, testy, publikacja pod stałym adresem |
| `model-3d` | „przebuduj model 3D”, „zmień podłogę w salonie”, „dodaj okno dachowe”, „pokaż widok z…”, „zrób rendery elewacji”, „wprowadź poprawki modelu” | model 3D domu i ogrodu w Blenderze: zmiana w plikach danych → kontrola → przebudowa → zrzut przed/po; dane i skrypty w prywatnym folderze modelu, tu tylko procedura; bez konektora Blender działa bez okna |
| `zakupy` | „kupić X na budowę”, „co kupić na…”, „kiedy zamawiać”, oferta hurtowni, dostawa | wszystko na działkę i do budynku w 🧱 Zakupy budowy, lista z kosztorysu, wyprzedzenia, porównanie dostawców |
| `przygotowanie` | „jutro spotkanie z…”, „o co zapytać”, „kogo wybrać z kilku” | karta przygotowania: pytania, czerwone flagi, macierz decyzji, zapis po spotkaniu |
| `przeglad-tygodnia` | niedziela wieczorem – automat na Macu, z przeglądem osobistym / „co nowego” | decyzje, nowa wiedza, terminy, budowa, zamówienia, porządki |

## Pulpit budowy

Pulpit budowy to strona (artefakt claude.ai) z decyzjami, rozbieżnościami, krokami etapu, checklistą i zadaniami. Jego kod i testy są w osobnym,
**prywatnym** repozytorium; tu jest tylko procedura `pulpit` (`plugins/dom-budowa/skills/pulpit/`) i pola Notion, na których pulpit stoi
(`notion-mapa.md`: NT, Pulpit, Dotyczy etapu, Krok). Procedura przenosi zaznaczenia ze strony do Notion, ściąga świeże dane, uruchamia testy
i publikuje stronę pod stałym adresem – wyłącznie na polecenie i tylko w sesji interaktywnej Claude Code (narzędzia artefaktów nie działają w trybie `claude -p`).
Adresy artefaktów i dane robocze leżą w folderze budowy poza repo.

## Indeks wiedzy

`tools/wiedza.py` trzyma lokalną kopię czterech baz Bazy wiedzy z Notion w SQLite z wyszukiwaniem pełnotekstowym (tylko do odczytu –
zapisy idą wyłącznie do Notion). Polecenia: `sync`, `szukaj`, `temat`, `etap`, `karty`, `karta`, `zrodla`, `duplikaty`, `stan`, `publikuj`. `tools/migawka.py`
publikuje tą samą drogą migawkę otwartych wpisów Notatnika i zadań dla czatu bez Notion. Dane leżą w `.dom/wiedza/` poza repo
i nigdy nie trafiają do git. Konfiguracja – plik `.dom/sekrety.env` (tryb 600, poza repo), cztery zmienne indeksu: `NOTION_TOKEN` (odczyt Notion; w bazie 💸 Wydatki także zmiana treści – `wydatki.py`),
`GITHUB_REPO` (prywatne repo kopii dla czatu na telefonie), `GITHUB_TOKEN_SYNC` (zapis kopii na Macu), `GITHUB_TOKEN_SEARCH` (odczyt kopii w czacie); w tym samym pliku `wydatki.py` trzyma `ARKUSZ_URL` i `ARKUSZ_SEKRET` (`docs/wydatki-arkusz.md`, 7); pełna lista kluczy – `docs/wiedza-runbook.md`, 1, krok 3.
Trzy kanały użycia i ograniczenia: `plugins/dom-budowa/skills/wiedza/references/indeks.md`.
Całość systemu wiedzy (części, kto co uruchamia, pomiary, decyzje): `docs/system-wiedzy.md`; instrukcja odtworzenia i naprawy (automaty, konektor Notion, rozjechany indeks, tokeny): `docs/wiedza-runbook.md`; rejestr decyzji – co wybrano, co sprawdzono i odrzucono, z liczbami z pomiarów: `docs/decyzje-system-wiedzy.md`.
Wydatki z Notion do arkusza Google z kosztorysem (jak działa, konfiguracja krok po kroku, kod Apps Script): `docs/wydatki-arkusz.md`.
Budżet domowy – wydatki z wpisów do arkusza „Budżet domowy” (przepływ, znacznik wysyłki, wdrożenie i kod Apps Script, sekrety `BUDZET_ARKUSZ_URL` i `BUDZET_ARKUSZ_SEKRET`): `docs/budzet-arkusz.md`.
Zdjęcia z budowy, dokumenty z telefonu i kopia dokumentów na Dysk Google (reguły, tryby, przypadki brzegowe): `plugins/dom-budowa/skills/dziennik/references/zdjecia-i-kopia.md`.
Kopie zapasowe wszystkiego (Mac, Dysk, Notion, repozytoria, dane asystenta) – plan, rytm, kontrola `tools/kopie.py`, odtworzenie: `docs/kopie-zapasowe.md`.
`tools/wiedza_jakosc.py` obserwuje jakość wyszukiwania (log zapytań `szukaj`, zbiory oceny, raport tygodniowy z alarmami,
ocena ręczna, miesięczne porównanie z Notion; pytania wymyślone: `tools/wiedza_jakosc_pytania.json`) – dane w `.dom/wiedza/`; opis: `plugins/dom-budowa/skills/wiedza/references/indeks-jakosc.md`.
`tools/wiedza_sedzia.py` (polecenie `wiedza_jakosc.py sedzia`, na sucho bez `--wyslij`) – sędzia LLM trafności wyników przez `claude -p` (kanarek izolacji; bez filtra danych osobowych – sekcja „Zgoda i granice” opisu); opis: `plugins/dom-budowa/skills/wiedza/references/indeks-sedzia.md`.
`tools/wiedza_porownanie.py` (polecenie `wiedza_jakosc.py pokaz`) – lokalny plik HTML do ręcznego porównania wyników indeksu i Notion (API, tylko odczyt) z ocenami sędziego; wyjście: same liczby i ścieżka pliku.

Źródła do Bazy wiedzy (filmy, playlisty, artykuły) dopisuje nocna kolejka z katalogu `AI/import-wiedzy/` (poza repo;
do 10.11.2026 `kurs-do-notion`): strona „Kolejka wiedzy” uruchamiana z `Kolejka.command`, zapis przez lokalny MCP `notion`.
Opis lokalny (ścieżki, dane kolejki): `AI/import-wiedzy/docs/README-lokalne.md`, sekcja 3; awarie – `docs/wiedza-runbook.md`, 5.9.

### Karty wiedzy

Czat na telefonie nie szuka tez sam, tylko czyta **karty** – gotowe wybory tez do typowych pytań. Wybór robi Mac, offline, mocnym modelem
czytającym całą bazę w małych porcjach; wynik leży w tym samym pliku `wiedza.sqlite`, który telefon już pobiera. Po co: sam czat widzi
przy pytaniach szerokich ok. 60% trafnych tez, a poziom „cały etap” (330–390 tys. znaków) przerasta okno rozmowy (test 28.10.2026: w całości
czyta 3 z 16 części). Dwa rodzaje: ok. 17 kart pytań (100–200 tez, pokrycie zmierzone wobec wzorca i pokazane w nagłówku karty) oraz
68 kart czynności (małe, tezy otagowane czynnością, pokrycie niemierzone).
- Czat i Claude Code: `python3 tools/wiedza.py karty [--do "A" "B" "C"]` (spis kart; z `--do` dopasowanie do pytania) i
  `karta KOD … --pytanie "A" "B" "C" --czesc k` (treść w częściach, z dopełnieniem z szukania). Karta drukuje tezy bez źródeł –
  `zrodla WI-… ` (albo `zrodla --temat "…"`) podaje źródła pogrupowane wg typu autora do sekcji „📚 Na czym się opieram”.
- Tylko Mac: `python3 tools/wiedza_karty.py` – `definicje`, `importuj-tagi`, `taguj`, `zbuduj`, `ocen`, `pomiar`, `aktualizuj`, `zapisz`.
- Dane (definicje kart, pomiar) leżą w `.dom/wiedza/karty/` poza repo; w repo jest tylko kod i procedura.
- Automat na Macu co godzinę (`aktualizuj`): nowe tezy trafiają do kart, a kopia dla czatu jedzie z publikacją.

Opis: `plugins/dom-budowa/skills/wiedza/references/karty.md`; jak czat korzysta z kart – `pytanie-do-bazy.md` w tym samym katalogu.

### Tryb głęboki

Pytanie złożone, którego nie pokrywa żadna karta (albo prośba „tryb głęboki”): czat zostawia je w prywatnym repo kopii indeksu, a Mac czyta
całą bazę w małych porcjach (Sonnet, dwa przebiegi), pisze pełną odpowiedź (Opus: tezy, otwarte sprzeczności, Notatnik z migawki) i odkłada
ją do repo; czat ją pobiera i przekazuje (3–6 minut, ok. 1–2 USD na pytanie, Mac musi nie spać). Token zapisu pytania leży w pliku dostępu,
poza repo. W Claude Code na Macu – lokalnie skrypt `pytania.py` z katalogu automatów (README automatów). Opis: `plugins/dom-budowa/skills/wiedza/references/tryb-gleboki.md`.

## Start

1. Repo sklonowane do `Dom/AI/dom` (folder budowy = dwa poziomy wyżej; inny – zmienna `DOM_HUB`; z kopii roboczej git
   `.claude/worktrees/<nazwa>` narzędzia liczą go od głównej kopii – `tools/hub.py` – a polecenia zapisujące bez jawnego
   `DOM_HUB` odmawiają, gdy zapis trafiłby w prawdziwy folder budowy), `git config core.hooksPath .githooks`, `git config user.email <id>+<login>@users.noreply.github.com`
   (autor commitów jest publiczny; imię inwestora dozwolone, e-mail tylko noreply). Lista słów zakazanych: `Dom/.dom/zakazane-w-repo.txt`
   (nazwiska, firmy, miejscowość – po jednym w linii; plik poza repo; bez niej walidacja i hooki zatrzymują się kodem 1 –
   świadomie same wzorce: `DOM_BEZ_LISTY=1`).
2. Python 3 + `pip3 install --user openpyxl pypdf` (kontrola danych wrażliwych w paczce).
3. W `Dom/AI/dom` uruchom `claude`. `/mcp` – jeśli jest zalogowany serwer `notion` (lokalny, krok 5), gotowe.
4. claude.ai → Customize → Plugins → Add marketplace → `sztalinux/notion-plugin` → zainstaluj `ja` i `dom-budowa`,
   włącz „Sync automatically” (jeśli organizacja na to pozwala). Bez synchronizacji – jak pobrać nową wersję:
   `plugins/ja/skills/rozwoj-harnessu/references/claude-ai-projekt.md`.
5. Przeglądy (szybki co godzinę, nocny, tygodniowy) uruchamia **launchd na Macu** przez `claude -p` z lokalnym serwerem
   MCP Notion (`claude mcp add --transport http --scope user notion https://mcp.notion.com/mcp`, logowanie `/mcp`) –
   instalacja i godziny: README w katalogu automatów (`AI/automaty/`, poza repo). Konektor Notion na claude.ai jest
   zablokowany przez organizację, dlatego zaplanowane zadania na claude.ai nie są używane; zapisy z telefonu idą przez
   dokument Claude „📥 Skrzynka” (plugin `ja`, `wpisy/references/skrzynka.md`). Kosztorys: `docs/wydatki-arkusz.md`, sekcja 7.
   Nocą (bez inwestora) harness i opisy sprawdza pętla samonaprawy z katalogu `AI/samonaprawa/` (poza repo, opis w jej
   README): poprawki pewne idą przez gałęzie `noc/…` i recenzję, reszta czeka w raporcie kampanii w `.dom/noc/<data>/`.
6. claude.ai → projekt „Dom” (tylko dokumenty budowy):
   - **Instructions:** `python3 tools/build.py` i wklej `dist/claude-ai-projekt/instrukcje.md` – dzięki temu każda
     wiadomość w projekcie korzysta z harnessu i Notion bez wpisywania „/” (opis:
     `plugins/ja/skills/rozwoj-harnessu/references/claude-ai-projekt.md`). Dawny `START.md` usuń.
   - **Wiedza projektu:** może zostać pusta. Przewodnik po dokumentach i mapę Notion asystent czyta ze strony Notion
     „📑 Przewodnik po dokumentach i Notion”, którą Claude Code aktualizuje sam. Pełne dokumenty asystent pobiera
     na prośbę – załączasz je do rozmowy. `Dom/_Do claude.ai/` to kopia awaryjna (opcjonalnie).

## Na co dzień

- Nowy plik od projektanta/wykonawcy → wrzuć do `Dom/_Przychodzące/` i uruchom `claude` w `Dom/AI/dom`.
  Asystent go posortuje, opisze w przewodniku i sam zaktualizuje stronę przewodnika w Notion – nic nie wgrywasz.
  Gdy na telefonie asystent poprosi o dokument – załącz wskazany plik.
- Wszystko, co przyjdzie Ci do głowy (emocja, zadanie, dziecko, suplement, budowa), wpisuj na stronę „📝 Wpisy” (pod „📓 Dziennik”) w Notion –
  punkt pod punktem albo jako podstronę (telefon wystarczy albo Claude na telefonie → „📥 Skrzynka”; bloki 1. poziomu Dziennika i strony z widgetu
  nie są już czytane – przejście robi jednorazowo przegląd, `przeglad-dnia/references/przejscia.md`). Szybki przebieg co godzinę (8–22) i nocny przegląd dnia rozłożą to według bazy „🧭 Obszary
  Dziennika”, a pod niejasnymi wpisami w „📝 Wpisy” doda krótkie okienko z pytaniem – odpowiedź wpisujesz w nim, przerobi ją następny przebieg. Gdy coś zepsuje się „w tle” (automat na Macu, skrypt, wydatek, który nie wszedł do arkusza), na górze „Wpisów” pojawi się blok pod „🔔 Komunikaty asystenta” – odpisz pod nim albo zostaw, jeśli ustąpi samo; sprawy za duże na przebieg trafiają do bazy „🤖 Zmiany asystenta” (Rodzaj Usterka) na stronie 🤖 Asystent AI – zgłoszona przez przebieg ma blok 🔔 do czasu naprawy (założona w Claude Code albo ręcznie – tylko gdy czeka na Ciebie); naprawia je Claude Code na polecenie „zrób ZP-n” (nie same). Nowy rodzaj wpisu = nowy wiersz w Obszarach, bez zmian w harnessie.
  Ręcznie: „przerób dziennik”. Chcesz, żeby asystent coś przemyślał („przygotuj mi pytania na jutrzejsze spotkanie”, „porównaj…”)
  – napisz to we wpisie; wynik będzie rano w przeglądzie dnia, w sekcji „🧠 Rozkminka” (bez prośby asystent rozkminek nie robi).
- Poprawki „na przyszłość” z telefonu trafiają do skrzynki zmian w Notion; Claude Code wdroży je na polecenie „wdróż”.
- Dzień na budowie → powiedz asystentowi, co się działo (telefon wystarczy) – trafi do Dziennika budowy, a „nie skończyliśmy, jutro kontynuujemy” przesunie kroki Harmonogramu; zdjęcia wgraj z telefonu na Dysk do `Dom/Zdjęcia/<etap>/<krok>/` albo do `Zdjęcia/_nowe` w folderze z nazwą, co na nich jest, – rozłoży je przegląd nocny (od razu: „rozłóż zdjęcia” w Claude Code; `plugins/dom-budowa/skills/dziennik/references/zdjecia-i-kopia.md`, 9).
- Przed krokiem „bez odwrotu” (beton, zasypka, tynki) zapytaj „co sprawdzić przed …” – dostaniesz bramkę z listą zdjęć do zrobienia.
- Każda zmiana w repo = podbita wersja zmienionego pluginu w `plugins/<plugin>/.claude-plugin/plugin.json` (inaczej claude.ai
  jej nie pobierze). Po pushu odśwież pluginy na claude.ai (o ile nie działa synchronizacja) – `rozwoj-harnessu/references/claude-ai-projekt.md`.
- Procedury działają same – piszesz normalnie, w dowolnej rozmowie. `/` (np. `/oferta`, na claude.ai `dom-budowa:oferta`) tylko gdy
  chcesz wymusić procedurę.
