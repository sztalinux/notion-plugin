# Pytanie do bazy – jak szukać i odpowiadać (czat na telefonie, Claude Code, zaplanowane zadania)

Cel: odpowiedź uwzględnia **całą** istotną wiedzę z bazy (z numerami WI), mówi, co przeczytała, i wprost – czego nie wie
ani nie sprawdziła. Droga domyślna to **karta wiedzy** (`karty.md`): gotowy wybór tez do typowych pytań, który na Macu zrobił
mocny model, czytając całą bazę w małych porcjach. Powód: czat na telefonie szukając sam widzi przy pytaniach szerokich ok. 60%
trafnych tez, a poziom „cały etap” (330–390 tys. znaków w 14–16 częściach) go przerasta – test z telefonu 28.10.2026: w całości
przeczytał 3 z 16 części. Pomiar kart wobec wzorca (598 trafnych tez dla 10 pytań inwestora): średnie pokrycie trafnych tez
68% samym wyborem modelu (rdzeń do ok. 200 tez; z rozszerzeniem `--wiecej` 89%), a rdzeń kart dla 10 pytań inwestora uzupełniony wzorcem – 100%, Kluczowych 88% (z rozszerzeniem 91%, po uzupełnieniu wzorcem 100%); test całej drogi pytanie → odpowiedź na telefonie: symulacja telefonu 29.10.2026 (Sonnet odpowiada całą drogą, 10 pytań inwestora, 1 przebieg): odpowiedź cytuje 83% trafnych tez i 100% Kluczowych przy 5–6 wywołaniach, dawna droga „dokładnie” tego samego dnia – 50% / 56% przy 10 wywołaniach. Dawna droga (szukanie z poziomami, pkt 3): 26.10.2026,
15 pytań bez Notion – jedno zapytanie dawało w odpowiedzi 73% Kluczowych i 42% Ważnych tez, poziomy 89% / 57% w skrócie i 100% / 81%
po rozwinięciu (stąd na drodze zapasowej głębokość i cały temat są obowiązkowe); 28.10.2026, 10 pytań łączących, wzorzec 598 tez, model
czyta i wskazuje tezy – „dokładnie” 60% trafnych tez / 56% Kluczowych, „cały etap” 68% / 86%. Polecenia i kanały: `indeks.md`.

## 1. Indeks – raz na rozmowę (czat)

Przeczytaj stronę dostępu (`indeks.md`, sekcja czatu) i pobierz kopię do stałej ścieżki **jednym poleceniem razem z pierwszym
poleceniem wiedzy** (`karty --do …`, pkt 2): `test -s /tmp/wiedza.sqlite || curl …` (to samo dla `wiedza.py`), potem
`python3 /tmp/wiedza.py karty --do … --db /tmp/wiedza.sqlite`. Linie z `test -s` powtarzaj w kolejnych wywołaniach (pobierają tylko
brakujące pliki, a `/tmp` bywa pusty); strony dostępu nie czytaj drugi raz. Claude Code: `tools/wiedza.py` bez pobierania.

## 2. Karta zamiast szukania – droga domyślna

1. **Sformułowania:** z pytania ułóż 2–3 zapytania **A, B, C** różnymi słowami (ogólniej, węziej, potocznie i fachowo – „woda przy
   ławie”, „drenaż opaskowy”), po 2–4 słowa treściowe, bez zdania i spójników. Służą do wyboru kart i do dopełnienia z szukania.
2. **Lista kart:** `karty --do "A" "B" "C"` drukuje zamiast spisu `## Dopasowanie do pytania (trafień w karcie / N)` (N ≤ 60 pierwszych
   trafień szukania): do 12 kart, najlepsza pierwsza (wg wagi trafień – wyższe pozycje szukania ważą więcej – nie zawsze wg liczby), linie
   `trafień n/N · <linia karty>` (pola – `indeks.md`); potem `trafienia poza wszystkimi kartami: m` i `## Pozostałe karty` (same kody).
