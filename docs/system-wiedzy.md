# System wiedzy budowy – mapa

Przegląd dla człowieka (i dla nowego agenta): z jakich części składa się obsługa bazy wiedzy, kto co uruchamia, co mierzymy
i dlaczego zrobiono to tak, a nie inaczej. Procedury dla asystenta są w `plugins/dom-budowa/skills/wiedza/` – ten plik ich nie
zastępuje, tylko pokazuje całość. Co robić, gdy coś przestaje działać: `docs/wiedza-runbook.md`.

Stan: 4.11.2026 (dom-budowa 2.16.3, ja 1.8.1). Wszystkie części poniżej działają; to, co jeszcze otwarte, jest w sekcji „Znane długi”.

## W jednym obrazku

```
Notion (jedyne źródło prawdy: Informacje WI, Tematy, Rozmowy i źródła ZRD, Rejestr sprzeczności SP, Notatnik, zadania)
   │  odczyt tokenem integracji (tylko do odczytu)                      ▲ zapisy: wyłącznie asystent przez Notion MCP
   ▼                                                                    │ (Mac: launchd + claude -p; czat: konektor)
Mac inwestora: tools/wiedza.py sync ──► wiedza.sqlite (FTS5, synonimy, listy podobnych, karty) + wektory.sqlite (Ollama, bge-m3)
   │  tools/migawka.py: otwarte wpisy Notatnika i zadania ──► migawka.md
   │  tools/wiedza_karty.py: karty wiedzy (model Claude na Macu) ──► tabele karty w wiedza.sqlite
   ▼  wiedza.py publikuj (token zapisu, tylko Mac)
Prywatne repo kopii: wiedza.sqlite · wiedza.py · migawka.md · pytania/ i odpowiedzi/ (tryb głęboki) · workflow GitHub Actions
   │  odczyt tokenem tylko do odczytu                                   ▲ Skrzynka: dokument Claude „📥 Skrzynka”
   ▼                                                                    │ (zapisy z telefonu, gdy Notion w czacie nie działa)
Czat na telefonie (claude.ai, pluginy ja + dom-budowa): karty → odpowiedź z numerami WI, „Na czym się opieram”, tryb głęboki
```

## Części

