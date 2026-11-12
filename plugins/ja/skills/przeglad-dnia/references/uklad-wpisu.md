# Układ wpisu przeglądu – dzień i tydzień

Dotyczy strony **☀️ Dziś** (plan dnia – sekcja D; to ją inwestor czyta rano) i czterech przeglądów: dnia (`przeglad-dnia`, B.8 –
historia planu), dnia budowy (`budowa`, „Wieczorem”, plugin dom-budowa), tygodnia osobistego (`przeglad-tygodnia-osobisty`)
i tygodnia budowy (`przeglad-tygodnia`, plugin dom-budowa). Cel: inwestor rano na telefonie w 30 sekund widzi, co pilne
i co go czeka – bez ściany tekstu.

## A. Zwijany nagłówek – jeden zapis

Każdy wpis przeglądu to zwijany nagłówek h2 na górze strony (najnowszy pierwszy), cała treść jest **w nim**:

```
<toggle heading="h2">
Przegląd dnia – wtorek 10.11.2026

**⚠ Na teraz**

- Po terminie: <wzmianka zadania> (od 7.11)
</toggle>
```

- Tytuł w linii zaraz po `<toggle heading="h2">`, treść po jednej pustej linii, bez wcięć; `</toggle>` w osobnej linii.
  Bez pustej linii tuż po otwarciu i tuż przed zamknięciem.
- **Nigdy** `## Tytuł {toggle="true"}`, `<details>` / `<summary>` ani zwykły nagłówek `##` z treścią pod spodem – Notion
  zapisuje znacznik dosłownie w tytule, a treść ląduje obok nagłówka zamiast pod nim (tak zepsuł się wpis z 08.11.2026).
- Zwijany blok bez nagłówka (blok dnia w „Przetworzone”, „Szczegóły” pod pytaniem) – ten sam zapis bez atrybutu: `<toggle>`.

**Sprawdzenie przed zapisem** (tanie, zawsze): tekst zaczyna się od `<toggle heading="h2">`, kończy `</toggle>`, liczba
otwarć `<toggle` równa się liczbie zamknięć i nigdzie nie ma `{toggle`, `<details`, `<summary`. Wpis dopisz na górze strony
(wstawienie na początku), nie zmieniaj starszych wpisów. Wynik zapisu bez ostrzeżeń → koniec; pełnego odczytu strony po
zapisie nie rób – strony przeglądów są długie, a przebieg wieczorny ma być tani.

**Naprawa raz w tygodniu:** przegląd tygodnia czyta i tak ostatnie wpisy dzienne – nagłówek dnia poza blokiem zwijanym
albo znacznik w tytule popraw punktowo (zamiana dokładnie tego fragmentu na ten sam tekst w `<toggle heading="h2">`,
tytuł bez znacznika); w linii „Porządki” wpisu tygodnia dopisz „naprawione nagłówki: n”.

## B. Treść

- **Sekcja = pogrubiona etykieta w osobnym akapicie, pod nią lista punktów.** Jedna sprawa = jeden punkt, do ok. 120 znaków
  (jedna–dwie linie na telefonie); szczegół w podpunkcie, nie w nawiasie ani po średniku.
- **Najważniejsze na górze:** „⚠ Na teraz” (po terminie, czeka na Ciebie, decyzje), potem „Jutro”, dopiero potem „Dziś”
  i liczby. Pusta sekcja → pomiń ją; cały dzień pusty → jeden punkt „Spokojny dzień – bez zmian” (plus linia budowy).
- Jedna rzecz = jedna wzmianka (link) – bez powtarzania nazwy w nawiasie obok wzmianki. Przy długich listach max 5 pozycji,
  reszta „+k”.
- **Informacje techniczne** (nieudany odczyt, limit zapytań, brak narzędzia, „nie sprawdzono”) – tylko w jednej linii
  kursywą na samym końcu wpisu: `_Odczyty: widok „🗓 Tydzień (7 dni)” nie odpowiedział; emocje – nie sprawdzono._`
  Nigdy w środku sekcji. Wszystko się udało → bez tej linii.
- Treść emocji i notatek o dziecku – tylko liczby (zasady przeglądów bez zmian).

## C. Szablony (przykłady zmyślone)

Przegląd dnia – sprawy osobiste (`przeglad-dnia`, B.8) = **historia planu dnia**: ta sama treść co strona ☀️ Dziś (sekcja D),
w zwijanym nagłówku h2 „Plan dnia – <dzień tygodnia> <data planu>”, bez zakładek: każda zakładka to pogrubiona etykieta
(„**🧭 Przegląd**”, „**🏗 Budowa**”, „**🏠 Prywatne**”, „**💼 Praca**”, „**📊 Wczoraj**”), pod nią jej punkty; najważniejsze z ramki –
pierwszy akapit wpisu. Rozkminka (B.2a) – osobna etykieta „**🧠 Rozkminka: <temat>**” na końcu, przed linią odczytów.

