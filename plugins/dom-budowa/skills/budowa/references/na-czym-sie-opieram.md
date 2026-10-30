# „📚 Na czym się opieram” – źródła odpowiedzi o budowie

Inwestor chce przy każdej odpowiedzi merytorycznej o budowie wiedzieć w skrócie, z jakich tez i źródeł korzystałeś – także
na telefonie (HZ-12, 30.10.2026). Zasada 14 w `budowa/SKILL.md`.

## Kiedy

Każda odpowiedź merytoryczna o budowie: pytanie do bazy wiedzy, analiza techniczna, rada (tryb doradcy), przygotowanie do
spotkania, etap (co sprawdzić, odbiór), zakupy. Nie dotyczy samych zapisów (notatka, dziennik, zadanie), przeglądów
i odpowiedzi organizacyjnych. W dwuwarstwowej odpowiedzi z bazy (`wiedza/references/pytanie-do-bazy.md`, pkt 9) sekcja
kończy i skrót, i rozwinięcie.

## Gdzie i jak długo

Na końcu odpowiedzi, przed blokami domknięcia (🛑 / ✅ / ⏳), osobny nagłówek „📚 Na czym się opieram”. Najwyżej ok. 8–10 linii;
nie powtarzaj treści odpowiedzi. Pomiń punkt, z którego nic nie wziąłeś.

1. **Tezy z bazy** – najważniejsze WI-n, każda z 3–6 słowami treści („WI-101 przerwa robocza – uszczelnienie”).
2. **Źródła** – ZRD-n: tytuł skrócony, autor/kanał (pole Kto), typ autora, wiarygodność, link, gdy jest. Nasze rozmowy
   (konstruktor, architekt, kierownik budowy) w osobnej linii przed twórcami i wykonawcami.
3. **Dokumenty projektu** – nazwa pliku i arkusz/rysunek (przewodnik po dokumentach).
4. **Notatnik / SP** – wpisy i sprzeczności, na których oparłeś ustalenia (numer albo tytuł, Status).
5. **Spoza bazy** – co jest `[opinia]`, a co `[internet]` (nazwa źródła; szczegóły są w sekcji „Z internetu”).

## Skąd wziąć źródła tez

Karta wiedzy i `etap` drukują tezy bez źródeł. Po wyborze tez użytych w odpowiedzi uruchom jedno polecenie (ten sam kanał co karta,
na telefonie z `--db /tmp/wiedza.sqlite`):

```
python3 tools/wiedza.py zrodla WI-101 WI-102 WI-103
```

Wynik jest pogrupowany: „Nasze rozmowy i notatki”, potem wg typu autora, w grupie najpierw źródła wielu tez. Do sekcji weź
2–5 źródeł niosących najwięcej użytych tez i wszystkie nasze rozmowy. `szukaj` bez `--krotko` podaje źródła przy każdej tezie –
tam polecenie niepotrzebne. Kopia indeksu bez polecenia `zrodla` (stary `wiedza.py`) → podaj same numery ZRD z `szukaj --krotko`
albo napisz „źródła: w Notion przy WI-…”.

## „Materiały do tematu”

Gdy inwestor prosi o materiały, źródła albo „co oglądać / czytać” do tematu – pełna lista zamiast skrótu:
`python3 tools/wiedza.py zrodla --temat "NAZWA"` (nazwa tematu albo jej część; kilka pasujących → polecenie wypisze kandydatów).
Pogrupuj: nasi projektanci i nasze rozmowy / kierownicy i inspektorzy / twórcy i kursy / wykonawcy (oraz producenci, inne);
przy każdym tytuł, autor, wiarygodność i link. Linki tylko z pola źródła – nie dopisuj ich z pamięci.
