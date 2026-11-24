# Nowa pozycja i nowy etap kosztorysu (pole „Nowa pozycja”)

Wydatek bez pasującej pozycji nie czeka na ręczną zmianę arkusza. Inwestor odpowiada „tak” albo podaje własną nazwę, a resztę
robi automat (pozycja w istniejącym etapie) albo pierwsza sesja Claude Code (nowy etap, pierwsze sprawdzenie po wdrożeniu).
Mechanizm: `docs/wydatki-arkusz.md` (akcja Apps Script „dodaj_pozycje”, kod ≥ 5).

## A. Propozycja w ❓ (przebieg i rozmowa)

1. Najpierw szukaj istniejącej pozycji – także w innym etapie i pod inną nazwą (lista pola Pozycja, kopia arkusza). Pasuje →
   zwykłe pytanie z tą pozycją (`koszty` B.2), nie nowa.
2. Nie pasuje żadna → okienko ❓ pod wpisem (`wpisy/references/pytania.md`, A) z gotową propozycją, bez kroków w arkuszu:
   **„Nowa pozycja: 47 | Pozycja X | Materiał | kpl – tak?”** (albo wpisz własną nazwę). Dobór:
   - etap – ten, na który poszedł wydatek (materiał na ściany → etap ścian); roboty poza umową mają w etapie gotową pozycję
     „Roboty dodatkowe – poza umową” – nie twórz drugiej;
   - nazwa – krótka, jak sąsiednie pozycje etapu (rzecz, nie sklep ani faktura), bez = + - @ na początku;
   - typ – Materiał / Robocizna / Sprzęt / Usługa / Formalności (zwykle typ wydatku); jednostka – kpl, m³, m², mb, kg, t, szt,
     h, dzień, mies., l (rzecz liczona w sztukach albo całość – kpl);
   - **żaden etap nie pasuje** → nowy etap: numer z zakładki „Szacunek AI 10.2026” (etap szacunku, np. wykończenie 40–46),
     a gdy go tam nie ma – kolejny wolny (`references/arkusze.md`, Etapy); nazwa etapu i stan (Koszty ogólne, Stan zero, SSO,
     Deweloperski, Wykończenie, Teren): „**Nowy etap 41 Etap Y (Wykończenie) i pozycja: 41 | Pozycja X | Materiał | kpl – tak?**”.
3. Odpowiedź (`pytania.md`, A – „Odczyt odpowiedzi”): „tak” / „ok” = propozycja; sama nazwa = propozycja z tą nazwą; inny
   etap, typ albo jednostka w odpowiedzi – weź je. Potem strona wydatku jak w `koszty` B.4: Pozycja **pusta**, pole
   **Nowa pozycja** = `<etap> | <nazwa> | <typ> | <jedn.>` (nowy etap: `<nr> <nazwa etapu> · <stan> | <nazwa> | <typ> | <jedn.>`),
   Arkusz „Do arkusza”. Kilka wydatków na tę samą nową pozycję – w każdej stronie ten sam tekst (automat doda jeden wiersz).
   - Pole działa tylko przy Rodzaju **Wydatek** i **Wycena**. Zwrot i Plan dotyczą pozycji, która już jest, więc
     z „Nową pozycją” dostają Błąd: najpierw wydatek z nową pozycją, potem zwrot albo plan z wybraną Pozycją.
   - Strona ma wybraną Pozycję i wypełnione pole → **wygrywa Pozycja** (świadomy wybór), a pole czyści najbliższy zapis.
     Chcesz zamienić istniejącą pozycję na nową → wyczyść Pozycję.
4. Wpis z ❓ do „Przetworzone”: `→ wydatek: <wzmianka 💸>; nową pozycję doda automat` (nowy etap: „…; etap doda najbliższa
   sesja Claude Code – nic nie musisz robić”).

## B. Co robi automat (`wydatki.py sync`, bez AI)

- Strona z „Nową pozycją” → akcja „dodaj_pozycje”:
  - wiersz w etapie: przed ostatnią pozycją etapu, a w etapie z jedną pozycją – za nią;
  - formuły i formaty z pozycji z kompletem formuł; Lp = najwyższy numer etapu w Kosztorysie i w Wydatkach + 1;
  - kontrola przed i po: „Kontrola powiązań”, RAZEM KOSZTORYS, sumy nagłówka etapu, komplet formuł nowego wiersza.
    Różnica = wiersz usunięty, strona „Błąd” → 🔔 (`koszty` E);
  - ta sama nazwa w etapie = istniejąca pozycja (ponowienie po „arkusz: timeout” nie doda drugiej), o ile jej wiersz jest
    kompletny;
  - wiersz etapu bez Lp (A = etap, B puste) → odmowa: „uzupełnij Lp albo usuń wiersz”.
- Potem `pozycje` (opcja w Notion), na stronie Pozycja = nowa opcja, „Nowa pozycja” pusta – i wydatek idzie do arkusza
  w tym samym przebiegu.
