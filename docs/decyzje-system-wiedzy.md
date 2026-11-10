# System wiedzy – rejestr decyzji (ADR)

Ten plik zapisuje, **dlaczego** system wiedzy budowy wygląda tak, a nie inaczej: co wybrano, co sprawdzono i odrzucono, z jakimi liczbami.
Jak system działa, co robić przy awarii i co znaczą pojęcia (WI, teza, Kluczowe, wzorzec, recall@widziane, karta, rdzeń), opisują `docs/system-wiedzy.md` i `docs/wiedza-runbook.md` – tutaj są tylko decyzje.
Wpisy powstały w listopadzie 2026 z planów, raportów nocnych i wyników pomiarów z okresu 16.10–5.11.2026; folder planów usunięto 2026-11 – w repo ten rejestr jest jedynym śladem tamtych uzasadnień, a pełne raporty z pomiarów leżą w prywatnym archiwum poza repo.
Każdy wpis ma ten sam układ: status, data, kontekst, decyzja, rozważane warianty, skutki, wdrożenie, źródło. Wpisy są w kolejności zbliżonej do chronologicznej; „zastąpiona” znaczy, że rozwiązanie działało i ustąpiło lepszemu, „odrzucona” – że eksperyment zakończył się decyzją „nie wdrażamy”, „otwarta” – że pytanie czeka na pomiar albo na inwestora.
Liczby pochodzą z pomiarów na konkretnym stanie bazy i wzorcu – porównuj je tylko w obrębie jednego wpisu (zasada z ADR-04); tę samą drogę różne wzorce oceniają różnie (ADR-17).
Słowo **niepewne** oznacza miejsce, w którym źródła były sprzeczne, niepełne albo nie dało się potwierdzić stanu w kodzie.
Nową decyzję dopisuj na końcu z kolejnym numerem; starej nie przepisuj – zmień jej status i wskaż następcę.

## Spis wpisów

| Nr | Decyzja | Status |
|---|---|---|
| ADR-01 | Indeks lokalny tylko do odczytu, Notion jedynym źródłem prawdy | przyjęta |
| ADR-02 | Kopia dla czatu w prywatnym repo, bez kompresji | przyjęta |
| ADR-03 | W nocy i w czacie szukamy w indeksie, nie w wyszukiwarce Notion | przyjęta |
| ADR-04 | Zamrożony pomiar odpowiedzi czatu i zasada „ten sam stan bazy” | przyjęta |
| ADR-05 | `szukaj`: zwarta linia i kilka sformułowań naraz | przyjęta |
| ADR-06 | Synonimy wybierane pomiarem; dopasowanie po rdzeniu odłożone | przyjęta, w części otwarta |
| ADR-07 | Odciski znaczenia liczone lokalnie, bez usługi zewnętrznej | przyjęta |
| ADR-08 | Listy „podobne” w kopii dla czatu – wydane mimo niespełnionego kryterium | przyjęta |
| ADR-09 | `duplikaty` to lista kandydatów, nie wykrywacz | przyjęta |
| ADR-10 | Notatnik, zadania i dokumenty poza indeksem | przyjęta |
| ADR-11 | Treść bazy do modeli Claude bez filtra danych osobowych | przyjęta |
| ADR-12 | Porządki w bazie: scalanie bez usuwania, rdzeń zamiast całości | przyjęta |
| ADR-13 | Przegląd między tematami: próg 0,65; nowy temat i runda 2 | przyjęta, w części otwarta |
| ADR-14 | Nocne przetwarzanie etapami: porównanie z całym tematem przed zapisem | przyjęta, odbiór otwarty |
| ADR-15 | Stały pomiar: reguła sędziego, hybryda w kontroli, mini-audyt | przyjęta |
| ADR-16 | Procedura czatu z trzema poziomami głębokości | zastąpiona przez ADR-23 |
| ADR-17 | Wzorzec pomiaru: pełny odrzucony, skalibrowany przyjęty | przyjęta |
| ADR-18 | Książka w Notion (rozdziały z przypisami) | odrzucona |
| ADR-19 | Poziom „cały etap” na telefonie | zastąpiona przez ADR-23 |
| ADR-20 | Filtr po kolumnach: „czynność” tylko w indeksie, etap wielokrotny nie | przyjęta w części, odrzucona w części |
| ADR-21 | Pytania o zamknięcie etapu: filtr po rodzaju, nie okno etapów | przyjęta |
| ADR-22 | Praca bez konektora Notion: lokalny MCP, launchd, migawka, Skrzynka | przyjęta |
| ADR-23 | Karty wiedzy: wybór tez robi Mac, nie czat | przyjęta |
| ADR-24 | Ocena ścisła po wyborze inkluzywnym, rdzeń 200 tez | przyjęta |
| ADR-25 | Budżet telefonu 75 tys. znaków: podział kart i krótsze tezy | przyjęta |
| ADR-26 | Tryb głęboki: pytanie złożone liczone poza telefonem | przyjęta |
| ADR-27 | Brama przy zapisie i budżet Kluczowych | otwarta |
| ADR-28 | Nocny wykonawca zadań: przygotowuje i mierzy, nie wydaje | przyjęta |
| ADR-29 | Dokumentacja: część publiczna ogólna, szczegóły prywatne poza repo | przyjęta |

Na końcu: „Pytania otwarte bez osobnego wpisu”.

---

## ADR-01: Indeks lokalny tylko do odczytu, Notion jedynym źródłem prawdy
- **Status:** przyjęta
- **Data:** 2026-10-16
- **Kontekst:** Asystent szukał wiedzy wyszukiwarką Notion – wolno i z limitami, a czat na telefonie, sesja na Macu i nocna kolejka potrzebowały tego samego wyniku. Repo harnessu jest publiczne, więc dane nie mogą w nim leżeć.
- **Decyzja:** Jeden plik SQLite z FTS5 budowany z czterech baz Notion przez API (integracja tylko do odczytu) i jeden moduł uruchamiany tym samym kodem w trzech kanałach. Indeks nigdy nie pisze do Notion; każdy wynik niesie datę stanu; w indeksie są wyłącznie kopie pól Notion.
- **Rozważane warianty:** usługa w chmurze albo własny serwer – odrzucone wprost („nie buduj niczego w chmurze”); zależności spoza biblioteki standardowej Pythona 3.9 – odrzucone, bo ten sam plik musi działać w piaskownicy czatu; czytanie relacji od strony Tematów i Źródeł – odrzucone, API zwraca najwyżej 25 relacji; rollupy pominięte.
- **Skutki:** wiedza zapisana z telefonu trafia do indeksu dopiero przy najbliższym `sync` na Macu (zaakceptowane). Planowany hook startu sesji usunięto w 2.6.2 – synchronizacja jest pozycją listy wyboru.
- **Wdrożenie:** dom-budowa 2.4.0, `tools/wiedza.py`, `wiedza/references/indeks.md`.
- **Źródło:** `POM-6-indeks-wiedzy.md`, `POM-6-instrukcja-dla-modelu.md` (folder planów usunięto 2026-11).

