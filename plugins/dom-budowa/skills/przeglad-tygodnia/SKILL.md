---
name: przeglad-tygodnia
description: Cotygodniowy przegląd budowy (osobno od spraw osobistych – te ma przeglad-tygodnia-osobisty z pluginu ja) i porządki w Notion budowy – co nowego doszło do wiedzy, otwarte sprzeczności czekające na decyzję, pytania do projektantów, zadania i terminy na najbliższe dni, informacje do ponownej weryfikacji. Używaj, gdy uruchamia go zaplanowane zadanie lub użytkownik pyta „co nowego”, „podsumuj tydzień”, „co czeka na mnie”, „przegląd”.
---

# Przegląd tygodnia

Cel: w 2 minuty inwestor wie, co doszło, co czeka na jego decyzję i co trzeba zrobić w tym tygodniu.
Przegląd czyta i podsumowuje – niczego nie rozstrzyga. Statusy zmienia tylko w ramach porządków zatwierdzonych
przez inwestora (sekcja „Porządki”). Kolejność i pierwszy plan wg zasady 12 w procedurze `budowa`:
najpierw bieżący etap i pilne terminy, sprawy zamknięte i odległe tylko licznikiem.

## Dane (ID: `budowa/references/zrodla.md`, `wiedza/references/notion-wiedza.md`)

Pobierz w jak najmniejszej liczbie zapytań:
1. **Rozmowy i źródła** dodane w ostatnich 7 dniach.
2. **Informacje**: Status „Nowe” (wszystkie) – pogrupuj po Tematach; pokazuj Kluczowe i Ważne, Ciekawostki tylko liczbą.
   Osobno: Informacje z „Moim komentarzem” zmienionym w 7 dniach – sprzeciw/wątpliwość → propozycja działania (`wiedza`, sekcja H).
2a. **Wiedza na teraz** – nie tylko nowa, ale bez powtórek z tygodnia na tydzień. Pula: Etap = bieżący etap albo „Cała
   budowa”, Status ≠ Nieaktualne, Dotyczy nas ≠ Nie, Istotność ≠ Ciekawostka (widok „🎯 Na teraz”).
   **Pod koniec etapu dołącz następny**: gdy pierwszy krok następnego etapu startuje w Harmonogramie za ≤ 8 tygodni (bez
   harmonogramu – gdy bieżący etap jest w końcówce wg strony DOM), do puli wchodzi następny etap – najpierw to, co trzeba
   zamówić, zdecydować albo przewidzieć z wyprzedzeniem (okna, dach, instalacje). Wtedy zmień też widok „🎯 Na teraz”
   (nazwa „… – <etap> + <następny>”, filtr Etap o następny) – to nie decyzja, wolno w zaplanowanym przeglądzie.
   Wybierz **max 6**:
   - najpierw **przed krokiem** – informacje pasujące (Tematy/Branża) do kroków Harmonogramu startujących w 14 dni i do
     otwartych decyzji z Notatnika; w tygodniu tuż przed krokiem (start ≤ 7 dni) mogą wrócić jako przypomnienie,
     jeśli Pokazano jest starsze niż 7 dni;
   - potem **jeszcze niepokazane** (Pokazano puste): Kluczowe → Ważne → bez oceny, nowsze pierwsze.
   Po przeglądzie ustaw im Pokazano = dzisiejsza data (to nie decyzja – wolno też w zaplanowanym przeglądzie).
   Reszta tylko licznikiem: „na ten etap jeszcze n niepokazanych” i „na później: SSO n, Deweloperski n, …”.
