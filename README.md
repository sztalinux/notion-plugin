# notion-plugin – harness AI do Notion: budowa domu i sprawy osobiste

Procedury i zasady, według których asystenci AI (Claude, Gemini, Codex…) pracują z Notion inwestora. Dwa pluginy:

- **`ja`** – jeden Dziennik w Notion na wszystko (emocje, praca, dziecko, zadania, suplementy, budowa), rozkładanie wpisów
  według bazy „🧭 Obszary Dziennika”, zadania, wieczorny przegląd dnia, rozwój harnessu;
- **`dom-budowa`** – budowa domu: oferty, koszty, notatki, wiedza, dokumenty, etapy, dziennik budowy, harmonogram, zakupy.

Repozytorium mówi tylko **jak** pracować. Dane są w Notion, liczby w Excelu, dokumenty w folderze budowy na komputerze.

> **Repo jest publiczne.** Nie trafiają tu żadne dane osobowe ani dane projektu (imiona domowników, nazwiska, firmy, adres,
> działki, telefony, e-maile, kwoty, notatki, treść wpisów). Pilnują tego `tools/build.py` i hook `.githooks/pre-commit`
> – ale przed każdym commitem i tak przejrzyj `git diff`.

## Struktura

```
Dom/                              ← folder budowy (centrum dokumentów, poza gitem)
  _Przychodzące/                  ← tu wrzucasz nowe pliki od projektantów i wykonawców
  _Do claude.ai/                  ← paczka (generowana): przewodnik po dokumentach + ściąga → wiedza projektu „Dom” na claude.ai
  Zdjęcia/                        ← zdjęcia z budowy (RRRR-MM-DD_<krok>/), poza indeksem i paczką
  Ściąga projektu.md              ← kopia ściągi z Notion („📐 Dane projektu”) do paczki awaryjnej
  .dom/                           ← indeks dokumentów, stan wgrania, lista słów zakazanych w repo
    wiedza/                       ← dane indeksu wiedzy (.dom/wiedza/) – poza repo, nigdy w git
  … foldery tematyczne (projekt, konstrukcja, instalacje, wyceny…)
  AI/dom/                         ← to repozytorium
    CLAUDE.md, AGENTS.md, GEMINI.md   ← punkty wejścia agentów
    .claude-plugin/marketplace.json   ← repo jest marketplace'em dla claude.ai (dwa pluginy)
    plugins/ja/skills/                ← procedury osobiste (Dziennik, zadania, emocje, dziecko, suple, przegląd dnia, harness)
    plugins/dom-budowa/skills/        ← procedury budowy
    .claude/skills/, .agents/skills/  ← dowiązania na każdy skill obu pluginów (odtwarza tools/build.py)
    .claude/settings.json             ← zezwolenia (hooków startowych nie ma – lista wyboru na starcie sesji: CLAUDE.md)
    .githooks/                        ← pre-commit (pliki, autor), commit-msg (wiadomość), pre-push (każdy wysyłany commit)
    tools/build.py                    ← walidacja (w tym dane osobowe) + dowiązania skilli + paczki dist/ (po jednej na plugin)
    tools/dokumenty.py                ← indeks folderu budowy i paczka dla claude.ai
    tools/wiedza.py                   ← indeks Bazy wiedzy (SQLite FTS5 z Notion, tylko do odczytu)
```

## Jak to działa

```
Telefon / czat ── poprawka sposobu pracy ──► Notion „Zmiany do harnessu” (obowiązuje od razu)
                                                   │
Claude Code (komputer; na starcie lista wyboru, domyślnie nic) ◄──┘
   ├─ „Dokumenty budowy” (tools/dokumenty.py): skan folderu budowy → paczka `_Do claude.ai/` + lista „do wgrania”
   ├─ „Indeks wiedzy” (tools/wiedza.py sync --publikuj --cicho): odświeża indeks Bazy wiedzy z Notion i publikuje kopię dla czatu
   ├─ klasyfikuje nowe dokumenty (procedura `dokumenty`)
   └─ wdraża zmiany harnessu → wersja → commit → push ──► GitHub sztalinux/notion-plugin
                                                               │ ręczne odświeżenie pluginów (claude-ai-projekt.md)
claude.ai (telefon, czat, Cowork) ◄── pluginy ja + dom-budowa ─┘   (każda rozmowa, bez projektu)
   ├─ projekt „Dom” – tylko kontener dokumentów budowy (wgrywasz paczkę ręcznie, opcjonalnie)
   └─ zaplanowane zadanie „Przegląd dnia” (poza projektem) ──► 📓 Dziennik w Notion
```

## Procedury

**Plugin `ja`**