- **Bezpiecznik pierwszego użycia.** Bez znacznika `<hub>/.dom/wydatki/nowa-pozycja-sprawdzona` akcja idzie na sucho.
  Istniejąca pozycja przechodzi, a nowa czeka na pierwsze sprawdzenie w sesji (sekcja D). W polu Błąd jest wtedy dopisek, bez 🔔.
- Kod Apps Script < 5 → strony czekają „Do arkusza”, `sync` kończy się kodem 1 z linią „… czeka: arkusz ma kod w wersji …”.
- Etapu nie ma w Kosztorysie albo jego nagłówek nie ma pozycji → strona czeka „Do arkusza” (bez 🔔). W polu Błąd jest
  dopisek „czeka na etap NN – doda go najbliższa sesja Claude Code”. Przy świeżej blokadzie sesji
  automat nie wstawia pozycji w żadnym etapie – strony czekają do przebiegu po `sesja --odblokuj`.
- Sprawy dla sesji (nowe etapy, pierwsze sprawdzenie) trafiają do `<hub>/.dom/wydatki/kosztorys-do-sesji.json`, a z niego do
  linii stanu sesji: „nowy etap kosztorysu: NN”, „nowa pozycja kosztorysu: pierwsze sprawdzenie”. Podgląd:
  `python3 tools/wydatki.py sesja`.
- Sprawa czeka na sesję ponad 3 dni → `sync` kończy się kodem 1, a przebieg zgłasza 🔔. W logu jest linia
  „czeka na sesję Claude Code ponad 3 dni: …”.

## C. Nowy etap w sesji Claude Code (linia stanu albo `sync` z `czekaja_na_etap` > 0)

Bez pytania i bez przypominania inwestorowi – zaraz po linii stanu (wyjątek w `CLAUDE.md`, start sesji), przed zadaniem
z pierwszej wiadomości. Polecenia w katalogu repo harnessu.

1. `python3 tools/wydatki.py sesja --zablokuj` – „nic nie czeka” albo „zajęte” (inna sesja) → nic nie rób, bez
   meldunku. Inaczej lista: nowe etapy (nazwa, stan, pozycje) i pierwsze sprawdzenie (sekcja D – po etapach).
2. **Konektor Google Sheets** (plik „Kosztorys budowy” po tytule; wzorzec – etap 47, `references/arkusze.md`):
   1. Odczyt Kosztorys A:C, Etapy A:B, Podsumowanie „Kontrola powiązań” i wiersz RAZEM KOSZTORYS. Rozpoznaj, gdzie etap jest,
      żeby go nigdy nie zdublować:
      - w Kosztorysie z pozycjami → od razu krok 4;
      - nagłówek w Kosztorysie bez pozycji (przerwana sesja) → tylko wiersz pozycji pod nim (2.3, część „pozycja”);
      - tylko w Etapach → blok w Kosztorysie (2.3), bez nowego wiersza Etapów;
      - nigdzie → 2.2 i 2.3.

      Migawka zmienianych zakresów z formułami do `<hub>/.dom/wydatki/migawka-RRRR-MM-DD-przed-etapNN.json`.
   2. Etapy: pierwszy wiersz 5–40 z pustym A (formuły D–R już w nim są) – B = stan; A („NN Nazwa etapu”) wpisz dopiero
      w kroku 2.4. Brak wolnego wiersza → stop (punkt 5, przyczyna).
   3. Kosztorys: wstaw 2 wiersze przed nagłówkiem pierwszego etapu o wyższym numerze (P1–P4 na górze). Nowy etap za
      wszystkimi wstaw przed nagłówkiem ostatniego etapu, bo zakresy sum (RAZEM, Etapy, Podsumowanie) kończą się na ostatniej
      pozycji arkusza i wiersz za nią by z nich wypadł.
      - **Pozycja najpierw:** formuły pozycji z kompletem formuł sąsiedniego etapu przeniesione na nowy wiersz, A
        `=$A$<nagłówek>`, B `NN.1` **jako tekst** (najpierw format tekstowy komórki B – inaczej „17.1” stanie się datą), C – nazwa
        **dokładnie** jak w liście z kroku 1, D typ, E jedn.
      - Potem nagłówek jak przy etapie 47, z wyjątkiem kolumny A: C `=UPPER(Etapy!A<n>)&"   ·   "&Etapy!B<n>`,
        G, I, J, Q, R, S, U `=SUM(X<p>)` (p – wiersz pozycji), T – formuła T z nagłówka sąsiedniego etapu z numerem tego wiersza.
      - Formaty i listy rozwijane skopiuj z nagłówka i pozycji sąsiedniego etapu. Formuły ze „;” (polskie ustawienia).
   4. **Na końcu kolumna A:** Etapy A = „NN Nazwa etapu”, potem Kosztorys A nagłówka `=Etapy!A<n>`. Dopiero wtedy automat
      widzi etap, więc nigdy nie trafi na niego w połowie.
   5. Kontrola: „Kontrola powiązań” i RAZEM jak przed, nowa pozycja w zakresach RAZEM (`$5:$<n>`), T puste, M = „NN.1 Nazwa”.
      Różnica → usuń wstawione wiersze, wyczyść A:B nowego wiersza Etapów, punkt 5 z przyczyną.
   6. Szacunek AI: przypisz pasujące wiersze w kol. J:K (`koszty` C.4), gdy są jednoznaczne.
