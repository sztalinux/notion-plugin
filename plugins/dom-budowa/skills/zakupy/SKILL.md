---
name: zakupy
description: "Zakupy na budowę – wszystko, co idzie na działkę albo do budynku (materiał, drobnica, narzędzia, wynajem) w bazie 🧱 Zakupy budowy: pojedyncza rzecz „kupić X na budowę”, lista z kosztorysu z ilościami i zapasem, zapytania do hurtowni, porównanie ofert dostawców, terminy zamówień z wyprzedzeniem, dostawy i stan materiału na budowie. Używaj, gdy użytkownik pyta „co muszę kupić na…”, „ile zamówić”, „zrób listę zakupów”, „porównaj oferty hurtowni”, „kiedy zamawiać okna / stal / dachówkę”, „co zamówić już teraz”, wkleja ofertę składu budowlanego, mówi „kupić taśmę / geowłókninę na budowę”, „kupiłem X na działkę” albo „przyjechała dostawa”."
---

# Zakupy – materiały i sprzęt

Cel: na każdy etap, który inwestor robi sam (i na materiał kupowany przez inwestora dla ekip), jest lista
z ilościami, zapasem, terminem zamówienia i najlepszą ofertą – bez przestoju „bo nie dojechało” i bez trzech
dodatkowych kursów do składu. Liczby wchodzą do arkusza kosztorysu (`koszty`), nie do Notion.

Wyprzedzenia zamówień: `references/wyprzedzenia.md`. Układ arkusza kosztorysu: `koszty/references/arkusze.md`.

**Granica z 🛒 Zakupy (plugin `ja`):** wszystko, co idzie na działkę albo do budynku – materiał, drobnica (taśma, kotwy,
folia), narzędzia i sprzęt, wynajem, transport – nawet jedna rolka z marketu → baza **🧱 Zakupy budowy**
(`collection://a9854c6c-43ec-4bc1-8ef0-273fb02261c7`). Mieszkanie, dziecko, praca, sprawy osobiste → 🛒 Zakupy (`zadania`).
Zakupów budowy nie dubluj zadaniem w TASKS – termin trzyma pole „Zamówić do”, a przypomina wieczorny przegląd budowy
(`budowa`, „Wieczorem”).

**Przypomnienie („kupić najpóźniej”).** „Zamówić do” to ostatni bezpieczny dzień zakupu. Wieczorny przegląd budowy zaczyna
przypominać o pozycji przed zamówieniem z wyprzedzeniem wg Rodzaju: **Materiał 7 dni**, **Drobnica 2 dni**, Narzędzia i sprzęt,
Wynajem, Transport i pusty Rodzaj 2 dni. Przy ręcznym „Zamówić do” dla zwykłej drobnicy wpisz datę, do której realnie trzeba kupić –
przypomnienie przyjdzie 2 dni wcześniej. Pozycja bez „Zamówić do” nie przypomina się (nie zgaduj terminu).
Przypomnienie jest linią w przeglądzie dnia, nie powiadomieniem na telefon; pilny zakup „na już” – zadanie z When (sekcja 0).

## 0. Pojedyncza rzecz („kupić X na budowę”, wpis z Dziennika)

1. Sprawdź duplikat wśród niedostarczonych: widok „🛒 Do zamówienia” (tryb view – widzi też wiersze sprzed minut,
   wyszukiwarka ich jeszcze nie zna), wyszukiwarka z parametrem bazy (1–2 słowa) tylko jako dopełnienie; jest → uzupełnij.
2. Nowy wiersz jednym wywołaniem: Pozycja (krótko), Status **Do kupienia** (drobnica, rzecz z marketu lub internetu – bez
   etapu zapytania) albo **Do zapytania** (materiał z hurtowni, betoniarni – sekcja B), Rodzaj, Sposób zakupu, Ilość
   (z jednostką), Specyfikacja (parametr z projektu, gdy dotyczy konstrukcji, izolacji, betonu), Link, Etap, Kto zamawia
   = Ja, Zamówić do – tylko gdy wpis ma termin albo wynika z kroku Harmonogramu (wtedy relacja Krok). Kwoty – nie tutaj.
   Zadanie w TASKS dodaj tylko przy zakupie „na już” (na dziś–najbliższe dni albo blokuje pracę ekipy); w Uwagach zakupu
   wzmianka o zadaniu. Zwykły zakup żyje wyłącznie w 🧱 Zakupach budowy.
3. „Kupiłem X na budowę” → Status **Dostarczone**, Dostawa = data; wydatek → `koszty`, sekcja B (wiersz w „💸 Wydatki → arkusz”);
   materiał z WZ / deklaracją właściwości → sekcja C.1. „Zamówiłem” → Zamówione, Dostawa = umówiony dzień dostawy, gdy
   znany (z niego biorą „dostawy jutro / w 7 dni” przegląd dnia i tygodnia budowy); po dostawie Dostawa = dzień faktyczny.

## A. Lista zakupów na etap („co kupić na ściany parteru”)

1. Wczytaj z kopii arkusza kosztorysu (`koszty`, „Gdzie są liczby”) pozycje Kosztorysu dla etapu: ilość, jednostka, cena,
   kto wykonuje (Sam/Ekipa), cennik. Dla pozycji „Ekipa” sprawdź w ofercie „Wybranej”, czy materiał jest w cenie –
   kupujesz tylko to, co nie jest. Brak pliku → poproś o niego i wypisz, co policzysz po otrzymaniu (pozycje etapu,
   ilości, zapas, terminy zamówień).
