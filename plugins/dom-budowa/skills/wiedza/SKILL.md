---
name: wiedza
description: Zapis wiedzy do Notion (Baza wiedzy – Tematy, Informacje, Rozmowy i źródła) z transkrypcji filmów YouTube, podcastów, artykułów ekspertów oraz z rozmów z konstruktorem, architektem, wykonawcami; wykrywanie sprzeczności (Rejestr sprzeczności) i ich rozstrzyganie po decyzji inwestora. Używaj, gdy użytkownik wkleja transkrypcję, napisy, link do filmu, notatki z filmu/artykułu, mówi „przerób ten film”, „wrzuć do wiedzy”, „dzwoniłem do konstruktora, powiedział…”, albo odpowiada na sprzeczność („SP-3: …”), albo pyta „co wiemy o…”, „co mówi baza wiedzy o…”, „jakie mamy sprzeczności w temacie…”.
---

# Wiedza – filmy, artykuły, rozmowy

Cel: z każdego źródła wyciągnąć **wszystko, co istotne, i nic poza tym**, przypiąć do właściwych tematów,
oznaczyć co nowe, co potwierdzone, a co sprzeczne – i niczego spornego nie rozstrzygać bez inwestora.

Struktura Notion, ID baz, pola i plan zapisu: `references/notion-wiedza.md`.
Ocena źródła: `references/ocena-zrodla.md`. Sprzeczności (ADR): `references/sprzecznosci.md`.
Szukanie w bazie (indeks lokalny, trzy kanały dostępu): `references/indeks.md`; pytanie do bazy: `references/pytanie-do-bazy.md`;
porównanie nowego źródła z bazą: `references/porownanie.md`. Zapisy wsadowe: `budowa`, zasada 6.
Porządki (scalanie duplikatów, zły temat, sprzeczności z przeglądu bazy): `references/porzadki.md` – nigdy nie usuwaj stron.

**Każda informacja ma źródło** – relację Źródła (wpis w Rozmowach i źródłach: film, rozmowa, dokument, notatki własne)
albo relację Notatnik (ustalenie lub decyzja naszej budowy, sekcja F). Informacji bez źródła nie zapisuj. Źródło nieznane
(np. stara notatka bez autora) → wpis „Notatki własne” z Wiarygodnością co najwyżej „3 – średnia” i Konfliktem „?”, a
w odpowiedzi zaznacz, że wymaga potwierdzenia. Dzięki temu przy każdej informacji widać, skąd jest i ile jest warta.

**Istotność i komentarz inwestora** – żeby przy dużej liczbie kursów i podcastów nie utonąć w informacjach:
- **Istotność:** **Kluczowe** = wpływa na decyzję, zamówienie, wykonanie lub odbiór u nas (błąd = koszt albo rzecz nie do
  cofnięcia); **Ważne** = dotyczy nas, warto pamiętać lub sprawdzić, ale nic nie blokuje; **Ciekawostka** = kontekst, inne
  warunki niż u nas, „dobrze wiedzieć”. Przy zapisie ustaw **propozycję** (Status „Nowe”); po przejrzeniu („Przejrzane”)
  to ocena inwestora – nie zmieniaj jej bez jego prośby. W razie wątpliwości wybierz niższą – Kluczowe ma zostać krótką listą.
- **Mój komentarz:** pole inwestora (zgadzam się / nie zgadzam, bo… / sprawdzić u…). Nigdy go nie nadpisuj ani nie
  skracaj; czytaj przy każdej odpowiedzi o tej informacji (sekcja E) i reaguj wg sekcji H.

## A. Nowe źródło

1. **Metadane:** film/artykuł – tytuł, autor/kanał, link, data publikacji (z linku spróbuj odczytać tytuł i datę);
   rozmowa – z kim, forma, data. Czego nie da się ustalić – wpisz „?” i dopisz do „Do uzupełnienia” w odpowiedzi
   (nie blokuj pracy). Sprawdź w Rozmowach i źródłach, czy to źródło już było – jeśli tak, zapytaj, czy przetworzyć ponownie.
   **Jedno źródło = jedna lekcja, artykuł, odcinek albo rozmowa** – kilka wklejonych naraz to kilka wpisów ZRD. W polu Kto
   zapisz autora i jego powiązania (np. współautor kursu ZRD-x), żeby było widać, które źródła nie są od siebie niezależne.
2. **Ocena źródła** wg `references/ocena-zrodla.md`: typ autora, konflikt interesów, wiarygodność 1–5.
   Nasz konstruktor/architekt = „Nasz projektant / wykonawca” – jego ustalenia dotyczą naszej budowy wprost.
