---
name: harmonogram
description: Planowanie w czasie – harmonogram budowy (kroki z datami, kto, zależności, oś czasu w Notion), terminy wynikające z harmonogramu (kiedy zamówić, kiedy bramka, kto musi być), „czekam na” (co inni mają zrobić i do kiedy), przesuwanie terminów i „co mnie czeka”. Używaj, gdy użytkownik mówi „ekipa wchodzi 3 listopada”, „przesuwamy płytę o tydzień”, „ułóż harmonogram”, „kiedy co zamówić”, „do piątku mam dać znać…”, „X ma mi przysłać do…”, „czekam na…”, „co mnie czeka w tym / przyszłym tygodniu”, „co jest po terminie”, „kiedy skończymy stan zero”.
---

# Harmonogram i terminy

Cel: inwestor podaje daty raz, a asystent pilnuje wszystkiego, co z nich wynika – zamówień z wyprzedzeniem, bramek przed
krokami „bez odwrotu”, obecności kierownika i geotechnika, terminów obiecanych przez innych. Arkusz kosztorysu trzyma pieniądze,
Notion trzyma czas.

## Gdzie co jest (Notion; ID i pola: `budowa/references/notion-mapa.md`)

| Co | Baza | Klucz |
|---|---|---|
| Kroki budowy w czasie | **Harmonogram** `collection://d7a479ab-1e23-453f-8f59-55f4097f7d04` | Krok, Nr etapu (= arkusz kosztorysu, Etapy), Termin (od–do), Kto, Status, Pewność terminu, Bez odwrotu, Zależy od / Blokuje |
| Moje zadania i cudze terminy | **TASKS** `collection://2a9f5982-09e7-81be-91e8-000b0e10a05e` (wspólna z pluginem `ja` – zawsze **Obszar = Dom**) | When, Status, **Kto**, Obszar, Harmonogram |
| Materiał do zamówienia | **🧱 Zakupy budowy** `collection://a9854c6c-43ec-4bc1-8ef0-273fb02261c7` | Zamówić do, Dostawa, Status, Krok |
| Umowa, w ramach której ekipa robi krok | **Umowy i gwarancje** `collection://60c06f30-7867-435d-8f2e-1e025a3daa5c` | Kroki |

Rzeczy bez daty (pytania, „pamiętać”) zostają w Notatniku – do TASKS trafia tylko to, co ma datę albo konkretny następny krok.

## A. Ułożenie harmonogramu („ułóż harmonogram stanu zero”, „ekipa wchodzi 3.11”)

1. Kroki z arkusza kosztorysu (Etapy: numer, nazwa; kto robi – umowa z ekipą albo zapytaj) i z planu etapu (`etap`, sekcja A). Nie dziel na drobne –
   krok = coś, co ma swój termin i odbiór (wykop, chudziak, płyta, ściany piwnicy, izolacje, zasypka, strop…).
2. Dla każdego kroku: Termin (od–do), Kto, Wykonawca, Zależy od, Bez odwrotu (betonowanie, zasypka, zakrycie instalacji),
   Pewność terminu (Szacunek / Uzgodnione ustnie / Potwierdzone na piśmie). Długości i przerwy technologiczne
   (dojrzewanie betonu, schnięcie) – `zakupy/references/wyprzedzenia.md`; nieznane → szacunek z oznaczeniem.
3. Pokaż plan jako tabelę (Nr | Krok | od–do | Kto | zależy od | bez odwrotu) i zapisz po „ok” jednym wywołaniem.
   Nowy krok → folder zdjęć `Dom/Zdjęcia/<Etap>/<Krok>` na Dysku (konektor; bez konektora – przy najbliższej sesji Claude
   Code) i jego link w polu „Zdjęcia” kroku. Zmiana nazwy kroku nie zmienia folderu (`dziennik/references/zdjecia-i-kopia.md`, 3).
4. Od razu pokaż **terminy pochodne** (sekcja B) – jako propozycję, bez zapisu do TASKS.

