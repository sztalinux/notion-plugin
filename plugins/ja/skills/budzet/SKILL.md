---
name: budzet
description: Budżet domowy w arkuszu Google „Budżet domowy” – wydatki z wpisów („200, pra, o, zam”, gotówka, wydatek na budowę także do budżetu) od razu w arkuszu (automat w ciągu godziny) i miesięczne zamknięcie – wyciągi (mBank, ZEN), lista zakupów Allegro, lista wydatków drugiej osoby, strona decyzji (artefakt), zapis do Transakcji, przypięcie płatności z wyciągu do wierszy z wpisów, kontrola arkusza, przychód drugiej osoby z sald i podsumowanie miesiąca. Wpis wydatku działa też w przebiegu na Macu; zamknięcie tylko w Claude Code na Macu (skrypty tools/budzet). Używaj, gdy użytkownik mówi „zamknijmy miesiąc”, „budżet za październik”, „wrzuciłem wyciągi”, „przenieś decyzje budżetu RRRR-MM”, „podsumuj miesiąc w budżecie”, „czy przychody są dobrze policzone”, wkleja listę Allegro albo listę wydatków ze skrótami, wpisuje wydatek w skrócie „kwota, konto, osoba, kategoria, opis” albo zwykłym zdaniem („wydałem N zł na regularne i M na jedzenie na mieście”), dodaje zdjęcie paragonu („rozpisz paragon”).
---

# Budżet domowy – wydatki na bieżąco i zamknięcie miesiąca

Kod: `tools/budzet/` (wpis, paragon, arkusz_budzetu, importuj, przenies, kontrola, allegro, strona). **Dane są poza repo** w
`<folder budowy>/.dom/budzet/` (`DANE` w `tools/budzet/wspolne.py`): `ustawienia.json` (ID arkusza, adres strony, folder
Dysku, konta, osoby, skróty kont i osób, pary pomijane, reguły specjalne), `kategorie.json`, `reguly.json` (reguły sklepów,
skróty kategorii, sprzedawcy Allegro – źródło prawdy; zakładka „Reguły” w arkuszu to widok), `oczekujace.json` (zapowiedziane
zwroty), `wyciagi/`, `listy/` (listy i `RRRR-MM-wpisy.jsonl`), `miesiace/`. Nigdy nie kopiuj tych danych do repo.
Arkusz ma locale en_US: w formułach kropka (`=12.99+5.49`). Układ arkusza (zakładka roku, Konta, formuły, nowy rok):
`references/arkusz.md`. Wpisy → arkusz (skrypt Apps Script arkusza, znacznik wysyłki, zapas, wdrożenie): `docs/budzet-arkusz.md`
w repo harnessu.

## Co przygotowuje inwestor (lista do przypomnienia na koniec miesiąca)

1. Wyciągi CSV za miesiąc: mBank i ZEN → folder Dysku `dysk_folder` (mogą obejmować kilka miesięcy).
2. Allegro → „Moje zakupy” → zaznacz i skopiuj tekst → plik na Dysk.
3. Lista wydatków drugiej osoby (nagłówki kont, skróty) – całe zapłacone kwoty z jej kont, bez tego, co było we wpisach
   (sekcja A). Gotówka jest tylko we wpisach – osobnej listy gotówki nie ma.
4. Salda kont drugiej osoby **na koniec ostatniego dnia miesiąca** (historia w aplikacji banku) i stan gotówki → zakładka
   Konta, kolumna następnego miesiąca. Saldo odczytane później → podaj też operacje z dni po końcu miesiąca (sekcja D).

## A. Wydatek z wpisu w trakcie miesiąca

Wpis w Dzienniku albo wiadomość w skrócie `kwota, konto, osoba, kategoria, opis` (zmyślone: „200, pra, o, zam”,
„150, z, a, dom, geolog”, „45, zak reg, bułki”). Konto i osoba są opcjonalne: bez konta = gotówka; gotówka i konta drugiej
osoby zawsze na drugą osobę. Skróty kont i osób – `ustawienia.json` (`skroty_kont`, `skroty_osob`); kategorii – `reguly.json`
(`skroty`, te same co w listach). Kwota z „+” = wpływ.

**Wydatek zwykłym zdaniem** („wydałem N zł na regularne i M na jedzenie na mieście” – bez skrótu, konta i osoby) to też
wydatek: sam przepisz go na skrót (kategorię dobierz ze skrótów w `reguly.json`, np. „N, zak reg” i „M, jedz, na mieście”)
i zapisz krokiem 2. Nie pytaj o konto ani osobę – brak szczegółów = gotówka drugiej osoby (wydatek na budowę – konto wg pkt 1;
wyjątek: paragon – niżej). Kilka wydatków w jednym wpisie =
osobne wywołania z `--id <id>-1`, `<id>-2` (ten sam ID nadpisałby poprzedni). Pytaj tylko o brakującą kwotę albo kategorię,
której nie da się dobrać.

