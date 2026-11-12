---
name: dokumenty
description: "Porządek w dokumentach budowy (folder budowy na komputerze inwestora), przewodnik po nich na stronie Notion (czyta go claude.ai) i paczka dla claude.ai (kopia awaryjna). Używaj, gdy raport „[dokumenty]” (z listy startowej) pokazuje nowe lub zmienione pliki, gdy inwestor mówi „wrzuciłem plik”, „dostałem nowy projekt / ofertę / umowę”, „posortuj dokumenty”, „co mam wgrać do claude.ai”, „wgrałem” (paczka), albo pyta, gdzie jest dany dokument lub która wersja jest aktualna. Także dokumenty z telefonu i kopia na Dysk Google: „wgrałem fakturę / WZ / wpis kierownika”, „zrób kopię dokumentów”, „wgrałem kopię”, „aplikacja Dysku nie działa”."
---

# Dokumenty budowy

Wszystkie pliki od projektantów, wykonawców i urzędów leżą w **folderze budowy** na komputerze inwestora
(katalog dwa poziomy nad repo harnessu; inny – zmienna `DOM_HUB`). Inwestor wrzuca je tam, najlepiej do `_Przychodzące/`.
Skrypt `tools/dokumenty.py` (uruchamiany z listy startowej Claude Code – pozycja „Dokumenty budowy” – albo na polecenie) prowadzi indeks plików
i buduje folder `_Do claude.ai/` – paczkę do wgrania w wiedzy projektu „Dom” na claude.ai.

**Przewodnik po dokumentach** (każdy aktualny dokument: co to jest, na jakie pytania odpowiada, gdzie leży, plus mapa
Notion) generuje skrypt; Claude Code przepisuje go na stronę Notion (sekcja C), skąd czyta go asystent na claude.ai –
bez wgrywania czegokolwiek. Pełne dokumenty nie zajmują kontekstu: gdy odpowiedź wymaga ich treści, asystent prosi
inwestora o konkretny plik. Kosztorysu też nie ma w projekcie – żyje w arkuszu Google (`koszty`, „Gdzie są liczby”).
Paczka (`00_SPIS.md`) to tylko kopia awaryjna; ściąga jest wyłącznie w Notion („📐 Dane projektu”), bez kopii w pliku.

Podział pracy: skrypt wykrywa nowe/zmienione/przeniesione pliki, duplikaty i dane wrażliwe oraz kopiuje pliki do paczki.
Ty decydujesz, co to za dokument, czy trafia do paczki i co zastępuje. Bez Twojej decyzji nowy plik do paczki nie trafi.

## Gdzie jesteś

| Miejsce | Co robisz |
|---|---|
| Claude Code w repo (widzisz raport „[dokumenty]”) | klasyfikacja – sekcja A, aktualizacja paczki – sekcja B |
| claude.ai (czat, telefon) | ściąga: Notion DOM → „📐 Dane projektu”; przewodnik: strona Notion „📑 Przewodnik po dokumentach i Notion”; potrzebny dokument – poproś o niego (niżej) |
| Gdzie indziej, bez plików | poproś o załączenie konkretnego dokumentu (nazwa z przewodnika) |

**Prośba o dokument** (claude.ai, telefon, Cowork – wszędzie, gdzie nie ma dostępu do folderu budowy): gdy odpowiedź
wymaga treści dokumentu, którego nie ma w rozmowie, napisz jawnie, czego potrzebujesz – nazwa z przewodnika, ścieżka
na komputerze, strona/arkusz i po co, np. „Potrzebuję projektu konstrukcji (`Projekty/Konstrukcja/Konstrukcja.pdf`, arkusz KT.03,
s. 3) – sprawdzę otulinę zbrojenia płyty”. Do czasu załączenia nie odpowiadaj z pamięci ani z domysłów; możesz podać,
co już wiadomo ze ściągi, z oznaczeniem źródła. W Claude Code nie proś – przeczytaj plik z folderu budowy.
Masz konektor Dysku Google → najpierw spróbuj odczytać dokument z `Dom/<folder>` na Dysku (kopia z Maca, sekcja D);
nie ma go albo tekst nieczytelny (rysunki) → poproś jak wyżej.

## A. Klasyfikacja nowych plików

