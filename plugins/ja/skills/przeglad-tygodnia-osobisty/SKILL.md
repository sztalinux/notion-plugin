---
name: przeglad-tygodnia-osobisty
description: Cotygodniowy przegląd spraw osobistych (zadania, dziecko, praca, emocje, suplementy) i porządki w Dzienniku; uruchamia też przegląd budowy (przeglad-tygodnia, dom-budowa). Używaj, gdy uruchamia go tygodniowy automat na Macu albo użytkownik mówi „przegląd tygodnia”, „podsumuj tydzień”, „jak minął tydzień”, „co mnie czeka w tym / przyszłym tygodniu” (sprawy prywatne), „posprzątaj dziennik”.
---

# Przegląd tygodnia – sprawy osobiste

Cel: raz w tygodniu inwestor widzi w 2 minuty, co się działo poza budową, co zaległo i co go czeka – osobno od budowy,
żeby intensywny tydzień na budowie nie zasłaniał reszty. Budowa ma własny przegląd (`przeglad-tygodnia`, plugin
dom-budowa) na stronie DOM; tu jest do niego jedna linia z odnośnikiem.

Strona wyniku: **„📅 Przeglądy tygodniowe”** pod Dziennikiem (`3faf5982-09e7-81e3-a6af-e3786ca4a074`).
Zaplanowany przebieg: raz w tygodniu (niedziela wieczór) uruchamia go **launchd na Macu** przez `claude -p` – jedyna droga,
zaplanowanych zadań na claude.ai nie używamy; polecenie: „Przegląd tygodnia (skill przeglad-tygodnia-osobisty z pluginu ja)”.
Ręcznie: „przegląd tygodnia”; „co mnie czeka w tym / przyszłym tygodniu” o sprawy prywatne – tylko część „Czeka na Ciebie”
i zadania z terminem w tym zakresie, bez wpisu (sprawy budowy – `harmonogram`, sekcja E).

## Zasady

- Odczyt **tylko przez zapisane widoki i strony** (`ja`, zasada 3 – limit zapytań rows/SQL): widoki „🤖 …” niżej.
- Najtańsze źródło to **7 ostatnich wpisów w „📆 Przeglądy dzienne”** (jedna strona) – zacznij od nich; widoki tylko
  na to, czego tam nie ma.
- Treść emocji i notatek o dziecku zostaje w Notion. Na stronie przeglądu (prywatnej): liczby, średnie i powtarzające się
  wzorce w kilku słowach. W odpowiedzi/logu zadania: same liczby i link.
- Niczego nie rozstrzygaj. Porządki (sekcja D) – w zaplanowanym przebiegu tylko te oznaczone jako „bez pytania”;
  resztę proponuj w przeglądzie.

## Kroki

1. **Budowa** – wczytaj skill `przeglad-tygodnia` (plugin dom-budowa) i wykonaj go; zapisze przegląd budowy na DOM
   („Przeglądy tygodniowe”). Weź link do wpisu, jedną linię skrótu (do decyzji n, terminy 7 dni n) i blok 🔔 porządków budowy
   (`porzadki-budowa-<RRRR-Www>`) – zapisz go w kroku 5 razem z własnym.
2. **Tydzień – sprawy osobiste** (odczyt):
   - „📆 Przeglądy dzienne” – wpisy z 7 dni (co się działo, co zamknięto); przy okazji napraw zepsute nagłówki dni
     (`przeglad-dnia/references/uklad-wpisu.md`, A, „Naprawa raz w tygodniu”) – bez pytania, to tylko format;
   - TASKS widok „🤖 Tydzień – prywatne” (`view://3faf5982-09e7-81b5-ad0a-000c1cfabfa0`): zamknięte w tygodniu, po terminie
     (tylko Deadline ☑ i „czekam na” – WAITING, Kto ≠ Ja; orientacyjne po dacie – sam licznik, `zadania`, „Termin twardy czy orientacyjny”),
     z terminem w 7 dni (osobno Prywatne / Dziecko); SOMEDAY tylko licznikiem;
   - praca – baza 🔨 TASKS na 💼 WORK, widok „🤖 Plan dnia – otwarte i zamknięte w 7 dni” (ID w `ja/references/notion-mapa.md`):
     zamknięte w tygodniu i z terminem w 7 dni (baza nie ma pola Deadline – praca nie bywa „po terminie”);
   - Wpisy emocji widok „🤖 Ostatni tydzień” (`view://3faf5982-09e7-81ec-83af-000c8b518d37`): liczba wpisów, najczęstsze
     emocje, średnia intensywność, powtarzające się triggery i potrzeby (kilka słów, bez cytatów);
   - Dziennik produktywności widok „🤖 Ostatni tydzień” (`view://3faf5982-09e7-81af-9ea1-000cbe3dd643`): dni zapisane,
     średnia ocena, najczęstsze przeszkadzajki;
   - strona dziecka: nowe punkty w „💬 Do przegadania” i „🎁 Prezenty” z tygodnia (licznik + tytuły tematów);
   - zadania rozmowy („Porozmawiać / Pogadać / Rozmowa” w nazwie, Obszar Dziecko lub Prywatne) zamknięte w tygodniu a temat nadal na liście „💬 Do przegadania” – pytania 🔔 z kluczem `KS-R…`
     (`przeglad-dnia/references/kontrola-spojnosci-rozmowy.md`; jedyne miejsce tej kontroli – nocny przegląd stosuje tylko odpowiedzi; licznik, bez treści tematów);
   - strona „💍 Wesele”: nowe punkty i zadania „Wesele:” z terminem w 30 dni;
   - Suple: Buy = tak (licznik, nazwy);
   - Zakupy: 🛒 Zakupy „Do kupienia” (licznik, najstarsze) i z Terminem w 7 dni (wymień).