3. **Ekstrakcja** – przeczytaj całość (długą transkrypcję w częściach, nic nie pomijaj w czytaniu):
   - jedna jednostka = jedna informacja zrozumiała bez filmu (co, warunek, liczba, dlaczego),
   - **zachowaj zawsze:** liczby z jednostkami, warunki i wyjątki („przy gruncie spoistym…”), nazwy systemów
     i produktów, kolejność prac, ostrzeżenia, uzasadnienia, koszty z datą,
   - **pomijaj:** wstępy, reklamy, anegdoty, powtórzenia, prośby o subskrypcję, dygresje bez treści,
   - popraw oczywiste błędy automatycznej transkrypcji w terminach (np. „ka em be” → KMB); niepewne oznacz `[niepewne w transkrypcji]`,
   - zachowaj znacznik czasu w polu Fragment, np. `12:40 – „…”` (cytat ≤ 20 słów).
   **Kontrola kompletności:** wypisz dla siebie wszystkie liczby, produkty i ostrzeżenia ze źródła i sprawdź, czy każde
   trafiło do jakiejś jednostki albo zostało świadomie pominięte (w odpowiedzi podaj, co pominięto i dlaczego).
4. **Tematy:** każdą jednostkę przypnij do 1–2 tematów z bazy Tematy (najpierw istniejące; nowy temat tylko gdy nic nie pasuje)
   oraz nadaj Branżę i Etap. Film o jednym temacie, który zahacza o inne – każda informacja idzie do swojego tematu.
   **Etap = kiedy ta wiedza będzie potrzebna**, czyli najwcześniejszy etap, w którym trzeba coś zdecydować, zamówić,
   przewidzieć albo sprawdzić – nie etap, którego dotyczy temat. Np. pion ciepłej wody → Stan zero (otwór w stropie P-1),
   odpływ skroplin klimatyzacji → Stan zero (kanalizacja podposadzkowa), membrana dachowa → SSO, gładzie → Deweloperski.
   „Cała budowa” tylko dla zasad bez konkretnego momentu (organizacja, budżet, umowy).
5. **Porównanie z całym tematem – przed zapisem.** Najpierw skończ ekstrakcję (pkt 3–4), nadaj jednostkom numery
   T-1, T-2… i dopiero potem porównuj – temat po temacie, każdą jednostkę z całym tematem i z trafieniami z innych
   tematów; przed pierwszym zapisem spisz listę relacji T-n → WI-x. Jak: `references/porownanie.md`. Przeszukaj też:
   „W skrócie” tematów, Rejestr sprzeczności (także rozstrzygnięte), decyzje w Notatniku budowy (wszystkie wpisy z tym
   samym Etapem i Branżą – filtr bazy, nie szukanie tekstu), ściągę projektu (`budowa/references/projekt.md`). Informacje sprawdzaj poleceniem `szukaj` z tezą jednostki: 2–4 słowa kluczowe, bez zdania
   i słów pomocniczych (końcówki fleksyjne obcina narzędzie; `*` = prefiks, np. `drena*`), nie przeglądaniem bazy; wynik niesie
   „Kto” do reguły „ten sam autor” (niżej). Polecenie i kanał: `references/indeks.md` (przebieg nocny – bezwzględna ścieżka z promptu). Sklasyfikuj:
   | Wynik | Działanie |
   |---|---|
   | NOWE | nowy wiersz, Status „Nowe” |
   | POTWIERDZENIE (to samo twierdzenie) | bez nowego wiersza – podepnij istniejący wiersz pod nowe źródło (Potwierdzenia liczą się same) |
   | UZUPEŁNIENIE (nowy szczegół) | nowy wiersz „Nowe” z dopiskiem „uzupełnia WI-x” |
   | SPRZECZNOŚĆ | nowy wiersz ze Statusem „Sporne” + wpis w Rejestrze („Czeka na decyzję”) |
   | ZGODNE / SPRZECZNE Z ROZSTRZYGNIĘCIEM | nie otwieraj sporu ponownie, chyba że źródło wnosi nowy argument – wtedy nowy SP z odwołaniem do starego |
   Różne zalecenia dla **różnych warunków** (inny grunt, inna technologia) to nie sprzeczność – zapisz warunek w treści.
   **Ten sam autor to nie potwierdzenie:** gdy istniejący wiersz pochodzi tylko od tego samego autora lub z tego samego
   kursu/bloga/podcastu (także ze starych notatek z niego), nie podpinaj go pod nowe źródło – Potwierdzenia liczą niezależne
   źródła. Powtórzenie wpisz w „Najważniejsze” nowego źródła („powtarza WI-x”), nowy szczegół – jako UZUPEŁNIENIE.