1. Lista: raport ze startu sesji albo `python3 tools/dokumenty.py lista --nowe`.
2. Dla każdego pliku ustal: co to jest (nazwa, folder, w razie wątpliwości pierwsza strona), kategorię, czy jest
   nowszą wersją czegoś, co już jest w przewodniku (`lista` – wpisy z „zawartość”) albo w paczce.
3. **Przewodnik (`--zawartosc`)** – każdy dokument przydatny agentom, w **jednej, najnowszej** wersji: projekty
   (architektura, konstrukcja, instalacje – najlepiej komplet w jednym PDF), opinie geotechniczne, warunki
   i uzgodnienia, oferty i wyceny, umowy, karty techniczne produktów, stare kosztorysy Excel (dziś kosztorys żyje w arkuszu Google). Przeczytaj dokument (duże PDF-y
   przejrzyj: spis treści, nagłówki, arkusze) i zapisz 2–4 zdania (do ~500 znaków): **na jakie pytania odpowiada
   i gdzie w nim szukać** – sekcje/arkusze ze stronami, rodzaje parametrów, wersja i data. Nie przepisuj faktów ani kwot –
   te idą do ściągi i Notion; przewodnik ma być krótki, bo jest w kontekście każdej rozmowy.
   Poza przewodnikiem (bez `--zawartosc`, `--bez-eksportu` z opisem dlaczego): starsze wersje, pojedyncze arkusze
   zawarte w komplecie, archiwa `.zip`, notatki pisane przez AI (to opinie, nie dokumenty), faktury, pliki niezwiązane z budową.
4. **Do wiedzy projektu (`--eksport`)** – domyślnie nic (przewodnik dodaje skrypt). Pełny dokument
   eksportuj tylko na wyraźną prośbę inwestora (np. na czas etapu, w którym jest potrzebny w prawie każdej rozmowie);
   po etapie zaproponuj `--bez-eksportu`. Dane osobowe w dokumentach nie wykluczają eksportu – projekt na claude.ai
   jest prywatny (decyzja inwestora); skrypt raz informuje, co wykrył.
5. Nowa wersja dokumentu: nadaj jej **tę samą** `--nazwa` co poprzedniej i nową `--zawartosc`, a starej usuń
   z przewodnika (`--zawartosc ""`, `--bez-eksportu`, opis „starsza wersja – zastąpiona przez …”). Nazwy są stałe –
   w przewodniku i w projekcie dokument się podmienia, a nie dubluje.
6. Zapisz decyzje (jedno wywołanie na plik):
   `python3 tools/dokumenty.py ustaw "<ścieżka>" --bez-eksportu --nazwa "<NN_Krotka-nazwa.ext>" --kategoria "<NN Kategoria>" --opis "<co to jest, z datą/wersją>" --zawartosc "<na jakie pytania odpowiada, gdzie szukać>"`
   Prefiksy nazw: 00 podsumowanie, 1x projekty, 2x grunt, 3x media i formalności, 4x koszty, 5x oferty, 6x umowy.
   Raport startowy pokazuje „Bez opisu zawartości w przewodniku: N” – uzupełnij je tym samym poleceniem.
7. Pliki z `_Przychodzące/`: przenieś do właściwego folderu tematycznego (istniejącego albo nowego, o czytelnej
   nazwie). Plików poza `_Przychodzące/` nie przenoś ani nie zmieniaj ich nazw. Nigdy nic nie usuwaj.
8. Uruchom `python3 tools/dokumenty.py` – przebuduje przewodnik; gdy się zmienił, zsynchronizuj stronę Notion (sekcja C).

## B. Po klasyfikacji – wiedza i paczka

- Dokument, który zmienia fakty (nowa rewizja projektu, opinia, umowa, wybrana oferta): zaproponuj analizę
  (procedura `analiza-techniczna`) i aktualizację ściągi: Notion → „📐 Dane projektu (ściąga)” (jedyne źródło – bez kopii w pliku), Notatnik.
- Oferta wykonawcy → procedura `oferta`.
- Ostrzeżenia skryptu („powyżej limitu”, informacja o danych osobowych) przekaż inwestorowi jednym zdaniem z propozycją
  (np. zmniejszona kopia PDF obok oryginału, oznaczona do paczki zamiast niego).
- Na koniec podaj listę „dodaj / podmień / usuń” z raportu. Po „wgrałem” o paczce dla claude.ai: `python3 tools/dokumenty.py wgrane`; „wgrałem kopię” (Dysk) – sekcja D.

