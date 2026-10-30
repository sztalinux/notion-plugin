---
name: zakupy
description: Zakupy materiałów i sprzętu na etap (głównie prace własne): lista z kosztorysu z ilościami i zapasem, zapytania do hurtowni, porównanie ofert dostawców, terminy zamówień z wyprzedzeniem, dostawy i stan materiału na budowie. Używaj, gdy użytkownik pyta „co muszę kupić na…”, „ile zamówić”, „zrób listę zakupów”, „porównaj oferty hurtowni”, „kiedy zamawiać okna / stal / dachówkę”, „co zamówić już teraz”, wkleja ofertę składu budowlanego, albo mówi „przyjechała dostawa”.
---

# Zakupy – materiały i sprzęt

Cel: na każdy etap, który inwestor robi sam (i na materiał kupowany przez inwestora dla ekip), jest lista
z ilościami, zapasem, terminem zamówienia i najlepszą ofertą – bez przestoju „bo nie dojechało” i bez trzech
dodatkowych kursów do składu. Liczby wchodzą do Excela (`koszty`), nie do Notion.

Wyprzedzenia zamówień: `references/wyprzedzenia.md`. Układ Excela: `koszty/references/arkusze.md`.

## A. Lista zakupów na etap („co kupić na ściany parteru”)

1. Wczytaj z aktualnego Excela (`koszty`, „Gdzie jest plik”) pozycje Kosztorysu dla etapu: ilość, jednostka, cena,
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
   netto i brutto | uwagi) + zadania „zamówić X do <data>” → TASKS (`notatka`).

**Zapis listy:** pozycje do zamówienia → baza Notion **Zamówienia i dostawy** (`collection://a9854c6c-43ec-4bc1-8ef0-273fb02261c7`):
Pozycja, Ilość, Etap, Krok (relacja do Harmonogramu), Zamówić do, Kto zamawia, Status „Do zapytania” – jednym wywołaniem;
kwoty tylko w Excelu. Terminy „Zamówić do” liczy procedura `harmonogram` (sekcja B), gdy krok ma datę.

## B. Zapytanie i porównanie ofert dostawców

1. Zapytanie ofertowe: lista pozycji z ilościami i jednostkami, producent/klasa (np. klasa betonu komórkowego, gatunek stali,
   grubość XPS, parametr lambda), termin i miejsce dostawy, sposób rozładunku, prośba o cenę netto + VAT, koszt transportu,
   termin ważności oferty i płatności. Podaj gotowy tekst do wysłania.
2. Porównanie (tabela): dostawca | cena jednostkowa netto/brutto | transport | termin | minimalne ilości / opakowania |
   zwroty palet / nadwyżek | razem porównywalne. Wyraźnie: **23 % VAT przy zakupie własnym vs 8 % w usłudze wykonawcy
   z materiałem** (`budowa`, zasada 3) – gdy ekipa oferuje materiał w cenie, porównuj brutto do brutto.
3. Zamienniki (inny producent, gęstość, klasa) tylko z zaznaczeniem i „do potwierdzenia z konstruktorem”, jeśli dotyczą
   konstrukcji lub izolacji przeciwwodnej (`analiza-techniczna`, Granice).
4. Wybrana oferta → wiersze do Excela: Wydatki „Planowane” (data dostawy, kwota brutto, etap, Typ Materiał, dostawca) –
   gotowe do wklejenia (`koszty`, sekcja B).

## C. Dostawa („przyjechało”, „brakuje”)

Aktualizuj wiersz w Zamówieniach: Status (Zamówione → Potwierdzone → Dostarczone / Problem), Dostawa, Rozładunek.

1. Sprawdź z zamówieniem: ilość, asortyment, uszkodzenia, dokumenty (WZ, deklaracja właściwości) → folder budowy (`dokumenty`).
2. Wydatek → `koszty` (Zrealizowane, nr FV); wpis w `dziennik` (dostawy).
3. Braki / nadwyżki: co dokupić (z terminem) albo co zwrócić – zadanie w TASKS.

## Zasady

- Ilości i ceny mają źródło (kosztorys, rysunek, oferta z datą). Ceny rynkowe tylko z widełkami i datą (`koszty`, Zasady).
- Zamawiaj materiał na konkretny krok, nie „na całą budowę” – chyba że cena lub dostępność tego wymaga (wtedy napisz dlaczego).
- Nie zmieniaj materiałów przewidzianych w projekcie bez projektanta.
- Dane dostawców (telefony, e-maile) tylko w Excelu, arkusz Wykonawcy (`budowa`, zasada 8).
