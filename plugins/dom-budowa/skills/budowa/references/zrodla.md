# Źródła prawdy – gdzie co leży

Zasada podziału: **harness = JAK pracujemy** (procedury, formaty, zasady) – to repozytorium.
**Dane = CO wiemy** (fakty, decyzje, liczby, wiedza) – Notion i Excel. Nie kopiuj danych do harnessu –
**repozytorium jest publiczne**.

## Mapa

| Co | Gdzie | Kto edytuje |
|---|---|---|
| Procedury, zasady, szablony | publiczne repo GitHub `sztalinux/notion-plugin` → pluginy `dom-budowa` i `ja` na koncie Claude (aktualizacja: ręczne odświeżenie lub synchronizacja – plugin `ja`, `rozwoj-harnessu/references/claude-ai-projekt.md`) | Claude Code (`rozwoj-harnessu`, sekcja B) |
| Zgłoszone zmiany harnessu (obowiązują od razu) | Notion → 🤖 Asystent AI (najwyższy poziom) → Zmiany do harnessu | dowolny asystent (`rozwoj-harnessu`, sekcja A) |
| Pomysły na rozwój (do analizy; wdrożenie tylko na polecenie) | Notion → 🤖 Asystent AI → 💡 Pomysły na rozwój | inwestor wpisuje, asystent analizuje (`rozwoj-harnessu`, sekcja C) |
| Terminy: harmonogram, zadania, czekam na, zamówienia | Notion → Harmonogram, TASKS, 🧱 Zakupy budowy (daty); kwoty i płatności – arkusz Google „Kosztorys budowy” (Etapy, Wydatki) | agent (`harmonogram`, `zakupy`), inwestor |
| Umowy, odbiory, gwarancje | Notion → Umowy i gwarancje; skany – folder budowy | agent (`oferta`, `etap`), inwestor |
| Luźne wpisy inwestora do rozłożenia (wszystkie obszary, także budowa) | Notion → „📓 Dziennik” (wolny tekst; podział na obszary w bazie „🧭 Obszary Dziennika”) | inwestor wpisuje, agent przetwarza (`wpisy`, plugin `ja`; sprawy budowy – `budowa`, „Luźny wpis z Dziennika”) |
| Liczby: kosztorys, wydatki, ceny zakupu | Arkusz Google „Kosztorys budowy” – prowadzi inwestor; kopia do analiz `Koszty/Kosztorys_google.json` (`tools/wydatki.py pobierz`, wartości, co wieczór) | Inwestor; wydatki dopisuje automat z kolejki „💸 Wydatki → arkusz” (`koszty`, sekcja B; `docs/wydatki-arkusz.md`); strukturę agent zmienia tylko na prośbę (`koszty`, sekcja C) |
| Notatki, decyzje, pytania, ryzyka naszej budowy | Notion → DOM → Notatnik budowy | Inwestor + agent (`notatka`) |
| Zadania z terminem | Notion → TASKS (baza na stronie ✅ Zadania, na DOM widok „🏗 Zadania budowy”; wspólna ze sprawami osobistymi, budowa = Obszar Dom) | Inwestor + agent (`notatka`, `harmonogram`; prywatne – `zadania`, plugin `ja`) |
| Porównanie wykonawców (jakość, zakres, knock-out) | Notion → Wybór wykonawcy – stan zero → baza „Porównanie wykonawców” | agent (`oferta`) |
| Wiedza: tematy, informacje, rozmowy i filmy | Notion → DOM → Baza wiedzy (Tematy, Informacje, Rozmowy i źródła) | agent (`wiedza`), inwestor przegląda |
| Sprzeczności i dylematy (ADR) | Notion → Baza wiedzy → Rejestr sprzeczności | agent zgłasza, **decyduje inwestor** |
| Indeks wiedzy (SQLite, kopia w prywatnym repo wskazanym w zmiennej `GITHUB_REPO`, strona dostępu w Notion) | Lokalnie w `.dom/wiedza/` (poza repo), tylko do odczytu; kopia dla czatu w prywatnym repo GitHub; ścieżka repo i token odczytu – Notion → 🤖 Asystent AI → 🔑 Asystent – dostęp; procedura `wiedza/references/indeks.md` | agent odtwarza z Notion (`python3 tools/wiedza.py sync`), nigdy nie zapisuje do niego wiedzy; Notion zostaje źródłem prawdy |
| Przeglądy tygodniowe | Notion → DOM → Przeglądy tygodniowe | agent (`przeglad-tygodnia`) |
| Dziennik inwestora (dni na budowie, dostawy, usterki, godziny własne) | Notion → DOM → Dziennik budowy (schemat: `dziennik/references/notion-dziennik.md`); zdjęcia w folderze budowy `Zdjęcia/` | inwestor + agent (`dziennik`) |
| Bramki i odbiory etapów | Notion → DOM → 🏗 Etap → zakładki etapów (przewodnik, checklista), „Stan zero – punkty bez odwrotu”; protokoły w folderze budowy | agent przygotowuje (`etap`), odbiera inwestor z kierownikiem |
| Analizy dokumentów | Notion (strona pod DOM) lub dokument w projekcie Claude | agent (`analiza-techniczna`) |
| Dokumenty: projekty, opinie, oferty, umowy (PDF, Excel) | folder budowy na komputerze inwestora; opis każdego dokumentu: strona Notion „📑 Przewodnik po dokumentach i Notion” (synchronizuje Claude Code); pełne dokumenty na prośbę | inwestor wrzuca, agent klasyfikuje (`dokumenty`); oryginały tylko odczyt |
| Ściąga projektu (najważniejsze liczby i decyzje) | **Notion → DOM → „📐 Dane projektu (ściąga)” – jedyne źródło**; `Ściąga projektu.md` w folderze budowy to kopia do paczki awaryjnej (Claude Code odświeża ją po zmianie w Notion) | agent po nowym dokumencie (`dokumenty`, `analiza-techniczna`), inwestor ręcznie |

