# Skrzynka – zapisy z czatu, gdy Notion jest niedostępny

**Kiedy:** w rozmowie nie ma narzędzi Notion (konektor wyłączony, „not connected”), a inwestor chce coś zapisać – wpis z budowy,
notatkę, zadanie, emocję, sprawę dziecka, suplement, wiedzę, pomysł. Nie odmawiaj i nie odsyłaj „zapisz sam w Notion”: zapisz do
Skrzynki, a przebieg godzinowy na Macu przeniesie wpis do Notion (zwykle w ciągu godziny). Odczyty bez Notion: Baza wiedzy
z indeksu, Notatnik i zadania z migawki (`dom-budowa`: `wiedza/references/indeks.md`, sekcja czatu).

**Gdzie:** dokument Claude **„📥 Skrzynka”** (Claude Docs). Link stoi na stronie Notion „🔑 Asystent – dostęp” i w pliku
„🔑 Dostęp asystenta” w wiedzy projektu „Dom”; bez linku – lista artefaktów (tytuł „📥 Skrzynka”); brak dokumentu → utwórz
nowy o tej nazwie z nagłówkami „## Nowe” i „## Przetworzone” (Mac czyta wszystkie dokumenty o tym tytule).

## Zapis (czat na telefonie)

Jedna pozycja listy pod „## Nowe” na sprawę; kilka spraw w wiadomości → kilka pozycji:

```
- [ ] 2026-10-28 14:10 · budowa · <treść dosłownie, słowami inwestora> · Pola: Typ=Pytanie; Etap=Stan zero; Do kogo=Kierownik budowy; Priorytet=Ważne · Procedura: notatka
- [ ] 2026-10-28 14:12 · zadanie · <treść> · Pola: Obszar=Prywatne; When=2026-10-30; Priority=Medium; Kto=Ja · Procedura: zadania
```

- **Obszar** = obszar Dziennika (budowa, dziennik budowy, emocja, praca, zadanie, zakup, dziecko, suple, wiedza, pomysł, inne).
- **Pola** = to, co ustaliłbyś przy zapisie do Notion według procedury docelowej (schematy: `notatka/references/notion-schematy.md`,
  `zadania`, `emocje`, `dziecko`, `suple`). Myślenie robi czat na telefonie, Mac tylko zapisuje – ale pola są podpowiedzią,
  nie rozkazem: Mac sprawdza duplikat i pola według skilla (`wpisy`, krok 5).
- Brak danych (data, czego dotyczy, kto) → nie zgaduj: dopisz w tej samej linii `❓ <pytanie z propozycją>`; Mac przeniesie je
  do „❓” w Dzienniku (`wpisy`, krok 4).
- Zdjęcia do Skrzynki nie wchodzą – powiedz inwestorowi, że zdjęcie dodaje w Notion albo na Dysku (`dziennik`, plugin dom-budowa).
- Odpowiedź inwestorowi: „Zapisane do Skrzynki (n); w Notion po najbliższym przebiegu, do godziny”. Nie pisz „zapisano w Notion”.

## Opróżnianie (Mac: `przeglad-dnia` A.1 i B.1; w rozmowie „przerób skrzynkę”)

1. Przeczytaj sekcję „Nowe” każdego dokumentu „📥 Skrzynka…” (lista artefaktów → tytuł; brak narzędzia Claude Docs → pomiń
   źródło i napisz „Skrzynka – brak odczytu” w odpowiedzi i w linii „🤖”).
2. Każdą pozycję przetwórz jak wpis Dziennika (`wpisy`, kroki 3–7) – pola z linii jako podpowiedź, duplikat i pola wg skilla.
3. Po zapisie przenieś linię do „## Przetworzone” jako `- [x] ~~…~~ → <gdzie>: <link>` (jedna edycja dokumentu na przebieg);
   niejasna → „❓” w Dzienniku jak w `wpisy` krok 4, w Skrzynce `→ ❓ Dziennik`. Nie usuwaj pozycji.
4. Ślad: w linii „🤖” i w odpowiedzi „Skrzynka n”. „Przetworzone” czyści przegląd tygodnia (pozycje starsze niż 14 dni).