**Paragon ze zdjęcia** (obraz we wpisie z dopiskiem, kto płacił i czym) → `references/paragony.md`: pobranie zdjęcia
(`paragon.py pobierz`), odczyt pozycji, rozpisanie i kontrola sumy skryptem (`paragon.py rozpisz` – części `<id>-1…n`
z polem `grupa`), część na budowę także do kolejki 💸. **Paragon bez „kto i czym” → ❓ pod wpisem, nic się nie zapisuje**
(wyjątek od „brak szczegółów = gotówka”). Paragon zawsze cały.

1. Wydatek na budowę (ekipa, materiał, usługa) → reguła `dom-budowa/skills/koszty/references/wydatek-przeplyw.md` (kosztorys i budżet, konto, zwroty).
2. Na Macu (przebieg albo Claude Code): `python3 tools/budzet/wpis.py dodaj "<treść wpisu>" --data <dzień wydatku albo wpisu>
   --id <id bloku / strony wpisu>`. Ten sam `--id` nadpisuje zapis – ponowny przebieg nie dubluje. Zapis z datą od 1.12.2026
   trafia do Transakcji w ciągu godziny (automat po przebiegu: `arkusz_budzetu.py sync`; ID wpisu w kolumnie O, Notatki
   „z wpisu”); w sesji Claude Code z inwestorem (nie w przebiegu) uruchom zaraz po zapisie
   `python3 tools/budzet/arkusz_budzetu.py sync`. Starsze zapisy
   (listopad) i te, których skrypt arkusza nie przyjął, dopisze zamknięcie miesiąca po ID. Usunięcie wydatku:
   `python3 tools/budzet/wpis.py usun RRRR-MM <id>` (w sesji potem `sync` – wiersz znika z arkusza).
   Wydatek budowy: dodatkowo `--budowa <id strony 💸>` i `--gotowka` (Sposób = Gotówka); konto budowy: `wpis.py ustaw-konto-budowy <skrót>`
   (`dom-budowa/skills/koszty/references/wydatek-przeplyw.md`). Składnia jest tu – nie sprawdzaj `--help`; jedno polecenie na wywołanie, ścieżka względna od repo, bez `cd`, potoków i `;`.
3. „✗ pierwsze pole to nie kwota” → wpis nie jest wydatkiem w skrócie; obsłuż go inną procedurą albo pytaniem ❓.
   „nieznany skrót kategorii” → zapis zostaje; pytanie pojawi się na stronie decyzji, a odpowiedź doda skrót.
4. Bez Maca (claude.ai, telefon): wydatek do Skrzynki z polem „Zrobić: wydatek …” (`wpisy/references/skrzynka.md`); Mac zapisze go krokiem 2.
5. Komunikat 🔔 `skrypt-arkusz_budzetu-kontrola` (nocna kontrola: wpis bez wiersza w arkuszu): odpowiedź „dopisz ponownie”
   → `python3 tools/budzet/arkusz_budzetu.py ponow <id>`; „usuń” → `python3 tools/budzet/wpis.py usun RRRR-MM <id>`
   (`wpisy/references/pytania.md`, C). Wiersz z ID wpisu bez zapisu w pliku – zaproponuj inwestorowi usunięcie wiersza w arkuszu.
   `skrypt-arkusz_budzetu-sync` – zapisy czekają w pliku; przyczyny: `docs/budzet-arkusz.md`, sekcja 5.

