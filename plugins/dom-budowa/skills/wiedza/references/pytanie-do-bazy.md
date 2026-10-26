# Pytanie do bazy – jak szukać i odpowiadać (czat na telefonie, Claude Code, zaplanowane zadania)

Cel: odpowiedź uwzględnia **całą** istotną wiedzę z bazy (z numerami WI), mówi, co przeczytała, i wprost – czego nie wie
ani nie sprawdziła. Pomiar (26.10.2026, 15 pytań bez Notion): stara droga (jedno zapytanie) – w odpowiedzi 73% Kluczowych i 42%
Ważnych tez; ta procedura – w skrócie 89% / 57%, po rozwinięciu 100% / 81% (przy 36% Kluczowych widzianych po jednym
zapytaniu na szerokim pytaniu) – dlatego głębokość i cały temat są obowiązkowe. Wołają ją: `wiedza` E, router
`budowa` (zasada 10) i każda procedura, która pyta bazę (`etap`, `zakupy`, `harmonogram`, `przygotowanie`, `analiza-techniczna`,
przeglądy). Polecenia i kanały: `indeks.md`.

## 1. Indeks – raz na rozmowę (czat)

Przeczytaj stronę dostępu (`indeks.md`, sekcja czatu) i pobierz kopię do stałej ścieżki **jednym poleceniem razem z pierwszym
szukaniem**: `test -s /tmp/wiedza.sqlite || curl …` (to samo dla `wiedza.py`), potem `python3 /tmp/wiedza.py szukaj …`.
Przed kolejnym szukaniem w tej rozmowie nie pobieraj ponownie, gdy plik jest; brak pliku → pobierz. Strony dostępu nie
czytaj drugi raz. Claude Code: `tools/wiedza.py` bez pobierania.

## 2. Dobierz głębokość

Wybierz poziom po rodzaju pytania; inwestor może go wymusić słowem w pytaniu („na szybko”, „dokładnie”). Wątpisz →
„normalnie”. Zawsze podaj użyty poziom i co przeczytałeś (pkt 9).

| Poziom | Kiedy | Polecenia | Wynik (ok.) |
|---|---|---|---|
| **szybko** | wąski fakt („ile”, „jaka klasa”, „czy wolno”); „na szybko” | `szukaj "A" "B" "C" --krotko --limit 60` | 22 tys. zn. |
| **normalnie** (domyślny) | „jak”, „na co uważać”, „co sprawdzić”, „co zamówić”, doradca | to samo z `--limit 100` + `temat "<główny temat>" --lista --krotko` | 77 tys. zn. |
| **dokładnie** | pytanie łączy kilka zagadnień (trafienia w ≥ 2 tematach), odbiór lub krok bez odwrotu, „dokładnie” | `--limit 100` + dwa najczęstsze tematy w całości (drugi też `--lista --krotko`) | 117 tys. zn. |

- **A B C** = 2–3 krótkie zapytania z pytania, różnymi słowami (ogólniej, węziej, potocznie i fachowo – „woda przy ławie”,
  „drenaż opaskowy”), 2–4 słowa treściowe każde, bez zdania i spójników; **jedno** wywołanie `szukaj`.
- **Główny temat** = ten, który najczęściej stoi w kolumnie `T:` linii wyniku; drugi – kolejny co do częstości. Podaj nazwę
  dokładnie jak w `T:` (skrócona nazwa bywa niejednoznaczna – narzędzie odpowie „pasuje kilka”).
- Cały temat czytaj także wtedy, gdy trafienia leżą w nim tylko w połowie: lista tematu łapie to, czego słowa pytania
  nie zawierają. Wynik długi (kilkadziesiąt tys. znaków) to norma – czytaj go porcjami wg pkt 3.
- `--ciekawostki` dopisz do `temat`, gdy pytanie dotyczy ciekawostek albo inwestor prosi o „wszystko”; domyślnie są ukryte
  (licznik w nagłówku).
- Pytania **ogólne i łączące** (większość pytań z telefonu) zaczynaj od „normalnie”; „szybko” zostaw faktom, bo na szerokim
  pytaniu widzi mniej niż połowę potrzebnych tez.
- **Sesja na Macu (Claude Code):** `--sens` (ranking po znaczeniu, wymaga Ollamy) pomaga tylko przy małych limitach (limit 25–40:
  ok. +8 pkt Kluczowych, limit 60: +2, od 100: nic albo gorzej), a większy limit daje więcej niż `--sens` – procedura go nie
  wymaga; możesz dopisać przy „szybko”, gdy potrzebujesz limitu 40. Na telefonie `--sens` nie istnieje.
- Sekcja „Podobne do trafień” (≈WI-n): przeczytaj tezę przed użyciem – to podpowiedź o sąsiednim zagadnieniu, nie trafienie.

## 3. Długie wyniki – czytaj porcjami, do końca

