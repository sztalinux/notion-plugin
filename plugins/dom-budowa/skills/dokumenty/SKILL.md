---
name: dokumenty
description: Porządek w dokumentach budowy (folder budowy na komputerze inwestora) i paczka aktualnych plików dla claude.ai. Używaj, gdy raport „[dokumenty]” (z listy startowej) pokazuje nowe lub zmienione pliki, gdy inwestor mówi „wrzuciłem plik”, „dostałem nowy projekt / ofertę / umowę”, „posortuj dokumenty”, „co mam wgrać do claude.ai”, „wgrałem”, albo pyta, gdzie jest dany dokument lub która wersja jest aktualna.
---

# Dokumenty budowy

Wszystkie pliki od projektantów, wykonawców i urzędów leżą w **folderze budowy** na komputerze inwestora
(katalog dwa poziomy nad repo harnessu; inny – zmienna `DOM_HUB`). Inwestor wrzuca je tam, najlepiej do `_Przychodzące/`.
Skrypt `tools/dokumenty.py` (uruchamiany z listy startowej Claude Code – pozycja „Dokumenty budowy” – albo na polecenie) prowadzi indeks plików
i buduje folder `_Do claude.ai/` – paczkę do wgrania w wiedzy projektu „Dom” na claude.ai.

**Przewodnik po dokumentach** (każdy aktualny dokument: co to jest, na jakie pytania odpowiada, gdzie leży, plus mapa
Notion) generuje skrypt; Claude Code przepisuje go na stronę Notion (sekcja C), skąd czyta go asystent na claude.ai –
bez wgrywania czegokolwiek. Pełne dokumenty nie zajmują kontekstu: gdy odpowiedź wymaga ich treści, asystent prosi
inwestora o konkretny plik. Excel też nie leży w projekcie – kopia szybko się starzeje, inwestor załącza aktualny.
Paczka (`00_SPIS.md` + ściąga) to tylko kopia awaryjna.

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
na komputerze, strona/arkusz i po co, np. „Potrzebuję projektu konstrukcji (`Projekt/Konstrukcja.pdf`, arkusz KT.03,
s. 3) – sprawdzę otulinę zbrojenia płyty”. Do czasu załączenia nie odpowiadaj z pamięci ani z domysłów; możesz podać,
co już wiadomo ze ściągi, z oznaczeniem źródła. W Claude Code nie proś – przeczytaj plik z folderu budowy.

## A. Klasyfikacja nowych plików

1. Lista: raport ze startu sesji albo `python3 tools/dokumenty.py lista --nowe`.
2. Dla każdego pliku ustal: co to jest (nazwa, folder, w razie wątpliwości pierwsza strona), kategorię, czy jest
   nowszą wersją czegoś, co już jest w paczce.
3. **Przewodnik (`--zawartosc`)** – każdy dokument przydatny agentom, w **jednej, najnowszej** wersji: projekty
   (architektura, konstrukcja, instalacje – najlepiej komplet w jednym PDF), opinie geotechniczne, warunki
   i uzgodnienia, oferty i wyceny, umowy, karty techniczne produktów, kosztorys Excel. Przeczytaj dokument (duże PDF-y
   przejrzyj: spis treści, nagłówki, arkusze) i zapisz 2–4 zdania (do ~500 znaków): **na jakie pytania odpowiada
   i gdzie w nim szukać** – sekcje/arkusze ze stronami, rodzaje parametrów, wersja i data. Nie przepisuj faktów ani kwot –
   te idą do ściągi i Notion; przewodnik ma być krótki, bo jest w kontekście każdej rozmowy.
   Poza przewodnikiem (bez `--zawartosc`, `--bez-eksportu` z opisem dlaczego): starsze wersje, pojedyncze arkusze
   zawarte w komplecie, archiwa `.zip`, notatki pisane przez AI (to opinie, nie dokumenty), faktury, pliki niezwiązane z budową.
4. **Do wiedzy projektu (`--eksport`)** – domyślnie nic poza ściągą (przewodnik dodaje skrypt). Pełny dokument
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
  (procedura `analiza-techniczna`) i aktualizację ściągi: Notion → „📐 Dane projektu (ściąga)” (jedyne źródło), Notatnik;
  po zmianie w Notion przepisz tę samą treść do `Ściąga projektu.md` w folderze budowy (kopia do paczki awaryjnej).
- Oferta wykonawcy → procedura `oferta`.
- Ostrzeżenia skryptu („powyżej limitu”, informacja o danych osobowych) przekaż inwestorowi jednym zdaniem z propozycją
  (np. zmniejszona kopia PDF obok oryginału, oznaczona do paczki zamiast niego).
- Na koniec podaj listę „dodaj / podmień / usuń” z raportu. Po słowach „wgrałem”: `python3 tools/dokumenty.py wgrane`.

## C. Przewodnik w Notion (Claude Code, automatycznie)

Strona Notion „📑 Przewodnik po dokumentach i Notion” (`3f6f5982-09e7-81f5-bade-ec877d8d936a`) jest głównym przewodnikiem
dla asystenta na claude.ai – czyta go z Notion, więc inwestor niczego nie wgrywa. Treść generuje skrypt
(`.dom/przewodnik-notion.md` w folderze budowy: dokumenty + dwie mapy Notion – budowa z `budowa/references/notion-mapa.md`
i sprawy osobiste z `ja/references/notion-mapa.md`, plugin `ja`).

1. Raport startowy pokazuje „Przewodnik zmieniony → przepisz stronę Notion…” → bez pytania zastąp całą treść strony
   zawartością pliku (jedno wywołanie, plik już ma składnię Notion; nie zmieniaj jej ręcznie).
2. Potem `python3 tools/dokumenty.py notion-ok`. Zgłoś jedną linią: „Przewodnik w Notion zaktualizowany”.
3. Paczka `_Do claude.ai/` to tylko kopia awaryjna (np. gdy Notion jest niedostępny) – wgrywanie jest opcjonalne.

## Zasady

- Paczka i folder budowy **nigdy** nie trafiają do repozytorium (repo jest publiczne) – dane osobowe są dozwolone
  w paczce, w repo nigdy.
- Nie przepisuj treści dokumentów do harnessu – fakty idą do ściągi i Notion.
- Zdjęcia z budowy leżą w `Zdjęcia/RRRR-MM-DD_<krok>/` (procedura `dziennik`); skrypt pomija foldery `Zdjęcia*`,
  więc nie trafiają do indeksu ani do paczki. Rysunek czy skan jako obraz → do folderu tematycznego, nie do Zdjęć.
- Gdy nie wiesz, czy plik jest nowszą wersją – zapytaj inwestora jednym pytaniem, zamiast zgadywać.
