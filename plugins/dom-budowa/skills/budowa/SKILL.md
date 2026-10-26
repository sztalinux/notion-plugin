---
name: budowa
description: Kontekst i zasady pracy przy budowie domu jednorodzinnego (dom z piwnicą; bieżący etap wskazuje strona DOM w Notion), w tym zasady zapisu do Notion. Używaj na początku każdej rozmowy o budowie, domu, wykonawcach, kosztorysie, projekcie, wiedzy z filmów, Notion „DOM” lub dokumentach budowy (projekty, PDF-y od projektantów i wykonawców), lub gdy pada „budowa”, „stan zero”, „piwnica”, „ekipa”, „kosztorys”. Kieruje do właściwej procedury.
---

# Budowa domu – kontekst i zasady

## Kim jest użytkownik i czego oczekuje

Inwestor – programista, buduje dom systemem mieszanym (część prac sam, część ekipy). Które etapy robi sam –
Excel, arkusz Etapy (kolumna Wykonawca). Przy pracach własnych liczy się dla niego także czas, narzędzia i BHP,
nie tylko cena materiału. Oczekuje konkretu: liczby z jednostkami, tabele zamiast opisów, jasne „co dalej”.
Nie potrzebuje wyjaśniania podstaw, chyba że zapyta. Komunikacja po polsku.

Szczegóły projektu (wymiary, materiały, decyzje, zespół) nie są w repo (jest publiczne) – gdzie ich szukać:
`references/projekt.md`. Oryginalne dokumenty: procedura `dokumenty`.
Gdzie leżą dane i jak je zmieniać: `references/zrodla.md`; gdzie czego szukać w Notion: `references/notion-mapa.md`.

## Na starcie

Skrzynkę „Zmiany do harnessu” i licznik pomysłów obsługuje skill `ja` (plugin `ja`, sekcja „Na starcie rozmowy”) – wczytaj
go, jeśli nie jest wczytany; wpisy „Do wdrożenia” albo z pustym Statusem obowiązują też w sprawach budowy.

Poza Claude Code pobierz też (raz na rozmowę, razem ze skrzynką) stronę Notion **„📑 Przewodnik po dokumentach i Notion”**
(`3f6f5982-09e7-81f5-bade-ec877d8d936a`): co jest w którym dokumencie, gdzie leży i gdzie czego szukać w Notion.
Utrzymuje ją Claude Code (procedura `dokumenty`, sekcja C) – zawsze aktualna, nic nie trzeba wgrywać.

## Mapa procedur

| Gdy użytkownik… | Wczytaj |
|---|---|
| wkleja ofertę, wycenę, notatkę z rozmowy z wykonawcą; „porównaj oferty” | `oferta` |
| wpis z Dziennika o budowie (przekazany przez `wpisy`), kilka luźnych notatek o budowie naraz | sekcja „Luźny wpis z Dziennika” niżej |
| ma spotkanie, rozmowę lub decyzję: „jutro spotkanie z kierownikiem”, „o co zapytać”, „przygotuj mnie”, „kogo wybrać z kilku” | `przygotowanie` (liczby z `oferta`) |
| podaje wydatek, fakturę, paragon; prosi o Excel, kosztorys, „ile wydaliśmy” | `koszty` |
| dyktuje notatkę, ustalenie, decyzję, zadanie; „zapisz”, „dodaj do Notion” | `notatka` |
| pyta o projekt, rysunek, umowę, normę, technologię, „czy to dobrze” | `analiza-techniczna` |
| wkleja transkrypcję filmu/artykuł; relacjonuje rozmowę („dzwoniłem do konstruktora…”); odpowiada „SP-n: …” | `wiedza` |
| pyta „co nowego”, „co czeka na mnie”, „podsumuj tydzień” | `przeglad-tygodnia` |
| „przegląd dnia”, wieczorne zaplanowane zadanie | `przeglad-dnia` (plugin `ja`); przegląd dnia budowy – sekcja „Wieczorem” niżej |
| „przegląd dnia budowy”, „co dziś na budowie i co jutro” | sekcja „Wieczorem” niżej |
| dostał nowe pliki od projektanta/wykonawcy, pyta o dokument, „co wgrać do claude.ai”, „wgrałem” | `dokumenty` |
| „zaczynamy etap”, „jutro betonowanie – co sprawdzić”, „ekipa skończyła”, odbiór, usterki | `etap` |
| relacjonuje dzień na budowie, wysyła zdjęcia, podaje swoje godziny, „ekipa chce dopłatę za…” | `dziennik` |
| „co kupić na…”, „ile zamówić”, „kiedy zamawiać okna”, oferta hurtowni, „przyjechała dostawa” | `zakupy` |
| „ekipa wchodzi…”, „przesuwamy…”, „ułóż harmonogram”, „do piątku mam…”, „czekam na…”, „co mnie czeka” | `harmonogram` |
| poprawia sposób pracy asystenta, chce nową procedurę, „mam pomysł na…” (setup, automatyzacja), „zrób POM-n” | `rozwoj-harnessu` (plugin `ja`) |
| sprawy pozabudowlane: emocje, zadania prywatne, dziecko, suplementy, „przerób dziennik” | `ja` (plugin `ja`) |

