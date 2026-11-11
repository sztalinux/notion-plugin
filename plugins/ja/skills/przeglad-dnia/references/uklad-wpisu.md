# Układ wpisu przeglądu – dzień i tydzień

Dotyczy czterech przeglądów: dnia (`przeglad-dnia`, B.8), dnia budowy (`budowa`, „Wieczorem”, plugin dom-budowa), tygodnia
osobistego (`przeglad-tygodnia-osobisty`) i tygodnia budowy (`przeglad-tygodnia`, plugin dom-budowa). Cel: inwestor rano
na telefonie w 30 sekund widzi, co pilne i co go czeka – bez ściany tekstu.

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
  kursywą na samym końcu wpisu: `_Odczyty: widok „📅 Jutro – wszystko” nie odpowiedział; emocje – nie sprawdzono._`
  Nigdy w środku sekcji. Wszystko się udało → bez tej linii.
- Treść emocji i notatek o dziecku – tylko liczby (zasady przeglądów bez zmian).

## C. Szablony (przykłady zmyślone)

Przegląd dnia – sprawy osobiste (`przeglad-dnia`, B.8; budowę zastępuje jedna sekcja z odnośnikiem):

```
<toggle heading="h2">
Przegląd dnia – wtorek 10.11.2026

**⚠ Na teraz**

- Po terminie: <wzmianka zadania> (od 7.11), <wzmianka zadania> (od 8.11)
- Czeka na Ciebie: 2 pytania pod wpisami (<wzmianka „📝 Wpisy”>), 1 komunikat 🔔, 1 w ❓ Dziennika (w tym spójność: 1)

**Jutro – plan (śr 11.11)**

- 10:00 <wzmianka zadania>
- Kupić: 3 suplementy – zadanie: zamówić suple (13.11); 6 pozycji z zakupów (z terminem: <wzmianka>)

**Dziś**

- Wpisy: 4 przetworzone (zadania 2, zakupy 1, dziecko 1)
- Praca: dzień zapisany · emocje: 2 wpisy

**Zadania (wszystkie obszary)**

- Zamknięte 2: <wzmianka>, <wzmianka>
- W toku / czeka 1 · dodane lub zmienione 3 · z Dziennika 2 · uzupełniono 1 wiersz (Priority)

**Pomysły i research**

- POM-n przeanalizowany – <wzmianka>, rekomendacja: odłożyć
- RES-n gotowy – <wzmianka>

**🏗 Budowa**

- Odbiór zbrojenia zrobiony; jutro betonowanie → <wzmianka wpisu z przeglądu budowy>

**🧠 Rozkminka: pytania na rozmowę z doradcą** (tylko na prośbę z wpisu – `przeglad-dnia`, B.2a)

- Założenie: …
- Pytania: …

_Odczyty: strona dziecka – nie sprawdzono._
</toggle>
```

Przegląd dnia budowy (`budowa`, „Wieczorem”, krok 3) – te same zasady, sekcje w tej kolejności: **⚠ Na teraz** (po terminie,
SP i pytania czekające na decyzję), **Jutro – plan** (z linią „Pogoda jutro” przy robotach – `etap/references/pogoda.md`), **Dziś**, **Decyzje i pytania** (SP domknięte dziś), **🧠 Rozkminka**
(tylko przekazana z `przeglad-dnia`, B.2a), linia odczytów. Tytuł: „Przegląd dnia budowy – <dzień tygodnia> <data>”.

Przeglądy tygodnia – szablony w ich procedurach, zapisane według sekcji A i B: zwijany nagłówek h2 z tytułem tygodnia,
każda etykieta z szablonu jako osobny pogrubiony akapit z punktami pod spodem.
