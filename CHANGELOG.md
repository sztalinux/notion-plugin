# Changelog

Od 15.10.2026 repo ma dwa pluginy – nagłówek wpisu: `## <plugin> [wersja] – data` (`dom-budowa` albo `ja`).
Starsze wpisy `## [wersja]` dotyczą `dom-budowa`. Wersjonowanie semver osobno dla każdego pluginu:
PATCH = poprawka treści, MINOR = nowa procedura/pole, MAJOR = zmiana struktury danych.

## dom-budowa [2.6.2] – 2026-10-20

- Start sesji Claude Code nie uruchamia już niczego sam: hooki `SessionStart` (skan dokumentów, synchronizacja indeksu wiedzy
  z publikacją kopii, przypominacz jakości wyszukiwania) usunięte z `.claude/settings.json`; polecenia zostają jako pozycje listy
  wyboru na starcie sesji („Dokumenty budowy”, „Indeks wiedzy”). `dokumenty` i `wiedza/references/indeks.md` opisują to wprost.
  PATCH – zmiana treści.

## ja [1.5.5] – 2026-10-20

- Lista wyboru na starcie sesji Claude Code (`CLAUDE.md`): Skrzynka zmian, Pomysły, git pull, Dokumenty budowy, Indeks wiedzy –
  domyślnie nic nie zaznaczone; wcześniej skrzynka, pomysły i przewodnik wykonywały się automatycznie. `ja` („Na starcie rozmowy”)
  i `rozwoj-harnessu` (tabela, krok A.4, sekcja C) zgodne z tym; `AGENTS.md` i README opisują nowy start. PATCH – zmiana treści.

## dom-budowa [2.6.1] – 2026-10-20

- `budowa` („Domknięcie każdej rozmowy”) i `etap` (wynik w rozmowie): ten sam stały format odpowiedzi co w `ja` – 🛑 Potrzebuję
  Twojej odpowiedzi (na górze, tylko gdy coś stoi), ✅ Zrobione, ⏳ Niezrobione. PATCH – zmiana treści.

## ja [1.5.4] – 2026-10-20

- Format odpowiedzi po pracy (🛑 / ✅ / ⏳) jest teraz jedną regułą w `AGENTS.md` (czytają ją wszyscy agenci), a nie tylko w `CLAUDE.md`
  i `ja`; `wpisy` (podsumowanie) i `rozwoj-harnessu` (krok B.8) używają go też.
- `rozwoj-harnessu`, B.6: usunięte „obce zmiany zgłoś” – równoległe sesje nie są powodem do uwag w odpowiedzi; kolizję zgłasza się
  tylko, gdy realnie utrudnia zmianę (`CLAUDE.md`, 0a). PATCH – zmiana treści.

## ja [1.5.3] – 2026-10-20

- HZ-10: `przeglad-dnia`, tryb wieczorny, krok 6 – gdy suplement ma Buy = tak, przegląd zakłada jedno zbiorcze zadanie
  „Zamówić suple: <nazwy>” z terminem najdalej za 3 dni (albo dopisuje do istniejącego, bez dublowania); pola Buy i bazy
  Zakupy nie rusza; wzmianka w „Jutro – plan” i w linii „🤖”.
- `ja`, „Domknięcie rozmowy”: stały format odpowiedzi – 🛑 Potrzebuję Twojej odpowiedzi (na górze, tylko gdy coś stoi),
  ✅ Zrobione, ⏳ Niezrobione. PATCH – zmiany treści. (Reguła równoległych sesji i ten sam format w `CLAUDE.md`.)

## dom-budowa [2.6.0] – 2026-10-19

- Nowe polecenie `tools/wiedza_jakosc.py sedzia` (moduł `tools/wiedza_sedzia.py`) – sędzia LLM dla obserwatora jakości: niezależny
  model ocenia, czy wyniki wyszukiwania odpowiadają na ogólne pytania budowlane (0/1/2), z metrykami P@12, MRR, zgodnością z oceną
  ręczną i porównaniem do poprzedniego przebiegu. Domyślnie tylko na sucho; wysyłka wymaga `--wyslij` i jawnego `--model`.
- Do modelu idą tylko pytanie, teza, szczegóły, temat i etap; pola „Kto” i „Z kim” są zablokowane na stałe, a każdy wiersz
  przechodzi filtr danych osobowych i słów zakazanych (normalizacja tekstu, wzorce telefonów, adresów, e-maili, nazw własnych).
  Model działa bez narzędzi, hooków i serwerów MCP (kontrola zdarzenia init), po kanarku na zmyślonej treści; wyniki wracają
  wyłącznie jako liczby, oceny leżą w pamięci poza repo. Hook startu nigdy nie wywołuje sędziego.
- Nowy `wiedza/references/indeks-sedzia.md`; `indeks-jakosc.md` odsyła do niego.

## dom-budowa [2.5.1] – 2026-10-19

- Kolumna statusu w TASKS nazywa się w Notion „Status”, a procedury i mapy pisały „PLANNED” (to tylko nazwa jednej z opcji
  statusu). Ujednolicone w `notatka` (i `notion-schematy.md`), `harmonogram`, `przeglad-tygodnia` i mapie Notion budowy;
  wartości opcji (TO DO, PLANNED, WAITING…) bez zmian. PATCH – poprawka treści.

## ja [1.5.2] – 2026-10-19

- To samo ujednolicenie w `zadania` (tabela pól i statusów, sekcja D) i w mapie Notion `ja`. PATCH – poprawka treści.

## ja [1.5.1] – 2026-10-19

- `przeglad-dnia`, tryb wieczorny: jawna kolejność wykonania – krok 5 (luki w zadaniach) przed budową, żeby zadanie prywatne
  z pustym Obszarem nie trafiło do przeglądu budowy; rozpoznawanie zadań ruszonych przez procedury po linku w śladzie
  „→ <gdzie>: <link>” (format z `wpisy`), nie po zgadywanym słowie. `zadania`, sekcja D: bez reguły opartej na relacjach
  Harmonogram i Dziennik budowy – widok przeglądu dnia ich nie zwraca. PATCH – poprawka treści.

## ja [1.5.0] – 2026-10-19

- `przeglad-dnia`, tryb wieczorny: nowy krok 5 „Zadania – zmiany dnia i luki w kolumnach” – zadania ze wszystkich obszarów
  zmienione tego dnia (także ręcznie w Notion): zamknięte, w toku, dodane lub zmienione, osobno te ruszone przez procedury;
  wynik w nowej linii „Zadania” wpisu w Przeglądach dziennych i w liczniku linii „🤖”. Odczyt przez nowy widok TASKS
  „🤖 Zmiany – od wczoraj (przegląd dnia)”, dzień cięty po czasie polskim. Kolejne kroki przenumerowane (Jutro 6, Research 7,
  wpis 8, linia „🤖” 9, odpowiedź 10).
- `zadania`: nowa sekcja D – reguły uzupełniania pustych kolumn (Obszar, Kto, Priority, Kategoria, Desc; Status i When bez zmian,
  wątpliwości do „❓”); „zrobiłem X” szuka też zadań zamkniętych w ostatnich 7 dniach, żeby ręcznie zamknięte zadanie
  nie dawało fałszywego „nie znalazłem”.
- Mapa Notion `ja`: widok przeglądu dnia z ID. README i `AGENTS.md`: opis przeglądu dnia.

## dom-budowa [2.5.0] – 2026-10-19

