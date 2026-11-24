# Jeden przepływ wydatku: kosztorys budowy + budżet domowy

**Jedyne źródło tej reguły.** `koszty` (B.5a), `budzet` (A), `wpisy/references/skrzynka.md` i mapa procedur w `ja` tylko tu
odsyłają. Wydatek na budowę trafia do kosztorysu (kolejka 💸) **i** do budżetu domowego jako `Inwestycja › Dom` (skrót `dom`),
chyba że inwestor powie inaczej.

## 1. Gdzie zapisać

| Wydatek | Kosztorys (kolejka 💸, `koszty` B) | Budżet domowy (`budzet` A, `wpis.py`) |
|---|---|---|
| Na budowę, zapłacony (Płatność = Zrealizowane) | tak | tak: `"<kwota>[, konto], dom[, opis]" --budowa <id strony 💸> --id <id strony 💸>` (Przelew / Karta / BLIK bez konta – nie teraz, z wyciągu, pkt 2) |
| Na budowę, „Do zapłaty” | tak | **nie teraz** – zapis przy przejściu na Zrealizowane (pkt 3; ten sam `--id`, bez dubla) |
| Na budowę + „tylko kosztorys” / „nie do budżetu” | tak | nie; w Notatkach strony 💸 „bez budżetu (prośba inwestora)” |
| Na budowę + inna kategoria budżetu („to z wesela”) | tak | tak, wskazany skrót kategorii zamiast `dom` |
| Zwrot otrzymany (Rodzaj = Zwrot, `koszty` B.7a) | tak | tak: `"+<kwota>[, konto], dom, zwrot <opis>" --budowa <id> --id <id>` – „+” = wpływ; w budżecie własny wiersz z kwotą ujemną (pomniejsza wydatki na dom) |
| Zwrot obiecany (Rodzaj = Zwrot, Płatność „Do zapłaty”) | tak | nie teraz – jak „Do zapłaty” (pkt 3) |
| Wycena (`koszty` B2), Plan (B3) | tak | nigdy |
| Prywatny (nie budowa) | nie | tak, kategoria wg skrótów (`budzet` A) |
| Paragon mieszany (część na budowę, część prywatna) | tak – strona 💸 na część budowlaną | tak, cały paragon: `paragon.py rozpisz … --budowa <id strony 💸>` (`ja/skills/budzet/references/paragony.md`, 4) – część Dom ma ID części paragonu, nie ID strony 💸 |

„Na budowę” rozpoznajesz jak w `koszty` B (materiał, ekipa, usługa, formalności dla domu). Niepewne → ❓ „Budowa czy
prywatne? (propozycja: …)”.

## 2. Konto (unikanie dubla przy zamknięciu miesiąca)

Konto jest tylko w budżecie domowym. W kosztorysie wystarczy Sposób (Gotówka albo Przelew) – konta tam nie zapisuj.
**Brak informacji o sposobie = gotówka** (inwestor napisze, gdy płaci inaczej): na stronie 💸 Sposób = Gotówka, w budżecie
`--gotowka`. Nie pytaj o konto budowy i nie zakładaj o nie 🔔.

- Strona 💸 ma Sposób = Gotówka → dopisz `--gotowka` (gotówka; nadpisuje też konto z treści). Wiersz w arkuszu budżetu:
  od 1.12.2026 w ciągu godziny (automat `arkusz_budzetu.py sync`), starsze – przy zamknięciu miesiąca.
- Konto podane we wpisie („150, z, dom”) – zostaje. Konto z wyciągiem: przy zamknięciu płatność z wyciągu (kwota do złotówki,
  ±4 dni) przypina się do wiersza z wpisu – bez drugiego wiersza.
- Sposób = Przelew / Karta / BLIK, a we wpisie nie ma konta → do budżetu z wpisu **nie zapisuj** (zapis bez konta byłby gotówką
  i dublem): płatność wejdzie z wyciągu przy zamknięciu miesiąca. W Notatkach strony 💸 „budżet – z wyciągu”.
- Wydatek prywatny bez szczegółów – bez zmian (gotówka drugiej osoby, `budzet` A).

## 3. Kanały

- **Mac – przebieg albo Claude Code:** pkt 1–2 od razu, po zapisie strony 💸 (ID strony = `--id` i `--budowa`; paragon mieszany –
  tylko `--budowa`, wiersz wyżej). Wiersz w budżecie od 1.12.2026 w ciągu godziny, starsze przy zamknięciu miesiąca.
- **Telefon (claude.ai bez Notion):** każdy wydatek – budowa i prywatny – do Skrzynki słowami inwestora z polem
  „Zrobić: wydatek …” (`wpisy/references/skrzynka.md`); Mac stosuje pkt 1–2 przy przeniesieniu.
- **„Do zapłaty” → „Zrealizowane”:** nocny przebieg (`przeglad-dnia`, B) czyta widok 💸 „🤖 Zrealizowane – 2 miesiące (budżet)”
  (ID w `budowa/references/notion-mapa.md`; Płatność = Zrealizowane, bez wycen i planów, od najnowszej Daty – baza nie ma daty edycji)
  od góry do pierwszej strony z Datą starszą niż 2 miesiące; pomija „bez budżetu” i „budżet – z wyciągu” w Notatkach; brak wpisu o ich ID w `wpis.py lista RRRR-MM` (lista pokazuje ID z prefiksem `w`) (miesiąc
  daty zapłaty) → zapis wg pkt 1–2. Ten sam `--id` nie dubluje, więc powtórka jest bezpieczna. (Decyzja: logika po stronie
  przebiegu, nie w `wydatki.py sync` – sync to narzędzie arkusza kosztorysu i nie zna wyjątków z pkt 1, np. innej kategorii.)
