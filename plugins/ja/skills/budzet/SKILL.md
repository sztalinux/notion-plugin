---
name: budzet
description: Budżet domowy w arkuszu Google „Budżet domowy” – wydatki zapisywane na bieżąco z wpisów („200, pra, o, zam”, gotówka, wydatek na budowę także do budżetu) i miesięczne zamknięcie – wyciągi (mBank, ZEN), lista zakupów Allegro, listy wydatków drugiej osoby i gotówki, strona decyzji (artefakt), zapis do Transakcji, kontrola arkusza, przychód drugiej osoby z sald i podsumowanie miesiąca. Wpis wydatku działa też w przebiegu na Macu; zamknięcie tylko w Claude Code na Macu (skrypty tools/budzet). Używaj, gdy użytkownik mówi „zamknijmy miesiąc”, „budżet za październik”, „wrzuciłem wyciągi”, „przenieś decyzje budżetu RRRR-MM”, „podsumuj miesiąc w budżecie”, „czy przychody są dobrze policzone”, wkleja listę Allegro albo listę wydatków ze skrótami, albo wpisuje wydatek w skrócie „kwota, konto, osoba, kategoria, opis”.
---

# Budżet domowy – wydatki na bieżąco i zamknięcie miesiąca

Kod: `tools/budzet/` (wpis, importuj, przenies, kontrola, allegro, strona). **Dane są poza repo** w
`<folder budowy>/.dom/budzet/` (`DANE` w `tools/budzet/wspolne.py`): `ustawienia.json` (ID arkusza, adres strony, folder
Dysku, konta, osoby, skróty kont i osób, pary pomijane, reguły specjalne), `kategorie.json`, `reguly.json` (reguły sklepów,
skróty kategorii, sprzedawcy Allegro – źródło prawdy; zakładka „Reguły” w arkuszu to widok), `oczekujace.json` (zapowiedziane
zwroty), `wyciagi/`, `listy/` (listy i `RRRR-MM-wpisy.jsonl`), `miesiace/`. Nigdy nie kopiuj tych danych do repo.
Arkusz ma locale en_US: w formułach kropka (`=12.99+5.49`). Układ arkusza (zakładka roku, Konta, formuły, nowy rok):
`references/arkusz.md`.

## Co przygotowuje inwestor (lista do przypomnienia na koniec miesiąca)

1. Wyciągi CSV za miesiąc: mBank i ZEN → folder Dysku `dysk_folder` (mogą obejmować kilka miesięcy).
2. Allegro → „Moje zakupy” → zaznacz i skopiuj tekst → plik na Dysk.
3. Lista wydatków drugiej osoby (nagłówki kont, skróty) i lista gotówki – tylko to, czego nie było we wpisach (sekcja A).
4. Salda kont drugiej osoby **na koniec ostatniego dnia miesiąca** (historia w aplikacji banku) i stan gotówki → zakładka
   Konta, kolumna następnego miesiąca. Saldo odczytane później → podaj też operacje z dni po końcu miesiąca (sekcja D).

## A. Wydatek z wpisu w trakcie miesiąca

Wpis w Dzienniku albo wiadomość w skrócie `kwota, konto, osoba, kategoria, opis` (zmyślone: „200, pra, o, zam”,
„150, z, a, dom, geolog”, „45, zak reg, bułki”). Konto i osoba są opcjonalne: bez konta = gotówka; gotówka i konta drugiej
osoby zawsze na drugą osobę. Skróty kont i osób – `ustawienia.json` (`skroty_kont`, `skroty_osob`); kategorii – `reguly.json`
(`skroty`, te same co w listach). Kwota z „+” = wpływ.

1. Wydatek na budowę (kategoria „dom”, ekipa, materiał) → najpierw `koszty` B (kolejka 💸), potem krok 2 z `--budowa <id strony 💸>`.
2. Na Macu (przebieg albo Claude Code): `python3 tools/budzet/wpis.py dodaj "<treść wpisu>" --data <dzień wydatku albo wpisu>
   --id <id bloku / strony wpisu>`. Ten sam `--id` nadpisuje zapis – ponowny przebieg nie dubluje. Skrypt nic nie pisze do
   arkusza: wiersz powstaje przy zamknięciu miesiąca.
3. „✗ pierwsze pole to nie kwota” → wpis nie jest wydatkiem w skrócie; obsłuż go inną procedurą albo pytaniem ❓.
   „nieznany skrót kategorii” → zapis zostaje; pytanie pojawi się na stronie decyzji, a odpowiedź doda skrót.
4. Bez Maca (claude.ai, telefon): nic nie zapisuj – zamknięcie miesiąca złapie wydatek z wyciągu albo listy.

Przy zamknięciu: gotówka i konta drugiej osoby z wpisów = wiersze z datą i opisem (ta sama kwota na liście drugiej osoby
jest pomijana jako „już z wpisu”); konto z wyciągiem = podpowiedź kategorii i opisu dla płatności z wyciągu (kwota do
złotówki różnicy, ±4 dni); budowa z `--budowa` nie pyta „nie ma w kosztorysie”.

