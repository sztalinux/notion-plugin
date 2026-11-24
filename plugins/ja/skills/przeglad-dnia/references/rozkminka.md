# Rozkminki w ciągu dnia (D6 – wynik w ok. 2–3 h)

Rozkminka = praca myślowa, o którą inwestor prosi we wpisie („przygotuj mi…”, „rozkmiń…”, `wpisy` krok 5). Tylko na wyraźną
prośbę, nigdy z własnej inicjatywy. Trzy procesy, każdy robi swoją część – **dwa procesy nigdy nie edytują tej samej strony**.

Tryb godzinowy działa tylko wtedy, gdy polecenie przebiegu szybkiego zawiera akapit „Rozkminki w ciągu dnia” (dokleja go
`przeglad.py`, gdy inwestor zainstalował plist `pl.dom.przeglad-rozkminka`, i tylko do 21:35 – ostatnia rozkminka startuje o 21:35). Bez tego akapitu – jak dawniej:
ślad `→ 🧠 rozkminka wieczorem`, robi ją nocny przegląd (`SKILL.md`, B.2a).

## 1. Szybki przebieg – zaznacza prośbę

- Jasne części wpisu zapisz normalnie. Ślad w bloku dnia „Przetworzone”: `~~wpis~~ → 🧠 rozkminka w toku RZ-<dd.mm>-<n>`
  (pełna treść prośby zostaje w śladzie, jak dawniej; numer `<n>` – od wartości podanej w poleceniu w górę).
- Na końcu odpowiedzi osobna linia: `ROZKMINKI: RZ-<dd.mm>-<n>[, …]` – **same tokeny, bez treści wpisu** (log nie może zawierać
  treści). `przeglad.py` dopisuje tokeny do kolejki w `stan.json`.
- Limit: najwyżej 3 rozkminki dziennie w ciągu dnia (pilnuje `przeglad.py`); nadmiar zrobi nocny.

## 2. Tryb `rozkminka` – osobny proces (plist, 8:35–21:35 co godzinę)

Polecenie podaje tokeny. Dla każdego:
1. Odczytaj blok dnia „Przetworzone” w „📓 Dzienniku” (tylko odczyt) i znajdź ślad z tokenem – stamtąd treść prośby, obszar i data.
2. Wykonaj rozkminkę procedurą tematu **tylko odczytem** (jak `SKILL.md`, B.2a: budowa – spotkanie, decyzja → `przygotowanie`,
   „Bez inwestora”; technika → `analiza-techniczna`; oferta → `oferta`; terminy → `harmonogram`; osobiste – skill obszaru).
3. Zapisz **wyłącznie** nową podstronę pod stałą stroną „🧠 Rozkminki” (pod Dziennikiem, `41cf5982-09e7-81a1-9b12-df2bcc2a7574`):
   tytuł „🧠 <temat> – <dd.mm>”, na górze token i data prośby, potem wynik; na końcu sekcja „Do decyzji” – nowe pytania,
   zadania i decyzje jako krótkie punkty (do 3), każdy sformułowany tak, by „tak” znaczyło zgodę.
4. Nie edytuj „📝 Wpisów”, Dziennika ani żadnej bazy. Nie zadawaj pytań w odpowiedzi.
5. Odpowiedź: po jednej linii `WYNIK: <token> <url podstrony>` na każdą rozkminkę; bez treści.

Dwa nieudane podejścia do tego samego tokenu → `przeglad.py` zdejmuje go z kolejki; ślad „w toku” zrobi nocny (B.2a).

## 3. Szybki (albo nocny) przebieg – oddaje wynik

Polecenie zawiera „Gotowe rozkminki: <token> <url>, …” – to nowa praca (liczy się w A.2). Dla każdej pozycji:
- we „📝 Wpisach” pod „🔔 Komunikaty asystenta” blok `🔔 <dd.mm> · 🧠 Gotowe: <temat> (<wzmianka podstrony>)` z kluczem
  `` `rozkminka-<token>` `` i punktami „Do decyzji” z podstrony jako checkboxy (`wpisy/references/pytania.md`, C.7; odpowiedzi
  obsługuje nocny przebieg – dopisek „zastosuję w nocnym przeglądzie”);
- ślad w „Przetworzone” zmień z `→ 🧠 rozkminka w toku <token>` na `→ 🧠 rozkminka: <wzmianka podstrony>`.
Na końcu odpowiedzi linia `GOTOWE: <token>, …` – tokeny, których blok 🔔 jest zapisany. Po udanym przebiegu `przeglad.py`
zdejmuje z listy tylko je; reszta wraca w następnym poleceniu – blok `rozkminka-<token>` już jest → nie dodawaj drugiego.

## 4. Nocny przegląd

- Zrób jak dawniej w B.2a (wynik w przeglądzie dnia) każdy ślad `→ 🧠 rozkminka wieczorem` oraz każdy `→ 🧠 rozkminka w toku <token>`
  z bloku dziś i wczoraj, który nie został zamieniony na `→ 🧠 rozkminka: <wzmianka>` (lista „Rozkminki w toku z kolejki dnia”
  w poleceniu to tylko podpowiedź). Po udanym nocnym przebiegu `przeglad.py` czyści kolejkę dnia.
- Odpowiedzi na bloki 🔔 `rozkminka-…` obsługuje nocny przebieg (świadoma decyzja: szybki zostaje tani).
