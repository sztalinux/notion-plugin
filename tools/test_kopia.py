#!/usr/bin/env python3
"""Testy tools/kopia.py na zmyślonym folderze budowy (bez Dysku).

    python3 tools/test_kopia.py
"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

TMP = Path(tempfile.mkdtemp(prefix="kopia-test-"))
os.environ["KOPIA_DANE"] = str(TMP / "stan")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kopia as K  # noqa: E402


class Dozwolone(unittest.TestCase):
    def test_nigdy(self):
        for s in (".dom/sekrety.env", "AI/dom/README.md", "Wiedza/kurs.md", "Wiedza - kursy i blogi/a.md",
                  "_Przychodzące/a.pdf", "_Do claude.ai/a.md", "_Na Dysk/2026-11-20/x.pdf", "Zdjęcia/a.jpg",
                  "Projekty/.DS_Store", "Umowy/~$umowa.docx", "Projekty/AI/x.pdf", "Projekty/a.pdf.part"):
            self.assertFalse(K.dozwolony(s), s)

    def test_tak(self):
        for s in ("Projekty/Konstrukcja/a.pdf", "Faktury/2026/2026-11-18_x.jpg", "Dostawy/Etap A/wz.jpg",
                  "Dziennik budowy KB/2026-11-18_1.jpg", "Media/Prąd/a.pdf"):
            self.assertTrue(K.dozwolony(s), s)

    def test_sprawdz_liste(self):
        zle = K.sprawdz_liste(["Dom/Projekty/a.pdf", "Dom/.dom/x", "Dom/AI/dom/a.md", "Dom/sekrety.env"])
        self.assertEqual(len(zle), 3)


class Roznice(unittest.TestCase):
    def test_nowe_zmienione_przeniesione_usuniete(self):
        pot = {"A/a": {"sha256": "1"}, "A/b": {"sha256": "2"}, "A/c": {"sha256": "3"}}
        teraz = {"A/a": {"sha256": "1"}, "A/b": {"sha256": "9"}, "B/c": {"sha256": "3"}, "A/d": {"sha256": "4"}}
        r = K.roznice(pot, teraz)
        self.assertEqual(r["nowe"], ["A/d"])
        self.assertEqual(r["zmienione"], ["A/b"])
        self.assertEqual(r["przeniesione"], [{"z": "A/c", "do": "B/c"}])
        self.assertEqual(r["usuniete"], [])


class Paczka(unittest.TestCase):
    def setUp(self):
        self.hub = Path(tempfile.mkdtemp(prefix="hub-", dir=TMP))
        for rel, tresc in (("Projekty/a.pdf", b"a"), ("Umowy/b.pdf", b"b"), (".dom/sekrety.env", b"x"),
                           ("AI/dom/c.md", b"c"), ("Projekty/~$tmp.docx", b"t")):
            p = self.hub / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(tresc)

    def test_paczka_tylko_dozwolone_i_kolejna_zawiera_niewgrane(self):
        teraz = K.skanuj(self.hub)
        self.assertEqual(sorted(teraz), ["Projekty/a.pdf", "Umowy/b.pdf"])
        r = K.roznice({}, teraz)
        p = K.zbuduj_paczke(self.hub, r, teraz, "2026-11-20", True)
        self.assertTrue((self.hub / p["folder"] / "SPIS.txt").exists())
        self.assertFalse((self.hub / p["folder"] / ".dom").exists())
        # paczka niewgrana: porównanie dalej z pustym potwierdzonym stanem → następna zawiera oba pliki i nowy
        (self.hub / "Umowy/n.pdf").write_bytes(b"n")
        teraz2 = K.skanuj(self.hub, teraz)
        r2 = K.roznice({}, teraz2)
        self.assertEqual(len(r2["nowe"]), 3)
        p2 = K.zbuduj_paczke(self.hub, r2, teraz2, "2026-11-20", True)
        self.assertTrue(p2["folder"].endswith("2026-11-20-b"))

    def test_aplikacja_archiwizuje_nie_kasuje(self):
        dysk = Path(tempfile.mkdtemp(prefix="dysk-", dir=TMP))
        pot = K.skanuj(self.hub)
        K.kopiuj_do_aplikacji(self.hub, dysk, K.roznice({}, pot), True, "2026-11-20")
        self.assertTrue((dysk / "Projekty/a.pdf").exists())
        (self.hub / "Projekty/a.pdf").write_bytes(b"nowa wersja")
        (self.hub / "Umowy/b.pdf").unlink()
        teraz = K.skanuj(self.hub, pot)
        r = K.roznice(pot, teraz)
        K.kopiuj_do_aplikacji(self.hub, dysk, r, True, "2026-11-21")
        self.assertEqual((dysk / "Projekty/a.pdf").read_bytes(), b"nowa wersja")
        self.assertEqual((dysk / "_Archiwum/2026-11-21/Projekty/a.pdf").read_bytes(), b"a")
        self.assertTrue((dysk / "_Archiwum/2026-11-21/Umowy/b.pdf").exists())

class Dzien(datetime):
    """Data „dzisiaj” w poleceniach kopia.py – testy nie zależą od dzisiejszej daty."""
    dzis = datetime(2026, 11, 20, 12)

    @classmethod
    def now(cls, tz=None):
        return cls.dzis


class Polecenia(unittest.TestCase):
    """main(): paczka --wykonaj, wgrane, stan (F-14, F-15, F-20). Bez folderu Dysku (DYSK_DOM wskazuje brak)."""

    def setUp(self):
        self.hub = Path(tempfile.mkdtemp(prefix="hub-", dir=TMP))
        (self.hub / "Projekty").mkdir()
        (self.hub / "Projekty/a.pdf").write_bytes(b"a")
        for latka in (mock.patch.object(K, "HUB", self.hub), mock.patch.object(K, "STAN_DIR", self.hub / ".dom/kopia"),
                      mock.patch.object(K, "datetime", Dzien),
                      mock.patch.dict(os.environ, {"DYSK_DOM": str(self.hub / "nie-ma-dysku")})):
            latka.start()
            self.addCleanup(latka.stop)

    def kopia(self, *argv) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(K.main(list(argv)), 0)
        return out.getvalue()

    def paczka(self, dzien: str):
        Dzien.dzis = datetime.fromisoformat(dzien + "T12:00")
        self.kopia("paczka", "--wykonaj")
        return json.loads((self.hub / ".dom/kopia/stan.json").read_text())

    def test_paczka_i_wgrane(self):
        stan = self.paczka("2026-11-20")
        folder = self.hub / stan["paczki"][-1]["folder"]
        self.assertEqual((folder / "Projekty/a.pdf").read_bytes(), b"a")
        self.assertTrue((folder / "SPIS.txt").exists())
        self.assertIn("paczki do wgrania: 2026-11-20", self.kopia("stan"))
        self.kopia("wgrane")
        self.assertIn("zmian od niej: 0", self.kopia("stan"))
        self.assertIn("aktualna", self.kopia("paczka"))

    def test_wgrane_starszej_po_nowszej_nie_cofa_stanu(self):
        # wgrane <nowsza> obejmuje starsze paczki; wgrane <starsza> nie cofa potwierdzonego stanu (F-14)
        self.paczka("2026-11-20")
        (self.hub / "Projekty/b.pdf").write_bytes(b"b")
        self.paczka("2026-11-22")
        self.kopia("wgrane", "2026-11-22")
        linia = self.kopia("stan")
        self.assertNotIn("paczki do wgrania", linia)
        self.assertIn("potwierdzona: 2026-11-22", linia)
        self.assertIn("brak paczki", self.kopia("wgrane", "2026-11-20"))
        self.assertIn("potwierdzona: 2026-11-22", self.kopia("stan"))

    def test_wgrane_starszej_przed_nowsza(self):
        self.paczka("2026-11-20")
        (self.hub / "Projekty/b.pdf").write_bytes(b"b")
        self.paczka("2026-11-22")
        self.kopia("wgrane", "2026-11-20")
        linia = self.kopia("stan")
        self.assertIn("potwierdzona: 2026-11-20", linia)
        self.assertIn("paczki do wgrania: 2026-11-22", linia)
        self.kopia("wgrane", "2026-11-22")
        self.assertIn("zmian od niej: 0", self.kopia("stan"))

if __name__ == "__main__":
    unittest.main(verbosity=1)
