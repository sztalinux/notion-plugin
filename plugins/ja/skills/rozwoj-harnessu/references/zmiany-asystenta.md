# Baza „🤖 Zmiany asystenta” – jedna baza zamiast HZ, POM i ZP

Baza: Notion → 🤖 Asystent AI → „🤖 Zmiany asystenta”, `collection://<ID-NOWEJ-BAZY>` (uzupełnia migracja).
Zastępuje trzy bazy: „Zmiany do harnessu” (HZ), „Pomysły na rozwój” (POM) i „🧯 Znane problemy” (ZP) – stare są w 🗄 Archiwum,
tylko do wglądu.

## Pola

| Pole | Typ | Dla | Skąd (stara baza) |
|---|---|---|---|
| Zmiana | tytuł | wszystkie | HZ „Zmiana”, POM „Pomysł”, ZP „Problem” |
| Rodzaj | select: Zasada / Pomysł / Usterka | wszystkie | HZ → Zasada, POM → Pomysł, ZP → Usterka |
| ID | tekst: `HZ-n` / `POM-n` / `ZP-n` | wszystkie | dotychczasowe ID wiersza (bez zmian numeru) |
| Status | select (niżej) | wszystkie | mapowanie niżej |
| Typ zmiany | select: Nowa zasada, Poprawka, Nowa procedura, Zmiana struktury Notion / Excela, Usunięcie | Zasada | HZ „Rodzaj” |
| Plugin | select: dom-budowa, ja | Zasada | HZ „Plugin” |
| Procedura | select (opcje jak w HZ) | Zasada | HZ „Procedura” |
| Treść do wdrożenia, Dlaczego | tekst | Zasada | HZ |
| Obszar | multi_select (suma opcji POM i ZP) | Pomysł, Usterka | POM / ZP „Obszar” |
| Nakład | select: S / M / L | Pomysł | POM |
| Wymaga ode mnie | tekst | Pomysł | POM |
| Przeanalizowano | data | Pomysł | POM |
| Skąd, Co zrobić | tekst | Usterka | ZP |
| Pierwszy raz, Ostatnio | data | Usterka | ZP |
| Zrobiono w wersji | tekst | wszystkie | HZ „Wdrożono w wersji”, POM „Zrobiono w wersji”, ZP „Rozwiązano w wersji” |
| Data wdrożenia | data | wszystkie | HZ „Data wdrożenia” (POM, ZP – puste) |
| Zgłoszono | data | wszystkie | „Zgłoszono” (czas utworzenia) starego wiersza – kopiowany, bo nowy wiersz ma nową datę utworzenia |

**ID nowego wiersza** (pole tekstowe, bez automatu): prefiks wg Rodzaju i numer o 1 większy od najwyższego numeru tego
prefiksu w bazie (jedno zapytanie przed zapisem). Ten sam ID nigdy nie jest używany drugi raz.

## Status

| Status | Zasada (HZ) | Pomysł (POM) | Usterka (ZP) |
|---|---|---|---|
| Nowy | pusty | Nowy, pusty | Nowy, pusty |
| Czeka na mnie | – | Pytania do mnie | Czeka na mnie |
| Przeanalizowany | – | Przeanalizowany | – |
| Do zrobienia | **Do wdrożenia** | Do zrobienia | – |
| W toku | – | – | W toku |
| Zrobione | Wdrożone | Zrobione | Rozwiązany |
| Odłożone | – | Odłożone | – |
| Odrzucone | Odrzucone | Odrzucone | Zostaje |

Zasada z pustym Statusem albo „Do zrobienia” = do wdrożenia (obowiązuje w rozmowach od razu). Usterka „Odrzucone” = dawne
„Zostaje” (nie warto naprawiać).

## Widoki

- „📥 Zasady do wdrożenia” – Rodzaj = Zasada, Status pusty albo Do zrobienia (skrzynka; liczba idzie do ☀️ Dziś).
- „💡 Tablica pomysłów” – Rodzaj = Pomysł, tablica wg Statusu.
- „🧯 Otwarte usterki” – Rodzaj = Usterka, Status inny niż Zrobione i Odrzucone, sortuj Ostatnio malejąco.
- „Wszystko” – tabela.

## Wpis inwestora „asystent: …”

We „📝 Wpisach” inwestor pisze „asystent: …”. Przebieg wybiera Rodzaj: reguła sposobu pracy („zawsze…”, „nie rób…”) → Zasada;
nowa funkcja, automatyzacja → Pomysł; coś, co miało działać, a nie działa → Usterka. Niepewne → ❓ pod wpisem z propozycją.
