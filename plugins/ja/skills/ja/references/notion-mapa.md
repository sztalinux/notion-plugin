# Notion – sprawy osobiste (mapa)

Mapa dla asystenta: gdzie szukać i dokąd zapisywać sprawy pozabudowlane. Same struktury i identyfikatory – treść jest w Notion.
Plik trafia do przewodnika (`tools/dokumenty.py`) – strona Notion „📑 Przewodnik po dokumentach i Notion”.
Zmiana struktury (nowa baza, widok, pole, sekcja) → zaktualizuj ten plik (procedura `rozwoj-harnessu`).

Strona **📓 Dziennik** `3f8f5982-09e7-80c8-a154-c59aeb844e8f` (najwyższy poziom) – jedno wejście na wszystko:

```
📓 Dziennik
├─ Jak używać (toggle)
├─ nowe wpisy inwestora – bloki 1. poziomu (po przebiegu pusto)
├─ 📝 Wpisy (podstrona) – wpisy pisane wprost w treści albo jako osobne strony (bloki i podstrony; po przetworzeniu pusto)
│   (drugie wejście: strony na najwyższym poziomie Private, np. z widgetu „nowa strona” w telefonie – lista stałych stron niżej)
├─ ### ❓ Czeka na Twoją odpowiedź (toggle) – wpisy z pytaniem asystenta, odpowiedź pod pytaniem
├─ ### Przetworzone (toggle) – zwijany blok na każdy dzień: linia „🤖” + ślad „~~wpis~~ → gdzie”
├─ ### 🧭 Dla asystenta (toggle) – baza 🧭 Obszary Dziennika, wzmianka przewodnika
├─ 📆 Przeglądy dzienne (podstrona – przeglądy osobiste; budowa ma własne na DOM)
├─ 📅 Przeglądy tygodniowe (podstrona – tydzień osobisty; budowa ma własny na DOM)
└─ 🗃 Przetworzone podstrony (podstrona – archiwum wpisów pisanych jako podstrony)
```

