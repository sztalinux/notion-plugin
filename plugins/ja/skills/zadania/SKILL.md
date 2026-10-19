---
name: zadania
description: Zadania inwestora poza budową (prywatne, dziecko, praca) we wspólnej bazie TASKS w Notion oraz lista zakupów (baza 🛒 Zakupy) – nowe zadanie z terminem albo „kiedyś”, nowa rzecz do kupienia, zmiana statusu po wpisie „zrobiłem X”, „kupiłem X”, „zacząłem”, „czekam na”, „odpuszczam”, odczyt „co mam dziś / jutro / w tym tygodniu”, „co kupić”. Używaj, gdy użytkownik mówi „muszę…”, „trzeba…”, „przypomnij mi…”, „kupić…”, „umówić…”, „zrobiłem…”, „zrobione”, „kupiłem…”, „co mam jutro”, wkleja link do rzeczy do kupienia, albo gdy wpis z Dziennika ma obszar Zadanie, Status zadania lub Zakup. Zadania budowy prowadzą procedury notatka i harmonogram (plugin dom-budowa).
---

# Zadania (wszystkie obszary poza budową)

Jedna baza **TASKS** (`collection://2a9f5982-09e7-81be-91e8-000b0e10a05e`) dla domu i spraw prywatnych; obszar rozróżnia
pole **Obszar** (Dom / Prywatne / Dziecko / Praca; puste = Dom – stare wiersze). Zadania budowy i domu (Obszar = Dom)
tworzą procedury `notatka` i `harmonogram` z pluginu `dom-budowa` – tu ich nie dubluj; zmianę statusu („zrobiłem”) obsługujesz
dla wszystkich obszarów. Rzeczy do kupienia (poza suplementami – `suple` – i materiałami budowy – `zakupy` z `dom-budowa`)
idą do osobnej bazy **🛒 Zakupy** (sekcja „Zakupy” niżej), nie do TASKS.

## A. Nowe zadanie

Najpierw ustal, czy to w ogóle zadanie. Nie zakładaj go w TASKS (także jako SOMEDAY), gdy wpis to – również w formie
„muszę przeczytać”, „trzeba obejrzeć”, „kupić X na prezent”:
- książka do przeczytania → Books, według obszaru „Książka do przeczytania” w bazie Obszary;
- film lub serial do obejrzenia → 🎬 Films, według obszaru „Film / serial do obejrzenia”;
- pomysł na prezent → strona dziecka „🎁 Prezenty” (`dziecko`) albo „💞 Relacja” → „🎁 Prezenty i niespodzianki”;
  prezent dla innej osoby → zapytaj, gdzie zapisać.
Zadanie załóż tylko przy terminie albo decyzji o zakupie („kupić prezent do 20.11”) – wtedy zadanie i pomysł na stronie osoby.
Bez tej kontroli takie wpisy lądowały w TASKS zamiast na listach i stronach osób.

1. Sprawdź duplikat: wyszukiwarka z parametrem bazy TASKS (1–2 słowa kluczowe), wśród niezakończonych.
   Jest → uzupełnij (termin, opis w treści), nie dubluj.
2. Pola:
   | Pole | Wartość |
   |---|---|
   | Name | krótko, bezokolicznik („Umówić stomatologa”) |
   | Obszar | Dziecko – gdy dotyczy dziecka; Praca – sprawy zawodowe; inaczej Prywatne. Budowa/działka/dom → nie tu, `budowa` |
   | When | termin z wpisu; „do piątku” licz od daty wpisu; brak terminu → puste |
   | PLANNED | z terminem lub „na dniach” → TO DO; „kiedyś” → SOMEDAY (zakup i link do produktu → baza Zakupy, nie zadanie) |
   | Priority | domyślnie Medium; „pilne”, „koniecznie” → High; drobiazg → Low |
   | Kategoria | Zakup (tylko zadanie dołożone do pozycji Zakupów, sekcja niżej) / Zdrowie / Nauka / Inne |
   | Kto | Ja; ktoś inny ma coś zrobić → jego rola opisowo w Desc, Kto = Inny, PLANNED WAITING |
   | Desc | jedno zdanie (skąd, po co); linki, listy, szczegóły – w treści strony |
3. Termin względny bez daty wpisu (np. „w piątek” w wpisie bez @today) → pytanie, nie zgaduj.

## Zakupy (baza 🛒 Zakupy)

Baza `collection://3747d532-a49b-44a4-b36f-b3196f917243` na stronie ✅ Zadania. Zapisuj według wiersza „Zakup” w bazie
Obszary (nadrzędny wobec poniższego opisu pól), **nie jako zadanie** – lista zakupów nie ma zaśmiecać TASKS.
1. Sprawdź duplikat (wyszukiwarka z parametrem bazy, 1–2 słowa, wśród „Do kupienia” i „Zamówione”); jest → uzupełnij.
2. Pola: Rzecz (krótko), Status (Do kupienia / Zamówione / Kupione / Odpuszczone), Gdzie (link we wpisie = Internet; inaczej
   Sklep albo Obojętnie), Sklep / serwis (gdy wynika z wpisu), Ilość, Termin (tylko gdy wpis go ma), Obszar, Link, Cena, Uwagi
   (jedno zdanie: po co, wariant, rozmiar; reszta w treści strony).
3. **Zadanie w TASKS dołóż tylko** przy terminie, „na już”, „pilnie”, „szybko” albo gdy skończyło się coś codziennego:
   Name „Kupić X”, Kategoria Zakup, Obszar jak w zakupie, relacja Zadanie w Zakupach.