- Nowe narzędzie `tools/wiedza_jakosc.py` – obserwator jakości wyszukiwania w indeksie wiedzy (POM-10): zbiór złoty
  (zapytania wyprowadzone z indeksu plus wbudowany zestaw ogólnych pytań z `tools/wiedza_jakosc_pytania.json`), historia
  przebiegów z porównaniem do poprzedniego i do bazy, alarmy regresji utrzymywane do potwierdzenia w `raport`,
  porównanie z wyszukiwarką Notion (`notion`, tylko odczyt, budżet żądań), ręczna ocena trafności (`reczna`), własne
  pytania kontrolne (`dodaj`) i cichy przypominacz tygodniowy (`przypomnij`, hook startu sesji).
- `tools/wiedza.py szukaj`: lokalny dziennik zapytań `szukaj.log.jsonl` (tylko ta maszyna, tryb 600, rotacja 2 MB,
  wyłączany `WIEDZA_LOG=0`); kanał zapytania z `WIEDZA_KANAL` albo środowiska Claude Code.
- Dane obserwatora leżą wyłącznie w `.dom/wiedza/jakosc/` poza repo; `.gitignore`, hook `pre-commit` i `tools/build.py`
  blokują ich nazwy w repo.
- Nowy `wiedza/references/indeks-jakosc.md`; `indeks.md` i `przeglad-tygodnia` (Spójność) odsyłają do raportu jakości.
- `.claude/settings.json`: trzeci hook startu (`wiedza_jakosc.py przypomnij --cicho`) i zezwolenie dla narzędzia.

## dom-budowa [2.4.1] – 2026-10-18

- `tools/wiedza.py szukaj`: poprawka klasy zapytań, które po 2.4.0 wypadały gorzej niż dawniej (pytanie z rzadkim słowem spoza
  tematu, np. czasownikiem, dostawało największą wagę w rankingu). Dopełnienie częściowe włącza się poniżej 12 trafień
  dopasowania wszystkich słów (było 5), wiersze dopełnienia są porządkowane najpierw liczbą pasujących słów, a w części
  z pełnym dopasowaniem wyżej stoją wpisy z dokładną formą wpisanego słowa. Pomiar na 3383 zapytaniach: względem wersji sprzed
  poprawek 616 wygranych i 16 przegranych, względem 2.4.0 – 48 wygranych i 5 przegranych (straty po 1–2 punkty).
- `references/indeks.md`: opis dopełnienia częściowego i pola `pelnych` dostosowany do nowych reguł.

## dom-budowa [2.4.0] – 2026-10-17

- Nowe narzędzie `tools/wiedza.py` – indeks Bazy wiedzy: lokalna kopia czterech baz Notion w SQLite z wyszukiwaniem
  pełnotekstowym, tylko do odczytu (Notion zostaje jedynym miejscem zapisu). Polecenia: `sync`, `szukaj`, `temat`,
  `duplikaty`, `stan`, `publikuj`; kopia dla czatu trafia do prywatnego repo. Synonimy budowlane w `tools/wiedza_synonimy.txt`.
- Nowy `wiedza/references/indeks.md` – trzy kanały użycia indeksu: Claude Code, czat/telefon i przebieg nocny; `szukaj --json` zwraca też `pelnych` (liczba trafień pełnych, reszta to dopełnienie częściowe).
- Odporność kopii indeksu: `publikuj --wymus` i `--reset`, kontrola, że repo kopii jest prywatne, samonaprawa uszkodzonego
  indeksu i uprawnienia 700/600; nowy `wiedza/references/indeks-awarie.md` opisuje komunikaty, odnowienie tokenów i odtworzenie repo.
- `wiedza`: A.5 szukanie w indeksie, A.7 synchronizacja po zapisie, E odczyt przez indeks; `notion-wiedza.md`: krok 7 planu
  zapisu, typy pól Rejestru sprzeczności i dopasowanie pola „Pytanie do” po prefiksie.
- `budowa` (zasady 6 i 10): indeks jako pierwszy sposób szukania w wiedzy; `przeglad-tygodnia` (Spójność): stan indeksu
  i duplikaty; mapy Notion (`budowa/references/notion-mapa.md`, `zrodla.md`) opisują indeks.
- `.claude/settings.json`: drugi hook startu (`sync --publikuj --cicho`) i zezwolenie dla `tools/wiedza.py`.
- Utwardzenie repo: `tools/build.py` pomija katalog `.maister` w kontroli prywatności i traktuje rozszerzenia SQLite jako
  pliki binarne; `.gitignore` i hook `pre-commit` blokują pliki SQLite.

## ja [1.4.3] – 2026-10-17

- Mapa Notion (`ja/references/notion-mapa.md`): podstrona „🔑 Asystent – dostęp” pod „🤖 Asystent AI” (dostęp czatu do indeksu
  wiedzy). PATCH – poprawka mapy.

## ja [1.4.2] – 2026-10-17

- `przeglad-dnia`, tryb szybki: zawsze trzy odczyty (Dziennik, „📝 Wpisy”, strony z widgetu); reguła 15 minut
  ocenia każde źródło osobno – świeża strona nie zatrzymuje już całego przebiegu; sam brak kropki to nie urwany wpis;
  odpowiedź podaje nowe wpisy per źródło („Dziennik n · Wpisy n · widget n”).
- `wpisy`: bloki pisane wprost w treści „📝 Wpisy” to nowe wpisy (ślad `(Wpisy)`, po przetworzeniu treść strony pusta);
  mapa Notion `ja` – opis „📝 Wpisy”. PATCH – poprawka treści.

## ja [1.4.0] – 2026-10-17

- Strona ✅ Zadania w zakładkach (📅 Dziś i tydzień z przełączanymi widokami, 🛒 Zakupy, 🏠 Prywatne, 🏗 Budowa, 👪 Dziecko);
  `zadania`, sekcja C i mapa Notion `ja` z ID widoków; `ja`, zasada 10: zakładki zamiast długich stron.
- HZ-7: zakupy do bazy 🛒 Zakupy (nie do TASKS); zadanie tylko przy terminie lub pilne – `zadania`, sekcja „Zakupy”;
  liczniki zakupów w przeglądach dnia i tygodnia; baza w mapie Notion.
- HZ-8: research RES-n robiony wieczorem (`przeglad-dnia`, krok B.6), odpowiedzi „RES-n” i sprzątanie „❓” (`wpisy`); baza 🔎 Research w mapie.
- HZ-9: format pytań w „❓” – osobny checkbox na pytanie, kontekst w „Szczegółach” (`wpisy/references/pytania.md`);
  zaznaczony checkbox liczy się jako odpowiedź.

## ja [1.3.4] – 2026-10-16

- HZ-5: książka, film/serial i pomysł na prezent to nie zadanie – idą do Books, 🎬 Films i na stronę osoby; zadanie tylko
  przy terminie lub decyzji o zakupie (`zadania`); baza 🎬 Films w mapie Notion `ja`.
- HZ-6: tematy do przegadania z dzieckiem i partnerką zawsze na stronę osoby, po świeżym zdarzeniu także zadanie
  z terminem +3 dni (`ja`, zasada 9; odwołanie w `dziecko`).

## ja [1.3.3] – 2026-10-16

- Strona „🤖 Asystent AI” przeniesiona na najwyższy poziom Private (była pod DOM) i trzyma skrzynkę Zmiany do harnessu
  oraz bazę Pomysły na rozwój – dla budowy i spraw osobistych. Lista stałych stron, mapa `ja`, `rozwoj-harnessu`
  i strona „🗺 Mapa Notion” zaktualizowane (ID stron i baz bez zmian).

## dom-budowa [2.3.3] – 2026-10-16