3. **Wybierz karty:** (a) jedną **kartę pytań** (jej linia ma `np. „…”` – przykładowe pytanie; karta czynności go nie ma), gdy pytanie należy
   do jej rodziny (nazwa, opis i przykładowe pytanie pasują) – zwykle najwyższą na liście, a przy zbliżonej liczbie trafień tę z **bieżącego etapu** budowy (strona DOM; w okresie stanu zero
   karty stanu zero przed kartami „Cała budowa” i SSO); (b) gdy żadna karta pytań nie pasuje – **2–4 karty
   czynności** najwyżej na liście (małe, do pytań wąskich i nietypowych); (c) łącznie do ok. 75 tys. znaków – więcej niż 3 części to za dużo,
   zawęź: tyle czat na telefonie czyta w całości, resztę tylko przegląda. „Trafienia poza wszystkimi kartami” m > 15 (linia kończy się
   „… (+k)”) → pytanie wykracza poza karty: użyj trybu głębokiego (pkt 2.7), a gdy jest niedostępny – dołóż poziom „normalnie” z pkt 3.
4. **Czytaj:** `karta KOD [KOD2 …] --pytanie "A" "B" "C" --czesc 1`, potem `--czesc 2` … – **wszystkie części, każdą w całości**
   (zwykle 1–3). Nagłówek kończy się „część k/n – dalej --czesc k+1”, ostatnia część – „część n/n (ostatnia)”. Kilka kodów = suma bez
   powtórzeń. Nagłówek podaje też „rozszerzenie: +n tez pokrewnych” – tezy z oceną „pokrewna”, poza rdzeniem: czytaj je (`karta KOD --wiecej --czesc 1` …) po rdzeniu, gdy inwestor prosi „więcej”/„rozwiń” albo pytanie wyraźnie wykracza poza rdzeń; w „Rozwinąć?” podaj ich liczbę. Odpowiedź buduj po ostatniej części, nie po każdej. Część, której okno nie udźwignęło, to tezy niewidziane: wpisz ją do zasięgu
   („części 1–2 z 3”) i dokończ szukaniem (pkt 3). Nagłówek niesie też liczbę tez (Kluczowe, Ważne), znaków, części, „dopełnienie n” i **pokrycie**
   (pkt 9) – przepisz je do zasięgu; kilka kart o różnym pokryciu: „kod: …; kod2: …”. `tez 0` / „karta pusta – użyj szukaj / temat / etap” = karta
   niezbudowana (z `--pytanie` pokaże tylko dopełnienie): traktuj jak brak karty, wpisz „karta KOD pusta” do zasięgu, idź drogą zapasową (pkt 3).
5. **Sekcje karty:** `## Kluczowe (n)` – wszystkie Kluczowe karty, na początku: czytaj je zawsze, bo z długiego wyniku czat czyta
   w całości głównie początek; `## <temat> – Ważne (n)` wg tematów; `## Dopełnienie z szukania (n)` – na końcu karty, do 20 trafień szukania
   dla A/B/C spoza karty: traktuj je jak tezy karty, bo to, czego wybór z góry nie objął („## Dopełnienie z szukania: brak – …” = szukanie nic
   nie dodaje); `## Otwarte sprzeczności (n)` – pkt 8. `## Ciekawostki (n)` na końcu – karta pokazuje je domyślnie (są jej częścią; wzorzec liczy je jako trafne), `--bez-ciekawostek`
   je ukrywa. Nieznany kod → „✗ karta „KOD”: nie ma takiej karty – podobne: …” (kod wyjścia 1).
6. **Notatnik** wg pkt 5, obok karty: karta niesie wiedzę z bazy, a „U nas ustalone” i „Czeka na decyzję” są tylko w Notatniku.
7. **Tryb głęboki** (`tryb-gleboki.md`): pytanie złożone bez pasującej karty pytań, m > 15 albo „tryb głęboki” / „przeczytaj całą bazę” od inwestora –
   Mac czyta całą bazę (3–6 min, ok. 1–2 USD); użyj go, zanim napiszesz „nie ma w bazie” (pkt 6). Nie dla faktów wąskich ani pytań pokrytych kartą.

## 3. Droga zapasowa – szukanie i poziomy głębokości