3. **Bez konektora** (albo jego błąd): plik zmian i `python3 tools/wydatki.py migruj` (`docs/wydatki-arkusz.md`, 8).
   - Operacja `wstaw`: Kosztorys, `przed` = wiersz z kroku 2.3, `ile` 2.
   - Operacje `zakres` z tymi samymi formułami, wartościami i tłem (`tla`) co w kroku 2, w tej samej kolejności: kolumna A na
     końcu, w osobnym pliku zmian. Komórka B pozycji z `"formaty": [["@"]]`, żeby Lp był tekstem.
   - Potem `pobierz` i kontrola jak w 2.5.
4. Najpierw `python3 tools/wydatki.py sesja --odblokuj`, potem `python3 tools/wydatki.py sync` – przy świeżej blokadzie `sync`
   nie wstawia pozycji (strony czekają), a etap jest już kompletny. Akcja „dodaj_pozycje” znajdzie pozycję po nazwie, ustawi
   Pozycję i wyśle wydatek. Dalsze pozycje tego etapu z listy doda sama, gdy jest znacznik pierwszego sprawdzenia. Na liście
   z kroku 1 czeka też pierwsze sprawdzenie → bez odblokowania i bez `sync` od razu sekcja D (oba w D.5).
5. Meldunek jedną linią (bez kwot): „Kosztorys: dodałem etap NN Nazwa (stan) z pozycją NN.1 – wydatek w arkuszu, wiersz N.”
   Nie wyszło → „Kosztorys: etapu NN nie dodałem – <przyczyna>; wydatek czeka w kolejce.” i blokada zdjęta; ta sama przyczyna
   drugi raz → wiersz Usterka (`rozwoj-harnessu`, D).

## D. Pierwsze sprawdzenie nowej pozycji (linia stanu „nowa pozycja kosztorysu: pierwsze sprawdzenie”)

Jednorazowo po wdrożeniu kodu 5, tak samo bez pytania jak sekcja C (w tej samej blokadzie `sesja --zablokuj`). Kod akcji nie
był nigdy uruchomiony na żywym arkuszu, więc pierwsze prawdziwe wstawienie robi sesja z kontrolą, a nie nocny automat.

1. `python3 tools/wydatki.py sprawdz` – kod w wersji < 5 → nic więcej nie rób: `sesja --odblokuj` i meldunek „Kosztorys: nowa
   pozycja czeka na wklejenie kodu arkusza w wersji 5” (czynność inwestora jest w 🔔 z `sync`).
2. `python3 tools/wydatki.py pobierz` i kopia `Koszty/Kosztorys_google.json` jako
   `<hub>/.dom/wydatki/migawka-RRRR-MM-DD-przed-pierwsza-pozycja.json`. Z konektorem odczytaj też sumy nagłówka etapu, RAZEM
   i „Kontrolę powiązań”.
3. Pierwsza pozycja z listy `sesja` (tekst dosłownie z listy – pełny, z typem i jednostką):
   `python3 tools/wydatki.py nowa-pozycja "<tekst>" --proba` – plan (Lp, wiersz, suma etapu, wzór). Potem to samo bez `--proba`.
4. Konektorem: nowy wiersz (formuły jak w sąsiedniej pozycji, Lp tekstem, Klucz „Lp Nazwa”, Kontrola pusta), sumy nagłówka
   etapu (zakres obejmuje nowy wiersz, wartości jak przed), RAZEM i „Kontrola powiązań” jak przed. Bez konektora – `pobierz`
   i porównanie z migawką z kroku 2 (te same wartości plus nowy wiersz).
5. Zgodne → `python3 tools/wydatki.py nowa-pozycja --potwierdz` (znacznik), `sesja --odblokuj`, potem
   `python3 tools/wydatki.py sync` (strona dostanie istniejący Lp, wydatek pójdzie). Meldunek: „Kosztorys: pierwsza nowa pozycja NN.n sprawdzona – od teraz
   automat dodaje je sam.”
6. Niezgodne → konektorem usuń własny wiersz i przywróć formuły sum nagłówka z migawki. Bez konektora blok 🔔
   (`pytania.md`, C) z dokładną czynnością: „Plik → Historia wersji → przywróć wersję sprzed <gg:mm>”. Znacznika nie twórz.
   Wiersz Usterka (`rozwoj-harnessu`, D) z przyczyną, `sesja --odblokuj`.