- Na DOM nie ma już Pomysłów na rozwój ani strony Asystent AI – w „🤖 Dla asystenta” jest odnośnik; mapa Notion
  budowy i `zrodla.md` wskazują nowe miejsce.

## ja [1.3.2] – 2026-10-16

- Baza TASKS przeniesiona z DOM na stronę ✅ Zadania (ID i widoki bez zmian) – mapa Notion `ja` zaktualizowana.

## dom-budowa [2.3.2] – 2026-10-16

- Na DOM zamiast bazy TASKS toggle „✅ Zadania budowy” z widokiem „🏗 Zadania budowy – otwarte” (Obszar Dom/puste)
  i odnośnikiem do strony ✅ Zadania; mapa Notion i `zrodla.md` zaktualizowane.

## dom-budowa [2.3.1] – 2026-10-15

- Sekcja „🔴 Do zamknięcia przed …” na DOM to teraz nagłówek rozwijany z widokiem Notatnika „🔴 Blokady – <etap>”
  (Krytyczne + otwarte + bieżący etap i formalności) zamiast ręcznej listy checkboxów. `budowa` (zasada 12), `notatka`,
  `etap` (A.7), `przygotowanie`, `przeglad-tygodnia` (Spójność) i mapa Notion zaktualizowane.

## dom-budowa [2.3.0] – 2026-10-15

- Zakładka 🏗 Etap na DOM przebudowana: wspólne Harmonogram i „Do zamknięcia” u góry, niżej zakładki etapów
  (Całość, Stan zero, SSO, Deweloperski, Wykończenie, Teren i ogród) z przewodnikiem etapu, widokiem Checklisty i otwartych
  spraw Notatnika. Strona „Etapy budowy – przewodnik” to już tylko odnośnik; mapa Notion, `zrodla.md` i `etap` zaktualizowane.

## ja [1.3.1] – 2026-10-15

- `ja`, zasada 8: generowany przewodnik to wyjątek od zmian punktowych (zastępowany w całości); wersja pluginów tylko
  na stronie „Asystent AI – harness” (Mapa Notion odsyła tam). Wejście z widgetu sprawdzone testową stroną.

## ja [1.3.0] – 2026-10-15

- `wpisy`, `przeglad-dnia` (tryb szybki): nowe wejście Dziennika – strony zakładane widgetem „nowa strona” w telefonie
  na najwyższym poziomie Private. Wpis = każda strona spoza listy stałych stron (porównanie po ID; 🔒 Prywatne na liście,
  nigdy nieotwierana); strona z podstronami/bazą albo wyglądająca na nowy obszar → pytanie w „❓”, bez przenoszenia.
  Po przetworzeniu strona idzie pod „🗃 Przetworzone podstrony”; świeża (< 15 min) czeka na następny przebieg, pusta → pominięta.
  „📝 Wpisy” działa dalej.
- Mapa `ja/references/notion-mapa.md`: komplet stałych stron najwyższego poziomu z ID (doszły DASHBOARD, DOM, Dziennik, ID Prywatnych).
- `ja`, zasada 8: harness i Notion mówią to samo – zmiana miejsca lub struktury obejmuje wszystkie opisy w repo i w Notion
  (lista miejsc); rozbieżność Notion z mapą → propozycja aktualizacji, nie ciche dopasowanie. `rozwoj-harnessu` B.7 odsyła do niej.

## dom-budowa [2.2.2] – 2026-10-15

- Mapa Notion budowy: wiersz Dziennika wymienia wszystkie wejścia wpisów (bloki, „📝 Wpisy”, strony z widgetu w Private).

## dom-budowa [2.2.1] – 2026-10-15

- `etap`, plan etapu krok 7: przy zmianie etapu przestawiany jest też widok „🎯 Na teraz – <etap>” w „✅ Checkliście budowy”.

## dom-budowa [2.2.0] – 2026-10-15

- Nowa baza Notion „✅ Checklista budowy” (strona na dole DOM, wzmianka w zakładce 🏗 Etap): punkty kontroli prac
  ze scalonych checklist kursu, z polami Etap, Element, Faza, Zrobione, Uwagi, Dotyczy nas i widokami na etapy.
  Mapa Notion i procedura `etap` (źródła, bramka krok 2 i 8, odbiór krok 2) korzystają z niej przy bramkach i odbiorach.

## ja [1.2.3] – 2026-10-15

- POM-9 (etap 4): mapa Notion – Relacja i Wesele pod Rodziną, Books w Collections, Quick notes w Archiwum, DASHBOARD
  w zakładkach z podstroną „🗺 Mapa Notion” (opis całości i kroki dla inwestora).

## ja [1.2.2] – 2026-10-15

- POM-9 (etapy 1–3): mapa Notion – nowa struktura najwyższego poziomu (Zadania, Rodzina, Zdrowie, Ja, WORK, Wiedza,
  Collections, Archiwum, Prywatne) z ID w `ja/references/notion-mapa.md`; strony przeniesione w całości (ID bez zmian).

## ja [1.2.1] – 2026-10-15

- `ja`, zasada 5: strona „🔒 Prywatne” i jej podstrony poza zasięgiem asystenta (nie czytać, nie przeszukiwać, nie cytować);
  wpis intymny z Dziennika zostaje w „❓” z pytaniem o ręczne przeniesienie; hasła nigdy nie są przepisywane. Mapa: strona
  „💞 Relacja” (obszar w bazie Obszary – konfiguracja), DASHBOARD jako strona startowa.

## dom-budowa [2.1.2] – 2026-10-15

- `budowa`, zasada 11: „🔒 Prywatne” poza zasięgiem także procedur budowy.

## ja [1.2.0] – 2026-10-15

- Nowy skill `przeglad-tygodnia-osobisty`: tydzień spraw osobistych (zadania prywatne/dziecko/praca, emocje i produktywność
  w liczbach, dziecko, wesele, suple) na stronie „📅 Przeglądy tygodniowe” pod Dziennikiem, z linią i odnośnikiem do przeglądu
  budowy (uruchamia `przeglad-tygodnia` z dom-budowa); czyta przez widoki „🤖 …” (limit zapytań) i przeglądy dzienne;
  przejmuje porządki w Dzienniku oraz przypomnienia o skrzynce zmian i pomysłach. Jedno zadanie tygodniowe poza projektem.
- Strona „💍 Wesele” i obszar „Wesele” w bazie Obszary (procedura ogólna – bez zmian w procedurach; tylko mapa).

## dom-budowa [2.1.1] – 2026-10-15

- `przeglad-tygodnia`: tylko budowa – wpisy o budowie czekające w „❓” Dziennika; porządki w Dzienniku, skrzynka zmian
  i pomysły przeniesione do `przeglad-tygodnia-osobisty` (plugin ja); zwraca link do wpisu, gdy wywołuje go przegląd osobisty.

## ja [1.1.0] – 2026-10-15

- `przeglad-dnia`, tryb wieczorny: budowa i sprawy osobiste mają osobne przeglądy – osobisty w nowej stronie „📆 Przeglądy
  dzienne” pod Dziennikiem (codziennie, bez treści emocji), budowa w „📆 Przeglądy dzienne – budowa” na DOM (pisze `budowa`,
  sekcja „Wieczorem”); w osobistym jedna linia „🏗 Budowa” z odnośnikiem do wpisu budowy z tego dnia. Powód: intensywne dni
  na budowie zasłaniały resztę.
- `wpisy`: wpisy pisane jako osobne strony inwestor zakłada w „📝 Wpisy” (podstrona Dziennika) – jej podstrony to nowe wpisy;
  tryb szybki czyta Dziennik i „Wpisy”. Pola „Gdzie” / „Jak zapisać” w bazie Obszary są nadrzędne także dla obszarów
  obsługiwanych przez skille (konfiguracja z Notion bez zmian harnessu).

