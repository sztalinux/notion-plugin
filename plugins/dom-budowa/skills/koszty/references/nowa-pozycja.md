# Nowa pozycja i nowy etap kosztorysu (pole „Nowa pozycja”, POM-31)

Wydatek bez pasującej pozycji nie czeka na ręczną zmianę arkusza: inwestor odpowiada „tak” albo własną nazwą, a resztę robi
automat (pozycja w istniejącym etapie) albo pierwsza sesja Claude Code (nowy etap). Mechanizm: `docs/wydatki-arkusz.md`
(akcja Apps Script „dodaj_pozycje”, kod ≥ 5).

## A. Propozycja w ❓ (przebieg i rozmowa)

1. Najpierw szukaj istniejącej pozycji – także w innym etapie i pod inną nazwą (lista pola Pozycja, kopia arkusza). Pasuje →
   zwykłe pytanie z tą pozycją (`koszty` B.2), nie nowa.
2. Nie pasuje żadna → okienko ❓ pod wpisem (`wpisy/references/pytania.md`, A) z gotową propozycją, bez kroków w arkuszu:
   **„Nowa pozycja: 47 | Pozycja X | Materiał | kpl – tak?”** (albo wpisz własną nazwę). Dobór:
   - etap – ten, na który poszedł wydatek (materiał na ściany → etap ścian); w etapie z „Roboty dodatkowe – poza umową”
     nowa pozycja dla robót poza umową to ta istniejąca, nie nowa;
   - nazwa – krótka, jak sąsiednie pozycje etapu (rzecz, nie sklep ani faktura), bez = + - @ na początku;
   - typ – Materiał / Robocizna / Sprzęt / Usługa / Formalności (zwykle typ wydatku); jednostka – kpl, m³, m², mb, kg, t, szt,
     h, dzień, mies., l (rzecz liczona w sztukach albo całość – kpl);
   - **żaden etap nie pasuje** → nowy etap: numer z zakładki „Szacunek AI 10.2026” (etap szacunku, np. wykończenie 40–46),
     a gdy go tam nie ma – kolejny wolny (`references/arkusze.md`, Etapy); nazwa etapu i stan (Koszty ogólne, Stan zero, SSO,
     Deweloperski, Wykończenie, Teren): „**Nowy etap 41 Etap Y (Wykończenie) i pozycja: 41 | Pozycja X | Materiał | kpl – tak?**”.
3. Odpowiedź (`pytania.md`, A – „Odczyt odpowiedzi”): „tak” / „ok” = propozycja; sama nazwa = propozycja z tą nazwą; inny
   etap, typ albo jednostka w odpowiedzi – weź je. Potem strona wydatku jak w `koszty` B.4: Pozycja pusta, pole
   **Nowa pozycja** = `<etap> | <nazwa> | <typ> | <jedn.>` (nowy etap: `<nr> <nazwa etapu> · <stan> | <nazwa> | <typ> | <jedn.>`),
   Arkusz „Do arkusza”. Kilka wydatków na tę samą nową pozycję – w każdej stronie ten sam tekst (automat doda jeden wiersz).
4. Wpis z ❓ do „Przetworzone”: `→ wydatek: <wzmianka 💸>; nową pozycję doda automat` (nowy etap: „…; etap doda najbliższa
   sesja Claude Code – nic nie musisz robić”).

## B. Co robi automat (`wydatki.py sync`, bez AI)

- Strona z „Nową pozycją” → akcja „dodaj_pozycje”: wiersz w etapie (przed ostatnią pozycją etapu, a w etapie z jedną
  pozycją – za nią), formuły i formaty z sąsiedniej pozycji, Lp = najwyższy numer w etapie + 1; kontrola przed i po
  („Kontrola powiązań”, RAZEM KOSZTORYS, sumy etapu) – różnica = wiersz usunięty, strona „Błąd” → 🔔 (`koszty` E).
  Ta sama nazwa w etapie = istniejąca pozycja (ponowienie po „arkusz: timeout” nie doda drugiej).
- Potem `pozycje` (opcja w Notion), na stronie Pozycja = nowa opcja, „Nowa pozycja” pusta – i wydatek idzie do arkusza
  w tym samym przebiegu.
- Kod Apps Script < 5 → strony czekają „Do arkusza”, `sync` kończy się kodem 1 z linią „… czeka: arkusz ma kod w wersji …”.
- Etapu nie ma w Kosztorysie → strona czeka „Do arkusza” (bez 🔔), w polu Błąd „czeka na etap NN – doda go najbliższa sesja
  Claude Code”; etap trafia do `<hub>/.dom/wydatki/etapy-do-dodania.json`, a z niego do linii stanu sesji
  („nowy etap kosztorysu: NN”). Sprawdzenie ręczne: `python3 tools/wydatki.py etapy`.

