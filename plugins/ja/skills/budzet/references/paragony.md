# Paragon ze zdjęcia → budżet domowy

Paragon to jedna płatność rozpisana na kategorie budżetu: każda kategoria to wiersz w Transakcjach (od 1.12.2026 od razu,
starsze przy zamknięciu – jak każdy wpis, sekcja A), a przy zamknięciu miesiąca płatność z wyciągu przypina się do całej
grupy, więc nic się nie dubluje. Sumy liczy skrypt `tools/budzet/paragon.py`, nie model – model tylko odczytuje pozycje
i dobiera kategorie.

## 1. Kiedy wpis jest paragonem

- Wpis we „📝 Wpisach” z obrazem (zdjęcie albo PDF paragonu, rachunku) i tekstem **kto i czym**: konto ze skrótów kont
  (`ustawienia.json`, `skroty_kont` – w tym konto gotówki) albo słowo „gotówka”, osoba opcjonalnie (zmyślone: „z, a”,
  „gotówka”, „pra”).
- **Obraz bez „kto i czym” → okienko ❓** pod wpisem (`wpisy/references/pytania.md`, A): „Kto płacił i czym? (propozycja:
  …)”. Nic nie zapisuj. To wyjątek od zasady sekcji A „brak szczegółów = gotówka drugiej osoby” – paragon na złym koncie
  zdublowałby się z wyciągiem albo z listą drugiej osoby.
- Paragon wchodzi zawsze cały. Prośba o część („tylko chemia z tego paragonu”) → ❓.
- Paragon w całości na budowę (jedna kategoria `dom`) to zwykły wydatek budowy – `dom-budowa/skills/koszty/references/wydatek-przeplyw.md`,
  bez `paragon.py`. Ten plik dotyczy paragonów prywatnych i mieszanych.
- Zdjęcia nie przejdą przez Skrzynkę ani czat na telefonie – powiedz inwestorowi, że zdjęcie dodaje we „📝 Wpisach” w Notion
  z dopiskiem „kto i czym”.

## 2. Pobranie i odczyt zdjęcia

1. W odczycie „📝 Wpisów” blok obrazu ma odnośnik `notion-file-block://…`. Pobierz dla niego podpisany adres pliku narzędziem
   Notion (adresy plików z odnośników) – adres wygasa po kilku minutach, więc od razu (to adres podpisany, z kluczem
   dostępu: nie zapisuj go w śladzie, 🔔 ani notatkach):
2. `python3 tools/budzet/paragon.py pobierz --url "<adres>" --data <dzień wpisu> --id <id bloku wpisu>` → „pobrano: <plik>”
   albo „już pobrane: <plik>” (ponowny przebieg nie pobiera drugi raz). Plik zostaje w `.dom/budzet/paragony/` jako dowód.
   Skrypt bierze tylko https i hosty plików Notion (`HOSTY_PLIKOW`), z limitem rozmiaru, bez nadpisywania.
3. Przeczytaj plik (obraz albo PDF). Nieczytelny → ❓ „Zdjęcie nieczytelne – dodasz wyraźniejsze?”.
4. Błąd pobierania (adres wygasł – pobierz nowy adres i ponów raz; host spoza listy; konektor Notion niedostępny) → w przebiegu
   blok 🔔 (`wpisy/references/pytania.md`, C; klucz `paragon-<id bloku>`, linia błędu skryptu), wpis zostaje we „Wpisach”.
   W sesji Claude Code inwestor może zamiast tego wkleić zdjęcie w rozmowę – odczytaj je wprost, bez `pobierz`; bez bloku
   Notion daj `--id c<RRRRMMDD>-<suma w groszach>` (zmyślone: `c20261205-4873`) – ten sam przy ponownym rozpisaniu.

## 3. Rozpisanie

Odczytaj ze zdjęcia: sklep, datę, **sumę do zapłaty z linii SUMA** (osobno – nie licz jej z pozycji, bo wtedy kontrola nic
nie sprawdza), każdą pozycję z kwotą końcową linii (po ilości × cenie), rabaty i kaucje.

- Każdej pozycji daj skrót kategorii z `reguly.json` (`skroty`). Pozycja niejasna → najbliższa kategoria i „?” na końcu
  opisu; nie pytaj o pojedyncze pozycje. Chemia i higiena zostają w Zakupach regularnych (drobniejsze kategorie – temat na
  2027; nie twórz nowych skrótów sam). Materiał lub narzędzie na budowę (`wydatek-przeplyw.md`, pkt 1) → `dom`.
- Rabat pod konkretną pozycją → ujemna kwota z kategorią tej pozycji; rabat na cały paragon → `rabat`; kaucja (butelki,
  opakowania) → `kaucja`. `rabat` i `kaucja` skrypt rozkłada na kategorie proporcjonalnie (największe reszty, grosze).
