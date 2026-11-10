# Zasady pisania procedur (SKILL.md)

Format: otwarty standard Agent Skills (agentskills.io) – czytają go Claude (Cowork, Code), Gemini CLI,
Codex i inne narzędzia. Trzymaj się go, żeby harness był przenośny.

## Frontmatter

```yaml
---
name: nazwa-katalogu        # kebab-case, identyczna z nazwą katalogu
description: Co robi. Używaj, gdy <sytuacje>, <frazy użytkownika w cudzysłowie>.
---
```

`description` decyduje, czy agent w ogóle sięgnie po procedurę. Pisz konkretne frazy, jakich
używasz na co dzień („wkleja ofertę”, „ile wydaliśmy”), nie ogólniki.

## Treść

- Tryb rozkazujący, do agenta: „Wczytaj…”, „Zapisz…”, nie „Możesz…”.
- Kolejność: cel (1–2 zdania) → procedura w krokach → format wyniku → czego nie robić.
- SKILL.md krótki (do ~150 linii); schematy, listy, szablony → `references/`.
- Bez nazw narzędzi konkretnego dostawcy („użyj notion-create-pages”) – opisuj działanie
  („utwórz wiersze w bazie Notatnik budowy jednym wywołaniem”). Agent sam dobierze narzędzie.
- Repo jest publiczne: bez danych osobowych i projektowych (nazwiska, firmy, adresy, działki, kontakty, kwoty).
  Przykłady na zmyślonych danych. Bez danych zmiennych (kwoty ofert, statusy) – te są w Notion i w arkuszu kosztorysu. Harness zawiera procedury,
  identyfikatory i schematy.
- Każda reguła ma powód, jeśli nie jest oczywisty („…bo zatwierdzeń Notion nie da się pominąć”).

## Test procedury

Po zmianie przetestuj na prawdziwym przykładzie z historii (np. wcześniejsza oferta):
nowa rozmowa → wklej wejście → sprawdź, czy agent sięgnął po procedurę i czy wynik ma właściwy format.
Jeśli nie sięgnął – popraw `description`.
