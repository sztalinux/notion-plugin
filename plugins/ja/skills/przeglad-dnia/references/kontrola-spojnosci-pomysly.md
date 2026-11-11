# Kontrola spójności: status pomysłu (POM-n) ↔ stan wdrożenia (krok 2 wieczornego przeglądu dnia)

Statusy w bazie „Pomysły na rozwój” zmienia inwestor ręcznie, a wdrożenia zapisuje Claude Code (pole „Zrobiono w wersji”
i `CHANGELOG.md`) – więc oba bywają rozjechane. Ta grupa serii „Kontrola spójności” (klucze `KS-…`) to **P**. Wspólny
format flag, odpowiedzi ☑ i limit 5 nowych flag na przebieg – jak w pozostałych grupach serii (`kontrola-spojnosci*.md`);
poniżej tylko to, co szczególne dla pomysłów. **Statusu pomysłu asystent sam nie zmienia** (decyzja inwestora jest
nadrzędna) – zmienia tylko pole „Zrobiono w wersji”, i to wyłącznie z nagłówka CHANGELOG (P1, P4).

## Reguły

Brane pod uwagę wiersze ze Statusem „Zrobione”, „Do zrobienia” albo „Przeanalizowany” (Nowy, Pytania do mnie, Odłożone,
Odrzucone – pomiń). Wartość pola „Zrobiono w wersji” ze słowem „częściowo” oznacza wdrożenie w częściach – status
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

## Przebieg (w kroku 2; jeden odczyt bazy pomysłów – cała tablica, wszystkie statusy, nie tylko „Nowy”; ten sam wynik służy analizie)

1. **Zastosuj odpowiedzi** na wcześniejsze punkty `KS-P…` (zanim dopiszesz nowe): ☑ przy P2 → Status „Zrobione”; ☑ przy P3 →
   Status „Zrobione” i pole „Zrobiono w wersji” z nagłówka CHANGELOG; dopisek „zostaje” / „częściowo” → nic nie zmieniaj;
   dopisek z wersją przy P1 → wpisz ją w pole. Rozpatrzony punkt idzie do „Przetworzone” z kluczem i dopiskiem „→ KS: <wykonano | zostaje>”.
2. **Wersje z CHANGELOG** – tylko gdy jest kandydat P1, P3 albo P4: `python3 tools/pomysly_wersje.py <n> <n> …` (z folderu repo;
   wypisuje „nagłówki” = jednoznaczne i „tylko w treści” = niejednoznaczne). Bez dostępu do `CHANGELOG.md` (przebieg poza
   repo, Bash niedozwolony, claude.ai) albo gdy nie możesz go przeczytać – pomiń P3 i P4, a P1 zamień na pytanie; P2 działa
   wyłącznie na danych z Notion i zostaje.
3. **Zapisz P1 i P4** (jedna edycja strony pomysłu, tylko pole „Zrobiono w wersji”, format „<plugin> <wersja>[, …]”) – bez pytania,
   bo wartość pochodzi z nagłówka CHANGELOG; są idempotentne (po zapisie wiersz nie jest już kandydatem), więc bez klucza.
   W linii „🤖” i w „Czeka na Ciebie” – licznik „uzupełniono wersje: n”.
4. **Pytania P1/P2/P3** – jedno pytanie = jeden to-do z kluczem `KS-P<n>-<ostatnie 6 znaków ID strony pomysłu>` w Dzienniku
   „❓” (format B, `wpisy/references/pytania.md`), np. `- [ ] POM-8: Status → Zrobione? (pole „Zrobiono w wersji” wypełnione) KS-P2-d1e2f3`;
   ID pomysłu (POM-n) podaj jako wzmiankę strony. Pomiń parę, której klucz jest już w „❓” (czeka) albo w „Przetworzone”
   (rozpatrzona – wyciszenie trwa, dopóki wpis tam jest). Liczy się do wspólnego limitu 5 nowych flag `KS-…` na przebieg.
5. **Licznik** do kroku 8 i linii „🤖”: `rozjazdy: n nowych, m wykonanych` (wspólny dla serii) + „uzupełniono wersje: k” (P1, P4).

## Czego nie robić

- Nie zmieniaj Statusu pomysłu bez ☑ inwestora i nie ruszaj treści strony pomysłu ani „Wymaga ode mnie”.
- Nie zgaduj wersji z treści wpisu CHANGELOG ani z `git log` – tylko nagłówek z numerem POM.
- Nie flaguj pomysłów „Nowy”, „Pytania do mnie”, „Odłożone”, „Odrzucone”; nie flaguj wdrożeń oznaczonych „częściowo”.
- Nie wdrażaj pomysłów i nie analizuj ich w tym kroku – to osobne zadanie kroku 2 (`rozwoj-harnessu`, C).
