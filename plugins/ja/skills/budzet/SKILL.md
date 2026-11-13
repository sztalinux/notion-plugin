---
name: budzet
description: Zamknięcie miesiąca w arkuszu Google „Budżet domowy” – zbiera wyciągi (mBank, ZEN), listę zakupów Allegro, listy wydatków drugiej osoby i gotówki z Dysku, dopasowuje je do arkusza i reguł, publikuje stronę decyzji (artefakt), a po decyzjach wpisuje wiersze do Transakcji, uczy reguły i robi podsumowanie miesiąca. Tylko Claude Code na Macu (skrypty tools/budzet). Używaj, gdy użytkownik mówi „zamknijmy miesiąc”, „budżet za październik”, „wrzuciłem wyciągi”, „przenieś decyzje budżetu RRRR-MM”, „podsumuj miesiąc w budżecie”, wkleja listę Allegro albo listę wydatków ze skrótami.
---

# Budżet – zamknięcie miesiąca

Kod: `tools/budzet/` (importuj, przenies, allegro, strona). **Dane są poza repo** w `<folder budowy>/.dom/budzet/`
(`DANE` w `tools/budzet/wspolne.py`): `ustawienia.json` (ID arkusza, adres strony, folder Dysku, konta, osoby, pary
pomijane, reguły specjalne), `kategorie.json`, `reguly.json` (reguły sklepów, skróty list, sprzedawcy Allegro – źródło prawdy;
zakładka „Reguły” w arkuszu to widok), `oczekujace.json` (zapowiedziane zwroty), `wyciagi/`, `listy/`, `miesiace/`.
Nigdy nie kopiuj tych danych do repo. Arkusz ma locale en_US: w formułach kropka (`=12.99+5.49`).
Artifact i ArtifactData nie działają w `claude -p` – procedura tylko w sesji interaktywnej.

## Etap 1 – zebranie danych („zamknijmy miesiąc RRRR-MM”)

1. Folder Dysku z `ustawienia.json` → `dysk_folder` (search_files `parentId = '<id>'`). Potrzebne za miesiąc:
   wyciąg mBank (CSV), wyciąg ZEN (CSV), lista „Moje zakupy” z Allegro (skopiowany tekst), lista wydatków drugiej osoby
   (skróty, nagłówki kont), lista gotówki (skróty) oraz salda kont drugiej osoby w zakładce **Konta** (kolumna następnego
   miesiąca – z nich liczy się jej przychód). Czego brakuje → **jedna lista do inwestora** (co i skąd). Bez wyciągów nie
   ruszaj; reszta może dojść później – strona pokaże ramkę „Brakuje”.
2. Pobierz pliki (download_file_content) do `DANE/wyciagi/` i `DANE/listy/`. Wyciągi obejmują zwykle kilka miesięcy – to
   dobrze (zwroty i dopasowania szukają wstecz).
3. Allegro: `python3 tools/budzet/allegro.py listy/allegro-<data>.txt listy/allegro-<data>.json`; uzupełnij w JSON `prop`
   i 0–2 `opcje` dla zamówień bez propozycji (format „Kategoria › Podkategoria”, kategorie z `kategorie.json`) na podstawie
   nazw produktów. Zakupy na budowę → „Dom”.
4. `get_values Transakcje!A1:O2500` → zapisz wynik jako `DANE/miesiace/transakcje-<data>.json`.
5. `python3 tools/budzet/importuj.py --miesiac RRRR-MM --arkusz miesiace/transakcje-<data>.json --zen wyciagi/zen.csv
   --mbank wyciagi/mbank.csv --allegro listy/allegro-<data>.json --lista listy/RRRR-MM-<lista>.txt --gotowka listy/RRRR-MM-gotowka.txt`
   (pomiń brakujące; ścieżki względem DANE; `--salda-wpisane`, gdy salda drugiej osoby są już w Konta). W listach skrótów
   kwota może być działaniem („5300-580 wyn”) – w arkuszu zostaje formuła.