Narzędzie pokazuje jednorazowo ok. 25–30 tys. znaków wyniku; dłuższy zastępuje podglądem początku (komunikat „Output too
large … saved to …”) albo ucina. `szukaj --limit 100` ma ok. 36 tys. znaków, lista tematu średnio 24 tys. (do 73 tys.), więc na
poziomach „normalnie” i „dokładnie” zapisz wynik do pliku i czytaj po 20 000 bajtów:
`python3 … szukaj … > /tmp/w1.txt; wc -c /tmp/w1.txt; head -c 20000 /tmp/w1.txt`, dalej `tail -c +20001 /tmp/w1.txt | head -c 20000`,
`tail -c +40001 …` – aż do końca pliku (rozmiar z `wc -c`). Kilka tematów naraz: polecenia po średniku, drugie i kolejne z `>>`
do tego samego pliku. Wynik widziany częściowo jest **nieprzeczytany** – nie odpowiadaj z samego początku; czego nie
przeczytałeś, wpisz do zasięgu (pkt 9). Wynik `szybko` (do ok. 25 tys. znaków) czytaj wprost.

## 4. Droga wg rodzaju pytania

| Rodzaj | Droga |
|---|---|
| wiedza („jak się robi”, „co grozi”) | pkt 2 |
| łączące („co zamówić”, „kiedy”, „co sprawdzić przed”) | procedura (`etap`, `zakupy`, `harmonogram`, `przygotowanie`) – ta sama droga szukania z pkt 2 + jej własne źródła |
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
Brak dostępu do Notion w danym kanale → napisz to w „Czego nie sprawdziłem”.

## 6. „Nie ma w bazie”

Napisz tak dopiero po: kilku sformułowaniach, przeczytaniu listy podobnych, całego głównego tematu i Notatnika dla etapu.
Inaczej pisz „nie znalazłem w przeczytanym” i podaj, co przeczytałeś.

## 7. Internet jako podpora, nie zapis

Gdy po pkt 6 czegoś brakuje albo inwestor prosi – uzupełnij wyszukiwaniem w sieci, w osobnej sekcji „Z internetu”:
każda informacja `[internet]` z nazwą źródła, linkiem, datą, typem autora i oceną wiarygodności (`ocena-zrodla.md`),
nigdy w jednym zdaniu z materiałami inwestora. **Nie proponuj zapisu do bazy** – tylko na wyraźną prośbę (wtedy `wiedza`, A).
Brak wyszukiwarki w danym kanale → napisz to.

## 8. Sprzeczność i tryb doradcy

- Sprzeczne tezy bez wpisu w Rejestrze → pokaż obie z wiarygodnością źródeł, wskaż mocniejszą i dlaczego `[opinia]`,
  zapytaj, czy otworzyć wpis SP (zapis tylko za zgodą). Wpis SP w trafieniach → numer i stanowiska obu stron.
- Doradca: rekomendacja `[opinia]` oparta na WI (numery) i wiedzy ogólnej, z pewnością, „co zmieniłoby moje zdanie”
  i kogo zapytać (konstrukcja → „do potwierdzenia z konstruktorem”); internet wg pkt 7. Decyzja inwestora → wpis „Decyzja”
  w Notatniku (`notatka`) za zgodą.

## 9. Forma odpowiedzi – skrót, potem rozwinięcie

Telefon: dwie warstwy; w obu **każda użyta teza ma numer WI** (jeden punkt może nieść kilka numerów – wszystkie tezy, które
to samo zagadnienie potwierdzają albo uzupełniają). Nie dopisuj wiedzy z pamięci jako „z bazy”.
- **Skrót** (pierwsza wiadomość, 5–8 punktów, bez wstępów): linia **Zasięg** (poziom; co przeczytałeś w całości – tematy z liczbą
  tez z nagłówka `temat`, liczba trafień `szukaj`, Notatnik: etap i liczba wpisów; ile Kluczowych i Ważnych tez było
  w przeczytanym i ile z nich zawiera odpowiedź), potem punkty, które razem niosą **wszystkie Kluczowe tezy** (zagadnienie,
  liczby z warunkami, numery WI), osobno „U nas ustalone” i „Otwarte” (SP z numerem, pytania z „Do kogo”). Na końcu:
  „Rozwinąć? (n Ważnych tez w m grupach)”.
- **Rozwinięcie** (po „rozwiń” albo od razu przy „dokładnie”) – pełna odpowiedź w kolejności: Zasięg → **U nas ustalone**
  (Notatnik, rozstrzygnięte SP, projekt) → **Co mówi wiedza** (Kluczowe, potem Ważne pogrupowane tematycznie, wiarygodność
  źródeł; ciekawostki jako licznik) → **Otwarte** → **Czego baza nie ma** → **Z internetu** `[internet]` → **Moja opinia**
  `[opinia]` → **Czego nie sprawdziłem** (kosztorys, projekt, Notion…) i proponowane zapisy (za zgodą).
Przy tezie z „Moim komentarzem” podaj go (`wiedza`, H). Szczegóły z Notion tylko dla WI, na których opierasz decyzję.

## 10. Budżet wywołań

`szybko`: do 2 wywołań poza Notatnikiem (pobranie + `szukaj`; strona dostępu). `normalnie`: 5–8 (strona dostępu, `szukaj` do pliku
i porcje, `temat` do pliku i porcje, Notatnik). `dokładnie`: do 10. Kilka poleceń łącz w jedno wywołanie (średnikiem). Nie powtarzaj
`szukaj` na to samo pytanie; nowe sformułowanie – tylko gdy lista tematu i „podobne” nie pokazały sedna.