6. **Dla naszej budowy:** oceń „Dotyczy nas” i w 1–2 zdaniach napisz, co to znaczy u nas (parametry budynku, gruntu i instalacji:
   `budowa/references/projekt.md`); ustaw propozycję **Istotności** (wyżej – „Dotyczy nas = Nie” to zwykle Ciekawostka). Wymaga działania (pytanie do konstruktora, ryzyko,
   rzecz do pilnowania na budowie) → wpis w Notatniku budowy (procedura `notatka`, Źródło = „ZRD-x <tytuł>, <minuta>”).
7. **Zapis do Notion** – kolejność i grupowanie wg „Plan zapisu” w `references/notion-wiedza.md` (zwykle 4–6 zatwierdzeń).
   Wiedza bez konfliktu zapisuje się od razu. Po zapisie: w sesji interaktywnej Claude Code w repo uruchom
   `python3 tools/wiedza.py sync --publikuj`; w przebiegu nocnym pomiń (sync robi skrypt); w czacie pomiń i napisz to wprost.
8. **Tematy – podsumowanie:** aktualizuj „W skrócie” i treść strony tematu tylko gdy temat dostał ≥ 3 nowe informacje,
   rozstrzygnięcie albo informacja zmienia „co obowiązuje dziś”. Pozostałe są widoczne w relacji Informacje tematu.

## B. Odpowiedź po przetworzeniu

```
**ZRD-x „<tytuł>”** – <autor>, <data> | wiarygodność <n>/5 | konflikt interesów: <…>
Zapisano: <n> nowych (<k> kluczowych, <w> ważnych, <c> ciekawostek), <n> potwierdzeń, <n> uzupełnień → tematy: <lista>
W pigułce: • <teza> (WI-x) • … (najważniejsze tezy całego źródła, ze wszystkich etapów – zasady niżej)
Na teraz (<bieżący etap>): • … • … (3–5 punktów z Kluczowych i Ważnych bieżącego etapu, z WI-x)
Na później: SSO <n> · Deweloperski <n> · Wykończenie <n> · … – wrócą w przeglądzie, gdy przyjdzie ich etap
⚠️ Sprzeczności – czekają na Twoją odpowiedź:
  SP-n <dylemat>: A) <stanowisko + źródło> vs B) <stanowisko + źródło>. Rekomenduję <…>, bo <…>.
  ❓ <pytanie> – odpowiedz np. „SP-n: B” albo „SP-n: zapytam konstruktora”.
Do Notatnika: <wpisy> | Pominięto: <co i dlaczego> | Do uzupełnienia: <np. data publikacji>
```

**W pigułce** – żeby inwestor w kilku zdaniach wiedział, co doszło do bazy, bez otwierania Notion: gdy źródło dało
≥ 3 nowe informacje lub uzupełnienia, wypisz 3–8 najważniejszych tez z całego źródła (nie tylko bieżącego etapu),
każda jednym zdaniem z liczbą lub warunkiem i numerem WI-x; najpierw Kluczowe, potem Ważne, Ciekawostki tylko gdy
niosą główną myśl materiału. Mniej niż 3 informacje – pomiń blok (wszystko jest w „Zapisano” i „Na teraz”).

## C. Rozstrzygnięcie sprzeczności (po odpowiedzi inwestora)

Tylko po wyraźnej odpowiedzi; niejasna → dopytaj, nie zgaduj. Kroki: `references/sprzecznosci.md`.

## D. „Przejrzałem nowe”

Zmień Status „Nowe” → „Przejrzane” dla wskazanych wierszy (albo wszystkich z danego źródła/tematu). Gdy inwestor przy tym
podaje ocenę albo uwagę („WI-12 ciekawostka”, „do WI-20: nie zgadzam się, bo…”) – zapisz Istotność i **Mój komentarz**
(dosłownie, jego słowami) w tym samym przebiegu, potem sekcja H. Bez oceny – propozycja asystenta zostaje.

## E. Pytanie do bazy („co wiemy o drenażu?”)

1. Szukaj i odpowiadaj wg `references/pytanie-do-bazy.md`: kilka sformułowań naraz, poziom głębokości (szybko / normalnie /
   dokładnie / cały etap – `etap --czesc k`), cały główny temat, Notatnik po polach, stała forma odpowiedzi z zasięgiem. Polecenia i kanały:
   `references/indeks.md`. Notion czytaj po szczegóły, przed decyzją i przed zapisem. Stan indeksu starszy niż 24 h – podaj
   jego datę w odpowiedzi. Indeks niedostępny → dotychczasowa droga: znajdź temat(y) w Tematach (nazwa i „W skrócie”);
   pobierz ich Informacje (Status ≠ Nieaktualne) i wpisy Rejestru (Status ≠ Zastąpione) – jednym zapytaniem na bazę.
   Gdy dwa tematy pokrywają ten sam zakres, nie łącz ich wiedzy po cichu – zgłoś to inwestorowi jako sprawę porządkową.
