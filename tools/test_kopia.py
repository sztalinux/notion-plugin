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

    def test_aplikacja_archiwum_bez_nadpisania(self):
        # druga zmiana tego samego pliku tego samego dnia nie nadpisuje wersji już zarchiwizowanej (F-10)
        dysk = Path(tempfile.mkdtemp(prefix="dysk-", dir=TMP))
        pot = K.skanuj(self.hub)
        K.kopiuj_do_aplikacji(self.hub, dysk, K.roznice({}, pot), True, "2026-11-20")
        for tresc in (b"v2", b"v3-dluzsza"):  # inna długość – skan porównuje rozmiar i mtime
            (self.hub / "Projekty/a.pdf").write_bytes(tresc)
            teraz = K.skanuj(self.hub, pot)
            K.kopiuj_do_aplikacji(self.hub, dysk, K.roznice(pot, teraz), True, "2026-11-21", teraz)
            pot = teraz
        arch = dysk / "_Archiwum/2026-11-21/Projekty"
        self.assertEqual(sorted(x.read_bytes() for x in arch.iterdir()), [b"a", b"v2"])
        self.assertEqual((dysk / "Projekty/a.pdf").read_bytes(), b"v3-dluzsza")

    def test_aplikacja_porownuje_z_dyskiem(self):
        # (a) plik usunięty ręcznie na Dysku wraca; (b) nowy plik z Maca, a na Dysku inny pod tą samą ścieżką –
        # wersja z Dysku do _Archiwum, kopia z Maca i wpis w logu (F-11)
        dysk = Path(tempfile.mkdtemp(prefix="dysk-", dir=TMP))
        pot = K.skanuj(self.hub)
        K.kopiuj_do_aplikacji(self.hub, dysk, K.roznice({}, pot), True, "2026-11-20", pot)
        (dysk / "Umowy/b.pdf").unlink()
        (dysk / "Projekty/n.pdf").write_bytes(b"WERSJA-Z-DYSKU")
        (self.hub / "Projekty/n.pdf").write_bytes(b"WERSJA-Z-MACA")
        teraz = K.skanuj(self.hub, pot)
        r = K.roznice(pot, teraz)
        self.assertEqual(K.brak_na_dysku(dysk, teraz, r), ["Umowy/b.pdf"])
        log = K.kopiuj_do_aplikacji(self.hub, dysk, r, True, "2026-11-21", teraz)
        self.assertEqual((dysk / "Umowy/b.pdf").read_bytes(), b"b")
        self.assertEqual((dysk / "Projekty/n.pdf").read_bytes(), b"WERSJA-Z-MACA")
        self.assertEqual((dysk / "_Archiwum/2026-11-21/Projekty/n.pdf").read_bytes(), b"WERSJA-Z-DYSKU")
        self.assertTrue(any("inna wersja" in x for x in log))
        self.assertTrue(any("brak na Dysku" in x for x in log))

    def test_zepsute_dowiazanie_pominiete(self):
        # zepsute dowiązanie nie wywraca skanu – pozycja w błędach odczytu (F-15)
        os.symlink(self.hub / "nie-ma.pdf", self.hub / "Projekty/skrot.pdf")
        bledy = []
        teraz = K.skanuj(self.hub, None, bledy)
        self.assertEqual(sorted(teraz), ["Projekty/a.pdf", "Umowy/b.pdf"])
        self.assertEqual(bledy, ["Projekty/skrot.pdf"])


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

    def kopia_kod(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            kod = K.main(list(argv))
        return kod, out.getvalue()

    def potwierdz(self, n: int):
        """n potwierdzonych plików (paczka + wgrane bez folderu Dysku)."""
        for i in range(n):
            (self.hub / f"Projekty/p{i:02}.pdf").write_bytes(b"x" * (i + 1))
        self.paczka("2026-11-20")
        self.kopia("wgrane")
        return sorted(json.loads((self.hub / ".dom/kopia/stan.json").read_text())["potwierdzone"])

    def dysk_z(self, pliki) -> Path:
        dysk = Path(tempfile.mkdtemp(prefix="dysk-", dir=TMP))
        for s in pliki:
            (dysk / s).parent.mkdir(parents=True, exist_ok=True)
            (dysk / s).write_bytes((self.hub / s).read_bytes())
        os.environ["DYSK_DOM"] = str(dysk)  # przywraca mock.patch.dict z setUp
        return dysk

    def test_nieczytelny_potwierdzony_to_nie_usuniety(self):
        # plik potwierdzony, potem nieczytelny (zepsute dowiązanie) – nie „usunięty na Macu” i bez archiwizacji
        # kopii z Dysku; pozycja ⚠ (recenzja F2, F-15)
        pot = self.potwierdz(2)
        (self.hub / "Projekty/a.pdf").unlink()
        os.symlink(self.hub / "nie-ma.pdf", self.hub / "Projekty/a.pdf")
        linia = self.kopia("stan")
        self.assertIn("usunięte 0", linia)
        self.assertIn("nie da się odczytać", linia)
        self.assertIn("aktualna", self.kopia("paczka"))
        dysk = self.dysk_z([s for s in pot if s != "Projekty/a.pdf"])
        (dysk / "Projekty/a.pdf").write_bytes(b"a")
        self.kopia("aplikacja", "--wykonaj")
        self.assertEqual((dysk / "Projekty/a.pdf").read_bytes(), b"a")
        self.assertFalse((dysk / "_Archiwum").exists())
        self.assertIn("Projekty/a.pdf", json.loads((self.hub / ".dom/kopia/stan.json").read_text())["potwierdzone"])

    def test_bezpiecznik_pusty_folder_dysku(self):
        # brakuje > 20% potwierdzonych i > 5 plików → folder Dysku niezsynchronizowany: aplikacja --wykonaj odmawia
        # bez --mimo-to, stan --cicho daje jedną linię ostrzeżenia
        pot = self.potwierdz(9)  # 10 potwierdzonych
        dysk = self.dysk_z(pot[:4])  # brakuje 6 z 10
        kod, out = self.kopia_kod("stan", "--cicho")
        self.assertEqual((kod, len(out.strip().splitlines())), (0, 1))
        self.assertIn("niezsynchronizowany", out)
        kod, out = self.kopia_kod("aplikacja", "--wykonaj")
        self.assertEqual(kod, 1)
        self.assertIn("--mimo-to", out)
        self.assertEqual(len(list(dysk.rglob("*.pdf"))), 4)
        kod, out = self.kopia_kod("aplikacja")  # na sucho: jedna linia zamiast listy braków
        self.assertNotIn("kopia ponownie: Projekty/p08.pdf", out)
        self.assertEqual(self.kopia_kod("aplikacja", "--wykonaj", "--mimo-to")[0], 0)
        self.assertEqual(len(list(dysk.rglob("*.pdf"))), 10)

    def test_bezpiecznik_progi(self):
        # 5 braków (50%, ale nie > 5) i 6 braków z 40 (15%) – zwykłe uzupełnienie
        pot = self.potwierdz(9)
        dysk = self.dysk_z(pot[:5])
        self.assertEqual(self.kopia_kod("aplikacja", "--wykonaj")[0], 0)
        self.assertEqual(len(list(dysk.rglob("*.pdf"))), 10)
        for i in range(10, 40):
            (self.hub / f"Projekty/p{i:02}.pdf").write_bytes(b"y" * (i + 1))
        self.paczka("2026-11-21")
        self.kopia("wgrane")
        pot = sorted(json.loads((self.hub / ".dom/kopia/stan.json").read_text())["potwierdzone"])
        self.assertEqual(len(pot), 40)
        dysk = self.dysk_z(pot[:34])  # brakuje 6 z 40
        kod, out = self.kopia_kod("stan", "--cicho")
        self.assertIn("brak na Dysku: 6", out)
        self.assertNotIn("niezsynchronizowany", out)
        self.assertEqual(self.kopia_kod("aplikacja", "--wykonaj")[0], 0)
        self.assertEqual(len(list(dysk.rglob("*.pdf"))), 40)

    def test_zepsute_dowiazanie_nie_wywraca_polecen(self):
        os.symlink(self.hub / "nie-ma.pdf", self.hub / "Projekty/skrot.pdf")
        self.assertIn("nie da się odczytać", self.kopia("stan"))
        self.paczka("2026-11-20")


if __name__ == "__main__":
    unittest.main(verbosity=1)
