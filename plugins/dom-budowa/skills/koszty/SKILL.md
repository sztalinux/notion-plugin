---
name: koszty
description: Kosztorys i wydatki budowy – arkusz Google „Kosztorys budowy” (źródło prawdy dla liczb, prowadzi inwestor) i kolejka wydatków w Notion „💸 Wydatki → arkusz”, z której automat na Macu dopisuje wydatki do arkusza. Używaj, gdy użytkownik podaje wydatek, fakturę, paragon, przelew dla ekipy („wydałem…”, „zapłaciłem…”, „kupiłem za…”), pyta „ile wydaliśmy”, „ile zostało”, „plan vs wydane”, „ile poszło na materiał / na ekipę”, prosi o analizę kosztorysu albo o zmianę w arkuszu (kolumna, formuła, pozycja).
---

# Koszty i kosztorys

Liczby żyją w **arkuszu Google „Kosztorys budowy”** – prowadzi go inwestor, to jedyne źródło prawdy dla kwot.
Wydatki trafiają do niego przez **kolejkę w Notion „💸 Wydatki → arkusz”**: asystent dodaje wiersz, a skrypt
`tools/wydatki.py` na Macu po każdym przebiegu Dziennika dopisuje go do arkusza (bez AI). Jak to działa i jak
skonfigurować: `docs/wydatki-arkusz.md` w repozytorium harnessu. Asystent:
- nie pisze do arkusza bezpośrednio i nie trzyma własnej kopii kwot (żadnych JSON-ów, „zapamiętanych” liczb z rozmów),
- do analiz czyta kopię `.xlsx` (niżej), a strukturę arkusza zmienia tylko na wyraźną prośbę (sekcja C).

Układ arkuszy i kolumn: `references/arkusze.md`. Pola bazy 💸 Wydatki: `notatka/references/notion-schematy.md`.

## Gdzie są liczby

- **Claude Code:** `Koszty/Kosztorys_google.xlsx` w folderze budowy – kopia arkusza, odświeżana co wieczór; świeżą
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
   plan i wydane. Na końcu 3 największe odchylenia z komentarzem i suma wydatków stanu zero bez typu (psuje podział).

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
   wysłany przez pomyłkę – w Claude Code `python3 tools/wydatki.py wycofaj <id strony>` (czyści Wydatki i Cennik).
7. Wydatek z ilością automat dopisuje też do arkusza Cennik (cena za jednostkę) – nie podawaj go osobno.

Zakup z listy 🧱 Zakupy budowy: najpierw `zakupy` (Status, dostawa), potem ten wydatek.

## C. Zmiana w arkuszu (pozycja, kolumna, formuła)

1. Opisz zmianę i jej wpływ (które arkusze i formuły) – przy większych poczekaj na „ok”.
2. Arkusz jest online – asystent nie edytuje go sam. Prosta zmiana (nowa pozycja, nowa kwota PLAN) → instrukcja krok po
   kroku dla inwestora (arkusz, wiersz, co wpisać, które formuły skopiować z wiersza wyżej). Nowa pozycja trafi na listę
   w Notion przy wieczornym `wydatki.py pozycje` (od razu: uruchom je w Claude Code).
3. Przebudowa → nowy plik `.xlsx` na kopii (openpyxl, bez utraty formuł, walidacji, formatowania warunkowego), przeliczony
   w LibreOffice bez błędów (#REF!, #NAME?, #VALUE!, #DIV/0!, #N/A), zgodny z Arkuszami Google (SUMIFS, INDEX/MATCH, IF,
   bez formuł tablicowych). Inwestor importuje go od nowa; przypomnij o ponownym wklejeniu kodu Apps Script i wdrożeniu
   (`docs/wydatki-arkusz.md`, sekcja 3, kroki 3–7) – adres wdrożenia się zmieni.
4. Kolumny A–O arkusza Wydatki, kolumny A, B, M arkusza Kosztorys i nazwy tych arkuszy czyta automat – zmiana ich kolejności
   albo nazw wymaga zmiany `tools/wydatki.py` i kodu Apps Script w tym samym kroku.
5. Oddaj plik albo instrukcję + krótką listę zmian (arkusz, zakres, co).

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
- Ceny jednostkowe zakupów: arkusz Cennik – wydatki z ilością dopisuje automat, resztę (np. oferty hurtowni) inwestor.
- Wiedza o kosztach z filmów trafia do Informacji w Bazie wiedzy (procedura `wiedza`, Rodzaj „Koszt / cena”,
  „Wrażliwe na czas”), a do arkusza tylko na prośbę inwestora.