## dom-budowa [2.1.0] – 2026-10-15

- `budowa`, sekcja „Wieczorem”: zamiast samego odczytu pisze **przegląd dnia budowy** (dziś, decyzje czekające, jutro) do
  „📆 Przeglądy dzienne – budowa” (strona wróciła na DOM) i zwraca link do przeglądu osobistego; ręcznie „przegląd dnia budowy”.

## ja [1.0.0] – 2026-10-15

POM-8: jeden Dziennik w Notion na wszystko + drugi plugin. Repo przemianowane na `sztalinux/notion-plugin` (marketplace
z dwoma pluginami).
- Nowy plugin `ja`: skill kontekstowy `ja` (kontekst osobisty, skrzynka zmian na starcie rozmowy, mapa procedur, zasady,
  `references/notion-mapa.md`), `wpisy` (router strony „📓 Dziennik” – mechanika dawnego `inbox`, obszary z bazy Notion
  „🧭 Obszary Dziennika”, nowy obszar = wiersz w bazie, nie zmiana harnessu; podstrony też są wpisami), `emocje` (Wpisy emocji,
  Dziennik produktywności, podsumowania na prośbę), `zadania` (wspólna TASKS z polem Obszar, zmiana statusu po „zrobiłem X”),
  `dziecko` (strona dziecka w sekcjach), `suple` (Buy / Status / Last break).
- Przeniesione z `dom-budowa`: `przeglad-dnia` – dwa tryby: szybki (co 1–2 h, nowe wpisy na bieżąco, pusty Dziennik = koniec
  bez zapisów, pomija wpisy świeższe niż 15 min) i wieczorny (ostatni przebieg, podsumowanie dnia i plan na jutro ze wszystkich
  obszarów w Przeglądach dziennych codziennie, część budowlana z `budowa` → „Wieczorem”, analiza pomysłów); oba zadania
  poza projektem i `rozwoj-harnessu` (dwa pluginy, wersje per plugin,
  pole Plugin w skrzynce, changelog z nagłówkiem pluginu).
- Odczyt baz: limit Notion obejmuje też tryb rows (wyczerpany 15.10) – procedury czytają przez zapisane widoki (tryb view, bez
  limitu) i wyszukiwarkę z parametrem bazy; Obszary przez widok „🤖 Aktywne (dla asystenta)” (także `budowa`, zasada 6).
- Wpisy-podstrony w Dzienniku po przetworzeniu przenoszone pod „🗃 Przetworzone podstrony” (nie wycinane z treści – to by je
  skasowało); data podstrony bez daty w treści = data jej ostatniej edycji. Sprawdzone na pierwszym przebiegu 15.10.
- HZ-3 `rozwoj-harnessu`, `ja`: wpisy w skrzynce z pustym Statusem (dodane ręcznie) są do wdrożenia – asystent najpierw
  uzupełnia ich pola; puste pola pomysłów uzupełnia przy analizie.
- Instrukcje projektu „Dom” zmienione (skrzynka opisana w `ja`) – wklej na nowo `dist/claude-ai-projekt/instrukcje.md`.

## dom-budowa [2.0.0] – 2026-10-15

POM-8 – zmiana struktury danych:
- `inbox` usunięty (zastąpiony przez `wpisy` w pluginie `ja`); `przeglad-dnia` i `rozwoj-harnessu` przeniesione do `ja`.
- `budowa`: „Na starcie” odsyła do `ja`; nowe sekcje „Luźny wpis z Dziennika” (klasy wpisu, jednoznaczność, źródło,
  duplikaty, tabela klasa → procedura) i „Wieczorem” (część budowlana przeglądu dnia); mapa procedur bez `inbox`.
- TASKS (dawniej „TASKS (2)”) jest wspólna ze sprawami osobistymi: nowe pole Obszar – procedury budowy ustawiają Obszar = Dom,
  puste = stare wiersze budowy; widoki „🏗 ToDo/Doing – Dom” i „⏳ Czekam na” filtrują Dom/puste (`notatka`, `harmonogram`,
  `przeglad-tygodnia`, schematy, mapa Notion).
- Strona DOM bez Inboxu (odnośnik do „📓 Dziennik”); Przeglądy dzienne przeniesione pod Dziennik; `przeglad-tygodnia` liczy
  i czyści wpisy Dziennika zamiast Inboxu.
- Narzędzia: `tools/build.py` dla wielu pluginów (walidacja per plugin, unikalne nazwy skilli, dowiązania `.claude/skills/`
  i `.agents/skills/` na każdy skill, `dist/<plugin>.plugin`); `tools/dokumenty.py` dokłada do przewodnika drugą mapę Notion
  (sprawy osobiste).

## [1.9.5] – 2026-10-14

- HZ-4 `budowa` (zasada 12), `notatka`: kolumny baz roboczych (Notatnik, TASKS) to krótkie właściwości – Notatka i Desc
  mają jedno zdanie; szczegóły, listy (checkboxy), kontekst, uzasadnienie decyzji i dopiski z datą idą do treści strony.
  Pola Bazy wiedzy i Rejestru bez zmian (opisuje je `wiedza`).

## [1.9.4] – 2026-10-14

- `inbox`, `przeglad-dnia`, `przeglad-tygodnia`: „Przetworzone” pogrupowane dzień po dniu w zwijanych blokach (najnowszy
  na górze, tytuł z datą i skrótem linii „🤖”); linia „🤖” i przetworzone wpisy trafiają do bloku dnia, kolejny przebieg
  tego dnia dopisuje się do niego; przegląd tygodnia czyści bloki starsze niż 14 dni. Ostrzeżenie: edycja Inboxu
  nie obejmuje nagłówka „✅ Zadania” (Notion zdejmuje wtedy zwijanie).

## [1.9.3] – 2026-10-14

- HZ-2 `inbox`, `przeglad-dnia`: po przebiegu pierwszy poziom Inboxu jest pusty (gotowy na wpisy następnego dnia) –
  linia „🤖” idzie na górę „Przetworzone”, nie pod „Jak używać”.
- `przeglad-dnia`, nowy krok 5: wpis w „📆 Przeglądy dzienne” (najnowszy pierwszy); ręczny przebieg = osobny wpis z tą samą
  datą i dopiskiem „(ręczne)”, „(ręczne 2)”…, bez nadpisywania wcześniejszych; sprostowanie starszego wpisu = linia
  z odesłaniem. Cel przeglądu: „krótkie podsumowanie” zamiast „jednej linii”. Strona dodana do mapy Notion.

## [1.9.2] – 2026-10-13

- HZ-1 `wiedza`, sekcja A: jedno źródło (ZRD) na lekcję, artykuł, odcinek lub rozmowę, z powiązaniami autora w polu Kto;
  materiały tego samego autora (kurs, blog, podcast, stare notatki z nich) nie liczą się jako potwierdzenia – powtórzenie
  trafia do „Najważniejsze”, nowy szczegół jako uzupełnienie.

## [1.9.1] – 2026-10-13

- `wiedza`, sekcja B: blok „W pigułce” w odpowiedzi po przetworzeniu źródła – 3–8 najważniejszych tez z całego
  materiału (wszystkie etapy, z WI-x), gdy źródło dało ≥ 3 informacje; inwestor wie, co doszło, bez otwierania Notion.

## [1.9.0] – 2026-10-13

