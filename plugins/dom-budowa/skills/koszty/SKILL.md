---
name: koszty
description: Kosztorys, wydatki i wyceny materiałów – arkusz Google „Kosztorys budowy” (źródło prawdy dla liczb, prowadzi inwestor) i kolejka w Notion „💸 Wydatki → arkusz”, z której automat na Macu dopisuje wydatki i wyceny do arkusza. Używaj, gdy użytkownik podaje wydatek, fakturę, paragon, przelew dla ekipy („wydałem…”, „zapłaciłem…”, „kupiłem za…”), cenę materiału od dostawcy („beton po 371 zł w X”, „biorę stal z Y”), pyta „ile wydaliśmy”, „ile zostało”, „plan vs wydane”, „ile poszło na materiał / na ekipę”, prosi o analizę kosztorysu albo o zmianę w arkuszu (kolumna, formuła, pozycja).
---

# Koszty i kosztorys

Liczby żyją w **arkuszu Google „Kosztorys budowy”** – prowadzi go inwestor, to jedyne źródło prawdy dla kwot.
Wydatki trafiają do niego przez **kolejkę w Notion „💸 Wydatki → arkusz”**: asystent dodaje wiersz, a skrypt
`tools/wydatki.py` na Macu po każdym przebiegu Dziennika dopisuje go do arkusza (bez AI). Jak to działa i jak
skonfigurować: `docs/wydatki-arkusz.md` w repozytorium harnessu. Asystent:
- nie pisze do arkusza bezpośrednio i nie trzyma własnej kopii kwot (żadnych JSON-ów, „zapamiętanych” liczb z rozmów),
- do analiz czyta kopię wartości (niżej), a strukturę arkusza zmienia tylko na wyraźną prośbę (sekcja C).

Układ arkuszy i kolumn: `references/arkusze.md`. Pola bazy 💸 Wydatki: `notatka/references/notion-schematy.md`.

## Gdzie są liczby

- **Claude Code:** `Koszty/Kosztorys_google.json` w folderze budowy – wartości wszystkich zakładek, odświeżane co wieczór; świeże
  pobierzesz poleceniem `python3 tools/wydatki.py pobierz`. Nie ma jej (arkusz jeszcze nieskonfigurowany, kod 2) →
  najnowszy `Koszty/Kosztorys_stan_zero_*.xlsx` wg indeksu dokumentów (`python3 tools/dokumenty.py lista`). Nigdy nie
  kopiuj arkusza do repo.
- **claude.ai, telefon, Cowork:** poproś o eksport (Arkusze Google → Plik → Pobierz → Microsoft Excel) i załączenie.
- Wydatki jeszcze w kolejce (Arkusz „Do arkusza” albo „Błąd”) nie są w arkuszu – przy „ile wydaliśmy” dolicz je osobno
  i powiedz to.

## A. Pytanie o liczby („ile wydaliśmy”, „ile poszło na płytę”, „co przekracza plan”)

1. Potrzebna aktualna kopia (wyżej). Jej brak → poproś o nią jednym zdaniem. Nie odpowiadaj z pamięci.
2. Odczytaj wartości z przeliczonego pliku (formuły bez zapisanych wyników → przelicz kopię w LibreOffice).
3. Odpowiedz w trzech warstwach (`budowa`, zasada 4): PLAN (Kosztorys kol. PLAN, Etapy) · UMÓWIONE (Etapy kol. „Umowa
   z ekipą”, wybrane oferty) · WYDANE (Wydatki „Zrealizowane”), plus zobowiązania (Wydatki „Do zapłaty”, Etapy kol.
   „Do zapłaty ekipie”).
4. Dla stanu zero podawaj podział z Podsumowania: materiał / ekipa / inne per etap (płyta, ściany, izolacje, strop…),
   plan, wydane i szacunek AI (kolumna obok; całość budowy wg stanów – tabela „Szacunek AI całej budowy”). Na końcu 3 największe odchylenia z komentarzem i suma wydatków stanu zero bez typu (psuje podział).

## B. Wydatek (Dziennik, rozmowa, faktura, paragon, przelew)

