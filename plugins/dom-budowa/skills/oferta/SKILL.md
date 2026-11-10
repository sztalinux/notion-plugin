---
name: oferta
description: Przyjęcie, rozbicie i ocena oferty wykonawcy budowy (stan zero, SSO i kolejne). Używaj, gdy użytkownik wkleja ofertę, wycenę, PDF, zdjęcie kosztorysu, notatkę z rozmowy telefonicznej z ekipą, pyta „co sądzisz o tej ofercie”, „porównaj oferty / wykonawców”, „jakie pytania zadać wykonawcy o tę ofertę”. Ostateczny wybór i przygotowanie rozmowy finałowej – procedura `przygotowanie`.
---

# Oferta wykonawcy

Cel: każda oferta trafia do danych w jednym formacie, z jawnym zakresem, brakami
i pytaniami – tak, żeby oferty dało się uczciwie porównać.

## Wejście

Tekst, PDF, zdjęcie, notatka z rozmowy (także ustna wycena). Jeśli nie wiadomo, kto
jest wykonawcą lub której fazy dotyczy oferta – zapytaj jednym pytaniem.

## Procedura

1. **Wczytaj stan:** karty w Notion „Porównanie wykonawców”, a liczby – Kosztorys, Etapy i Cennik z kopii arkusza
   (`koszty`, „Gdzie są liczby”; bez kopii porównuj tylko z kartami i zaznacz to w odpowiedzi).
   Sprawdź, czy wykonawca już istnieje (porównuj nazwy bez wielkości liter i form prawnych).
2. **Rozbij ofertę na pozycje** Kosztorysu (`koszty/references/arkusze.md`):
   - robocizna i materiał tej samej firmy = osobne wiersze (Materiał w cenie?: „Nie” / „Tylko materiał”),
   - kwoty netto + stawka VAT; jeśli podano tylko brutto – wpisz brutto i VAT 0%, zaznacz w Uwagach,
   - Obejmuje etapy = numery etapów z `references/etapy.md`, które pozycja pokrywa,
   - wycena ustna → Nr „ustnie RRRR-MM-DD”, Zgodna z projektem „Do sprawdzenia”.
   Niczego nie dopisuj od siebie do zakresu – jeśli czegoś nie ma w ofercie, to tego nie ma.
3. **Sprawdź zakres i zgodność** z `references/etapy.md` (lista etapów i punkty krytyczne projektu):
   - każdy etap: ✓ wyceniony / ◐ w pakiecie bez kwoty / ✗ brak,
   - niezgodności z projektem (np. murowane ściany piwnicy zamiast żelbetu W8) → Zgodna z projektem „Nie” i wyraźnie w podsumowaniu,
   - knock-out i czerwone flagi: Notion → „Wybór wykonawcy – stan zero”, sekcja Runda 1,
   - technologia wykonawcy sprzeczna z Bazą wiedzy lub rozstrzygnięciem SP → wpis w Rejestrze sprzeczności
     (Rodzaj „Źródło vs oferta wykonawcy”, procedura `wiedza`); rozstrzyga inwestor.
4. **Porównaj liczby:**
   - z planem (kosztorys – suma etapów objętych ofertą, ta sama warstwa: robocizna do robocizny),
   - z innymi ofertami na ten sam zakres; braki wyceń z kosztorysu, żeby porównanie było „jabłka do jabłek”,
   - nietypowo niskie/wysokie pozycje (±30% od planu lub mediany ofert) → oznacz do dopytania.
5. **Przygotuj pytania do wykonawcy** – tylko te, na które oferta nie odpowiada.
   Źródło pytań: Notion „Wybór wykonawcy – stan zero” (Rundy 1–3, Umowa). Maksymalnie 10, od najważniejszych.
6. **Zapisz:**
   - arkusz: cena materiału od dostawcy (zł za jednostkę) → wycena w kolejce „💸 Wydatki → arkusz” (`koszty` B2) –
     trafi do Cennika; oferta ekipy (robocizna, transze) nie idzie do Cennika – kwota umowy wchodzi do Etapy
     „Umowa z ekipą” dopiero po podpisaniu (`koszty` C i D); wierszy do wklejania nie podawaj,
   - Notion → baza „Porównanie wykonawców – stan zero”: utwórz/zaktualizuj kartę
     (pola i wartości: `notatka/references/notion-schematy.md`),
   - aktualizuj sekcję „Co już wiem z rozmów i ofert” na stronie „Wybór wykonawcy” jednym wpisem.
   Zapisy do Notion grupuj wg zasady 6 z `budowa`.

## Sam czy ekipa

Gdy etap jest w Excelu oznaczony „Sam” albo inwestor pyta „czy robić to samemu”: zestaw ofertę z wykonaniem własnym –
materiał brutto (23%) + sprzęt (zakup/wynajem) + czas (dni × realne tempo, `[szacunek]`) + ryzyko jakości i brak gwarancji
vs oferta brutto (8% z materiałem) + termin. Podaj różnicę w zł i w dniach pracy; nie decyduj – to wybór inwestora
(zapisz jako Decyzja w Notatniku). Instrukcja wykonania → `analiza-techniczna`, „Praca własna”.
Kwoty podane tylko brutto przelicz na netto wg stawek (8 % usługa z materiałem, 23 % materiał własny). Wynik jako tabela:
pozycja | ekipa | sam – netto, VAT, brutto, sprzęt, dni pracy – i na końcu różnica w zł oraz w dniach.
Wartość własnego czasu w zł podaj tylko, jeśli inwestor ją podał.

## Po wyborze – zakres do umowy

Status „Wybrana” (decyzja inwestora) → przygotuj zakres do umowy wg `references/umowa.md`, sekcja „Zakres do umowy”:
pozycje w cenie, „nie w cenie”, pytania na piśmie, transze powiązane z odbiorami (`etap`). Projekt umowy od wykonawcy
sprawdza `analiza-techniczna`, sekcja „Umowy”.
Po podpisaniu → wiersz w Notion **Umowy i gwarancje** (`collection://60c06f30-7867-435d-8f2e-1e025a3daa5c`): Rodzaj, Strona, Zakres,
Etap, Podpisano, Status „Podpisana”, Dokument (plik w folderze budowy), relacja Kroki (Harmonogram); kwoty i transze – arkusz
(Etapy „Umowa z ekipą”, zapłacone transze jako wydatki – `koszty` D); terminy z umowy → `harmonogram`.

## Wynik w rozmowie

```
**<Wykonawca> – <zakres w 5 słowach>**: <netto> netto (<brutto> brutto), VAT <x>%
Zakres: ✓ 02 05 07 … | ◐ 03 | ✗ 04 10   Zgodność: Tak/Nie/Do sprawdzenia
vs plan: +/-X% (robocizna) | vs najtańsza porównywalna: +/-Y%
Ryzyka: …
Pytania do wykonawcy: 1. … 2. …
```

Potem tabela porównawcza wszystkich aktywnych ofert dla tej fazy (kolumny: wykonawca, zakres,
robocizna netto, materiał netto, braki doliczone z planu, razem porównywalne, zgodność, status).

## Czego nie robić

- Nie wybieraj wykonawcy za użytkownika – rekomenduj z uzasadnieniem wg kryteriów z wagami (Notion, sekcja „Kryteria i wagi oceny”).
- Nie zapisuj telefonów i e-maili nigdzie poza arkuszem Wykonawcy w Excelu.
- Nie zmieniaj statusu oferty na „Wybrana” bez wyraźnej decyzji użytkownika.
