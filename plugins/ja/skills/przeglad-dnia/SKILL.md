---
name: przeglad-dnia
description: Zaplanowane przebiegi bez inwestora (launchd na Macu przez claude -p) w dwóch trybach – SZYBKI (co godzinę w ciągu dnia) rozkłada nowe wpisy z „📓 Dziennika” (i strony z widgetu na najwyższym poziomie Private) na bieżąco i kończy się od razu, gdy nic nie ma; WIECZORNY robi podsumowanie dnia (z ręcznymi zmianami w zadaniach i uzupełnieniem ich pustych kolumn) i plan dnia na stronie „☀️ Dziś” w zakładkach (przegląd, budowa, prywatne, praca, wczoraj; historia w „📆 Przeglądy dzienne”), budowa dodatkowo w „📆 Przeglądy dzienne – budowa” na DOM – i linię „🤖” w Dzienniku, plus analizę nowych pomysłów i rozkminki, o które inwestor prosi we wpisie („przygotuj mi…”, „jakie pytania…”). Używaj, gdy uruchamia go automat na Macu („Dziennik – szybki przebieg”, „Przegląd dnia”) albo użytkownik mówi „przegląd dnia”, „podsumuj dzień”, „plan na jutro”, „wieczorny przegląd”, „ogarnij dzisiejsze”.
---

# Przegląd dnia – tryb szybki i wieczorny

Dwa zaplanowane przebiegi uruchamia **launchd na Macu** przez `claude -p` z lokalnym serwerem MCP Notion (skrypt poza repo) –
to jedyna droga: zaplanowanych zadań na claude.ai nie używamy (konektor Notion jest tam zablokowany). Ręcznie – prośba
w rozmowie, te same zasady:

| Zadanie | Kiedy | Polecenie | Co robi |
|---|---|---|---|
| Dziennik – szybki przebieg | co godzinę 8:05–22:05 i 22:30 | „Dziennik – szybki przebieg (skill przeglad-dnia z pluginu ja, tryb szybki)” | rozkłada nowe wpisy; pusto → koniec bez zapisów |
| Przegląd dnia | raz w nocy, 2:00 (przegląd poprzedniego dnia) | „Przegląd dnia (skill przeglad-dnia z pluginu ja, tryb wieczorny)” | ostatni szybki przebieg + zmiany w zadaniach + pomysły + plan dnia na stronie ☀️ Dziś |

Ręcznie w rozmowie: „przerób dziennik” = tryb szybki, „przegląd dnia” / „podsumuj dzień” = tryb wieczorny, „plan dnia” = tylko
krok 8 na dziś (odczyty kroków 3–7, bez zapisów poza stroną ☀️ Dziś).

## Zasady trybu bez inwestora (oba tryby)

- Nie ma kogo zapytać: niejasne → pytanie w Notion (okienko pod wpisem w „📝 Wpisy”; sprawy spoza wpisów – Dziennik „❓”,
  strona pomysłu), nie tylko w odpowiedzi.
- Nie wybieraj ani nie zgaduj decyzji za inwestora; nie zmieniaj układu ani kwot planu w arkuszu kosztów ani terminów kroków
  Harmonogramu budowy (wyjątki: termin kroku podany przez inwestora we wpisie i przesunięcie z relacji o tempie prac – `harmonogram` C, wstęp i C.4) (wydatki, wyceny i plan kwoty, który inwestor sam podał we wpisie, zapisuj w kolejce „💸 Wydatki → arkusz” wg `koszty`
  B/B2/B3 – to nie decyzja; własnych szacunków planu nie zapisuj) – zostaw wpis z pytaniem i propozycją (`wpisy`, krok 4). Nowy obszar Dziennika tylko proponuj, nie dodawaj sam.
