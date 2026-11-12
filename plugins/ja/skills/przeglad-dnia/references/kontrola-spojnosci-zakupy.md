# Kontrola spójności: zakup ↔ zadanie „Kupić X” (krok 5b wieczornego przeglądu dnia)

Inwestor zmienia statusy zakupów i zamyka zadania ręcznie w Notion; wpisy „kupiłem X” z Dziennika synchronizują obie bazy
(`zadania`, sekcja „Zakupy” pkt 4 i B.2), ręczne zmiany – nie. Ten krok wychwytuje rozjazdy. **Bezpieczne uzupełnienie (Z4) robi sam,
decyzje i daty zostawia inwestorowi** w pytaniach „❓” (`SKILL.md`, zasady trybu bez inwestora). Zakres: baza 🛒 Zakupy (prywatne).
🧱 Zakupy budowy nie mają relacji Zadanie ani „Kupione dnia” – poza zakresem.

Format flag i klucze `KS-…` są wspólne z serią „Kontrola spójności” (kolejne grupy = własna litera): ta grupa to **Z**.

## Reguły

| Grupa | Rozjazd | Skutek |
|---|---|---|
| **Z1** | zakup Kupione albo Odpuszczone, a powiązane zadanie (relacja Zadanie) otwarte (TO DO, IN PROGRESS, WAITING, BLOCKED, PLANNED, ON HOLD) | flaga; po ☑: zadanie DONE (zakup Kupione) albo ARCHIVED (Odpuszczone) |
| **Z2** | zadanie Kategorii Zakup zamknięte, a zakup z relacją do niego nadal „Do kupienia” (DONE: „Do kupienia” lub „Zamówione” nie flaguj – zamknięcie zadania „Zamówić X” jest zgodne) | flaga z wyborem: DONE → Kupione albo Odpuszczone; ARCHIVED → Odpuszczone |
| **Z3** | zakup Kupione bez „Kupione dnia”, **zmieniony od wczoraj** (ostatnia edycja wiersza wczoraj albo dziś, czas polski); starsze zostają puste – bez flagi | flaga z proponowaną datą (dzień ostatniej edycji zakupu); po ☑: Kupione dnia = ta data |
| **Z4** | zakup Kupione albo Odpuszczone ma research RES-n o Statusie innym niż Zamknięty, a zakup nie ma otwartego zadania (Z1 czeka → poczekaj) | **sam**: research Status „Zamknięty” |

Z2 pyta, bo zamknięcie zadania nie musi znaczyć, że kupiono (mogło być odpuszczone) – zakupu nie przestawiaj bez ☑.
Z3 pyta, bo data edycji nie musi być dniem zakupu (inwestor mógł oznaczyć zakup później); dzienna kontrola widzi tylko świeże
zmiany, więc starszych zakupów bez daty nie flaguj i nie uzupełniaj. Z4 to uzupełnienie zgodne z `wpisy` (zasada „Research”:
zakup już Kupione → research Zamknięty).
Nigdy nie zmieniaj Status zakupu ani zadania bez ☑ inwestora; nie zakładaj zadań; nie ruszaj Terminu zakupu.

## Odczyt (tylko widoki, `ja` zasada 3)

1. Widok bazy 🛒 Zakupy „🤖 Spójność – zamknięte zakupy (przegląd dnia)” – ID w `ja/references/notion-mapa.md`: Kupione i
   Odpuszczone dodane w ostatnim miesiącu (Dodano), z kolumnami Kupione dnia, Zadanie, Research, Uwagi i czasem ostatniej edycji
   (brak kolumny w widoku → właściwości strony zakupu, tylko dla wierszy Kupione bez daty i z Research). Daje Z1, Z3, Z4.
2. „🛒 Do kupienia” (wynik z kroku 6 użyj ponownie) i „📦 Zamówione – czekam” – tylko wiersze z niepustą relacją Zadanie (Z2).
3. Stan powiązanych zadań i researchów: strony z relacji, pojedynczo, **razem max 12 stron na przebieg** (zaczynaj od
   wierszy z relacją Zadanie, potem Research; reszta następnego dnia). Status zadania i jego edycja to właściwości strony.
4. Odpowiedzi na wcześniejsze flagi: ☑ i dopiski pod punktami `KS-Z…` w Dzienniku „❓”.