| Część | Rola | Szczegóły |
|---|---|---|
| Notion | Jedyne źródło prawdy. Nic nie zapisuje się do indeksu, indeks nigdy nie zapisuje do Notion | `references/notion-wiedza.md` |
| Indeks (`tools/wiedza.py`) | Lokalna kopia czterech baz wiedzy w jednym pliku SQLite poza repo: szukanie po słowach (FTS5, synonimy z `tools/wiedza_synonimy.txt`, ranking bm25, kilka sformułowań naraz, wynik zwarty `--krotko`), `temat`, `etap`, `duplikaty`, `zrodla`, `stan`, `publikuj` | `references/indeks.md`, `references/indeks-awarie.md` |
| Odciski i listy podobnych (`tools/wiedza_sens.py`) | Lokalny model embeddingów (Ollama, bge-m3) liczy „odcisk znaczenia” każdej tezy w trakcie `sync`; z nich powstają listy najbliższych znaczeniowo, które jadą do kopii dla czatu (telefon nie liczy embeddingów). Brak Ollamy = krok pominięty, reszta działa | `references/indeks.md` |
| **Karty wiedzy** (`tools/wiedza_karty.py`) | Gotowe wybory tez do typowych pytań: ok. 17 kart pytań (rdzeń do 200 tez + rozszerzenie) i ok. 68 kart czynności (małe, tezy otagowane). Wybór robi na Macu model Claude czytający całą bazę w porcjach, potem ocena ścisła tez (`ocen`); wynik leży w tabelach `karty` i `karty_wi` tego samego pliku `wiedza.sqlite`. Telefon wybiera kartę (`karty --do`) i czyta ją w całości (`karta KOD --czesc k`) z dopełnieniem z szukania | `references/karty.md`, `references/pytanie-do-bazy.md` |
| Migawka (`tools/migawka.py`) | Otwarte wpisy Notatnika budowy i zadania w jednym pliku Markdown, publikowanym obok indeksu – czat bez Notion czyta z niej stan spraw | `references/indeks.md` |
| Kopia dla czatu | Indeks, `wiedza.py` i migawka publikowane do prywatnego repo; czat pobiera je tokenem tylko do odczytu | `references/indeks.md`, `indeks-awarie.md` |
| Praca bez Notion (`budowa`, zasada 13) | Gdy w rozmowie nie ma narzędzi Notion: wiedza z indeksu, Notatnik i zadania z migawki, a każdy zapis do dokumentu Claude „📥 Skrzynka” słowami, bez pól Notion; przebieg godzinowy na Macu przenosi wpisy do Notion | `plugins/ja/skills/wpisy/references/skrzynka.md` |
| Tryb głęboki | Pytanie złożone, którego nie pokrywa żadna karta: czat zostawia je w prywatnym repo, workflow GitHub Actions (leży w prywatnym repo kopii, nie w tym; model przez token OAuth Claude Code) czyta całą bazę, pisze odpowiedź i odkłada ją do repo; 3–6 minut, ok. 1–2 USD. Lokalny skrypt Maca (`pytania.py`) jest wersją zapasową | `references/tryb-gleboki.md` |
| Automaty na Macu (launchd, poza repo) | Przeglądy Dziennika (szybki, wieczorny, tygodniowy) przez `claude -p` z lokalnym serwerem MCP Notion; przed każdym przebiegiem `sync --publikuj`, `migawka.py` i `wiedza_karty.py aktualizuj`. To one utrzymują kopię dla telefonu świeżą | `docs/wiedza-runbook.md`, sekcje 2 i 5.1 |
| Obserwator (`tools/wiedza_jakosc.py`) | Stałe zbiory pytań i znanych wierszy; alarm, gdy szukanie po zmianach zaczyna gubić to, co znajdowało | `references/indeks-jakosc.md` |
| Sędzia LLM (`wiedza_jakosc.py sedzia`) | Model bez narzędzi ocenia sens wyników dla pytań testowych (0/1/2); bez filtra danych osobowych – do modeli Claude wolno, do repo nie | `references/indeks-sedzia.md` |
| Ocena ręczna (`wiedza_jakosc.py reczna`) | Inwestor ocenia wyniki w terminalu; punkt odniesienia dla sędziego | `references/indeks-jakosc.md` |
| Nocna kolejka (poza repo, prywatna) | Kolejka filmów i artykułów: tezy → porównanie z bazą (etap porównania) → zapis do Notion → odświeżenie indeksu; kontrola wyrywkowa, sędzia, mini-audyt, trend czatu; własna strona w przeglądarce. Szuka w indeksie, nie w Notion | `references/porownanie.md` |

## Kto co uruchamia

1. **Start sesji Claude Code w repo** – lista wyboru (`CLAUDE.md`), domyślnie nic. Pozycja „Indeks wiedzy” = `sync --publikuj --cicho`
   i przypomnienie obserwatora.
2. **Automaty launchd (samo)** – szybki przebieg co godzinę w ciągu dnia (8:05–22:05 i 22:30), wieczorny 22:45, tygodniowy w niedzielę
   wieczorem. Każdy zaczyna od `sync --publikuj`, `migawka.py` i `wiedza_karty.py aktualizuj --publikuj` (nowe tezy → tagi
   czynności, wybór do kart pytań, ocena ścisła, zapis, publikacja). Mac uśpiony = przebieg przesunięty do wybudzenia, wyłączony = przepada
   (wpisy poczekają).
3. **Noc (inwestor uruchamia z strony kolejki)** – po każdej pozycji odświeżenie indeksu, co N-te pytanie o wiedzę kontrola obu
   silników, na końcu publikacja kopii, obserwator i sędzia (gdy minął ustawiony odstęp). Nowe tezy z nocy trafiają do kart przy
   najbliższym przebiegu godzinowym; do tego czasu widać je w „Dopełnieniu z szukania”.
4. **Czat na telefonie** – pobiera kopię i migawkę i czyta karty; zapisy (gdy brak Notion) do Skrzynki; pytania złożone zostawia
   trybowi głębokiemu.
