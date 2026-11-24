# Kontrola spójności: status pomysłu (POM-n) ↔ stan wdrożenia (przegląd tygodnia)

Robi ją raz w tygodniu `przeglad-tygodnia-osobisty` (krok 3); nocny przegląd dnia stosuje tylko odpowiedzi ☑ („Przebieg”, 1) –
codzienny odczyt całej tablicy pomysłów kosztował ok. 38 tys. znaków na noc (pomiar 24.11.2026), a rozjazdy powstają rzadko.

Statusy pomysłów (Rodzaj Pomysł w „🤖 Zmiany asystenta”; odczyt widokiem „🤖 Pomysły – kontrola wersji”) zmienia inwestor ręcznie, a wdrożenia zapisuje Claude Code (pole „Zrobiono w wersji”
i `CHANGELOG.md`) – więc oba bywają rozjechane. Ta grupa serii „Kontrola spójności” (klucze `KS-…`) to **P**. Wspólny
format flag, odpowiedzi ☑ i limit 5 nowych flag na przebieg – jak w pozostałych grupach serii (`kontrola-spojnosci*.md`);
poniżej tylko to, co szczególne dla pomysłów. **Statusu pomysłu asystent sam nie zmienia** (decyzja inwestora jest
nadrzędna) – zmienia tylko pole „Zrobiono w wersji”, i to wyłącznie z nagłówka CHANGELOG (P1, P4).

## Reguły

Czytaj wyłącznie widok „🤖 Pomysły – kontrola wersji” (`view://422f5982-09e7-81c6-87b4-000cdd9ad46f`, tryb view): Rodzaj = Pomysł
ze Statusem „Do zrobienia” albo „Przeanalizowany” oraz „Zrobione” z polem „Zrobiono w wersji” pustym albo ze słowem „gałąź” – czyli sami kandydaci
(kilka wierszy zamiast całej tablicy; „💡 Tablica pomysłów” tu nie czytaj). Nowy, Czeka na mnie, Odłożone i Odrzucone są poza widokiem. Wartość pola „Zrobiono w wersji” ze słowem „częściowo” oznacza wdrożenie w częściach – status
„Przeanalizowany” albo „Do zrobienia” jest wtedy celowy (P2 jej nie flaguje); wartość „gałąź … (czeka na scalenie)”
to praca poza główną gałęzią – dopóki CHANGELOG nie ma wpisu z tym POM, nic nie rób.

| Grupa | Rozjazd | Skutek |
|---|---|---|
| **P1** | Status „Zrobione”, „Zrobiono w wersji” **puste** | CHANGELOG ma nagłówek z POM-n → **uzupełnij pole** (jedyny zapis bez ☑); nie ma → pytanie „❓ Uzupełnić »Zrobiono w wersji«?” (inwestor wpisuje wersję albo „skrypt poza repo, data”) |
| **P2** | Status „Do zrobienia” / „Przeanalizowany”, pole „Zrobiono w wersji” niepuste, bez „częściowo” i bez „gałąź” | pytanie „❓ Status → Zrobione?” (☑ = ustaw „Zrobione”, pole zostaje) |
| **P3** | Status „Do zrobienia” / „Przeanalizowany”, pole **puste**, a CHANGELOG ma nagłówek z POM-n | pytanie „❓ Status → Zrobione? (CHANGELOG: <wersja>)” (☑ = ustaw „Zrobione” i uzupełnij pole z nagłówka) |
| **P4** | pole „Zrobiono w wersji” to „gałąź … (czeka na scalenie)”, a CHANGELOG na głównej gałęzi ma nagłówek z tym POM-n | **zastąp pole** wersją z nagłówka (po scaleniu przez integratora; Status bez zmian) – przy Statusie innym niż „Zrobione” dopisz „ (częściowo)”, żeby P2 nie pytał o wdrożenie niepełne |