3. **Dziennik i harness** (odczyt): wpisy z okienkiem ❓ we „Wpisach” i bloki 🔔 starsze niż 7 dni bez odpowiedzi (poza blokami `ZP-n`; wymień wpis i pytanie – sprawy budowy
   tylko licznikiem, są w przeglądzie budowy); widok „📥 Zasady do wdrożenia” (Rodzaj Zasada) – wpisy do wdrożenia starsze niż 7 dni
   (przypomnienie: napisz „wdróż” w Claude Code). **Kontrola spójności pomysłów (grupa P)** – widok „🤖 Pomysły – kontrola
   wersji” (kilka wierszy) wg `przeglad-dnia/references/kontrola-spojnosci-pomysly.md`: wersję uzupełniasz tylko z nagłówka
   CHANGELOG, Status zmienia dopiero ☑ inwestora (blok 🔔 `KS-P…`, stosuje nocny przegląd). Pierwszy przegląd
   w miesiącu (dzień ≤ 7): strona „📘 Instrukcja obsługi” (ID w `ja/references/notion-mapa.md`) – sekcje z linią „Stan:”
   starszą niż 60 dni wymień w „Czeka na Ciebie” („Instrukcja: n sekcji do sprawdzenia – …”); tokeny z datą ważności
   w sekcji „Utrzymanie” wygasające w 30 dni – też tam. W tym samym przebiegu nadpisz kopię offline `AI/Instrukcja obsługi.md`
   w folderze budowy treścią pobranej strony (jedyne odświeżenie kopii; bez dostępu do plików → „kopia instrukcji: do odświeżenia”).
   **Zdjęcia, kopie i jakość wiedzy (bez zmian w Notion i w repo):** `python3 tools/zdjecia.py stan` (etap, ostatni przebieg rozkładania zdjęć,
   blokada; liczba plików w `Zdjęcia/_nowe` – `search_files` konektorem Dysku; bez konektora „niesprawdzone”; rozkłada przegląd nocny), `python3 tools/kopia.py stan --cicho` (kopia dokumentów) i `python3 tools/wiedza_jakosc.py przypomnij --cicho` (jedna linia, gdy
   raport jakości czeka; przebieg złoty robi przed przebiegiem sam skrypt automatu – linii „przebieg złoty należny / nie mieści się” nie wpisuj do 🔔, to nie czynność inwestora: powtarza się → Usterka, `rozwoj-harnessu`, D); polecenie niedostępne → „niesprawdzone”. Coś do zrobienia (pliki w `_nowe`, kopia po terminie, alarm jakości) → jeden
   komunikat 🔔 z kluczem `zdjecia-i-kopie` (`wpisy/references/pytania.md`, C; „Co możesz zrobić”: np. „napisz w Claude Code »rozłóż zdjęcia«”); w tygodniowym
   wpisie tylko liczby.
   **Kopie zapasowe:** `python3 tools/kopie.py stan --cicho` (tylko odczyt; brak wyjścia = wszystko aktualne; polecenie
   niedostępne → „niesprawdzone”). Pozycje ⚠/✗ → jeden komunikat 🔔 z kluczem `kopie-zapasowe` we „Wpisach”
   (`wpisy/references/pytania.md`, C; kolejny tydzień – aktualizacja bloku, wszystko ✓ → „ustąpiło”), w okienku
   „Co możesz zrobić”: najpilniejsza pozycja i czynność z `docs/kopie-zapasowe.md`, 4 (repo harnessu), a po kopii
   „powiedz w Claude Code na Macu »zrobiłem …«” – przebieg nie wpisze potwierdzenia (`kopie.py potwierdz` tylko tam).
