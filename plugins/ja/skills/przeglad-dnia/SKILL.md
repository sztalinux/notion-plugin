---
name: przeglad-dnia
description: Zaplanowane przebiegi bez inwestora (claude.ai, poza projektem) w dwóch trybach – SZYBKI (co godzinę lub co 2 godziny w ciągu dnia) rozkłada nowe wpisy z „📓 Dziennika” (i strony z widgetu na najwyższym poziomie Private) na bieżąco i kończy się od razu, gdy nic nie ma; WIECZORNY robi podsumowanie dnia (z ręcznymi zmianami w zadaniach i uzupełnieniem ich pustych kolumn) i plan na jutro – sprawy osobiste w „📆 Przeglądy dzienne” pod Dziennikiem, budowa osobno w „📆 Przeglądy dzienne – budowa” na DOM (z odnośnikiem między nimi) – i linię „🤖” w Dzienniku, plus analizę nowych pomysłów. Używaj, gdy uruchamia go zaplanowane zadanie („Dziennik – szybki przebieg”, „Przegląd dnia”) albo użytkownik mówi „przegląd dnia”, „podsumuj dzień”, „plan na jutro”, „wieczorny przegląd”, „ogarnij dzisiejsze”.
---

# Przegląd dnia – tryb szybki i wieczorny

Dwa zaplanowane zadania na claude.ai, oba **poza projektem** (pliki projektu „Dom” nie doklejają się do przebiegu):

| Zadanie | Kiedy | Polecenie | Co robi |
|---|---|---|---|
| Dziennik – szybki przebieg | co 1–2 h w ciągu dnia (np. 8–22) | „Dziennik – szybki przebieg (skill przeglad-dnia z pluginu ja, tryb szybki)” | rozkłada nowe wpisy; pusto → koniec bez zapisów |
| Przegląd dnia | raz wieczorem (np. 21:30) | „Przegląd dnia (skill przeglad-dnia z pluginu ja, tryb wieczorny)” | ostatni szybki przebieg + podsumowanie dnia + zmiany w zadaniach + plan na jutro + pomysły |

Ręcznie w rozmowie: „przerób dziennik” = tryb szybki, „przegląd dnia” / „podsumuj dzień” = tryb wieczorny.

## Zasady trybu bez inwestora (oba tryby)

- Nie ma kogo zapytać: niejasne → pytanie w Notion (Dziennik „❓”, strona pomysłu), nie tylko w odpowiedzi.
- Nie zapisuj decyzji inwestora, rozstrzygnięć sprzeczności (SP), zmian w Excelu ani zmian terminów kroków Harmonogramu
  budowy – zostaw w „❓” z pytaniem i propozycją. Nowy obszar Dziennika tylko proponuj w „❓”, nie dodawaj sam.
- Bez planu do akceptacji; zapisy wsadowo (`ja`, zasada 2); odczyt baz przez zapisane widoki i wyszukiwarkę (`ja`, zasada 3), nie SQL.
- Błąd zapisu (brak uprawnień, limit) → nie ponawiaj w kółko; odnotuj „nie zapisano: …” i zakończ.
- W odpowiedzi (log zadania) bez treści emocji i notatek o dziecku – liczby i linki.

## A. Tryb szybki – ma być tani

1. **Trzy odczyty – zawsze wszystkie trzy, także gdy pierwszy coś dał:** strona Dziennik
   (`3f8f5982-09e7-80c8-a154-c59aeb844e8f`), strona „📝 Wpisy” (`3faf5982-09e7-80b2-9b33-c48745d67a4f` – bloki w jej treści
   i lista podstron) i lista stron najwyższego poziomu Private (narzędzie listy stron prywatnych; porównaj ID z listą
   stałych stron w `ja/references/notion-mapa.md`; 🔒 Prywatne nie otwieraj). Otwórz tylko strony spoza listy.
   Nie pobieraj jeszcze Obszarów, przewodnika ani baz. Brak narzędzia do listy stron prywatnych → to źródło pomiń
   i napisz „widget – brak odczytu” w odpowiedzi i w linii „🤖” (`wpisy`, krok 1).