- Nowa procedura `przeglad-dnia` (codzienny wieczorny przegląd bez inwestora): Inbox bez pytań w rozmowie (przeniesione
  z „trybu wieczornego” w `inbox`), analiza nowych pomysłów (max 3 na wieczór), „na jutro” (zadania, kroki, dostawy,
  zamówienia), linia „🤖” z licznikami i punktami „jutro”; sekcja „Rozszerzanie” na kolejne codzienne kroki.
- `inbox`: zamiast trybu wieczornego – odesłanie do `przeglad-dnia`. Zaplanowane zadanie na claude.ai: nowe polecenie
  „Przegląd dnia (skill przeglad-dnia)”.

## [1.8.2] – 2026-10-12

- `budowa`, zasada 6: odczyt baz najpierw trybem rows (filtr strukturalny – działa mimo wyczerpanego limitu SQL), potem
  view, SQL tylko do zliczeń/łączeń; rollupy w rows/view to odnośniki – pobieraj strony albo zaznacz brak.

## [1.8.1] – 2026-10-12

- `przeglad-tygodnia`: przypomnienie przed krokiem już po 7 dniach (w tygodniu tuż przed krokiem); pod koniec etapu
  (następny za ≤ 8 tygodni) do „Wiedzy na teraz” wchodzi następny etap, a widok „🎯 Na teraz” obejmuje oba.
- Notion, Baza wiedzy: blok „🗂 Wiedza wg etapu” z zakładką na każdy etap.
- `budowa`, zasada 6: limit zapytań SQL w Notion – czytaj widokami (tryb view), przy limicie przejdź na view.

## [1.8.0] – 2026-10-12

- `wiedza`: Etap informacji = **kiedy wiedza będzie potrzebna** (najwcześniejszy etap decyzji / zamówienia / przewidzenia),
  nie etap tematu; po przetworzeniu źródła podział „Na teraz” (bieżący etap) i „Na później” (liczniki etapów).
- Notion, Informacje: pole „Pokazano”; zakładki „🎯 Na teraz – Stan zero” (bieżący etap + Cała budowa) i „🗂 Wg etapu”.
  Przegląd etapów istniejących informacji: 15 przeniesionych do etapu, w którym trzeba działać.
- `przeglad-tygodnia`: sekcja „Wiedza na teraz” – max 6 informacji, najpierw pod kroki z 14 dni i otwarte decyzje,
  potem niepokazane; „Pokazano” zapobiega powtórkom z tygodnia na tydzień, reszta licznikiem.
- `etap`: przy zmianie etapu przestawienie widoku „🎯 Na teraz”; wiedza etapu wpleciona w plan.

## [1.7.1] – 2026-10-12

- `inbox`: trzy strefy – na wierzchu tylko nowe wpisy, niejasne z pytaniem przenoszone do „❓ Czeka na Twoją odpowiedź”
  (tam odpowiedź pod pytaniem), załatwione do „Przetworzone”; linia „🤖” z ostatniego przebiegu jest zastępowana, nie dopisywana.
  Strona DOM: nowy zwijany nagłówek „❓ Czeka na Twoją odpowiedź” i nowa podpowiedź „Jak używać”.

## [1.7.0] – 2026-10-12

- Notion, Informacje: pola **Istotność** (Kluczowe / Ważne / Ciekawostka) i **Mój komentarz** (pole inwestora); na stronie
  Baza wiedzy zakładki „🆕 Do przejrzenia” (wg Istotności), „⭐ Kluczowe i ważne”, „💬 Z moim komentarzem”.
- `wiedza`: propozycja Istotności przy zapisie (po przejrzeniu decyduje inwestor), Ciekawostki w odpowiedziach tylko
  licznikiem, komentarz inwestora pokazywany przy informacji; sekcja H – sprzeciw/wątpliwość w komentarzu → jedno
  proponowane działanie (pytanie do projektanta, SP, „Nieaktualne”). „Przejrzałem nowe” przyjmuje ocenę i komentarz.
- `przeglad-tygodnia`: nowa wiedza bez ciekawostek, Twoje komentarze z ostatnich 7 dni.

## [1.6.0] – 2026-10-12

- Notion: baza „💡 Pomysły na rozwój” na stronie DOM (rozwijana sekcja nad „Dla asystenta”, widok „💡 Tablica”) –
  pomysły na harness i cały setup (Notion, Excel, zdjęcia, automatyzacje), ID POM-n.
- `rozwoj-harnessu`, sekcja C: zapis pomysłu, analiza (co jest, co trzeba zrobić, ograniczenia i zgody, nakład,
  zależności, decyzje, rekomendacja; niejasne → „Pytania do mnie”), wdrożenie tylko na polecenie „zrób POM-n”.
- `inbox`: „pomysł: …” → baza pomysłów; tryb wieczorny analizuje też nowe pomysły. `przeglad-tygodnia`: licznik pomysłów.
- Claude Code na starcie: jedna linia o pomysłach (nowe do analizy, „Do zrobienia”), bez wdrażania.

## [1.5.1] – 2026-10-12

- `inbox`: wpis = każdy blok pierwszego poziomu pod „📥 Inbox” (akapit lub punkt, także zaczynający się od daty),
  poza „Jak używać” i „Przetworzone”; jeden blok może zawierać kilka spraw.

## [1.5.0] – 2026-10-12

Planowanie i obsługa budowy: harmonogram, „czekam na”, zamówienia, umowy i gwarancje, płatności.
- Nowa procedura `harmonogram`: ułożenie harmonogramu (kroki z numerami etapów jak w Excelu, Kto, zależności, „bez odwrotu”,
  pewność terminu), terminy pochodne (zamówienia z wyprzedzeniem, zadanie bramki, umówienie kierownika/geotechnika,
  pogoda, transza), przesunięcia z przeliczeniem zależnych kroków, „czekam na”, „co mnie czeka”.
- Notion: bazy Harmonogram (widok „📅 Oś czasu”), Zamówienia i dostawy („🛒 Do zamówienia”), Umowy i gwarancje
  („🛡 Gwarancje”); TASKS: pole „Kto”, relacja Harmonogram, widoki „⏳ Czekam na” i „📆 Kalendarz”. Strona DOM:
  Harmonogram i Zamówienia w zakładce Etap, Umowy w zakładce Wykonawcy.
- `zakupy`: lista i dostawy w bazie Zamówienia; `oferta`: po podpisaniu wiersz w Umowach; `etap`: po odbiorze krok
  „Zrobione”, daty gwarancji/rękojmi; `dziennik`: status kroku, przesunięcia → `harmonogram`; `notatka`: TASKS z „Kto”.
- `koszty`: arkusz Płatności (proponowany układ w `references/arkusze.md`, dodaje inwestor) zamiast Wydatków „Planowane”.
- `inbox`: zadania i cudze terminy → `harmonogram`; tryb wieczorny (zaplanowane zadanie bez inwestora: tylko jednoznaczne
  wpisy, decyzje i terminy kroków zostają z pytaniem).
- `przeglad-tygodnia`: harmonogram 14 dni, „bez odwrotu”, czekam na, zamówienia, gwarancje 60 dni.

## [1.4.4] – 2026-10-12

- `inbox`: Notion nie zapisuje daty dopisania punktu – data zdarzenia tylko z wpisu (`@today` albo data tekstem);
  „dziś/wczoraj” bez daty → pytanie z propozycją daty, nie zgadywanie. Podpowiedź w Inboxie na stronie DOM.

## [1.4.3] – 2026-10-12