- Decyzję, którą inwestor **sam napisał** – wpis „SP-n: …” albo „decyzja: …”, pole Decyzja w Rejestrze sprzeczności –
  domknij ze wszystkimi skutkami (Status, data, Notatnik, wiedza, temat) wg `wiedza/references/sprzecznosci.md` (plugin
  dom-budowa), „Bez inwestora”. Tekst w polu Decyzja jest odpowiedzią – własny wariant, połączenie opcji albo rozstrzygnięcie
  części dylematu też domykasz (z dopiskiem asystenta); pytanie tylko przy „?”, „nie wiem”, otwartym „A albo B” lub sprzeczności.
  Pole Decyzja sprawdza wieczór (krok 3) – każdy przebieg od nowa, także wiersze z czekającym pytaniem.
- Bez planu do akceptacji; zapisy wsadowo (`ja`, zasada 2); odczyt baz przez zapisane widoki i wyszukiwarkę (`ja`, zasada 3), nie SQL.
- Błąd zapisu (brak uprawnień, limit) → nie ponawiaj w kółko; odnotuj „nie zapisano: …” i zakończ.
- W odpowiedzi (log zadania) bez treści emocji i notatek o dziecku – liczby i linki.

## A. Tryb szybki – ma być tani

1. **Pięć odczytów – zawsze wszystkie, także gdy pierwszy coś dał:** Skrzynka – dokumenty Claude o tytule „📥 Skrzynka”,
   sekcja „Nowe” (`wpisy/references/skrzynka.md`; brak narzędzia Claude Docs → pomiń i napisz „Skrzynka – brak odczytu”), strona Dziennik
   (`3f8f5982-09e7-80c8-a154-c59aeb844e8f`), strona „📝 Wpisy” (`3faf5982-09e7-80b2-9b33-c48745d67a4f` – bloki w jej treści
   i lista podstron) i lista stron najwyższego poziomu Private (narzędzie listy stron prywatnych; porównaj ID z listą
   stałych stron w `ja/references/notion-mapa.md`; 🔒 Prywatne nie otwieraj). Otwórz tylko strony spoza listy. Piąty: widok
   „⚠ Błędy do zgłoszenia” w „💸 Wydatki → arkusz” (tryb view, `koszty`, sekcja E) oraz stan stron z komunikatów 💸 pod
   „🔔 Komunikaty asystenta” we „Wpisach”. Lista „Komunikaty z automatów Maca” w poleceniu przebiegu (dokleja ją
   `przeglad.py`, gdy coś się zepsuło albo ustąpiło) to szóste źródło – bez odczytu.
   Nie pobieraj jeszcze Obszarów, przewodnika ani baz. Brak narzędzia do listy stron prywatnych → to źródło pomiń
   i napisz „widget – brak odczytu” w odpowiedzi i w linii „🤖” (`wpisy`, krok 1).
2. **Nic nowego → koniec.** Brak bloków na pierwszym poziomie Dziennika i w treści „Wpisów” (wpis z okienkiem ❓ bez
   odpowiedzi się nie liczy), podstron w „Wpisach” i nowych stron w Private (definicja w `wpisy`), brak pozycji w „Nowe”
   Skrzynki i brak odpowiedzi inwestora (tekst w okienku ❓ we „Wpisach”; w Dzienniku „❓” – dopisek albo zaznaczony
   checkbox; `wpisy/references/pytania.md`), brak wierszy w widoku błędów i komunikatów 💸, których strona nie jest już
   „Błąd”, brak listy od automatu w poleceniu i brak odpowiedzi pod blokami 🔔 (blok 🔔 bez odpowiedzi się nie liczy – inaczej
   każdy przebieg przestałby być tani) → odpowiedz jedną linią „Dziennik: nic nowego (<godzina>;
   widget: 0, Skrzynka: 0)”
   i zakończ. **Zero zapisów** – nie dopisuj linii „🤖”, nie zmieniaj strony.