- Jedno polecenie, każda pozycja osobnym argumentem w cudzysłowie (`kwota, skrót[, opis]`, kwota także z separatorem
  tysięcy „1 234,56”). Zmyślony przykład paragonu mieszanego – najpierw z `--proba`, `--budowa` po kroku 4.2:
  ```
  python3 tools/budzet/paragon.py rozpisz --id <id bloku wpisu> --data <data z paragonu> --platnosc "z, a" --sklep "Sklep A" --suma 48,73 --zdjecie <plik z pobierz> --budowa <id strony 💸> "6,49, zak reg, chleb" "9,99, zak reg, płyn" "-2,00, zak reg, rabat" "3,00, kaucja" "18,90, dom, taśma" "12,35, zak reg, ser?"
  ```
  Ścieżka względna od repo, bez `cd`, potoków i `;`. Wynik: części `w<id>-1…n` (jedna na kategorię), wspólne pole `grupa`,
  pole `paragon` (sklep, suma, liczba części, plik zdjęcia); Notatki wiersza „z paragonu – sklep, razem, części”.
- `✗ suma części … ≠ suma paragonu` → przeczytaj zdjęcie jeszcze raz (pominięta pozycja, ilość × cena, rabat). Druga
  niezgodność → ❓ pod wpisem z różnicą („brakuje N zł – której pozycji nie widzę?”); nic się nie zapisało.
- `✗ nieznany skrót` → wybierz istniejący skrót. `✗ brak „kto i czym”` → ❓ jak w punkcie 1.
- `✗ jest już paragon … z tą samą datą, sumą i sklepem` → to samo zdjęcie drugi raz (ten sam paragon = ten sam `--id`);
  naprawdę drugi taki zakup → `--mimo-to`.

## 4. Część na budowę (paragon mieszany)

1. `rozpisz … --proba` – pokazuje kwotę części Inwestycja › Dom (z jej udziałem w rabatach i kaucjach), nic nie zapisuje.
2. Strona w kolejce 💸 na tę kwotę wg `dom-budowa/skills/koszty` (sekcja B) i `wydatek-przeplyw.md` (Sposób wg płatności
   paragonu). Pozycję kosztorysu zaproponuj w ❓ tak, jak każe procedura `koszty` (gdy brak pasującej – jej wzorzec nowej
   pozycji); nie zgaduj w ciszy.
3. `rozpisz` z `--budowa <id strony 💸>` – część Dom zostaje w budżecie jako Inwestycja › Dom z ID `w<id>-k` (nie z ID
   strony 💸, jak przy zwykłym wydatku budowy) i z dopiskiem „w kosztorysie budowy (💸)”, więc zamknięcie nie pyta
   „nie ma w kosztorysie”. Bez `--budowa` skrypt zapisze, ale wypisze uwagę – wtedy wróć do kroku 2.

## 5. Po zapisie, poprawka, usunięcie

- Sesja Claude Code z inwestorem: `python3 tools/budzet/arkusz_budzetu.py sync` (przebieg – automat w ciągu godziny).
- Ślad (`wpisy`, krok 6): `~~wpis~~ (Wpisy) → 💰 budżet: paragon <sklep>, <n> części (<kategorie>)` + `💸` przy części na
  budowę. Blok ze zdjęciem idzie razem z wpisem do „Przetworzone” – nie usuwaj go.
- Poprawka („ser to nie regularne”) → `rozpisz` z tym samym `--id` i poprawionymi pozycjami: zastępuje cały paragon (część,
  której już nie ma, znika z arkusza przy `sync`; zwykły wydatek zapisany wcześniej z tym samym ID bloku też). Usunięcie:
  `python3 tools/budzet/wpis.py usun RRRR-MM <id wpisu albo części>` – cały paragon i wpis z tym ID. Ten sam ID bloku nie
  idzie do `wpis.py dodaj`, gdy jest już paragonem (skrypt odmawia).
- **Paragon rozliczony** – przypięty do płatności z wyciągu albo z zamkniętego miesiąca: `rozpisz` odmawia (`✗ … nie
  zastępuję go`), bo kwoty w arkuszu są już z wyciągu. Odpisz w ❓ pod wpisem, że kategorie trzeba poprawić ręcznie
  w arkuszu (które wiersze – ID części w kolumnie O). To samo, gdy `sync` zgłosi „część paragonu przypięta do płatności”.

## 6. Zamknięcie miesiąca (liczy `importuj.py` – tu do wyjaśnień inwestorowi)

- **Karta** (konto z wyciągiem): płatność równa sumie paragonu (do złotówki różnicy, ±4 dni, także przez przełom miesiąca)
  przypina się do wszystkich części – ID wyciągu w kolumnie O każdego wiersza, różnicę groszową bierze największa część.
  Części nie ma jeszcze w arkuszu (listopad, skrypt nie wdrożony) → wiersze z płatności z kategoriami części. Bez pary →
  strona decyzji.
- **Konto drugiej osoby:** pozycja listy równa sumie paragonu na tym samym koncie → pominięta „już z paragonu”; równa
  jednej części – wchodzi normalnie (chyba że jest też bliska sumie, do pięciu złotych – wtedy decyzja); bliska sumie, ale
  inna → strona decyzji „możliwy duplikat paragonu”.
- **Gotówka:** tylko z wpisów i paragonów – dubla nie ma.
- Wpis z ostatnich dni miesiąca, którego płatność przyszła w wyciągu dopiero przy imporcie kolejnego miesiąca, dostaje wiersz
  z datą płatności – także z miesiąca już zamkniętego (zmienia się wtedy jego suma); powiedz o tym w podsumowaniu zamknięcia.
