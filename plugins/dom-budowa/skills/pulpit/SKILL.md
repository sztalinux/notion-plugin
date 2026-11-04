---
name: pulpit
description: Synchronizacja pulpitu budowy (artefakt claude.ai z decyzjami, rozbieżnościami, krokami etapu, checklistą i zadaniami) z Notion – odczyt tego, co inwestor zaznaczył na stronie, zapis do Notion, odświeżenie danych strony i publikacja pod stałym adresem. Tylko sesja interaktywna Claude Code. Używaj, gdy użytkownik mówi „zsynchronizuj pulpit”, „odśwież pulpit”, „pokaż, co by się zmieniło” (pulpit), „przenieś decyzje z pulpitu”, „opublikuj pulpit”, wkleja polecenie z przycisku „Odśwież” na stronie pulpitu, albo pyta, co pulpit zapisał w Notion i które konflikty czekają.
---

# Pulpit budowy – synchronizacja

Pulpit to strona (artefakt claude.ai), na której inwestor wybiera warianty decyzji, oznacza rozbieżności, odhacza kroki,
punkty checklisty i zadania. Strona trzyma te zmiany w swojej bazie, **Notion jest źródłem prawdy**. Ta procedura przenosi
zmiany z bazy strony do Notion, ściąga z Notion świeże dane i publikuje stronę. Nic nie dzieje się samo – tylko na polecenie.

**Tylko sesja interaktywna Claude Code.** Narzędzia artefaktów (odczyt i zapis bazy strony, publikacja) nie istnieją w trybie
`claude -p`, w zaplanowanych zadaniach ani na telefonie (test 1.11.2026). Brak tych narzędzi → zatrzymaj się, powiedz to jednym
zdaniem i nie szukaj obejść (ani innego kanału do artefaktu, ani zapisu do Notion „na piechotę”).

## Gdzie co leży

| Co | Gdzie |
|---|---|
| Kod pulpitu, skrypty, testy, `dist/` | **prywatne** repo – `<repo pulpitu>`, domyślnie `AI/pulpit` w folderze budowy (nie w tym harnessie) |
| Dane robocze (nigdy w repo) | `.dom/pulpit/` w folderze budowy: `dane.json` (wynik pull), `stan.json` (zrzut bazy strony), `sync-log.jsonl`, `notion-zapisy.jsonl` |
| Adresy artefaktów: pulpit, specyfikacja, tablica prac | `.dom/pulpit/adresy.md` (prywatny plik poza repo; adresów nie przepisuj do harnessu ani do commitów) |
| Pola Notion, na których to stoi | `budowa/references/notion-mapa.md` (Notatnik: NT, Pulpit, Dotyczy etapu, Krok; Harmonogram; Checklista) |
| Szczegóły: kolekcje bazy strony, mapowania, konflikty, log | `references/obieg.md` |

Skrypty uruchamiaj z `<repo pulpitu>`; tokeny Notion czytają same z pliku sekretów w folderze budowy – nie wypisuj ich ani nie
kopiuj do odpowiedzi.

## Tryby

- **Pełny** („zsynchronizuj pulpit”, „odśwież pulpit”, polecenie z przycisku „Odśwież”) – kroki 0–6.
- **Podgląd** („pokaż, co by się zmieniło”) – kroki 1–3 bez żadnego zapisu: push tylko `--dry-run`, bez publikacji, bez zmian
  w bazie strony (także bez zamykania prośby i bez `meta/sync`). Na końcu napisz, co zrobi tryb pełny.
- **Bezobsługowy** (nikt nie odpowie na pytania) – konflikt pomiń i wpisz do raportu; reszta idzie dalej.

## Obieg

0. **Przygotowanie.** Odczytaj adresy z `.dom/pulpit/adresy.md`. Załóż blokadę (`mkdir .dom/pulpit/sync.lock`; istnieje →
   inny obieg trwa albo został po awarii: zapytaj, nie zdejmuj sama). Odczytaj `meta/prosba` z bazy strony; stan „nowa” ustaw na
   „w toku” (kto, kiedy). Brak prośby i polecenie wprost od inwestora → rób dalej; brak prośby i brak polecenia → nic nie publikuj.
1. **Baza strony → `stan.json`.** Dla kolekcji `decyzje`, `rozb`, `zadania`, `kroki`, `checklista`, `spotkania`, `meta` wykonaj
   odczyt całej kolekcji (ArtifactData, akcja `list`; kolejne strony wyników do końca). Zapisz `.dom/pulpit/stan.json` wg
   `data/schema/stan.schema.json` w `<repo pulpitu>` (pola dokumentu bez zmian, klucz dokumentu = klucz rekordu).