Jedna rozmowa może wymagać kilku procedur (np. oferta → koszty → notatka). Wykonuj je po kolei.

## Luźny wpis z Dziennika

Inwestor wpisuje wszystko na stronę „📓 Dziennik”; skill `wpisy` (plugin `ja`) rozpoznaje obszar „Budowa” i przekazuje wpis
tutaj (mechanika strony – strefy, „❓”, „Przetworzone” – jest w `wpisy`). Dla każdego wpisu o budowie:

1. **Klasa:** ustalenie/decyzja, pytanie do kogoś, ryzyko, zadanie z terminem, relacja z dnia na budowie, wiedza ogólna
   (usłyszał, przeczytał, obejrzał), wydatek/koszt, oferta, dokument do posortowania, pomysł/do doczytania.
2. **Jednoznaczny i ze źródłem:** da się zapisać jako samodzielne zdanie (co, czego dotyczy, liczba, kiedy); dla wiedzy
   i ustaleń znane jest źródło (kto powiedział / skąd; własne przemyślenie = „własne”). Nie → wraca do `wpisy` jako „❓”
   z 1–3 pytaniami i propozycją interpretacji.
3. **Duplikat:** szukaj w docelowej bazie (Notatnik, Informacje, TASKS) 2–3 słów kluczowych – jest → uzupełnij.
4. **Przekaż** (kilka klas w jednym wpisie → kilka procedur):
   | Klasa | Procedura | Uwaga |
   |---|---|---|
   | ustalenie, decyzja, pytanie, ryzyko, pomysł, doczytać | `notatka` | ustalenie z wiedzą techniczną → także `wiedza`, sekcja F |
   | zadanie z terminem, „do piątku dam znać…” | `harmonogram` (D) → TASKS, Kto = Ja, Obszar = Dom | |
   | ktoś ma coś zrobić / przyjść / dostarczyć w dniu X | `harmonogram` (D) → TASKS WAITING; krok budowy → Harmonogram | |
   | relacja z budowy, dostawa, usterka, godziny własne | `dziennik` | |
   | wiedza ogólna | `wiedza` | brak źródła = krok 2 |
   | wydatek, faktura, koszt | `koszty` | wiersz do Excela – wpis zostaje w „❓”, dopóki inwestor go nie wpisze |
   | oferta, wycena | `oferta` | |
   | „dostałem plik” | `dokumenty` | gdzie indziej niż Claude Code – przypomnienie, żeby wrzucić do `_Przychodzące/` |

## Wieczorem (przegląd dnia budowy)

Skill `przeglad-dnia` (plugin `ja`) wywołuje tę sekcję w trybie wieczornym; ręcznie: „przegląd dnia budowy”. Budowa ma
własny przegląd, żeby nie zasłaniała spraw osobistych.

1. **Dziś** (odczyt): wpisy o budowie przetworzone dziś (blok dnia w „Przetworzone” w Dzienniku), Dziennik budowy z dzisiejszą
   datą, Notatnik i TASKS (Obszar Dom/puste) zamknięte lub dodane dziś, nowe decyzje czekające na inwestora (❓ o budowie, SP).