Użyj, gdy: `karty` zgłosi „# karty: brak w tej kopii indeksu …” albo polecenie nie istnieje (stara kopia – `indeks.md`, „Ograniczenia kopii”); wybrana
karta jest pusta (pkt 2.4) albo „żadna karta nie ma trafień”; pytanie jest wąskim faktem („ile”, „jaka klasa”, „czy wolno”) i żadna karta nie pasuje;
albo jako uzupełnienie wg pkt 2. Poziom wybierz po rodzaju pytania (inwestor może go wymusić: „na szybko”, „dokładnie”); wątpisz → „normalnie”;
podaj go w zasięgu (pkt 9).

| Poziom | Kiedy | Polecenia | Wynik (ok.) |
|---|---|---|---|
| **szybko** | wąski fakt; „na szybko” | `szukaj "A" "B" "C" --krotko --limit 60` | 22 tys. zn. |
| **normalnie** (domyślny) | „jak”, „na co uważać”, „co sprawdzić”, „co zamówić”, doradca | to samo z `--limit 100` + `temat "<główny temat>" --lista --krotko` | 77 tys. zn. |
| **dokładnie** | pytanie łączy kilka zagadnień (trafienia w ≥ 2 tematach), odbiór lub krok bez odwrotu, „dokładnie” | `--limit 100` + dwa najczęstsze tematy w całości (drugi też `--lista --krotko`) | 117 tys. zn. |
| **cały etap** (tylko Mac) | pytanie o cały etap, gdy żadna karta nie pasuje; „cały etap”, „wszystko” | `etap "<etap>" --czesc 1` … do ostatniej części (bez `szukaj`); zamknięcie etapu, odbiory i kolejność → `--kontrola` | 330 tys. zn. w 14 częściach (z `--kontrola` 390 tys. / 16) |

- **A B C** jak w pkt 2, w jednym wywołaniu `szukaj`. **Główny temat** = ten, który najczęściej stoi w kolumnie `T:` linii wyniku,
  drugi – kolejny co do częstości; podaj nazwę dokładnie jak w `T:` (skrócona bywa niejednoznaczna – narzędzie odpowie „pasuje kilka”).
- Cały temat czytaj także wtedy, gdy trafienia leżą w nim tylko w połowie: lista tematu łapie to, czego słowa pytania nie zawierają.
  Pytania ogólne i łączące zaczynaj od „normalnie” („szybko” widzi na nich mniej niż połowę potrzebnych tez); `--ciekawostki` także
  przy `temat`. „Podobne do trafień” (≈WI-n) to podpowiedź o sąsiednim zagadnieniu: przeczytaj tezę przed użyciem.
- **Cały etap** = Kluczowe i Ważne tezy etapu i „Cała budowa” wg tematów, Kluczowe z innych etapów i otwarte SP; `--kontrola` dokłada
  Ważne rodzaju Kontrola / odbiór i Kolejność prac z innych etapów (zamknięcie etapu: sam etap niesie 55% trafnych tez, z tym 93%).
  Etap: z pytania albo bieżący z DOM (brak → zapytaj); czytaj wszystkie części po kolei. **Nie na telefonie** (czat czyta w całości
  3 z 16 części) – tam karta. Pytanie o jedno zagadnienie („czy XPS pod płytę”) to nie cały etap: wystarczy cały temat.
- Mac: `--sens` (po znaczeniu, wymaga Ollamy) pomaga tylko przy limitach 25–40 (ok. +8 pkt Kluczowych; 60: +2; od 100: nic) – niewymagany.
- **Długie wyniki:** narzędzie pokazuje jednorazowo ok. 25–30 tys. znaków, dłuższy wynik zastępuje podglądem („Output too large … saved
  to …”) albo ucina. `szukaj --limit 100` ma ok. 36 tys. znaków, lista tematu średnio 24 tys. (do 73 tys.), więc na poziomach „normalnie”
  i „dokładnie” zapisz wynik do pliku i czytaj po 20 000 bajtów: `python3 … szukaj … > /tmp/w1.txt; wc -c /tmp/w1.txt; head -c 20000
  /tmp/w1.txt`, dalej `tail -c +20001 /tmp/w1.txt | head -c 20000`, `tail -c +40001 …` – do końca (kilka tematów: po średniku, kolejne
  z `>>`). Wynik widziany częściowo jest **nieprzeczytany** – wpisz to do zasięgu (pkt 9). `karta --czesc k` i `etap --czesc k` tną
  same (części po ok. 25 tys. znaków) – bez pliku i `head`/`tail`.