4. „Kupiłem X” → Zakupy: Status Kupione + Kupione dnia; powiązane zadanie DONE (sekcja B). „Zamówiłem X” → Zamówione.
   „Odpuszczam X” → Odpuszczone (powiązane zadanie ARCHIVED).
5. Odczyt „co kupić”: widok „🛒 Do kupienia” (grupy wg Gdzie), „📦 Zamówione – czekam”, „✅ Kupione” (ID w `ja/references/notion-mapa.md`).
   Zakup z Termin lub pilny wymień osobno na górze.

## B. Status istniejącego zadania

| Inwestor pisze | PLANNED |
|---|---|
| „zrobiłem X”, „X zrobione”, „załatwione” | DONE |
| „zacząłem”, „w toku”, „robię” | IN PROGRESS |
| „czekam na … (od kogo)” | WAITING (+ kto w Desc albo Kto) |
| „przesuwam na …”, „w przyszłym tygodniu” | zostaje, When = nowy termin |
| „odpuszczam”, „nieaktualne” | ARCHIVED |

1. Szukaj we **wszystkich obszarach** wśród niezakończonych (wyszukiwarka z parametrem bazy TASKS – słowa z wpisu, potem porównanie treści i statusu).
   Brak trafienia → sprawdź jeszcze zadania zamknięte (DONE, ARCHIVED) z ostatnią edycją w ostatnich 7 dniach: inwestor zamyka
   zadania także ręcznie w Notion, więc wpis „zrobiłem X” bywa spóźniony. Jest takie → nic nie zmieniaj, w śladzie
   „→ już zamknięte (ręcznie)” z odnośnikiem.
2. Jedno trafienie → zmień status; w treści strony dopisz linię „<data>: <co się stało> (z Dziennika)”. Zadanie budowy
   (Obszar Dom/puste) z powiązanym krokiem Harmonogramu → status kroku zostaw procedurze `harmonogram` (przekaż jej sprawę).
3. Brak trafienia także wśród świeżo zamkniętych → Dziennik „❓”: „Nie znalazłem zadania »…« – utworzyć jako zrobione (ślad) czy pominąć?”.
4. Kilka trafień → „❓” z listą (nazwa, termin) do wyboru.

## C. Odczyt

Strona ✅ Zadania ma zakładki: 📅 Dziś i tydzień (wszystkie obszary; widoki „📅 Dziś” – po terminie i na dziś, „🗓 Tydzień (7 dni)”),
🛒 Zakupy, 🏠 Prywatne (z pracą), 🏗 Budowa, 👪 Dziecko. „Co mam dziś / w tym tygodniu” → widoki „📅 Dziś” i „🗓 Tydzień (7 dni)”;
jutro → „📅 Jutro – wszystko”; sprawy jednego obszaru → widok jego zakładki (ID: `ja/references/notion-mapa.md`).
Pokaż w tabeli: zadanie | obszar | termin | status; zadania po terminie osobno na górze. SOMEDAY pokazuj tylko licznikiem,
chyba że pyta o nie wprost.

## D. Luki w kolumnach (wieczorny przegląd dnia)

Inwestor dodaje i edytuje zadania ręcznie w Notion, często bez pól – np. z widoku „📅 Dziś”, który nie ustawia Obszaru.
Puste Obszar znaczy w starych wierszach Dom, więc zadanie prywatne z pustym Obszarem trafiłoby do przeglądu budowy.
`przeglad-dnia` (krok 5) uzupełnia luki w wierszach zmienionych tego dnia, bez pytań w rozmowie:

| Pole (puste) | Uzupełnij |
|---|---|
| Obszar | **Dom** – gdy Kategoria jest budowlana (Media, Kredyt, Czyszczenie działki, Stan zero, SSO, Ogrodzenie, Teren, Przygotowanie do budowy, Wiata kontener, Projektowanie, Zakup działki, Ogród) albo wypełniona jest relacja Harmonogram lub Dziennik budowy. **Prywatne** – Kategoria Zdrowie lub Nauka. Inaczej z nazwy i opisu, tylko gdy jednoznaczne (dziecko, praca, zwykła sprawa prywatna); wątpliwość → „❓” |
| Kto | Ja – chyba że Status WAITING albo nazwa lub opis wskazuje kogoś innego (wtedy „❓”) |
| Priority | Medium |
| Kategoria | Obszar inny niż Dom: z nazwy (Zakup, Zdrowie, Nauka), niejasne → Inne. Obszar Dom zostaw (kategorię nadają `notatka` i `harmonogram`) |
| Desc | jedno zdanie z treści strony, gdy ją ma; pusta strona → zostaw puste |

Status (kolumna statusu; w starszych opisach „PLANNED”), When i Name zostają – to decyzje inwestora. Termin wynikający z nazwy
lub opisu („do piątku”, data) → „❓” z proponowaną datą. Wpisanych wartości nie nadpisuj.

## Zasady

- Porządek statusami, nie usuwaniem; zamykając, dopisz jednym zdaniem, jak się skończyło.
- Nie zakładaj zadań z rzeczy, które są tylko informacją albo emocją – to inne obszary.
- Zakup dla dziecka → Obszar Dziecko, Kategoria Zakup; pomysł na prezent bez terminu i decyzji o zakupie → strona osoby (sekcja A).
- Temat do przegadania z dzieckiem lub partnerką → strona osoby, zadanie tylko po świeżym zdarzeniu (`ja`, zasada 9).