| Czego szukasz | Gdzie | ID | Najważniejsze pola |
|---|---|---|---|
| Nowe wpisy, pytania asystenta | 📓 Dziennik (schemat wyżej) | `3f8f5982-09e7-80c8-a154-c59aeb844e8f` | – (wolny tekst) |
| Podział wpisów na obszary (dokąd co idzie) | 🧭 Obszary Dziennika → widok „🤖 Aktywne (dla asystenta)” (tryb view – bez limitu) | `collection://253b7564-00ac-45b2-a3f4-956275e3a7e0`, `view://3faf5982-09e7-817b-a060-000c05f26c6a` | Obszar, Rozpoznawanie, Gdzie, Jak zapisać, Procedura, Aktywny, Kolejność, Przykład |
| Wpisy pisane w treści „Wpisów” albo jako osobne strony | 📝 Wpisy (pod Dziennikiem) – bloki w treści i podstrony = nowe wpisy | `3faf5982-09e7-80b2-9b33-c48745d67a4f` | – |
| Wpisy z widgetu „nowa strona” (telefon) | najwyższy poziom Private – każda strona spoza listy stałych stron niżej (lista stron prywatnych) | – | – |
| Przegląd dnia – sprawy osobiste (dziś / jutro; ręczne „(ręczne)”) | 📆 Przeglądy dzienne (pod Dziennikiem) | `3faf5982-09e7-81df-a361-cc65fddb81f4` | – |
| Przegląd tygodnia – sprawy osobiste | 📅 Przeglądy tygodniowe (pod Dziennikiem) | `3faf5982-09e7-81e3-a6af-e3786ca4a074` | – |
| Widoki do przeglądu tygodnia (tryb view) | TASKS „🤖 Tydzień – prywatne”, Wpisy emocji „🤖 Ostatni tydzień”, Dziennik produktywności „🤖 Ostatni tydzień” | `view://3faf5982-09e7-81b5-ad0a-000c1cfabfa0`, `view://3faf5982-09e7-81ec-83af-000c8b518d37`, `view://3faf5982-09e7-81af-9ea1-000cbe3dd643` | – |
| Widok do przeglądu dnia (tryb view) | TASKS „🤖 Zmiany – od wczoraj (przegląd dnia)” – wszystkie obszary, ostatnia edycja od wczoraj, najnowsze pierwsze; czasy w UTC, dzień tnie procedura (`przeglad-dnia`, krok 5) | `view://3fef5982-09e7-81ec-b46b-000c107597a5` | Name, Obszar, Status, When, Priority, Kategoria, Kto, Desc, Harmonogram, Research, Last edited time |
| Relacja z narzeczoną (do przegadania, prezenty, wspólny czas, daty) | 💞 Relacja (pod 👨‍👩‍👧 Rodzina) | `3faf5982-09e7-81ac-9071-d72e1036eb1f` | sekcje: 💬 Do przegadania, 🎁 Prezenty i niespodzianki, 💡 Wspólny czas i randki, 📅 Ważne daty |
| Strona startowa ze skrótami | 📌 DASHBOARD (zakładki obszarów; podstrona 🗺 Mapa Notion) | `8ef0a264-9b9e-4463-8e2e-2c64887f110d` | – |
| **Poza zasięgiem asystenta** | 🔒 Prywatne i jej podstrony – nie czytaj, nie przeszukuj, nie cytuj (`ja`, zasada 5) | `3faf5982-09e7-816b-92ab-d8b79c61ad92` | – |
| Wesele (notatki, linki, wzmianki zadań) | 💍 Wesele (pod 👨‍👩‍👧 Rodzina) | `3faf5982-09e7-81ec-bdc0-c8e41b99d52a` | sekcje: 📝 Notatki i pomysły, 🔗 Linki, miejsca, usługodawcy, ✅ Do zrobienia |
| Przegląd dnia – budowa | 📆 Przeglądy dzienne – budowa (strona na DOM, plugin dom-budowa) | `3f8f5982-09e7-815e-8b03-eacaa74db190` | – |
| Przetworzone wpisy-podstrony | 🗃 Przetworzone podstrony (pod Dziennikiem) | `3faf5982-09e7-8115-908f-f764d3133d6f` | – |
| Wszystkie zadania (dom i prywatne) | TASKS (baza na stronie ✅ Zadania; na DOM tylko widok budowy) | `collection://2a9f5982-09e7-81be-91e8-000b0e10a05e` | Name, **Obszar** (Dom / Prywatne / Dziecko / Praca; puste = Dom), PLANNED, When, Priority, Kategoria, Kto, Desc |
| Zadania prywatne / dziecka / jutro (widoki bazy) | TASKS → „🏠 Prywatne”, „👪 Dziecko”, „📅 Jutro – wszystko” | `view://3faf5982-09e7-81f9-9832-000c4e6b8e97`, `view://3faf5982-09e7-81aa-8e09-000c3fb8e29f`, `view://3faf5982-09e7-818a-9939-000cb6095c9c` | – |
| Zadania – zakładki strony ✅ Zadania (blok widoku TASKS w każdej; 17.10.2026) | 📅 Dziś i tydzień: „📅 Dziś” (po terminie i na dziś, bez SOMEDAY), „🗓 Tydzień (7 dni)”; 🏠 Prywatne („🏠 Prywatne i praca”, bez Dziecka); 🏗 „🏗 Budowa” (Dom lub puste); 👪 „👪 Dziecko” | `view://3faf5982-09e7-816b-b1d9-000cbc1bc16d`, `view://3fcf5982-09e7-8192-836c-000c587023ce`, `view://3faf5982-09e7-819b-ae03-000c7ac0a486`, `view://038b205e-2e33-4347-91db-fe4ab5151474`, `view://346db48d-3111-4209-a5ca-92639d9b1dcb` | zakładka 🛒 Zakupy: blok widoku bazy Zakupy – „🛒 Do kupienia” `view://281a1146-6bc2-425a-8792-cc9382a544ee`, „📦 Zamówione – czekam” `view://3fcf5982-09e7-8177-9782-000cf6f4b61b` |
| Lista zakupów (poza suplementami i materiałami budowy) | 🛒 Zakupy (na stronie ✅ Zadania; zakładka 🛒 Zakupy) | `collection://3747d532-a49b-44a4-b36f-b3196f917243`; widoki bazy: „🛒 Do kupienia” `view://3fcf5982-09e7-814b-bb71-000cd7dc0e88`, „📦 Zamówione – czekam” `view://3fcf5982-09e7-81d4-9e65-000c5460bb85`, „✅ Kupione” `view://3fcf5982-09e7-81db-93f8-000cb1f40a2d` | Rzecz, Status (Do kupienia / Zamówione / Kupione / Odpuszczone), Gdzie, Sklep / serwis, Ilość, Termin, Obszar, Link, Cena, Uwagi, Kupione dnia, Zadanie (tylko pilne / z terminem), Research |
| Research do zakupów i spraw (RES-n) | 🔎 Research (na stronie ✅ Zadania) | `collection://02ad37a1-64a4-452a-9eac-a8c2012c867e`; widoki: „🔎 Do zrobienia” `view://3fcf5982-09e7-8117-840c-000cf5543291`, „❓ Pytania do mnie” `view://3fcf5982-09e7-8169-ae28-000c5278adda` | Temat, ID (RES-n), Status (Do zrobienia / Pytania do mnie / Gotowy / Zamknięty), Zlecenie (Wprost / Z wpisu), Obszar, Rekomendacja, Zrobiono, Zakup, Zadanie |
| Emocje (jeden wiersz = jedna emocja) | Dziennik emocji → Wpisy emocji | `collection://41556944-46fa-4155-ae95-5b74b983d7aa` | Wpis (nazwa emocji), Kiedy, Intensywność, Trigger / co się stało, Ciało, Myśl, Potrzeba, Reakcja, Emocja wtórna, Czynniki podatności |
| Podsumowania dni emocji (tylko na prośbę) | Dziennik emocji → Dni (dziennik emocji) | `collection://15f206a7-3832-472f-9ed6-b01a515193e1` | Dzień, Data, Podsumowanie (opcjonalnie) |
| Dzień pracy | Dziennik emocji → Dziennik produktywności (praca) | `collection://4b0ef0a5-859e-42e0-98fa-673510b4629c` | Data (tytuł), Początek pracy, Koniec pracy, Ocena produktywności (1–10), Opis pracy, Przerwy i przeszkadzajki, Multitasking |
| Notatki o dziecku | Strona dziecka (nazwa = imię) | `241f5982-09e7-8023-9793-fa12d36bdb2e` | sekcje: 💬 Do przegadania, 🎁 Prezenty, 📝 Obserwacje i informacje, 💡 Pomysły (zabawy, wyjazdy, książki), 🩺 Zalecenia (fizjoterapia, przedszkole), 🗄 Archiwum |
| Książki dla dziecka | strona dziecka → 💡 Pomysły → baza Ksiazki | `collection://32ff5982-09e7-809c-b4ac-000b8a8bf9ac` | Name |
| Suplementy | Suple | `collection://0771d295-5bc0-46e3-b0cb-def13bccab8d` | Name, Status (TAKING / BREAK / TO START / SUSPENDED), **Buy**, Who, When, Last break, Type |
| Książki do przeczytania | Books → All | `collection://5b028761-478a-4d72-acfd-6082043487c2` | Name, Author, Status (To read…), Priority (Must/Should/May), Area |
| Filmy i seriale do obejrzenia | 🎬 Films (w 🗂️ Collections) | `collection://bea14b52-2a7f-45a2-b5a7-cbd1c255fa8b` | Name, Status (To watch / Watched), Tags, URL |
| Poprawki sposobu pracy asystenta | Zmiany do harnessu | `collection://e217448a-60ec-4af6-8584-8f368315109c` | Zmiana, Status, **Plugin**, Procedura, Rodzaj, Treść do wdrożenia, Dlaczego |
| Pomysły na rozwój harnessu | Pomysły na rozwój (na stronie 🤖 Asystent AI) | `collection://fdee4f05-8f43-4be4-a0d5-2b88642fa6d3` | ID (POM-n), Status, Obszar, Nakład, Wymaga ode mnie |
| Wersja harnessu, skrzynka i pomysły | 🤖 Asystent AI | `3f4f5982-09e7-81f5-b7f9-d6cf5d79bb34` | – |
| Dostęp do indeksu wiedzy z czatu (kopia, token odczytu, polecenia) | 🔑 Asystent – dostęp (podstrona 🤖 Asystent AI; tylko dla asystenta) | `3fcf5982-09e7-810e-aaca-f2b582438924` | – |