- Strona DOM uproszczona: Inbox i Zadania u góry; zakładki Etap (checklista „Do zamknięcia” + bramki, plan przepustów,
  etapy budowy), Notatnik, Dziennik, Wiedza, Wykonawcy, Więcej; na dole zwinięta sekcja „🤖 Dla asystenta” (przewodnik,
  harness, ściąga „📐 Dane projektu”). Nazwy sekcji używane w procedurach bez zmian; mapa Notion i `projekt.md` zaktualizowane.

## [1.4.2] – 2026-10-12

- Strona DOM: Inbox i Zadania jako rozwijane nagłówki, reszta w zakładkach (Do zamknięcia, Notatnik, Dziennik, Wiedza,
  Wykonawcy, Projekt ze ściągą, Rzadko) – mapa Notion zaktualizowana.

## [1.4.1] – 2026-10-12

- `inbox`: Inbox to sekcja „📥 Inbox” (toggle, wolny tekst) na stronie DOM, nie baza – inwestor pisze punkt pod punktem;
  pytania asystenta jako punkt „❓ asystent (data)” pod wpisem, odpowiedź pod spodem; załatwione wpisy przenoszone do
  „Przetworzone” (ślad z linkiem), które czyści przegląd tygodnia. Baza Inbox z 1.4.0 usunięta (decyzja inwestora).
- Strona DOM: kolejność Inbox → Zadania → reszta bez zmian; sekcja „📐 Dane projektu” wróciła na poziom główny
  (była zagnieżdżona pod „Asystent AI”); podstrony Stan zero i Plan przepustów w „Strony i materiały”; prototypy układu usunięte.
- `przeglad-tygodnia`, `notion-mapa.md`, `zrodla.md`, README: zgodnie z powyższym.

## [1.4.0] – 2026-10-12

Inbox, spójność przy ręcznych zmianach w Notion, mniej miejsc z tą samą informacją.
- Nowa procedura `inbox` + baza Notion „Inbox” (DOM): luźne wpisy inwestora; asystent przetwarza je na „przerób inbox” –
  wpis niejednoznaczny albo bez źródła wraca z pytaniami (Status „Do wyjaśnienia”, pola Pytania asystenta / Odpowiedź),
  jednoznaczny trafia przez właściwą procedurę do Notatnika / Bazy wiedzy / Dziennika / TASKS / Excela („Trafiło do”).
- `budowa`, zasada 11 (dawna 11 → 12): Notion jest źródłem prawdy i inwestor edytuje go ręcznie – czytaj przed zapisem,
  nie poprawiaj ręcznych zmian bez pytania; ściąga ma jedno źródło: Notion „📐 Dane projektu” (plik w folderze = kopia).
- `przeglad-tygodnia`: liczniki Inboxu (w tym pytania czekające na inwestora) i sekcja „Spójność” – rozjazdy między
  Notatnikiem, Bazą wiedzy, checklistą „Do zamknięcia”, Dziennikiem i TASKS, proponowane w „Porządkach”.
- Notion: strona „Asystent AI – harness budowy” skrócona do ramki z wersją + skrzynka (opis procedur jest w README repo);
  opcja `inbox` w polu Procedura skrzynki; mapa Notion z Inboxem.
- `rozwoj-harnessu`: krok 7 aktualizuje tylko linię „Wersja”.

## [1.3.0] – 2026-10-11

Bez wgrywania plików na claude.ai; kolejność szukania odpowiedzi; wiedza zawsze ze źródłem.
- Przewodnik po dokumentach i mapa Notion na stronie Notion „📑 Przewodnik po dokumentach i Notion” – Claude Code
  aktualizuje ją sam (`tools/dokumenty.py` generuje `.dom/przewodnik-notion.md`, raport mówi, kiedy przepisać stronę;
  `dokumenty.py notion-ok`). Claude Code nie może zapisywać plików w wiedzy projektu na claude.ai, ale Notion claude.ai
  czyta na żywo. Paczka `_Do claude.ai/` – tylko kopia awaryjna. `CLAUDE.md`: synchronizacja na starcie sesji bez pytania.
- `budowa`: przewodnik z Notion raz na rozmowę; nowa zasada 10 – kolejność szukania odpowiedzi: materiały inwestora →
  sprawy nierozstrzygnięte (Notatnik, sprzeczności, rozmowy, dziennik, archiwum) → internet z oznaczeniem `[internet]`,
  źródłem, datą, typem autora i oceną wiarygodności (zasady 10–11 przenumerowane; odwołania w `etap`, `przeglad-tygodnia`).
- `wiedza`: każda informacja ma źródło (Źródła albo Notatnik); sekcja F – ustalenie z Notatnika → Informacja z relacją
  do wpisu; sekcja G – notatki własne i archiwum jako źródło („Notatki własne”); odpowiedź „co wiemy” podaje źródła.
- `notatka`: ustalenie z wiedzą techniczną → od razu także Informacja w Bazie wiedzy (krok 6).
- Notion: Informacje ↔ Notatnik (relacja „Notatnik” / „Wiedza”), Forma „Notatki własne” w Rozmowach i źródłach.
- **Instrukcje projektu zmienione – wklej ponownie** (`dist/claude-ai-projekt/instrukcje.md`); wiedza projektu może być pusta.

## [1.2.0] – 2026-10-11

- Nowa procedura `przygotowanie`: karta przygotowania do spotkania, rozmowy lub decyzji (cel, 3 najważniejsze rzeczy,
  co wiemy u nas, pytania z „dobrą odpowiedzią” i czerwonymi flagami, macierz decyzji przy wyborze, co zabrać,
  czego nie obiecywać, słowniczek, zapis po spotkaniu); `references/sytuacje.md` – kierownik budowy, wybór wykonawcy
  z finalistów (rozmowa finałowa, referencje), konstruktor/architekt, węzeł betoniarski, hurtownia, odbiór, urząd.
  „Kogo wybrać” przechodzi z `oferta` do `przygotowanie` (liczby nadal z `oferta`).
- Nowy `budowa/references/notion-mapa.md`: struktura Notion z perspektywy „czego szukasz” (strony, bazy, widoki, pola,
  słowniki); `tools/dokumenty.py` dołącza ją do przewodnika `00_SPIS.md`, więc jest w kontekście każdej rozmowy
  w projekcie „Dom”. `rozwoj-harnessu`: zmiana struktury Notion = aktualizacja mapy.
- Instrukcje projektu bez zmian (nie trzeba wklejać ponownie); `00_SPIS.md` – wgraj nową wersję.

## [1.1.0] – 2026-10-11

Lekki projekt „Dom” na claude.ai: przewodnik po dokumentach zamiast pełnych dokumentów w kontekście każdej rozmowy.
- `tools/dokumenty.py`: nowe pole `--zawartosc` (na jakie pytania odpowiada dokument, gdzie szukać); `00_SPIS.md` to teraz
  **przewodnik po dokumentach** – każdy dokument z opisem zawartości lub eksportem, z informacją, czy jest w wiedzy projektu,
  czy tylko na komputerze; przepisywany tylko przy zmianie treści (wcześniej codziennie lądował na liście „podmień”);
  raport startowy liczy dokumenty bez opisu zawartości.
- `dokumenty`: paczka = przewodnik + ściąga; pełne dokumenty i Excel tylko na wyraźną prośbę inwestora (decyzja inwestora);
  nowa sekcja „Prośba o dokument” – gdy brakuje treści, asystent jawnie prosi o konkretny plik (nazwa, ścieżka,
  strona/arkusz, po co) i nie odpowiada z pamięci; w Claude Code czyta plik z folderu.