Przegląd dnia budowy (`budowa`, „Wieczorem”, krok 3) – te same zasady, sekcje w tej kolejności: **⚠ Na teraz** (po terminie,
SP i pytania czekające na decyzję), **Jutro – plan** (z linią „⚠️ Pogoda jutro” tylko przy przekroczonym progu – `etap/references/pogoda.md`), **Dziś**, **Decyzje i pytania** (SP domknięte dziś), **🧠 Rozkminka**
(tylko przekazana z `przeglad-dnia`, B.2a), linia odczytów. Tytuł: „Przegląd dnia budowy – <dzień tygodnia> <data>”.

Przeglądy tygodnia – szablony w ich procedurach, zapisane według sekcji A i B: zwijany nagłówek h2 z tytułem tygodnia,
każda etykieta z szablonu jako osobny pogrubiony akapit z punktami pod spodem.

## D. Strona ☀️ Dziś – plan dnia

Strona `416f5982-09e7-81b3-b96d-ddd19086bc5b` (najwyższy poziom Private, w Ulubionych). Wieczorny przebieg **nadpisuje całą
treść** (zamiana treści strony, bez jej odczytu – nie ma podstron) planem na **dzień planu = dzień przeglądu + 1** (dzień
przeglądu z linii „Teraz” / „dzień przeglądu” w poleceniu, nie z zegara – przebieg kończy się czasem po północy). Ręczny przebieg
w ciągu dnia (prośba „plan dnia”) = plan na dziś, z dopiskiem „(ręczne)” w podpisie ramki.

**Zasady:**
- Dzień planu i 6 kolejnych = „najbliższe 7 dni”; „po terminie” = When / Termin przed dniem planu i niezakończone. Widoki
  Notion liczą „dziś” po swojemu – zakres utnij sam.
- Każda sprawa to wzmianka (link) – klikalna; obok tylko to, czego nie widać w nazwie (godzina, „od 8.11”, kto). Jedna sprawa
  w zakładce 🧭 raz: co jest w ramce, nie powtarzaj w „Najbliższe 7 dni”. W zakładkach obszarów może się powtórzyć.
- Znaczniki obszaru po wzmiance w 🧭: 🏗 budowa · 🏠 prywatne · 👪 dziecko · 💼 praca. 🔒 = krok bez odwrotu, ⏰ = termin zamówienia.
- Limity: ramka max 3 punkty; każda lista max 5, reszta „+k” z odesłaniem do zakładki; „Najbliższe 7 dni” max 4 na dzień,
  dni bez spraw pomiń. Pusta sekcja → pomiń; pusta zakładka → jedna linia („Nic na najbliższe dni.”).
- Emocje i notatki o dziecku – tylko liczby; zadania dziecka nazwą (to zadania, nie notatki).
- Weekend (dzień planu sob./nd. – przebieg w piątek i sobotę): **pracy nie rób** – bez odczytów Jiry, pliku pracy i WORK,
  zakładki 💼 nie ma, w 🧭 nic z pracy. Plan na poniedziałek (przebieg w niedzielę) – pełna zakładka, „Wczoraj” = piątek.
- Informacje techniczne (nieudany odczyt) – tylko kursywą na końcu zakładki 📊.

**Ramka – co do niej trafia (max 3, w tej kolejności):** krok bez odwrotu albo bramka w dniu planu · sprawa z godziną w dniu
planu · zamówienie z terminem ⏰ w dniu planu · zadanie Highest / High po terminie · zadanie z When = dzień planu. Nic → „Spokojny
dzień – nic pilnego.”

**Szablon** (przykłady zmyślone; `<…>` – wzmianki). Każda sekcja = pogrubiony akapit i punkty pod nim (sekcja B) – w każdej zakładce, nigdy jedna linia z kilkoma sekcjami:

```
<callout icon="☀️" color="blue_bg">
**Czwartek 13.11 – plan dnia**

- 🔒 <krok: betonowanie płyty> – ekipa od 7:00; odbiór zbrojenia był wczoraj
- 10:00 <zadanie: wizyta u lekarza>
- ⏰ <zakup budowy: beton> – zamówić dziś

_Przegląd z 12.11, 22:51 · historia: <wzmianka 📆 Przeglądy dzienne>_
</callout>

<tabs>
<tab icon="🧭">
Przegląd

**⚠ Po terminie (3)**

- <zadanie> 🏠 – od 8.11
- <zadanie> 🏗 – od 10.11
- +1 w zakładkach

**❓ Czeka na Ciebie (4)**

- <SP-n> 🏗 – decyzja przed betonem (do 18.11)
- 2 pytania pod wpisami (<wzmianka 📝 Wpisy>) · 1 w ❓ Dziennika

**📅 Najbliższe 7 dni**

- **pt 14.11** · <zadanie> 🏗 · <zadanie> 💼
- **pn 17.11** · ⏰ <zakup budowy> · <zadanie> 👪
</tab>
<tab icon="🏗">
Budowa

**Dziś na budowie**

- <krok> – ekipa, 7:00 · dostawa: <zakup> 

**Najbliższe kroki**

- 🔒 <krok> – 19.11 (szacunek) · kto

**Do zamówienia**

- ⏰ <zakup budowy> – zamówić do 17.11

**Decyzje i pytania**

- <SP-n> – czeka na Ciebie (do 18.11)

Szczegóły dnia budowy: <wzmianka wpisu z „📆 Przeglądy dzienne – budowa”>
</tab>
<tab icon="🏠">
Prywatne

**Dziś**

- 10:00 <zadanie> · <zadanie dziecka> 👪

**W tygodniu**

- **sob 15.11** · <zadanie>

**Kupić**

- 4 suplementy – <zadanie „Zamówić suple”> (13.11) · <zakup> (termin 14.11)

**Gotowe do przeczytania**

- <RES-n> – rekomendacja w jednym zdaniu · <POM-n> przeanalizowany
</tab>
<tab icon="💼">
Praca

**Na dziś**

- <zadanie> (projekt) – w toku
- <zadanie> (projekt) – Highest

**Na daily**

- Wczoraj: <zadanie>, <zadanie>
- Dziś: <zadanie>
- Blokery: <zadanie WAITING> – czekam na odpowiedź

**Pozostałe otwarte: 6** (najstarsze bez ruchu: <zadanie>)
</tab>
<tab icon="📊">
Wczoraj

- Wpisy: 4 przetworzone (zadania 2, zakupy 1) · emocje: 2 wpisy · praca: dzień zapisany
- Zadania: zamknięte 2, zmienione 3, uzupełniono 1 · spójność: 1 flaga · komunikaty 🔔: 0
</tab>
</tabs>
```

**Zakładka 💼 Praca** (POM-27; tylko gdy dzień planu to pon.–pt.) – trzy źródła, każde opcjonalne (brak → jedna linia kursywą w 📊 „Praca: Jira – brak odczytu”):
- **Jira** – serwer MCP `atlassian` (tylko odczyt); strona i `cloudId` w `.dom/praca.json` w folderze budowy (poza repo – nazw
  projektu ani klienta nie wpisuj do repo). Dwa zapytania, pola tylko `summary, status, priority, issuetype, updated`, format
  markdown: (1) `assignee = currentUser() AND statusCategory != Done ORDER BY priority DESC, updated DESC`, max 15;
  (2) `assignee = currentUser() AND updated >= "<od>" ORDER BY updated DESC`, max 10 (`od` z pliku niżej). Opisów zgłoszeń nie czytaj.
- **Kod i PR-y** – plik `.dom/praca/dzien.json` (skrypt `AI/automaty/praca.py` przed przebiegiem): `commity` od początku
  ostatniego dnia roboczego (`od`), `pr_moje`, `pr_do_recenzji` (z `moj_glos`), `pr_zamkniete`, `bledy`.
- **Lista WORK** – widok bazy 🔨 TASKS „🤖 Plan dnia – otwarte i zamknięte w 7 dni” (ID w `ja/references/notion-mapa.md`;
  **treści samej strony WORK nie czytaj**) i TASKS z Obszar = Praca (krok B.6).

Łączenie: jedna sprawa = jedno zgłoszenie (numer `ABC-123` z Jiry, commita, gałęzi, PR-a i pola Ticket w WORK); pokazuj
numer i tytuł, link do zgłoszenia albo PR-a. Sekcje:
- **Na dziś** (max 5): PR do mojej recenzji bez mojego głosu → moje zgłoszenia w toku (statusy kategorii „In Progress”,
  np. w realizacji, code review – z PR-em i jego stanem) → Highest / High otwarte → WORK IN PROGRESS i TO DO z When ≤ dzień planu.
- **Na daily** – gotowa ściąga do powiedzenia: **Wczoraj** = zgłoszenia z commitami lub zmianą od `od` + PR-y utworzone /
  zamknięte + DONE z WORK (po jednym punkcie na zgłoszenie, max 5) · **Dziś** = pierwsze 2–3 z „Na dziś” ·
  **Blokery** = zgłoszenia On Hold / WAITING w WORK, moje PR-y czekające na recenzję dłużej niż 2 dni robocze.
- **PR-y** (tylko gdy są): moje otwarte z liczbą głosów i celem gałęzi; do mojej recenzji.
- **Pozostałe otwarte: n** (licznik zgłoszeń Jiry i WORK).
- **Tydzień** – tylko gdy dzień planu to poniedziałek: zgłoszenia otwarte wg statusu (liczby), PR-y czekające, 3 najważniejsze
  na tydzień (najwyższy priorytet, potem najdłużej bez ruchu).

Nic w Jirze, Azure DevOps ani WORK nie zmieniaj. Treści kodu, opisów i komentarzy nie przepisuj do Notion – tylko numery,
tytuły, statusy i linki.