## C. Nowy etap w sesji Claude Code (linia stanu albo `sync` z `czekaja_na_etap` > 0)

Bez pytania i bez przypominania inwestorowi – zaraz po linii stanu (wyjątek w `CLAUDE.md`, start sesji), przed zadaniem
z pierwszej wiadomości. Polecenia w katalogu repo harnessu.

1. `python3 tools/wydatki.py etapy --zablokuj` – „brak nowych etapów” albo „zajęte” (inna sesja) → nic nie rób, bez
   meldunku. Inaczej lista: etap, nazwa, stan, pozycje (nazwa, typ, jedn.), liczba stron.
2. **Konektor Google Sheets** (plik „Kosztorys budowy” po tytule; wzorzec – etap 47, `references/arkusze.md`):
   1. Odczyt Kosztorys A:C, Etapy A:B, Podsumowanie „Kontrola powiązań” i wiersz RAZEM KOSZTORYS. Etap już jest → krok 3.
      Migawka zmienianych zakresów z formułami do `<hub>/.dom/wydatki/migawka-RRRR-MM-DD-przed-etapNN.json`.
   2. Etapy: pierwszy wiersz 5–40 z pustym A (formuły D–R już w nim są) – A = „NN Nazwa etapu”, B = stan. Brak wolnego
      wiersza → stop (punkt 5, przyczyna).
   3. Kosztorys: wstaw 2 wiersze przed nagłówkiem pierwszego etapu o wyższym numerze (P1–P4 na górze); nowy etap za
      wszystkimi – przed nagłówkiem ostatniego etapu, bo zakresy sum (RAZEM, Etapy, Podsumowanie) kończą się na ostatniej
      pozycji arkusza i wiersz za nią by z nich wypadł. Nagłówek jak przy etapie 47: A `=Etapy!A<n>`,
      C `=UPPER(Etapy!A<n>)&"   ·   "&Etapy!B<n>`, G, I, J, Q, R, S, U `=SUM(X<p>)` (p – wiersz pozycji), T – formuła T
      z nagłówka sąsiedniego etapu z numerem tego wiersza. Pozycja: formuły pozycji sąsiedniego etapu przeniesione na nowy
      wiersz, A `=$A$<nagłówek>`, B `NN.1` **jako tekst** (najpierw format tekstowy komórki B – inaczej „17.1” stanie się
      datą), C – nazwa **dokładnie** jak w liście z kroku 1, D typ, E jedn.; formaty
      i listy rozwijane skopiuj z nagłówka i pozycji sąsiedniego etapu. Formuły ze „;” (polskie ustawienia).
   4. Kontrola: „Kontrola powiązań” i RAZEM jak przed, nowa pozycja w zakresach RAZEM (`$5:$<n>`), T puste, M = „NN.1 Nazwa”.
      Różnica → usuń wstawione wiersze, wyczyść A:B nowego wiersza Etapów, punkt 5 z przyczyną.
   5. Szacunek AI: przypisz pasujące wiersze w kol. J:K (`koszty` C.4), gdy są jednoznaczne.
3. **Bez konektora** (albo jego błąd): plik zmian i `python3 tools/wydatki.py migruj` (`docs/wydatki-arkusz.md`, 8) – operacja
   `wstaw` (Kosztorys, `przed` = wiersz z kroku 2.3, `ile` 2) i operacje `zakres` z tymi samymi formułami, wartościami
   i tłem (`tla`) co w kroku 2 (komórka B pozycji z `"formaty": [["@"]]` – Lp jako tekst); potem `pobierz` i kontrola jak w 2.4.
4. `python3 tools/wydatki.py sync` – akcja „dodaj_pozycje” znajdzie pozycję po nazwie, ustawi Pozycję i wyśle wydatek; dalsze
   pozycje tego etapu z listy doda sama. `python3 tools/wydatki.py etapy --odblokuj`.
5. Meldunek jedną linią (bez kwot): „Kosztorys: dodałem etap NN Nazwa (stan) z pozycją NN.1 – wydatek w arkuszu, wiersz N.”
   Nie wyszło → „Kosztorys: etapu NN nie dodałem – <przyczyna>; wydatek czeka w kolejce.” i blokada zdjęta; ta sama przyczyna
   drugi raz → wiersz Usterka (`rozwoj-harnessu`, D).
