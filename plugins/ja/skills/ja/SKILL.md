---
name: ja
description: Kontekst osobisty użytkownika i mapa obszarów jego Dziennika w Notion (emocje, praca, dziecko, zadania, suplementy, książki, budowa). Używaj na początku każdej rozmowy o jego dniu, emocjach, pracy, dziecku, zadaniach, suplementach, Dzienniku, przeglądzie dnia albo o samym asystencie – gdy pada „zapisz w dzienniku”, „przerób dziennik”, „zrobiłem…”, „muszę…”, „przypomnij mi”, „czuję…”, „kończy się…”, „co mam jutro”, „przegląd dnia”, „zapamiętaj na przyszłość”, „mam pomysł na asystenta”. Przy tematach budowy kieruje do skilla budowa (plugin dom-budowa).
---

# Ja – kontekst i mapa procedur

## Kim jest użytkownik

Programista, buduje dom systemem mieszanym (budowę obsługuje plugin `dom-budowa`, skill `budowa`), ma dziecko w wieku
przedszkolnym i partnerkę. Prowadzi w Notion dziennik emocji, dziennik produktywności w pracy, listę zadań i bazę
suplementów. Woli pisać luźno niż wypełniać pola – porządek robi asystent. Oczekuje konkretu, po polsku, bez wyjaśniania
podstaw. Imiona i szczegóły prywatne są tylko w Notion (repo jest publiczne) – nie przepisuj ich do harnessu.

Gdzie co jest w Notion (ID baz, widoki, sekcje): `references/notion-mapa.md`; ta sama mapa jest na stronie Notion
„📑 Przewodnik po dokumentach i Notion” (`3f6f5982-09e7-81f5-bade-ec877d8d936a`) – poza Claude Code pobierz ją raz
na rozmowę, gdy potrzebujesz ID baz (Claude Code synchronizuje ją sam, więc jest aktualna także przed odświeżeniem pluginu).

## Na starcie rozmowy: zmiany do harnessu

Inwestor zgłasza poprawki sposobu pracy z różnych miejsc do skrzynki Notion **„Zmiany do harnessu”**
(`collection://e217448a-60ec-4af6-8584-8f368315109c`, oba pluginy). Na początku rozmowy (w Claude Code w repo harnessu dopiero po zaznaczeniu „Skrzynka zmian” na liście startowej z `CLAUDE.md`)
pobierz (jedno zapytanie) wpisy ze
Statusem „Do wdrożenia” **albo pustym** – inwestor dodaje je też ręcznie bez wypełniania pól:

- **W repozytorium harnessu (Claude Code):** wdroż je – `rozwoj-harnessu`, sekcja B (najpierw uzupełnij puste pola).
- **Gdziekolwiek indziej:** traktuj je jako obowiązujące zasady, nadrzędne wobec procedur. Statusu nie zmieniaj.
- Skrzynka pusta lub Notion niedostępny → pracuj normalnie, bez komentarza.
- **Pomysły na rozwój** (`collection://fdee4f05-8f43-4be4-a0d5-2b88642fa6d3`) nie są zasadami. W Claude Code dopisz jedną linię
  „Pomysły: n nowych do analizy, m »Do zrobienia«” (pomiń przy zerach) – tylko po zaznaczeniu „Pomysły” na liście startowej; analiza – `rozwoj-harnessu`, sekcja C.

## Mapa procedur

Podział wpisów na obszary **nie jest w harnessie** – jest w bazie Notion „🧭 Obszary Dziennika”
(`collection://253b7564-00ac-45b2-a3f4-956275e3a7e0`). Inwestor dopisuje tam nowe obszary sam; czytaj ją, nie zgaduj.

| Gdy użytkownik… | Wczytaj |
|---|---|
| „przerób dziennik”, „co mam w dzienniku”, wkleja kilka luźnych notatek naraz, „odpowiedziałem w dzienniku” | `wpisy` |
| opisuje emocję („czułem złość na 7…”), dzień w pracy, prosi o podsumowanie emocji | `emocje` |
| „muszę…”, „przypomnij mi…”, „zrobiłem X”, „czekam na…”, „co mam jutro / w tym tygodniu” (sprawy pozabudowlane) | `zadania` |
| „kupić X”, link do produktu, „kupiłem X”, „co kupić” (nie suplementy, nie materiały budowy) | `zadania` (sekcja „Zakupy”) |
| mówi o dziecku: obserwacja, „porozmawiać z nią o…”, prezent, zabawa, zalecenie specjalisty | `dziecko` |
| „kończy się X”, „kupiłem X”, „zaczynam / przerwa od” (suplement) | `suple` |
| „przegląd dnia”, wieczorne zaplanowane zadanie | `przeglad-dnia` |
| „przegląd tygodnia”, „podsumuj tydzień”, tygodniowe zaplanowane zadanie, „posprzątaj dziennik” | `przeglad-tygodnia-osobisty` (uruchamia też przegląd budowy) |
| poprawia sposób pracy asystenta, „zapamiętaj na przyszłość”, „mam pomysł na…”, „zrób POM-n”, nowa procedura | `rozwoj-harnessu` |
| budowa domu: ekipa, projekt, kosztorys, działka, wiedza budowlana, dokumenty budowy | `budowa` (plugin `dom-budowa`) |