2. **Nic nowego → koniec.** Brak bloków na pierwszym poziomie Dziennika i w treści „Wpisów”, podstron w „Wpisach” i nowych
   stron w Private (definicja w `wpisy`) i brak odpowiedzi inwestora (dopisek albo zaznaczony checkbox,
   `wpisy/references/pytania.md`) pod pytaniami w „❓” → odpowiedz jedną linią „Dziennik: nic nowego (<godzina>; widget: 0)”
   i zakończ. **Zero zapisów** – nie dopisuj linii „🤖”, nie zmieniaj strony.
3. **Inwestor może jeszcze pisać – oceniaj każde źródło osobno** (treść Dziennika, treść „Wpisów”, każda podstrona,
   każda strona z widgetu). Źródło edytowane mniej niż 15 minut temu (czas ostatniej edycji strony), którego najnowszy wpis
   jest pusty albo urwany w pół zdania, pomiń w tym przebiegu – następny je weźmie; **pozostałe źródła przetwórz**. Sam
   brak kropki to nie urwanie (z telefonu inwestor pisze bez kropek). Tylko gdy pominąłeś wszystko, co nowe →
   „Dziennik: pomijam, świeże wpisy (<godzina>)” i zakończ. Pusta strona z widgetu starsza niż 15 minut → pominięta
   (`wpisy`, krok 6).
4. **Są wpisy:** procedura `wpisy`, kroki 2–7, bez pytań w rozmowie (wyjątki z zasad wyżej). Linia „🤖” w bloku dnia –
   krótka, z godziną: `🤖 11:00: przetworzono 2 (zadania 1, emocje 1), czeka na Ciebie 1, świeże pominięte 1`. Kolejne
   przebiegi tego dnia dopisują swoje linie pod spodem w tym samym bloku; tytuł bloku pokazuje sumę dnia. W odpowiedzi
   podaj nowe wpisy per źródło – „Dziennik n · Wpisy n · widget n” (albo „widget – brak odczytu”) – żeby było widać,
   że przebieg sprawdził wszystkie trzy.
5. Bez analizy pomysłów, bez „jutra”, bez wpisów w przeglądach – to robi wieczór.

## B. Tryb wieczorny – podsumowanie i plan

Budowa i sprawy osobiste mają **osobne przeglądy**, żeby intensywny dzień na budowie nie zasłaniał reszty:
budowa → „📆 Przeglądy dzienne – budowa” na stronie DOM (pisze skill `budowa`, sekcja „Wieczorem”); reszta → „📆 Przeglądy
dzienne” pod Dziennikiem, z jedną linią odsyłającą do przeglądu budowy z tego dnia.

**Kolejność wykonania:** kroki 1–2, potem **5** (luki w zadaniach), dopiero potem 3, 4 i 6–10. Krok 5 idzie przed budową, bo
zadanie prywatne z pustym Obszarem znaczy „Dom” i bez uzupełnienia trafiłoby do przeglądu budowy.

1. **Ostatni szybki przebieg** – jak A.1–A.4, ale bez reguły 15 minut (wieczorem przetwórz wszystko, co jednoznaczne).
2. **Pomysły na rozwój** – `rozwoj-harnessu`, sekcja C: Status Nowy lub pusty → analiza (max 3, najstarsze pierwsze);
   „Pytania do mnie” z odpowiedzią → analizuj dalej. Niczego nie wdrażaj.
3. **Budowa** – skill `budowa` (plugin dom-budowa), sekcja „Wieczorem”: sam zbiera dzień i jutro budowy i dopisuje wpis
   w „📆 Przeglądy dzienne – budowa” (gdy dzień budowy był pusty – nie pisze). Weź z niego link do wpisu i 1 linię skrótu.