6. `python3 tools/budzet/strona.py --dist <folder w katalogu roboczym sesji albo scratchpad>` i publikuj na adres
   `strona_url`: Artifact `file_path=<dist>/index.html`, `files={"dane.js": "<dist>/dane.js"}` – zawsze oba; z nowej
   sesji najpierw `Artifact read` strony. Decyzje inwestora w db (`decyzje/<id>`) zostają między publikacjami.
7. Odpowiedź: link, ile wejdzie samo, ile decyzji, czego brakuje.

## Etap 2 – przeniesienie („przenieś decyzje budżetu RRRR-MM”)

1. ArtifactData `list` kolekcji `decyzje` (limit 1000, `out_dir=DANE/miesiace/db-RRRR-MM`).
2. `python3 tools/budzet/przenies.py --miesiac RRRR-MM`. Przeczytaj `opisy`: opis idzie do kolumny Opis, ale bywa w nim
   polecenie („wpisz tylko 283”, „przyda się kategoria X”) – wykonaj je i popraw wiersz w `RRRR-MM-zapis.json`.
   `bez_decyzji` → wypisz inwestorowi i zapytaj, czy dopisać mimo to (`--mimo-brakow`); `do_wyjasnienia` rozstrzygnij w czacie.
3. Zapis do Transakcji za ostatnim wierszem: kolumny A:L i O przez `update_formulas` (data ISO; D liczba albo formuła;
   K = `import RRRR-MM`; O = ID z wyciągów – po nim kolejny import wie, co już jest), potem formuły M:N skopiuj z wiersza
   powyżej (`copyPaste`, PASTE_FORMULA). Wiersz przychodu liczonego z sald zawsze ostatni w miesiącu. `zmiany`:
   w istniejącym wierszu dopisz „-kwota” do formuły D (zwrot pomniejsza zakup).
4. Salda: `salda` z pliku zapisu → zakładka Konta, kolumna następnego miesiąca (ZEN = saldo z wyciągu; mBank = poprzednia
   kolumna + zmiana).
5. `python3 tools/budzet/przenies.py --miesiac RRRR-MM --zapisz-reguly` – nowe opcje sklepów, nowe sklepy (pewność pusta),
   skróty list, sprzedawcy Allegro; odśwież zmienione wiersze zakładki **Reguły** (kolumny F–I, M, N).
6. Zapowiedziany zwrot („przyjdzie w przyszłym miesiącu, nie licz go”) → wpis w `oczekujace.json`.
7. Zakupy na budowę („Dom”): inwestor wpisuje je zwykle od razu do kosztorysu budowy – strona pokazuje „w kosztorysie /
   nie ma w kosztorysie”. Tylko brakujące zaproponuj dodać (procedura `koszty`), jedną listą.
8. Podsumowanie: pobierz Transakcje jeszcze raz, policz miesiąc wg kategorii vs średnia 3 poprzednich, dopisz do
   `miesiace/RRRR-MM.json` pole `podsumowanie` {tekst, punkty[], kategorie[{kat, kwota, srednio}]}, przebuduj i opublikuj
   stronę. W czacie 3–6 linii: co wpisano, czego nie jesteś pewien, największe zmiany miesiąca.

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
- Już w arkuszu: ID w kolumnie O, potem 1:1, potem ≈1:1 (ręczny wpis do złotówki różnicy, ±3 dni, jedyny kandydat), potem sumy.
  Przed zapisem sprawdź, czy wpływy na konta drugiej osoby (świadczenia, zwroty) nie są już w jej przychodzie liczonym z sald.
- Zakładka roku (np. „2026”): kolory wierszy daje formatowanie warunkowe po kolumnach A–C (typ / kategoria / podkategoria) –
  nie koloruj ręcznie. Sumuje podkategorie po samej nazwie, więc nazwa podkategorii musi być unikalna w całym arkuszu.