## B. Terminy pochodne (po każdym nowym lub przesuniętym kroku)

Dla kroku z datą wylicz i **pokaż jako propozycję** (w odpowiedzi, w przeglądzie dnia lub tygodnia, w raporcie) –
**bez zadań w TASKS**: inwestor sam dodaje zadania na bieżąco (decyzja z 2.11.2026). Zapisz coś dopiero na wyraźne
„dodaj to zadanie”.
- **Zamówienia:** materiał na krok (`zakupy`, sekcja A) → „Zamówić do” = start kroku minus wyprzedzenie
  (`zakupy/references/wyprzedzenia.md`) minus 2 dni zapasu; dostawa ≥ 1 dzień przed startem. Pole „Zamówić do”
  w 🧱 Zakupach budowy uzupełniaj tylko w wierszach, które już są (wiersze zakłada `zakupy`).
- **Bramka:** krok „Bez odwrotu” → dzień przed: „Bramka: <krok> – sprawdzić wg `etap` (B)”.
- **Ludzie:** kto musi być (`etap/references/formalnosci.md`, „kto musi być obecny”): kierownik przy odbiorze zbrojenia,
  geotechnik przy dnie wykopu → „umówić <kogo> na <data>” z wyprzedzeniem 3–7 dni.
- **Pogoda:** betonowanie, izolacje, tynki zewnętrzne – przy bramce „sprawdzić prognozę” (progi: `etap/references/pogoda.md`);
  wpisz w Uwagach kroku robotę z datą (np. „betonowanie 20.11”) – wieczorny przegląd ostrzeże w ten dzień i przez 7 dni
  pielęgnacji, gdy prognoza przekroczy próg.
- **Płatności:** transza po odbiorze kroku – przypomnienie dla `koszty` (sekcja D), bez kwot w Notion. Termin kroku
  przesuwa też miesiąc transzy i materiału w planie gotówki (`koszty`, D.4) – przy przesunięciu na inny miesiąc wspomnij o tym.
Zadanie, które inwestor dodał sam albo kazał dodać, podpinaj relacją do kroku – wtedy przesunięcie kroku je pokaże.

## C. Przesunięcie („płyta przesunięta o tydzień”, „ekipa spóźni się 3 dni”)

**Aktualizuj od razu, bez osobnej prośby** (HZ-14): gdy z rozmowy, wpisu z Dziennika albo innej procedury (dziennik,
notatka, zakupy, etap, oferta) wynika zmiana terminu, kolejności lub zakresu kroku (umówiona dostawa betonu, inny dzień
wykopu, krok bez uziomu, bez XPS) – w tej samej pracy zmień w Harmonogramie Termin, nazwę kroku (zakres), Status
(Przesunięte / Potwierdzone / W trakcie) i Pewność terminu, a w Uwagach **na początku** dopisz „<data>: <powód>. Było X–Y”
(starej treści nie usuwaj). Datę podaną przez inwestora zapisz jako „Uzgodnione ustnie” – także w przebiegu bez inwestora
(to fakt, nie decyzja). Kroki zależne przelicz wg 2 jako „Szacunek” (bez inwestora – tylko wg 4) i pokaż tabelę „było → jest”.
Na koniec każdej rozmowy o budowie sprawdź, czy Harmonogram zgadza się z tym, co w niej padło.

1. Zmień Termin kroku (Status „Przesunięte”, w Uwagach powód i data zmiany). „Przesunięte” trzyma tylko krok, którego
   termin zmieniłeś, do potwierdzenia nowego terminu z ekipą – wtedy „Potwierdzone”.
2. Przelicz kroki, które od niego zależą (relacja Blokuje): nowy Termin z Pewnością „Szacunek” (krok z terminem
   potwierdzonym przez innych lub „Bez odwrotu” – tylko propozycja w tabeli), i pokaż ich terminy pochodne (propozycja,
   sekcja B); ich Status zostaje bez zmian.