| Procedura | Kiedy | Co robi |
|---|---|---|
| `ja` | każda rozmowa o dniu, zadaniach, emocjach, dziecku, Dzienniku, harnessie | kontekst, zasady, mapa procedur, skrzynka zmian |
| `wpisy` | „przerób dziennik”, luźne notatki naraz | rozpoznaje obszar wg bazy „🧭 Obszary Dziennika”, przekazuje do procedury, niejasne → „❓” w Dzienniku |
| `emocje` | „czułem…”, „dziś w pracy…”, „podsumuj emocje” | Wpisy emocji, Dziennik produktywności, podsumowania na prośbę |
| `zadania` | „muszę…”, „zrobiłem X”, „co mam jutro” | wspólna TASKS z polem Obszar; zmiana statusu z Dziennika |
| `dziecko` | obserwacja, „porozmawiać z nią o…”, prezent, zalecenie | strona dziecka w sekcjach |
| `suple` | „kończy się…”, „kupiłem…”, przerwa | baza Suple: Buy, Status, Last break |
| `przeglad-dnia` | co 1–2 h (tryb szybki) i wieczorem (zaplanowane) / „przegląd dnia” | szybki: nowe wpisy na bieżąco, pusto = koniec bez zapisów; wieczorny: podsumowanie dnia, zmiany w zadaniach (także ręczne) z uzupełnieniem pustych kolumn i plan na jutro – osobiste pod Dziennikiem, budowa osobno na DOM (z odnośnikiem), analiza pomysłów |
| `przeglad-tygodnia-osobisty` | raz w tygodniu (zaplanowane) / „przegląd tygodnia” | sprawy osobiste w liczbach, zaległe, najbliższy tydzień, porządki w Dzienniku; uruchamia przegląd budowy i linkuje do niego |
| `rozwoj-harnessu` | „zapamiętaj na przyszłość”, nowa procedura, „mam pomysł…”, „zrób POM-n” | skrzynka w Notion → wdrożenie do repo; pomysły → analiza → wdrożenie na polecenie |

**Plugin `dom-budowa`**

| Procedura | Kiedy | Co robi |
|---|---|---|
| `budowa` | każda rozmowa o budowie | kontekst, zasady, mapa procedur, luźne wpisy o budowie, część budowlana przeglądu dnia |
| `oferta` | oferta / wycena / rozmowa z ekipą | rozbicie, zakres 01–13, zgodność z projektem, porównanie, pytania; „sam czy ekipa”; zakres do umowy |
| `koszty` | Excel, wydatek, faktura, „ile wydaliśmy” | plan / umówione / wydane, wiersze do wklejenia, płatności i transze |
| `notatka` | „zapisz”, „ustaliliśmy”, „decyzja” | Notatnik budowy, TASKS (Obszar Dom), „Do zamknięcia” |
| `analiza-techniczna` | projekt, rysunek, umowa, pytanie techniczne, „jak to zrobić samemu” | [projekt]/[szacunek]/[opinia], pytania do projektanta, instrukcja pracy własnej |
| `wiedza` | transkrypcja, artykuł, „dzwoniłem do…”, „SP-n: …”, „co wiemy o…” | Baza wiedzy, sprzeczności (ADR), odczyt stanu wiedzy; szukanie i duplikaty przez indeks `tools/wiedza.py` |
| `dokumenty` | nowe pliki, „wgrałem”, „gdzie jest…” | folder budowy, indeks, paczka dla claude.ai, przewodnik w Notion |
| `etap` | „zaczynamy etap”, „jutro betonowanie”, odbiór, usterki | plan etapu, bramki „bez odwrotu”, protokół odbioru |
| `dziennik` | „dziś na budowie…”, zdjęcia, godziny własne, roboty dodatkowe | Dziennik budowy w Notion, przekazanie kosztów/zadań |
| `harmonogram` | „ekipa wchodzi…”, „przesuwamy…”, „czekam na…”, „co mnie czeka” | harmonogram w Notion (oś czasu), terminy pochodne (zamówienia, bramki, ludzie), przesunięcia |
| `zakupy` | „co kupić na…”, „kiedy zamawiać”, oferta hurtowni, dostawa | lista z kosztorysu, wyprzedzenia, porównanie dostawców |
| `przygotowanie` | „jutro spotkanie z…”, „o co zapytać”, „kogo wybrać z kilku” | karta przygotowania: pytania, czerwone flagi, macierz decyzji, zapis po spotkaniu |
| `przeglad-tygodnia` | poniedziałek / „co nowego” | decyzje, nowa wiedza, terminy, budowa, zamówienia, porządki |

## Indeks wiedzy