- `budowa` (zasada 7), `projekt.md`, `zrodla.md`, `koszty`: to samo zachowanie; Excel na claude.ai zawsze załączany aktualny.
- `claude-ai-projekt.md`: instrukcje projektu skrócone do odnośników (zasady są w skillach, więc rzadko trzeba je wklejać
  ponownie). **Wklej instrukcje na nowo** (`dist/claude-ai-projekt/instrukcje.md`). Aktualizacja pluginu: opcja
  odświeżenia marketplace'u, jeśli jest; inaczej usuń i dodaj marketplace ponownie (opcji „Check for updates” może nie być).
- `marketplace.json`: opis pluginu zgodny z `plugin.json` (claude.ai pokazywał stary opis).

## [1.0.3] – 2026-10-10

- `rozwoj-harnessu/references/claude-ai-projekt.md`: sekcja „Wiedza projektu a kontekst” tylko opisuje działanie
  (kontekst / RAG, wskaźnik pojemności) – o zawartości paczki decyduje wyłącznie `dokumenty` (usunięta sprzeczna reguła z 1.0.2).
  Tekst instrukcji projektu bez zmian.

## [1.0.2] – 2026-10-10

claude.ai na co dzień: instrukcje projektu zamiast `START.md`, ręczna aktualizacja pluginu.
- Nowy `rozwoj-harnessu/references/claude-ai-projekt.md`: tekst instrukcji projektu „Dom” (przy każdej wiadomości skill
  `budowa` → procedura, raz na rozmowę skrzynka „Zmiany do harnessu”, dane z Notion i wiedzy projektu, bez „/”;
  gdy skille są niedostępne – powiedz to i nie zgaduj procedur), aktualizacja pluginu przez „Check for updates”,
  wiedza projektu a kontekst. **Wklej instrukcje na nowo** (`dist/claude-ai-projekt/instrukcje.md`), usuń `START.md`.
- `tools/build.py`: generuje `dist/claude-ai-projekt/instrukcje.md` z numerem wersji.
- `rozwoj-harnessu`: po wdrożeniu przypomnienie o „Check for updates” (i o ponownym wklejeniu instrukcji, gdy się zmieniły).
- README, `dostawcy.md`, `zrodla.md`: aktualizacja pluginu nie jest automatyczna (organizacja może blokować synchronizację);
  hooki pluginu działają w Cowork i Claude Code, nie w czacie; `/` tylko do wymuszenia procedury.

## [1.0.1] – 2026-10-10

Poprawki po testach na sucho procedur 1.0.0.
- `etap`: sprawy etapu obejmują też wpisy Typ „Pamiętać” niezależnie od Statusu („Ustalone”); bramka sprawdza poprzednie bramki
  i pogodę na dzień kroku.
- `dziennik`: data względna → data, sprawdzenie duplikatu wpisu z tego dnia, zasada pola „Przed zakryciem OK”.
- `zakupy`: bez pliku Excela – prośba o plik i lista tego, co zostanie policzone.
- `oferta`: „Sam czy ekipa” – przeliczenie brutto → netto i format wyniku (tabela ekipa vs sam, różnica w zł i dniach).
- `wiedza`: tryb odczytu pokazuje Status decyzji i zgłasza nakładające się tematy.
- `analiza-techniczna`: praca własna – ilości na jednostkę przy braku wymiarów, kontrole z `etap/references/odbiory.md`.

## [1.0.0] – 2026-10-10

Pierwsza stabilna wersja – baza do dalszego rozwoju. Harness obejmuje teraz także fazę wykonywania budowy (budowa mieszana: część prac sam, część ekipy).
- Nowa procedura `etap`: plan etapu (zależności sam/ekipa, blokady, ludzie, pogoda), bramki „bez odwrotu” z listą
  zdjęć przed zakryciem, odbiór z protokołem i płatnością dopiero po odbiorze; `references/odbiory.md` (co sprawdzać
  krok po kroku), `references/formalnosci.md` (urzędy, dziennik, kierownik, kto musi być obecny).
- Nowa procedura `dziennik`: wpis z dnia na budowie (kto, co, pogoda, dostawy, godziny własne, problemy, zdjęcia),
  roboty dodatkowe tylko na piśmie przed wykonaniem; schemat bazy Notion „Dziennik budowy” (`references/notion-dziennik.md`).
- Nowa procedura `zakupy`: lista zakupów na etap z kosztorysu + drobnica + zapas, zapytania i porównanie ofert hurtowni,
  terminy zamówień; `references/wyprzedzenia.md` (wyprzedzenia, czasy technologiczne, okna pogodowe).
- `oferta`: sekcje „Sam czy ekipa” i „Po wyborze – zakres do umowy”; `references/umowa.md` – lista kontrolna umowy z wykonawcą.
- `koszty`: sekcja D „Płatności, transze, kredyt” (transza tylko po protokole odbioru, roboty dodatkowe osobno).
- `analiza-techniczna`: tryb „Praca własna – jak to zrobić” (materiały, narzędzia, kroki z kontrolą, błędy, BHP).
- `budowa`: zasada 3 – 8% VAT obejmuje usługę z materiałem, porównania brutto do brutto; opis inwestora (Sam/Ekipa z Excela).
- `notatka`: „Pamiętać” ze Statusem „Ustalone” (nie zaśmieca „otwartych”), wraca w checkliście etapu.
- `przeglad-tygodnia`: poprawiona numeracja źródeł; sekcje „Budowa w tym tygodniu” i „Zamówić / zapłacić do 14 dni”.
- `rozwoj-harnessu`: po wdrożeniu aktualizacja strony przewodnika w Notion (wersja, tabela procedur).
- `dokumenty` / `tools/dokumenty.py`: foldery `Zdjęcia*` pomijane (zdjęcia nie trafiają do indeksu ani paczki).
- `wiedza`: tryb odczytu „co wiemy o…” (stan wiedzy, co obowiązuje u nas, otwarte sprzeczności, luki).
- `notatka`: przy duplikacie nie powstaje drugi wpis ani link – zostaje jedno źródło prawdy; nowe źródło dopisuje się do pola Źródło.
- `CLAUDE.md`, `rozwoj-harnessu`: jedna sesja Claude Code w repo naraz; commit tylko własnych plików.
- Notion: baza „Dziennik budowy”, opcje `etap`/`dziennik`/`zakupy` w skrzynce, pulpit DOM i strona przewodnika zaktualizowane.
- README: tabela procedur.

## [0.4.5] – 2026-10-10

- Zasada prywatności doprecyzowana (decyzja inwestora): imię i nazwisko inwestora w historii gita dozwolone;
  dane innych osób i e-maile – nigdy. Audyt całej historii publicznego repo (wszystkie obiekty): czysto.
- `CLAUDE.md`: nie przepisuj opublikowanej historii (force push zostawia stare commity po SHA), chyba że wyciekły
  dane – wtedy zatrzymaj się i zapytaj inwestora.

## [0.4.4] – 2026-10-09

- `dokumenty` / `tools/dokumenty.py`: dane osobowe w paczce dla claude.ai są dozwolone (paczka trafia tylko do prywatnego
  projektu – decyzja inwestora); kontrola PESEL/konta/kontaktów tylko informuje, raz na wersję pliku.
  Repo publiczne – bez zmian: hooki blokują dane osobowe.

## [0.4.3] – 2026-10-09

Pełna kontrola prywatności przed GitHubem (prośba inwestora).
- `.githooks/pre-commit`: oprócz plików sprawdza autora i commitera (imię z listy zakazanych, e-mail inny niż noreply).
- `.githooks/commit-msg`: wiadomość commita bez danych osobowych/projektowych.
- `.githooks/pre-push`: ostatnia kontrola każdego wysyłanego commita – metadane, wiadomość, treść zmienionych plików,
  także commitów zrobionych z `--no-verify`. Logika w `tools/build.py` (`--tozsamosc`, `--wiadomosc`, `--commity`).