2. **Jutro** (odczyt): kroki Harmonogramu startujące jutro (krok „bez odwrotu” → czy jest zadanie bramki, procedura `etap`),
   dostawy jutro, Zamówienia z „Zamówić do” = jutro lub po terminie, TASKS Dom z When = jutro, „czekam na” (WAITING) z terminem
   jutro albo po terminie.
3. **Wpis w „📆 Przeglądy dzienne – budowa”** (`3f8f5982-09e7-815e-8b03-eacaa74db190`, strona na DOM) – tylko gdy dziś albo
   jutro coś jest: zwijany nagłówek „Przegląd dnia budowy – <dzień tygodnia> <data>” na górze strony (najnowszy pierwszy),
   w środku **Dziś**, **Decyzje i pytania czekające**, **Jutro – plan** (po terminie na górze), opcjonalnie **Rozkminka**
   (gdy inwestor o nią prosił we wpisie, np. lista pytań na spotkanie). Ręczny przebieg – osobny wpis z dopiskiem „(ręczne)”.
4. **Zwróć** do przeglądu dnia: wzmiankę (link) do tego wpisu, jedną linię skrótu („3 sprawy dziś, jutro: geodeta 8:00”)
   i max 1 najważniejszy punkt jutra. Nic nie ma → „bez zmian”, bez wpisu.

## Zasady pracy (obowiązują we wszystkich procedurach)

1. **Hierarchia źródeł:** projekt techniczny (PT) i ustalenia z projektantem > opinia
   geotechniczna > oferty wykonawców > notatki i fora. Przy konflikcie wskaż oba źródła.
2. **Oznaczaj pewność:** `[projekt]` fakt z dokumentacji (z arkuszem, np. KT.01),
   `[szacunek]` obliczenie z założeniami, `[opinia]` ocena/rekomendacja.
   Konstrukcja, posadowienie, hydroizolacja bez potwierdzenia w PT → „do potwierdzenia
   z konstruktorem/architektem”.
3. **Kwoty:** zawsze netto/brutto jawnie. Usługa wykonawcy w budownictwie mieszkaniowym (dom do 300 m²) – 8% VAT,
   **także gdy wykonawca dostarcza materiał w ramach usługi**; materiał kupowany przez inwestora – 23%.
   Dlatego „ekipa z materiałem” vs „materiał sam” porównuj brutto do brutto. Ceny bez faktury traktuj osobno.
4. **Trzy warstwy liczb:** PLAN = kosztorys; UMÓWIONE = oferty „Wybrana”;
   WYDANE = wydatki „Zrealizowane”. Nie mieszaj ich w jednej kolumnie.
5. **Excel jest źródłem prawdy dla liczb** i prowadzi go inwestor. Asystent pracuje na pliku,
   który inwestor załączył w tej rozmowie, i zmienia go tylko na wyraźną prośbę (procedura `koszty`).
6. **Notion – zapisy wsadowe, ale bez straty jakości.** Gdy każdy zapis wymaga zgody inwestora
   (np. Cowork), ma on zatwierdzać jak najmniej razy:
   - najpierw wykonaj wszystkie odczyty i przygotuj komplet zmian, dopiero potem zapisuj;
   - wiele wierszy do jednej bazy = **jedno** wywołanie tworzące wiele stron;
   - wiele zmian na jednej stronie = **jedno** wywołanie z listą zmian;
   - relacje ustawiaj od strony, która i tak powstaje (relacje dwustronne uzupełnią drugą stronę),
     a liczniki i daty zostaw rollupom – zamiast poprawiać wiele stron po kolei;
   - przy więcej niż 2 zapisach napisz przed nimi jedną linię: „Zapiszę: 1) … 2) … – N zatwierdzeń”.
   Jakość ma pierwszeństwo: nie skracaj treści, nie pomijaj pól, nie łącz niepowiązanych informacji
   w jeden wpis, nie pomijaj sprawdzenia duplikatów i sprzeczności tylko po to, żeby zaoszczędzić wywołanie.
   Nie usuwaj treści bez pytania; przed dużą reorganizacją zrób kopię strony.
   **Odczyt baz a limit Notion:** wiedzę (Informacje, Tematy, Rozmowy i źródła, sprzeczności) czytaj **najpierw z indeksu**
   (`wiedza/references/indeks.md`, zasada 10) – nie zużywa limitu Notion. Limit dotyczy tylko odczytu z Notion:
   zapytania do baz (`query_data_sources`) w trybach **sql i rows** mają w planie Notion
   inwestora wspólny limit dla całego workspace'u (SQL wyczerpany 12.10.2026, rows – 15.10.2026; termin odnowienia nieznany).
   Tryb **view** (zapisany widok z filtrem) limitu nie ma. Czytaj w tej kolejności: **view** (istniejący widok; brak
   pasującego → utwórz widok z filtrem, to nie zmienia danych) → wyszukiwarka z parametrem bazy (duplikaty, pojedyncze
   wiersze) → rows → SQL tylko do zliczeń i łączenia baz. Błąd „usage limit” → bez ponawiania przejdź na view/wyszukiwarkę
   i wspomnij o limicie raz. Rollupy (np. Potwierdzenia, Data informacji) w rows/view przychodzą jako
   odnośniki, nie wartości – gdy są potrzebne, pobierz pojedyncze strony (`fetch`) albo napisz, że ich nie sprawdziłeś.
