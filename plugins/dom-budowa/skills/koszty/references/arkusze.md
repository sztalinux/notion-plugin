# Arkusz „Kosztorys budowy” – układ (stan: 2026-11-26)

Arkusz Google prowadzi inwestor i nie jest wgrywany ponownie (zmiany układu: `docs/wydatki-arkusz.md`, sekcja 8); kopia wartości do analiz: `Koszty/Kosztorys_google.json` w folderze budowy (`tools/wydatki.py
pobierz`). Jeśli arkusz wygląda inaczej niż tu opisano – pracuj na faktycznym układzie i zgłoś aktualizację tego pliku
(procedura `rozwoj-harnessu`). Kolumny czytane przez automat są oznaczone ⚙ – ich kolejności i nazw arkuszy nie zmieniaj
bez zmiany `tools/wydatki.py` i kodu Apps Script (`docs/wydatki-arkusz.md`).

## Arkusze (kolejność)
Instrukcja · Podsumowanie · Wydatki ⚙ · Cennik ⚙ · Etapy · Kosztorys ⚙ · Szacunek AI 10.2026 (pełna wycena AI, wartości).

## Etapy
Przygotowanie do budowy (stan przed stanem zero, od 26.11.2026): 01 Przygotowanie i obsługa – poza sumą stanu zero
i jego rezerwą. Stan zero = etapy z umowy z ekipą: 02 Droga dojazdowa · 03 Płyta fundamentowa · 04 Ściany
piwnicy · 05 Izolacje i zasypka · 06 Strop i schody · 07 Rozszalowanie i sprzątanie · 08 Rezerwa i roboty dodatkowe.
Koszty ogólne (stan w Etapy kol. B; do 10.11.2026 „Organizacja”): P1–P4 (sprzed budowy), 15 Obsługa budowy – kolejne etapy, 16 Narzędzia. Teren: 50 Przyłącza, zbiorniki, zjazd.
Wykończenie: 47 Wyposażenie domu (meble – zakupy na zapas; od 18.11.2026). Numer nowego etapu bierz z zakładki szacunku AI
(wykończenie 40–46, kolejne wolne numery dalej), żeby etap kosztorysu i szacunek się nie gryzły.
Etapy SSO i dalsze dojdą, gdy będą oferty; do tego czasu ich koszt pokazuje szacunek AI (zakładka i tabela wg stanów).
Nową pozycję w istniejącym etapie dodaje automat (pole „Nowa pozycja”, `references/nowa-pozycja.md`), nowy etap – sesja
Claude Code (tamże, C). Zakresy sum (RAZEM KOSZTORYS, Etapy D–G, Podsumowanie „Kontrola powiązań”) kończą się na ostatniej
pozycji arkusza (`$5:$<n>`), Etapy mają formuły w wierszach 5–40 – wiersz wstawiony za ostatnią pozycją arkusza wypada z sum,
więc nowe wiersze idą zawsze wewnątrz bloków. Sumy w nagłówku etapu (`=SUM(G<od>:G<do>)`) poprawia ten, kto wstawia wiersz.
⚙ Teksty, po których automat (akcja nowej pozycji) znajduje kolumny i wiersze: nagłówki „PLAN…”, „Wydane…”, „Klucz…”,
„Kontrola” w wierszu 4 Kosztorysu, „Pozycja” w wierszu 4 Wydatków, „RAZEM KOSZTORYS” w kol. C Kosztorysu, „Kontrola
powiązań” w Podsumowaniu (pod nią trzy wiersze kontroli). Zmiana tekstu = akcja odmawia, dopóki nie zmienisz kodu.

## Kolumny wejściowe (kremowe – wpisuje inwestor albo automat)
- **Wydatki!A:Q** ⚙ – A Data · B Status (Zrealizowane / Do zapłaty) · C Kwota brutto (zwrot – z minusem) · D Etap (lista z Etapy!A) · E Pozycja
  (lista „Lp Nazwa” z Kosztorys!M) · F Typ (Materiał / Robocizna / Sprzęt / Usługa / Formalności) · G Ilość · H Jedn. ·
  I Cena jedn. (formuła – nie nadpisuj) · J Sposób · K Opis · L Dostawca / nr FV · M Notatki · N Kontrola (formuła ⚠ –
  nie nadpisuj) · O Źródło (`notion:<id>` = dopisane z kolejki 💸 Wydatki – ponowne wysłanie tej strony poprawia ten wiersz, A:H, J:M i P; stare wiersze – opis z dawnego arkusza Google) · P VAT % (wpisuje `sync`
  z pola VAT %, ułamek w formacie %) · Q Netto (formuła – nie nadpisuj). Kontrola N nie żąda ilości przy kwocie ujemnej (zwrot).
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
- **Podsumowanie** (od 26.11.2026) – bloki wg stanów w kolejności budowy (dziś: Przygotowanie do budowy, Stan zero,
  Wykończenie): wiersz nagłówka „STAN”, wiersze etapów (`=Etapy!<kol><n>`, te same kolumny co nagłówek w wierszu 5: umowa,
  plan materiał / ekipa / inne, wydane, pozostało, do zapłaty ekipie, szacunek AI), „<Stan> razem”, a w stanie zero
  i wykończeniu także „Rezerwa na <stan>” (B – %, kremowe) i „… z rezerwą”. Koszty ogólne i Teren nie mają bloku. Pod blokami
  „Do zapłaty”, legenda i jedna tabela „Cała budowa wg stanów” (wszystkie stany: PLAN, WYDANE, pozostało, szacunek AI
  materiał / robocizna / razem – SUMIFS po nazwie stanu z Etapy kol. B i z zakładki szacunku). Nowy stan w Etapy kol. B
  wymaga wiersza w tej tabeli i na liście walidacji Etapy kol. B. Pod „Kontrolą danych” (kol. A–C) – „Kontrola powiązań”
  (automat czyta trzy pierwsze wiersze po etykiecie): PLAN Kosztorys − Etapy, WYDANE Wydatki − Etapy, liczba ⚠ w Kosztorysie, potem
  „Stany: tabela − Etapy” i „Bloki stanów − tabela” (suma bloku vs wiersz stanu, łapie etap bez wiersza w bloku) – wszystko 0.
  Wykres pod kontrolami – etapy stanu zero. Styl: nagłówek bloku = podkreślony tytuł, „razem” = jasny szaroniebieski pasek. Dodanie etapu lub bloku: `references/nowa-pozycja.md`, C.2.7.