Zasada pomysłu: „Zrobione” bez wersji uzupełniasz tylko, gdy wersja jest **jednoznaczna** – czyli stoi w nagłówku
`## <plugin> [wersja] – data (POM-n)`. Sama wzmianka POM-n w treści wpisu nie wystarcza (bywa odwołaniem do innego pomysłu;
starsze wpisy sprzed 11.11 nie mają numerów w nagłówkach) – wtedy P1 daje pytanie, a P3 nie flaguje wcale.
Kilka nagłówków jednego POM (kolejne etapy) → wpisz wszystkie wersje po przecinku („ja 1.4.0, ja 1.5.0”).

## Przebieg (przegląd tygodnia; jeden odczyt widoku kandydatów)

1. **Zastosuj odpowiedzi** na wcześniejsze punkty `KS-P…` (robi to tylko nocny przegląd dnia, krok 2; tygodniowy zaczyna od punktu 2): ☑ przy P2 → Status „Zrobione”; ☑ przy P3 →
   Status „Zrobione” i pole „Zrobiono w wersji” z nagłówka CHANGELOG; dopisek „zostaje” / „częściowo” → nic nie zmieniaj;
   dopisek z wersją przy P1 → wpisz ją w pole. Rozpatrzony punkt idzie do „Przetworzone” z kluczem i dopiskiem „→ KS: <wykonano | zostaje>”.
2. **Wersje z CHANGELOG** – tylko gdy jest kandydat P1, P3 albo P4: `python3 tools/pomysly_wersje.py <n> <n> …` (z folderu repo;
   czyta CHANGELOG z gałęzi main, czyli to, co wdrożone – linia „⚠ … czytam plik z dysku” = gałęzi main nie ma, wynik może
   obejmować niescalone zmiany, więc P1 i P4 zamień na pytania; wypisuje „nagłówki” = jednoznaczne i „tylko w treści” = niejednoznaczne). Bez dostępu do `CHANGELOG.md` (przebieg poza
   repo, Bash niedozwolony, claude.ai) albo gdy nie możesz go przeczytać – pomiń P3 i P4, a P1 zamień na pytanie; P2 działa
   wyłącznie na danych z Notion i zostaje.
3. **Zapisz P1 i P4** (jedna edycja strony pomysłu, tylko pole „Zrobiono w wersji”, format „<plugin> <wersja>[, …]”) – bez pytania,
   bo wartość pochodzi z nagłówka CHANGELOG; są idempotentne (po zapisie wiersz nie jest już kandydatem), więc bez klucza.
   Licznik „uzupełniono wersje: n” – punkt 5.
4. **Pytania P1/P2/P3** – jedno pytanie = jeden to-do z kluczem `KS-P<n>-<ostatnie 6 znaków ID strony pomysłu>` jako blok 🔔
   we „Wpisach” (`wpisy/references/pytania.md`, C.7; dopisek „zastosuję w nocnym przeglądzie”), np. `- [ ] POM-8: Status → Zrobione? (pole „Zrobiono w wersji” wypełnione) KS-P2-d1e2f3`;
   ID pomysłu (POM-n) podaj jako wzmiankę strony. Pomiń parę, której klucz jest już w 🔔 (czeka) albo w „Przetworzone”
   (rozpatrzona – wyciszenie trwa, dopóki wpis tam jest). Liczy się do wspólnego limitu 5 nowych flag `KS-…` na przebieg.
5. **Licznik** do wpisu tygodniowego (linia „Porządki”, fragment „spójność: …”) i odpowiedzi: `pomysły n pytań, wersje uzupełnione k` (P1, P4);
   wykonane nocą odpowiedzi ☑ liczą się do nocnego `rozjazdy: … m wykonanych`.

## Czego nie robić

- Nie zmieniaj Statusu pomysłu bez ☑ inwestora i nie ruszaj treści strony pomysłu ani „Wymaga ode mnie”.
- Nie zgaduj wersji z treści wpisu CHANGELOG ani z `git log` – tylko nagłówek z numerem POM.
- Nie flaguj pomysłów „Nowy”, „Czeka na mnie”, „Odłożone”, „Odrzucone”; nie flaguj wdrożeń oznaczonych „częściowo”.
- Nie wdrażaj pomysłów i nie analizuj ich – analiza tylko na prośbę inwestora (`rozwoj-harnessu`, C).