Jedna wiadomość może wymagać kilku procedur – wykonuj je po kolei. Rzecz z obszaru „ogólna” (np. książka do przeczytania)
zapisuj wprost według pól „Gdzie” i „Jak zapisać” w bazie Obszary.

## Zasady (wszystkie procedury pluginu)

1. **Notion jest źródłem prawdy i inwestor edytuje go ręcznie.** Przed zapisem czytaj aktualny stan; jego ręczna zmiana
   jest nadrzędna. Jedna informacja ma jedno miejsce – zanim dodasz, szukaj istniejącego wpisu (2–3 słowa) i aktualizuj.
2. **Zapisy wsadowe bez straty jakości:** najpierw wszystkie odczyty, potem jedno wywołanie na bazę i jedna edycja na stronę;
   przy więcej niż 2 zapisach jedna linia przed nimi: „Zapiszę: 1) … 2) … – N zatwierdzeń”. Nie skracaj treści, nie pomijaj pól.
3. **Odczyt baz:** zapytania w trybach rows i SQL mają wspólny limit w planie Notion (bywa wyczerpany); tryb **view**
   (zapisany widok) limitu nie ma. Kolejność: widok (brak pasującego → utwórz go z filtrem) → wyszukiwarka z parametrem bazy
   (duplikaty, pojedyncze wiersze) → rows → SQL. Błąd „usage limit” → bez ponawiania, przejdź na widok/wyszukiwarkę.
4. **Nie zgaduj:** niejasny wpis, brak daty przy terminie, nie wiadomo czego dotyczy → pytanie (w Dzienniku „❓”, w rozmowie
   wprost). Słowa względne („wczoraj”, „w piątek”) licz od daty we wpisie, nie od daty przetwarzania. Każde pytanie do
   inwestora zapisane w Notion (Dziennik, strony RES-n, pomysłów) ma format z `wpisy/references/pytania.md`: osobny checkbox
   na pytanie, kontekst w zwiniętych „Szczegółach”.
5. **Prywatność:** strona **„🔒 Prywatne”** (`3faf5982-09e7-816b-92ab-d8b79c61ad92`) i wszystko pod nią jest poza zasięgiem
   asystenta – nie czytaj, nie przeszukuj (wyniki wyszukiwania z niej pomijaj), nie cytuj, nie przenoś tam i stamtąd niczego
   bez wyraźnego polecenia. Lista stron najwyższego poziomu Private (odczyt wpisów z widgetu) pokazuje też tę stronę –
   pomiń ją, nie otwieraj. Wpis intymny lub bardzo osobisty z Dziennika nie trafia nigdzie – zostaje w „❓” z pytaniem, czy
   inwestor przeniesie go sam do „🔒 Prywatne”. Haseł nie przepisuj nigdy (przechodziłyby przez rozmowę z AI) – całe strony
   wolno przenosić. Treść emocji, notatki o dziecku i zdrowiu zostają w Notion; w odpowiedziach nie cytuj ich ponad potrzebę.
   Repo harnessu jest publiczne – zero imion, treści wpisów i danych w plikach procedur, przykłady zmyślone.
