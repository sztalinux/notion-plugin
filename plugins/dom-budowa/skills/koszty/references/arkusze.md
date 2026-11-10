# Arkusz „Kosztorys budowy” – układ (stan: 2026-11-10)

Arkusz Google prowadzi inwestor i nie jest wgrywany ponownie (zmiany układu: `docs/wydatki-arkusz.md`, sekcja 8); kopia wartości do analiz: `Koszty/Kosztorys_google.json` w folderze budowy (`tools/wydatki.py
pobierz`). Jeśli arkusz wygląda inaczej niż tu opisano – pracuj na faktycznym układzie i zgłoś aktualizację tego pliku
(procedura `rozwoj-harnessu`). Kolumny czytane przez automat są oznaczone ⚙ – ich kolejności i nazw arkuszy nie zmieniaj
bez zmiany `tools/wydatki.py` i kodu Apps Script (`docs/wydatki-arkusz.md`).

## Arkusze (kolejność)
Instrukcja · Podsumowanie · Wydatki ⚙ · Cennik ⚙ · Etapy · Kosztorys ⚙ · Szacunek AI 10.2026 (pełna wycena AI, wartości).

## Etapy
Stan zero = etapy z umowy z ekipą: 01 Przygotowanie i obsługa · 02 Droga dojazdowa · 03 Płyta fundamentowa · 04 Ściany
piwnicy · 05 Izolacje i zasypka · 06 Strop i schody · 07 Rozszalowanie i sprzątanie · 08 Rezerwa i roboty dodatkowe.
Koszty ogólne (stan w Etapy kol. B; do 10.11.2026 „Organizacja”): P1–P4 (sprzed budowy), 15 Obsługa budowy – kolejne etapy, 16 Narzędzia. Teren: 50 Przyłącza, zbiorniki, zjazd.
Etapy SSO i dalsze dojdą, gdy będą oferty; do tego czasu ich koszt pokazuje szacunek AI (zakładka i tabela wg stanów).

## Kolumny wejściowe (kremowe – wpisuje inwestor albo automat)
- **Wydatki!A:O** ⚙ – A Data · B Status (Zrealizowane / Do zapłaty) · C Kwota brutto · D Etap (lista z Etapy!A) · E Pozycja
  (lista „Lp Nazwa” z Kosztorys!M) · F Typ (Materiał / Robocizna / Sprzęt / Usługa / Formalności) · G Ilość · H Jedn. ·
  I Cena jedn. (formuła – nie nadpisuj) · J Sposób · K Opis · L Dostawca / nr FV · M Notatki · N Kontrola (formuła ⚠ –
  nie nadpisuj) · O Źródło (`notion:<id>` = dopisane z kolejki 💸 Wydatki – ponowne wysłanie tej strony poprawia ten wiersz, A:H i J:M; stare wiersze – opis z dawnego arkusza Google).
- **Kosztorys!A:V** ⚙ – A Etap (formuła: wiersz etapu `=Etapy!A<n>`, pozycje `=$A$<wiersz etapu>` – nazwa i stan idą z Etapów;
  nagłówek etapu w C pokazuje „NAZWA · stan”) · B Lp (np. 03.5) · C Pozycja · D Typ · E Jedn. · F Ilość plan · **G PLAN (zł)** – formuła: wybrana
  oferta × ilość plan (kol. P), a bez niej kol. U · H Ilość kupiona (z Wydatków) · I Wydane · J Pozostało · K Zakończono (Tak) · L Uwagi ([umowa] /
  [szacunek AI]) · M Klucz (formuła „Lp Pozycja” – źródło listy w Wydatkach i w Notion) · N Cena wybrana (Cennik kol. G)
  · O Najniższa oferta · P Ilość plan × cena wybrana (podpowiedź do PLAN) · Q–S Szacunek AI: materiał / robocizna / razem
  (razem także ze sprzętem i usługami) · T Kontrola (⚠ etap spoza Etapów, ⚠ brak typu) · U Plan ręczny (kwota PLAN, gdy brak wybranej oferty – wpisuje
  inwestor albo `sync` z kolejki, Rodzaj Plan) · V Materiał (grupa – wspólna oferta z Cennika dla kilku pozycji, np. stal płyty, ścian i stropu). Ceny N–O
  są w jednostce pozycji (oferta za tonę → zł/kg przy pozycji w kg).