**Struktura najwyższego poziomu (POM-9, 15.10.2026)** – strona startowa 📌 DASHBOARD w zakładkach, opis całości dla inwestora: „🗺 Mapa Notion”
(`3faf5982-09e7-8186-b1f1-f2b4ed2a9448`, pod DASHBOARD). **Lista stałych stron najwyższego poziomu Private (komplet –
każda inna strona na tym poziomie to nowy wpis z widgetu, `wpisy`):**
- 📌 DASHBOARD `8ef0a264-9b9e-4463-8e2e-2c64887f110d` – strona startowa w zakładkach, 🗺 Mapa Notion;
- 🛖 DOM `24af5982-09e7-806b-821a-e157ff33be42` – budowa (plugin dom-budowa);
- 📓 Dziennik `3f8f5982-09e7-80c8-a154-c59aeb844e8f` – wejście na wszystko (schemat wyżej);
- ✅ Zadania `3faf5982-09e7-8188-8bbd-ce6f8f691cdd` – zakładki (📅 Dziś i tydzień, 🛒 Zakupy, 🏠 Prywatne, 🏗 Budowa, 👪 Dziecko), pod nimi baza TASKS
  (wszystkie obszary) i jej widoki, bazy 🛒 Zakupy i 🔎 Research; na DOM tylko widok zadań budowy;
