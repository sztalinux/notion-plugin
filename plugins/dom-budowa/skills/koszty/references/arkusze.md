# Arkusz „Kosztorys budowy” – układ (stan: 2026-11-08)

Arkusz Google prowadzi inwestor; kopia do analiz: `Koszty/Kosztorys_google.xlsx` w folderze budowy (`tools/wydatki.py
pobierz`). Jeśli arkusz wygląda inaczej niż tu opisano – pracuj na faktycznym układzie i zgłoś aktualizację tego pliku
(procedura `rozwoj-harnessu`). Kolumny czytane przez automat są oznaczone ⚙ – ich kolejności i nazw arkuszy nie zmieniaj
bez zmiany `tools/wydatki.py` i kodu Apps Script (`docs/wydatki-arkusz.md`).

## Arkusze (kolejność)
Instrukcja · Podsumowanie · Wydatki ⚙ · Cennik · Etapy · Kosztorys ⚙ · Szacunek AI 10.2026 (archiwum wartości).

## Etapy
Stan zero = etapy z umowy z ekipą: 01 Przygotowanie i obsługa · 02 Droga dojazdowa · 03 Płyta fundamentowa · 04 Ściany
piwnicy · 05 Izolacje i zasypka · 06 Strop i schody · 07 Rozszalowanie i sprzątanie · 08 Rezerwa i roboty dodatkowe.
Organizacja: P1–P4 (sprzed budowy), 15 Obsługa budowy – kolejne etapy, 16 Narzędzia. Teren: 50 Przyłącza, zbiorniki, zjazd.
Etapy SSO i dalsze dojdą, gdy będą oferty (pełny szacunek całej budowy: `Kosztorys_17.10.2026_v3.xlsx`).

## Kolumny wejściowe (kremowe – wpisuje inwestor albo automat)
- **Wydatki!A:O** ⚙ – A Data · B Status (Zrealizowane / Do zapłaty) · C Kwota brutto · D Etap (lista z Etapy!A) · E Pozycja
  (lista „Lp Nazwa” z Kosztorys!M) · F Typ (Materiał / Robocizna / Sprzęt / Usługa / Formalności) · G Ilość · H Jedn. ·
  I Cena jedn. (formuła – nie nadpisuj) · J Sposób · K Opis · L Dostawca / nr FV · M Notatki · N Kontrola (formuła ⚠ –
  nie nadpisuj) · O Źródło (`notion:<id>` = dopisane z kolejki 💸 Wydatki; stare wiersze – opis z dawnego arkusza Google).
- **Kosztorys!A:M** ⚙ – A Etap · B Lp (np. 03.5) · C Pozycja · D Typ · E Jedn. · F Ilość plan · **G PLAN (zł)** – jedyna
  kolumna planu · H Ilość kupiona (z Wydatków) · I Wydane · J Pozostało · K Zakończono (Tak) · L Uwagi ([umowa] /
  [szacunek AI]) · M Klucz (formuła „Lp Pozycja” – źródło listy w Wydatkach i w Notion).
- **Etapy!A:O** – A Etap · B Stan · C Umowa z ekipą (transza) · D Uwagi / terminy · E–H PLAN: Materiał / Ekipa / Inne /
  razem · I–M WYDANE: Materiał / Ekipa / Inne / Bez typu / razem · N Pozostało · O Do zapłaty ekipie (kolumnę Wykonawca
  inwestor usunął 8.11.2026).
- **Cennik!A:I** – ręczny rejestr cen zakupu: Data, Materiał / usługa, Jedn., Cena jedn. brutto, Dostawca, Ilość, Wartość
  (formuła), Pozycja kosztorysu, Uwagi.
- **Podsumowanie!B** – rezerwa na stan zero (%).

## Trzy warstwy liczb
PLAN = Kosztorys kol. G (sumy w Etapy E–H); UMÓWIONE = Etapy kol. C (umowa z ekipą) i wybrane oferty;
WYDANE = Wydatki „Zrealizowane”; zobowiązania = Wydatki „Do zapłaty” i Etapy kol. O.
Kolory: każdy etap ma własny pastel (pasek w kol. A Kosztorysu i Etapów, kol. Etap w Wydatkach); materiał – brzoskwiniowy,
ekipa – zielony, inne – fioletowy, plan – niebieski, wydane – piaskowy, pozostało – miętowy, zakończone – zielony znacznik w kol. K.
„Ekipa” = Typ Robocizna (transze z umowy, roboty dodatkowe); „Inne” = Sprzęt, Usługa, Formalności.