4. **Wpis w „📅 Przeglądy tygodniowe”** na górze strony, zwijany nagłówek h2 „Tydzień <RRRR-Www> (<data od–do>)”, zapisany wg
   `przeglad-dnia/references/uklad-wpisu.md`, sekcje A–B (`<toggle heading="h2">`; każda etykieta niżej to pogrubiony akapit
   z punktami; najpierw po terminie i czekające; nieudane odczyty jedną linią na końcu):
   ```
   **Po terminie:** zadanie z Deadline – od kiedy → zamknąć, przesunąć czy odpuścić? · czekam na – przypomnij się <komu> · po dacie orientacyjnej: n (bez pytań)
   **Czeka na Ciebie:** n pytań pod wpisami i w 🔔 (najstarsze: …), HZ-x do wdrożenia
   **Zrobione:** 3–6 punktów (prywatne / dziecko / praca)
   **Najbliższy tydzień:** zadania z terminem wg dni, wesele (30 dni), „kupić: n suplementów, n pozycji z zakupów (z terminem: …)”
   **Emocje i praca (liczby):** n wpisów emocji, najczęściej: …, śr. intensywność x; praca: n dni, śr. ocena y; wzorzec: …
   **Dziecko:** n nowych tematów do przegadania, n pomysłów na prezent
   **Kopie:** aktualne / ⚠ n (…) · ✗ n (…) / niesprawdzone
   **🏗 Budowa:** <linia skrótu> → <wzmianka przeglądu budowy z tego tygodnia>
   **Porządki (n):** n propozycji z sekcji D – pytania w 🔔 we „Wpisach” · archiwum: przeniesiono n dni (dd.mm–dd.mm) ·
   naprawione nagłówki: n · spójność: rozmowy n pytań, pomysły n pytań, wersje uzupełnione k (ponad limit 5 flag: +k)
   ```
   Pusty tydzień → krótki wpis „spokojny tydzień” z linią budowy. Ręczny przebieg – osobny wpis z dopiskiem „(ręczne)”.
5. **Porządki bez pytania** (sekcja D, pierwsza lista) – **zawsze, także w zaplanowanym przebiegu**: bloki dni i wpisy
   przeglądów dziennych starsze niż 14 dni do archiwum – zrób to **przed zapisem wpisu z kroku 4**, żeby wpis od razu miał liczbę i zakres dni w linii
   „Porządki” (jedna edycja strony – `ja`, zasada 2; brak takich dni → „archiwum: nic”, także w pustym tygodniu).
   Pozostałe porządki tylko proponujesz: jeden blok 🔔 pod „🔔 Komunikaty asystenta” we „Wpisach” (`wpisy/references/pytania.md`, C.7; klucz `porzadki-<RRRR-Www>`, jedno to-do
   na porządek – max 3, więcej → jedno to-do zbiorcze; lista, warianty i blok z poprzedniego tygodnia – C.7, „Porządki tygodnia”; „zastosuję w nocnym przeglądzie”). Tygodniowy dodaje i aktualizuje bloki **tylko pod nagłówkiem 🔔**, jedną
   punktową edycją „Wpisów” (szybki nie startuje, gdy trwa tygodniowy); listy „Komunikaty z automatów” nie dostaje. Wpis tygodniowy: tylko liczba
   (linia „Porządki”).
6. **Odpowiedź** (log): link do wpisu + liczby, w tym „archiwum: n dni”; bez treści emocji.

## D. Porządki w Dzienniku

Bez pytania (także w zaplanowanym przebiegu – to tylko ślad, linki są w docelowych miejscach):
- bloki dni w „Przetworzone” w Dzienniku starsze niż 14 dni → **przenieś** (nie usuwaj) na podstronę Dziennika
  „🗃 Przetworzone – archiwum” (ID w `ja/references/notion-mapa.md`): najpierw wklej te same zwijane bloki na górę archiwum
  (najnowszy dzień na górze), sprawdź, że są, dopiero potem zdejmij je z Dziennika (jedna edycja każdej strony);
- podstrony w „🗃 Przetworzone podstrony” zostają – nie ruszaj;
- wpisy w „📆 Przeglądy dzienne” starsze niż 14 dni → podstrona „🗃 Przeglądy dzienne – archiwum” (ID w mapie), tak samo
  (najpierw wklej na górę archiwum, sprawdź, potem zdejmij; podstronę archiwum na dole strony zostaw – przy zamianie treści
  przepisz jej znacznik `<page>` bez zmian). Stronę budowy archiwizuje tak samo `przeglad-tygodnia` (porządki).
Do zatwierdzenia (propozycja w przeglądzie):
- wpisy z okienkiem ❓ i bloki 🔔 bez odpowiedzi od 14 dni (poza blokami `ZP-n`) → zamknąć jako „pominięte”, przeformułować pytanie czy zostawić;
- obszar z bazy Obszary, do którego nic nie trafiło od 60 dni → wyłączyć (Aktywny = nie)?;
- wpisy pomijane wielokrotnie z tym samym typem treści → propozycja nowego wiersza w Obszarach;
- TASKS prywatne z Deadline ☑ po terminie od 14 dni → zamknąć / przesunąć / SOMEDAY (propozycja domyślna na pozycję –
  `wpisy/references/pytania.md`, C.7); zadań z terminem
  orientacyjnym nie proponuj przesuwać ani zamykać (`zadania`, „Termin twardy czy orientacyjny”);
Odpowiedź (☑ albo dopisek pod to-do) czyta nocny przebieg (`przeglad-dnia`, B.2; klucz `porzadki-<RRRR-Www>`) – wykonaj wtedy
zatwierdzone porządki wsadowo (`ja`, zasada 2; które – `wpisy/references/pytania.md`, C.7), punkt do „Przetworzone” (wątpliwe zostają w bloku). Niczego innego nie usuwaj. Archiwum tylko do wglądu – nie zapisuj tam nic nowego.
