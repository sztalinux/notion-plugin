---
name: ksiazka-domu
description: Książka domu – dokumentacja domu i budowy w Notion („📘 Książka domu” na DOM) – rozdział po każdym odebranym etapie (jak zbudowane, odstępstwa od projektu, zdjęcia przed zakryciem, dostawy i produkty, wykonawcy i gwarancje, protokoły, koszt, uwagi na przyszłość) oraz część „gdzie co biegnie” (trasy instalacji, zawory, rewizje, studzienki, uziom, strefy „nie wiercić / nie kopać”), przeglądy okresowe i spis dokumentów powykonawczych. Używaj, gdy procedura `etap` kończy odbiór etapu, gdy użytkownik mówi „napisz rozdział książki domu”, „zapisz w książce domu…”, „zawór główny jest 1,2 m od narożnika”, „gdzie biegnie rura / kabel…”, „gdzie nie wiercić”, „kto robił dach i do kiedy gwarancja”, „kiedy przegląd…”, „dokumentacja powykonawcza”, „książka domu”. Gdzie leży plik i która wersja jest aktualna – `dokumenty`.
---

# Książka domu

Cel: na koniec budowy inwestor ma jedną dokumentację „jak zbudowany jest mój dom i gdzie co jest”, pisaną na bieżąco –
rozdział po każdym etapie i część „gdzie co biegnie”, z której korzysta się latami (wiercenie, kopanie, awarie, gwarancje).
Asystent składa szkice z danych, które już są w Notion, arkuszu i na Dysku; inwestor czyta i poprawia.

**Gdzie:** Notion → DOM → „📘 Książka domu” (`415f5982-09e7-81e0-90a8-c003b8aaf38d`; strona na dole DOM, odnośnik w zakładce
🗂 Więcej). Zakładki: Dane domu · A. Przebieg budowy · B. Gdzie co biegnie · Przeglądy i konserwacja · Spis dokumentów;
pod nimi propozycja „Co zbierać od teraz”. Rozdziały etapów to podstrony książki. Format główny: Notion; PDF – sekcja E.

## Źródła

| Co | Skąd |
|---|---|
| Dane domu, parametry, uczestnicy | odnośniki na stronie książki: „📐 Dane projektu (ściąga)”, „📇 Kontakty”, Umowy i gwarancje – **nie przepisuj**, jedna informacja ma jedno miejsce (`budowa`, zasady 8 i 11) |
| Co zrobiono w etapie, kiedy, kto | Dziennik budowy (Etap, Krok harmonogramu, Zdjęcia, Ujęcia przed zakryciem, Dokumenty z dnia, Problemy / usterki) i Harmonogram (kroki etapu, Kto, Wykonawca) |
| Jak zbudowane | projekt (ściąga, przewodnik po dokumentach) + co wykonano naprawdę (Dziennik, protokół odbioru z `etap` C) |
| Odstępstwa od projektu | Notatnik: Typ Decyzja, Etap = ten etap, Status Ustalone / Zrobione – co inaczej, dlaczego, kto zatwierdził; Rejestr sprzeczności (rozstrzygnięte SP o tym etapie) |
| Dostawy i produkty | 🧱 Zakupy budowy: Etap = ten etap, Status Dostarczone – Pozycja, Specyfikacja, Dostawca, Uwagi (producent, typ, partia), **Dokumenty** (link do `Dostawy/<Etap>/` na Dysku) |
| Kto robił, gwarancja | Umowy i gwarancje (Odbiór, Gwarancja do, Rękojmia do, Zgłaszanie usterek); osoby – odnośnik do „📇 Kontakty”, bez telefonów i e-maili |
| Protokoły i odbiory | protokół z `etap` C, wpisy kierownika (`Dziennik budowy KB/`), protokoły prób, inwentaryzacja geodety – folder budowy (`dokumenty`) |
| Koszt etapu | arkusz kosztorysu, zakładka Etapy (WYDANE) – tylko odczyt, z datą stanu; arkusz wygrywa przy rozbieżności (`koszty`) |
| Gdzie co biegnie | zdjęcia z miarą w `<Etap>/<NN Krok>/przed zakryciem/`, pole „Ujęcia przed zakryciem” w Dzienniku budowy, „Plan przepustów i tras instalacji” (plan sprzed wykonania), szkice powykonawcze instalatorów, mapa geodety |

## A. Rozdział etapu (po odbiorze – wywołuje `etap` C)

1. Rozdział powstaje **po odbiorze całego etapu** (wynik „odebrane” albo „odebrane warunkowo”) – nie po pojedynczym kroku,
   bo przed odbiorem stan się jeszcze zmienia. Odebrane warunkowo → otwarte usterki wymień w sekcji „Protokoły i odbiory”.
2. Zbierz źródła z tabeli dla tego etapu. Czego brakuje (np. zdjęć przed zakryciem dla kroku, WZ dostawy) – nie zgaduj:
   wpisz „brak – <czego>” w sekcji, a listę braków podaj w odpowiedzi.
3. Złóż szkic wg `references/szablon-rozdzialu.md` (stały układ ośmiu sekcji). Oznaczaj pewność jak w `budowa`, zasada 2:
   `[projekt]`, `[wykonano]` (Dziennik, protokół, zdjęcie), `[szacunek]`. Zdjęć nie wklejaj – linki do folderów kroków
   i `Dostawy/<Etap>/` (tak jak w Dzienniku budowy).
4. Zapisz: podstrona książki „<Etap> – rozdział” (ikona etapu) jednym wywołaniem, Status szkicu w pierwszej linii
   („Szkic asystenta <data> – do przeczytania”); w zakładce „A. Przebieg budowy” zamień linię „<Etap> – czeka na odbiór
   etapu” na odnośnik do rozdziału z datą odbioru. Strony książki zmieniaj punktowo, nigdy całą treścią.