3. **Inwestor może jeszcze pisać – oceniaj każde źródło osobno** (treść Dziennika, treść „Wpisów”, każda podstrona,
   każda strona z widgetu). Źródło edytowane mniej niż 15 minut temu (czas ostatniej edycji strony), którego najnowszy wpis
   jest pusty albo urwany w pół zdania, pomiń w tym przebiegu – następny je weźmie; **pozostałe źródła przetwórz**. Sam
   brak kropki to nie urwanie (z telefonu inwestor pisze bez kropek). Tylko gdy pominąłeś wszystko, co nowe →
   „Dziennik: pomijam, świeże wpisy (<godzina>)” i zakończ. Pusta strona z widgetu starsza niż 15 minut → pominięta
   (`wpisy`, krok 6).
4. **Są wpisy:** procedura `wpisy`, kroki 2–7, bez pytań w rozmowie (wyjątki z zasad wyżej). Komunikaty (lista od automatu,
   błędy kolejki 💸 – `koszty`, E, odpowiedzi pod 🔔) – `wpisy/references/pytania.md`, C, w tej samej edycji „Wpisów”. Linia „🤖” w bloku dnia –
   krótka, z godziną, bez wyliczania zapisów (te są w podpunktach wpisów, `wpisy` krok 6): `🤖 11:00: przetworzono 2
   (zadania 1, emocje 1), czeka na Ciebie 1, świeże pominięte 1`; liczby per źródło – tylko w odpowiedzi (log). Kolejne
   przebiegi tego dnia dopisują swoje linie (każdą z jej śladem) na górze tego samego bloku, nad wcześniejszymi
   (`wpisy` krok 7); tytuł bloku pokazuje sumę dnia. W odpowiedzi
   podaj nowe wpisy per źródło – „Dziennik n · Wpisy n · widget n · Skrzynka n” (albo „widget – brak odczytu”) – żeby było
   widać, że przebieg sprawdził wszystkie cztery.
5. Bez analizy pomysłów, bez „jutra”, bez wpisów w przeglądach – to robi wieczór.

## B. Tryb wieczorny – podsumowanie i plan

Budowa i sprawy osobiste mają **osobne przeglądy**, żeby intensywny dzień na budowie nie zasłaniał reszty:
budowa → „📆 Przeglądy dzienne – budowa” na stronie DOM (pisze skill `budowa`, sekcja „Wieczorem”); reszta → „📆 Przeglądy
dzienne” pod Dziennikiem, z jedną linią odsyłającą do przeglądu budowy z tego dnia.

**Kolejność wykonania:** kroki 1–2a, potem **5** i **5a–5c** (luki w zadaniach, kontrola spójności zadań, zakupów i rozmów), dopiero potem 3, 4 i 6–10. Krok 5 idzie przed budową, bo
zadanie prywatne z pustym Obszarem znaczy „Dom” i bez uzupełnienia trafiłoby do przeglądu budowy.

1. **Ostatni szybki przebieg** – jak A.1–A.4, ale bez reguły 15 minut (wieczorem przetwórz wszystko, co jednoznaczne).
   Komunikaty 🔔 z linią `→ ZP-n`: sprawdź Status tych wierszy „🧯 Znane problemy” (wyszukiwarka z parametrem bazy) –
   „Rozwiązany” albo „Zostaje” → blok do „Przetworzone” (`wpisy/references/pytania.md`, C.5). Wiersze ZP „Czeka na mnie”
   (widok „🧯 Otwarte”) bez bloku 🔔 → dodaj blok (tamże, C.5).
2. **Pomysły na rozwój** – `rozwoj-harnessu`, sekcja C: Status Nowy lub pusty → analiza (max 3, najstarsze pierwsze);
   „Pytania do mnie” z odpowiedzią → analizuj dalej. Niczego nie wdrażaj.
   **Kontrola spójności pomysłów (grupa P)** – z jednego odczytu całej tablicy pomysłów (wszystkie statusy, nie tylko „Nowy”): „Zrobione” bez „Zrobiono
   w wersji”, „Do zrobienia” / „Przeanalizowany” przy wdrożeniu zapisanym w polu albo w nagłówku `CHANGELOG.md`, „gałąź …”
   już scalona. Pole wersji uzupełniasz tylko z nagłówka CHANGELOG z numerem POM; **Status zmienia dopiero ☑ inwestora**
   (pytanie w „❓”, klucz `KS-P…`). Reguły i obsługa odpowiedzi: `references/kontrola-spojnosci-pomysly.md`.
