---
name: dziennik
description: Dziennik inwestora – wpis z budowy po każdym dniu pracy lub wizycie (co zrobiono, kto był, pogoda, dostawy, godziny własne, problemy, ustalenia z ekipą, roboty dodatkowe, zdjęcia) do Notion „Dziennik budowy”. Używaj, gdy użytkownik relacjonuje dzień na budowie („dziś na budowie…”, „ekipa zrobiła…”, „byłem na działce”, „przyjechał beton”), wysyła zdjęcia z budowy, podaje swoje godziny pracy, mówi o problemie lub usterce, o robotach dodatkowych („ekipa chce dopłatę za…”), albo pyta „co się działo w zeszłym tygodniu”.
---

# Dziennik budowy (inwestora)

Cel: każdy dzień na budowie zostawia ślad, który po roku pozwala odpowiedzieć: co, kiedy, kto, za ile, w jakich
warunkach i gdzie są zdjęcia. To podstawa przy sporze z ekipą, gwarancji, rozliczeniu pracy własnej i przy
przeglądzie tygodnia. Dziennik inwestora nie zastępuje dziennika budowy prowadzonego przez kierownika.

Baza i pola: `references/notion-dziennik.md`. Zdjęcia: folder budowy `Zdjęcia/RRRR-MM-DD_<etap-krok>/`
(skrypt dokumentów pomija ten folder – zdjęcia nie trafiają do paczki ani do indeksu).

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
   | usterka do poprawy, rzecz do zrobienia z terminem | `notatka` – TASKS (When), Do kogo = Ekipa |
   | „ekipa chce dopłatę za…” (roboty dodatkowe) | sekcja B |
   | koniec kroku / etapu, „jutro betonujemy” | `etap` – odbiór albo bramka; Harmonogram – Status kroku (W trakcie / Zrobione) |
   | przesunięcie, opóźnienie ekipy, nowy termin | `harmonogram`, sekcja C |
   | wiedza od wykonawcy („mówi, że…”) | `wiedza` (Rozmowy i źródła), jeśli to coś więcej niż ustalenie na dziś |
3. **Zdjęcia:** podaj docelowy folder i nazwy (`RRRR-MM-DD_<krok>_<co>.jpg`); we wpisie zapisz ścieżkę folderu i listę
   ujęć. Jeśli krok zakrywa coś na stałe (zbrojenie, izolacja, instalacje, trasy w zasypce) – sprawdź, czy są zdjęcia
   z miarą; brak → przypomnij **zanim** będzie za późno (procedura `etap`, sekcja B). Pole „Przed zakryciem OK”
   zaznacz tylko, gdy zdjęcia zakrywanych elementów są zrobione; inaczej zostaw odznaczone i wymień to w podsumowaniu.
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
- Zakup lub wynajem narzędzi → `koszty` (Typ „Sprzęt”, etap 16 lub etap, dla którego kupiono).
- Wypadek, zagrożenie, praca na wysokości / w wykopie bez zabezpieczeń → zapisz jako Ryzyko Krytyczne i powiedz wprost.

## D. „Co się działo” (pytanie o okres)

Pobierz wpisy z okresu jednym zapytaniem; odpowiedz chronologicznie: dni pracy ekipy / własne, postęp per krok,
dostawy i koszty gotówkowe, otwarte problemy, zdjęcia (foldery). Nie interpretuj ponad to, co w wpisach.

## Wynik w rozmowie

```
**Dziennik <data> – <etap / krok>**: ekipa <n> os. / ja <h> h | pogoda: … | dostawy: …
Zrobione: … | Problemy: … | Ustalenia: …
Zdjęcia: Zdjęcia/<folder>/ (<n> ujęć) – brakuje: …
Przekazane: koszty <n> wierszy | notatnik <n> | zadania <n> | etap: …
```

## Zasady

- Jeden dzień / jedna wizyta = jeden wpis; dopisek tego samego dnia → aktualizuj wpis, nie twórz drugiego.
- Pisz, co widziałeś i co powiedziano – oceny techniczne oddzielnie (`[opinia]`) i tylko na prośbę.
- Nie zapisuj kwot wyłącznie w dzienniku – każda zapłacona kwota idzie też do kolejki „💸 Wydatki → arkusz” (`koszty`, sekcja B).
- Zdjęcia nigdy do repozytorium ani do paczki dla claude.ai.