2. **Push do Notion.** `python3 tools/pulpit_push.py --dry-run` → pokaż inwestorowi plan (tabela: pozycja, co zmieni w Notion).
   - **Konflikt** (strona zmieniona w Notion po ostatnim pull) → pokaż obie wersje i zapytaj, nie nadpisuj: „zostaje moje” albo
     „zostaje Notion” (`references/obieg.md`, „Konflikty”). Bezobsługowo: pomiń i zostaw w raporcie.
   - Po „ok” (albo bez pytania, gdy plan nie ma konfliktów i inwestor wydał polecenie pełnego obiegu) uruchom
     `python3 tools/pulpit_push.py`. Na podstawie JSON-u wyniku ustaw w bazie strony `sync` i `wersja_notion` dla każdej
     zapisanej pozycji (ArtifactData, `update`; wiele rekordów – jedno wywołanie zbiorcze), a `konflikt` dla zatrzymanych.
3. **Pull z Notion.** `python3 tools/pulpit_pull.py` → `.dom/pulpit/dane.json` i raport braków (rekordy bez etapu, źródeł,
   numeru NT). Błąd walidacji → stary `dane.json` zostaje; zgłoś i nie publikuj.
4. **Testy.** W `<repo pulpitu>`: `npm run check` (build + testy). Czerwono → **nie publikuj**, zgłoś, co padło (🛑),
   zdejmij blokadę, w `meta/prosba` ustaw „błąd” z krótkim powodem.
5. **Publikacja.** Opublikuj `dist/pulpit.html` narzędziem Artifact pod stałym adresem pulpitu (`url` z `adresy.md`; nigdy
   nowy adres) **razem z plikami obok strony**: `files` = {`styl.css`: `dist/styl.css`, `skrypt.js`: `dist/skrypt.js`,
   `dane.js`: `dist/dane.js`} – zawsze wszystkie trzy (od 0.10.0 dane leżą w `dane.js`; pominięty plik zostaje stary, więc
   strona pokazałaby nowy kod ze starymi danymi). Publikuj `dane.js`, nie `dist/dane.json` (to tylko podgląd). Narzędzie wymaga
   wcześniejszego odczytu z nowej sesji: odczyt `index.html` (ok. 30 KB) i `action: "list"`, `scope: "files"` dla adresu
   pulpitu (ścieżki bez treści); nie czytaj `skrypt.js` ani `dane.js`. Potem w bazie strony: `meta/sync` (czas, wersja strony, liczby) i `meta/prosba` → „wykonana” (kto, kiedy).
   Dopisz linię do `.dom/pulpit/sync-log.jsonl` (wyzwalacz, liczby, konflikty, wersja strony – `references/obieg.md`).
   Zdejmij blokadę (`rmdir .dom/pulpit/sync.lock`).
6. **Podsumowanie** w blokach jak w innych procedurach (format: `budowa`, „Domknięcie każdej rozmowy”):
   - 🛑 konflikty do rozstrzygnięcia i czerwone testy – z propozycją domyślną;
   - ✅ co zapisano w Notion (liczby wg rodzaju: decyzje, rozbieżności, zadania, kroki, checklista), ile rekordów w pull,
     wersja strony;
   - ⏳ **do czatu** (skrypt ich nie zapisuje): sprzeczności rozstrzygnięte na stronie (→ `wiedza`, z relacją do decyzji),
     notatki ze spotkań (`spotkania/*` → wpis w Rozmowach i źródłach, dalej `wiedza`), pominięte konflikty, braki z pull.

## Zasady

- **Nigdy nie nadpisuj po cichu.** Strona zmieniona w Notion po pull-u = konflikt, decyduje inwestor. Ręczna zmiana inwestora
  w Notion jest nadrzędna (`budowa`, zasada 11).
- **Nic nie usuwaj** – ani stron Notion, ani rekordów bazy strony. Odznaczenie na stronie nie cofa statusu w Notion.
- **Zapisy do Notion robi wyłącznie `pulpit_push.py`** (statusy, odhaczenia, wybór i notatka decyzji; nie zakłada stron).
  Resztę – sprzeczności SP, notatki ze spotkań, zakładanie wpisów – robi czat własnymi procedurami (`wiedza`, `notatka`).
- Każdy zapis do Notion jest logowany (`sync-log.jsonl`, `notion-zapisy.jsonl`).
- **Publikacja tylko po zielonych testach** i tylko pod stałym adresem. Awaria w środku → poprzedni `dane.json` i poprzednia
  strona zostają.
- Powtórzony obieg bez zmian nic nie robi (klucz rekordu + `sync`/`wersja_notion`) – można go bezpiecznie uruchomić ponownie.
- Dane projektu nigdy w harnessie: ani w tej procedurze, ani w commitach, ani w przykładach (przykłady: „NT-1”, „Firma A”).
- Tokeny, adresy artefaktów i treść `stan.json` / `dane.json` nie trafiają do odpowiedzi poza tym, co potrzebne do decyzji.