## ADR-02: Kopia dla czatu w prywatnym repo, bez kompresji
- **Status:** przyjęta
- **Data:** 2026-10-16 (kopia), 2026-10-26 (rezygnacja z `.gz`)
- **Kontekst:** Czat na telefonie wychodzi do sieci tylko do GitHuba i rejestrów pakietów – nie sięgnie Maca. Indeks zawiera pola osób trzecich.
- **Decyzja:** `publikuj` wysyła indeks i sam moduł do prywatnego repo, tylko gdy dane się zmieniły; czat pobiera je tokenem tylko do odczytu (ważnym 90 dni), którego wartość leży wyłącznie w pliku sekretów i na stronie dostępu. Pliku `.gz` nie publikujemy.
- **Rozważane warianty:** `.gz` obok indeksu – pobranie 9,25 MB trwało medianę ok. 2,5 s (1,4–4,5 s, 8 prób), `.gz` miałby 3,04 MB i dał ok. 1,3 s zysku; odrzucone jako dodatkowy plik i krok procedury za zysk mniejszy niż jedna odpowiedź modelu. Repo publiczne – wykluczone (program odmawia publikacji).
- **Skutki:** wrócić do `.gz`, gdy pobranie na telefonie przekroczy 5 s albo indeks 25 MB. Pomiar robiono z Maca, nie z piaskownicy czatu. Token odczytu trzeba odnawiać z zapasem.
- **Wdrożenie:** dom-budowa 2.4.0 (`publikuj`); decyzja o `.gz` przy 2.7.0.
- **Źródło:** `POM-6-indeks-wiedzy.md`, `Z2-szukaj-zwarty-wiele.md`, `rano/2026-10-25-Z2.md`, `rano/pytania.md` (folder planów usunięto 2026-11).

## ADR-03: W nocy i w czacie szukamy w indeksie, nie w wyszukiwarce Notion
- **Status:** przyjęta
- **Data:** 2026-10-25
- **Kontekst:** Nocna kolejka szukała powiązanej wiedzy naprzemiennie w indeksie i w Notion. Kontrola wyrywkowa i audyt 20 źródeł (22.10) pozwoliły porównać oba silniki.
- **Decyzja:** tryb szukania w nocy = indeks; model kontroli wyrywkowej = Sonnet; sędzia w tle co 1 dzień; historia zmian folderu kolejki i planów w lokalnym gicie bez zdalnego repo.
- **Rozważane warianty:** wyszukiwarka Notion – w kontroli 72 testów pokrycie trafnych wyników 84% (indeks) wobec 40% (Notion), w audycie powiązania uwzględnione przy zapisie 63% wobec 47%; tryb „naprzemiennie” – zbędny, kontrola i tak porównuje oba silniki; Opus do oceny 0/1/2 – prosta praca, Sonnet ok. 2× szybciej; zdalne prywatne repo dla kolejki – niewybrane.
- **Skutki:** Notion zostaje miejscem zapisu i źródłem prawdy. Wyszukiwanie to 3–6% czasu przetwarzania filmu, więc cały plan dotyczył trafności, nie kosztu nocy.
- **Wdrożenie:** ustawienia nocnej kolejki (poza repo); uzasadnienie powtórzone w `docs/system-wiedzy.md`.
- **Źródło:** `Z0-decyzje-i-git.md`, `00-PLAN.md` (folder planów usunięto 2026-11).

## ADR-04: Zamrożony pomiar odpowiedzi czatu i zasada „ten sam stan bazy”
- **Status:** przyjęta
- **Data:** 2026-10-25
- **Kontekst:** Wcześniejsze pomiary (obserwator, sędzia, kontrola nocna, audyt) dotyczyły wyszukiwania albo zapisu. Nikt nie mierzył odpowiedzi na pytanie z telefonu, a baza zmienia się co noc.
- **Decyzja:** zamrożony zestaw 53 pytań (w tym 10 dosłownych pytań inwestora) i wzorzec trafnych tez; miara główna recall@widziane, obok długość wyniku i kompletność odpowiedzi od pytania do odpowiedzi. Każda zmiana szukania liczy wariant bazowy V0 obok nowego, tego samego dnia, i raportuje różnicę; pogorszenie albo alarm obserwatora = brak wydania.
- **Rozważane warianty:** automatyczny pomiar prawdziwego czatu na telefonie – niemożliwy, zostaje testem inwestora; porównywanie liczb z różnych dni – odrzucone: ten sam V0 dawał 25,3%, 26,9% i 28,0% zależnie od stanu bazy.
- **Skutki:** punkt wyjścia V0: recall@widziane 25,3%, średnio 15 398 znaków wyniku, kompletność odpowiedzi 39% (15 pytań); koszt pomiaru 16,86 USD. Narzędzie oceny i zbiory leżą poza repo.
- **Wdrożenie:** poza repo; zasada w `docs/wiedza-runbook.md`, sekcja 4.
- **Źródło:** `Z1-pomiar-bazowy.md`, `_zasady.md`, `00-PLAN.md` (folder planów usunięto 2026-11).

## ADR-05: `szukaj`: zwarta linia i kilka sformułowań naraz
- **Status:** przyjęta
- **Data:** 2026-10-26
- **Kontekst:** Wynik miał 12 linii po ok. 750 znaków, z czego ok. 60% to metadane; 48 z 49 zapytań nocnych wpadało w tryb „którekolwiek słowo”; jedno sformułowanie dawało jedną szansę.
- **Decyzja:** kilka zapytań w jednym wywołaniu łączonych reciprocal rank fusion (k = 60, niestrojone), `--krotko` (teza do 220 znaków, domyślnie 25 linii), `temat --lista`. Tryb pełny bez zmian – noc potrzebuje pola „Kto”.
- **Rozważane warianty (53 pytania, V0 = 25,3%):** samo `--krotko` 25 – 38,4% przy 0,53× znaków (większość zysku); 3 sformułowania + `--krotko` – 42,0% przy 0,62×; to samo z odcinaniem ogona „którekolwiek słowo” – 41,4% (odcinanie odrzucone przy kilku zapytaniach); `--limit 40` – 50,6% przy 0,95× (zostawione procedurze czatu); trzy osobne wywołania – 58,0%, ale 1,66× znaków; linia pełna – 29,1%.
- **Skutki:** regresja 1219/1219 przypadków identycznych, 0 alarmów obserwatora. Precyzja tego, co czat widzi, spadła z 41% do 35%.
- **Wdrożenie:** dom-budowa 2.7.0, `tools/wiedza.py`.
- **Źródło:** `Z2-szukaj-zwarty-wiele.md`, `rano/2026-10-25-Z2.md` (folder planów usunięto 2026-11).

