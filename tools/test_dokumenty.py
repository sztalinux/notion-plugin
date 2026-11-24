#!/usr/bin/env python3
"""Testy tools/dokumenty.py na zmyślonym folderze budowy (pliki .txt w katalogu tymczasowym, bez Notion).

    python3 tools/test_dokumenty.py
"""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HUB = Path(tempfile.mkdtemp(prefix="dokumenty-test-"))
os.environ["DOM_HUB"] = str(HUB)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dokumenty as D  # noqa: E402


def uruchom(*argv) -> str:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        kod = D.main(list(argv))
    assert kod == 0, (argv, kod, out.getvalue())
    return out.getvalue()


def plik(rel: str, tresc: str):
    p = HUB / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(tresc, encoding="utf-8")


class Dokumenty(unittest.TestCase):
    def setUp(self):
        for p in HUB.iterdir():
            shutil.rmtree(p) if p.is_dir() else p.unlink()
        (HUB / ".dom").mkdir()
        plik("Projekty/opis-techniczny.txt", "projekt wersja 1")
        plik("Umowy/umowa.txt", "umowa robocza")
        uruchom()
        uruchom("ustaw", "Projekty/opis-techniczny.txt", "--bez-eksportu", "--opis", "opis techniczny v1",
                "--zawartosc", "konstrukcja, izolacje")
        uruchom("ustaw", "Umowy/umowa.txt", "--bez-eksportu", "--opis", "umowa", "--zawartosc", "zakres i terminy")

    def indeks(self) -> dict:
        return D.wczytaj(D.INDEKS, {"pliki": {}})["pliki"]

    def test_nowy_plik_do_klasyfikacji(self):
        plik("Projekty/nowy.txt", "coś nowego")
        r = uruchom()
        self.assertIn("Nowe pliki do sklasyfikowania (1)", r)
        self.assertEqual(self.indeks()["Projekty/nowy.txt"]["status"], "nowy")

    def test_przeniesienie_zachowuje_opis(self):
        (HUB / "Projekty/archiwum").mkdir()
        (HUB / "Projekty/opis-techniczny.txt").rename(HUB / "Projekty/archiwum/opis-techniczny.txt")
        r = uruchom()
        self.assertIn("Przeniesione: 1", r)
        self.assertEqual(self.indeks()["Projekty/archiwum/opis-techniczny.txt"]["opis"], "opis techniczny v1")

    def test_duplikat(self):
        plik("Projekty/kopia-umowy.txt", "umowa robocza")
        r = uruchom()
        self.assertIn("Duplikaty (pominięte): 1", r)
        self.assertEqual(self.indeks()["Projekty/kopia-umowy.txt"]["opis"], "duplikat: Umowy/umowa.txt")

    def test_zmieniona_tresc(self):
        plik("Umowy/umowa.txt", "umowa podpisana – inna treść")
        self.assertIn("Zmieniona treść dokumentów", uruchom())

    def test_dry_run_nie_zapisuje(self):
        plik("Projekty/nowy.txt", "coś nowego")
        przed = D.INDEKS.read_bytes()
        uruchom("--dry-run")
        self.assertEqual(D.INDEKS.read_bytes(), przed)

    def test_ustaw_nowego_pliku_nie_polyka_zdarzen(self):
        # A.7: nowa wersja przeniesiona z _Przychodzące pod inną nazwą, stara usunięta, od razu `ustaw` na nowej
        # ścieżce – synchronizacja w `ustaw` zapisuje indeks, więc jej zdarzenia muszą paść tutaj (F-9)
        (HUB / "Projekty/opis-techniczny.txt").unlink()
        plik("Projekty/opis-techniczny-v2.txt", "projekt wersja 2")
        plik("Umowy/umowa.txt", "umowa podpisana – inna treść")
        r = uruchom("ustaw", "Projekty/opis-techniczny-v2.txt", "--bez-eksportu", "--opis", "opis techniczny v2",
                    "--zawartosc", "konstrukcja, izolacje")
        self.assertIn("Usunięte z dysku: 1", r)
        self.assertIn("Zniknęły dokumenty z przewodnika", r)
        self.assertIn("Projekty/opis-techniczny.txt", r)
        self.assertIn("Zmieniona treść dokumentów", r)
        self.assertIn("Umowy/umowa.txt", r)

    def test_ustaw_znanego_pliku_bez_synchronizacji(self):
        r = uruchom("ustaw", "Umowy/umowa.txt", "--kategoria", "60 Umowy")
        self.assertNotIn("Usunięte", r)
        self.assertEqual(self.indeks()["Umowy/umowa.txt"]["kategoria"], "60 Umowy")


if __name__ == "__main__":
    unittest.main(verbosity=1)
