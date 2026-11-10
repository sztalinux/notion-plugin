---
name: dziennik
description: Dziennik inwestora – wpis z budowy po każdym dniu pracy lub wizycie (co zrobiono, kto był, pogoda, dostawy, godziny własne, problemy, ustalenia z ekipą, roboty dodatkowe, zdjęcia) do Notion „Dziennik budowy”. Używaj, gdy użytkownik relacjonuje dzień na budowie („dziś na budowie…”, „ekipa zrobiła…”, „byłem na działce”, „przyjechał beton”), wysyła zdjęcia z budowy, podaje swoje godziny pracy, mówi o problemie lub usterce, o robotach dodatkowych („ekipa chce dopłatę za…”), albo pyta „co się działo w zeszłym tygodniu”. Także zdjęcia na Dysku Google: „rozłóż zdjęcia”, „wgrałem zdjęcia”, „gdzie są zdjęcia …”, „cofnij ostatnie rozłożenie”.
---

# Dziennik budowy (inwestora)

Cel: każdy dzień na budowie zostawia ślad, który po roku pozwala odpowiedzieć: co, kiedy, kto, za ile, w jakich
warunkach i gdzie są zdjęcia. To podstawa przy sporze z ekipą, gwarancji, rozliczeniu pracy własnej i przy
przeglądzie tygodnia. Dziennik inwestora nie zastępuje dziennika budowy prowadzonego przez kierownika.

Baza i pola: `references/notion-dziennik.md`. Zdjęcia: Dysk Google `Dom/Zdjęcia/<etap>/<NN krok>/`, pliki
`RRRR-MM-DD_<oryginał>`; inwestor wgrywa z telefonu do folderu kroku albo do `Zdjęcia/_nowe` – rozkładanie, tryby i reguły:
`docs/zdjecia-i-kopia.md` (repo harnessu). W Dzienniku tylko link folderu i liczba – zdjęć nie wstawiaj do treści wpisu.

## A. Wpis z dnia / wizyty

1. **Rozbij relację** na pola wpisu: data, etap, krok, kto na budowie (ekipa – ile osób; ja – ile godzin; kierownik;
   geotechnik; dostawa), co zrobiono (konkretnie: „ściany piwnicy – zbrojenie osi A–C”), pogoda (temperatura,
   opady – ważne przy betonie, murowaniu, zasypce), dostawy (co, ile, od kogo, dokument), problemy, ustalenia z ekipą.
   Brakujące dane → `?` i wymień w podsumowaniu (`budowa`, zasada 7). Nie dopowiadaj faktów.
   Datę względną („dziś”, „wczoraj”) przelicz na datę. Zanim zapiszesz, sprawdź w bazie, czy wpis z tą datą już jest –
   jeśli tak, zaktualizuj go.
2. **Wyłuskaj to, co idzie dalej** (jedno wywołanie na bazę – `budowa`, zasada 6):
   | Co w relacji | Dokąd |
   |---|---|
   | dostawa, zakup, zaliczka, gotówka dla ekipy | `koszty`, sekcja B – wiersze w „💸 Wydatki → arkusz” (Zrealizowane / Do zapłaty) |
   | ustalenie, pytanie, ryzyko, decyzja | `notatka` – Notatnik budowy z Etapem i Do kogo |
   | usterka do poprawy, rzecz do zrobienia z terminem | `notatka` – TASKS (When), Kto = Ekipa |
   | „ekipa chce dopłatę za…” (roboty dodatkowe) | sekcja B |
   | koniec kroku / etapu, „jutro betonujemy” | `etap` – odbiór albo bramka; Harmonogram – Status kroku (W trakcie / Zrobione) |
   | przesunięcie, opóźnienie ekipy, nowy termin, „nie skończyliśmy – jutro kontynuujemy”, „nie robili (deszcz)” | `harmonogram`, sekcja C (pkt 4 – terminy kroków przesuwasz od razu) |
   | wiedza od wykonawcy („mówi, że…”) | `wiedza` (Rozmowy i źródła), jeśli to coś więcej niż ustalenie na dziś |
3. **Zdjęcia:** inwestor wysyła je w rozmowie albo pisze, że wgrał → wskaż folder kroku na Dysku (link z pola „Zdjęcia”
   kroku w Harmonogramie) albo `Zdjęcia/_nowe` z folderem nazwanym, co na nich jest („zbrojenie z miarą”); zdjęcia
   z rozmowy nie trafią na Dysk same. Pola wpisu wypełniasz po rozłożeniu (sekcja E). Jeśli krok zakrywa coś na stałe
   (zbrojenie, izolacja, instalacje, trasy w zasypce) – sprawdź, czy są zdjęcia z miarą (`przed zakryciem/` w folderze
   kroku); brak → przypomnij **zanim** będzie za późno (`etap`, sekcja B).
4. **Zapisz wpis** jednym wywołaniem (pola wg `references/notion-dziennik.md`), potwierdź linkiem i podaj,
   co przekazano do innych procedur.

