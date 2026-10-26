---
name: etap
description: Plan, bramki „bez odwrotu” i odbiór etapu budowy (stan zero, SSO, instalacje, wykończenie) – także przy pracach własnych. Używaj, gdy użytkownik mówi „zaczynamy etap”, „ekipa wchodzi w poniedziałek”, „jutro betonowanie / zasypka / tynki”, „co muszę mieć gotowe przed…”, „co sprawdzić zanim…”, „ekipa skończyła, co sprawdzić”, „odbiór”, „usterki”, „zmieniamy etap na SSO”, albo gdy inna procedura (dziennik, oferta, zakupy) sygnalizuje początek lub koniec etapu.
---

# Etap budowy – plan, bramki, odbiór

Cel: żaden krok „bez odwrotu” (betonowanie, zasypka, tynki, wylewki) nie zaczyna się, zanim nie zostaną zamknięte
decyzje, które potem kosztują kucie albo rozkopywanie; a każdy etap kończy się odbiorem z protokołem,
zanim pójdzie za niego płatność. Asystent przygotowuje listy i protokoły – odbiera inwestor z kierownikiem budowy.

## Źródła (czytaj przed każdym trybem)

| Co | Gdzie |
|---|---|
| Kolejność prac i co ustalić przed etapem | Notion → DOM → 🏗 Etap → „🗂 Etapy” → zakładka etapu (`budowa/references/notion-mapa.md`); odhaczone tam punkty przewodnika = zamknięte |
| Kontrola prac krok po kroku (ustalenia, zamówienie, odbiór dostawy, kontrola) | Notion → „✅ Checklista budowy” (`budowa/references/notion-mapa.md`): Etap + Element, Dotyczy nas ≠ Nie; listy „Cała budowa” (beton, zbrojenie, dostawy) przy każdym betonowaniu i dostawie; widok etapu jest też w jego zakładce |
| Bramki stanu zero | Notion → „Stan zero – punkty bez odwrotu” (strona w zakładce 🏗 Etap na DOM, „📄 Strony”) |
| Otwarte sprawy etapu | Notatnik budowy: Etap = ten etap, Status Otwarte / Do omówienia **oraz** wszystkie wpisy Typ „Pamiętać” niezależnie od Statusu, poza „Odrzucone” (mają „Ustalone” – to rzeczy do przypilnowania na budowie, nie sprawy otwarte) |
| Co i jak kontrolować | Baza wiedzy → Informacje: Rodzaj „Kontrola / odbiór”, „Błąd do uniknięcia”, „Kolejność prac” dla etapu; `references/odbiory.md` |
| Parametry projektu | ściąga projektu (`budowa/references/projekt.md`) – grubości, klasy, rzędne, zbrojenie |
| Kto robi (Sam / Ekipa), ilości | Excel: arkusze Etapy i Kosztorys (`koszty/references/arkusze.md`) |
| Zakres umowy z ekipą | Oferty „Wybrana” w Excelu + umowa w folderze budowy (`dokumenty`) |
| Formalności i obecność osób | `references/formalnosci.md` |

## A. Plan etapu („zaczynamy stan zero / SSO”, „ekipa wchodzi za 2 tygodnie”)

1. Zbierz źródła z tabeli. Ustal, które kroki robi ekipa, a które inwestor sam (Excel → Etapy).
2. Wypisz **kolejność kroków z zależnościami**: co musi być skończone (przez kogo) zanim wejdzie następny –
   szczególnie styk praca własna → ekipa (np. „izolacja pozioma i pierwsza warstwa – sam, przed wejściem murarzy”).
3. **Blokady:** otwarte decyzje i pytania z Notatnika, które muszą być zamknięte przed startem – z adresatem i terminem.
4. **Ludzie i terminy:** kierownik budowy (odbiory zbrojenia, wpisy), geotechnik, geodeta, elektryk/hydraulik
   (przepusty, uziom), dostawy betonu/stali – co trzeba umówić i z jakim wyprzedzeniem.
5. **Materiały i sprzęt** do zamówienia na ten etap → procedura `zakupy` (lista z Kosztorysu + wyprzedzenia).
6. **Formalności** (`references/formalnosci.md`) i **pogoda**: ograniczenia temperatury/opadów dla betonu, murowania,
   zasypki, tynków – podaj widełki [opinia] i co zrobić, jeśli prognoza nie pasuje.
7. Zapis: zadania z terminem → TASKS (procedura `notatka`); przy zmianie etapu zaproponuj przestawienie strony DOM
   (`budowa`, zasada 12) jednym zestawem zmian – razem z widokiem Informacji „🎯 Na teraz – <etap>”
   (`view://3f7f5982-09e7-81bf-a377-000c19ce62cc`: nazwa i filtr Etap = nowy etap lub „Cała budowa”; poprzedni etap
   z filtra usuń) i z widokiem „🎯 Na teraz – <etap>” w „✅ Checkliście budowy”
   (`view://3faf5982-09e7-8182-a371-000c5e455e52`: nazwa i filtr Etap = nowy etap) oraz z sekcją „🔴 Do zamknięcia”
   (tytuł i widok `view://ddbaff9a-2f5b-47a5-bf7b-aa031bf88fc8`: nazwa i filtr Etap = nowy etap, „Projekt i formalności”
   zostaje). Zakładki etapów w bloku
   „🗂 Wiedza wg etapu” i widoki etapów checklisty są stałe – nie zmieniaj ich.