5. **Ręcznie, od czasu do czasu** – ocena ręczna po większej zmianie szukania, `zloty --odnowa` po dużych zmianach bazy, przegląd
   raportów jakości, `wiedza_karty.py ocen --zastosuj` po przebudowie kart.

## Droga pytania z telefonu

1. `karty --do "A" "B" "C"` – spis kart dopasowanych do pytania (trafienia w kartach i poza nimi).
2. Jedna karta pytań albo 2–4 karty czynności (do ok. 75 tys. znaków), wszystkie części w całości; pod nimi dopełnienie z szukania i otwarte
   sprzeczności. Nagłówek karty podaje jej **pokrycie** wobec wzorca (albo „niemierzone”).
3. Odpowiedź z numerami WI, zasięgiem („czego baza nie wie”) i sekcją „📚 Na czym się opieram” (`zrodla`).
4. Pytanie złożone bez pasującej karty albo ponad 15 trafień poza kartami → tryb głęboki (wstępna odpowiedź z karty od razu).
5. Karty niedostępne w kopii (stara kopia) → droga zapasowa: poziomy szukania szybko / normalnie / dokładnie.

## Pomiary (ostatnie, do 29.10.2026)

| Co | Wynik | Skąd |
|---|---|---|
| Szukanie przed zmianami – czy to, co czat zobaczył, zawiera trafne tezy (recall@widziane, 53 pytania, wzorzec 598 tez) | 25,3% | Z1, 25.10 |
| Po zwartym wyniku i kilku sformułowaniach (2.7.0) | 42,0% (+16,7 pkt) przy 0,62× znaków | Z2 |
| Po odciskach znaczenia i listach podobnych (2.9.0) | 47,5% wobec 42,4% wariantu bez nich, tego samego dnia (+5,1 pkt), przy 1,25× znaków | Z4 |
| Zgodność sędziego z oceną ręczną (30 par, reguła „trafny” ↔ ocena 2) | 10/10 przy „trafny” (dawna reguła: 7/10) | Z9 |
| Mini-audyt: powiązania uwzględnione przy zapisie nowych źródeł (tryb indeksu) | 73,7% (audyt z 22.10: 63% w trybie indeksu, 47% w trybie Notion) | Z0, Z9 |
| Kontrola wyrywkowa, 72 testy: pokrycie trafnych wyników | indeks 84%, wyszukiwarka Notion 40% | Z0 |
| Etap porównania w nocy: relacje audytu ocenione ≥ 2 | 88%, ok. 0,56 USD na pozycję | Z8 |
| Karty pytań: rdzeń samym wyborem modelu / z rozszerzeniem / rdzeń uzupełniony wzorcem | 68% (Kluczowe 88%) / 89% (91%) / 100% | Z13, 29.10 |
| Symulacja telefonu: karty vs poziom „dokładnie” (10 pytań; trafne tezy w odpowiedzi / wywołania) | 83% (Kluczowe 100%), 5,6 wywołań vs 50% (56%), 10,4 | Z13 |
| Zbiór sprawdzający spoza wzorca (12 pytań) | karty 84% (Kluczowe 92%) vs „dokładnie” 72% (90%) | Z13 |

Jak czytać: **recall@widziane** – jaka część trafnych tez ze wzorca znalazła się w tym, co agent faktycznie zobaczył; **Kluczowe (K)** – to samo
tylko dla tez o Istotności „Kluczowe”; **pokrycie karty** – jaka część trafnych tez wzorca jest na karcie (miara wobec jednego wzorca, nie „prawdy
absolutnej” – tezy dodane później wzorzec nie ocenia); **zgodność sędziego** – ile ocen sędziego zgadza się z oceną inwestora. Porównuj zawsze na
tym samym stanie bazy (baza zmienia się co noc): wariant bazowy i nowy tego samego dnia, raportuj różnicę, nie samą liczbę. Pomiar po każdej
zmianie szukania lub kart: `wiedza_jakosc.py zloty` (alarmy obserwatora), `wiedza_karty.py pomiar`; szczegóły w runbooku, sekcja „Jak mierzyć”.

