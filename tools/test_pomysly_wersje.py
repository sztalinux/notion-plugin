#!/usr/bin/env python3
"""Testy tools/pomysly_wersje.py na zmyślonym CHANGELOG (bez prawdziwych danych).

    python3 tools/test_pomysly_wersje.py
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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


class OdczytChangelog(unittest.TestCase):
    def test_z_galezi_main(self):
        wynik = subprocess.CompletedProcess([], 0, stdout=PRZYKLAD.encode("utf-8"), stderr=b"")
        with mock.patch.object(P.subprocess, "run", return_value=wynik) as run:
            tekst, ostrzezenie = P.czytaj_changelog()
        self.assertEqual(tekst, PRZYKLAD)
        self.assertEqual(ostrzezenie, "")
        self.assertIn("main:CHANGELOG.md", run.call_args[0][0])

    def test_bez_main_plik_z_ostrzezeniem(self):
        wynik = subprocess.CompletedProcess([], 128, stdout=b"", stderr=b"fatal: invalid object name 'main'.")
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "CHANGELOG.md").write_text("## ja [1.0.0] – 2026-01-01 (POM-3)\n", encoding="utf-8")
            with mock.patch.object(P.subprocess, "run", return_value=wynik), mock.patch.object(P, "ROOT", Path(d)):
                tekst, ostrzezenie = P.czytaj_changelog()
        self.assertIn("POM-3", tekst)
        self.assertIn("gałęzi main", ostrzezenie)

    def test_bez_gita_i_pliku(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(P.subprocess, "run", side_effect=FileNotFoundError("git")), \
                    mock.patch.object(P, "ROOT", Path(d)):
                tekst, ostrzezenie = P.czytaj_changelog()
        self.assertIsNone(tekst)
        self.assertIn("brak też", ostrzezenie)

    def test_prawdziwy_parsuje_sie(self):
        tekst, _ = P.czytaj_changelog()
        self.assertTrue(P.sekcje(tekst))


if __name__ == "__main__":
    unittest.main()