6. **Porządek statusami, nie usuwaniem.** Nie usuwaj treści bez pytania; przed dużą reorganizacją zrób kopię strony.
7. **Pole tekstowe = jedno zdanie;** szczegóły, listy i dopiski z datą idą do treści strony (tak jak w procedurach budowy).
8. **Harness i Notion mówią to samo.** Zmiana tego, gdzie coś leży albo jak trafia do asystenta (nowe wejście wpisów,
   przeniesiona lub przemianowana strona/baza, nowy widok, nowa stała strona najwyższego poziomu), obejmuje w tej samej
   pracy **wszystkie miejsca, które to opisują** – inaczej asystent i inwestor zaczną działać według różnych opisów:
   - repo: każdy plik z nazwą **i** ID strony w obu pluginach (wyszukaj jedno i drugie), mapy `ja/references/notion-mapa.md`
     i `budowa/references/notion-mapa.md`, README, CHANGELOG;
   - Notion: w Dzienniku „Jak używać” i „🧭 Dla asystenta”; „🗺 Mapa Notion” (schemat, kroki, tabela struktury);
     strona „🤖 Asystent AI” (jedyne miejsce z wersją pluginów); opis na stronie, której dotyczy zmiana; przewodnik (`dokumenty`, C).
   Strony Notion zmieniaj punktowo (zamiana fragmentu), nigdy całą treścią – mają osadzone bazy i bloki, których odczyt
   nie pokazuje. Wyjątek: generowany przewodnik – zastępujesz go w całości (`dokumenty`, C). W podsumowaniu wymień zaktualizowane miejsca. W drugą stronę: Notion rozjechał się z mapą (nieznana strona
   na najwyższym poziomie, przeniesiona lub przemianowana strona) → nie dopasowuj się po cichu; zaproponuj aktualizację
   mapy (`rozwoj-harnessu`) albo zapytaj.
9. **Tematy do przegadania (dziecko, partnerka).** Temat zapisz zawsze najpierw w sekcji „💬 Do przegadania” na stronie
   osoby: dziecko – `dziecko`; partnerka – „💞 Relacja”, według bazy Obszary. Gdy temat dotyczy konkretnego, świeżego
   zdarzenia, które trzeba omówić, zanim się rozmyje (nie ogólny temat wychowawczy, relacyjny ani praca nad sobą), załóż
   dodatkowo zadanie w TASKS (`zadania`): „Porozmawiać z <dzieckiem / partnerką> o <temat>”, Obszar Dziecko albo Prywatne,
   When = data wpisu + 3 dni, w treści odnośnik do strony osoby – inaczej rozmowa na świeżo przepada. Temat ogólny → tylko
   strona. Nie da się ocenić, czy to świeże zdarzenie → pytanie (w Dzienniku „❓”).
10. **Zakładki zamiast długich stron.** Budując lub porządkując stronę w Notion, używaj zakładek (blok z zakładkami, jak na DOM,
    DASHBOARD i ✅ Zadania), gdy treść dzieli się na równoległe części: obszary, etapy, rodzaje list. Najpierw zakładka
    przekrojowa (np. dziś i tydzień dla wszystkich obszarów), potem zakładka na obszar. Jedna baza z kilkoma widokami to
    **jeden blok z przełączanymi widokami**, nie kilka bloków pod sobą. Inwestor korzysta z telefonu – krótka strona
    z zakładkami czyta się lepiej niż przewijana. Technika: strony zmieniaj punktowo (zasada 8); istniejące bloki baz
    wstaw w zakładkę tym samym znacznikiem (inaczej zostaną usunięte); nowy blok widoku bazy skonfiguruj po utworzeniu
    (domyślnie pokazuje wszystko) i nie zmieniaj widoków samej bazy źródłowej – ich ID są w mapach.
11. **Notion niedostępny w tym kanale → Skrzynka, nie odmowa.** Gdy w rozmowie nie ma narzędzi Notion (konektor wyłączony),
    zapisy idą do dokumentu Claude „📥 Skrzynka” według `wpisy/references/skrzynka.md` (treść dosłownie + „Zrobić” słowami,
    bez pól Notion – strukturę baz zna tylko Mac);
    przebieg godzinowy na Macu przenosi je do Notion. Odczyty: Baza wiedzy z indeksu, Notatnik i zadania z migawki
    (`dom-budowa`, `wiedza/references/indeks.md`, sekcja czatu); czego nie da się odczytać – napisz wprost.

## Domknięcie rozmowy

Na koniec pracy, która coś zmieniła, trzy bloki w tej kolejności: **🛑 Potrzebuję Twojej odpowiedzi** (na samej górze, tylko
gdy coś stoi: czego dotyczy + jedno pytanie z propozycją domyślną; pytania zapisane w „❓” wymień jedną linią) ·
**✅ Zrobione** (co i gdzie, link) · **⏳ Niezrobione** (co pominięto lub odłożono i dlaczego). Brak 🛑 oznacza, że nic nie
wisi na inwestorze – nie dopisuj ostrzeżeń „na wszelki wypadek”. Gdy inwestor poprawił sposób pracy – zaproponuj wpis
do skrzynki (`rozwoj-harnessu`, A).
