# Pogoda przy robotach – progi i prognoza na jutro

Jedno miejsce dla progów pogodowych: `etap` (A.6, B.6), `harmonogram` („Pogoda”) i wieczorny przegląd budowy
(`budowa`, „Wieczorem”, krok 2) czytają stąd. Progi to typowa praktyka `[opinia]` – **do potwierdzenia z kierownikiem
budowy i kartą produktu**; projekt i karta producenta mają pierwszeństwo. Gdy Baza wiedzy ma konkretniejszą informację
(karty `karty --do`, `wiedza/references/pytanie-do-bazy.md`), podaj ją z WI-x zamiast poniższej tabeli. Nie wymyślaj progów
spoza tej listy i bazy wiedzy.

## Progi (ostrzegaj, gdy prognoza je przekracza)

| Robota | Ostrzeżenie, gdy | Co zaproponować |
|---|---|---|
| Betonowanie, murowanie, rdzenie, wieńce | temperatura (w dzień lub w nocy) poniżej ok. +5 °C; opad ulewny w trakcie | domieszki, osłony, maty – decyzja z kierownikiem; albo przesunięcie |
| Beton po wylaniu (pielęgnacja min. 7 dni) | mróz w nocy; upał (powyżej ok. +25–30 °C) | osłona folią/matą; w upał betonowanie rano i polewanie |
| Hydroizolacja ścian (masy, folie w płynie) | deszcz lub wilgotne podłoże w dzień kroku i do związania warstwy (wg karty); temperatura poniżej progu z karty | przesunięcie; osłona folią |
| Zasypka, wykop | deszcz w dniu kroku i dzień wcześniej (grunt spoisty się rozmacza); mróz (zamarznięty grunt nie zagęszcza się) | przerwa i odwodnienie; przesunięcie |
| Tynki zewnętrzne, elewacja | temperatura poniżej ok. +5 °C; deszcz; silne słońce lub wiatr (zbyt szybkie wysychanie) | przesunięcie; siatki osłonowe |
| Dach (pokrycie, membrana) | deszcz; silny wiatr (praca na wysokości) | przesunięcie; membrana jako zabezpieczenie tymczasowe |

Robota spoza tabeli (np. wnętrza po zamknięciu bryły) – bez ostrzeżeń pogodowych.

## Prognoza na jutro (wieczorny przegląd budowy)

Tylko gdy jutro jest krok Harmonogramu z robotami na budowie (Termin = jutro lub trwa jutro, Status inny niż „Zrobione”,
Kto = Ekipa albo Sam, robota z tabeli wyżej). Inaczej nie szukaj prognozy – przebieg ma być tani.

1. **Miejscowość** weź ze ściągi (Notion → DOM → „📐 Dane projektu”). Do wyszukiwania w sieci podaj **tylko miejscowość** –
   bez adresu, numeru działki i innych danych. Miejscowości w ściądze brak → pomiń prognozę, dopisz linię
   „pogoda: brak miejscowości w ściądze” (jedno ostrzeżenie, bez zadania).
2. **Prognoza** z sieci (aktualne źródło z podaniem nazwy i godziny odczytu), na jutro: temperatura min. i maks., opady
   (mm / prawdopodobieństwo), wiatr. Oznacz `[internet]` – to prognoza, nie fakt. Brak wyniku → „pogoda: nie udało się pobrać
   prognozy”, bez ponawiania i bez blokowania reszty przeglądu.
3. **Porównaj z progami** dla robót jutra. Linia w sekcji „Jutro – plan” wpisu budowy:
   `Pogoda jutro [internet, <źródło> <godzina>]: <min>–<maks> °C, opady <…>, wiatr <…> – <OK dla <robota> | ⚠️ <robota>: <próg przekroczony> → <propozycja>>`.
   Krok „bez odwrotu” z przekroczonym progiem = ostrzeżenie na górze „Jutro – plan” (razem z przypomnieniem bramki wg `etap`, B).
4. Przegląd niczego nie przesuwa i nie zakłada zadań – to informacja dla inwestora; przesunięcie kroku robi `harmonogram`
   na jego polecenie.
5. W linii skrótu dla przeglądu dnia (`budowa`, „Wieczorem”, krok 4) dopisz „pogoda: ⚠️ …” tylko przy przekroczonym progu.
