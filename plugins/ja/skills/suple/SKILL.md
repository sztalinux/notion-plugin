---
name: suple
description: Suplementy w bazie „Suple” w Notion – zaznaczenie do kupienia, gdy się kończą, odznaczenie po zakupie, start, przerwa i powrót do brania; lista „co kupić”. Używaj, gdy użytkownik pisze „kończy się magnez”, „brakuje mi witaminy D”, „kupiłem omegę”, „zaczynam ashwagandhę”, „robię przerwę od…”, „wracam do…”, „jakie suple mam kupić”, albo gdy wpis z Dziennika ma obszar Suple.
---

# Suplementy

Baza **Suple** (`collection://0771d295-5bc0-46e3-b0cb-def13bccab8d`): Name, Status (TAKING / BREAK / TO START / SUSPENDED),
**Buy** (checkbox – lista zakupów), Who (kto bierze – opcja inwestora jest podana w bazie Obszary, wiersz „Suple”),
When, Last break, Type, ceny (formuły) i dawki (liczby) – nie ruszaj.

## Procedura

1. Dopasuj suplement do wiersza po Name (odmiana, skróty, „wit. D” = „Witamina D”). Odczyt: wyszukiwarka z parametrem bazy Suple (nazwa) albo widok.
2. Zmiana według wpisu:
   | Wpis | Zmiana |
   |---|---|
   | „kończy się”, „brakuje”, „trzeba kupić” | Buy = tak |
   | „kupiłem”, „przyszło” | Buy = nie |
   | „zaczynam X” | Status = TAKING (wiersz jest) |
   | „przerwa od X” | Status = BREAK, Last break = data wpisu |
   | „wracam do X” | Status = TAKING |
   | „odstawiam X na dobre” | Status = SUSPENDED |
3. Brak wiersza przy „zaczynam”, „kończy się”, „chcę spróbować” → nowy wiersz: Name, Status = TO START (przy „zaczynam”
   → TAKING), Who = opcja inwestora (albo osoba, o której mowa), Buy = tak, reszta pusta.
4. Dwa pasujące wiersze albo nie wiadomo, o czyj suplement chodzi (Who ma dwie osoby, a wpis mówi o jednej) → pytanie pod wpisem w „📝 Wpisy” (`wpisy`, krok 4).
5. Nie zmieniaj dawek, cen, linków ani pól, o których wpis nie mówi.

## Odczyt

„Co mam kupić” → wiersze z Buy = tak (widok z filtrem Buy; brak – utwórz „🛒 Do kupienia”): nazwa, kto, link. Pozycje ze Statusem
BREAK / SUSPENDED wymień osobno jako „do sprawdzenia (wstrzymane)”, nie jako do kupienia – Buy odznacza dopiero inwestor
(pytanie z wieczornego przeglądu dnia, `przeglad-dnia/references/kontrola-spojnosci-suple.md`). „Co biorę” → Status = TAKING według When.