- **Etapy!A:R** – A Etap · B Stan · C Umowa z ekipą (transza) · D–G PLAN: Materiał / Ekipa / Inne / razem · H–L WYDANE:
  Materiał / Ekipa / Inne / Bez typu / razem · M Pozostało · N Do zapłaty ekipie · O Uwagi / terminy · P–R Szacunek AI:
  materiał / robocizna / razem (wiersze szacunku przypisane do etapu). Kolumnę Wykonawca inwestor usunął, a Uwagi przeniósł na koniec (7.11.2026) – nowe formuły
  odwołujące się do Etapów buduj po nagłówkach żywego arkusza (`wydatki.py pobierz`), nie po literach z tego opisu.
- **Cennik!A:Q** ⚙ – wyceny dostawców (jeden wiersz = jedna oferta): A Data · B Materiał / usługa · C Jedn. · D Cena (z oferty)
  · E Netto / Brutto · F VAT % (wpis 8 albo 23 = procent; przy netto obowiązkowy, bez niego G = „⚠ VAT?”) · G Cena brutto
  (formuła) · O Cena netto (formuła, na końcu, żeby nie przesuwać kolumn czytanych przez skrypt) · P Materiał (grupa – formuła z pozycji) ·
  Q Cena brutto za jednostkę bazową (t → kg) · H Dostawca ·
  I Pozycja kosztorysu (lista) · J Status (Oferta / Wybrana / Odrzucona) · K Najtańsza (formuła ★, porównanie brutto w obrębie
  pozycji) · L Ważna do · M Uwagi · N Źródło (`notion:<id>` = wycena z kolejki; ponowne wysłanie aktualizuje wiersz).
- **Podsumowanie!B** – rezerwa na stan zero (%). Kol. M–O – szacunek AI etapów stanu zero (materiał / robocizna / razem); tabela H:M
  „Szacunek AI całej budowy wg stanów” (szacunek materiał / robocizna / razem, plan, wydane) i pod nią „Kontrola powiązań”
  (PLAN Kosztorys − Etapy, WYDANE Wydatki − Etapy, liczba ⚠ w Kosztorysie – wszystko powinno dawać 0).
- **Szacunek AI 10.2026!A:L** – A Stan · B Etap (wycena AI) · C Lp · D Pozycja · E Typ · F Ilość · G Jedn. · H Cena · I Wartość AI ·
  J Etap kosztorysu · K Pozycja kosztorysu (J–K: przypisanie, kremowe; uzupełnia asystent) · L Uwagi.

## Trzy warstwy liczb
PLAN = Kosztorys kol. G (sumy w Etapy D–G); UMÓWIONE = Etapy kol. C (umowa z ekipą) i wybrane oferty;
WYDANE = Wydatki „Zrealizowane”; zobowiązania = Wydatki „Do zapłaty” i Etapy kol. N.
Kolory: każdy etap ma własny pastel (pasek w kol. A Kosztorysu i Etapów, kol. Etap w Wydatkach); materiał – brzoskwiniowy,
ekipa – zielony, inne – fioletowy, plan – niebieski, wydane – piaskowy, pozostało – miętowy, zakończone – zielony znacznik w kol. K.
Wydatki: wiersze po dacie, odcień wiersza wg kwoty (do 500 / 500–5 000 / 5 000–50 000 / 50 000+ zł), niebieski = „Do zapłaty”,
żółty = ⚠ w Kontroli; Status, Etap i Typ jako kolorowe pola. Cennik: wybrana oferta – zielony wiersz, odrzucona – szary tekst.
„Ekipa” = Typ Robocizna (transze z umowy, roboty dodatkowe); „Inne” = Sprzęt, Usługa, Formalności.
