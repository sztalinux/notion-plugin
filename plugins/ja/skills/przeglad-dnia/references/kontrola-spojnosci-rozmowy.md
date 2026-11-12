# Kontrola spójności: zadanie rozmowy („Porozmawiać z…”) ↔ temat w „💬 Do przegadania” (krok 5c wieczornego przeglądu dnia)

Temat rozmowy leży na stronie osoby (dziecko – `dziecko`, partnerka – „💞 Relacja”), a po świeżym zdarzeniu powstaje też zadanie
„Porozmawiać z <dzieckiem / partnerką> o <temat>” (`ja`, zasada 9). Inwestor zamyka zadanie ręcznie w Notion, a temat zostaje
na liście do przegadania. Ten krok o tym przypomina **pytaniem** – bez inwestora niczego nie przestawia (`SKILL.md`, zasady trybu).
Format flag i klucze `KS-…` są wspólne z serią „Kontrola spójności” (`kontrola-spojnosci.md`, „Przebieg”): ta grupa to **R**.

**Zadanie rozmowy** = zadanie z Obszarem **Dziecko** albo **Prywatne**, którego Name zawiera w dowolnym miejscu (bez względu
na wielkość liter i odmianę) „porozmawia”, „pogada” albo „rozmow” (np. „Porozmawiać z…”, „pogadać o…”, „Rozmowa – …”,
„Umówić rozmowę z…”). Zasada 9 tworzy nazwę „Porozmawiać z…”, ale inwestor dopisuje też ręczne warianty –
reguła łapie wszystkie. Inny Obszar → nie flaguj.

## Reguła

| Grupa | Rozjazd | Propozycja w pytaniu (☑ = wykonaj) |
|---|---|---|
| **R1** | zadanie rozmowy ma Status **DONE**, a na stronie osoby jest pasujący temat w „💬 Do przegadania” bez dopisku „przegadane” | pod tematem zagnieżdżony punkt `<dd.mm.rrrr> – ✅ przegadane (zadanie zamknięte)` |

Zadanie zamknięte nie znaczy, że temat jest wyczerpany (rozmowa mogła się odbyć tylko częściowo) – stąd pytanie, nie automat.
**ARCHIVED** (odpuszczone) nie flaguj: odpuszczenie zadania nie znaczy, że rozmowa się odbyła.
Po ☑ **nic nie przenoś i nie usuwaj** – temat zostaje na swoim miejscu z dopiskiem (`dziecko`, pkt 2 – zagnieżdżony punkt z datą;
sekcja 🗄 Archiwum nie przyjmuje nowych wpisów, a „💞 Relacja” jej nie ma). Przenoszenie do archiwum to ręczna decyzja inwestora.

## Dopasowanie zadania do tematu (brak relacji – dopasuj ostrożnie)

1. Strona osoby wynika z treści zadania (odnośnik do strony dziecka albo „💞 Relacja”; zasada 9 go wymaga). Brak odnośnika:
   Obszar Dziecko → strona dziecka; Obszar Prywatne → bez flagi (licznik „niedopasowane”).
2. Kandydat = punkt „💬 Do przegadania” bez dopisku „przegadane”, który ma co najmniej jedno wspólne słowo kluczowe (≥ 4 litery,
   bez odmiany po końcówkach, bez słów rozmowy z definicji wyżej) z częścią nazwy zadania po „o” (brak „o” – z całą nazwą)
   **i** którego data (`dd.mm.rrrr` na początku) to When zadania − 3 dni (±1 dzień); przy ręcznym wariancie (nazwa nie zaczyna się
   od „Porozmawiać z”) wystarczy data nie późniejsza niż When.
3. **Dokładnie jeden** kandydat → flaga. Zero albo kilku → bez flagi, tylko licznik „niedopasowane: n” w odpowiedzi (log) –
   przy wspólnych imionach i podobnych tematach nie zgaduj.

## Odczyt

1. **Wieczór:** wiersze z kroku 5 przeglądu (zmienione od północy czasu polskiego) ze Statusem DONE, które są zadaniami rozmowy
   (wyżej) – także te zamknięte wpisem z Dziennika (`zadania` zostawia temat na liście). Brak takich wierszy →
   pomiń cały krok (bez odczytu stron osób).
2. Dla każdego (max 3 na przebieg): pobierz stronę zadania (odnośnik do osoby) i sekcję „💬 Do przegadania” strony osoby
   (jedna strona = jeden odczyt; `dziecko` – `241f5982-09e7-8023-9793-fa12d36bdb2e`, „💞 Relacja” –
   `3faf5982-09e7-81ac-9071-d72e1036eb1f`).
3. **Odpowiedzi na wcześniejsze flagi** `KS-R-…`: zaznaczone ☑ → wykonaj propozycję (jedna edycja strony osoby, punkt zagnieżdżony
   pod tematem, nie zmieniaj tekstu tematu); „zostaje” / „zgodne” → nic. Rozpatrzone idą do „Przetworzone” z kluczem
   i dopiskiem „→ KS: <wykonano | zostaje>” (jak w `kontrola-spojnosci.md`, „Przebieg” 1).

**Pełny przebieg tygodniowy** (`przeglad-tygodnia-osobisty`, krok 2): zadania rozmowy zamknięte w tygodniu (widok
„🤖 Tydzień – prywatne”) – te same reguły, żeby wyłapać zamknięte w dni, których wieczór nie widział.

## Flaga i wynik

- Klucz: `KS-R-<ostatnie 6 znaków ID zadania>`; pomiń parę, której klucz jest w „❓” albo w „Przetworzone”. Limit 5 flag na
  przebieg razem z innymi grupami serii (reszta „+k”).
- Pytanie w „❓” Dziennika (format B, `wpisy/references/pytania.md`), jeden to-do do ok. 12 słów, bez treści tematu:
  `- [ ] „<początek nazwy zadania>” zamknięte – oznaczyć temat jako przegadany? (<wzmianka strony osoby>) KS-R-a1b2c3`.
  W „Szczegóły”: data zadania i że po ☑ dopiszesz zagnieżdżony punkt „✅ przegadane”. **Treść tematu to dane prywatne** –
  w pytaniu i w logu tylko link do strony osoby i liczby, bez cytowania tematu.
- Licznik `rozjazdy: n nowych, m wykonanych` wspólny z innymi grupami (linia „🤖”, „Czeka na Ciebie”).

## Czego nie robić

- Nie flaguj zadań bez odnośnika do strony osoby ani bez jednoznacznego tematu.
- Nie przenoś, nie usuwaj i nie przepisuj tematów; nie zakładaj nowych zadań; nie zamykaj zadań.
- Nie oceniaj, czy rozmowa była potrzebna – tylko pytaj o porządek na liście.
