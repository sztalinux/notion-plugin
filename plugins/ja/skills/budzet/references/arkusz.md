# Arkusz „Budżet domowy” – układ i formuły

Opis struktury, bez danych (kwoty, imiona i konta są w arkuszu i w `ustawienia.json`). Imię drugiej osoby = `osoba_listy`,
pierwszej = `osoba_wyciagi`, kategoria przychodu z sald = `przychod_z_sald.kategoria`, etykieta wiersza w zakładce roku =
`przychod_z_sald.etykieta_roku`.

## Transakcje (kolumny A–O)

A data (format `d"-"mmm"-"yyyy`) · B status · C Typ (Przychód / Wydatek / Koszt / Inwestycja / Przelew) · D kwota (liczba
albo formuła sumy, format `#,##0.00" zł"`) · E Kategoria · F Podkategoria · G Konto · H Osoba · I Opis · J Projekt ·
K Tag (`import RRRR-MM`) · L Notatki (`z wpisu` przy wierszach z wpisów) · M miesiąc `=IF($A2="","",DATE(YEAR($A2),MONTH($A2),1))`
(format `yyyy-mm`) · N rok `=IF($A2="","",YEAR($A2))` · O ID importu (ukryta; ID z wyciągów `b…`, Allegro `a…`, list `l…`,
wpisów `w…` – po przecinku; wiersz z wpisu po przypięciu płatności ma też ID wyciągu). Nagłówki w wierszu 1 (C1:O1 sprawdza
skrypt arkusza – `docs/budzet-arkusz.md`), dane od wiersza 2. Daty skrypt zapisuje w strefie arkusza (Plik → Ustawienia).
Pary kategoria–podkategoria i typy: zakładka Kategorie (kopia w `kategorie.json`); zła para podświetla się na pomarańczowo.

## Zakładka roku (np. „2026”)

- Wiersz 1: numery miesięcy w D:O, rok w P1. Wiersze sekcji: Typ w A, Kategoria w B, Podkategoria w C; komórka miesiąca
  sumuje Transakcje po A (typ), B (kategoria) albo C (podkategoria – **po samej nazwie**, więc nazwa musi być unikalna).
  Wzorzec: `IFERROR(IF($A..; suma po C; IF($B..; suma po E; IF($C..; suma po F))); 0)` – nowy wiersz kopiuj z sąsiedniego.
- Sekcja Przelew ma wiersze O->A i A->O (kategorie przelewów między osobami) – z nich liczy się przychód drugiej osoby.
- Pod sekcjami: wiersz pierwszej osoby i wiersz drugiej osoby = suma Transakcji z daną Osobą, **bez** Przychodów
  i Przelewów; wiersz „do dodania” (`etykieta_roku`, oznaczony „NIE ZMIENIAĆ WIERSZA”) = wiersz drugiej osoby + O->A − A->O
  − Przychody z jej Osobą poza wierszem z sald. Sprawdzenie: wiersze obu osób razem = Wydatek + Koszt + Inwestycja.
- Kolory: formatowanie warunkowe na A2:P94 według kolumn A–C (typ ciemny i pogrubiony, kategoria pogrubiona, podkategoria
  jasna; kolor sekcji). Nie formatuj ręcznie – wiersz dodany w środku dostanie kolor sam.

## Konta

Kolumny B:M = miesiące 1–12, wartość = stan na **1. dzień** tego miesiąca (czyli koniec poprzedniego). Wiersze: konta
pierwszej osoby (z wyciągów), konta drugiej osoby, gotówka, oszczędności emerytalne, długi (wiersz „Długi” – liczy się
do drugiej osoby). Wiersz drugiej osoby (`przychod_z_sald.wiersz_konta`) = jej konta + gotówka + długi; emerytalne liczą się do
pierwszej osoby. Komórka może być formułą (`=1000+250`) – tak zapisuj korekty odczytu sald.

Przychód drugiej osoby za miesiąc m (wiersz w Transakcjach, ostatni w miesiącu):
`=(Konta!<kolumna m+1><wiersz> - Konta!<kolumna m><wiersz>) + XLOOKUP("<etykieta_roku>"; '<rok>'!A:A; '<rok>'!<kolumna m>)`
– tworzy go `importuj.py`; nie wpisuj gotowej liczby.

## Nowy rok

Grudzień potrzebuje salda na 1.01 następnego roku, a styczeń – zakładki nowego roku. Przed zamknięciem grudnia:
1. Zduplikuj zakładkę roku, zmień nazwę i rok w P1; sprawdź, że formatowanie warunkowe i formuły wierszy osób przeszły.
2. Ustal z inwestorem, gdzie zapisać salda na 1.01 (nowa kolumna albo zakładka Konta roku) i popraw w `ustawienia.json`
   to, co się zmieniło. `importuj.py` w grudniu nie tworzy wiersza przychodu z sald (zgłasza to w „Brakuje”) – dopisz go
   ręcznie według wzoru wyżej.