2a. **Rozkminki – tylko na prośbę z wpisu** (ślad `→ 🧠 rozkminka wieczorem` w dzisiejszym lub wczorajszym bloku
   „Przetworzone”, `wpisy` krok 5, **także ślady z kroku 1 tego przebiegu** – na stronie ich jeszcze nie ma, zapisz je od razu
   jako `→ 🧠 rozkminka: <wzmianka>`; z własnej inicjatywy nie rób – to koszt). Max 2, najstarsze pierwsze; reszta jutro
   („rozkminki czekają: n” w „⚠ Na teraz”). Procedura tematu **tylko odczytem**: budowa – spotkanie, decyzja → `przygotowanie`
   („Bez inwestora”), technika → `analiza-techniczna`, oferta → `oferta`, terminy → `harmonogram`; osobiste – skill `ja` obszaru.
   Wynik = sekcja „🧠 Rozkminka: <temat>”: budowa → krok 3, reszta → krok 8. Bez zapisów do baz – nowe pytania, zadania
   i decyzje → jedno „❓” w Dzienniku (`wpisy/references/pytania.md`, B). Ślad zmień na `→ 🧠 rozkminka: <wzmianka wpisu>` (krok 9).
3. **Budowa** – skill `budowa` (plugin dom-budowa), sekcja „Wieczorem”: sam zbiera dzień i najbliższe 7 dni budowy (zwraca punkty do zakładki 🏗) i dopisuje wpis
   w „📆 Przeglądy dzienne – budowa” (gdy dzień budowy był pusty – nie pisze); najpierw domyka sprzeczności z Decyzją wpisaną
   przez inwestora; ostrzeżenie pogodowe dopisuje tylko przy przekroczonym progu w dniu roboty wrażliwej wpisanej w Uwagach
   kroku i w 7 dniach pielęgnacji betonu (`etap/references/pogoda.md`; codziennej prognozy nie ma – inwestor patrzy sam) –
   to „poranny brief” bez osobnego zadania. Weź z niego link do wpisu, 1 linię skrótu (z ⚠️ pogodowym, jeśli jest), liczbę domkniętych SP
   i punkty do zakładki 🏗 planu (`budowa/references/wieczorem.md`, krok 4).
4. **Dziś – sprawy osobiste** (tylko odczyt): blok dzisiejszego dnia w „Przetworzone” (wpisy obszarów innych niż Budowa,
   liczby per obszar), dzień pracy z Dziennika produktywności, liczba wpisów emocji z dziś (bez treści), nowe punkty na stronie
   dziecka, wpisy z okienkiem ❓ we „Wpisach”, bloki pod „🔔 Komunikaty asystenta” (liczba) i pozycje „❓” Dziennika. Zadania zmienione dziś – krok 5.
