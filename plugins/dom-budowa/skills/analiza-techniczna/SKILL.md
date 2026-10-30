---
name: analiza-techniczna
description: Analiza dokumentacji budowy (projekt techniczny, rysunki KT/arch., opinie geotechniczne, umowy z wykonawcami, karty produktów, normy) i odpowiedzi na pytania techniczne. Używaj, gdy użytkownik dołącza PDF/rysunek projektu lub umowę, pyta „czy to dobrze zaprojektowane”, „co z tego wynika”, „jak to wykonać”, „ile tego potrzeba”, o technologię (hydroizolacja, drenaż, beton, zbrojenie, izolacje, instalacje), albo prosi o listę pytań do projektanta.
---

# Analiza techniczna

Cel: rzetelna odpowiedź z odniesieniem do dokumentu, oddzielająca fakty od szacunków,
z listą rzeczy do wyjaśnienia z projektantem. Asystent nie zastępuje konstruktora ani kierownika budowy.

## Procedura

1. **Ustal źródła:** który dokument, która wersja/data, które arkusze. Najpierw sprawdź, czy
   istnieje już analiza tego zakresu (Notion, dokumenty projektu – np. „Analiza konstrukcji – stan zero”)
   i buduj na niej, zamiast zaczynać od zera. Przy pytaniach o technologię sprawdź też Bazę wiedzy
   (drogą z `wiedza/references/pytanie-do-bazy.md` – najpierw karta) i Rejestr sprzeczności – rozstrzygnięcia inwestora mają pierwszeństwo przed opinią ogólną.
2. **Czytaj dokument, nie pamięć:** cytuj arkusz i element (np. „KT.01, ściana oś B”, „opis 1.5”).
   Rozbieżność opisu z rysunkiem → wskaż obie wartości, nie wybieraj po cichu.
3. **Oznacz każdy wniosek:** `[projekt]` / `[szacunek]` (z założeniami i dokładnością, np. ±10–15%) /
   `[opinia]` (rekomendacja, praktyka wykonawcza).
4. **Normy i przepisy:** powołuj się tylko na konkretne, znane zapisy (numer normy/rozporządzenia, paragraf).
   Gdy nie masz pewności – napisz, co sprawdzić i gdzie, zamiast cytować z pamięci.
   Aktualne ceny, dostępność produktów, zmiany przepisów → wyszukaj i podaj źródło z datą.
5. **Ilości:** pokaż wzór i dane wejściowe (wymiary z arkusza), zaokrąglenie i zapas osobno.
   Jeśli ilość trafia do kosztorysu – przekaż ją procedurze `koszty` jako zmianę parametru z podanym źródłem.
6. **Wyjaśnienia z projektantem:** numerowana lista (kontynuuj numerację istniejącej listy, jeśli jest),
   każdy punkt: problem → dlaczego ważne → proponowane rozwiązania → adresat.
   Zapisz je procedurą `notatka` (Typ „Pytanie”, Do kogo = Konstruktor/Architekt/Geotechnik).

## Format wyniku (dla analizy dokumentu)

Użyj `references/szablon-analizy.md`. Dla krótkiego pytania technicznego: odpowiedź w 3–8 zdaniach
+ „Na czym to opieram” (1–3 źródła) + ewentualne „Do potwierdzenia z …”.

## Praca własna – „jak to zrobić”

Gdy inwestor ma wykonać coś sam („jak ułożyć izolację poziomą”, „jak murować pierwszą warstwę”): odpowiedz jako instrukcja
wykonania, nie wykład. Format: **warunki wstępne** (co musi być gotowe, pogoda) → **materiały z ilościami i zapasem**
(→ `zakupy`) → **narzędzia** (co kupić, co wynająć) → **kroki** z kontrolą po każdym (pomiar, tolerancja, zdjęcie) →
**typowe błędy** (z Bazy wiedzy, Rodzaj „Błąd do uniknięcia”) → **BHP** (wykop, wysokość, prąd, pył, ciężary) →
**kiedy przerwać i zapytać** (kierownik, konstruktor). Parametry z projektu cytuj z arkuszem; praktykę oznacz `[opinia]`.
Czas pracy podaj w widełkach – wchodzi do porównania „sam czy ekipa” (`oferta`).
Bez wymiarów (długość ścian, powierzchnie) podaj ilości na jednostkę (m, m²) i poproś o wymiary albo plik. Kontrole po
każdym kroku bierz z `etap/references/odbiory.md`, a zdjęcia przed zakryciem – jak w `etap`, sekcja B.

## Umowy z wykonawcami

Sprawdź: zakres (lista etapów 01–14 / co NIE jest w cenie), ryczałt vs obmiar, harmonogram płatności
po odbiorach, zatrzymanie 5–10%, kary umowne, gwarancja i rękojmia, odbiory częściowe z kierownikiem,
roboty dodatkowe (stawki), kto zapewnia media i materiał. Wskaż ryzykowne zapisy i zaproponuj brzmienie.
Pełna lista kontrolna: `oferta/references/umowa.md`.
Na końcu dodaj, że to nie jest porada prawna i przy dużej kwocie warto, by umowę przejrzał prawnik.

## Granice

- Nie zatwierdzaj zmian konstrukcyjnych (grubości, zbrojenie, posadowienie, zmiana materiału ścian) –
  przygotuj argumenty i pytania dla konstruktora.
- Bezpieczeństwo (wykopy > 1,5 m, skarpy, stemplowanie, prąd) – zawsze wskaż ryzyko wprost.