2. Kolejność w obrębie stanu wiedzy: Kluczowe → Ważne → nieocenione; Ciekawostki tylko jako licznik („+ n ciekawostek –
   pokazać?”), chyba że pytanie dotyczy właśnie ich. Przy informacji z **Moim komentarzem** podaj go obok („Twoja uwaga: …”);
   komentarz sprzeciwu oznacz – to nie jest wiedza „obowiązująca u nas”, dopóki sprawa nie jest rozstrzygnięta. Kolejność
   odpowiedzi (u nas ustalone → stan wiedzy z WI-x, liczby z warunkami, przy rozbieżnych warunkach oba → otwarte SP → luki),
   internet `[internet]` i tryb doradcy: `pytanie-do-bazy.md`, pkt 7–9.
3. Nie dopisuj wiedzy z własnej pamięci do odpowiedzi jako „z bazy”. Własne uzupełnienie oznacz `[opinia]` i zaproponuj
   zapis dopiero po potwierdzeniu źródłem.
4. Nic nie zapisuj (tryb tylko do odczytu), chyba że inwestor poprosi o zanotowanie luki jako „Doczytać” (`notatka`).
5. Przy każdej informacji podaj jej źródło (ZRD-x z typem autora i wiarygodnością albo „ustalenie w Notatniku”).

## F. Ustalenie z Notatnika → wiedza

Gdy wpis w Notatniku budowy ma Status „Ustalone” lub „Zrobione” i niesie wiedzę techniczną o naszej budowie
(Typ „Decyzja”, „Pamiętać” z parametrem, zasadą wykonania, materiałem, kolejnością prac; zamknięte „Pytanie” z odpowiedzią):

1. Sprawdź, czy taka informacja już jest (Informacje: Tematy + słowa kluczowe) – jest → podepnij Notatnik i ewentualnie
   zaktualizuj „Dla naszej budowy”, bez nowego wiersza.
2. Nowa → wiersz w Informacjach: samodzielne zdanie (co obowiązuje u nas), Dotyczy nas „Tak”, Istotność (zwykle Kluczowe
   albo Ważne), „Dla naszej budowy”,
   Tematy, Branża, Etap, Status „Przejrzane” (ustalił inwestor), relacja **Notatnik** = ten wpis; Źródła = rozmowa
   z Rozmów i źródeł, z której ustalenie wynika (jeśli jest – pole Źródło w Notatniku).
3. Ustalenie zmienia „co obowiązuje dziś” w temacie → zaktualizuj „W skrócie” tematu. Sprzeczne z dotychczasową wiedzą →
   procedura sprzeczności (sekcja A, krok 5), nie nadpisuj po cichu.
4. Sprawy organizacyjne bez wiedzy technicznej (kto, kiedy, zamówić) zostają tylko w Notatniku.

## G. Notatki własne i archiwum

Stare notatki inwestora (np. Notion → Archiwum – stare notatki) przetwarzaj jak źródło (sekcja A): jedna podstrona = jeden
wpis w Rozmowach i źródłach (Forma „Notatki własne”, Z kim wg pochodzenia – kurs/internet/rozmowa, jeśli wiadomo,
Typ autora „Inny”, Wiarygodność „3 – średnia” lub niżej, Konflikt „?”). Informacje Status „Nowe” – inwestor je przejrzy.
Rzeczy nieaktualne (wybór działki, wybór projektanta) pomiń; działania dla budowy → Notatnik (procedura `notatka`).

## H. Komentarz inwestora do informacji

Gdy w „Moim komentarzu” jest sprzeciw, wątpliwość albo „sprawdzić” (zauważysz go w odpowiedzi, przeglądzie lub sekcji D) –
zaproponuj **jedno** działanie, nic nie zmieniaj bez zgody:
- informacja dotyczy nas i kłóci się ze zdaniem inwestora → pytanie do projektanta/kierownika w Notatniku (`notatka`, Do kogo)
  albo wpis w Rejestrze („Źródło vs nasza decyzja”), gdy inwestor ma już stanowisko;
- inwestor uważa ją za błędną lub nieaktualną → Status „Nieaktualne” (komentarz zostaje jako uzasadnienie);
- komentarz uzupełnia (np. własne doświadczenie) → nic; przy kolejnych pytaniach traktuj go jako opinię inwestora, nie źródło.
