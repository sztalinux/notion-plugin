# Jeden przepływ wydatku: kosztorys budowy + budżet domowy

**Jedyne źródło tej reguły.** `koszty` (B.5a), `budzet` (A), `wpisy/references/skrzynka.md` i mapa procedur w `ja` tylko tu
odsyłają. Wydatek na budowę trafia do kosztorysu (kolejka 💸) **i** do budżetu domowego jako `Inwestycja › Dom` (skrót `dom`),
chyba że inwestor powie inaczej.

## 1. Gdzie zapisać

| Wydatek | Kosztorys (kolejka 💸, `koszty` B) | Budżet domowy (`budzet` A, `wpis.py`) |
|---|---|---|
| Na budowę, zapłacony (Płatność = Zrealizowane) | tak | tak: `"<kwota>[, konto], dom[, opis]" --budowa <id strony 💸> --id <id strony 💸>` |
| Na budowę, „Do zapłaty” | tak | **nie teraz** – zapis przy przejściu na Zrealizowane (pkt 3; ten sam `--id`, bez dubla) |
| Na budowę + „tylko kosztorys” / „nie do budżetu” | tak | nie; w Notatkach strony 💸 „bez budżetu (prośba inwestora)” |
| Na budowę + inna kategoria budżetu („to z wesela”) | tak | tak, wskazany skrót kategorii zamiast `dom` |
| Zwrot otrzymany (Rodzaj = Zwrot, `koszty` B.7a) | tak | tak: `"+<kwota>[, konto], dom, zwrot <opis>" --budowa <id> --id <id>` – „+” = wpływ; zamknięcie miesiąca odejmuje go od wydatku na dom („zwrot pomniejsza zakup”) |
| Wycena (`koszty` B2), Plan (B3) | tak | nigdy |
| Prywatny (nie budowa) | nie | tak, kategoria wg skrótów (`budzet` A) |

„Na budowę” rozpoznajesz jak w `koszty` B (materiał, ekipa, usługa, formalności dla domu). Niepewne → ❓ „Budowa czy
prywatne? (propozycja: …)”.

## 2. Konto (unikanie dubla przy zamknięciu miesiąca)

- Strona 💸 ma Sposób = Gotówka → dopisz `--gotowka` (gotówka, osobny wiersz przy zamknięciu – jak dotąd).
- Sposób = Przelew / Karta / BLIK albo pusty, a we wpisie nie ma konta → **nie podawaj konta**: `wpis.py` z `--budowa` sam weźmie
  `konto_budowy` z `ustawienia.json` (w folderze danych budżetu, poza repo). Konto z wyciągiem = przy zamknięciu tylko
  podpowiedź dla transakcji z wyciągu (dopasowanie: kwota do złotówki, ±4 dni), bez drugiego wiersza.
- Konto podane we wpisie („150, z, dom”) – zostaje.
- **Brak klucza `konto_budowy`** → `wpis.py` zapisze gotówkę (jak dotąd) i wypisze uwagę. Wtedy jeden blok 🔔 we „Wpisach”
  (`wpisy/references/pytania.md`, C; klucz `konto-budowy` – aktualizuj, nie dubluj; odpowiedź obsługuje nocny przebieg): „Wskaż konto, z którego płacisz za
  budowę (wpiszę je do ustawień budżetu)”. Jednorazowo w tym samym bloku lista wpisów z `budowa` zapisanych na gotówce
  w bieżącym miesiącu (`python3 tools/budzet/wpis.py lista RRRR-MM`, tylko daty, kwoty i ID – bez opisów) z pytaniem, czy je
  przepisać na to konto. **Danych nie zmieniaj bez odpowiedzi.** Po odpowiedzi (przebieg albo Claude Code):
  `python3 tools/budzet/wpis.py ustaw-konto-budowy <skrót konta>`, a przepisanie zatwierdzonych = `wpis.py dodaj` z tym samym `--id`
  i skrótem konta w treści; blok → „Przetworzone”.
- Wydatek prywatny bez szczegółów – bez zmian (gotówka drugiej osoby, `budzet` A).

## 3. Kanały

- **Mac – przebieg albo Claude Code:** pkt 1–2 od razu, po zapisie strony 💸 (ID strony = `--id` i `--budowa`).
- **Telefon (claude.ai bez Notion):** każdy wydatek – budowa i prywatny – do Skrzynki słowami inwestora z polem
  „Zrobić: wydatek …” (`wpisy/references/skrzynka.md`); Mac stosuje pkt 1–2 przy przeniesieniu.
- **„Do zapłaty” → „Zrealizowane”:** nocny przebieg (`przeglad-dnia`, B) przegląda strony 💸 zmienione od wczoraj z Płatność =
  Zrealizowane, Rodzaj wydatek lub zwrot, bez „bez budżetu” w Notatkach; brak wpisu o ich ID w `wpis.py lista RRRR-MM` (miesiąc
  daty zapłaty) → zapis wg pkt 1–2. Ten sam `--id` nie dubluje, więc powtórka jest bezpieczna. (Decyzja: logika po stronie
  przebiegu, nie w `wydatki.py sync` – sync to narzędzie arkusza kosztorysu i nie zna wyjątków z pkt 1, np. innej kategorii.)
