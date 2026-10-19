# Asystent inwestora (budowa domu i sprawy osobiste) – instrukcje startowe

Ten plik czyta każdy agent AI pracujący w tym repo (Claude, Gemini, Codex i inne).
Jest celowo krótki: cała wiedza i procedury są w dwóch pluginach – `plugins/ja/skills/` (Dziennik, emocje, zadania,
dziecko, suplementy, przegląd dnia, rozwój harnessu) i `plugins/dom-budowa/skills/` (budowa domu).

## Zanim cokolwiek zrobisz

1. Wczytaj `plugins/ja/skills/ja/SKILL.md` – kontekst ogólny, mapa obszarów i procedur, skrzynka zmian.
   Sprawy budowy: `plugins/dom-budowa/skills/budowa/SKILL.md` – kontekst budowy, zasady pracy, mapa procedur budowy.
2. Dobierz procedurę do zadania (tabela niżej) i wczytaj jej `SKILL.md`.
3. Pliki z `references/` czytaj dopiero wtedy, gdy procedura każe.
4. Sprawdź skrzynkę „Zmiany do harnessu” w Notion (opis: procedura `ja`, sekcja „Na starcie rozmowy”).

| Zadanie | Procedura |
|---|---|
| Oferta / wycena / rozmowa z wykonawcą | `plugins/dom-budowa/skills/oferta/SKILL.md` |
| Excel z kosztorysem, wydatek, faktura, budżet | `plugins/dom-budowa/skills/koszty/SKILL.md` |
| Notatka, ustalenie, decyzja, zadanie → Notion | `plugins/dom-budowa/skills/notatka/SKILL.md` |
| Projekt, rysunki, umowa, norma, pytanie techniczne | `plugins/dom-budowa/skills/analiza-techniczna/SKILL.md` |
| Transkrypcja filmu, artykuł, relacja z rozmowy, sprzeczności „SP-n” | `plugins/dom-budowa/skills/wiedza/SKILL.md` |
| Nowe pliki od projektanta/wykonawcy, paczka dokumentów dla claude.ai | `plugins/dom-budowa/skills/dokumenty/SKILL.md` |
| Start etapu, „co sprawdzić przed betonowaniem”, odbiór, usterki | `plugins/dom-budowa/skills/etap/SKILL.md` |
| Relacja z dnia na budowie, zdjęcia, godziny własne, roboty dodatkowe | `plugins/dom-budowa/skills/dziennik/SKILL.md` |
| Harmonogram, terminy, przesunięcia, „czekam na”, „co mnie czeka” | `plugins/dom-budowa/skills/harmonogram/SKILL.md` |
| Lista zakupów na etap, oferty hurtowni, kiedy zamawiać, dostawa | `plugins/dom-budowa/skills/zakupy/SKILL.md` |
| Luźne wpisy ze strony „📓 Dziennik”: „przerób dziennik”, kilka notatek naraz | `plugins/ja/skills/wpisy/SKILL.md` |
| Emocja, dzień w pracy, podsumowanie emocji | `plugins/ja/skills/emocje/SKILL.md` |
| Zadania prywatne / dziecka / pracy, „zrobiłem X”, „co mam jutro” | `plugins/ja/skills/zadania/SKILL.md` |
| Dziecko: obserwacje, do przegadania, prezenty, zalecenia | `plugins/ja/skills/dziecko/SKILL.md` |
| Suplementy: „kończy się”, „kupiłem”, przerwa | `plugins/ja/skills/suple/SKILL.md` |
| Spotkanie, rozmowa, decyzja: „jutro mam spotkanie z…”, „o co zapytać”, „jak wybrać z kilku” | `plugins/dom-budowa/skills/przygotowanie/SKILL.md` |
| Przegląd tygodnia, „co nowego”, „co czeka na mnie” | `plugins/dom-budowa/skills/przeglad-tygodnia/SKILL.md` |
| Przegląd dnia (wieczorne zaplanowane zadanie): Dziennik, zmiany w zadaniach, pomysły, jutro | `plugins/ja/skills/przeglad-dnia/SKILL.md` |
| Przegląd tygodnia – sprawy osobiste (z odnośnikiem do przeglądu budowy), porządki w Dzienniku | `plugins/ja/skills/przeglad-tygodnia-osobisty/SKILL.md` |
| Zmiana samego harnessu (nowa procedura, poprawka), pomysł na rozwój setupu, „zrób POM-n” | `plugins/ja/skills/rozwoj-harnessu/SKILL.md` |

## Zasady, które obowiązują zawsze

- Pisz po polsku, konkretnie; kwoty zawsze z dopiskiem netto/brutto.
- Fakt z projektu ≠ szacunek ≠ opinia – oznaczaj, co jest czym. Sprawy konstrukcyjne
  bez potwierdzenia w projekcie oznacz „do potwierdzenia z konstruktorem”.
- Zapisy do Notion grupuj tak, żeby inwestor zatwierdzał jak najmniej razy – ale nigdy kosztem
  jakości i kompletności (szczegóły: `plugins/dom-budowa/skills/budowa/SKILL.md`, zasada 6).
- **To repozytorium jest publiczne.** Nigdy nie zapisuj w nim danych osobowych ani danych projektu
  (imiona domowników, nazwiska, firmy, adresy, działki, PESEL, konta, telefony, e-maile, kwoty, notatki, treść wpisów
  Dziennika) – te są w Notion, Excelu i folderze budowy.
- Gdy użytkownik poprawi Twój sposób pracy, zaproponuj zmianę w odpowiednim `SKILL.md`
  (procedura `rozwoj-harnessu`), żeby poprawka działała w kolejnych rozmowach.