- **Szacunek AI 10.2026!A:L** – A Stan · B Etap (wycena AI) · C Lp · D Pozycja · E Typ · F Ilość · G Jedn. · H Cena · I Wartość AI ·
  J Etap kosztorysu · K Pozycja kosztorysu (J–K: przypisanie, kremowe; uzupełnia asystent) · L Uwagi.

## Trzy warstwy liczb
PLAN = Kosztorys kol. G (sumy w Etapy D–G); UMÓWIONE = Etapy kol. C (umowa z ekipą) i wybrane oferty;
WYDANE = Wydatki „Zrealizowane”; zobowiązania = Wydatki „Do zapłaty” i Etapy kol. N.
Kolory stanów (od 26.11.2026; tło / tekst): Koszty ogólne e7e9ee / 4a5568 · Przygotowanie do budowy dcebdd / 3f6b47 ·
Stan zero f1e6d2 / 7a5c2e · SSO d9e6f2 / 2f5d8a · Deweloperski e4ddf0 / 5b4b8a · Wykończenie f2dce3 / 8a3d57 · Teren d5ecea / 2e6e68.
Etapy kol. A:B – formatowanie warunkowe wg kol. B (nowy etap dostaje kolor sam); Podsumowanie – nagłówek bloku (tło + kreska
w kolorze tekstu), kol. A etapów bloku i wiersze tabeli „wg stanów” (wpisane, nowy blok dostaje kolor swojego stanu).
Kosztorys kol. A i kol. Etap w Wydatkach – nadal własny pastel każdego etapu. Materiał – brzoskwiniowy,
ekipa – zielony, inne – fioletowy, plan – niebieski, wydane – piaskowy, pozostało – miętowy, zakończone – zielony znacznik w kol. K.
Wydatki: wiersze po dacie, odcień wiersza wg kwoty (do 500 / 500–5 000 / 5 000–50 000 / 50 000+ zł), niebieski = „Do zapłaty”,
żółty = ⚠ w Kontroli; Status, Etap i Typ jako kolorowe pola. Cennik: wybrana oferta – zielony wiersz, odrzucona – szary tekst.
„Ekipa” = Typ Robocizna (transze z umowy, roboty dodatkowe); „Inne” = Sprzęt, Usługa, Formalności.

## Proponowane (nie ma w arkuszu – dodaje inwestor albo agent na prośbę, `koszty` C)
**Płatności** – plan płatności z umów i zamówień, gdy inwestor chce go prowadzić w arkuszu (gotówka w czasie działa bez tej
zakładki: `references/gotowka.md`; `wydatki.py gotowka` jej nie czyta). Wiersze od 5, nagłówki w wierszu 4:
A Data planowana · B Etap (lista z Etapy!A) · C Co (transza z umowy / zamówienie / faktura) · D Kwota brutto · E Sposób
(Gotówka / Przelew) · F Status (Plan / Zapłacone – zapłacone idzie też jako wydatek przez kolejkę) · G Skąd termin (umowa,
krok Harmonogramu) · H Uwagi. Obok zestawienie miesięczne J:N: J Miesiąc (1. dzień miesiąca, format RRRR-MM) · K Plan
`=SUMIFS(D:D;A:A;">="&J5;A:A;"<"&EDATE(J5;1);F:F;"Plan")` · L w tym gotówką (to samo z `E:E;"Gotówka"`) · M Do zapłaty
z Wydatków (`SUMIFS` po kolumnach Kwota, Status = „Do zapłaty” i Data – litery po nagłówkach żywego arkusza) · N z rezerwą
`=(K5+M5)*(1+<komórka rezerwy w Podsumowaniu>)`. Formuły z „;” (polskie ustawienia), bez formuł tablicowych.
