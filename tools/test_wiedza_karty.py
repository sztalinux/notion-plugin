#!/usr/bin/env python3
"""Testy kodu wyjścia `wiedza_karty.py aktualizuj` (bez indeksu, modelu i danych – sama funkcja kodu).

    python3 tools/test_wiedza_karty.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wiedza_karty as K  # noqa: E402


def wynik(**pola):
    w = {"otagowane": 0, "dopisane": 0, "ocenione": 0, "bledy": 0}
    w.update(pola)
    return w


class KodAktualizacji(unittest.TestCase):
    def test_same_bledy_daja_1(self):
        self.assertEqual(K.kod_aktualizacji(0, wynik(bledy=3)), 1)

    def test_bledy_przy_postepie_daja_0(self):
        self.assertEqual(K.kod_aktualizacji(0, wynik(bledy=2, otagowane=1)), 0)
        self.assertEqual(K.kod_aktualizacji(0, wynik(bledy=2, dopisane=1)), 0)
        self.assertEqual(K.kod_aktualizacji(0, wynik(bledy=2, ocenione=1)), 0)

    def test_bez_bledow_0(self):
        self.assertEqual(K.kod_aktualizacji(0, wynik()), 0)

    def test_stop_zostawia_swoj_kod(self):
        self.assertEqual(K.kod_aktualizacji(K.KOD_STOP, wynik(bledy=3)), K.KOD_STOP)


if __name__ == "__main__":
    unittest.main()