8. **Wiedza na ten etap:** z Informacji (Etap = ten etap, Kluczowe i Ważne, Status ≠ Nieaktualne) wybierz to, co zmienia
   plan, bramki albo zamówienia, i wpleć w punkty 2–6 z WI-x – nie jako osobną listę do czytania.

## B. Bramka („jutro betonowanie płyty”, „w czwartek zasypka”, „co sprawdzić zanim…”)

1. Nazwij krok i co po nim jest nieodwracalne (jedno zdanie).
2. Zbuduj checklistę: punkty bramki z Notion + sprawy Notatnika dla tego kroku + nieodhaczone punkty „✅ Checklisty budowy”
   dla elementów tego kroku + kontrole z `references/odbiory.md`
   + parametry z projektu. Każdy punkt ma mieć: **co**, **jak sprawdzić** (pomiar, dokument, zdjęcie), **kto**.
3. Sprawdź też **poprzednie bramki** ze strony „Stan zero – punkty bez odwrotu”: niezamknięty punkt wcześniejszej bramki
   to też blokada tego kroku.
4. Oznacz stan każdego punktu: ✅ zamknięte / ❌ otwarte / ⏭ świadomie pominięte (z powodem – zapisz jako Decyzja).
5. Punkt ❌ o priorytecie Krytyczne → napisz wprost: **„Nie betonować / nie zasypywać, dopóki …”**.
6. **Pogoda na dzień kroku:** temperatura (dzień i noc) i opady – widełki z `references/odbiory.md` `[opinia]`;
   jeśli prognoza nie pasuje, zaproponuj przesunięcie.
7. **Zdjęcia przed zakryciem:** lista ujęć z miarą (od stałych punktów), które mają powstać zanim krok zakryje
   instalacje, zbrojenie, izolację – to jedyna dokumentacja na lata (procedura `dziennik`).
8. Po bramce: odhacz punkty na stronie Notion i w „✅ Checkliście budowy” (Zrobione, wynik w Uwagach), zamknij wpisy
   w Notatniku (status + dopisek), zapisz pominięcia jako Decyzje.

## C. Odbiór („ekipa skończyła płytę”, „odbieram hydroizolację”, „są usterki”)

1. Wejście: relacja, zdjęcia, pomiary, protokół od ekipy, wpisy kierownika. Ustal, który etap i jaki zakres umowy.
2. Lista kontrolna: punkty Faza „Kontrola” z „✅ Checklisty budowy” dla tego elementu + `references/odbiory.md`
   + wymagania z projektu + zakres z oferty „Wybrana”
   (czy wykonano wszystko, co w cenie). Dla pracy własnej – ta sama lista, bez zakresu umowy.
3. Protokół (tabela): element | wymaganie i źródło (`[projekt]` / norma / `[opinia]`) | wynik | usterka | termin usunięcia | kto.
4. Zaproponuj wynik: **odebrane / odebrane warunkowo (lista usterek) / nieodebrane** – decyduje inwestor
   z kierownikiem budowy; asystent nie odbiera.
5. Zapis: usterki → Notatnik (Typ „Ryzyko” lub „Pytanie”, Do kogo = Ekipa, Kiedy = termin) i TASKS; wpis z odbioru →
   procedura `dziennik`; dokumenty (WZ betonu, atesty stali, karty produktów, protokoły prób) → folder budowy (`dokumenty`).
6. **Płatność za etap dopiero po odbiorze** – przekaż do `koszty` (transza wg umowy, zatrzymanie), z linkiem do protokołu.
7. **Harmonogram i gwarancja:** krok w Harmonogramie → Status „Zrobione”; odbiór końcowy umowy → w Umowach i gwarancjach
   Odbiór = data protokołu, Gwarancja do / Rękojmia do (z umowy; rękojmia ustawowo 5 lat dla budynku, jeśli umowa jej
   nie wyłącza – `[opinia]`, sprawdź umowę), Status „Odebrana”.

## Wynik w rozmowie

```
**<Etap / krok> – <tryb: plan / bramka / odbiór>** (<data>)
Blokady ❌ (n): … – kto, do kiedy
Do sprawdzenia na budowie: 1. … (jak, kto)  2. …
Zdjęcia przed zakryciem: …
Ludzie / dostawy do umówienia: …
Zapisane: Notion … | 🛑 Czeka na Twoją odpowiedź: … (tylko gdy coś stoi)
```

## Czego nie robić

- Nie odbieraj za kierownika budowy ani nie zatwierdzaj zmian konstrukcyjnych (`analiza-techniczna`, Granice).
- Nie skracaj bramki, żeby „zdążyć przed betonem” – lepiej przesunąć betonowanie niż kuć płytę.
- Nie wymyślaj tolerancji i wymagań – podawaj źródło albo oznacz `[opinia]` i „do potwierdzenia z kierownikiem”.