## B. Zamknięcie – zebranie danych („zamknijmy miesiąc RRRR-MM”)

1. Folder Dysku z `ustawienia.json` → `dysk_folder` (szukaj plików z `parentId = '<id>'`). Brakujące rzeczy z listy
   „Co przygotowuje inwestor” → **jedna lista do inwestora**. Bez wyciągów nie ruszaj; reszta może dojść później – strona
   pokaże ramkę „Brakuje”.
2. Pobierz pliki do `DANE/wyciagi/` i `DANE/listy/`.
3. Allegro: `python3 tools/budzet/allegro.py listy/allegro-<data>.txt listy/allegro-<data>.json`; uzupełnij w JSON `prop`
   i 0–2 `opcje` dla zamówień bez propozycji (format „Kategoria › Podkategoria”, kategorie z `kategorie.json`) na podstawie
   nazw produktów. Zakupy na budowę → „Dom”.
4. Pobierz `Transakcje!A1:O2500` i zapisz jako `DANE/miesiace/transakcje-<data>.json`.
5. `python3 tools/budzet/importuj.py --miesiac RRRR-MM --arkusz miesiace/transakcje-<data>.json --zen wyciagi/zen.csv
   --mbank wyciagi/mbank.csv --allegro listy/allegro-<data>.json --lista listy/RRRR-MM-<lista>.txt --gotowka listy/RRRR-MM-gotowka.txt`
   (pomiń brakujące; ścieżki względem DANE; wpisy z sekcji A czyta sam; `--salda-wpisane`, gdy salda są już w Konta).
   W listach kwota może być działaniem („5300-580 wyn”) – w arkuszu zostaje formuła.
6. `python3 tools/budzet/strona.py --dist <folder w scratchpadzie>` i opublikuj na adres `strona_url`: strona
   `<dist>/index.html` plus plik `dane.js` – zawsze oba; z nowej sesji najpierw odczytaj stronę. Decyzje inwestora w bazie
   strony (`decyzje/<id>`) zostają między publikacjami. Artefakty nie działają w `claude -p` – etapy B i C tylko w sesji
   interaktywnej.
7. Odpowiedź: link, ile wejdzie samo, ile decyzji, czego brakuje.

## C. Zamknięcie – przeniesienie („przenieś decyzje budżetu RRRR-MM”)

1. Pobierz kolekcję `decyzje` z bazy strony (limit 1000) do `DANE/miesiace/db-RRRR-MM`.
2. `python3 tools/budzet/przenies.py --miesiac RRRR-MM`. Przeczytaj `opisy`: opis idzie do kolumny Opis, ale bywa w nim
   polecenie („wpisz tylko 283”, „przyda się kategoria X”) – wykonaj je i popraw wiersz w `RRRR-MM-zapis.json`.
   `bez_decyzji` → wypisz inwestorowi i zapytaj, czy dopisać mimo to (`--mimo-brakow`); `do_wyjasnienia` rozstrzygnij w czacie.
3. Zapis do Transakcji za ostatnim wierszem: kolumny A:L i O formułami (data ISO; D liczba albo formuła; K = `import RRRR-MM`;
   O = ID źródeł – po nich kolejny import wie, co już jest), potem formuły M:N skopiuj z wiersza powyżej (wklej tylko
   formuły) i format z wiersza powyżej (wklej tylko format). Wiersz przychodu z sald zawsze ostatni w miesiącu. `zmiany`:
   w istniejącym wierszu dopisz „-kwota” do formuły D (zwrot pomniejsza zakup).
4. Salda: `salda` z pliku zapisu → zakładka Konta, kolumna następnego miesiąca (ZEN = saldo z wyciągu; mBank = poprzednia
   kolumna + zmiana). Salda drugiej osoby – od inwestora (sekcja D).
5. `python3 tools/budzet/przenies.py --miesiac RRRR-MM --zapisz-reguly` – nowe opcje sklepów, nowe sklepy (pewność pusta),
   skróty list i wpisów, sprzedawcy Allegro; odśwież zmienione wiersze zakładki **Reguły** (kolumny F–I, M, N).
6. Zapowiedziany zwrot („przyjdzie w przyszłym miesiącu, nie licz go”) → wpis w `oczekujace.json`.
7. Zakupy na budowę („Dom”) bez wpisu z `--budowa`: strona pokazuje „w kosztorysie / nie ma w kosztorysie”. Tylko brakujące
   zaproponuj dodać (procedura `koszty`), jedną listą.
8. **Kontrola:** pobierz Transakcje jeszcze raz (plik jak w B.4) i `python3 tools/budzet/kontrola.py --arkusz <plik> --rok RRRR`.
   Pewne poprawki techniczne (kwota tekstem → liczba, brak Osoby w wierszu konta drugiej osoby, Osoba w przelewie) zrób sam;
   duplikat sprawdź z wyciągiem (w wyciągu raz, w arkuszu dwa razy) i usuń dopiero po zgodzie inwestora.