## Decyzje i dlaczego

- **Indeks zamiast Notion w nocy i w czacie.** Wyszukiwarka Notion trafia w ok. 40% tego, co indeks (kontrola 72 testów), jest wolna i ma limity
  workspace'u. Notion zostaje źródłem prawdy i miejscem zapisu; indeks jest tylko do odczytu i odtwarzalny z Notion.
- **Lokalnie zamiast Bedrock.** Odciski liczy Ollama na Macu (bge-m3), bez nowej usługi zewnętrznej. Nowa usługa zewnętrzna wymaga zgody inwestora.
- **Listy podobnych w kopii dla czatu.** Czat na telefonie wychodzi tylko do GitHuba i rejestrów pakietów, nie policzy embeddingów – dostaje wynik
  policzony na Macu.
- **Karty zamiast poziomów szukania.** Sam czat widzi przy pytaniach szerokich ok. 60% trafnych tez (pomiar 28.10; w symulacji telefonu z tabeli wyżej poziom „dokładnie” dał 50%, bo dochodzi czytanie porcjami), a poziom „cały etap” (330–390 tys. znaków)
  przerasta okno rozmowy. Karty dają 83% przy połowie wywołań. Poziomy zostają jako droga zapasowa.
- **Książki w Notion nie budujemy.** Rozdziały na temat (pilotaż) dały mniej niż karty; spis spisów nie zmniejszył czytania. Rekomendacja: nie.
- **Ocena ścisła po wyborze inkluzywnym.** Wybór modelu jest szeroki (300–1000 tez na kartę), telefon czyta ok. 75 tys. znaków; ocena 2/1/0
  zawęża rdzeń do 200 tez, a reszta pokrewnych idzie do rozszerzenia (`--wiecej`). Wzorzec pomiaru dopisany do rdzenia daje 100%.
- **Tryb głęboki w GitHub Actions.** Mac nie musi nie spać; lokalny `pl.dom.pytania` zostaje zapasowy. Sekret: token OAuth Claude Code w sekretach repo kopii.
- **Automaty launchd zamiast zaplanowanych zadań claude.ai**, gdy konektor Notion na claude.ai jest zablokowany: te same przebiegi idą na Macu przez
  `claude -p` i lokalny serwer MCP Notion. Zapisy z telefonu bez Notion – Skrzynka.
- **Treść bazy do modeli Claude bez filtra danych osobowych** (decyzja z 26.10.2026): dane osobowe mają nie trafiać do publicznego repo, a nie
  „nie można ich przeglądać”. Filtr zostaje dla repo i commitów (`tools/build.py`, hooki).
- **Kopia dla czatu tylko w prywatnym repo.** Indeks zawiera pola osób trzecich; program odmawia publikacji do repo publicznego.

## Znane długi (stan na 4.11.2026)

- Karty pytań dla kolejnych etapów budujemy dopiero, gdy etap nadejdzie; karty czynności nie mają zmierzonego pokrycia (tagi modelu).
- Pokrycie nowych kart (podzielonych 30.10) po `ocen --zastosuj` wymaga `pomiar --zapisz`.
- Nocna kolejka od przepięcia na lokalny MCP Notion (28.10) nie była sprawdzona w nocy; brak kontroli logowania MCP i sieci przed startem
  (automaty launchd ją mają).
- Etap porównania w nocy: noc testowa na 10 filmach i audyt jeszcze nie zrobione.

## Gdzie czytać dalej

`references/indeks.md` (polecenia), `indeks-awarie.md` (komunikaty `[wiedza]`, tokeny), `indeks-jakosc.md` i `indeks-sedzia.md` (miary),
`karty.md` (karty), `pytanie-do-bazy.md` (jak czat szuka i odpowiada), `tryb-gleboki.md`, `porownanie.md` (etap porównania),
`porzadki.md` (duplikaty i sprzeczności), `plugins/ja/skills/wpisy/references/skrzynka.md` (Skrzynka). Każda zmiana procedur i narzędzi:
procedura `rozwoj-harnessu` (wersja → CHANGELOG → `tools/build.py` → commit → push).