## 4. Droga wg rodzaju pytania

| Rodzaj | Droga |
|---|---|
| wiedza („jak się robi”, „co grozi”) | pkt 2 (karta) |
| łączące („co zamówić”, „kiedy”, „co sprawdzić przed”) | procedura (`etap`, `zakupy`, `harmonogram`, `przygotowanie`) – ta sama droga z pkt 2 + jej własne źródła |
| po polach („co otwarte”, „o co zapytać kierownika”) | pkt 5 (Notatnik), tylko doprecyzowana wiedzą z pkt 2 |
| doradca („czy jest sens”, „co byś zrobił”, burza mózgów) | pkt 2 + pkt 8 |
| dokument projektu, umowa, rysunek | plik z przewodnika (Mac) albo projekt „Dom” na claude.ai; w rozmowie poza projektem powiedz wprost, że go nie widzisz |
| ilości i koszty | kosztorys (dziś: poproś o plik); terminy i zadania – filtr bazy TASKS / widoki Notatnika |

## 5. Co obowiązuje u nas – Notatnik po polach (bez indeksu)

Notatnik jest mały i strukturalny – czytaj go filtrem bazy, nie szukaniem tekstu: Etap = etap pytania **lub „Cała budowa”**,
Typ ∈ Decyzja / Pytanie / Pamiętać / Ryzyko, Status ≠ Zrobione i ≠ Odrzucone (schemat: `notatka/references/notion-schematy.md`).
Zwróci zwykle 5–20 wpisów – przeczytaj wszystkie; więcej niż ok. 25 → zawęź Branżą pytania. Brak etapu w pytaniu →
zapytaj albo weź bieżący z DOM. Uzupełnij o decyzje Ustalone z tego etapu. Z wyniku:
- **U nas ustalone:** decyzje i wpisy „Pamiętać” (Status Ustalone) – na początku odpowiedzi; „Do omówienia” to jeszcze nie ustalenie;
- **Czeka na decyzję:** otwarte Pytania i Decyzje (z „Do kogo”) – na końcu odpowiedzi.
Brak narzędzi Notion w kanale → Notatnik i zadania z migawki: pobierz `migawka.md` tą samą drogą co indeks (`indeks.md`,
sekcja czatu), z sekcji Notatnika weź wpisy Etapu pytania i „Cała budowa” o Typie jak wyżej (filtruj w głowie), w zasięgu
podaj „Notatnik z kopii, stan <data z pierwszej linii pliku>”; brak migawki → „Czego nie sprawdziłem”.

## 6. „Nie ma w bazie”

Napisz tak dopiero po: karcie (wszystkie części) z dopełnieniem, a przy drodze zapasowej – kilku sformułowaniach, liście
podobnych i całym głównym temacie – oraz Notatniku dla etapu. Pokrycie karty poniżej 100% albo niemierzone znaczy, że brak w karcie nie dowodzi
braku w bazie. Inaczej pisz „nie znalazłem w przeczytanym” i podaj, co przeczytałeś.

## 7. Internet jako podpora, nie zapis

Gdy po pkt 6 czegoś brakuje albo inwestor prosi – uzupełnij wyszukiwaniem w sieci, w osobnej sekcji „Z internetu”:
każda informacja `[internet]` z nazwą źródła, linkiem, datą, typem autora i oceną wiarygodności (`ocena-zrodla.md`),
nigdy w jednym zdaniu z materiałami inwestora. **Nie proponuj zapisu do bazy** – tylko na wyraźną prośbę (wtedy `wiedza`, A).
Brak wyszukiwarki w danym kanale → napisz to.