- `rozwoj-harnessu`, `CLAUDE.md`, README: hooki i anonimowy autor commitów.

## [0.4.2] – 2026-10-09

- `tools/dokumenty.py`: kontrola danych wrażliwych nie przepuszcza plików, gdy brak `pypdf`/`openpyxl`
  (blokada „nie sprawdzono”, bez zapamiętania wyniku); `dokumenty`: skany oceniaj samodzielnie (skrypt czyta tylko tekst).

## [0.4.1] – 2026-10-09

Porządek w Notion przy rosnącym projekcie (prośba inwestora z Claude Code).
- `budowa`, zasada 10: na pierwszym planie bieżący etap (sekcja „Do zamknięcia przed …” na stronie DOM), sprawy
  krytyczne, terminy 14 dni i decyzje; zamknięte i odległe – drugi plan (licznik). Każdy wpis z Etapem i Priorytetem,
  aktualizacja zamiast dublowania, porządek statusami (bez usuwania), przestawienie strony DOM przy zmianie etapu.
- `przeglad-tygodnia`: nowa sekcja „Porządki” (duplikaty, braki pól, sprawy bez ruchu, stara „Nowa” wiedza,
  sprawy zakończonego etapu) – propozycje do zatwierdzenia jednym „tak”; wynik z „Na później” i „Porządki”.

## [0.4.0] – 2026-10-09

Folder budowy jako centrum dokumentów + repo publiczne bez danych osobowych
(scalone z wersją 0.4.0 przygotowaną na claude.ai).
- Nowe publiczne repo `sztalinux/dom` z czystą historią (claude.ai dodaje publiczny marketplace bez konektora GitHub).
- Nowa procedura `dokumenty`: pliki od projektantów i wykonawców trafiają do folderu budowy na komputerze;
  agent je klasyfikuje (kategoria, wersja, czy przydatne agentom), a `tools/dokumenty.py` buduje paczkę
  `_Do claude.ai/` z aktualnymi wersjami i spisem `00_SPIS.md` – do wgrania w wiedzy projektu „Dom” na claude.ai.
- Hook SessionStart w `.claude/settings.json`: przy każdym starcie Claude Code skan folderu budowy, przebudowa
  paczki i raport (nowe pliki, zmiany, co wgrać). Skrypt blokuje w paczce pliki z PESEL, numerem konta
  i kontaktami w arkuszach oraz pliki powyżej limitu claude.ai.
- Repo publiczne: usunięte dane osobowe (imię inwestora → „inwestor”, lokalizacja, numery działek, zespół);
  ściąga projektu przeniesiona do folderu budowy i paczki, `budowa/references/projekt.md` to teraz odnośnik
  (Notion / folder budowy / projekt na claude.ai); przykłady w `etapy`, `wiedza`, `notatka` uogólnione.
- `tools/build.py`: kontrola prywatności we wszystkich plikach tekstowych (telefon, e-mail, działka, kod pocztowy,
  adres, PESEL, pliki dokumentów w repo) + lista słów zakazanych poza repo (`.dom/zakazane-w-repo.txt` w folderze budowy).
- Hook `.githooks/pre-commit` blokuje commit z danymi (`git config core.hooksPath .githooks`).
- Zasada 9 w `budowa`, `AGENTS.md`, `CLAUDE.md`, `pisanie-procedur.md`: harness publiczny, przykłady na zmyślonych danych;
  `rozwoj-harnessu`: dane z wpisów skrzynki uogólniaj („Firma A”), konkret zostaje w Notion.
- `koszty`, `zrodla.md`, `dostawcy.md`, README: Excel i dokumenty w folderze budowy zamiast `dane/` w repo;
  nazwa repo `sztalinux/dom`.
- `.claude/settings.local.json` (lokalnie): wyłączona synchronizacja pluginów z claude.ai w folderze repo.

## [0.3.0] – 2026-10-09

Repo jako marketplace + skrzynka zmian w Notion.
- Repo = prywatny marketplace (`.claude-plugin/marketplace.json`), plugin w `plugins/dom-budowa/`. claude.ai (czat, telefon,
  Cowork) pobiera go z GitHuba z automatyczną synchronizacją – bez ręcznego wgrywania.
- Skrzynka „Zmiany do harnessu” w Notion: zgłoszenia z dowolnego miejsca obowiązują od razu (`budowa`, „Na starcie”),
  Claude Code wdraża je do repo na starcie każdej sesji (`CLAUDE.md`, `rozwoj-harnessu` sekcja B) i robi push.
- `.claude/settings.json`: zezwolenia na git i build; plugin z konta wyłączony w folderze repo (bez dublowania skilli).
- `koszty`: w Claude Code Excel z lokalnego katalogu poza gitem, w czacie – plik załączony.
- `przeglad-tygodnia`: przypomina o zmianach czekających na wdrożenie.

## [0.2.0] – 2026-10-09

Wiedza z filmów + Excel jako źródło prawdy.
- Nowa procedura `wiedza`: transkrypcje filmów/artykułów → Notion (Źródła, Baza wiedzy, strony tematyczne);
  klasyfikacja nowe / potwierdzenie / uzupełnienie / sprzeczność; ocena wiarygodności i konfliktu interesów;
  „Dotyczy nas” z przekazaniem działań do Notatnika; Rejestr sprzeczności jak ADR – rozstrzyga tylko inwestor.
- Nowa procedura `przeglad-tygodnia` (+ zaplanowane zadanie w poniedziałki).
- `budowa`, zasada 6: zapisy do Notion wsadowo (jak najmniej zatwierdzeń), ale nigdy kosztem jakości.
- `koszty` i `oferta`: rezygnacja z generatora i plików JSON – Excel prowadzi inwestor, asystent pracuje na
  załączonym pliku i zmienia go tylko na prośbę. Usunięto `koszty/scripts/generuj.py` i schematy JSON.
- Notion: istniejąca Baza wiedzy (Tematy + Rozmowy i źródła) rozszerzona o bazy Informacje i Rejestr sprzeczności;
  Rozmowy i źródła dostały pola Link, Typ autora, Konflikt interesów, Wiarygodność, ID (ZRD); rollupy liczą potwierdzenia i datę informacji.
- `wiedza` obsługuje też relacje z rozmów („dzwoniłem do konstruktora…”) – jeden przepływ dla filmów i rozmów.

## [0.1.0] – 2026-10-09

Pierwszy szkielet harnessu.
- Procedury: `budowa` (kontekst, zasady, mapa), `oferta`, `koszty`, `notatka`, `analiza-techniczna`, `rozwoj-harnessu`.
- Adaptery: plugin Claude, `CLAUDE.md`, `GEMINI.md`, `gemini-extension.json`, `.agents/skills`, `.claude/skills`.
- `tools/build.py`: walidacja (nazwy, opisy, wersje, odwołania, brak telefonów) + paczki `dist/`.
- `koszty/scripts/generuj.py`: generowanie Excela z JSON + przeliczenie + kontrola błędów formuł.
- Zasady pracy przeniesione z dokumentu „jak-pracujemy-z-plikami” (projekt Claude „Dom”).

## Do zrobienia

- [ ] Po ~10 filmach: przegląd jakości ekstrakcji (czy nic ważnego nie ginie, czy nie ma duplikatów) i korekta procedury `wiedza`.
- [ ] Pierwszy przegląd tygodnia uruchomiony z claude.ai (zadanie zaplanowane) – sprawdzić format i czas.
