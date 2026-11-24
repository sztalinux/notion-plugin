# Wieczorem – przegląd dnia budowy (`budowa`, sekcja „Wieczorem”)

`przeglad-dnia` (plugin `ja`) wywołuje tę sekcję wieczorem; ręcznie: „przegląd dnia budowy” (osobno od spraw osobistych).

1. **Dziś** (odczyt): wpisy o budowie przetworzone dziś (blok dnia w „Przetworzone” w Dzienniku + wieczorem wpisy budowy
   z kroku 1 przebiegu – `przeglad-dnia` B.9), Dziennik budowy z dzisiejszą
   datą, Notatnik i TASKS (Obszar Dom/puste) zamknięte lub dodane dziś, nowe decyzje czekające na inwestora (❓ o budowie, SP),
   błędy kolejki 💸 zgłoszone we „Wpisach” (`koszty` E) – licznik, bez powtarzania pytań. **Najpierw domknij decyzje wpisane** w Rejestrze (widok
   „🤖 Decyzja wpisana – do domknięcia”) wg `wiedza/references/sprzecznosci.md`, „Bez inwestora” – jedyny zapis tego kroku. Z konektorem Dysku: „zdjęcia: w `_nowe` czeka n” (bez rozkładania – `dziennik/references/zdjecia-i-kopia.md`, 6).
2. **Jutro i najbliższe 7 dni** (odczyt; „jutro” = dzień planu, `przeglad-dnia` B.8): widok Harmonogramu „🤖 Najbliższe 7 dni
   (plan dnia)” (ID w mapie – jeden mały odczyt; „📅 Oś czasu” tylko do ostrzeżenia pogodowego niżej) – kroki z Terminem w 7 dni i zaległe, kroki startujące jutro (krok „bez odwrotu” → przypomnij bramkę wg `etap`, bez zadania), dostawy
   jutro i „dostawa po terminie” (🧱 z Dostawą przed dniem planu, Status nadal „Zamówione” / „Potwierdzone”), 🧱 Zakupy budowy z „Zamówić do” w oknie przypomnienia wg Rodzaju (`zakupy`, „Przypomnienie”) lub po terminie, Status przed
   zamówieniem (bez Zamówione, Potwierdzone, Dostarczone, Problem i Nieaktualne; pozycje „Problem” z tego samego odczytu – osobna
   wzmianka „z problemem: n”, nie jako do zamówienia), TASKS Dom z When = jutro i z Deadline ☑ po terminie (orientacyjne po dacie – sam licznik; `zadania`, plugin ja), WAITING z terminem jutro lub po, otwarte wpisy
   Notatnika z Kiedy = jutro lub po terminie; **ostrzeżenie pogodowe** tylko w dniu roboty wrażliwej wpisanej z datą w Uwagach kroku
   i przez 7 dni pielęgnacji betonu po niej, gdy próg przekroczony (progi i przebieg – `etap/references/pogoda.md`); codziennej
   prognozy nie ma. Odczyt do ostrzeżenia pogodowego: jeden odczyt widoku „📅 Oś czasu” (bez filtra, pokazuje Uwagi;
   „🤖 Najbliższe 7 dni” pomija kroki „Zrobione”) – kroki, których Termin zachodzi na okres od jutra − 7 dni do jutra,
   w każdym Statusie, z ich Uwagami; stron kroków nie otwieraj.
3. **Wpis w „📆 Przeglądy dzienne – budowa”** (`3f8f5982-09e7-815e-8b03-eacaa74db190`, strona na DOM) – gdy dziś albo jutro coś jest
   (albo rozkminka): zwijany nagłówek h2 „Przegląd dnia budowy – <dzień tygodnia> <data>” na górze, zapis i układ wg `przeglad-dnia/references/uklad-wpisu.md`
   (plugin `ja`): ⚠ Na teraz · Jutro – plan (z linią „⚠️ Pogoda jutro” tylko przy przekroczonym progu) · Dziś · Decyzje i pytania (SP domknięte dziś) · 🧠 Rozkminka (tylko z `przeglad-dnia`, B.2a; ręcznie –
   ślady `→ 🧠 rozkminka wieczorem` o budowie) · linia o nieudanych odczytach. Ręczny przebieg – osobny wpis z dopiskiem „(ręczne)”.
4. **Zwróć** do przeglądu dnia: link do wpisu, jedną linię skrótu („3 sprawy dziś, SP: 1 domknięte, jutro: geodeta 8:00”),
   max 1 punkt do ramki planu (krok bez odwrotu, bramka, ostrzeżenie pogodowe, zamówienie ⏰ na jutro – w tej kolejności) i punkty
   zakładki 🏗 (`przeglad-dnia/references/uklad-wpisu.md`, D), każdy jako wzmianka: **Dziś na budowie** (kroki, dostawy, ekipa jutro) ·
   **Najbliższe kroki** (7 dni, 🔒 bez odwrotu, pewność terminu) · **Do zamówienia** (⏰ te same pozycje co w kroku 2) ·
   **Decyzje i pytania** (SP czekające, z terminem, jeśli jest) – max 5 w każdej – oraz licznik „Po dacie orientacyjnej: n (najstarsze: <zadanie>)”
   dla zadań Dom bez Deadline z When przed dniem planu (jedna linia na końcu zakładki; zero = pomiń). Nic nie ma → „bez zmian”, bez wpisu.
