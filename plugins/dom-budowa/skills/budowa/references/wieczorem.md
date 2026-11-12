# Wieczorem – przegląd dnia budowy (`budowa`, sekcja „Wieczorem”)

`przeglad-dnia` (plugin `ja`) wywołuje tę sekcję wieczorem; ręcznie: „przegląd dnia budowy” (osobno od spraw osobistych).

1. **Dziś** (odczyt): wpisy o budowie przetworzone dziś (blok dnia w „Przetworzone” w Dzienniku + wieczorem wpisy budowy
   z kroku 1 przebiegu – `przeglad-dnia` B.9), Dziennik budowy z dzisiejszą
   datą, Notatnik i TASKS (Obszar Dom/puste) zamknięte lub dodane dziś, nowe decyzje czekające na inwestora (❓ o budowie, SP),
   błędy kolejki 💸 zgłoszone we „Wpisach” (`koszty` E) – licznik, bez powtarzania pytań. **Najpierw domknij decyzje wpisane** w Rejestrze (widok
   „🤖 Decyzja wpisana – do domknięcia”) wg `wiedza/references/sprzecznosci.md`, „Bez inwestora” – jedyny zapis tego kroku. Z konektorem Dysku: „zdjęcia: w `_nowe` czeka n” (bez rozkładania – `dziennik/references/zdjecia-i-kopia.md`, 6).
2. **Jutro** (odczyt): kroki Harmonogramu startujące jutro (krok „bez odwrotu” → przypomnij bramkę wg `etap`, bez zadania), dostawy
   jutro, 🧱 Zakupy budowy z „Zamówić do” = jutro lub po terminie (bez Dostarczone i Nieaktualne) albo w oknie przypomnienia wg Rodzaju
   (`zakupy`, „Przypomnienie”), TASKS Dom z When = jutro, WAITING z terminem jutro lub po, otwarte wpisy
   Notatnika z Kiedy = jutro lub po terminie; **ostrzeżenie pogodowe** tylko w dniu roboty wrażliwej wpisanej z datą w Uwagach kroku
   i przez 7 dni pielęgnacji betonu po niej, gdy próg przekroczony – Uwagi kroków z Terminem od jutra − 7 dni do jutra, także
   „Zrobione” (`etap/references/pogoda.md`, „Odczyt”); codziennej prognozy nie ma.
3. **Wpis w „📆 Przeglądy dzienne – budowa”** (`3f8f5982-09e7-815e-8b03-eacaa74db190`, strona na DOM) – gdy dziś albo jutro coś jest
   (albo rozkminka): zwijany nagłówek h2 „Przegląd dnia budowy – <dzień tygodnia> <data>” na górze, zapis i układ wg `przeglad-dnia/references/uklad-wpisu.md`
   (plugin `ja`): ⚠ Na teraz · Jutro – plan (z linią „⚠️ Pogoda jutro” tylko przy przekroczonym progu) · Dziś · Decyzje i pytania (SP domknięte dziś) · 🧠 Rozkminka (tylko z `przeglad-dnia`, B.2a; ręcznie –
   ślady `→ 🧠 rozkminka wieczorem` o budowie) · linia o nieudanych odczytach. Ręczny przebieg – osobny wpis z dopiskiem „(ręczne)”.
4. **Zwróć** do przeglądu dnia: link do wpisu, jedną linię skrótu („3 sprawy dziś, SP: 1 domknięte, jutro: geodeta 8:00”)
   i max 1 punkt jutra (ostrzeżenie pogodowe ma pierwszeństwo). Nic nie ma → „bez zmian”, bez wpisu.