## ADR-06: Synonimy wybierane pomiarem; dopasowanie po rdzeniu odłożone
- **Status:** przyjęta; część o dopasowaniu po rdzeniu – otwarta
- **Data:** 2026-10-26
- **Kontekst:** Słownik miał 35 grup i działa na całe słowa po stronie tezy, więc grupy nie odpalały się na formach odmienionych.
- **Decyzja:** dopisano 9 jednostek (formy odmienione 5 grup i 4 nowe grupy), każdą zmierzono osobno; wydane razem z ADR-05. Jedną grupę zawężono, bo samo słowo było wieloznaczne.
- **Rozważane warianty:** zestaw 15 jednostek – +2,0 pkt, ale 2 alarmy obserwatora, odrzucony; 6 grup z formami odmienionymi odrzuconych, bo obniżały precyzję; rezygnacja z wydania – rozważana, bo zysk jest mały.
- **Skutki:** synonimy to mała dźwignia: V0 +1,6 pkt, a po ADR-05 ok. +0,2 pkt. Właściwym lekiem miało być dopasowanie terminów po rdzeniu w kodzie, „po odciskach, osobną zmianą”; w kodzie z 10.11.2026 nadal jest dopasowanie całych słów – **niepewne**, czy zmianę porzucono, czy zapomniano.
- **Wdrożenie:** dom-budowa 2.7.0, `tools/wiedza_synonimy.txt`.
- **Źródło:** `Z3-synonimy.md`, `rano/2026-10-25-Z3.md`, `rano/pytania.md` (folder planów usunięto 2026-11).

## ADR-07: Odciski znaczenia liczone lokalnie, bez usługi zewnętrznej
- **Status:** przyjęta
- **Data:** 2026-10-25 (zgoda), 2026-10-26 (wydanie)
- **Kontekst:** Indeks szuka po słowach, a co najmniej 94% przeoczeń z audytu leżało w tym samym temacie, tylko innymi słowami.
- **Decyzja:** lokalny model embeddingów (Ollama, bge-m3) na Macu; wektory w osobnym pliku obok indeksu, liczone przyrostowo na końcu `sync`; brak Ollamy = krok pominięty po cichu, bez nowego kroku dla inwestora. Każda nowa usługa zewnętrzna wymaga zgody inwestora.
- **Rozważane warianty:** embeddingi z usługi w chmurze (Bedrock) – „na razie nie”, wraca, gdy komputer nie da rady albo pomiar pokaże przewagę; porównania modeli nie robiono. Wektory w pliku indeksu – odrzucone (kopia dla czatu ma ich nie zawierać). Liczenie przed publikacją – odrzucone: sama wysyłka indeksu zajmuje ok. 104 s z budżetu 110 s.
- **Skutki:** pełne przeliczenie 2261 tez: odciski 97,5 s i listy 72,4 s; przyrost po jednym filmie 8,5–10 s. Ollama musi działać jako usługa systemowa. Instalacja przestawiła domyślnego Pythona – cofnięte do 3.9.
- **Wdrożenie:** dom-budowa 2.9.0, `tools/wiedza_sens.py`.
- **Źródło:** `Z0-decyzje-i-git.md`, `Z4-odciski-podobne.md`, `rano/2026-10-26-Z4.md` (folder planów usunięto 2026-11).

## ADR-08: Listy „podobne” w kopii dla czatu – wydane mimo niespełnionego kryterium
- **Status:** przyjęta
- **Data:** 2026-10-26
- **Kontekst:** Telefon nie policzy odcisku pytania. Kryterium zadania: +10 pkt recall@widziane przy najwyżej 1,3× znaków.
- **Decyzja:** Mac liczy dla każdej tezy do 10 sąsiadów (próg 0,55) i publikuje tabelę w kopii; `szukaj --krotko` dopisuje do 8 linii „Podobne do trafień” (próg 0,7, sąsiedzi 5 pierwszych trafień). Ranking hybrydowy `--sens` działa tylko na Macu. Wydane decyzją inwestora.
- **Rozważane warianty:** wynik to +5,1 pkt (47,5% wobec 42,4%) przy 1,25× znaków – remis z `--limit 33` po słowach (47,5% przy 1,29×); `--sens` daje +3,6 pkt bez dodatkowych znaków. Opcje: listy bez sekcji w wyniku albo brak wydania. Wybrano sekcję, bo listy są potrzebne i tak (duplikaty, nocne porównanie, przegląd między tematami), a żadne z 53 pytań nie wypadło gorzej.
- **Skutki:** kopia większa o 3,8%. Pożytek maleje z liczbą wyników: ok. +7 pkt Kluczowych przy 25–40 liniach, +3 przy 60, około zera od 100 linii i z całym tematem.
- **Wdrożenie:** dom-budowa 2.9.0, `tools/wiedza.py`, `tools/wiedza_sens.py`.
- **Źródło:** `Z4-odciski-podobne.md`, `rano/2026-10-26-Z4.md`, `rano/2026-10-26-Z5.md`, `rano/pytania.md` (folder planów usunięto 2026-11).

## ADR-09: `duplikaty` to lista kandydatów, nie wykrywacz
- **Status:** przyjęta
- **Data:** 2026-10-26
- **Kontekst:** Dawne `duplikaty` po podobieństwie znaków nie znajdowało żadnej pary nawet przy progu 0,6. Duplikaty w bazie to parafrazy – podobieństwo znaków par uznanych za duplikat miało medianę 0,26.
- **Decyzja:** `duplikaty` bierze pary z list podobnych od progu 0,84 (51 par w całej bazie); `--slowa` zostawia starą metodę.
- **Rozważane warianty:** samo wyłączenie `autojunk` i niższy próg znaków – odrzucone, parafrazy zostają poza zasięgiem; niższy próg po znaczeniu – setki par tygodniowo przy tej samej precyzji. Kalibracja na 107 parach ocenionych jako duplikat: żaden próg ani cecha (cosinus, Jaccard, podobieństwo znaków, ich sumy) nie odróżnia duplikatu od pary „bliskiej” – precyzja 6–13% przy częstości bazowej 6,5%.
- **Skutki:** rozpoznanie duplikatu wymaga sędziego (modelu albo inwestora); lista służy przeglądowi tygodnia i nocnemu porównaniu jako źródło kandydatów.
- **Wdrożenie:** dom-budowa 2.9.0, `tools/wiedza.py duplikaty`.
- **Źródło:** `rano/2026-10-26-Z4.md`, `rano/2026-10-25-Z6.md`, `rano/pytania.md` (folder planów usunięto 2026-11).

## ADR-10: Notatnik, zadania i dokumenty poza indeksem
- **Status:** przyjęta (uzupełniona migawką z ADR-22)
- **Data:** 2026-10-25
- **Kontekst:** Planowano osobne tabele, szukanie i odciski dla Notatnika budowy. Notatnik miał ok. 175 wpisów.
- **Decyzja:** zadanie skreślono. Notatnik czytany jest w całości filtrem pól (Etap, Branża, Typ, Status), zadania i harmonogram – filtrem bazy, ściąga projektu – w całości, dokumenty – z przewodnika albo z projektu na claude.ai. Duplikaty w Notatniku sprawdza się odczytem wpisów z tym samym Etapem i Branżą, nie szukaniem 2–3 słów.
- **Rozważane warianty:** indeks Notatnika z własnym FTS i listami podobnych – odrzucony: po zawężeniu zostaje 5–20 wpisów, które czat czyta w całości, a pytania o zadania są strukturalne (status, termin).
- **Skutki:** wraca, gdy Notatnik urośnie do kilkuset aktywnych wpisów. Liczby „5–20 wpisów” nie potwierdzono pomiarem. Migawka kosztorysu w kopii – odłożona; **niepewne**, czy nadal aktualna po przeniesieniu kosztorysu do arkusza (3.0.0).
- **Wdrożenie:** dom-budowa 2.10.0 (`pytanie-do-bazy.md`, `notatka` krok 2).
- **Źródło:** `Z4B-notatnik-w-indeksie.md`, `00-PLAN.md`, `rano/pytania.md` (folder planów usunięto 2026-11).