## 8. Sprzeczność i tryb doradcy

- Sprzeczne tezy bez wpisu w Rejestrze → pokaż obie z wiarygodnością źródeł, wskaż mocniejszą i dlaczego `[opinia]`,
  zapytaj, czy otworzyć wpis SP (zapis tylko za zgodą). Wpis SP (w trafieniach, w „Otwartych sprzecznościach” karty) → numer i stanowiska.
- Doradca: rekomendacja `[opinia]` oparta na WI (numery) i wiedzy ogólnej, z pewnością, „co zmieniłoby moje zdanie”
  i kogo zapytać (konstrukcja → „do potwierdzenia z konstruktorem”); internet wg pkt 7. Decyzja inwestora → wpis „Decyzja”
  w Notatniku (`notatka`) za zgodą.

## 9. Forma odpowiedzi – skrót, potem rozwinięcie

Telefon: dwie warstwy; w obu **każda użyta teza ma numer WI** (jeden punkt może nieść kilka numerów – wszystkie tezy, które
to samo zagadnienie potwierdzają albo uzupełniają). Nie dopisuj wiedzy z pamięci jako „z bazy”.
- **Skrót** (pierwsza wiadomość, 5–8 punktów, bez wstępów): linia **Zasięg** – karta/karty (kod, liczba tez, **pokrycie dosłownie
  z nagłówka**: „pokrycie X% trafnych / Y% Kluczowych (wobec wzorca …)” albo „pokrycie: niemierzone (karta czynności – tagi modelu)” / samo
  „pokrycie: niemierzone”; „części k z n przeczytane w całości”) · liczba tez z dopełnienia · Notatnik (etap, liczba wpisów, stan migawki) · ile
  Kluczowych tez z przeczytanego zawiera odpowiedź. Pokrycie wypisz zawsze, także gdy niskie: to miara zaufania inwestora do karty. Przy drodze
  zapasowej zamiast karty: poziom, tematy z liczbą tez z nagłówka `temat`, liczba trafień `szukaj`, przy „cały etap” etap i części
  „k z n”. Potem punkty, które razem niosą **wszystkie Kluczowe tezy** (zagadnienie, liczby z warunkami, numery WI), osobno
  „U nas ustalone” i „Otwarte” (SP z numerem, pytania z „Do kogo”). Na końcu: „Rozwinąć? (n Ważnych tez w m grupach)”.
- **Rozwinięcie** (po „rozwiń” albo od razu przy „dokładnie”) – pełna odpowiedź w kolejności: Zasięg → **U nas ustalone**
  (Notatnik, rozstrzygnięte SP, projekt) → **Co mówi wiedza** (Kluczowe, potem Ważne pogrupowane tematycznie, wiarygodność
  źródeł; ciekawostki jako licznik) → **Otwarte** → **Czego baza nie ma** → **Z internetu** `[internet]` → **Moja opinia**
  `[opinia]` → **Czego nie sprawdziłem** (kosztorys, projekt, Notion…) i proponowane zapisy (za zgodą).
Przy tezie z „Moim komentarzem” podaj go (`wiedza`, H). Szczegóły z Notion tylko dla WI, na których opierasz decyzję.

## 10. Budżet wywołań

Karta: strona dostępu + `karty --do` (z pobraniem kopii) + części (zwykle 1–3) + Notatnik = ok. 4–6 wywołań, mniej niż dawne
„normalnie”. Droga zapasowa: `szybko` do 2 wywołań poza Notatnikiem (pobranie + `szukaj`; strona dostępu), `normalnie` 5–8 (strona
dostępu, `szukaj` do pliku i porcje, `temat` do pliku i porcje, Notatnik), `dokładnie` do 10, `cały etap` (tylko Mac) liczba części
+ 3 (pobranie, Notatnik, zapas) – dziś do 20. Kilka poleceń łącz w jedno wywołanie (średnikiem). Nie powtarzaj `karty --do` ani
`szukaj` na to samo pytanie; nowe sformułowanie – tylko gdy lista kart, dopełnienie i „podobne” nie pokazały sedna.
