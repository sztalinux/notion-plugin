---
name: harmonogram
description: Planowanie w czasie – harmonogram budowy (kroki z datami, kto, zależności, oś czasu w Notion), terminy wynikające z harmonogramu (kiedy zamówić, kiedy bramka, kto musi być), „czekam na” (co inni mają zrobić i do kiedy), przesuwanie terminów i „co mnie czeka”. Używaj, gdy użytkownik mówi „ekipa wchodzi 3 listopada”, „przesuwamy płytę o tydzień”, „ułóż harmonogram”, „kiedy co zamówić”, „do piątku mam dać znać…”, „X ma mi przysłać do…”, „czekam na…”, „co mnie czeka w tym / przyszłym tygodniu”, „co jest po terminie”, „kiedy skończymy stan zero”.
---

# Harmonogram i terminy

Cel: inwestor podaje daty raz, a asystent pilnuje wszystkiego, co z nich wynika – zamówień z wyprzedzeniem, bramek przed
krokami „bez odwrotu”, obecności kierownika i geotechnika, terminów obiecanych przez innych. Excel trzyma pieniądze,
Notion trzyma czas.

## Gdzie co jest (Notion; ID i pola: `budowa/references/notion-mapa.md`)

| Co | Baza | Klucz |
|---|---|---|
| Kroki budowy w czasie | **Harmonogram** `collection://d7a479ab-1e23-453f-8f59-55f4097f7d04` | Krok, Nr etapu (= Excel, arkusz Etapy), Termin (od–do), Kto, Status, Pewność terminu, Bez odwrotu, Zależy od / Blokuje |
| Moje zadania i cudze terminy | **TASKS** `collection://2a9f5982-09e7-81be-91e8-000b0e10a05e` (wspólna z pluginem `ja` – zawsze **Obszar = Dom**) | When, Status, **Kto**, Obszar, Harmonogram |
| Materiał do zamówienia | **Zamówienia i dostawy** `collection://a9854c6c-43ec-4bc1-8ef0-273fb02261c7` | Zamówić do, Dostawa, Status, Krok |
| Umowa, w ramach której ekipa robi krok | **Umowy i gwarancje** `collection://60c06f30-7867-435d-8f2e-1e025a3daa5c` | Kroki |

Rzeczy bez daty (pytania, „pamiętać”) zostają w Notatniku – do TASKS trafia tylko to, co ma datę albo konkretny następny krok.

## A. Ułożenie harmonogramu („ułóż harmonogram stanu zero”, „ekipa wchodzi 3.11”)

1. Kroki z Excela (arkusz Etapy: numer, nazwa, Ekipa/Sam) i z planu etapu (`etap`, sekcja A). Nie dziel na drobne –
   krok = coś, co ma swój termin i odbiór (wykop, chudziak, płyta, ściany piwnicy, izolacje, zasypka, strop…).
2. Dla każdego kroku: Termin (od–do), Kto, Wykonawca, Zależy od, Bez odwrotu (betonowanie, zasypka, zakrycie instalacji),
   Pewność terminu (Szacunek / Uzgodnione ustnie / Potwierdzone na piśmie). Długości i przerwy technologiczne
   (dojrzewanie betonu, schnięcie) – `zakupy/references/wyprzedzenia.md`; nieznane → szacunek z oznaczeniem.
3. Pokaż plan jako tabelę (Nr | Krok | od–do | Kto | zależy od | bez odwrotu) i zapisz po „ok” jednym wywołaniem.
4. Od razu wygeneruj **terminy pochodne** (sekcja B).

## B. Terminy pochodne (po każdym nowym lub przesuniętym kroku)

Dla kroku z datą wylicz i zaproponuj jednym zestawem:
- **Zamówienia:** materiał na krok (`zakupy`, sekcja A) → wiersze w Zamówieniach z „Zamówić do” = start kroku minus
  wyprzedzenie (`zakupy/references/wyprzedzenia.md`) minus 2 dni zapasu; dostawa ≥ 1 dzień przed startem.
- **Bramka:** krok „Bez odwrotu” → zadanie dzień przed: „Bramka: <krok> – sprawdzić wg `etap` (B)”, Kto = Ja.
- **Ludzie:** kto musi być (`etap/references/formalnosci.md`, „kto musi być obecny”): kierownik przy odbiorze zbrojenia,
  geotechnik przy dnie wykopu → zadanie „umówić <kogo> na <data>” z wyprzedzeniem 3–7 dni.
- **Pogoda:** betonowanie, izolacje, tynki zewnętrzne – w zadaniu bramki dopisz „sprawdzić prognozę” (progi: `etap`).
- **Płatności:** transza po odbiorze kroku – przypomnienie dla `koszty` (sekcja D), bez kwot w Notion.
Każde zadanie/zamówienie podpinaj relacją do kroku – wtedy przesunięcie kroku przesuwa je razem z nim.

## C. Przesunięcie („płyta przesunięta o tydzień”, „ekipa spóźni się 3 dni”)

1. Zmień Termin kroku (Status „Przesunięte”, w Uwagach powód i data zmiany).
2. Przelicz kroki, które od niego zależą (relacja Blokuje), i ich terminy pochodne (zamówienia, bramki, umówieni ludzie).
3. Pokaż zestawienie „było → jest” i co trzeba **odwołać lub przesunąć u innych** (dostawa, kierownik, pompa) – to są
   zadania dla inwestora (Kto = Ja). Zapisz po „ok”.

## D. Czekam na („geodeta tyczy w czwartek”, „ekipa ma przysłać wycenę do 15.10”)

- Cudzy termin → TASKS: Name „<kto> – <co>”, **Kto** = ta osoba/rola, Status „WAITING”, Obszar = Dom, When = termin, Desc = skąd wiadomo
  (rozmowa, data). Gdy dotyczy kroku – relacja Harmonogram.
- Mój termin wobec kogoś („do piątku dam znać X”) → TASKS: Kto = Ja, Status „TO DO”, Obszar = Dom, When = termin.
- Po terminie: „czekam na” bez zmiany statusu → w przeglądzie (i w „co mnie czeka”) jako „przypomnij się <komu>”.
- „Zrobione / przyszło” → DONE; jeśli wynikło z tego ustalenie – `notatka`, wiedza – `wiedza`.

## E. „Co mnie czeka” (domyślnie 14 dni)

Jedno zestawienie, chronologicznie: kroki harmonogramu (start/koniec), moje zadania, czekam na (z terminem i po terminie),
zamówienia z „Zamówić do” i dostawy, bramki. Na górze: po terminie i dzisiaj/jutro. Na dole: licznik spraw dalej niż 14 dni.

## Zasady

- Daty względne licz od daty podanej w rozmowie/wpisie (Dziennik: `@today`); brak daty przy terminie → zapytaj.
- Terminów innych osób nie zmieniaj „na domysł” – tylko z ich informacji (inwestor relacjonuje) i z Pewnością terminu.
- Kwoty nigdy w Harmonogramie ani Zamówieniach – Excel (`koszty`).
- Termin w Notatniku (pole Kiedy) i zadanie w TASKS dla tej samej sprawy → zadanie w TASKS, w Notatniku link; nie dubluj dat.