3. Pokaż zestawienie „było → jest” i co trzeba **odwołać lub przesunąć u innych** (dostawa, kierownik, pompa) – to są
   istniejące zadania i zamówienia powiązane z krokiem – ich nowe terminy zapisz po „ok”; nowych zadań nie zakładaj.
4. **Wpis z budowy o tempie prac** („nie skończyliśmy, jutro kontynuujemy”, „przez deszcz nie robili”, „skończyli dzień
   wcześniej”) to fakt od inwestora, nie decyzja – także w przebiegu bez inwestora: przedłuż albo skróć koniec Terminu
   kroku (Status „W trakcie”), a kroki zależne (Blokuje) przesuń tylko tyle, żeby zaczynały się najwcześniej dzień po
   nowym końcu poprzednika (krok z zapasem zostaje); w Uwagach „+N dni – wpis z <data>”. Terminów u innych (dostawa,
   pompa, kierownik, geotechnik) i kroków „Bez odwrotu” nie zmieniaj sam: w rozmowie – pytanie z propozycją; bez
   inwestora – okienko pod wpisem, gdy termin wypada w ciągu 3 dni, inaczej linia w przeglądzie dnia budowy. Nie wiadomo,
   którego kroku dotyczy, albo o ile → pytanie.

## D. Czekam na („geodeta tyczy w czwartek”, „ekipa ma przysłać wycenę do 15.10”)

- Cudzy termin → TASKS: Name „<kto> – <co>”, **Kto** = ta osoba/rola, Status „WAITING”, Obszar = Dom, When = termin, Desc = skąd wiadomo
  (rozmowa, data). Gdy dotyczy kroku – relacja Harmonogram.
- Mój termin wobec kogoś („do piątku dam znać X”) → TASKS: Kto = Ja, Status „TO DO”, Obszar = Dom, When = termin.
- Po terminie: „czekam na” bez zmiany statusu → w przeglądzie (i w „co mnie czeka”) jako „przypomnij się <komu>”.
- „Zrobione / przyszło” → DONE; jeśli wynikło z tego ustalenie – `notatka`, wiedza – `wiedza`.

## E. „Co mnie czeka” (domyślnie 14 dni)

Jedno zestawienie, chronologicznie: kroki harmonogramu (start/koniec), moje zadania, czekam na (z terminem i po terminie),
zamówienia z „Zamówić do” (bez Dostarczone i Nieaktualne – jak przegląd dnia budowy) i dostawy, bramki. Na górze: po terminie i dzisiaj/jutro. Na dole: licznik spraw dalej niż 14 dni.

## Zasady

- Daty względne licz od daty podanej w rozmowie/wpisie (Dziennik: `@today`); brak daty przy terminie → zapytaj.
- Terminów innych osób nie zmieniaj „na domysł” – tylko z ich informacji (inwestor relacjonuje) i z Pewnością terminu.
- Kwoty nigdy w Harmonogramie ani Zakupach budowy – arkusz kosztorysu (`koszty`).
- Zadanie z relacją do kroku i sam krok rozjeżdżają się przy ręcznych zmianach (zadanie DONE, krok nie; krok „Zrobione”, zadanie
  otwarte; zadanie po końcu kroku; „czekam na” ze starym terminem po przesunięciu). Rozjazdy wychwytuje kontrola spójności
  (`ja/skills/przeglad-dnia/references/kontrola-spojnosci.md`) – pytaniem w „❓”; relację do kroku ustawiaj więc zawsze, gdy zadanie z niego wynika.
- Termin w Notatniku (pole Kiedy) i zadanie w TASKS dla tej samej sprawy → zadanie w TASKS, w Notatniku link; nie dubluj dat.
  Otwarte wpisy Notatnika z Kiedy (w oknie albo po terminie) wchodzą do „co mnie czeka” (E), jak w przeglądzie tygodnia (pkt 4).
