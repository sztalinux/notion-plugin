# Rejestr sprzeczności – jak ADR

Każdy wpis SP to mini-ADR: kontekst → stanowiska → opcje → rekomendacja → **decyzja inwestora** → konsekwencje.
Asystent przygotowuje wszystko do decyzji, ale **nigdy nie wypełnia pola Decyzja sam**.

## Kiedy otworzyć wpis

- Nowe źródło mówi coś innego niż istniejąca wiedza **dla tych samych warunków** (Źródło vs źródło).
- Źródło podważa projekt techniczny (Źródło vs projekt) – priorytet zwykle „Krytyczne” lub „Ważne”.
- Źródło podważa naszą decyzję zapisaną w Notatniku/Rejestrze (Źródło vs nasza decyzja).
- Źródło podważa ofertę lub technologię wykonawcy (Źródło vs oferta wykonawcy).
- Brak sprzeczności, ale jest realny wybór z kompromisami, który trzeba podjąć (Dylemat bez sprzeczności).

Nie otwieraj wpisu dla różnic w szczegółach bez znaczenia praktycznego (np. 8 vs 10 cm zakładu, gdy obie wartości mieszczą się w wymaganiach) – zapisz wtedy obie wartości w Szczegółach wiedzy.

## Wypełnienie przy zgłoszeniu

| Pole | Treść |
|---|---|
| Dylemat | pytanie w jednym zdaniu („Taśma pęczniejąca wystarczy w przerwie roboczej przy gruncie spoistym?”) |
| Stanowisko A | dotychczasowe: treść + źródło (WI-x / ZRD-y / projekt KT.0x / decyzja z Notatnika) |
| Stanowisko B | nowe: treść + ZRD-y + fragment z minutą |
| Kontekst naszej budowy | dlaczego to ma znaczenie u nas, czego dotyczy w projekcie i ofertach |
| Opcje | 2–4 opcje z kosztem / ryzykiem / wpływem na harmonogram |
| Rekomendacja asystenta | wybór + uzasadnienie (wiarygodność źródeł, warunki, ryzyko błędu, koszt) |
| Pytanie do inwestora | jedno konkretne pytanie, na które da się odpowiedzieć krótko |
| Status | „Czeka na decyzję” |

## Rozstrzygnięcie – po odpowiedzi inwestora

Odpowiedź inwestora przychodzi trzema drogami: w rozmowie, wpisem „SP-n: …” w Dzienniku (procedura `wpisy`) albo wpisaną
przez niego treścią pola **Decyzja** w Rejestrze (widok „🤖 Decyzja wpisana – do domknięcia”: Decyzja niepusta, Status
„Czeka na decyzję” lub „Do sprawdzenia u projektanta”). Wszystkie trzy domykasz tymi samymi krokami – także w przeglądzie
dnia bez inwestora (szczegóły niżej, „Bez inwestora”).

1. Odpowiedź jasna? Jeśli nie – dopytaj jednym pytaniem.
2. „Zapytam konstruktora/architekta” → Status „Do sprawdzenia u projektanta” + wpis Typ „Pytanie” w Notatniku budowy (Do kogo = adresat). Koniec.
3. Decyzja → uzupełnij: Decyzja (co wybrano), Uzasadnienie (słowa inwestora + argumenty), Data decyzji, Status „Rozstrzygnięte”,
   Konsekwencje (co zmieniono i gdzie). Jeśli źródłem rozstrzygnięcia jest rozmowa (np. z konstruktorem) – dodaj ją do Rozmów i źródeł i podepnij.
4. Wiersze wiedzy: zwycięskie → „Przejrzane”; przegrane → „Nieaktualne” z dopiskiem w Szczegółach „odrzucone w SP-n”
   (jeśli przegrane jest poprawne w innych warunkach – zostaw „Przejrzane” i dopisz warunek).
5. Skutki: decyzja dotycząca naszej budowy → wpis Typ „Decyzja” w Notatniku; zmiana zakresu/kosztu → uwaga do arkusza kosztorysu (`koszty`)
   (procedura `koszty`); temat → aktualizacja „W skrócie” i sekcji „Sprzeczności i rozstrzygnięcia”.
6. Nowy argument przeciw wcześniejszej decyzji → nowy wpis SP ze Stanowiskiem A = stara decyzja (SP-n), a stary dostaje
   Status „Zastąpione” dopiero po nowej decyzji inwestora.

## Bez inwestora – decyzja wpisana w Notion albo w Dzienniku

Przegląd dnia (wieczorem: `budowa`, „Wieczorem”; wpisy „SP-n: …” – każdy przebieg `wpisy`) domyka decyzję, którą inwestor
**sam napisał**. Asystent nadal niczego nie wybiera za niego.

- **Jasna** = da się ją jednoznacznie przypisać do jednej opcji z pola Opcje albo do jednego stanowiska (np. „Niedopuszczalne”
  przy dylemacie „dopuszczalne czy niedopuszczalne” = stanowisko B) albo sama opisuje, co robimy. Wtedy kroki 3–5 wyżej:
  - **Decyzja i Uzasadnienie – słowa inwestora zostają na początku bez zmian**; dopisz po nich ` — = opcja X: <treść opcji
    w jednym zdaniu> (dopisek asystenta, <data>)`. Część opcji, której inwestor wprost nie wybrał (np. zapis w umowie,
    dodatkowy zakup), idzie do Konsekwencji jako propozycja, nie do Decyzji. Puste Uzasadnienie – „(nie podano)” i argumenty
    z Rekomendacji jako „za tym przemawia: …”.
  - Data decyzji = data wpisu w Dzienniku albo data ostatniej edycji wiersza Rejestru; Status „Rozstrzygnięte”.
  - Notatnik: **najpierw istniejący wpis** z tym dylematem (relacja „Karta (Notatnik)”, wzmianka w Kontekście, wyszukiwarka
    2–3 słowa w Notatniku) → Status „Ustalone”, Typ „Decyzja”, dopisek w treści; dopiero gdy go nie ma – nowy wpis Typ „Decyzja”.
  - Wiersze wiedzy, „W skrócie” tematu i sekcja „Sprzeczności i rozstrzygnięcia” – jak krok 4–5.
  - **Bez nowych zadań w TASKS i bez zmian w arkuszu kosztów** – skutki do zrobienia (umowa, zamówienie, pytanie do
    projektanta, pozycja w arkuszu) wypisz w Konsekwencjach jako „do zrobienia (propozycja): …”.
- **Niejasna** (pasuje do kilku opcji, sprzeczna z polem Opcje, „?”, „może”, „raczej”) → nic nie zmieniaj w wierszu;
  pytanie „SP-n: wpisałeś »…« – czy to znaczy opcję X?” z propozycją, w formacie `wpisy/references/pytania.md` (plugin `ja`)
  (w Dzienniku „❓”; wpis „SP-n: …” – okienko pod nim). Ten sam wiersz nie dostaje drugiego pytania, dopóki pierwsze czeka.
- „Zapytam konstruktora / projektanta” w polu Decyzja albo we wpisie → krok 2 (to nie decyzja; pole Decyzja wyczyść
  i przenieś jego treść na początek Konsekwencji z datą).
- Ślad: „SP-n rozstrzygnięte (<opcja>) – <link>” w bloku dnia „Przetworzone” i licznik „SP: n domknięte” w linii „🤖”.