## B. Roboty dodatkowe i zmiany zakresu

1. Ustal: co, dlaczego (brak w umowie / zmiana projektu / błąd wykonawcy / życzenie inwestora), ile (netto + VAT,
   robocizna / materiał), kto to zgłosił, czy praca już wykonana.
2. Porównaj z zakresem umowy (Oferty „Wybrana”, umowa w folderze budowy, `oferta/references/umowa.md`) –
   jeśli pozycja jest w cenie, napisz to wprost z odwołaniem do punktu umowy.
3. Zasada: **cena uzgodniona na piśmie przed wykonaniem** (SMS/mail wystarczy). Zaproponuj treść wiadomości
   do wykonawcy (co, cena, termin, że wchodzi do protokołu odbioru).
4. Zapis: uzgodniona kwota → PLAN pozycji „Roboty dodatkowe – poza umową” w etapie (instrukcja – `koszty`, sekcja C),
   zapłata → wydatek na tę pozycję (`koszty`, sekcja B); wpis w dzienniku; decyzja → Notatnik (Typ „Decyzja”).

## C. Godziny własne i narzędzia

- Godziny pracy własnej zapisuj we wpisie (liczba, co robiono). Na życzenie podaj sumę za etap – służy do uczciwego
  porównania „sam vs ekipa” (`oferta`, sekcja „Sam czy ekipa”) i do planowania kolejnych etapów.
- Zakup lub wynajem narzędzi → `koszty` (Typ „Sprzęt”, Pozycja z etapu 16 albo z etapu, dla którego kupiono).
- Wypadek, zagrożenie, praca na wysokości / w wykopie bez zabezpieczeń → zapisz jako Ryzyko Krytyczne i powiedz wprost.

## D. „Co się działo” (pytanie o okres)

Pobierz wpisy z okresu jednym zapytaniem; odpowiedz chronologicznie: dni pracy ekipy / własne, postęp per krok,
dostawy i koszty gotówkowe, otwarte problemy, zdjęcia (foldery). Nie interpretuj ponad to, co w wpisach.

## E. Zdjęcia na Dysku – „rozłóż zdjęcia”, ślad w Dzienniku

Rozkładanie `Zdjęcia/_nowe` (konektor Dysku albo skrypt, plan na sucho, dziennik ruchów, cofanie) – wyłącznie wg
`docs/zdjecia-i-kopia.md`, sekcja 8; tam też tryby bez aplikacji/konektora i przypadki brzegowe. Ślad (raport
`python3 tools/zdjecia.py slad <plan>`), jednym wywołaniem na dzień zrobienia (nie wgrania):
- wpis z tego dnia jest → uzupełnij; nie ma → wpis minimalny (Data, Etap, Krok, Zdjęcia); dwa wpisy → ten z pasującym krokiem;
- „Zdjęcia” = `<łącznie> zdj.: <NN Krok> (<n>) <link folderu>; …` – liczba zawsze na początku (czyta ją pulpit);
- „Krok harmonogramu” = kroki, w których przybyły zdjęcia; „Dokumenty z dnia” = linki faktur, WZ, wpisów KB;
- „Ujęcia przed zakryciem” = które ujęcia z listy `etap` B są w `przed zakryciem/`, których brakuje; „Przed zakryciem OK”
  zaznacz tylko przy komplecie, inaczej wymień braki w podsumowaniu.
Ślad dopiero po udanym ruchu pliku; nieudany zapis do Notion ponów przy następnym przebiegu.
„Gdzie są zdjęcia X” → link z pola „Zdjęcia” kroku i liczba plików; „cofnij ostatnie rozłożenie” → `zdjecia.py cofnij`
(plan, „ok”, `--zrobione`) – oba wg `docs/zdjecia-i-kopia.md`, 8.

## Wynik w rozmowie

```
**Dziennik <data> – <etap / krok>**: ekipa <n> os. / ja <h> h | pogoda: … | dostawy: …
Zrobione: … | Problemy: … | Ustalenia: …
Zdjęcia: <n> zdjęć – <NN Krok> (link) | przed zakryciem: brakuje …
Przekazane: koszty <n> wierszy | notatnik <n> | zadania <n> | etap: …
```

## Zasady

- Jeden dzień / jedna wizyta = jeden wpis; dopisek tego samego dnia → aktualizuj wpis, nie twórz drugiego.
- Pisz, co widziałeś i co powiedziano – oceny techniczne oddzielnie (`[opinia]`) i tylko na prośbę.
- Nie zapisuj kwot wyłącznie w dzienniku – każda zapłacona kwota idzie też do kolejki „💸 Wydatki → arkusz” (`koszty`, sekcja B).
- Zdjęcia nigdy do repozytorium, paczki dla claude.ai, artefaktów ani treści wpisu; nie opisuj osób widocznych na zdjęciach.