## ADR-11: Treść bazy do modeli Claude bez filtra danych osobowych
- **Status:** przyjęta
- **Data:** 2026-10-26
- **Kontekst:** Sędzia i przeglądy wysyłały tezy do modelu po filtrze danych osobowych i słów zakazanych (zgoda z 19.10). Filtr wycinał wiedzę: 264 tezy (11,7%) nie trafiły do przeglądu bazy, a w nocnym porównaniu 3 z 12 tez jednej pozycji.
- **Decyzja:** do modeli Claude (ta sama usługa co czat) treść bazy i Notatnika idzie bez filtra; filtr zostaje tylko dla publicznego repo i commitów. Lokalny model – bez ograniczeń; nowa usługa zewnętrzna – po zgodzie inwestora. Zasada: dane osobowe mają nie trafiać do publicznego repo, a nie być niedostępne do przeglądania.
- **Rozważane warianty:** filtr z listą wyjątków i dopasowaniem całych wyrazów – planowany, zbędny po decyzji; przegląd odfiltrowanych tez modelem lokalnym – zbędny.
- **Skutki:** odfiltrowane pozycje oceniono ponownie (187 nowych grup, 6,88 USD). Treści bazy nadal nie wypisuje się do rozmów, logów ani raportów. Dług: martwy kod filtra w narzędziu oceny czatu.
- **Wdrożenie:** dom-budowa 2.10.0, `tools/wiedza_sedzia.py`; nocna kolejka (poza repo).
- **Źródło:** `_zasady.md`, `rano/2026-10-25-Z6.md`, `rano/2026-10-26-Z8.md`, `rano/2026-10-26-Z9.md` (folder planów usunięto 2026-11).

## ADR-12: Porządki w bazie: scalanie bez usuwania, rdzeń zamiast całości
- **Status:** przyjęta
- **Data:** 2026-10-26
- **Kontekst:** Przegląd 35 tematów dał 1030 grup (bliskie 734, zły temat 113, sprzeczność 95, duplikat 88) i 70 grup w Notatniku. Scalanie w Notion jest w praktyce nieodwracalne.
- **Decyzja:** najpierw reguły w procedurze, potem zapis. Zakres: rdzeń 263 grup o wysokiej pewności. Stron się nie usuwa: wycofana teza dostaje status „Nieaktualne” i dopisek „Scalone do…”, wpis Notatnika – „Odrzucone”. Tryb samodzielny: stan Notion sprawdzany przed każdą grupą, log PRZED/PO, skrypt cofnięcia, pilot 10 grup.
- **Rozważane warianty:** decyzja linia po linii dla wszystkich grup – za dużo; tylko duplikaty i sprzeczności – za wąsko; nowy status „Scalone” w Notatniku – odrzucony (zmiana struktury bazy); zgoda na każdą paczkę – zastąpiona trybem samodzielnym po próbce 8/10 trafnych.
- **Skutki:** 166 grup zrobionych, 97 pominiętych z powodem; 106 tez wycofanych, 20 wpisów Notatnika odrzuconych, 5 nowych sprzeczności. Wiersz główny wybiera się wg pełni wiersza, nie długości tezy. Liczba duplikatów to dolna granica: sędzia tematu znalazł 13 z 46 powtórzeń znanych z audytu.
- **Wdrożenie:** dom-budowa 2.8.0, 2.8.1 (`wiedza/references/porzadki.md`, `notatka/references/scalanie.md`).
- **Źródło:** `Z6-przeglad-bazy.md`, `Z7-scalanie.md`, `rano/2026-10-25-Z6.md`, `rano/2026-10-26-Z7.md` (folder planów usunięto 2026-11).

## ADR-13: Przegląd między tematami: próg 0,65; nowy temat i runda 2
- **Status:** przyjęta w części (próg), otwarta w części
- **Data:** 2026-10-26 (pomiar), 2026-11-04 (decyzja)
- **Kontekst:** Po scaleniu sprawdzono pary podobnych tez z różnych tematów – 6698 par do oceny.
- **Decyzja:** nie dokańczać oceny par; w przyszłych przeglądach brać pary między tematami od podobieństwa 0,65.
- **Rozważane warianty:** dokończenie do 0,60 (ok. 8 USD) albo całości (ok. 21 USD) – odrzucone: 2039 ocenionych par dało 71 grup i 0 duplikatów; grupę daje 17% par przy podobieństwie ≥ 0,70, 4% w paśmie 0,65–0,70 i 2% w paśmie 0,60–0,65.
- **Skutki:** po porządkach między tematami prawie nie ma powtórzeń (96% par to tezy pokrewne). Otwarte, czeka na przegląd inwestora: propozycja nowego tematu (4 tezy główne, 21 dodatkowych) i zakres drugiej rundy scalania (rdzeń wg reguł jest pusty). Decyzję o progu podjął 4.11 asystent na zgodzie ogólnej – inwestor może ją zmienić.
- **Wdrożenie:** brak w repo.
- **Źródło:** `rano/2026-10-26-Z6.md`, `rano/pytania.md`, `NOC-2026-11-04.md` (folder planów usunięto 2026-11).

## ADR-14: Nocne przetwarzanie etapami: porównanie z całym tematem przed zapisem
- **Status:** przyjęta; kryterium odbioru otwarte
- **Data:** 2026-10-26
- **Kontekst:** Audyt: w trybie indeksu 63% powiązań oznaczonych, 18% widzianych i nieoznaczonych, 19% nigdy niepokazanych; potwierdzeń nie podpinano wcale (0 w 79 pozycjach).
- **Decyzja:** krok 1 – same tezy do pliku; krok 2 – skrypt i model porównują każdą tezę z całym tematem i 15 trafieniami z innych tematów; krok 3 – zapis wg listy relacji; krok 4 – kontrola śladów po synchronizacji. Potwierdzenie czy powtórzenie rozstrzyga kod regułą niezależności źródeł, nie model. Ta sama zasada obowiązuje na czacie.
- **Rozważane warianty:** w wersji czatu `szukaj` z filtrem tematu dla każdej tezy (limit 40) – odrzucone, przy średnio 108 tezach w temacie to nie „cały temat”; wybrano jedną listę tematu. Ostrzejszy prompt ekstrakcji – odłożony (19 tez zamiast dawnych 11 wierszy).
- **Skutki:** pomiar zastępczy: lista łapie 88% relacji audytu przy 0,56 USD na pozycję (górna granica). Kryterium „≥ 85% w audycie po zmianie” niesprawdzone; **niepewne**, czy noc testowa się odbyła – są statystyki z 10 pozycji przerobionych 26.10, a status mówi „noc testowa i audyt niezrobione”.
- **Wdrożenie:** nocna kolejka (poza repo); dom-budowa 2.10.0, `wiedza/references/porownanie.md`.
- **Źródło:** `Z8-etap-porownania-noc.md`, `rano/2026-10-26-Z8.md`, `rano/Z8-A5-projekt.md`, `STAN-PRAC-2026-11-01.md` (folder planów usunięto 2026-11).