5. **Zadania – zmiany dnia i luki w kolumnach** (wszystkie obszary; inwestor zmienia statusy i kończy zadania sam w Notion,
   więc nie ma ich we wpisach). Odczyt: widok TASKS „🤖 Zmiany – od wczoraj (przegląd dnia)” (tryb view, ID w
   `ja/references/notion-mapa.md`; `has_more` → następna strona). Widok daje dwa dni, bo „dziś” w filtrze Notion zależy od
   strefy konta – **dzień utnij sam**: zostaw wiersze z `Last edited time` w **dniu przeglądu** (linia „Teraz” w poleceniu;
   przebieg rusza o 2:00, więc to wczorajsza data kalendarza): od jego północy do następnej północy czasu polskiego (czasy
   w wyniku są w UTC: północ to 22:00 UTC poprzedniego dnia latem, 23:00 zimą). Notion nie trzyma historii – nie pisz „z X na Y”, klasyfikuj po
   stanie bieżącym:
   - zamknięte: Status DONE albo ARCHIVED (osobne liczby); w toku / czeka: IN PROGRESS, WAITING, BLOCKED, ON HOLD;
     dodane lub zmienione: pozostałe (TO DO, PLANNED, SOMEDAY);
   - wiersze ruszone dziś przez procedury (link do wiersza w śladzie „→ <gdzie>: <link>” w dzisiejszym bloku „Przetworzone”;
     porównaj z odczytanym widokiem) policz osobno jako „z Dziennika” – ręczne zmiany inwestora nie mają się mieszać
     z automatycznymi.

   **Uzupełnij luki** w tych wierszach według `zadania`, sekcja D (tylko wskazane pola; Status i When nie zmieniaj; wątpliwości
   → jedno zbiorcze „❓” w formacie `wpisy/references/pytania.md`). Zapis wsadowy, jedna edycja na wiersz. Do wpisu w przeglądzie
   (krok 8) i do linii „🤖” weź liczby per kategoria, nazwy zamkniętych i zmienionych (max 5 na obszar, reszta „+k”) i listę
   uzupełnionych pól.

   **5a. Kontrola spójności** – `references/kontrola-spojnosci.md`: zastosuj odpowiedzi inwestora na dawne flagi `KS-…`, potem
   wychwyć nowe rozjazdy (dziś: zadanie budowy ↔ krok Harmonogramu) na wierszach z kroku 5, które mają relację Harmonogram.
   Tylko pytania w „❓” (max 5), żadnych zmian bez ☑ inwestora; licznik „rozjazdy” idzie do kroku 8 i linii „🤖”.
   **5b. Kontrola spójności zakupów** – `references/kontrola-spojnosci-zakupy.md`: zakup Kupione / Odpuszczone ↔ zadanie „Kupić X”
   (flagi „❓” z kluczem `KS-Z…`, wspólny limit 5 z 5a, zmiana statusu dopiero po ☑ inwestora) oraz pytanie o „Kupione dnia”
   z proponowaną datą (tylko zakupy zmienione od wczoraj) i bezpieczne uzupełnienie researchu Zamknięty. Liczniki „rozjazdy”
   i „zakupy” idą do kroku 8 i linii „🤖”.
   **5c. Kontrola spójności: rozmowy** – `references/kontrola-spojnosci-rozmowy.md`: zadanie rozmowy („Porozmawiać / Pogadać /
   Rozmowa” w nazwie, Obszar Dziecko lub Prywatne) DONE (wiersze kroku 5)
   ↔ temat w „💬 Do przegadania” na stronie osoby. Tylko pytanie „❓” z kluczem `KS-R…` (wspólny limit 5 z 5a); po ☑ dopisek
   „✅ przegadane” pod tematem, nic się nie przenosi. Treści tematów nie wypisuj; licznik „rozjazdy” jak w 5a.
