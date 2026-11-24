---
name: model-3d
description: Model 3D domu i ogrodu w Blenderze, po którym można chodzić – zmiany w modelu przez pliki danych (JSON) i przebudowę skryptem, podgląd przed/po, rendery kontrolne, praca przez konektor Blendera albo bez okna. Używaj, gdy użytkownik mówi „przebuduj model 3D”, „zmień podłogę w salonie”, „dodaj okno dachowe”, „podnieś taras”, „przesuń ścianę w modelu”, „pokaż widok z kuchni na ogród”, „dodaj drzewo / rabatę w modelu”, „zapisz model”, „zrób rendery elewacji”, „dostałem DWG rzutów od architekta”, „co w modelu jest przybliżone”, albo pyta, jak chodzić po modelu, „wprowadź poprawki modelu”, „zrób M3D-n” (lista poprawek w Notion).
---

# Model 3D domu i ogrodu

Model to **szkic roboczy do oglądania i rozmów** (z projektantem, wykonawcą, w domu), nie dokumentacja: wymiary sprawdza
się w projekcie, sprawy konstrukcyjne z konstruktorem. Powstaje w całości z plików danych – skrypt kasuje i odtwarza scenę,
więc każda trwała zmiana idzie do danych, nigdy „ręcznie” do Blendera.

## Gdzie co leży

| Co | Gdzie |
|---|---|
| Dane, skrypty, zapisany model, podglądy | **prywatny** folder modelu – `<folder modelu>`, domyślnie `Projekty/Model 3D` w folderze budowy (własne repo git, poza tym harnessem) |
| Zasady sesji w folderze modelu | `<folder modelu>/CLAUDE.md` – przeczytaj na początku |
| Format danych (pola, współrzędne, typy elementów) | `<folder modelu>/dane/FORMAT.md` – czytaj zamiast kodu |
| Stan prac: co gotowe, co czeka na inwestora, co przybliżone | `<folder modelu>/STAN.md` |
| Instrukcja dla inwestora (chodzenie po modelu, polecenia) | `<folder modelu>/INSTRUKCJA.md` |
| Rysunki źródłowe (projekt, mapa geodety, koncepcja ogrodu, wizualizacje) | folder budowy – ścieżki w `<folder modelu>/dane/projekt.json` |

W harnessie nie ma danych projektu (wymiarów, współrzędnych, adresu) – są w folderze modelu. Nie przepisuj ich do
procedur, commitów harnessu ani do Notion bez prośby.

## Zasady

1. **Zmiana = dane + przebudowa.** Zmieniaj `dane/*.json` (dom, wnętrza, ogród, kamery, materiały) i przebuduj. Kod
   w `narzedzia/` zmieniaj tylko, gdy danych nie da się tak opisać (nowy typ elementu) – wtedy uzupełnij też `FORMAT.md`
   i kontrolę danych.
2. **Decyzje inwestora są nadrzędne wobec rysunków** (lista `decyzje_inwestora` w danych domu). Nie cofaj ich przy
   „poprawianiu wg projektu”, nawet gdy rysunek pokazuje inaczej; nową decyzję dopisz do tej listy.
3. **Każde założenie do `do_weryfikacji`.** Czego nie ma na rysunku, a jest w modelu (przyjęta wysokość, kształt, materiał),
   zapisz tam jednym zdaniem; sprawy konstrukcyjne z dopiskiem „do potwierdzenia z konstruktorem”. Po zmianie zaktualizuj
   `STAN.md` (sekcje „Gotowe”, „Do zrobienia”, „Przybliżenia”).
4. **Fakt z projektu ≠ szacunek.** W odpowiedzi rozróżniaj: wymiar z rysunku, wartość przyjęta, pomysł do decyzji.
   Decyzje budowlane (układ, materiały, otwory) należą do inwestora – zapytaj z propozycją domyślną; wariant techniczny
   modelowania wybierz sam.
5. **Zasoby z internetu tylko po zgodzie inwestora na listę** (źródło, licencja, rozmiar); domyślnie proceduralnie: materiały
   w realnej skali, meble i rośliny buduje skrypt.
6. **Blender jest jeden.** Budowanie i zrzuty rób sam, po kolei; czytanie rysunków możesz rozdzielić na pomocników
   (każdy zwraca fragment danych z niepewnościami), w miarę możliwości na tańszym modelu.

## Typowa zmiana – kroki

1. Przeczytaj `<folder modelu>/CLAUDE.md` i fragment `FORMAT.md` dotyczący zmiany; znajdź element w danych po `id` /
   nazwie pomieszczenia.
2. **Zrzut „przed”** z kamery, która widzi zmieniane miejsce (albo ustaw widok) – zapisz do `podglad/`.
3. Zmień dane. Uruchom kontrolę bez Blendera: `python3 narzedzia/sprawdz.py` – błędy popraw przed przebudową (przy błędach
   skrypt budujący nie rusza sceny).
4. Przebuduj (niżej). Przeczytaj podsumowanie: liczba obiektów, ostrzeżenia, nieudane kroki.
5. **Zrzut „po”** z tego samego miejsca; obejrzyj oba i sprawdź, czy zmiana jest tam, gdzie miała być, i czy nic obok się
   nie zepsuło. Pokaż inwestorowi „po” (i „przed”, gdy różnica jest subtelna).
