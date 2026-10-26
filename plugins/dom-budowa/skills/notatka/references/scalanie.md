# Notatnik – scalanie duplikatów i wpisów dublujących wiedzę

Statusy Notatnika nie mają „Nieaktualne”, a struktury bazy nie zmieniasz. Zasady ogólne (bieżący stan przed zapisem,
log PRZED/PO poza repo, nigdy nie usuwaj stron): `wiedza/references/porzadki.md`.

1. **Nie wycofuj wpisu otwartego** (Status „Otwarte” albo „Do omówienia”) – zniknąłby z widoków spraw do zamknięcia na DOM.
   Taki wpis zostaje; najwyżej podepnij relację Wiedza.
2. **Wpis zostaje jeden** (krok 2 procedury): treść duplikatu dopisz w treści strony wpisu głównego z datą, Źródła połącz
   („…; …”), relację Wiedza przenieś.
3. **Wpis wycofany:** Status „Odrzucone” i na samym początku treści strony linia
   „Scalone do WI-x (RRRR-MM-DD)” albo „Scalone do <wzmianka wpisu głównego> (RRRR-MM-DD)”; reszta treści i pola bez zmian.
4. **Wpis dublujący wiedzę** (Pamiętać, który powtarza tezę WI): wpis wycofaj jak w pkt 3, a na WI-x ustaw Dotyczy nas
   „Tak”; brakujące ustalenia naszej budowy z wpisu dopisz do „Dla naszej budowy” WI-x („z Notatnika, RRRR-MM-DD: …”).
   Relacja Notatnik ↔ Wiedza zostaje – prowadzi od wycofanego wpisu do tezy.
5. Po każdej paczce sprawdź widoki na DOM („🔴 Do zamknięcia przed …”, „Krytyczne i otwarte”) – te same otwarte wpisy co
   przed zapisem. W widokach Notatnika dodaj filtr „Status ≠ Odrzucone”, chyba że widok służy przeglądowi odrzuconych.