## Notion – identyfikatory (konto prywatne inwestora)

Pełna mapa z perspektywy „czego szukasz” (widoki, pola, słowniki): `notion-mapa.md`.

| Element | ID |
|---|---|
| Strona DOM (pulpit) | `24af5982-09e7-806b-821a-e157ff33be42` |
| Notatnik budowy (data source) | `collection://7423414a-707b-415f-8751-c6ab7ebb6753` |
| TASKS (data source) | `collection://2a9f5982-09e7-81be-91e8-000b0e10a05e` |
| Wybór wykonawcy – stan zero (strona) | `3f3f5982-09e7-81e8-b361-c7bee2e3847d` |
| Porównanie wykonawców – stan zero (data source) | `collection://f7ca5f38-8fc3-46e7-8345-8a32cc8b5215` |
| Zakładka 🏗 Etap na DOM – przewodnik etapów w zakładkach (strona „Etapy budowy – przewodnik” `3f3f5982-09e7-8161-b30e-fdcf2284554b` to tylko odnośnik) | `8e0aca76-56ea-42ec-a022-99e903afb926` |
| Baza wiedzy (strona) | `3f4f5982-09e7-8193-a68e-fd35c9265012` |
| Tematy / Informacje / Rozmowy i źródła / Rejestr sprzeczności | `wiedza/references/notion-wiedza.md` |
| Przeglądy tygodniowe (strona) | `3f4f5982-09e7-8144-af5e-f9521a52ea9d` |
| 🤖 Asystent AI (wersje obu pluginów, skrzynka, pomysły) | `3f4f5982-09e7-81f5-b7f9-d6cf5d79bb34` |
| 🔑 Asystent – dostęp (strona pod 🤖 Asystent AI: dostęp do indeksu wiedzy dla czatu) | `3fcf5982-09e7-810e-aaca-f2b582438924` |
| 📓 Dziennik (strona wpisów) / 📆 Przeglądy dzienne – budowa (na DOM) | `3f8f5982-09e7-80c8-a154-c59aeb844e8f` / `3f8f5982-09e7-815e-8b03-eacaa74db190` |
| Zmiany do harnessu (data source) | `collection://e217448a-60ec-4af6-8584-8f368315109c` |
| Pomysły na rozwój (data source) | `collection://fdee4f05-8f43-4be4-a0d5-2b88642fa6d3` |
| Dziennik budowy (data source) | `collection://cc113d57-3eaa-4f52-80f6-e4b39a4b4c92` |
| Przewodnik po dokumentach i Notion (strona, generowana) | `3f6f5982-09e7-81f5-bade-ec877d8d936a` |
| Harmonogram (data source) | `collection://d7a479ab-1e23-453f-8f59-55f4097f7d04` |
| 🧱 Zakupy budowy (data source) | `collection://a9854c6c-43ec-4bc1-8ef0-273fb02261c7` |
| 💸 Wydatki → arkusz (data source; kolejka do arkusza Google) | `collection://72cff09c-609b-405d-a32c-263271b3b59c` |
| Umowy i gwarancje (data source) | `collection://60c06f30-7867-435d-8f2e-1e025a3daa5c` |

Schematy baz budowy (pola i dozwolone wartości): `skills/notatka/references/notion-schematy.md`.
Jeśli ID przestanie działać, wyszukaj stronę po nazwie i zaktualizuj tabelę.