4. **Dziś – sprawy osobiste** (tylko odczyt): blok dzisiejszego dnia w „Przetworzone” (wpisy obszarów innych niż Budowa,
   liczby per obszar), dzień pracy z Dziennika produktywności, liczba wpisów emocji z dziś (bez treści), nowe punkty na stronie
   dziecka, wpisy w „❓”. Zadania zmienione dziś – krok 5.
5. **Zadania – zmiany dnia i luki w kolumnach** (wszystkie obszary; inwestor zmienia statusy i kończy zadania sam w Notion,
   więc nie ma ich we wpisach). Odczyt: widok TASKS „🤖 Zmiany – od wczoraj (przegląd dnia)” (tryb view, ID w
   `ja/references/notion-mapa.md`; `has_more` → następna strona). Widok daje dwa dni, bo „dziś” w filtrze Notion zależy od
   strefy konta – **dzień utnij sam**: zostaw wiersze z `Last edited time` od północy czasu polskiego (czasy w wyniku są w UTC:
   północ to 22:00 UTC poprzedniego dnia latem, 23:00 zimą). Notion nie trzyma historii – nie pisz „z X na Y”, klasyfikuj po
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
6. **Jutro – sprawy osobiste** (odczyt; jedyny zapis – zadanie z suplementami, niżej): TASKS „📅 Jutro – wszystko” bez Obszaru Dom i zadania prywatne po terminie
   (When < dziś, niezakończone), suplementy z Buy = tak (licznik), zakupy z 🛒 Zakupy: „Do kupienia” (licznik) i z Terminem
   do jutra (wymień; widok „🛒 Do kupienia”). Na stronie przewodnika (`3f6f5982-09e7-81f5-bade-ec877d8d936a`)
   sprawdź ID, jeśli któryś odczyt się nie powiedzie.

   **Suplementy do zamówienia:** gdy jest choć jeden z Buy = tak, poszukaj w TASKS (wyszukiwarka z parametrem bazy, „suple”,
   wśród niezakończonych) otwartego zadania „Zamówić suple”. Jest → dopisz do niego brakujące suplementy (Name i treść strony),
   bez dublowania. Brak → załóż jedno zbiorcze: Name „Zamówić suple: <nazwy>”, Obszar Prywatne, Kategoria Zakup, Kto Ja,
   Priority Medium, Status TO DO, When = dzień przeglądu + 3 dni (najpóźniej, nigdy dalej), Desc jedno zdanie, lista (nazwa,
   kto, link) w treści strony. Nie ruszaj pola Buy ani bazy 🛒 Zakupy – odznaczenie robi `suple` po „kupiłem”, a zadanie
   zamyka `zadania` po „zamówiłem” / „zrobione”. Dopisz „zadanie: zamówić suple (<termin>)” albo „suple: zadanie już jest”
   w „Jutro – plan” wpisu (krok 8) i w linii „🤖” (krok 9). Tylko tryb wieczorny; szybki przebieg bez zmian.
7. **Research** (baza 🔎 Research, RES-n; widok „🔎 Do zrobienia” – ID w `ja/references/notion-mapa.md`): weź max 2 najstarsze.
   Dla każdego przeczytaj zlecenie i powiązany zakup / zadanie, zrób research w sieci (aktualne źródła, ceny i sklepy w Polsce)
   i dopisz w treści strony „## Wynik (asystent, data)”: Rekomendacja (1–2 zdania), Opcje (tabela: co, cena orientacyjna,
   plusy, minusy, link), Na co uważać, Źródła. Pole Rekomendacja = jedno zdanie, Status „Gotowy”, Zrobiono = data; w Uwagach
   zakupu albo Desc zadania dopisz „Research RES-n gotowy”. Brak kluczowej informacji (budżet, wymiar, zastosowanie) → zrób,
   co się da, dopisz „### ❓ Pytania (data)” z 1–3 pytaniami (format: `wpisy/references/pytania.md`) i propozycją domyślną,
   Status „Pytania do mnie”, a w Dzienniku „❓” linię „RES-n: <pytanie> (wzmianka)”. Research nie podejmuje decyzji i nie
   zmienia statusów zakupów ani zadań. **Zabezpieczenie** (tylko wieczorem – szybki ma być tani): każda linia RES-n w „❓”,
   której research nie ma już Statusu „Pytania do mnie”, idzie do „Przetworzone” z dopiskiem „→ rozwiązane poza Dziennikiem”.