3. **Rejestr sprzeczności**: Status „Czeka na decyzję” i „Do sprawdzenia u projektanta” (z datą zgłoszenia – najstarsze pierwsze).
4. **Notatnik budowy**: Status „Otwarte” lub „Do omówienia” z Priorytetem Krytyczne/Ważne; wpisy z „Kiedy” w ciągu 14 dni lub po terminie.
5. **TASKS** (Obszar Dom albo puste – sprawy prywatne nie wchodzą do przeglądu budowy): niezakończone z „When” w ciągu 7 dni lub po terminie; osobno **czekam na** (Status „WAITING”, Kto ≠ Ja) – po terminie = „przypomnij się”.
5a. **Harmonogram** (`collection://d7a479ab-1e23-453f-8f59-55f4097f7d04`): kroki startujące / kończące się w 14 dni, kroki po terminie
    bez statusu „Zrobione”, kroki „Bez odwrotu” w 14 dni (czy jest zadanie bramki), terminy „Szacunek” na najbliższe 14 dni
    (do potwierdzenia u wykonawcy).
5b. **Zamówienia i dostawy**: „Zamówić do” w 14 dni lub po terminie bez statusu „Zamówione”; dostawy w 7 dni.
5c. **Umowy i gwarancje**: Gwarancja do / Rękojmia do w ciągu 60 dni (przegląd przed upływem, zgłoszenie usterek).
6. **Informacje**: „Wrażliwe na czas” z Datą informacji starszą niż 12 miesięcy, jeśli dotyczą bieżącego etapu.
7. **Harness i pomysły** – nie tutaj: skrzynkę zmian i „Pomysły na rozwój” raportuje przegląd osobisty
   (`przeglad-tygodnia-osobisty`, plugin `ja`).
8. **Dziennik budowy** (ID: `dziennik/references/notion-dziennik.md`): wpisy z 7 dni – dni pracy ekipy
   i własne, otwarte problemy, kroki zakryte bez zdjęć („Przed zakryciem OK” odznaczone).
9. **Dziennik – sprawy budowy:** wpisy o budowie w „❓ Czeka na Twoją odpowiedź” na stronie „📓 Dziennik”
   (`3f8f5982-09e7-80c8-a154-c59aeb844e8f`) bez odpowiedzi – wymień wpis i pytanie. Pozostałe wpisy, porządki w Dzienniku
   i jego „Przetworzone” – przegląd osobisty (`przeglad-tygodnia-osobisty`, plugin `ja`).
10. **Spójność** (inwestor edytuje Notion ręcznie – wychwyć rozjazdy, nie naprawiaj bez zgody):
    - Notatnik „Ustalone”/„Zrobione” z wiedzą techniczną bez relacji „Wiedza” → kandydaci do `wiedza`, sekcja F;
    - Informacje bez Tematów albo bez Źródeł i bez Notatnika; Tematy, których „W skrócie” przeczy nowszym Informacjom
      lub decyzjom; Informacje „Sporne” bez wpisu w Rejestrze;
    - sprawy blokujące bieżący etap bez Priorytetu „Krytyczne” (np. termin przed startem etapu, a Priorytet „Ważne”) –
      nie widać ich w „🔴 Do zamknięcia” na DOM;
    - Dziennik: problemy bez wpisu w Notatniku/TASKS; TASKS „DONE”, a powiązany wpis Notatnika otwarty;
    - indeks wiedzy (`wiedza/references/indeks.md`): `python3 tools/wiedza.py stan --json` i `python3 tools/wiedza.py duplikaty --od <data sprzed 7 dni> --json`
      → lista kandydatów na duplikaty do DECYZJI inwestora (nie scalaj bez zgody); `zbudowano` starsze niż 7 dni albo `ostatni_pelny`
      starszy niż 14 dni → zaproponuj ręczny `sync --pelny`; `liczniki.informacje` porównaj z liczbą Informacji w Notion, gdy jest znana
      (duża rozbieżność → `sync --pelny`); `kopia_aktualna` = false → zaproponuj `publikuj --teraz`. Na claude.ai nie ma `tools/`:
      użyj kanału czatu z `indeks.md` (daty kopii tylko informacyjnie); bez dostępu napisz „indeks niedostępny” i czytaj Notion.
    - jakość wyszukiwania: w Claude Code `python3 tools/wiedza_jakosc.py raport` → alarmy i zapytania bez wyników do decyzji
      inwestora (`indeks-jakosc.md`); na claude.ai napisz, że raport jakości jest dostępny tylko w Claude Code.