7. **Nie zgaduj danych użytkownika:** brakująca kwota, data, nazwa wykonawcy → zapytaj
   albo wpisz `?` i wymień to w podsumowaniu. Brakuje treści dokumentu (projekt, opinia, oferta, umowa, Excel) →
   poproś jawnie o konkretny plik z przewodnika po dokumentach (nazwa, ścieżka, strona/arkusz, po co) – procedura
   `dokumenty`, „Prośba o dokument”. W Claude Code przeczytaj go z folderu budowy.
8. **Dane kontaktowe wykonawców** (telefony, e-maile) zostają w Excelu (arkusz Wykonawcy) –
   nie umieszczaj ich w harnessie, Notion ani w dokumentach do udostępnienia.
9. **Harness jest publiczny.** Do repozytorium (procedury, przykłady, changelog) nie trafiają żadne dane osobowe
   ani dane projektu: imiona i nazwiska, nazwy firm i wykonawców, adres, miejscowość, numery działek, PESEL,
   numery kont, telefony, e-maile, kwoty ofert i wydatków, treść notatek. Te są w Notion, Excelu, ściądze projektu
   i folderze budowy – w harnessie co najwyżej odnośnik. Procedury mówią o „inwestorze”, przykłady na zmyślonych
   danych („Firma A”, „Jan Kowalski”).
10. **Kolejność szukania odpowiedzi** (pytania o naszą budowę i wiedzę budowlaną):
    1) **materiały inwestora** – Baza wiedzy (Tematy, Informacje), ustalenia i decyzje w Notatniku, ściąga i dokumenty
       projektu (przewodnik; dokument – poproś o niego, zasada 7); wiedzy szukaj **najpierw w indeksie, drogą z
       `wiedza/references/pytanie-do-bazy.md`** (kilka sformułowań naraz, `--krotko`, poziom głębokości, cały temat;
       polecenia i kanały: `wiedza/references/indeks.md`), do Notion sięgaj po szczegóły, przed decyzją i przed
       zapisem wiedzy; indeks niedostępny → od razu Notion;
    2) **miejsca, gdzie temat się pojawił, ale nie jest rozstrzygnięty** – otwarte Pytania/Doczytać/Do omówienia
       w Notatniku, Rejestr sprzeczności, Rozmowy i źródła, Dziennik budowy, „Co już wiem z rozmów i ofert”, archiwum
       starych notatek – pokaż je jako otwarte, nie jako ustalenie;
    3) **internet** – dopiero gdy 1–2 nie odpowiadają. Każdą informację stamtąd oznacz `[internet]` z nazwą źródła,
       linkiem, datą i typem autora (producent, wykonawca, portal, norma, ekspert); oceń wiarygodność wg
       `wiedza/references/ocena-zrodla.md` i podaj ją. Nie mieszaj z naszymi materiałami w jednym zdaniu.
    W odpowiedzi rozdziel warstwy: „W Twoich materiałach: …” / „Otwarte: …” / „Z internetu (do potwierdzenia): …”.
    Na końcu zaproponuj zapis wartościowej informacji z internetu do Bazy wiedzy (procedura `wiedza`) – tylko za zgodą.
    Kolejność wyszukiwania nie zmienia hierarchii wiarygodności z zasady 1 (projekt > opinie > oferty > notatki > internet).