## ADR-15: Stały pomiar: reguła sędziego, hybryda w kontroli, mini-audyt
- **Status:** przyjęta
- **Data:** 2026-10-27
- **Kontekst:** Zgodność sędziego LLM z oceną ręczną liczono regułą „trafny” ↔ ocena co najmniej 1; kontrola nocna porównywała dwa silniki; jakość zapisu sprawdził tylko jednorazowy audyt.
- **Decyzja:** zgodność liczona regułą „trafny” ↔ ocena 2; kontrola dostaje trzeci silnik (hybryda słów i znaczenia); mini-audyt 10 pozycji i trend czatu w tle co 30 dni; trend liczy stały wariant V0 jako miernik dryfu bazy i indeksu.
- **Rozważane warianty:** dawna reguła – 7/10 zgodnych wobec 10/10 przy nowej; mini-audyt tylko ręcznie albo co 60 dni – odrzucone; trend „aktualnego wariantu” – odłożony.
- **Skutki:** ocena 30 par przez inwestora: zgodność 21/29 (sędzia 2 → trafny 8/10, 0 → nietrafny 8/9, 1 → pół na pół); rozbieżności niemal tylko przy ocenie „częściowo”. Pierwszy mini-audyt: 73,7% powiązań uwzględnionych, 6,74 USD. Lekcja: zestaw do oceny ręcznej jest celowo zrównoważony – trzeba to napisać w instrukcji, inaczej wygląda na słabe szukanie.
- **Wdrożenie:** dom-budowa 2.10.0 (`tools/wiedza_sedzia.py`, `wiedza_jakosc.py reczna --wczytaj`); kontrola i mini-audyt w nocnej kolejce (poza repo).
- **Źródło:** `Z9-staly-pomiar.md`, `rano/2026-10-26-Z9.md` (folder planów usunięto 2026-11).

## ADR-16: Procedura czatu z trzema poziomami głębokości
- **Status:** zastąpiona przez ADR-23 jako droga domyślna (zostaje drogą zapasową)
- **Data:** 2026-10-27
- **Kontekst:** Czat znajdował wiedzę, ale jej nie używał. Inwestor postawił cel „co najmniej 95% zaufania” – przede wszystkim na telefonie.
- **Decyzja:** poziomy szybko (limit 60), normalnie (limit 100 i cały główny temat), dokładnie (limit 100 i 2 tematy); długie wyniki czytane porcjami; odpowiedź dwuwarstwowa (skrót ze wszystkimi Kluczowymi, potem rozwinięcie); „nie ma w bazie” dopiero po całej drodze; internet jako podpora bez propozycji zapisu.
- **Rozważane warianty (53 pytania, Kluczowe / Ważne widoczne):** 25 linii – 48 / 49%; limit 100 – 79 / 80%; 100 i 1 temat – 90 / 91% przy 77 tys. znaków; 100 i 2 tematy – 96 / 94% przy 117 tys.; `--sens` przy dużych limitach – około zera; cel „najwyżej 4 wywołania” – nieosiągalny, bo narzędzie ucina wynik powyżej ok. 30 tys. znaków.
- **Skutki:** odpowiedzi od pytania do końca (15 pytań): Kluczowe użyte 73% → 89% w skrócie → 100% po rozwinięciu; Ważne 42% → 81% (cel 90% niespełniony). Wobec pełniejszego wzorca (ADR-17) poziom „dokładnie” wczytuje tylko ok. 62% trafnych tez.
- **Wdrożenie:** dom-budowa 2.10.0, `wiedza/references/pytanie-do-bazy.md`.
- **Źródło:** `Z5-procedura-czatu.md`, `rano/2026-10-26-Z5.md`, `rano/pytania.md` (folder planów usunięto 2026-11).

## ADR-17: Wzorzec pomiaru: pełny odrzucony, skalibrowany przyjęty
- **Status:** przyjęta
- **Data:** 2026-10-27
- **Kontekst:** Wzorzec z ADR-04 powstał z puli szukania i tematów pytania, więc mógł nie widzieć trafnych tez spoza niej („ślepota puli”).
- **Decyzja:** dla 10 pytań inwestora model ocenił każdą widoczną tezę bazy (2198). Wzorcem do dalszych pomiarów jest wersja potwierdzona dwukrotnie (Sonnet, potem Opus bez etykiety istotności): 598 trafnych tez, w tym 91 Kluczowych – trzon na pewno trafnych, nie komplet.
- **Rozważane warianty:** pełny wzorzec bez kalibracji (1604 tezy, 62% spoza puli) – odrzucony: zgodność z ponowną oceną 61,7% przy progu 80% (spoza puli 36,7%, z puli 86,7%), bo sędzia widział etykietę istotności i paczki „prawie wszystko nie na temat”. Drugi przebieg kalibracji z innym ziarnem – niezrobiony.
- **Skutki:** ta sama droga dostaje różne liczby zależnie od wzorca (limit 100: 33% / 52% / 63%). Powtarzalność ocen ok. 62%, więc różnice poniżej 5 pkt to szum, a decyzje wydawnicze wymagają 2 przebiegów na pytanie. Przy okazji: wyłączenie pamięci podręcznej promptu dla jednorazowych wywołań obniżyło koszt o 36%.
- **Wdrożenie:** zbiory poza repo; pojęcia „wzorzec” i „pokrycie” w `wiedza/references/karty.md` i runbooku.
- **Źródło:** `Z5B-ksiazka-pilot.md`, `rano/2026-10-26-Z5B.md`, `rano/2026-10-27-Z5B-kalibracja.md` (folder planów usunięto 2026-11).

## ADR-18: Książka w Notion (rozdziały z przypisami)
- **Status:** odrzucona
- **Data:** 2026-10-27 (rekomendacja „nie”), 2026-11-01 (zamknięcie)
- **Kontekst:** 26.10 przyjęto architekturę docelową „kartoteka + książka”: rozdział na temat, ciągły tekst z przypisami do tez, czytany przez czat przez spis treści w Notion.
- **Decyzja:** książki jako drogi czatu do wiedzy nie budujemy; jej rolę przejęły karty (ADR-23).
- **Rozważane warianty:** pilot rozdziału (147 tez, 120 tys. znaków, 0 sierot, 0 błędnych przypisów) – w obrębie tematu pokazał 76% trafnych tez wobec 15% z `szukaj --limit 40`; wersja zwięzła – ten sam wynik przy 0,51× znaków. Ale pytania rozkładają się na wiele tematów: „spis spisów” dał 65,8% / Kluczowe 72,2% przy 121 tys. znaków wobec 66,8% / 66,7% przy 134 tys. dla „dokładnie” (0,90× znaków, kryterium 0,70×), a w tematach z rozdziałem −4,2 pkt (kryterium +20). Wybór podrozdziałów gubi ok. ¼ trafień. Koszt całości: 55–76 USD (Sonnet), ok. 100 USD (Opus).
- **Skutki:** inwestor uznał, że książki nie będzie czytał w całości. Niewdrożony pomysł poboczny: „spis spisów” jako wybór tematów dawał ten sam wynik przy 0,73× znaków – pomiaru na 53 pytaniach nie powtórzono.
- **Wdrożenie:** brak.
- **Źródło:** `00-PLAN.md`, `Z5B-ksiazka-pilot.md`, `Z5C-ksiazka-dla-agenta.md`, `rano/2026-10-26-Z5B.md`, `rano/2026-10-27-Z5C.md` (folder planów usunięto 2026-11).

