# Skrzynka – zapisy z czatu, gdy Notion jest niedostępny

**Kiedy:** w rozmowie nie ma narzędzi Notion (konektor wyłączony, „not connected”), a inwestor chce coś zapisać – wpis z budowy,
notatkę, zadanie, emocję, sprawę dziecka, suplement, wiedzę, pomysł. Nie odmawiaj i nie odsyłaj „zapisz sam w Notion”: zapisz do
Skrzynki, a przebieg godzinowy na Macu przeniesie wpis do Notion (zwykle w ciągu godziny). Odczyty bez Notion: Baza wiedzy
z indeksu, Notatnik i zadania z migawki (`dom-budowa`: `wiedza/references/indeks.md`, sekcja czatu).

**Gdzie:** dokument Claude **„📥 Skrzynka”** (Claude Docs). Link stoi na stronie Notion „🔑 Asystent – dostęp” i w pliku
„🔑 Dostęp asystenta” w wiedzy projektu „Dom”; bez linku – lista artefaktów (tytuł „📥 Skrzynka”); brak dokumentu → utwórz
nowy o tej nazwie z nagłówkami „## Nowe” i „## Przetworzone” (Mac czyta wszystkie dokumenty o tym tytule).

## Zapis (czat na telefonie)

Jedna pozycja listy pod „## Nowe” na sprawę; kilka spraw w wiadomości → kilka pozycji. **Bez pól Notion** – struktura baz
może się zmienić, a bez Notion nie da się jej sprawdzić; telefon pisze, co ma się stać, Mac robi resztę procedurą `wpisy`:

```
- [ ] 2026-10-28 14:10 · <treść dosłownie, słowami inwestora> · Zrobić: <jedno zdanie, co z tym zrobić – „zanotuj jako pytanie do kierownika na stan zero”, „zadanie prywatne na piątek 30.10”, „wpis z dnia na budowie”>
- [ ] 2026-10-28 14:12 · <treść> · Zrobić: <…>
```

- **Treść** dosłownie, jak w Dzienniku – nie streszczaj. **Zrobić** = intencja słowami, z tym, co inwestor powiedział albo co
  wynika z rozmowy (termin jako data, kogo dotyczy, którego etapu). Nie wpisuj nazw pól, statusów ani ID baz.
- Brak danych (data, czego dotyczy, kto) → nie zgaduj: dopisz w tej samej linii `❓ <pytanie z propozycją>`; Mac przeniesie je
  do „❓” w Dzienniku (`wpisy`, krok 4). Czego inwestor nie dopowiedział w rozmowie, nie dopowiadaj za niego.
- Zdjęcia do Skrzynki nie wchodzą – powiedz inwestorowi, że zdjęcie dodaje w Notion albo na Dysku (`dziennik`, plugin dom-budowa).
- Odpowiedź inwestorowi: „Zapisane do Skrzynki (n); w Notion po najbliższym przebiegu, do godziny”. Nie pisz „zapisano w Notion”.

## Opróżnianie (Mac: `przeglad-dnia` A.1 i B.1; w rozmowie „przerób skrzynkę”)

1. Przeczytaj sekcję „Nowe” każdego dokumentu „📥 Skrzynka…” (lista artefaktów → tytuł; brak narzędzia Claude Docs → pomiń
   źródło i napisz „Skrzynka – brak odczytu” w odpowiedzi i w linii „🤖”).
2. Każdą pozycję przetwórz jak wpis Dziennika (`wpisy`, kroki 3–7): obszar według bazy Obszarów, pola według skilla
   docelowego, „Zrobić” z linii to intencja inwestora (termin, adresat, etap) – nadrzędna wobec domysłów, nie wobec schematu bazy.
3. Po zapisie przenieś linię do „## Przetworzone” jako `- [x] ~~…~~ → <gdzie>: <link>` (jedna edycja dokumentu na przebieg);
   niejasna → „❓” w Dzienniku jak w `wpisy` krok 4, w Skrzynce `→ ❓ Dziennik`. Nie usuwaj pozycji.
4. Ślad: w linii „🤖” i w odpowiedzi „Skrzynka n”. „Przetworzone” czyści przegląd tygodnia (pozycje starsze niż 14 dni).