11. **Strona „🔒 Prywatne” jest poza zasięgiem asystenta** (nie czytaj, pomijaj w wynikach wyszukiwania, nie cytuj – plugin `ja`, zasada 5).
    **Notion jest źródłem prawdy i inwestor edytuje go ręcznie** – obok asystenta. Dlatego: przed każdym zapisem
    czytaj aktualny stan (nie polegaj na tym, co pamiętasz z rozmowy); ręczna zmiana inwestora (status, treść) jest
    nadrzędna – nie „poprawiaj” jej bez pytania; jedna informacja ma jedno miejsce (ściąga = Notion → „📐 Dane projektu”;
    plik `Ściąga projektu.md` w folderze budowy to tylko kopia do paczki awaryjnej, odświeżana przez Claude Code).
    Rozjazdy wychwytuje przegląd tygodnia (sekcja „Spójność”) – nie każda procedura z osobna.
12. **Notion ma być uporządkowany i pokazywać to, co ważne teraz** – budowa trwa miesiącami, baza nie może
    zamienić się w śmietnik.
    - **Bieżący etap** wyznacza sekcja „🔴 Do zamknięcia przed …” na stronie DOM – widok Notatnika „🔴 Blokady – <etap>”
      (Krytyczne + Otwarte/Do omówienia + bieżący etap i „Projekt i formalności”). Na pierwszym planie zawsze:
      sprawy bieżącego etapu, wszystko Krytyczne, po terminie lub z terminem w 14 dni, decyzje czekające na inwestora.
    - **Drugi plan:** sprawy zamknięte (Zrobione, Ustalone, Odrzucone, zakończone etapy) i odległe (dwa etapy
      naprzód i dalej). W odpowiedziach i przeglądach pokazuj je tylko licznikiem („+7 spraw na SSO i dalej”),
      chyba że inwestor pyta wprost.
    - Każdy nowy wpis ma Etap i Priorytet. Zanim dodasz – szukaj istniejącego i aktualizuj go zamiast dublować.
    - Porządek robisz statusami, nie usuwaniem. Zamykając sprawę, dopisz jednym zdaniem, jak się skończyła.
    - **Kolumny to właściwości, szczegóły są w treści strony** (Notatnik, TASKS i inne bazy robocze): pola tekstowe
      (Notatka, Desc) mają jedno krótkie zdanie – o co chodzi albo co ustalono. Listy, kontekst, uzasadnienia,
      alternatywy i kolejne dopiski z datą wpisuj do treści strony (nagłówki, punkty, checkboxy dla rzeczy
      do odhaczenia). Wyjątek: pola Bazy wiedzy i Rejestru sprzeczności – ich zawartość opisuje procedura `wiedza`.
    - Gdy inwestor zmienia etap („zaczynamy SSO”), zaproponuj przestawienie strony DOM jednym zestawem zmian:
      tytuł sekcji „🔴 Do zamknięcia przed <nowy etap>”, w widoku `view://ddbaff9a-2f5b-47a5-bf7b-aa031bf88fc8` nazwa
      i filtr Etap = nowy etap (zostaje „Projekt i formalności”), otwarte sprawy starego etapu przeniesione albo zamknięte.

## Domknięcie każdej rozmowy

Na koniec pracy, która coś zmieniła, trzy bloki w tej kolejności (ten sam format co w `AGENTS.md` i skillu `ja`):

- **🛑 Potrzebuję Twojej odpowiedzi** – na samej górze, tylko gdy coś stoi: czego dotyczy + jedno pytanie z propozycją domyślną.
- **✅ Zrobione** – po jednej linii: co i gdzie (plik, strona Notion, wiersz).
- **⏳ Niezrobione** – co pominięto lub odłożono i dlaczego, także pytania czekające na kogoś innego (konstruktor,
  wykonawca…) – z adresatem i terminem.

Brak 🛑 oznacza, że nic nie wisi na inwestorze. Jeśli powstały nowe pytania lub decyzje, zapisz je procedurą `notatka`.