## ADR-19: Poziom „cały etap” na telefonie
- **Status:** zastąpiona przez ADR-23 (polecenie zostaje dla pracy na Macu)
- **Data:** 2026-10-28
- **Kontekst:** Pytanie inwestora: czy czytanie całej wiedzy etapu gubi tezy w długim kontekście i co będzie, gdy baza urośnie 2×.
- **Decyzja:** dodano polecenie `etap` (tezy Kluczowe i Ważne etapu w częściach po 25 tys. znaków) i czwarty poziom procedury. Po teście z telefonu Kluczowe przeniesiono na początek, a poziom zostawiono tylko dla Maca.
- **Rozważane warianty (10 pytań, wzorzec 598):** cała wiedza etapu (921 tez, 288 tys. znaków) – w wejściu 74,4% / Kluczowe 90,1%, po czytaniu 67,6% / 85,7%; „dokładnie” po czytaniu 60,5% / 56,0%. Model pomija ok. 9% tego, co ma przed oczami; baza 1,7× obniża czytanie tych samych tez o ok. 6 pkt. Układ tez wg czynności zamiast tematów – 66,1%, bez zysku, odrzucony.
- **Skutki:** test z telefonu: czat przeczytał w całości 3 z 16 części – rzetelnie czyta ok. 75 tys. znaków. Przy bazie 2× cała wiedza etapu (ok. 330 tys. tokenów) nie zmieści się w oknie. Wąskie gardło to dobór tego, co trafia do modelu, nie czytanie ani ułożenie.
- **Wdrożenie:** dom-budowa 2.11.0, 2.12.2 (`tools/wiedza.py etap`).
- **Źródło:** `Z12-czytaj-wszystko-czy-filtruj.md`, `rano/2026-10-28-Z12.md`, `rano/2026-10-28-dziennik-sesji.md` (folder planów usunięto 2026-11).

## ADR-20: Filtr po kolumnach: „czynność” tylko w indeksie, etap wielokrotny nie
- **Status:** przyjęta w części (tagi czynności), odrzucona w części (etap wielokrotny, nowe pola w Notion)
- **Data:** 2026-10-28
- **Kontekst:** Czy da się kolumnami – istniejącymi albo nowymi – odfiltrować to, co do pytania nie pasuje.
- **Decyzja:** lista 68 czynności budowy i tagi tez trzymane lokalnie, poza Notion; pola „Czynność” i „Etapy” w Notion nie powstają. Warunek powrotu do filtra kolumnami na czacie: wybór modelu daje co najmniej 80% trafnych przy najwyżej 200 tys. znaków.
- **Rozważane warianty:** wyrocznia (zna odpowiedź), czynność i etapy – 71,1% po czytaniu przy 71 tys. znaków, zbiór o 29% mniejszy niż przy temacie. Model znający tylko pytanie – wybiera za dużo (91% przy 362 tys. znaków) albo przy 20 czynnościach daje 62,5% przy 253 tys. (gorzej niż cała wiedza etapu). Etap wielokrotny – +1,2 pkt (75,6% wobec 74,4%), odrzucony. Pola w Notion od razu – odrzucone (ok. 2200 zapisów bez dowodu zysku).
- **Skutki:** tagi stały się kartami czynności (ADR-23), bez pomiaru pokrycia. Tagowanie 1635 tez: 4,43 USD. Etykiety błędne wg próbki 60 tez: etap 13–17%, rodzaj 3%, istotność 7–10%.
- **Wdrożenie:** dom-budowa 2.13.0 (`tools/wiedza_karty.py taguj`, `importuj-tagi`).
- **Źródło:** `rano/2026-10-28-Z12.md`, `rano/2026-10-28-Z12-D.md`, `rano/pytania.md` (folder planów usunięto 2026-11).

## ADR-21: Pytania o zamknięcie etapu: filtr po rodzaju, nie okno etapów
- **Status:** przyjęta
- **Data:** 2026-10-28
- **Kontekst:** Pytanie „co sprawdzić, zanim ruszy kolejny etap” traciło najwięcej: jego trafne tezy leżą we wszystkich etapach (55 z 60 trafnych tez „spoza etapu” pochodziło z tego jednego pytania).
- **Decyzja:** dla takich pytań dokładane są tezy rodzaju „Kontrola / odbiór” i „Kolejność prac” ze wszystkich etapów (`etap --kontrola`); procedura `etap` kieruje „co i jak kontrolować” do bazy wiedzy, nie tylko do Notatnika. Później powstały osobne karty kontroli i zamknięcia etapu.
- **Rozważane warianty:** sam filtr etapu – 53,7% trafnych dla tego pytania; okno „etap bieżący i następny” – odzyskałoby 23 z 60 tez; etap wielokrotny – 8 z 60; filtr rodzaju – 79% przy 133 tys. znaków, a razem z etapem 86,6% (92,6% dla tego pytania) przy 342 tys.
- **Skutki:** przyczyną nie były błędne etykiety, tylko pytanie obejmujące kilka etapów. Rekomendowany pomiar na 53 pytaniach przed zmianą procedury nie został zrobiony – wdrożono od razu; **niepewne**, czy pominięto go świadomie. Test z telefonu: czat odpowiedział samym Notatnikiem, stąd poprawka w 2.12.2.
- **Wdrożenie:** dom-budowa 2.11.0, 2.12.2, 2.13.0–2.13.1.
- **Źródło:** `rano/2026-10-28-Z12.md`, `rano/2026-10-28-Z12-D.md`, `rano/2026-10-28-dziennik-sesji.md` (folder planów usunięto 2026-11).

## ADR-22: Praca bez konektora Notion: lokalny MCP, launchd, migawka, Skrzynka
- **Status:** przyjęta
- **Data:** 2026-10-28
- **Kontekst:** Konektor Notion na claude.ai został zablokowany na poziomie organizacji. Telefon stracił odczyt Notatnika i zadań oraz zapis; stanęły zaplanowane zadania i nocna kolejka.
- **Decyzja:** (1) Mac: lokalny serwer MCP Notion z własnym logowaniem; (2) przeglądy Dziennika przez launchd i `claude -p` zamiast zadań claude.ai; (3) telefon czyta indeks i migawkę otwartych wpisów Notatnika i zadań z kopii, a pola dostępu z pliku w projekcie; (4) telefon zapisuje do dokumentu „Skrzynka”, opróżnianego co godzinę; (5) nic nie cofać, gdy konektor wróci.
- **Rozważane warianty:** wniosek o odblokowanie – niewybrany; osobne prywatne konto – odłożone (mniejszy limit, a kupuje tylko zapis z telefonu); inny asystent AI – trzeci kanał do utrzymania; skrzynka w prywatnym repo – zostaje jako zapas.
- **Skutki:** pozycja Skrzynki to data, treść dosłownie i intencja słowami, bez pól Notion – struktura baz może się zmienić, a bez Notion nie da się jej sprawdzić. Przebieg godzinowy: ok. 0,5–0,8 USD. Stąd zasada, że każde rozwiązanie oparte na konektorze ma drogę zapasową.
- **Wdrożenie:** dom-budowa 2.12.0–2.12.1, ja 1.6.0–1.6.1 (`tools/migawka.py`, `wpisy/references/skrzynka.md`); automaty poza repo.
- **Źródło:** `rano/2026-10-28-dziennik-sesji.md` (folder planów usunięto 2026-11).