11. **Zamówienia z wyprzedzeniem**: pozycje na najbliższe dwa etapy, których termin zamówienia (`zakupy/references/wyprzedzenia.md`)
   wypada w ciągu 14 dni; **płatności** – Wydatki „Planowane” z datą w 14 dni i transze po odbiorach, jeśli Excel jest
   dostępny w tym miejscu (inaczej napisz, że to wymaga aktualnego pliku).

## Wynik

```
## Przegląd budowy – tydzień <RRRR-Www> (<data>)
**Do decyzji (n):** SP-x <dylemat> – od <n> dni … (najstarsze/krytyczne pierwsze)
**Nowa wiedza (n z m źródeł; k kluczowych, c ciekawostek):** <Temat>: 1–2 najważniejsze punkty z WI-x; … (max 8 punktów)
**Twoje komentarze do wiedzy:** WI-x – <komentarz> → proponuję: …
**Wiedza na teraz (<etap>):** • WI-x <informacja w jednym zdaniu> – dlaczego teraz (krok / decyzja) … (max 6)
  Na ten etap jeszcze n niepokazanych (widok „🎯 Na teraz”) · na później: SSO n, Deweloperski n, Wykończenie n
**Dotyczy naszej budowy:** • …
**Pytania do projektantów (n):** Konstruktor: …; Architekt: …
**Harmonogram 14 dni:** <krok – od–do – kto>; **Bez odwrotu:** <krok – data – bramka gotowa?>
**Terminy 7 dni:** <zadanie – data>; **Po terminie:** …
**Czekam na:** <kto – co – termin> (po terminie: przypomnij się)
**Gwarancje (60 dni):** <umowa – do kiedy>
**Budowa w tym tygodniu:** dni ekipy / własne, problemy otwarte, braki zdjęć przed zakryciem
**Zamówić / zapłacić do 14 dni:** <pozycja – do kiedy – skąd>
**Do ponownej weryfikacji:** WI-x <cena/przepis z roku …>
**Dziennik – budowa:** m wpisów o budowie czeka na Twoją odpowiedź: <wpis> – <pytanie>
**Sugestia na ten tydzień:** 1–3 konkretne kroki.
**Na później (n):** licznik spraw z dalszych etapów – bez listy.
**Porządki (n):** propozycje z sekcji „Porządki” – do zatwierdzenia jednym „tak”.
```

## Porządki (raz w tygodniu, max 10 pozycji)

Znajdź i zaproponuj – nie wykonuj bez zgody; po „tak” wykonaj wsadowo (zasada 6):
- duplikaty w Notatniku i TASKS (to samo zagadnienie dwa razy) → scal w starszy wpis; kandydatów na duplikaty
  Informacji bierz z listy `duplikaty --od` (punkt „Spójność”);
- wpisy bez Etapu lub Priorytetu → uzupełnij;
- sprawy po terminie albo bez zmian od 30 dni → zamknąć, przesunąć termin czy zostawić (pytanie zbiorcze);
- Informacje „Nowe” starsze niż 30 dni → „Przejrzane” albo „Nieaktualne”;
- otwarte sprawy zakończonego etapu → przenieść do bieżącego albo zamknąć;
- rozjazdy z punktu „Spójność” → dopisać relację Wiedza / Informację (`wiedza`, F), uzgodnić statusy, poprawić „W skrócie”.
Niczego nie usuwaj – porządek tylko statusami i scalaniem (z dopiskiem, co scalono).

Zapis: dopisz przegląd na górze strony Notion „Przeglądy tygodniowe” (pod DOM, `3f4f5982-09e7-8144-af5e-f9521a52ea9d`)
jako zwijany nagłówek z tytułem tygodnia – **jedno wywołanie**. W rozmowie podaj ten sam tekst. Gdy wywołał cię przegląd
osobisty (`przeglad-tygodnia-osobisty`), zwróć mu wzmiankę do wpisu i jedną linię skrótu (do decyzji n, terminy 7 dni n).
Pusty tydzień (brak nowych rzeczy i terminów) → krótka informacja „bez zmian”, bez zapisu do Notion.