1. Wyciągnij: datę, kwotę **brutto** (tyle, ile zapłacono), na co, przy materiale ilość i jednostkę, typ (Materiał /
   Robocizna / Sprzęt / Usługa / Formalności), sposób (Przelew / Gotówka / Karta / BLIK), płatność (Zrealizowane =
   zapłacone; Do zapłaty = faktura albo transza czeka), dostawcę / nr FV. Datę względną przelicz na datę.
2. **Pozycja** – wybierz z listy pola Pozycja w bazie (opcje = pozycje arkusza Kosztorys, numer + nazwa; pobierz schemat
   bazy). Zasady:
   - przelew dla ekipy za etap z umowy → „Ekipa – transza …” tego etapu, Typ Robocizna;
   - dopłata poza umową → „Roboty dodatkowe – poza umową” w etapie, którego dotyczy (osobny wiersz, nigdy w transzy);
   - materiał → pozycja materiału w etapie, na który poszedł (beton na chudziak → chudziak, stal na ściany → stal ścian);
   - jedna faktura na kilka pozycji → kilka wierszy (podziel kwotę wg faktury; bez rozbicia → zapytaj);
   - brak pasującej pozycji albo niepewność → nie zgaduj: pytanie z propozycją (we wpisie Dziennika „❓” wg `wpisy`,
     w rozmowie – wprost); nowa pozycja to zmiana arkusza (sekcja C).
3. Sprawdź duplikat: w bazie wiersz z tą samą datą i kwotą → zaktualizuj go zamiast dodawać drugi.
4. Zapisz wiersze w „💸 Wydatki → arkusz” jednym wywołaniem: Wydatek (krótko, co kupione), Data, Kwota, Pozycja, Typ,
   Ilość + Jedn. (materiał – obowiązkowo), Płatność, Sposób, Dostawca / nr FV, Notatki, **Arkusz = „Do arkusza”**
   (puste działa tak samo; „Nie wysyłać” wstrzymuje). Wydatek wpisany ręcznie w arkuszu nie idzie do kolejki – jedna droga.
   Brakujące pole, które da się uzupełnić później (sposób, nr FV) – zostaw puste; brak kwoty, daty albo pozycji → pytanie
   zamiast zapisu.
5. Potwierdź jedną linią: „N wydatków w kolejce do arkusza (pozycje …) – trafią do niego przy najbliższym przebiegu na
   Macu”. Bez narzędzi Notion → Skrzynka (`budowa`, zasada 13), słowami ze wszystkimi polami z kroku 1.
6. Wiersz z Arkusz = „Błąd” (powód w polu Błąd) pokazuj w przeglądzie dnia budowy jako sprawę czekającą; po poprawce pola
   inwestor albo asystent ustawia znów „Do arkusza”. Wiersz „W arkuszu” poprawia się już w arkuszu, nie w Notion; wydatek
   wysłany przez pomyłkę – w Claude Code `python3 tools/wydatki.py wycofaj <id strony>`.

Zakup z listy 🧱 Zakupy budowy: najpierw `zakupy` (Status, dostawa), potem ten wydatek.

## B2. Wycena dostawcy (cena materiału przed zakupem)

1. Jedna oferta jednego dostawcy na jedną rzecz = jeden wiersz w tej samej kolejce, **Rodzaj = Wycena**: Wydatek (co,
   np. „Beton C25/30 W8 (płyta)”), Data, Kwota = **cena za jednostkę**, Jedn., Cena podana (Netto / Brutto – nie zgaduj,
   zapytaj), przy netto **VAT %** (stawka od inwestora albo z oferty), Dostawca, Pozycja (gdy pasuje), Status wyceny = Oferta, Ważna do, Notatki (transport, minimum, z czego
   wyliczona cena – np. „28 930 zł za 8 t”), Arkusz = „Do arkusza”. Cena za całość → przelicz na jednostkę i zapisz w Notatkach.
2. Kilka ofert na to samo = kilka wierszy z tą samą Pozycją; arkusz oznacza najtańszą (★, porównanie brutto).
3. Decyzja („biorę z X”) → w wierszu X Status wyceny = Wybrana, w pozostałych ofertach tej pozycji = Odrzucona; wszystkie
   zmienione znów „Do arkusza” (arkusz zaktualizuje te same wiersze). Kosztorys pokaże cenę wybraną i ilość × cena –
   zaproponuj inwestorowi nowy PLAN pozycji (sekcja C, krok 2).