## ADR-23: Karty wiedzy: wybór tez robi Mac, nie czat
- **Status:** przyjęta
- **Data:** 2026-10-29
- **Kontekst:** Czat szukający sam widzi przy pytaniach szerokich ok. 60% trafnych tez, „cały etap” przerasta telefon (ADR-19), a dobry wybór mieści się w ok. 71 tys. znaków (ADR-20).
- **Decyzja:** model na Macu czyta całą bazę w porcjach (dwa przebiegi w różnej kolejności) i zapisuje gotowe listy tez: karty pytań (rdzeń i rozszerzenie) oraz karty czynności (tagi). Karty leżą w tym samym pliku indeksu; telefon wybiera kartę i czyta ją w całości z dopełnieniem z szukania. Poziomy z ADR-16 zostają drogą zapasową.
- **Rozważane warianty:** dobór kodem (głosowanie kilku sformułowań, tagi czynności, rodzaj) do 75 tys. znaków – planowany na tę noc, w źródłach brak jego wyniku (**niepewne**); wybór kolumn przez czat – ADR-20; książka – ADR-18.
- **Skutki:** pokrycie wzorca: rdzeń samym wyborem modelu 68% (Kluczowe 88%), z rozszerzeniem 89% (91%). Symulacja telefonu, 10 pytań: 83% trafnych i 100% Kluczowych przy 5,6 wywołania wobec 50% i 56% przy 10,4 dla „dokładnie”; 12 pytań spoza wzorca: 84% / 92% wobec 72% / 90%. Długi: karty kolejnych etapów dopiero, gdy etap nadejdzie; dane kart leżą poza repo – bez kopii zapasowej odbudowa kosztuje dziesiątki USD.
- **Wdrożenie:** dom-budowa 2.13.0 (`tools/wiedza_karty.py`, `wiedza.py karty` / `karta`, `wiedza/references/karty.md`).
- **Źródło:** `00-PLAN.md` (wiersz Z13 – osobnej karty zadania ani raportu nie było), `rano/2026-10-28-dziennik-sesji.md`, `STAN-PRAC-2026-11-01.md` (folder planów usunięto 2026-11).

## ADR-24: Ocena ścisła po wyborze inkluzywnym, rdzeń 200 tez
- **Status:** przyjęta
- **Data:** 2026-10-29 (skrypt poza narzędziem), 2026-11-04 (polecenie w narzędziu)
- **Kontekst:** Wybór modelu jest szeroki (300–1000 tez na kartę), a telefon czyta ok. 75 tys. znaków.
- **Decyzja:** po wyborze każda teza karty pytań dostaje ocenę 2 (konieczna), 1 (pokrewna) albo 0. Rdzeń to oceny 2 i najlepsze oceny 1 do 200 tez; reszta pokrewnych idzie do rozszerzenia. Tezy wzorca dopisano do rdzenia kart odpowiadających pytaniom inwestora. Nowe tezy przechodzą tę samą ocenę przy aktualizacji godzinowej.
- **Rozważane warianty:** sam wybór inkluzywny – za duży na telefon; ostrzejszy prompt wyboru – niemierzony; nowe tezy wpuszczane do rdzenia bez oceny – tak działało od 29.10 do 4.11 (dług, spłacony).
- **Skutki:** rdzeń uzupełniony wzorcem daje 100% pokrycia – to miara wobec jednego wzorca, nie „prawda absolutna”, bo tez dodanych później wzorzec nie ocenia. Ocena 571 zaległych tez kosztowała 0,61 USD; 17 kart z rdzeniem do 200 tez, pokrycie 99% / Kluczowe 100%. **Niepewne:** tabela statusu planu mówi o gałęzi niescalonej, a CHANGELOG i podsumowanie nocy – o wydaniu 2.16.6.
- **Wdrożenie:** dom-budowa 2.16.6, `tools/wiedza_karty.py ocen`.
- **Źródło:** `00-PLAN.md`, `NOC-2026-11-04.md`, `README-lokalne.md` (folder planów usunięto 2026-11).

## ADR-25: Budżet telefonu 75 tys. znaków: podział kart i krótsze tezy
- **Status:** przyjęta
- **Data:** 2026-10-30
- **Kontekst:** Test z telefonu pokazał, że rzetelnie czytane są ok. 3 części po 25 tys. znaków, a wszystko ponad to jest przeglądane. Jedna karta kontroli etapu miała 4–5 części.
- **Decyzja:** projektować pod stały budżet – karta pytań ma się mieścić w 3 częściach. Kartę kontroli podzielono na trzy węższe, a tezy bazy skrócono: reguła zostaje w tezie, uzasadnienie i anegdota idą do „Szczegółów”.
- **Rozważane warianty:** czytanie zawsze wszystkich Kluczowych – wystarczy do ok. 220 Kluczowych (było 147, ok. 50 tys. znaków); budżet liczby Kluczowych na etap – propozycja niewdrożona (ADR-27).
- **Skutki:** skrócono 1055 z 2199 tez (średnio 304 → 243 znaki), więc telefon czyta ok. 308 tez zamiast 246. Skracanie zmieniło treść w Notion skryptem z kontrolą liczb i plikiem cofnięcia. Przy zbliżonych trafieniach wybierana jest karta bieżącego etapu. **Niepewne:** ta praca nie miała karty zadania ani raportu – liczby pochodzą z CHANGELOG.
- **Wdrożenie:** dom-budowa 2.13.1, 2.13.2.
- **Źródło:** `rano/2026-10-28-dziennik-sesji.md`, skrypty `z14/` (folder planów usunięto 2026-11).

