#!/usr/bin/env python3
"""Testy wzorców kontroli prywatności (`build.py`, lista WZORCE) na zmyślonych danych – P05-13.

    python3 tools/test_build_wzorce.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402


def zmyslone(s: str) -> str:
    """„§” rozcina zmyślone wartości w źródle, żeby sam plik testu przechodził kontrolę prywatności."""
    return s.replace("§", "")


def trafienia(linia: str) -> list:
    return [opis for rx, opis in build.WZORCE if rx.search(zmyslone(linia))]


class Wzorce(unittest.TestCase):
    def test_kwoty(self):
        for linia in ("45 tys. z§ł", "1,2 mln z§ł", "1500 z§łotych", "1500 z§l", "1500 p§ln", "120k z§ł",
                      "1500 P§LN", "P§LN 1500", "3 400,50 z§ł"):
            self.assertIn("kwota", trafienia(linia), linia)

    def test_adresy(self):
        for linia in ("al§. Lipowa", "os§. Słoneczne", "osie§dle Zielone", "u§l. Krótka"):
            self.assertIn("adres", trafienia(linia), linia)

    def test_telefony(self):
        for linia in ("7§1 345 67 89", "(7§1) 345-67-89", "00§486001§00200", "+48 7§1 345 67 89", "00§48 600 1§00 200"):
            self.assertIn("numer telefonu", trafienia(linia), linia)

    def test_obejscia_f3(self):
        """Zapisy, które wcześniej omijały wzorce (F-3)."""
        for linia, opis in (("12 500,- z§ł", "kwota"), ("Faktura: z§ł 12 500 brutto", "kwota"), ("tel. 600.1§00.200", "numer telefonu"),
                            ("Działka nr ewid. 12§3/4, obręb", "numer działki"), ("działki ewid. 12§3/4", "numer działki"),
                            ("dz. ew. nr 12§3/4", "numer działki"), ("u§l.Kwiatowa 5", "adres"), ("u§l. kwiatowa 5", "adres"),
                            ("jan [at] exa§mple.com", "adres e-mail"), ("jan(małpa)exa§mple.pl", "adres e-mail")):
            self.assertIn(opis, trafienia(linia), linia)

    def test_zwykly_tekst_przechodzi(self):
        for linia in ("N zł", "N tys. zł", "pln w nazwie pliku", "kosztorys w PLN", "al. i os. bez nazwy",
                      "wersja 3.14.4, ja 1.13.5", "2026-11-12 17:05", "m > 15: 35/176", "top 60 · 12 kart",
                      "tez 1636, w kartach 2197", "os. – osoba", "WI-1622, WI-300", "3 z 3 złapane", "2 złącza", "5 złomu",
                      "IP 192.168.100.200", "wersja 1.27.0", "nr 12/2026", "ul. i al.", "ul. nr 5", "[at] w nawiasie",
                      "zł/m³", "N zł, 2 osoby", "kwota w zł: N", "ewidencja 3/4 kroków", "e-mail: x [at] y"):
            self.assertEqual(trafienia(linia), [], linia)

    def test_sprawdz_tekst_zgodny_z_wzorcami(self):
        """Wstępny odsiew w sprawdz_tekst (linie z cyfrą, cały tekst) nie gubi trafień pojedynczych wzorców."""
        przyklady = ["45 tys. z§ł", "12 500,- z§ł", "Faktura: z§ł 12 500", "tel. 600.1§00.200", "7§1 345 67 89",
                     "działki ewid. 12§3/4", "u§l.Kwiatowa", "u§l. kwiatowa 5", "jan [at] exa§mple.com", "ab@exa§mple.com",
                     "N zł", "wersja 1.27.0", "al. i os. bez nazwy"]
        tekst = "\n".join(przyklady)
        bledy = build.sprawdz_tekst("x", zmyslone(tekst), [])
        for nr, linia in enumerate(przyklady, 1):
            oczekiwane = sorted(trafienia(linia))
            znalezione = sorted(b.split("wygląda na ")[1].split(" – ")[0] for b in bledy if b.startswith(f"x:{nr}:"))
            self.assertEqual(znalezione, oczekiwane, linia)


if __name__ == "__main__":
    unittest.main()