6. **Plan – najbliższe 7 dni** (odczyt; jedyne zapisy – suplementy, niżej): TASKS „🗓 Tydzień (7 dni)” (wszystkie obszary,
   z zaległymi; zastępuje „📅 Jutro – wszystko” i „📅 Dziś”) – zakres i „po terminie” licz od **dnia planu** (`references/uklad-wpisu.md`, D);
   praca – Jira (MCP `atlassian`, tylko odczyt), plik `.dom/praca/dzien.json` (commity, PR-y) i widok bazy 🔨 TASKS ze strony 💼 WORK (`uklad-wpisu.md`, D); suplementy z Buy = tak (licznik – **bez** Statusu BREAK / SUSPENDED,
   te to „do sprawdzenia”, niżej), zakupy z 🛒 Zakupy: „Do kupienia” (licznik) i z Terminem
   do jutra (wymień; widok „🛒 Do kupienia”). Na stronie przewodnika (`3f6f5982-09e7-81f5-bade-ec877d8d936a`)
   sprawdź ID, jeśli któryś odczyt się nie powiedzie.

   **Suplementy wstrzymane (kontrola spójności, grupa S1):** suplement z Buy = tak i Statusem BREAK albo SUSPENDED nie jest
   „do kupienia” – nie wliczaj go do licznika ani do zadania „Zamówić suple”, pokaż osobno jako „do sprawdzenia” i zadaj jedno
   zbiorcze pytanie „❓ Odznaczyć Buy?” (klucz `KS-S1-…`, propozycja: tak); pola Buy nie zmieniaj bez ☑ inwestora.
   Reguły, klucze i obsługa odpowiedzi: `references/kontrola-spojnosci-suple.md`.

   **Suplementy po zamkniętym zadaniu** (przed licznikiem): zadanie „Zamówić suple” DONE od poprzedniego wieczornego przeglądu
   (wiersze z widoku kroku 5, bez ucinania do dziś) → Buy = nie suplementom wymienionym w nim (Name i treść strony; jedna
   edycja na wiersz), w linii „🤖” „suple: Buy odznaczone n”; ARCHIVED → Buy zostaje. Inaczej następny krok założy nowe
   zadanie z tą samą listą.
   **Suplementy do zamówienia:** gdy jest choć jeden z Buy = tak (i Status inny niż BREAK / SUSPENDED), poszukaj w TASKS (wyszukiwarka z parametrem bazy, „suple”,
   wśród niezakończonych) otwartego zadania „Zamówić suple”. Jest → dopisz do niego brakujące suplementy (Name i treść strony),
   bez dublowania. Brak → załóż jedno zbiorcze: Name „Zamówić suple: <nazwy>”, Obszar Prywatne, Kategoria Zakup, Kto Ja,
   Priority Medium, Status TO DO, When = dzień przeglądu + 3 dni (najpóźniej, nigdy dalej), Desc jedno zdanie, lista (nazwa,
   kto, link) w treści strony. Poza akapitem wyżej nie ruszaj pola Buy ani bazy 🛒 Zakupy – odznaczenie robi `suple` po „kupiłem”, a zadanie
   zamyka `zadania` po „zamówiłem” / „zrobione”. Dopisz „zadanie: zamówić suple (<termin>)” albo „suple: zadanie już jest”
   w zakładce 🏠 „Kupić” planu (krok 8) i w linii „🤖” (krok 9). Tylko tryb wieczorny; szybki przebieg bez zmian.
7. **Research** (baza 🔎 Research, RES-n; widok „🔎 Do zrobienia” – ID w `ja/references/notion-mapa.md`): weź max 2 najstarsze.
   Dla każdego przeczytaj zlecenie i powiązany zakup / zadanie, zrób research w sieci (aktualne źródła, ceny i sklepy w Polsce)
   i dopisz w treści strony „## Wynik (asystent, data)”: Rekomendacja (1–2 zdania), Opcje (tabela: co, cena orientacyjna,
   plusy, minusy, link), Na co uważać, Źródła. Pole Rekomendacja = jedno zdanie, Status „Gotowy”, Zrobiono = data; w Uwagach
   zakupu albo Desc zadania dopisz „Research RES-n gotowy”. Brak kluczowej informacji (budżet, wymiar, zastosowanie) → zrób,
   co się da, dopisz „### ❓ Pytania (data)” z 1–3 pytaniami (format: `wpisy/references/pytania.md`) i propozycją domyślną,
   Status „Pytania do mnie”, a w Dzienniku „❓” linię „RES-n: <pytanie> (wzmianka)”. Research nie podejmuje decyzji i nie
   zmienia statusów zakupów ani zadań. **Zabezpieczenie** (tylko wieczorem – szybki ma być tani): każda linia RES-n w „❓”,
   której research nie ma już Statusu „Pytania do mnie”, idzie do „Przetworzone” z dopiskiem „→ rozwiązane poza Dziennikiem”.