- 🤖 Asystent AI `3f4f5982-09e7-81f5-b7f9-d6cf5d79bb34` – wszystko o samym asystencie (budowa i sprawy osobiste): wersja pluginów,
  skrzynka Zmiany do harnessu, baza Pomysły na rozwój; podstrona 🔑 Asystent – dostęp `3fcf5982-09e7-810e-aaca-f2b582438924` (dostęp do indeksu wiedzy dla czatu –
  nie jest stroną najwyższego poziomu);
- 👨‍👩‍👧 Rodzina `3faf5982-09e7-8134-b482-c6eb748e87a7` – strona dziecka, 💞 Relacja, 💍 Wesele;
- 🩺 Zdrowie `3faf5982-09e7-81a2-93bd-c85b2ebe040b` – Suplementacja (baza Suple), Examinations, notatki zdrowotne;
- 🧠 Ja `3faf5982-09e7-81b6-b5b7-e0d5e3fe7ef8` – Personality (Dziennik emocji, Terapie, Wartości…), Hobbies, Inspiration;
- 💼 WORK `c1dc91d3-5247-4c9b-8ec9-cc431c1b3ebb` – praca;
- 📚 Wiedza `3faf5982-09e7-8113-a03c-eed243d4adc8` – Knowledge, My Kindle Clippings;
- 🗂️ Collections `44321b47-fd10-46f8-8d2e-574ac07502ac` – listy i kolekcje, Books, 🎬 Films, Listy do zabrania, Linki do obejrzenia;
- 🗄 Archiwum `3faf5982-09e7-8100-8725-cc0ca586a23e` – nieużywane strony (tylko do wglądu, nie zapisuj);
- 🔒 Prywatne `3faf5982-09e7-816b-92ab-d8b79c61ad92` – poza zasięgiem asystenta (wyżej): na liście tylko po to, żeby jej nie
  otwierać.
Inwestor dodał nową stałą stronę na tym poziomie → dopisz ją tu (`ja`, zasada 8).
Nowa strona w obszarze: zapisuj pod stroną obszaru; nowy rodzaj wpisu z Dziennika – wiersz w bazie Obszary.

**Archiwa (tylko do wglądu, nie zapisuj):** 🗄 Archiwum (ALL TODOS, DONE, stara RESOURCES z Others, kopie zapasowe,
Quick notes – rozebrany w POM-9, oryginały w jego podstronie „Przetworzone”). Strona WORK ma własną bazę zadań z pracy – nie zapisuj tam; zadania z pracy
wpisane do Dziennika idą do TASKS z Obszar = Praca.