Brak wierszy z relacją, brak świeżego Z3 i brak Z4 do uzupełnienia → pomiń resztę i napisz „zakupy: bez zmian”.
**Zasięg:** zakupy dodane dawniej niż miesiąc temu kontrola pomija (świadomie – okno miesiąca trzyma koszt odczytu stałym; zakup
pilny / z zadaniem zwykle zamyka się szybciej). Zadanie i zakup bez relacji nie są rozjazdem (to wyłapuje `zadania`).

## Przebieg

1. **Zastosuj zaznaczone odpowiedzi** (zanim dopiszesz nowe flagi): punkt `KS-Z…` z ☑ → wykonaj skutek z tabeli (jedna edycja
   wiersza; przy zmianie zakupu na Kupione ustaw też Kupione dnia = dzień ostatniej edycji zadania, a w treści strony zakupu
   dopisz linię „<data>: Kupione dnia z daty edycji zadania (kontrola spójności)”); dopisek inwestora zamiast ☑ → wykonaj, jeśli
   jednoznaczny, inaczej dopytaj tym samym punktem; „zostaje” / „zgodne” → nic nie zmieniaj. Rozpatrzony punkt idzie do
   „Przetworzone” z dopiskiem „→ KS: <wykonano | zostaje>” i kluczem.
   Z3 z ☑ → Kupione dnia = proponowana data + w treści strony zakupu „<data>: Kupione dnia potwierdzone (kontrola spójności)”
   (Uwag nie ruszaj); dopisek z inną datą → ta data.
2. **Uzupełnienie (Z4)** – od razu, jedna edycja wiersza: research Status „Zamknięty” + w treści strony RES-n „<data>:
   zamknięty – zakup <Kupione|Odpuszczone> (kontrola spójności)”. Gdy Uwagi zakupu zawierają „przeniesione do 🧱” (rzecz
   przeszła do 🧱 Zakupów budowy), dopisek brzmi „zamknięty – zakup przeniesiony (kontrola spójności)”, nie „Odpuszczone”.
   Linia RES-n w „❓” Dziennika zniknie przy zabezpieczeniu kroku 7 przeglądu.
3. **Nowe rozjazdy (Z1, Z2, Z3)** wg tabeli. Klucz: `KS-<grupa>-<ostatnie 6 znaków ID zakupu>` (np. `KS-Z1-a1b2c3`). Pomiń parę, której
   klucz jest już w „❓” (czeka) albo w „Przetworzone” (rozpatrzona; wyciszenie trwa, dopóki wpis tam jest). **Max 5 nowych
   flag na przebieg łącznie ze wszystkimi grupami KS**, reszta „+k” w linii „🤖”.
4. **Dopisz flagi** do Dziennika „❓ Czeka na Twoją odpowiedź” (format B, `wpisy/references/pytania.md`; jedna edycja
   z resztą zapisów przeglądu – `SKILL.md`, krok 9). Jedno pytanie = jeden to-do, do ok. 12 słów, klucz na końcu:
   `- [ ] Zadanie „<nazwa>” → DONE? (zakup Kupione) KS-Z1-a1b2c3`. Z2 z DONE = dwa to-do pod jednym punktem, „zaznacz jedno”:
   `- [ ] Zakup „<rzecz>” → Kupione` i `- [ ] Zakup „<rzecz>” → Odpuszczone` + klucz; przy ARCHIVED jeden to-do (Odpuszczone).
   Z3: `- [ ] Zakup „<rzecz>” – Kupione dnia <dd.mm.rrrr>? KS-Z3-a1b2c3`.
   Powód i skutek ☑ – w „Szczegóły” (stan zakupu i zadania, daty).

## Wynik w przeglądzie

Do linii „🤖” i „Czeka na Ciebie” (krok 8–9) wlicz flagi do licznika `rozjazdy: n nowych, m wykonanych`, a uzupełnienia osobno:
`zakupy: zamknięto n researchów` (brak wszystkiego – „zakupy: bez zmian”). Nazw nie wypisuj w odpowiedzi
poza linkami (log zadania).

## Czego nie robić

- Nie przestawiaj Status zakupu ani zadania bez ☑ (także gdy wpis w Dzienniku zamknął tylko jedno z pary – to robi `zadania`).
- Nie zamykaj researchu, gdy zadanie zakupu jest otwarte (Z1 najpierw) ani research „Pytania do mnie” zakupu, który nadal
  „Do kupienia”.
- Nie wpisuj nazw rzeczy ani cen do repo – przykłady tylko z zmyślonych danych.
