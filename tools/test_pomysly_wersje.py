#!/usr/bin/env python3
"""Testy tools/pomysly_wersje.py na zmyślonym CHANGELOG (bez prawdziwych danych).

    python3 tools/test_pomysly_wersje.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pomysly_wersje as P  # noqa: E402

PRZYKLAD = """# Changelog

## ja [1.5.0] – 2026-02-03 (POM-7, POM-9)

POM-9 – coś; odwołanie do POM-12 w treści.

## dom-budowa [2.1.0] – 2026-02-02 (POM-4)

Wpis.

## ja [1.4.0] – 2026-02-01 (POM-7)

Pierwsza część.

## [1.0.0] – 2026-01-01

Stary wpis bez pluginu. POM-4 wspomniany w treści.

## [Unreleased]

POM-99 – nie liczy się.
"""


class Mapa(unittest.TestCase):
    def setUp(self):
        self.m = P.mapa_pomyslow(PRZYKLAD)

    def test_naglowki_kilka_wersji(self):
        self.assertEqual(self.m[7]["naglowki"], ["ja 1.5.0", "ja 1.4.0"])

    def test_naglowek_dwa_pomysly(self):
        self.assertEqual(self.m[9]["naglowki"], ["ja 1.5.0"])

    def test_tylko_w_tresci_nie_jest_naglowkiem(self):
        self.assertEqual(self.m[12], {"naglowki": [], "tylko_w_tresci": ["ja 1.5.0"]})
        self.assertEqual(self.m[4], {"naglowki": ["dom-budowa 2.1.0"], "tylko_w_tresci": ["dom-budowa 1.0.0"]})

    def test_nagłówek_bez_daty_pomijany(self):
        self.assertNotIn(99, self.m)


class Numer(unittest.TestCase):
    def test_formy(self):
        self.assertEqual(P.numer("14"), 14)
        self.assertEqual(P.numer("pom-8"), 8)

    def test_zle(self):
        with self.assertRaises(ValueError):
            P.numer("abc")


class PrawdziwyChangelog(unittest.TestCase):
    def test_parsuje_sie(self):
        tekst = (P.ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertTrue(P.sekcje(tekst))


if __name__ == "__main__":
    unittest.main()