`tools/wiedza.py` trzyma lokalną kopię czterech baz Bazy wiedzy z Notion w SQLite z wyszukiwaniem pełnotekstowym (tylko do odczytu –
zapisy idą wyłącznie do Notion). Polecenia: `sync`, `szukaj`, `temat`, `duplikaty`, `stan`, `publikuj`. Dane leżą w `.dom/wiedza/` poza repo
i nigdy nie trafiają do git. Konfiguracja – plik `.dom/sekrety.env` (tryb 600, poza repo), cztery zmienne: `NOTION_TOKEN` (odczyt Notion),
`GITHUB_REPO` (prywatne repo kopii dla czatu na telefonie), `GITHUB_TOKEN_SYNC` (zapis kopii na Macu), `GITHUB_TOKEN_SEARCH` (odczyt kopii w czacie).
Trzy kanały użycia i ograniczenia: `plugins/dom-budowa/skills/wiedza/references/indeks.md`.
`tools/wiedza_jakosc.py` obserwuje jakość wyszukiwania (log zapytań `szukaj`, zbiory oceny, raport tygodniowy z alarmami,
ocena ręczna, miesięczne porównanie z Notion; pytania wymyślone: `tools/wiedza_jakosc_pytania.json`) – dane w `.dom/wiedza/`; opis: `plugins/dom-budowa/skills/wiedza/references/indeks-jakosc.md`.
`tools/wiedza_sedzia.py` (polecenie `wiedza_jakosc.py sedzia`, na sucho bez `--wyslij`) – sędzia LLM trafności wyników przez `claude -p` (kanarek izolacji, filtr danych osobowych); opis: `plugins/dom-budowa/skills/wiedza/references/indeks-sedzia.md`.

## Start

1. Repo sklonowane do `Dom/AI/dom` (folder budowy = dwa poziomy wyżej; inny – zmienna `DOM_HUB`),
   `git config core.hooksPath .githooks`, `git config user.email <id>+<login>@users.noreply.github.com`
   (autor commitów jest publiczny; imię inwestora dozwolone, e-mail tylko noreply). Lista słów zakazanych: `Dom/.dom/zakazane-w-repo.txt`
   (nazwiska, firmy, miejscowość – po jednym w linii; plik poza repo).
2. Python 3 + `pip3 install --user openpyxl pypdf` (kontrola danych wrażliwych w paczce).
3. W `Dom/AI/dom` uruchom `claude`. `/mcp` – jeśli jest „claude.ai Notion”, gotowe.
4. claude.ai → Customize → Plugins → Add marketplace → `sztalinux/notion-plugin` → zainstaluj `ja` i `dom-budowa`,
   włącz „Sync automatically” (jeśli organizacja na to pozwala). Bez synchronizacji – jak pobrać nową wersję:
   `plugins/ja/skills/rozwoj-harnessu/references/claude-ai-projekt.md`.
5. claude.ai → trzy zaplanowane zadania **poza projektem** (trzecie: raz w tygodniu „Przegląd tygodnia (skill
   przeglad-tygodnia-osobisty z pluginu ja)”): co 1–2 h w ciągu dnia „Dziennik – szybki przebieg (skill
   przeglad-dnia z pluginu ja, tryb szybki)” i raz wieczorem „Przegląd dnia (skill przeglad-dnia z pluginu ja, tryb wieczorny)”.
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
- Wszystko, co przyjdzie Ci do głowy (emocja, zadanie, dziecko, suplement, budowa), wpisuj na stronę „📓 Dziennik” w Notion –
  punkt pod punktem albo jako podstronę (telefon wystarczy; widget „nowa strona” w telefonie zakłada stronę na najwyższym
  poziomie Private – też trafi do Dziennika). Szybki przebieg co 1–2 h i wieczorny przegląd dnia rozłożą to według bazy „🧭 Obszary
  Dziennika”, a pod niejasnymi dopisze pytania w „❓”. Nowy rodzaj wpisu = nowy wiersz w Obszarach, bez zmian w harnessie.
  Ręcznie: „przerób dziennik”.
- Poprawki „na przyszłość” z telefonu trafiają do skrzynki w Notion; Claude Code wdroży je po zaznaczeniu „Skrzynka zmian” na starcie sesji.
- Dzień na budowie → powiedz asystentowi, co się działo (telefon wystarczy) – trafi do Dziennika budowy; zdjęcia wrzuć do `Dom/Zdjęcia/RRRR-MM-DD_<krok>/`.
- Przed krokiem „bez odwrotu” (beton, zasypka, tynki) zapytaj „co sprawdzić przed …” – dostaniesz bramkę z listą zdjęć do zrobienia.
- Każda zmiana w repo = podbita wersja zmienionego pluginu w `plugins/<plugin>/.claude-plugin/plugin.json` (inaczej claude.ai
  jej nie pobierze). Po pushu odśwież pluginy na claude.ai (o ile nie działa synchronizacja) – `rozwoj-harnessu/references/claude-ai-projekt.md`.
- Procedury działają same – piszesz normalnie, w dowolnej rozmowie. `/` (np. `/oferta`, na claude.ai `dom-budowa:oferta`) tylko gdy
  chcesz wymusić procedurę.
