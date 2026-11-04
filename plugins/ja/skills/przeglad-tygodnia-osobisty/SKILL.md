---
name: przeglad-tygodnia-osobisty
description: Cotygodniowy przegląd spraw osobistych (zadania prywatne, dziecko, praca, emocje i produktywność w liczbach, wesele, suplementy) i porządki w Dzienniku, z odnośnikiem do osobnego przeglądu tygodnia budowy; uruchamia też przegląd budowy (skill przeglad-tygodnia z pluginu dom-budowa). Używaj, gdy uruchamia go zaplanowane zadanie tygodniowe albo użytkownik mówi „przegląd tygodnia”, „podsumuj tydzień”, „jak minął tydzień”, „co mnie czeka w tym tygodniu” (sprawy prywatne), „posprzątaj dziennik”.
---

# Przegląd tygodnia – sprawy osobiste

Cel: raz w tygodniu inwestor widzi w 2 minuty, co się działo poza budową, co zaległo i co go czeka – osobno od budowy,
żeby intensywny tydzień na budowie nie zasłaniał reszty. Budowa ma własny przegląd (`przeglad-tygodnia`, plugin
dom-budowa) na stronie DOM; tu jest do niego jedna linia z odnośnikiem.

Strona wyniku: **„📅 Przeglądy tygodniowe”** pod Dziennikiem (`3faf5982-09e7-81e3-a6af-e3786ca4a074`).
Zaplanowane zadanie: raz w tygodniu (np. niedziela wieczór), **poza projektem**, polecenie: „Przegląd tygodnia (skill
przeglad-tygodnia-osobisty z pluginu ja)”. Ręcznie: „przegląd tygodnia”.

## Zasady

- Odczyt **tylko przez zapisane widoki i strony** (`ja`, zasada 3 – limit zapytań rows/SQL): widoki „🤖 …” niżej.
- Najtańsze źródło to **7 ostatnich wpisów w „📆 Przeglądy dzienne”** (jedna strona) – zacznij od nich; widoki tylko
  na to, czego tam nie ma.
- Treść emocji i notatek o dziecku zostaje w Notion. Na stronie przeglądu (prywatnej): liczby, średnie i powtarzające się
  wzorce w kilku słowach. W odpowiedzi/logu zadania: same liczby i link.
- Niczego nie rozstrzygaj. Porządki (sekcja D) – w zaplanowanym przebiegu tylko te oznaczone jako „bez pytania”;
  resztę proponuj w przeglądzie.

## Kroki

1. **Budowa** – wczytaj skill `przeglad-tygodnia` (plugin dom-budowa) i wykonaj go; zapisze przegląd budowy na DOM
   („Przeglądy tygodniowe”). Weź link do wpisu i jedną linię skrótu (do decyzji n, terminy 7 dni n).
2. **Tydzień – sprawy osobiste** (odczyt):
   - „📆 Przeglądy dzienne” – wpisy z 7 dni (co się działo, co zamknięto);
   - TASKS widok „🤖 Tydzień – prywatne” (`view://3faf5982-09e7-81b5-ad0a-000c1cfabfa0`): zamknięte w tygodniu, po terminie,
     z terminem w 7 dni (osobno Prywatne / Dziecko / Praca); SOMEDAY tylko licznikiem;
   - Wpisy emocji widok „🤖 Ostatni tydzień” (`view://3faf5982-09e7-81ec-83af-000c8b518d37`): liczba wpisów, najczęstsze
     emocje, średnia intensywność, powtarzające się triggery i potrzeby (kilka słów, bez cytatów);
   - Dziennik produktywności widok „🤖 Ostatni tydzień” (`view://3faf5982-09e7-81af-9ea1-000cbe3dd643`): dni zapisane,
     średnia ocena, najczęstsze przeszkadzajki;
   - strona dziecka: nowe punkty w „💬 Do przegadania” i „🎁 Prezenty” z tygodnia (licznik + tytuły tematów);
   - strona „💍 Wesele”: nowe punkty i zadania „Wesele:” z terminem w 30 dni;
   - Suple: Buy = tak (licznik, nazwy);
   - Zakupy: 🛒 Zakupy „Do kupienia” (licznik, najstarsze) i z Terminem w 7 dni (wymień).
3. **Dziennik i harness** (odczyt): wpisy z okienkiem ❓ we „Wpisach” i pozycje „❓” Dziennika starsze niż 7 dni bez odpowiedzi (wymień wpis i pytanie – sprawy budowy
   tylko licznikiem, są w przeglądzie budowy); skrzynka „Zmiany do harnessu” – wpisy do wdrożenia starsze niż 7 dni
   (przypomnienie: uruchom Claude Code); „Pomysły na rozwój” – nowe bez analizy i „Pytania do mnie”.
4. **Wpis w „📅 Przeglądy tygodniowe”** na górze strony, zwijany nagłówek „Tydzień <RRRR-Www> (<data od–do>)”:
   ```
   **Zrobione:** 3–6 punktów (prywatne / dziecko / praca)
   **Zaległe i po terminie:** zadanie – od kiedy → zamknąć, przesunąć czy odpuścić?
   **Najbliższy tydzień:** zadania z terminem wg dni, wesele (30 dni), „kupić: n suplementów, n pozycji z zakupów (z terminem: …)”
   **Emocje i praca (liczby):** n wpisów emocji, najczęściej: …, śr. intensywność x; praca: n dni, śr. ocena y; wzorzec: …
   **Dziecko:** n nowych tematów do przegadania, n pomysłów na prezent
   **Czeka na Ciebie:** n pytań pod wpisami i w ❓ (najstarsze: …), HZ-x do wdrożenia, POM-x z pytaniami
   **🏗 Budowa:** <linia skrótu> → <wzmianka przeglądu budowy z tego tygodnia>
   **Porządki (n):** propozycje z sekcji D – do zatwierdzenia jednym „tak”
   ```
   Pusty tydzień → krótki wpis „spokojny tydzień” z linią budowy. Ręczny przebieg – osobny wpis z dopiskiem „(ręczne)”.
5. **Porządki** (sekcja D) i **odpowiedź** (log): link do wpisu + liczby; bez treści emocji.

## D. Porządki w Dzienniku

Bez pytania (także w zaplanowanym przebiegu – to tylko ślad, linki są w docelowych miejscach):
- bloki dni w „Przetworzone” w Dzienniku starsze niż 14 dni → **przenieś** (nie usuwaj) na podstronę Dziennika
  „🗃 Przetworzone – archiwum” (ID w `ja/references/notion-mapa.md`): najpierw wklej te same zwijane bloki na górę archiwum
  (najnowszy dzień na górze), sprawdź, że są, dopiero potem zdejmij je z Dziennika (jedna edycja każdej strony);
- podstrony w „🗃 Przetworzone podstrony” zostają – nie ruszaj.
Do zatwierdzenia (propozycja w przeglądzie):
- wpisy z okienkiem ❓ i pozycje „❓” bez odpowiedzi od 14 dni → zamknąć jako „pominięte”, przeformułować pytanie czy zostawić;
- obszar z bazy Obszary, do którego nic nie trafiło od 60 dni → wyłączyć (Aktywny = nie)?;
- wpisy pomijane wielokrotnie z tym samym typem treści → propozycja nowego wiersza w Obszarach;
- TASKS prywatne po terminie od 14 dni → zamknąć / przesunąć / SOMEDAY (pytanie zbiorcze).
Po „tak” wykonaj wsadowo (`ja`, zasada 2). Niczego innego nie usuwaj. Archiwum tylko do wglądu – nie zapisuj tam nic nowego.
