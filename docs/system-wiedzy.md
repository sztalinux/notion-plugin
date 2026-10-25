# System wiedzy budowy – mapa

Przegląd dla człowieka: z jakich części składa się obsługa bazy wiedzy, kto co uruchamia i gdzie szukać szczegółów.
Procedury dla asystenta są w `plugins/dom-budowa/skills/wiedza/` – ten plik ich nie zastępuje, tylko pokazuje całość.
Stan: 25.10.2026. Elementy oznaczone **[planowane]** jeszcze nie działają.

## Części

| Część | Rola | Szczegóły |
|---|---|---|
| Notion | Jedyne źródło prawdy: bazy Informacje (tezy WI), Tematy, Rozmowy i źródła (ZRD), Rejestr sprzeczności (SP) | `references/notion-wiedza.md` |
| Indeks (`tools/wiedza.py`) | Lokalna kopia tych baz w jednym pliku SQLite poza repo; szukanie po słowach (FTS5, synonimy z `tools/wiedza_synonimy.txt`, ranking bm25); tylko odczyt Notion | `references/indeks.md`, `references/indeks-awarie.md` |
| Kopia dla czatu | Indeks publikowany do prywatnego repo; czat na telefonie pobiera go tokenem tylko do odczytu | `references/indeks.md` |
| Obserwator (`tools/wiedza_jakosc.py`) | Stałe zbiory pytań i znanych wierszy; alarm, gdy wyszukiwanie po zmianach zaczyna gubić to, co znajdowało | `references/indeks-jakosc.md` |
| Sędzia LLM (`wiedza_jakosc.py sedzia`) | Model bez narzędzi ocenia sens wyników dla pytań testowych; filtr danych osobowych przed wysłaniem | `references/indeks-sedzia.md` |
| Ocena ręczna (`wiedza_jakosc.py reczna`) | Inwestor ocenia wyniki w terminalu; punkt odniesienia dla sędziego | `references/indeks-jakosc.md` |
| Nocne przetwarzanie (poza repo, prywatne) | Kolejka filmów i artykułów, przetwarzanie do Notion, kontrola wyrywkowa obu silników (indeks i wyszukiwarka Notion) ze ślepą oceną sędziego | – |
| **[planowane]** Odciski znaczenia | Lokalny model embeddingów (Ollama) liczony w trakcie `sync` dla nowych i zmienionych tez; przełącznik źródła: lokalnie / Bedrock / brak | – |
| **[planowane]** Listy podobnych | Dla każdej tezy najbliższe znaczeniowo; trafiają do kopii dla czatu, bo czat nie może liczyć embeddingów | – |

## Kto co uruchamia

1. **Start sesji Claude Code w repo** – lista wyboru (`CLAUDE.md`). Pozycja „Indeks wiedzy” = `sync --publikuj --cicho`
   i przypomnienie obserwatora. **[planowane]** Odciski znaczenia liczą się w środku `sync`; brak Ollamy = pominięte
   bez błędu, więc nie dochodzi żadna nowa pozycja na liście.
2. **Noc (inwestor uruchamia)** – po każdej pozycji odświeżenie indeksu, co N-te pytanie o wiedzę kontrola obu silników,
   na końcu publikacja kopii, obserwator i sędzia (gdy minął ustawiony odstęp).
3. **Czat na telefonie** – pobiera kopię i szuka; przeglądy dnia i tygodnia działają jako zaplanowane zadania claude.ai.
4. **Ręcznie, od czasu do czasu** – ocena ręczna, `zloty --odnowa` po dużych zmianach bazy, przegląd raportów jakości.

## Pomiary (październik 2026)

- Kontrola wyrywkowa (te same zapytania, ślepa ocena każdego wyniku): indeks znalazł 84% wszystkich trafnych wyników
  znalezionych przez którykolwiek silnik, wyszukiwarka Notion 40% (72 testy).
- Audyt końcowego efektu (20 źródeł, punkt odniesienia = cały temat): asystent oznaczył 63% istotnych powiązań
  z istniejącą wiedzą w trybie indeksu i 47% w trybie Notion; ponad 94% pominiętych powiązań leżało w tym samym temacie.
- Ocena ręczna vs sędzia (wstępnie, 10 par): pełna zgodność przy mapowaniu „trafny” ↔ ocena 2.

Wniosek: wyszukiwanie dostarcza ok. 80% potrzebnej wiedzy, a największe straty są przy porównaniu nowej tezy z bazą.

## Kolejność dalszych zmian

1. Szukanie na czacie: kilka sformułowań w jednym wywołaniu, krótszy wynik, procedura z czytaniem całego tematu.
2. Odciski znaczenia w `sync` i listy podobnych w kopii dla czatu.
3. Porządki w bazie (duplikaty, sprzeczności) – raport do decyzji inwestora.
4. Test jakości odpowiedzi czatu przed i po zmianach.
5. Osobny etap porównania z całym tematem w nocnym przetwarzaniu.

Każda zmiana procedur i narzędzi: procedura `rozwoj-harnessu` (wersja → CHANGELOG → `tools/build.py` → commit → push).