2. Uzupełnij o **drobnicę**, której kosztorys zwykle nie ma: z checklist etapu (`etap`), Bazy wiedzy (Rodzaj „Materiał / produkt” – w indeksie
   `szukaj … --rodzaj "Materiał / produkt" --etap …`, `wiedza/references/indeks.md`)
   i praktyki `[opinia]` – np. kotwy, dystanse, folia, taśmy, kleje, siatki, zaprawa do pierwszej warstwy, impregnat,
   paliwo do agregatu. Oznacz, co jest szacunkiem.
3. Policz **ilość do zamówienia** = ilość z kosztorysu (albo z `analiza-techniczna`, jeśli trzeba przeliczyć
   z rysunków) × (1 + zapas). Zapas podaj jawnie (typowo 3–5 % bloczki/płytki, 5–10 % izolacje i folie, stal wg
   zestawienia + cięcie; dachówka wg producenta). Przelicz na jednostki handlowe (palety, rolki, opakowania).
4. **Terminy:** dla każdej pozycji – kiedy ma być na budowie (z planu etapu) minus wyprzedzenie z `references/wyprzedzenia.md`
   = ostatni dzień zamówienia. Pozycje, które trzeba zamówić w ciągu 14 dni, wypisz na górze.
5. **Logistyka:** transport (HDS, wymiary palet, dojazd), gdzie składować (pod dachem / na paletach / zabezpieczenie
   przed deszczem i kradzieżą), co kupić w dwóch dostawach.
6. Wynik: tabela (pozycja | ilość + jednostka handlowa | zapas | kiedy na budowie | zamówić do | skąd / cena orientacyjna
   netto i brutto | uwagi). Zadań „zamówić X do <data>” w TASKS nie zakładaj – terminy są w bazie.

**Zapis listy:** pozycje do zamówienia → **🧱 Zakupy budowy**: Pozycja, Ilość, Rodzaj, Specyfikacja, Sposób zakupu,
Etap, Krok (relacja do Harmonogramu), Zamówić do, Kto zamawia, Status „Do zapytania” (drobnica – „Do kupienia”) – jednym
wywołaniem; kwoty tylko w arkuszu kosztorysu. Terminy „Zamówić do” liczy procedura `harmonogram` (sekcja B), gdy krok ma datę.

## B. Zapytanie i porównanie ofert dostawców

1. Zapytanie ofertowe: lista pozycji z ilościami i jednostkami, producent/klasa (np. klasa betonu komórkowego, gatunek stali,
   grubość XPS, parametr lambda), termin i miejsce dostawy, sposób rozładunku, prośba o cenę netto + VAT, koszt transportu,
   termin ważności oferty i płatności. Podaj gotowy tekst do wysłania.
2. Porównanie (tabela): dostawca | cena jednostkowa netto/brutto | transport | termin | minimalne ilości / opakowania |
   zwroty palet / nadwyżek | razem porównywalne. Wyraźnie: **23 % VAT przy zakupie własnym vs 8 % w usłudze wykonawcy
   z materiałem** (`budowa`, zasada 3) – gdy ekipa oferuje materiał w cenie, porównuj brutto do brutto.
3. Zamienniki (inny producent, gęstość, klasa) tylko z zaznaczeniem i „do potwierdzenia z konstruktorem”, jeśli dotyczą
   konstrukcji lub izolacji przeciwwodnej (`analiza-techniczna`, Granice).
4. Każda oferta → wycena w kolejce (`koszty`, sekcja B2), trafia do arkusza Cennik; wybrana oferta → Status wyceny
   „Wybrana”, pozostałe „Odrzucona”, wszystkie zmienione znów „Do arkusza” (PLAN pozycji przelicza się sam – `koszty` B2, krok 3); zapłata albo faktura → wydatek (`koszty`, sekcja B).

## C. Dostawa („przyjechało”, „brakuje”)

Aktualizuj wiersz w Zakupach budowy: Status (Zamówione → Potwierdzone → Dostarczone / Problem), Dostawa, Rozładunek.

1. Sprawdź z zamówieniem: ilość, asortyment, uszkodzenia, dokumenty (WZ, deklaracja właściwości). Zdjęcie WZ z telefonu →
   `Dostawy/<Etap>/` (`dokumenty`, D); są w folderze → zaznacz „Dokumenty dostawy” i wpisz link pliku w pole „Dokumenty”.
   Z WZ, etykiety albo karty dopisz do Uwag jedną linię „Produkt: producent, typ / klasa, partia” – z niej powstaje sekcja
   „Dostawy i produkty” rozdziału Książki domu (`ksiazka-domu`); osobnej bazy produktów nie ma.
2. Wydatek → `koszty`, sekcja B (nr FV; Płatność „Zrealizowane” tylko po zapłacie – faktura z terminem = „Do zapłaty”, `koszty` D); wpis w `dziennik` (dostawy).
3. Braki / nadwyżki: co dokupić → nowy wiersz w Zakupach budowy (z „Zamówić do”); co zwrócić → Uwagi
   w wierszu dostawy.

## Zasady

- Ilości i ceny mają źródło (kosztorys, rysunek, oferta z datą). Ceny rynkowe tylko z widełkami i datą (`koszty`, Zasady).
- Zamawiaj materiał na konkretny krok, nie „na całą budowę” – chyba że cena lub dostępność tego wymaga (wtedy napisz dlaczego).
- Nie zmieniaj materiałów przewidzianych w projekcie bez projektanta.
- Dane dostawców (telefony, e-maile) tylko w „📇 Kontakty” na DOM (`budowa`, zasada 8).
