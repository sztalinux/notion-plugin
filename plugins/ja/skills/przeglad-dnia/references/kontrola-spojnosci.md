# Kontrola spójności (krok 5a wieczornego przeglądu dnia)

Inwestor zmienia statusy i daty ręcznie w Notion, więc powiązane rzeczy rozjeżdżają się po cichu. Ten krok wychwytuje
rozjazdy i **tylko o nich pyta** – bez inwestora niczego nie przestawia (`SKILL.md`, zasady trybu). Wspólny dla serii
„Kontrola spójności”: każda grupa reguł ma w tabeli własny blok (litera), a procedura i format poniżej są wspólne.

## Reguły

| Grupa | Rozjazd | Propozycja w pytaniu (☑ = wykonaj) |
|---|---|---|
| **H1** | zadanie zamknięte (DONE) z relacją Harmonogram, a krok nie jest „Zrobione” i jego koniec Terminu (przy jednodniowym – ta data) jest przed dniem przeglądu | krok Status → „Zrobione” |
| **H2** | krok „Zrobione”, a zadanie z relacją do niego jest otwarte (TO DO, IN PROGRESS, WAITING, BLOCKED) z When ≤ koniec Terminu kroku (zadanie z When po końcu kroku to zwykle czynność następcza – nie flaguj) | zadanie Status → DONE |
| **H3** | krok **nie** „Zrobione”, a otwarte zadanie z relacją ma When po końcu Terminu kroku | zadanie When → koniec Terminu kroku |
| **H4** | krok „Przesunięte”, a zadanie WAITING z relacją ma When przed początkiem Terminu kroku (stary termin „czekam na” po przesunięciu; bywa zgodne z planem – np. dostawa przed startem) | zadanie When → początek Terminu kroku |

Zawsze tylko po ☑ inwestora i **nigdy** nie zmieniaj Terminu ani Pewności terminu kroku (to `harmonogram`, C). Zmiana Statusu
kroku na „Zrobione” i zmiana pola zadania to wykonanie decyzji inwestora, nie decyzja asystenta. Inne grupy serii (zakupy ↔ zadania,
„Porozmawiać z…” ↔ „💬 Do przegadania”) dopisuj jako kolejne wiersze z własną literą.

## Odczyt (tylko widoki – bez SQL i rows, `ja` zasada 3)

1. **Zadania z relacją:** wiersze Obszaru Dom (albo pustego) z kroku 5 przeglądu, które mają niepustą kolumnę Harmonogram
   (widok daje adresy kroków), oraz wiersze widoku „⏳ Czekam na” (`view://3f7f5982-09e7-8126-9825-000cc472cb4d`, mały odczyt)
   z relacją Harmonogram – te ostatnie nie wymagają dziś edycji zadania, bo „czekam na” po przesunięciu kroku zwykle nie jest
   ruszane. Brak takich wierszy w obu źródłach → pomiń cały krok i napisz „spójność: bez zmian”.
2. **Kroki:** widok Harmonogramu „📅 Oś czasu” (`view://3f7f5982-09e7-814f-bb28-000c12b8d4f1`, jeden odczyt; to duży
   wynik, więc czytaj go tylko w kroku 1 niepustym). Dopasuj kroki po adresie; potrzebne: Krok, Status, Termin (od–do).
3. **Odpowiedzi na wcześniejsze flagi:** zaznaczone ☑ i dopiski pod punktami `KS-` w Dzienniku „❓” (krok 3 poniżej).

**Zasięg wieczoru:** H1 i H3 widać tylko, gdy zadanie zmieniono od wczoraj (krok 5); H4 – dla każdego „czekam na” z relacją;
H2 zaczyna się od zmiany po stronie kroku (krok „Zrobione”), której widok zadań nie widzi – wieczorem trafia tylko na zadania
edytowane od wczoraj. Pełny przebieg robi `przeglad-tygodnia` (`dom-budowa`, punkt „Spójność”): dla kroków „Zrobione” czyta
strony zadań z relacji Zadania (pojedynczo, max 15) dla H2 i widok „🏗 ToDo/Doing – Dom” tylko pomocniczo – nie zwraca
wszystkich otwartych zadań.

## Przebieg

1. **Zastosuj zaznaczone odpowiedzi** (zanim dopiszesz nowe flagi): punkt `KS-…` z ☑ → wykonaj propozycję z tabeli (jedna edycja
   wiersza, a przy H1 dopisz w Uwagach kroku „Zrobione – potwierdzone <data> (kontrola spójności)”); dopisek inwestora
   zamiast ☑ → wykonaj dopisek, jeśli jednoznaczny (inaczej zostaw i dopytaj tym samym punktem); dopisek „zostaje” / „zgodne”
   → nic nie zmieniaj. Każdy rozpatrzony punkt idzie do „Przetworzone” z dopiskiem „→ KS: <wykonano | zostaje>” i kluczem.
2. **Znajdź nowe rozjazdy** wg tabeli. Klucz flagi: `KS-<grupa>-<ostatnie 6 znaków ID zadania>` (np. `KS-H2-a1b2c3`).
   Pomiń parę, której klucz jest już w „❓” (czeka) albo w „Przetworzone” (rozpatrzona – wyciszenie trwa, dopóki wpis tam jest;
   przegląd tygodnia archiwizuje po 14 dniach). Max 5 nowych flag na przebieg, reszta „+k” w linii „🤖” – bez zalewu pytań.
3. **Dopisz flagi** do Dziennika „❓ Czeka na Twoją odpowiedź” (format B, `wpisy/references/pytania.md`; to jedna edycja
   razem z resztą zapisów przeglądu – `SKILL.md`, krok 9). Jedno pytanie = jeden to-do, do ok. 12 słów, z kluczem na końcu:
   `- [ ] Krok „<krok>” → Zrobione? (zadanie „<nazwa>” zamknięte) KS-H1-a1b2c3`. Powód i skutek ☑ – w „Szczegóły”
   (stan kroku i zadania: Status, daty; „po ☑ ustawię …”).

## Wynik w przeglądzie

W linii „🤖” i w „Czeka na Ciebie” podaj licznik `rozjazdy: n nowych, m wykonanych` (brak – „spójność: bez zmian”). Nazw zadań
i kroków nie wypisuj w odpowiedzi poza linkami (log zadania).

## Czego nie robić

- Nie flaguj zadań bez relacji do kroku (to nie rozjazd, tylko brak powiązania – to wyłapuje `zadania`, D).
- Zadanie zamknięte dziś przez wpis z Dziennika („zrobiłem X”) flaguj tak samo: `zadania` zostawia status kroku procedurze
  `harmonogram`, więc nic go nie synchronizuje.
- Nie zakładaj nowych zadań i nie zmieniaj terminów kroków; krok zależny przesuwa `harmonogram` (C), nie ten krok.
