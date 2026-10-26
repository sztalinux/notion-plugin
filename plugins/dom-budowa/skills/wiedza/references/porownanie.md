# Porównanie z całym tematem (A.5)

Cel: żadna istniejąca informacja, do której rzetelny redaktor dałby odnośnik, nie zostaje pominięta. Audyt nocy
(22.10.2026): 19% powiązanych informacji nigdy nie trafiło do wyników wyszukiwania, 18% trafiło i nie dostało odnośnika,
potwierdzeń nie podpinano wcale – w 94% przypadków brakujący wiersz leżał w tym samym temacie.

1. **Tezy najpierw.** Skończ ekstrakcję całego źródła, zanim zaczniesz porównywać. Jednostkom nadaj numery T-1, T-2…
2. **Temat po temacie.** Dla każdego tematu jednostek:
   - raz na temat: `temat "<temat>" --lista --krotko` – wszystkie widoczne wiersze tematu (nie pierwsze 12); porównaj z nimi
     każdą jednostkę tego tematu (nazwa tematu dokładnie jak w bazie; przy „pasuje kilka” podaj pełną);
   - dla każdej jednostki `szukaj "<2–4 słowa>" --limit 20` (pełne linie, bo potrzebujesz „Kto”; kilka sformułowań, gdy
     jednostka ma synonimy) – trafienia z innych tematów i „Kto” kandydatów z listy tematu;
   - wiersze z sekcji „podobne” traktuj jak trafienia: przeczytaj tezę, zanim uznasz relację.
3. **Lista relacji przed zapisem.** Spisz dla siebie, teza po tezie: `T-n → NOWA` albo `T-n → TYP WI-x` (POWTÓRZENIE,
   POTWIERDZENIE, UZUPEŁNIENIE, SPRZECZNOŚĆ; kilka relacji – wszystkie). Relacja = ten sam konkretny problem; ta sama
   branża albo etap to jeszcze nie relacja. Inne warunki (grunt, technologia) to UZUPEŁNIENIE, nie SPRZECZNOŚĆ.
4. **POTWIERDZENIE czy POWTÓRZENIE** rozstrzygnij po „Kto” źródeł WI-x (reguła „ten sam autor” w SKILL.md A.5):
   niezależne źródło → podepnij WI-x pod nowy ZRD; ten sam autor lub krąg → „powtarza WI-x” w Najważniejsze.
5. **Zapis według listy** (A.7): każda relacja z listy musi zostawić ślad – numer WI-x w Szczegółach nowego wiersza,
   w Najważniejsze ZRD, podpięcie WI-x pod ZRD albo wspólny SP.
6. **Kontrola po zapisie.** Przejdź listę jeszcze raz i sprawdź ślad każdej relacji; braki uzupełnij, a pominięte
   świadomie podaj w odpowiedzi („Relacje odrzucone: T-n → WI-x – powód”).

Przebieg nocny (kolejka, ustawienie „porównanie etapami”) robi kroki 2–3 skryptem (`kolejka_porownanie.py`) i podaje
agentowi gotową listę; krok 6 sprawdza skrypt po sync.