8. **Wpis w „📆 Przeglądy dzienne”** (`3faf5982-09e7-81df-a361-cc65fddb81f4`, pod Dziennikiem) – **codziennie**, także
   w spokojny dzień: zwijany nagłówek „Przegląd dnia – <dzień tygodnia> <data>” na górze strony (najnowszy pierwszy):
   ```
   **Dziś:** 3–6 punktów – prywatne / dziecko / praca (bez treści emocji – tylko „emocje: n wpisów”)
   **Zadania (wszystkie obszary):** zamknięte n (nazwy) · w toku / czeka n · dodane lub zmienione n · z Dziennika n ·
   uzupełniono n wierszy (pola)   ← brak zmian → „bez zmian”
   **Czeka na Ciebie:** n pytań w ❓ (rozwiń w Dzienniku)
   **Jutro – plan:** zadania z terminem wg priorytetu, po terminie na górze, „kupić: n suplementów, n pozycji z zakupów (z terminem: …)”
   **Research:** n gotowych, m czeka na Ciebie – wzmianki stron RES-n (brak researchu → pomiń linię)
   **🏗 Budowa:** <1 linia skrótu> → <wzmianka wpisu z przeglądu budowy z tego dnia>   (brak dnia budowy → „bez zmian”)
   **Rozkminka** (tylko gdy inwestor prosił we wpisie albo dzień przyniósł decyzję do przemyślenia): 2–5 zdań
   ```
   **Ręczny przebieg** (prośba w rozmowie) = osobny wpis z tą samą datą i dopiskiem „(ręczne)”, kolejne „(ręczne 2)”… –
   tak samo w przeglądzie budowy. Nigdy nie nadpisuj wcześniejszego wpisu – sprostowanie to jedna linia kursywą na jego
   górze z odesłaniem.
9. **Linia „🤖”** – na górze dzisiejszego bloku w „Przetworzone”, w tej samej edycji Dziennika co krok 1:
   ```
   🤖 15.10 wieczór: dziś przetworzono 6 (budowa 3) · zadania: 3 zamknięte, uzupełniono 2 · czeka na Ciebie 1 · pomysły – 1 · research: 1 gotowy · jutro: 2 prywatne, 3 budowa → przeglądy
   	- jutro: <sprawa – kto – kiedy>      ← max 3 punkty: najpierw prywatne, potem 1 najważniejszy budowy
   ```
10. **Odpowiedź** (log zadania): linia „🤖” + lista zapisów (gdzie, link) i błędów.

## Koszt i częstotliwość

Każdy przebieg to osobna sesja – nawet pusty zużywa limit konta na start (instrukcje, opisy skilli, narzędzia Notion) i jeden
odczyt Dziennika. Dlatego tryb szybki ma wyjście w kroku A.2 bez dalszych odczytów i zapisów, a strona Dziennik ma zostać
krótka (przegląd tygodnia czyści „Przetworzone” starsze niż 14 dni). Zacznij od co 2 godzin; częściej – gdy limit pozwala.

## Rozszerzanie

Nowa rzecz codzienna (np. poranny brief, suplementy do kupienia) = nowy krok trybu wieczornego przed wpisem w Przeglądach
i jeden licznik w linii „🤖”. Tryb szybki zostaje minimalny. Nowy obszar Dziennika nie wymaga zmian tutaj – obsługuje go `wpisy`.