8. **Plan dnia na stronie ☀️ Dziś + historia** – **codziennie**, także w spokojny dzień; układ, zasady i szablon:
   `references/uklad-wpisu.md`, D. Najpierw nadpisz treść strony ☀️ Dziś (`416f5982-09e7-81b3-b96d-ddd19086bc5b`) planem na dzień
   planu – ramka „najważniejsze” i zakładki 🧭 Przegląd · 🏗 Budowa (z kroku 3) · 🏠 Prywatne (kroki 6–7, 2a) · 💼 Praca · 📊 Wczoraj
   (kroki 1, 4, 5, 2). Potem ta sama treść jako historia na górze „📆 Przeglądy dzienne” (`3faf5982-09e7-81df-a361-cc65fddb81f4`):
   zwijany nagłówek h2 „Plan dnia – <dzień tygodnia> <data planu>”, zakładki jako pogrubione etykiety (`uklad-wpisu.md`, C) –
   **wstawienie na początku strony bez jej odczytu** (strona jest długa; archiwum robi przegląd tygodnia).
   **Ręczny przebieg** (prośba w rozmowie) = osobny wpis z tą samą datą i dopiskiem „(ręczne)”, kolejne „(ręczne 2)”… –
   tak samo w przeglądzie budowy. Nigdy nie nadpisuj wcześniejszego wpisu – sprostowanie to jedna linia kursywą na jego
   górze z odesłaniem.
9. **Linia „🤖”** – na górze dzisiejszego bloku w „Przetworzone”, w tej samej edycji Dziennika co zapisy kroku 1 – tę jedną
   edycję (`wpisy`, krok 7) zrób na końcu przebiegu, po kroku 8, gdy znasz już wszystkie liczby (kroki 3–5 doliczają
   ślad kroku 1 z tego przebiegu – na stronie jeszcze go nie ma; krok 3 dostaje listę wpisów budowy z kroku 1):
   ```
   🤖 15.10 wieczór: dziś przetworzono 6 (budowa 3) · SP: 1 domknięte · zadania: 3 zamknięte, uzupełniono 2 · spójność: 1 nowa flaga, pomysły: 1 wersja uzupełniona · zakupy: 1 flaga, 2 daty · czeka na Ciebie 1 · komunikaty: 1 · pomysły – 1 · research: 1 gotowy · rozkminki: 1 · jutro: 2 prywatne, 3 budowa → przeglądy
   	- jutro: <sprawa – kto – kiedy>      ← max 3 punkty: najpierw prywatne, potem 1 najważniejszy budowy
   ```
10. **Odpowiedź** (log zadania): linia „🤖” + lista zapisów (gdzie, link) i błędów.

## Koszt i częstotliwość

Każdy przebieg to osobna sesja – nawet pusty zużywa limit konta na start (instrukcje, opisy skilli, narzędzia Notion) i jeden
odczyt Dziennika. Dlatego tryb szybki ma wyjście w kroku A.2 bez dalszych odczytów i zapisów, a strona Dziennik ma zostać
krótka (przegląd tygodnia przenosi „Przetworzone” i wpisy obu stron „📆 Przeglądy dzienne” starsze niż 14 dni do archiwum;
wieczór nie czyta stron przeglądów – tylko dopisuje na górze). Godziny ustawia launchd (README automatów); rzadszy szybki = zmiana tam, nie tutaj.

## Rozszerzanie

Nowa rzecz codzienna (np. suplementy do kupienia; osobny poranny brief z powiadomieniem – dopiero po starcie robót, gdy Harmonogram ma daty, i jako przebieg launchd, nie zadanie na claude.ai) = nowy krok trybu wieczornego przed wpisem w Przeglądach
i jeden licznik w linii „🤖”. Tryb szybki zostaje minimalny. Nowy obszar Dziennika nie wymaga zmian tutaj – obsługuje go `wpisy`.