## ADR-26: Tryb głęboki: pytanie złożone liczone poza telefonem
- **Status:** przyjęta
- **Data:** 2026-10-29 (wersja lokalna), ok. 2026-10-30 (GitHub Actions)
- **Kontekst:** Pytanie złożone, którego nie pokrywa żadna karta, wymaga przeczytania całej bazy – telefon tego nie udźwignie.
- **Decyzja:** czat zostawia pytanie w prywatnym repo kopii (osobny token zapisu tylko do tej ścieżki) i od razu daje wstępną odpowiedź z karty; pełną odpowiedź pisze model czytający całą bazę i odkłada ją do repo. Wykonawcą jest workflow GitHub Actions w repo kopii; lokalny automat Maca zostaje jako zapas.
- **Rozważane warianty:** tylko lokalny automat na Macu – pierwsza wersja, wada: Mac musi nie spać; czytanie całej bazy przez czat – ADR-19.
- **Skutki:** 3–6 minut i ok. 1–2 USD na pytanie. **Niepewne:** przejście na Actions nie ma wpisu w CHANGELOG, a `wiedza/references/tryb-gleboki.md` (stan z 2.13.0) nadal opisuje wykonanie na Macu, podczas gdy `docs/system-wiedzy.md` podaje Actions jako drogę główną. Dług: strona dostępu bez sekcji trybu głębokiego.
- **Wdrożenie:** dom-budowa 2.13.0 (`wiedza/references/tryb-gleboki.md`); workflow i automat poza repo.
- **Źródło:** `STAN-PRAC-2026-11-01.md`, `README-lokalne.md`, `00-PLAN.md` (folder planów usunięto 2026-11).

## ADR-27: Brama przy zapisie i budżet Kluczowych
- **Status:** otwarta
- **Data:** 2026-10-28
- **Kontekst:** Baza rośnie „film za filmem”. W próbce 16 z 30 losowych tez Kluczowych i Ważnych to relacje z filmu (opinia, anegdota), a wśród tez trafnych dla pytań – 1 z 30.
- **Decyzja:** brak – jest propozycja: drobne uzupełnienie jako dopisek do istniejącej tezy (do 300 znaków) zamiast nowego wiersza; relacja z filmu nie staje się osobną tezą; istotność należy do faktu, a nie do filmu; budżet liczby Kluczowych na etap.
- **Rozważane warianty:** wdrożenie od razu – odrzucone bez pomiaru; rekomendowany pierwszy krok – pomiar „fakt czy relacja” na 598 trafnych tezach (ok. 1 USD) i próba na 10 filmach – niezrobiony.
- **Skutki:** to jedyna z propozycji, która spowalnia wzrost bazy; pozostałe (kolumny, układ) tego nie robią. Ryzyka: nadpisanie „Szczegółów”, zgubienie szczegółu w cudzym wierszu, podniesienie istotności przez relację.
- **Wdrożenie:** brak.
- **Źródło:** `rano/2026-10-28-Z12-D.md`, `rano/pytania.md`, `rano/2026-10-28-dziennik-sesji.md` (folder planów usunięto 2026-11).

## ADR-28: Nocny wykonawca zadań: przygotowuje i mierzy, nie wydaje
- **Status:** przyjęta
- **Data:** 2026-10-25
- **Kontekst:** Zadania planu były duże, limit konta wspólny z kolejką filmów, a inwestor chciał rano liczb i dowodów, nie opinii.
- **Decyzja:** skrypt uruchamia karty zadań bez inwestora, każde zadanie repo w osobnej kopii roboczej i gałęzi. Zakazane: push, zapisy w Notion, wydania, usuwanie. Pytania z rekomendacją trafiają do jednego pliku, decyzje domyślne są jawnie wypisane w raporcie; przy progu limitu tygodnia praca staje, na okno 5-godzinne czeka. Rano inwestor przegląda i wydaje. Każda karta ma kryteria odbioru w liczbach i właściciela plików – jedno zadanie na plik naraz.
- **Rozważane warianty:** wydania w nocy – odrzucone (publiczne repo, trudno odwracalne zapisy w Notion); wyjątki za zgodą: scalanie w trybie samodzielnym (ADR-12) i noc 4/5.11 na zgodzie ogólnej.
- **Skutki:** raporty zawierają tylko liczby, numery i ścieżki. Lekcja: polecenie wypisujące listę procesów ujawniło w logu sesji fragment promptu z treścią bazy – nie powtarzać. Skrypt wykonawcy zachowano w prywatnym archiwum planów (poza repo).
- **Wdrożenie:** poza repo.
- **Źródło:** `00-PLAN.md`, `PROMPTY.md`, `_zasady.md`, `rano/RAPORT-2026-10-26.md` (folder planów usunięto 2026-11).

## ADR-29: Dokumentacja: część publiczna ogólna, szczegóły prywatne poza repo
- **Status:** przyjęta
- **Data:** 2026-11-04
- **Kontekst:** Za rok inwestor albo nowy agent ma w 15 minut zrozumieć system i odtworzyć go po awarii. Repo jest publiczne, więc ścieżki, nazwa repo kopii i terminy tokenów nie mogą w nim leżeć.
- **Decyzja:** w repo dwa ogólne pliki (mapa i runbook) z nazwami zmiennych bez wartości; wszystko prywatne w lokalnym README poza repo. Kryterium odbioru: test „obcego czytelnika” – nowa sesja bez kontekstu odpowiada na pytania kontrolne tylko z tych plików.
- **Rozważane warianty:** jedna pełna dokumentacja w repo – wykluczona przez prywatność; test dymny 6 sesji po zmianach procedur – pominięty (koszt, mała wartość po przeglądzie statycznym).
- **Skutki:** test dał 6/6 poprawnych odpowiedzi. Lokalne README leżało w folderze planów; 10.11.2026 przeniesiono je do prywatnego folderu importu wiedzy i poprawiono odesłanie w runbooku. Dług: brak regularnej kopii zapasowej danych poza repo.
- **Wdrożenie:** dom-budowa 2.16.6 (`docs/system-wiedzy.md`, `docs/wiedza-runbook.md`).
- **Źródło:** `Z11-dokumentacja.md`, `README-lokalne.md`, `NOC-2026-11-04.md` (folder planów usunięto 2026-11).

---

## Pytania otwarte bez osobnego wpisu

Stan na 5.11.2026 wg źródeł; każde warto zamknąć osobnym wpisem, gdy zapadnie decyzja.

- **Pierwsza noc kolejki po przepięciu na lokalny MCP Notion** – zaplanowane 2–3 pozycje przy inwestorze, potem audyt (ADR-14); od 28.10 kolejka nie była uruchamiana w nocy.
- **Wariant aktualnej drogi w trendzie czatu** – trend liczy tylko stały V0 (ADR-15); dopisanie wariantu kart odłożone.
- **Pokrycie kart czynności** – niemierzone (ADR-20, ADR-23).
- **Karty pytań dla kolejnych etapów** – budować, gdy etap nadejdzie; wymaga zgody na koszt i limit tygodnia.
- **Fakt czy relacja** – pomiar za ok. 1 USD, od którego zależy ADR-27.
- **Dopasowanie synonimów po rdzeniu** – ADR-06.
- **„Spis spisów” jako wybór tematów w drodze zapasowej** – ADR-18; po wprowadzeniu kart prawdopodobnie bez znaczenia.
- **Nowy temat i druga runda scalania** – ADR-13, czeka na przegląd 25 linii przez inwestora.
- **Rozbieżności w promptach nocnej kolejki** (duplikat w Notatniku szukany tekstem zamiast filtrem pól; nocne tezy trafiają do kart dopiero przy pierwszym przebiegu godzinowym rano) – odnotowane 4.11, niski priorytet.
- **Kroki ręczne inwestora bez potwierdzenia** – odświeżenie pluginów i instrukcji projektu na claude.ai, regularna kopia zapasowa danych poza repo.
