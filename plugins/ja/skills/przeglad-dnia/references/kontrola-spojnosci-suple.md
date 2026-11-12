# Kontrola spójności: suplement Buy = tak przy statusie BREAK / SUSPENDED (krok 6 wieczornego przeglądu dnia)

Inwestor przełącza Status suplementu w Notion ręcznie (`suple` zmienia go tylko na wpis „przerwa od X” / „odstawiam X”),
a pole **Buy** zostaje zaznaczone. Bez tej kontroli licznik „kupić: n suplementów” i zadanie „Zamówić suple” zawyżają zakupy
o suplementy, których inwestor w tej chwili nie bierze. Ta grupa serii „Kontrola spójności” (klucze `KS-…`) to **S**.
Tylko odczyt i pytanie w „❓” – **asystent sam nie zmienia pola Buy ani Statusu**.

## Reguła

| Grupa | Rozjazd | Skutek |
|---|---|---|
| **S1** | suplement z Buy = tak i Status BREAK albo SUSPENDED | **nie wliczaj** do licznika „kupić” ani do zadania „Zamówić suple”; pokaż osobno jako „do sprawdzenia”; jedno zbiorcze pytanie „❓”; po ☑ Buy = nie |

Status TAKING i TO START z Buy = tak to zwykły zakup (bez zmian). Suplement po „wracam do X” ma Status TAKING – wtedy Buy
znów się liczy.

## Przebieg (w kroku 6, na wierszach już odczytanych z Buy = tak – bez dodatkowego odczytu)

1. **Podziel wiersze z Buy = tak** po Statusie: BREAK / SUSPENDED → „do sprawdzenia”, reszta → zwykłe „do kupienia”.
   Licznik „kupić: n suplementów”, lista do zadania „Zamówić suple” i jego treść liczą wyłącznie zwykłe. Zadanie „Zamówić suple”
   już istnieje i wymienia suplement, który jest teraz „do sprawdzenia” → nie usuwaj go sam; dopisz w „Czeka na Ciebie” linię
   „suple: zadanie wymienia wstrzymany <nazwa>” (nazwę podaj tylko jako wzmiankę strony wiersza).
2. **Zastosuj odpowiedź na wcześniejsze pytanie** (zanim dopiszesz nowe): punkt `KS-S1-…` z ☑ → Buy = nie dla wskazanych
   suplementów (jedna edycja na wiersz; Status, When, Last break, dawki i ceny bez zmian); dopisek inwestora zamiast ☑ („zostaw”,
   „kupuję mimo przerwy”) → nic nie zmieniaj, a suplement od tej pory wlicz do zakupów (wyciszenie: wpis w „Przetworzone”
   z kluczem, jak niżej). Rozpatrzony punkt idzie do „Przetworzone” z dopiskiem „→ KS: <Buy odznaczone | zostaje>”.
3. **Pytanie „❓”** (format B, `wpisy/references/pytania.md`; jedna edycja Dziennika z resztą zapisów przeglądu – krok 9):
   **jedno zbiorcze pytanie na przebieg**, nawet gdy „do sprawdzenia” jest kilka suplementów; to-do w jednym punkcie:
   `- [ ] Odznaczyć Buy? <nazwa 1>, <nazwa 2> (Status BREAK/SUSPENDED) KS-S1-<klucz>` – zaznaczenie = tak, odznacz Buy wszystkim
   wymienionym; wybór pojedynczych → dopisek pod punktem. Propozycja domyślna: tak.
   Klucz: `KS-S1-` + ostatnie 6 znaków ID pierwszego (alfabetycznie) suplementu na liście; lista zmienia się → nowy klucz.
   Pomiń pytanie, gdy ten sam zestaw ma klucz już w „❓” (czeka) albo w „Przetworzone” (rozpatrzony – dopóki wpis tam jest,
   pozycje nadal pokazuj w „Jutro – plan” jako „do sprawdzenia”, ale nie pytaj ponownie). Liczy się do wspólnego limitu
   5 nowych flag na przebieg (`KS-…`).
4. **Wynik w przeglądzie** (krok 8–9): w „Jutro – plan” `kupić: n suplementów (+ k do sprawdzenia)`; do licznika „spójność /
   rozjazdy” w linii „🤖” dolicz 1, gdy dopisano pytanie, a „wykonanych” – gdy Buy odznaczono.

## Czego nie robić

- Nie zmieniaj Buy, Status ani innych pól suplementu bez ☑ inwestora (osobny przypadek: zamknięte zadanie „Zamówić suple” – `przeglad-dnia`, B.6).
- Nie zakładaj ani nie zamykaj zadań z tego powodu; nie ruszaj bazy 🛒 Zakupy.
- Nie wypisuj nazw suplementów poza linkami / wzmiankami w logu zadania (dane o zdrowiu – `ja`, zasada 5; w odpowiedzi „bez treści emocji i notatek o dziecku – liczby i linki”).