5. W tym samym przebiegu uzupełnij część B (sekcja B, kroki 2–3) punktami z tego etapu, a „Spis dokumentów” – dokumentami
   z protokołów i dostaw (nazwa, etap, link).
6. W odpowiedzi: link do rozdziału, braki z kroku 2 i pytanie o odstępstwa, których nie da się ustalić z Notatnika.
   Inwestor poprawia tekst w Notion; po jego „przeczytane” zmień pierwszą linię na „Sprawdzony przez inwestora <data>”.

## B. Gdzie co biegnie (punkt dokumentacji)

Wejście: „zapisz w książce: zawór główny wody 1,2 m od narożnika NE, 0,4 m od ściany”, zdjęcie z miarą, szkic instalatora,
mapa geodety albo krok A.5.

1. Ustal obszar: Działka / Pod płytą i w piwnicy / W ścianach i stropach (toggle w zakładce B).
2. Wiersz tabeli: **Co** · **Gdzie** (odległość od dwóch stałych punktów – narożnik, oś ściany, krawędź płyty) ·
   **Głębokość / wysokość** · **Średnica / przekrój** · **Zdjęcie** (link do pliku lub folderu `przed zakryciem/`) ·
   **Źródło** (pomiar inwestora z datą, szkic instalatora, mapa geodety, `[projekt]` gdy tylko plan). Brak jednej odległości
   → wpisz punkt z „?” i zapytaj w odpowiedzi – bez dwóch odległości punktu nie da się potem odnaleźć.
3. Strefy „Nie wiercić / nie kopać / nie kuć” pod tabelą obszaru: trasa + pas (np. „ściana kuchni, pas 30 cm nad blatem –
   rury wody”). Strefę wyznacza pomiar albo szkic, nie sam projekt.
4. Ten sam punkt już jest → popraw wiersz (dopisz nowe źródło), nie dubluj. Pomiar przeczy projektowi → zostaw pomiar,
   a rozjazd zapisz w rozdziale etapu („Odstępstwa”) i w Notatniku (`notatka`, Typ Decyzja albo Pytanie).
5. Rysunek tras na podkładzie z projektu – tylko na prośbę, jako orientacyjny; wiążące są pomiary i mapa geodety.

## C. Odczyt („gdzie biegnie…”, „gdzie nie wiercić”, „kto robił…”, „kiedy przegląd”)

Czytaj stronę książki i podstrony rozdziałów; nie ma w książce → źródła z tabeli (Dziennik, zdjęcia, Plan przepustów)
z wyraźnym „nie ma w książce – z <źródło>” i propozycją dopisania (sekcja B). Plan sprzed wykonania nie jest pomiarem –
mów to wprost, zanim inwestor zacznie wiercić.

## D. Przeglądy i spis dokumentów

- **Przeglądy i konserwacja:** wiersz na urządzenie lub element (co, jak często, ostatnio, następny, kto / podstawa –
  instrukcja, karta gwarancyjna, przepis). Uzupełniaj, gdy urządzenie trafia do domu (dostawa, odbiór instalacji) albo na prośbę;
  warunek gwarancji z przeglądem → także zadanie w TASKS z terminem tylko na „dodaj” (`harmonogram`, B).
- **Spis dokumentów:** dokument, etap, link do pliku na Dysku. Dokumentów nie kopiuj do Notion – plik zostaje w folderze
  budowy (`dokumenty`).

## E. Wersja zamrożona (PDF)

Na start brak narzędzia. Na prośbę: inwestor eksportuje stronę z podstronami do PDF w Notion i zapisuje w
`Dom/Książka domu/` na Dysku („Książka domu – <etap> – RRRR-MM.pdf”); podpowiedz mu to po każdym sprawdzonym rozdziale.
PDF ze zdjęciami w treści i składanie z folderu budowy – osobny pomysł do wdrożenia później (POM-2, „co zostało”).

## Bez Notion (droga zapasowa)

- Claude Code bez Notion: szkic rozdziału jako Markdown do folderu budowy `Książka domu/<Etap> – rozdział.md` (poza repo);
  po powrocie dostępu przenieś do Notion i zostaw plik jako kopię.
- Czat i telefon bez Notion: punkt dokumentacji słowami do „📥 Skrzynki” (`budowa`, zasada 13) – Mac przeniesie go do
  Notion; rozdział etapu odłóż do sesji z Notion.
- Ostatni wyeksportowany PDF i zdjęcia na Dysku działają bez Notion i bez asystenta.

## Nawyki (propozycja)

Lista „Co zbierać od teraz” na stronie książki to **propozycja do potwierdzenia przez inwestora** – nie wymuszaj jej
i nie twórz z niej zadań. Gdy w rozmowie o bramce albo dostawie brakuje czegoś z listy (zdjęcie z miarą, WZ, karta),
przypomnij jednym zdaniem. Pełna lista i uzasadnienie: `references/nawyki.md`.

## Czego nie robić

- Nie przepisuj ściągi projektu, kontaktów ani kwot z innych miejsc – odnośnik albo „stan na <data>” z arkusza.
- Nie pisz rozdziału przed odbiorem etapu i nie zgaduj tras ani wymiarów – brak danych to „?” i pytanie.
- Nie wklejaj zdjęć do Notion (linki do Dysku); nie kopiuj dokumentów do Notion.
- Nic z książki nie trafia do repo (adresy, osoby, wymiary domu) – w repo tylko procedura i szablon na zmyślonych danych.