Przy zamknięciu: gotówka i konta drugiej osoby z wpisów – ID w kolumnie O = już w arkuszu, inaczej wiersz z datą i opisem
(zapas); ta sama kwota na liście drugiej osoby jest pomijana jako „już z wpisu” (paragon: tylko suma całego paragonu, kwota
bliska sumie → strona decyzji – `references/paragony.md`, 6). Konto z wyciągiem: płatność (do złotówki różnicy, ±4 dni,
także przez przełom miesiąca) przypina się do wiersza z wpisu (paragon: do wszystkich części, gdy płatność = suma) – ID
wyciągu do O, kwota z wyciągu do D, bez nowego wiersza;
wpisu nie ma w arkuszu – wiersz z płatności z kategorią wpisu; wpis z ostatnich dni miesiąca bez pary, gdy wyciąg ich nie
obejmuje, czeka na import kolejnego miesiąca; reszta bez pary → strona decyzji. Budowa z `--budowa` nie pyta „nie ma w kosztorysie”.

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
   --mbank wyciagi/mbank.csv --allegro listy/allegro-<data>.json --lista listy/RRRR-MM-<lista>.txt`
   (pomiń brakujące; ścieżki względem DANE; wpisy z sekcji A czyta sam – także końcówkę poprzedniego i początek następnego
   miesiąca; `--salda-wpisane`, gdy salda są już w Konta).
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
3. Zapis do Transakcji za ostatnim wierszem – numer ostatniego wiersza odczytaj tuż przed zapisem (automat dopisuje wiersze
   z wpisów co godzinę): kolumny A:L i O formułami (data ISO; D liczba albo formuła; K = `import RRRR-MM`; L = Notatki z pliku;
   O = ID źródeł – po nich kolejny import wie, co już jest), potem formuły M:N skopiuj z wiersza powyżej (wklej tylko
   formuły) i format z wiersza powyżej (wklej tylko format). `przypiecia` (płatność z wyciągu do wierszy z wpisów):
   `python3 tools/budzet/arkusz_budzetu.py przypnij --miesiac RRRR-MM`; bez skryptu – konektorem: w każdym wierszu dopisz
   „,<id wyciągu>” w O, a podaną kwotę wpisz w D. Wiersz przychodu z sald zawsze ostatni w miesiącu. `zmiany`:
   w istniejącym wierszu dopisz „-kwota” do formuły D (zwrot pomniejsza zakup).
4. Salda: `salda` z pliku zapisu → zakładka Konta, kolumna następnego miesiąca (ZEN = saldo PLN z wyciągu; mBank =
   poprzednia kolumna + zmiana). `korekty` dopisz do salda konta w tej samej formule (`=1000+250-80`, przykład
   zmyślony): Allegro Pay do spłaty (minus), zwrot odjęty od zakupu, a jeszcze niezaksięgowany (plus), niewydana reszta
   karty podarunkowej (plus – kwotę podaje inwestor). Dzięki temu zmiana sald zgadza się z oszczędnościami (sekcja D).
   Salda drugiej osoby – od inwestora (sekcja D).
5. `python3 tools/budzet/przenies.py --miesiac RRRR-MM --zapisz-reguly` – nowe opcje sklepów, nowe sklepy (pewność pusta),
   skróty list i wpisów, sprzedawcy Allegro; odśwież zmienione wiersze zakładki **Reguły** (kolumny F–I, M, N).
6. Zwrot odjęty od zakupu w tym miesiącu, a pieniądze przyjdą później (albo zapowiedziany zwrot „nie licz go”) → wpis
   w `oczekujace.json` na miesiąc wpływu: `miesiac`, `klucz` (fragment opisu z wyciągu), `kierunek`, `kwota`, `powod`.
   Import tamtego miesiąca pominie wpływ (bez dubla), a import tego miesiąca doda kwotę do `korekty` salda.
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
  Wiersze z wpisów (ID z prefiksem `w` w O) nie są scalane – jeden ID = jeden wiersz.
- Zwrot z wyciągu pomniejsza zakup, którego dotyczy (formuła „zakup − zwrot”), nie osobny wiersz; zwrot z wpisu („+”) to
  własny wiersz z kwotą ujemną.
- Allegro: wydatki z listy zamówień (data zamówienia, zwrócone pomijane); płatności Allegro w banku, spłaty Allegro Pay
  i karta podarunkowa – pomijane, żeby się nie dublowały.
- Lista skrótów: bez dat → 1. dzień miesiąca. Gotówka (tylko z wpisów) zawsze na drugą osobę (konto i osoba z `ustawienia.json`).
- Pensja w arkuszu brutto (przelew + pakiety jako osobne wiersze) – przelew z banku nie jest wtedy nowym wierszem.
- Pary pomijane razem (np. wydatek oddany tego samego dnia) – `ustawienia.json` → `pary_pomijane`.
- Pytaj tylko o to, czego nie da się ustalić z danych; jedna lista braków zamiast serii pytań.
- Już w arkuszu: ID w kolumnie O, potem wiersz z wpisu (przypięcie, wyżej), potem 1:1, potem ≈1:1 (ręczny wpis do złotówki
  różnicy, ±3 dni, jedyny kandydat), potem sumy; pozycje list i wpisów (gotówka, konta drugiej osoby) – ID albo ręczny wiersz
  z tą samą kwotą, kontem i kategorią. Wiersze z wpisów nie liczą się do „wpisane ręcznie do dnia X”.
- Zakładka roku: kolory daje formatowanie warunkowe – nie koloruj ręcznie; nazwa podkategorii unikalna w całym arkuszu.
