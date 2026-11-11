# Odczyt baz Notion a limit zapytań (`budowa`, zasada 6)

Wiedzę (Informacje, Tematy, Rozmowy i źródła, sprzeczności) czytaj **najpierw z indeksu**
(`wiedza/references/indeks.md`; kolejność – `budowa`, zasada 10) – nie zużywa limitu Notion. Limit dotyczy tylko odczytu
z Notion: zapytania do baz (`query_data_sources`) w trybach **sql i rows** mają w planie Notion inwestora wspólny limit dla
całego workspace'u (SQL wyczerpany 12.10.2026, rows – 15.10.2026; termin odnowienia nieznany).

Tryb **view** (zapisany widok z filtrem) limitu nie ma. Czytaj w tej kolejności: **view** (istniejący widok; brak
pasującego → utwórz widok z filtrem, to nie zmienia danych) → wyszukiwarka z parametrem bazy (duplikaty, pojedyncze
wiersze) → rows → SQL tylko do zliczeń i łączenia baz. Błąd „usage limit” → bez ponawiania przejdź na view/wyszukiwarkę
i wspomnij o limicie raz.

Rollupy (np. Potwierdzenia, Data informacji) w rows/view przychodzą jako odnośniki, nie wartości – gdy są potrzebne,
pobierz pojedyncze strony (`fetch`) albo napisz, że ich nie sprawdziłeś.