4. Ceny zapłaconej nie wpisuj jako wyceny – wynika z wydatku (Wydatki, Cena jedn.).

## C. Zmiana w arkuszu (pozycja, kolumna, formuła)

1. Opisz zmianę i jej wpływ (które arkusze i formuły) – przy większych poczekaj na „ok”.
2. Nigdy nie proś o ponowny import pliku – arkusz żyje w Google. Prosta zmiana danych (nowa pozycja, kwota PLAN) →
   instrukcja krok po kroku dla inwestora; nowa pozycja trafi na listę w Notion przy wieczornym `wydatki.py pozycje`.
3. Zmiana układu lub wyglądu (kolumny, formuły, kolory, listy) – w Claude Code, na żywym arkuszu, według
   `docs/wydatki-arkusz.md`, sekcja 8: docelowy `.xlsx` sprawdzony lokalnie i porównany z kopią → plik zmian → `migruj`
   → `pobierz` i kontrola (zero błędów formuł, te same sumy); cofanie – historia wersji arkusza. Formuły zgodne z Arkuszami Google
   (SUMIFS, INDEX/MATCH, IF, MINIFS; bez formuł tablicowych). Poza Claude Code – opisz zmianę i odłóż do Claude Code.
4. Szacunek AI (zakładka „Szacunek AI 10.2026”, pełna wycena z 10.2026): gdy dochodzi nowa pozycja albo etap (np. SSO),
   przypisz pasujące wiersze szacunku w kol. J (etap) i K (pozycja „Lp Nazwa”) – plik zmian z operacją `zakres` tylko na
   tych komórkach J:K; nie zmieniaj kwot szacunku. Wiersze niepasujące zostają bez przypisania (liczą się wg stanu).
5. Kolumny A–O arkusza Wydatki, kolumny A, B, M arkusza Kosztorys i nazwy tych arkuszy czyta automat – zmiana ich kolejności
   albo nazw wymaga zmiany `tools/wydatki.py` i kodu Apps Script w tym samym kroku.
6. Oddaj plik albo instrukcję + krótką listę zmian (arkusz, zakres, co).

## D. Płatności, transze, kredyt

1. Transze z umowy z ekipą: kwota w Etapy kol. „Umowa z ekipą”, reszta do zapłaty w kol. „Do zapłaty ekipie”; terminy
   odbiorów – Harmonogram (`harmonogram`). Przed każdą transzą sprawdź protokół odbioru (`etap`, sekcja C) – bez niego
   powiedz to wprost. Zapłacona transza → wydatek (sekcja B) na pozycję „Ekipa – transza …”; faktura czeka → Płatność
   „Do zapłaty”.
2. Zaliczka, zatrzymanie, kary – zasady z umowy (`oferta/references/umowa.md`); kwoty zapisuj jako wydatki tej samej transzy.
3. Kredyt w transzach po etapach – na „co do banku” zestaw: etap, stan wg arkusza (Podsumowanie), dokumenty (faktury,
   zdjęcia, wpisy kierownika), termin kontroli. Wymagania banku są w umowie kredytowej (folder budowy) – nie zgaduj ich.
4. „Ile potrzebuję w tym miesiącu”: wydatki „Do zapłaty” + transze, których odbiór wypada w miesiącu (Harmonogram) +
   zamówienia z `zakupy` z terminem w miesiącu; osobno zobowiązania bez daty.

## Zasady

- Kwoty wydatków = tyle, ile zapłacono (zwykle brutto). Oferty = netto + VAT.
- Ceny rynkowe: z widełkami min–max i źródłem z datą; nie wymyślaj cen – wyszukaj.
- Nie zmieniaj ilości ani cen PLAN bez wskazania źródła (przedmiar, zestawienie stali, oferta, umowa).
- Cennik = wyceny przed zakupem (sekcja B2); ceny zapłacone są w Wydatkach.
- Wiedza o kosztach z filmów trafia do Informacji w Bazie wiedzy (procedura `wiedza`, Rodzaj „Koszt / cena”,
  „Wrażliwe na czas”), a do arkusza tylko na prośbę inwestora.