6. Dopisz założenia do `do_weryfikacji`, zaktualizuj `STAN.md`; na prośbę „zapisz model” zapisz plik sceny.
7. Zmiany w folderze modelu zacommituj w jego prywatnym repo (`git add <pliki>`, bez plików odtwarzalnych – `.gitignore`);
   push tylko na polecenie inwestora.

## Przebudowa i podgląd

- **Przez konektor Blendera** (Blender otwarty z dodatkiem MCP): wykonaj w Blenderze skrypt budujący z folderu modelu –
  `S = "<folder modelu>/narzedzia/buduj.py"; exec(open(S).read(), {"__file__": S, "__name__": "__main__"})`.
  Opcje podaj w słowniku jako `"ARGS": [...]` (np. `["--bez", "ogrod,wnetrza"]` przy pracy nad samą bryłą).
- **Droga zapasowa bez konektora** (Blender bez okna – działa także bez otwartego programu i w automacie):
  `<Blender> -b --python-exit-code 1 -P narzedzia/buduj.py -- --zapisz` w folderze modelu. Podgląd w tej drodze:
  `<Blender> -b --python-exit-code 1 -P narzedzia/rendery.py -- --tylko elewacje,kamery` → obrazy w `podglad/`.
  Na Macu `<Blender>` to `/Applications/Blender.app/Contents/MacOS/Blender`.
- Obie drogi dają ten sam model: porównaj `suma_kontrolna` w `model/raport.json` po przebudowie każdą z nich. Druga
  przebudowa z rzędu nie może zmienić liczby obiektów ani dodać nazw z końcówką `.001`.
- **Zrzut z okna bywa nieaktualny** po zmianie kamery: przełącz widok PERSP → CAMERA, odśwież obszar (`tag_redraw()`)
  i zrób zrzut ponownie; gdy nadal się nie zgadza, zrób render z kamery skryptem `rendery.py`.
- Porównanie z projektem: rendery ortogonalne czterech elewacji zestaw z arkuszami elewacji, ujęcia „jak wizualizacja”
  z wizualizacjami architekta.

## Lista poprawek inwestora („wprowadź poprawki modelu”, „zrób M3D-n”)

Inwestor wpisuje poprawki do modelu w Notion – baza „🏠 Poprawki modelu 3D” na stronie DOM
(`collection://41bf5982-09e7-81e0-8e87-000b02dc8a70`; pola: Poprawka, Status, Gdzie, Szczegóły, Zdjęcie, Odpowiedź asystenta,
Zrobiono, ID „M3D-n”). Baza jest tylko skrzynką – niczego z niej nie wprowadzaj bez polecenia.

1. Pobierz wiersze ze Statusem „Nowa” albo pustym (najstarsze pierwsze); obejrzyj załączone zdjęcia i zrzuty.
2. Każdą poprawkę wprowadź jak typową zmianę (kroki niżej). Życzenie inwestora co do wyglądu domu to jego decyzja – dopisz
   ją do decyzji inwestora w danych domu; gdy jest sprzeczna z rysunkami albo dotyczy konstrukcji, wprowadź ją i dopisz
   pytanie do architekta / konstruktora w pliku stanu modelu.
3. Oznacz wiersze jednym zapisem: „Zrobiona” + Zrobiono + jedno zdanie w „Odpowiedź asystenta”; poprawkę niejasną albo
   niewykonalną – „Pytanie” z pytaniem zwrotnym (nie zgaduj).
4. Bez konektora Notion: ta sama lista jako plik `POPRAWKI.md` w folderze modelu (linia = poprawka; zrobione pod nagłówkiem
   „Zrobione” z datą) – inwestor może ją też podyktować w rozmowie.

Szczegółów wystroju wnętrz (dobór mebli i dodatków) nie zmieniaj bez prośby – inwestor zajmuje się nimi przy projektowaniu
wnętrz; zasoby z internetu pobieraj dopiero po jego zgodzie na listę (źródło, licencja, rozmiar).

## Nowe źródła

- Rzuty w DWG/DXF od architekta zamiast PDF → odczytaj geometrię z DXF (dokładniej niż z PDF), zaktualizuj dane domu,
  porównaj z dotychczasowymi i wypisz różnice > 2 cm; nie nadpisuj decyzji inwestora.
- Nowa mapa geodety → przelicz teren skryptem z folderu modelu (`narzedzia/teren_z_dwg.py`; kotwica układu i rzędna zera
  są w `dane/projekt.json`, nie w kodzie).
- Rysunek w PDF wektorowym: czytaj wektory (zamiana strony na SVG), nie obraz; liczba z łańcucha wymiarowego wygrywa
  z pomiarem wektora przy różnicy do 3 cm.

## Wynik

Po zmianie odpowiedz w blokach z `AGENTS.md` (🛑 / ✅ / ⏳): co zmienione i w którym pliku danych, zrzut „po”, co dopisane do
`do_weryfikacji`, co odłożone. Pytania do inwestora tylko o decyzje budowlane.

## Czego nie robić

- Nie poprawiaj sceny ręcznie w Blenderze, jeśli zmiana ma zostać – przebudowa ją skasuje.
- Nie przenoś danych projektu do tego harnessu (repo publiczne) i nie podpinaj folderu modelu pod repo harnessu.
- Nie traktuj modelu jak dokumentacji: wymiarów do wykonania nie podawaj z modelu, tylko z projektu.
- Nie twórz repozytorium na GitHubie ani nie wypychaj bez zgody inwestora.