## C. Przewodnik w Notion (Claude Code, automatycznie)

Strona Notion „📑 Przewodnik po dokumentach i Notion” (`3f6f5982-09e7-81f5-bade-ec877d8d936a`) jest głównym przewodnikiem
dla asystenta na claude.ai – czyta go z Notion, więc inwestor niczego nie wgrywa. Treść generuje skrypt
(`.dom/przewodnik-notion.md` w folderze budowy: dokumenty + dwie mapy Notion – budowa z `budowa/references/notion-mapa.md`
i sprawy osobiste z `ja/references/notion-mapa.md`, plugin `ja`).

1. Raport startowy pokazuje „Przewodnik zmieniony → przepisz stronę Notion…” → bez pytania zastąp całą treść strony
   zawartością pliku (jedno wywołanie, plik już ma składnię Notion; nie zmieniaj jej ręcznie).
2. Potem `python3 tools/dokumenty.py notion-ok`. Zgłoś jedną linią: „Przewodnik w Notion zaktualizowany”.
3. Paczka `_Do claude.ai/` to tylko kopia awaryjna (np. gdy Notion jest niedostępny) – wgrywanie jest opcjonalne.

## D. Dokumenty z telefonu i kopia na Dysku Google

Pełne reguły, tryby bez aplikacji/konektora i przypadki brzegowe: `docs/zdjecia-i-kopia.md` (sekcje 4 i 7; tryby – 5; przypadki brzegowe – 11).
- **Z telefonu** (faktura papierowa, WZ, wpis kierownika, protokół – zdjęcie w `Dom/Zdjęcia/_nowe`, najlepiej w folderze
  „faktura …”, „WZ …”, „dziennik KB”): rozkłada go to samo „rozłóż zdjęcia” (`dziennik`, E). Faktury → `Faktury/RRRR/`
  (`RRRR-MM-DD_sprzedawca_numer`), WZ / karty / deklaracje → `Dostawy/<Etap>/`, wpisy kierownika → `Dziennik budowy KB/`,
  protokoły → `Umowy/Protokoły/`. Sprzedawcę, numer i datę odczytaj z pliku; niepewne → pytanie 🔔. **Zdjęcie faktury
  nie tworzy wydatku** – wydatek tylko na wyraźną prośbę (`koszty`, B).
- **Kopia Mac → Dysk** („zrób kopię dokumentów”, „wgrałem kopię”): `python3 tools/kopia.py stan` → `paczka` (na sucho) →
  `paczka --wykonaj`; inwestor przeciąga `_Na Dysk/<data>` do `Dom/_Kopie` i mówi „wgrałem kopię” → `kopia.py wgrane`,
  potem (z konektorem) rozłóż paczkę wg `docs/zdjecia-i-kopia.md`, 7. Działa aplikacja Dysku → `kopia.py aplikacja`.
  Na Dysk nigdy: `.dom`, `AI`, `Wiedza…`, `_Przychodzące`, `_Do claude.ai`.
- **„Aplikacja Dysku nie działa”** – nic do naprawiania (Mac służbowy – sprawa dla IT inwestora, nie obchodź zabezpieczeń);
  zdjęcia i dokumenty idą konektorem, kopia paczką (`docs/zdjecia-i-kopia.md`, 5 i 8). `kopia.py aplikacja` dopiero, gdy
  inwestor potwierdzi, że aplikacja działa.
- Nic nie kasuj ani nie nadpisuj – stare wersje i usunięte na Macu idą do `_Archiwum` na Dysku.

## Zasady

- Paczka i folder budowy **nigdy** nie trafiają do repozytorium (repo jest publiczne) – dane osobowe są dozwolone
  w paczce, w repo nigdy.
- Nie przepisuj treści dokumentów do harnessu – fakty idą do ściągi i Notion.
- Zdjęcia z budowy leżą na Dysku w `Zdjęcia/<etap>/<krok>/` (`dziennik`, E); skrypt pomija foldery `Zdjęcia*`, `_Na Dysk`,
  `_Kopie`, `_Archiwum`, więc nie trafiają do indeksu ani do paczki. Rysunek czy skan jako obraz → folder tematyczny.
- Gdy nie wiesz, czy plik jest nowszą wersją – zapytaj inwestora jednym pytaniem, zamiast zgadywać.
