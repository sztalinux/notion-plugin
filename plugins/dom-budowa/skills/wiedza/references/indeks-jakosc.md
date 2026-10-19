# Indeks wiedzy – obserwator jakości wyszukiwania

Cel: wiedzieć, czy `wiedza.py szukaj` nadal znajduje to, co powinien, zanim inwestor zauważy złą odpowiedź.
Narzędzie: `python3 tools/wiedza_jakosc.py` – tylko Claude Code na Macu (na claude.ai nie ma `tools/`).

## Co mierzy

- **Log zapytań**: każde `szukaj` na indeksie z `.dom/wiedza/` dopisuje wiersz do `szukaj.log.jsonl` – kanał
  (`claude-code`, `nocny` – ustawiają go skrypty nocne, `inny`), zapytanie (do 500 znaków), tryb (AND, dopełnienie,
  samo OR, same słowa wypełniające), liczby trafień, 5 pierwszych WI, czas. Bez treści wierszy. `WIEDZA_LOG=0` wyłącza log.
- **Zbiory oceny** (`zloty`): known-item (słowa wiersza z perturbacjami: odmiana, bez polskich znaków, rama pytania,
  wypełniacz, rzadki czasownik, kolejność), tematy (nazwa tematu → informacje z relacją), pytania wymyślone
  z predykatami słów, test czasowników i przypadki inwestora. Miary: success@12 i MRR (po całej liście), P@12.
  Wiersze ukryte w Notion (Nieaktualne, Ciekawostka, usunięte) wypadają z oceny – to nie jest regresja.
- **Porównanie z Notion** (`notion`, raz w miesiącu): przybliżenie dawnej drogi „prosto do Notion”.

## Czego nie mierzy

- Zapytań z czatu na telefonie i zaplanowanych zadań claude.ai – działają na kopii w sandboksie, logu nie ma.
  Zbiory oceny testują ten sam kod i ten sam indeks, więc pokrywają też ten kanał.
- Prawdziwej trafności: predykaty słów to przybliżenie (±1 P@12 na pytanie, ślepe na synonimy i sens).
- Wyszukiwarki Notion MCP: `notion` używa publicznego API (filtr `contains`, AND słów, przy zerze OR).

## Polecenia

- `zloty [--odnowa] [--ustaw-baze]` – przebieg zbiorów (kilka sekund), zapis w historii, porównanie z poprzednim
  i z bazą (pierwszy przebieg = baza). Zmianę wyników przyjętą przez inwestora zatwierdź `--ustaw-baze`.
  `--odnowa` (program podpowie ją po przyroście informacji o > 10%) losuje nowy zbiór KI i robi bazą nowy przebieg.
- `dodaj "zapytanie" --powinno WI-12,WI-40` – przypadek „to powinno się znaleźć”; od tej chwili każda jego strata
  to alarm. Dodawaj, gdy inwestor mówi „tego nie znalazł” albo odpowiedź opierała się na złych wierszach.
- `raport [--dni 7]` – raport tygodniowy (opis niżej); `--json` dla agenta. Raport potwierdza pokazane alarmy.
- `reczna [--n 30]` – ocena ręczna (sekcja niżej); `notion [--budzet 300]` – porównanie z Notion, tylko odczyt.
- `przypomnij --cicho` – hook startu sesji: jedna linia, gdy raport tygodniowy czeka, są niepotwierdzone alarmy
  albo obserwator nie działa („obserwator nie działa: Typ” – najwyżej raz w tygodniu). Raz w tygodniu sam robi
  przebieg `zloty`; przebieg odrzucony przez równoległy sync albo dłuższy niż 10 s – kolejna próba po dobie.

Pytania: `.dom/wiedza/jakosc/pytania.json`, przy pierwszym użyciu kopia `tools/wiedza_jakosc_pytania.json` (pytania
wymyślone, bez treści bazy). Format: `{"zestawy": {"NAZWA": [{"q": "pytanie", "wzory": ["drena", "glebok|poziom"]}]}}` –
trafna informacja ma na początku jakiegoś słowa (bez polskich znaków, w tezie, szczegółach, „dla naszej budowy” albo
nazwie tematu) każdy wzór. Plik można rozszerzać; `--odnowa` go nie rusza. Zestaw KLUCZOWE8 to baza testu czasowników.

## Jak czytać raport

- `log`: zapytań wg kanału, zero wyników, dopełnienie (część słów), wąskie (< 5 trafień), mediana trafień i czasu.
- `zbiór złoty`: wynik ostatniego przebiegu; `vs poprzedni` i `vs baza` – lepsze/gorsze ID zapytań (KI-WI-…, T-…,
  nazwa zestawu, V… czasowniki, W… przypadki inwestora), liczone na wspólnych ID.
- `zapytania z logu bez wyników`: kandydaci do decyzji inwestora – dopisać synonim, dopisać informację, zignorować.
- Alarmy (względem poprzedniego przebiegu i bazy; zostają w historii, aż pokaże je `raport`): KI success@12 spada
  o > 5 pkt; tematy P@12 o > 2; pytanie traci ≥ 3 pkt P@12; przypadek inwestora gorszy; zero wyników ≥ 2× wobec
  poprzednich 4 tygodni (od 5%, min. 20 zapytań w obu okresach); ostatni wpis logu starszy niż 7 dni. Alarm po
  zmianie `szukaj` → nie wydawaj zmiany bez wyjaśnienia w CHANGELOG; bez zmiany kodu → `wiedza.py stan` i ostatni sync
  (porównanie mówi, czy między przebiegami zmienił się kod szukaj albo dane indeksu).
- Punkty P@12 w porównaniach i alarmach są przeliczone na 12 możliwych trafnych: pytanie z jedną trafną informacją
  traci 12 pkt, gdy jej zabraknie (sumy w linii wyniku zostają surowe).

## Ocena ręczna

`python3 tools/wiedza_jakosc.py reczna` uruchamia inwestor sam, w terminalu: dla każdego z 5 pierwszych wyników
naciska y (trafny), n (nietrafny), s (pomiń), q (przerwa – to samo polecenie wznawia). Tekst wyników pokazuje tylko
w terminalu; uruchomione przez agenta podaje same liczby. To higiena, nie zabezpieczenie – agent nie uruchamia jej
przez `script` ani pty. Wynik („trafne %”) widać w `raport`. Raz po większej zmianie `szukaj`, ok. 30–45 minut.

## Prywatność

- Wszystko leży obok indeksu w `<hub>/.dom/wiedza/` (katalog 700, pliki 600), nigdy w repo ani w kopii dla czatu;
  z `--db` w innym miejscu program odmawia zapisu. `.gitignore`, hook `pre-commit` i `build.py` blokują te pliki.
- Wyjście poleceń: liczby, numery WI, rangi, czasy i ID; tekst – tylko zapytania z logu (wpisane przez inwestora
  i agentów) i, w terminalu inwestora, wyniki oceny ręcznej. Token Notion nigdy nie jest drukowany.

## Sędzia LLM

`sedzia` – model ocenia 0/1/2 pierwsze 12 wyników pytań wymyślonych (zgoda inwestora 19.10.2026: bez danych
osobowych). Domyślnie na sucho; wysyłka tylko `--wyslij` po zgodzie inwestora. Co idzie do modelu, filtr, jak czytać
wynik: `references/indeks-sedzia.md`. Hook startu nigdy go nie woła.