9. Podsumowanie: policz miesiąc wg kategorii vs średnia 3 poprzednich, dopisz do `miesiace/RRRR-MM.json` pole
   `podsumowanie` {tekst, punkty[], kategorie[{kat, kwota, srednio}]}, przebuduj i opublikuj stronę. W czacie 3–6 linii:
   co wpisano, czego nie jesteś pewien, największe zmiany miesiąca, przychód drugiej osoby rozbity jak w sekcji D.

## D. Przychód drugiej osoby (liczony z sald)

Druga osoba nie ma wyciągów w imporcie, więc jej przychód liczy się z bilansu: **zmiana sald jej kont (Konta, wiersz
osoby: konta, gotówka, długi) + jej wydatki + przelewy do pierwszej osoby − przelewy od niej − wpływy już zapisane jako
Przychód z jej Osobą**. Wiersz w Transakcjach (kategoria `przychod_z_sald`) ma formułę z zakładki Konta i wiersza
„do dodania” w zakładce roku (`references/arkusz.md`). Żeby wynik był dobry:

- Każdy wiersz z konta drugiej osoby i z gotówki ma jej imię w kolumnie Osoba; każdy wpływ na jej konta (świadczenia,
  zwroty, inne) – też (inaczej liczy się podwójnie). Przelewy między osobami (O->A, A->O) – bez Osoby.
- Salda na koniec ostatniego dnia miesiąca. Odczyt później (np. 3. dnia) przesuwa przychód między miesiącami: płatności
  z dni po końcu miesiąca dodaj do odczytanego salda, wpływy odejmij (formuła w komórce Konta, np. `=1000+250`), i zapisz.
- Pytanie „czy przychód jest dobrze policzony” → rozpisz miesiąc: zmiana salda każdego konta, wydatki, przelewy, wpływy,
  obok dwóch poprzednich miesięcy; sprawdź kontrolę (C.8) i datę odczytu sald. Formuły zgadzają się zawsze – sprawdzaj dane.
- „Oszczędności” w dashboardzie (Przychód − Koszt − Wydatki − Inwestycje) ≠ zmiana sald „Razem wolne” w Konta → rozbij
  różnicę po stronie pierwszej osoby (u drugiej zgadza się z definicji): saldo ZEN w Konta inne niż w wyciągu (wpisuj saldo
  PLN z wyciągu), karta podarunkowa Allegro kupiona, a niewydana, zakupy Allegro Pay spłacane w kolejnym miesiącu, zwrot
  odjęty od zakupu, a zaksięgowany w kolejnym miesiącu, wymiana walut, puste salda w Konta (wtedy porównanie nic nie mówi).

## Zasady

- Pewność reguły: Zawsze – wpisuje się samo; Zwykle (i pusta) – strona z zaznaczoną propozycją; Pytaj – zawężone opcje;
  Pomiń – nie wpisuje się. Każda karta ma też „Inne wydatki › Inne wydatki: inne” i „Inna kategoria…”; wybór spoza opcji
  dopisuje się do opcji sklepu.
- BLIK do osób – pytaj o każdy. Bankomat, przelewy własne, doładowania portfela, wymiana walut – pomijane.
- Ten sam dzień, konto i kategoria → jeden wiersz z formułą sumy, nie gotowy wynik. Cashback – jeden wiersz na miesiąc.
- Zwrot pomniejsza zakup, którego dotyczy (formuła „zakup − zwrot”), nie osobny wiersz.
- Allegro: wydatki z listy zamówień (data zamówienia, zwrócone pomijane); płatności Allegro w banku, spłaty Allegro Pay
  i karta podarunkowa – pomijane, żeby się nie dublowały.
- Listy skrótów: bez dat → 1. dzień miesiąca; gotówka zawsze na drugą osobę (konto i osoba z `ustawienia.json`).
- Pensja w arkuszu brutto (przelew + pakiety jako osobne wiersze) – przelew z banku nie jest wtedy nowym wierszem.
- Pary pomijane razem (np. wydatek oddany tego samego dnia) – `ustawienia.json` → `pary_pomijane`.
- Pytaj tylko o to, czego nie da się ustalić z danych; jedna lista braków zamiast serii pytań.
- Już w arkuszu: ID w kolumnie O, potem 1:1, potem ≈1:1 (ręczny wpis do złotówki różnicy, ±3 dni, jedyny kandydat), potem
  sumy; pozycje list i wpisów (gotówka, konta drugiej osoby) – ID albo ręczny wiersz z tą samą kwotą, kontem i kategorią.
- Zakładka roku: kolory daje formatowanie warunkowe – nie koloruj ręcznie; nazwa podkategorii unikalna w całym arkuszu.
