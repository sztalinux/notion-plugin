---
name: notatka
description: Zapis notatek, ustaleń, decyzji, pytań, ryzyk i zadań budowy do Notion (Notatnik budowy, TASKS). Używaj, gdy użytkownik dyktuje lub wkleja notatkę z budowy, rozmowy z projektantem/ekipą, mówi „zapisz”, „zanotuj”, „dodaj do Notion”, „przypomnij mi”, „ustaliliśmy że…”, „decyzja: …”, albo gdy inna procedura wygenerowała otwarte pytania lub decyzje.
---

# Notatka → Notion

Cel: żadna myśl nie zostaje jako luźny tekst. Każda trafia jako wiersz z typem, etapem,
branżą i adresatem, tak żeby dało się ją filtrować i zamknąć.

## Procedura

1. **Rozbij wejście na jednostki** – jedna myśl = jeden wiersz. Sklasyfikuj każdą:

   | Rodzaj | Gdzie | Typ / Status |
   |---|---|---|
   | pytanie do kogoś | Notatnik budowy | Typ „Pytanie”, Status „Otwarte”, Do kogo = adresat |
   | ustalenie / fakt / rzecz do przypilnowania na budowie | Notatnik budowy | Typ „Pamiętać”, Status „Ustalone” (to nie jest sprawa otwarta – wraca w checkliście etapu, procedura `etap`), Etap = kiedy ma wrócić |
   | decyzja | Notatnik budowy | Typ „Decyzja”, Status „Ustalone”; w Notatce jedno zdanie (co ustalono), w treści strony: *dlaczego, alternatywy, kto zdecydował* |
   | ryzyko | Notatnik budowy | Typ „Ryzyko”, Priorytet wg wpływu |
   | do doczytania / pomysł | Notatnik budowy | Typ „Doczytać” / „Pomysł” |
   | konkretne działanie z terminem | TASKS | Status „TO DO”, When = termin, Kto = Ja, Obszar = Dom |
   | ktoś inny ma coś zrobić do daty („czekam na”) | TASKS | Status „WAITING”, Kto = ta osoba, Obszar = Dom, When – procedura `harmonogram`, D |
   | relacja z dnia na budowie, dostawa, usterka, roboty dodatkowe | → procedura `dziennik` | stąd ustalenia i zadania wracają tu |
   | koszt / płatność | → procedura `koszty` | nie zapisuj kwot tylko w Notion |
   | oferta / wycena | → procedura `oferta` | |
   | kilka luźnych, niejasnych wpisów naraz / „przerób dziennik” | → procedura `wpisy` (plugin `ja`) | wyjaśnia, potem wraca tu |
   | rozmowa z projektantem/wykonawcą, film, artykuł – „kto co powiedział” | → procedura `wiedza` (Rozmowy i źródła, Informacje, Tematy) | stąd tylko działania do Notatnika |

2. **Sprawdź duplikaty:** wyszukaj w Notatniku 2–3 słowa kluczowe. Jeśli wpis istnieje – nie twórz drugiego
   i nie linkuj wpisów do siebie: zostaje jedno źródło prawdy. Zaktualizuj istniejący (status, dopisek z datą);
   nowy szczegół dopisz w treści jego strony (z datą), a gdy informacja pochodzi z innego źródła niż to w polu Źródło –
   dodaj drugie źródło do Źródła (np. „…; pulpit DOM, 10.2026”).
3. **Pokaż plan zapisu** jako tabelę (Nazwa | Typ | Etap | Branża | Do kogo | Priorytet | Status).
   Przy 1–3 oczywistych wpisach zapisz od razu; przy więcej lub przy niepewnej klasyfikacji – poproś o „ok”.
4. **Zapisz jednym wywołaniem na bazę** (wiele stron w jednej operacji; zasada 6 z `budowa`), wartości pól dokładnie
   wg `references/notion-schematy.md`. Źródło = skąd to wiadomo (rozmowa z X dnia RRRR-MM-DD, PT KT.03, oferta Y).
5. **Krytyczne sprawy przed etapem** (blokują start etapu): Priorytet „Krytyczne” i Etap = bieżący etap – wtedy wpis
   sam pojawia się w sekcji „🔴 Do zamknięcia przed …” na stronie DOM (widok Notatnika). Niczego tam nie dopisuj
   ani nie odhaczaj ręcznie; sprawę zamyka Status wpisu.
6. **Ustalenie = wiedza:** wpis ze Statusem „Ustalone”/„Zrobione”, który niesie wiedzę techniczną (decyzja, parametr,
   zasada wykonania, odpowiedź na pytanie) → w tym samym zestawie zapisów dodaj Informację w Bazie wiedzy z relacją
   do tego wpisu (procedura `wiedza`, sekcja F). Tak Baza wiedzy zawsze pokazuje, co u nas obowiązuje i skąd to wiadomo.
7. **Potwierdź:** lista utworzonych/zmienionych wpisów z linkami.

## Zasady

- Nazwa wiersza: krótka i samodzielna („Wysokość drzwi garażu 2,10 m – kolizja z belką”), bez „Notatka z…”.
- Kolumny to właściwości (`budowa`, zasada 12): Notatka w Notatniku i Desc w TASKS – jedno krótkie zdanie;
  szczegóły, listy (np. pozycje do sprawdzenia jako checkboxy), kontekst i dopiski z datą – w treści strony.
- Daty jako daty Notion, nie tekst. Termin względny („za tydzień”) przelicz na datę.
- Nie zmieniaj ani nie usuwaj cudzych wpisów bez prośby; zamknięcie = Status „Zrobione”/„Odrzucone” + dopisek.
- Jeśli narzędzia Notion są niedostępne: przygotuj wpisy jako tabelę Markdown do wklejenia i powiedz o tym wprost.
