#!/usr/bin/env python3
"""Testy tools/kopie.py na zmyślonym folderze budowy (repozytoria w katalogu tymczasowym, bez sieci).

    python3 tools/test_kopie.py
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

HUB = Path(tempfile.mkdtemp(prefix="kopie-test-"))
os.environ["DOM_HUB"] = str(HUB)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kopie as K  # noqa: E402

DZIS = date(2026, 11, 20)
GIT_ENV = {**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test",
           "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test"}


def sh(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, env=GIT_ENV)


def repo(nazwa: str, zdalne: bool, przed: int = 0, brudne: bool = False) -> Path:
    d = HUB / "AI" / nazwa
    d.mkdir(parents=True)
    sh("git", "init", "-q", "-b", "main", cwd=d)
    (d / "a.txt").write_text("a")
    sh("git", "add", "a.txt", cwd=d)
    sh("git", "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "start", cwd=d)
    if zdalne:
        goly = HUB / "zdalne" / f"{nazwa}.git"
        sh("git", "init", "-q", "--bare", str(goly), cwd=HUB)
        sh("git", "remote", "add", "origin", str(goly), cwd=d)
        sh("git", "push", "-q", "-u", "origin", "main", cwd=d)
    for i in range(przed):
        (d / f"n{i}.txt").write_text(str(i))
        sh("git", "add", ".", cwd=d)
        sh("git", "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", f"n{i}", cwd=d)
    if brudne:
        (d / "zmiana.txt").write_text("x")
    return d


class Repozytoria(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo("czyste", zdalne=True)
        repo("przed", zdalne=True, przed=2)
        repo("brudne", zdalne=True, brudne=True)
        repo("lokalne", zdalne=False)
        (HUB / "AI" / "archiwum").mkdir()
        (HUB / "AI" / ".ukryty").mkdir()
        cls.wynik = {p["klucz"]: p for p in K.repozytoria(HUB)}

    def test_stany(self):
        w = self.wynik
        self.assertEqual(w["repo:czyste"]["stan"], "✓")
        self.assertEqual(w["repo:przed"]["stan"], "⚠")
        self.assertIn("niewypchnięte commity: 2", w["repo:przed"]["szczegol"])
        self.assertEqual(w["repo:brudne"]["stan"], "⚠")
        self.assertIn("niezacommitowane pliki: 1", w["repo:brudne"]["szczegol"])
        self.assertEqual(w["repo:lokalne"]["stan"], "✗")
        self.assertEqual(w["repo:archiwum"]["stan"], "✗")
        self.assertNotIn("repo:.ukryty", w)

    def test_dysk_zewnetrzny_obejmuje_katalogi_bez_zdalnego(self):
        w = {p["klucz"]: p for p in K.repozytoria(HUB, "2026-11-18")}
        self.assertEqual(w["repo:archiwum"]["stan"], "✓")
        self.assertEqual(w["repo:lokalne"]["kiedy"], "2026-11-18")
        self.assertEqual(w["repo:przed"]["stan"], "⚠")  # dysk zewnętrzny nie zastępuje pushu

    def test_bez_blokady_indeksu(self):
        self.assertFalse((HUB / "AI" / "czyste" / ".git" / "index.lock").exists())


class Reczne(unittest.TestCase):
    def test_terminy(self):
        rej = {"notion": (DZIS - timedelta(days=31)).isoformat(), "zdjecia": (DZIS - timedelta(days=5)).isoformat(),
               "sekrety": "2026-01-01"}
        w = {p["klucz"]: p["stan"] for p in K.reczne(rej, DZIS)}
        self.assertEqual(w["notion"], "⚠")
        self.assertEqual(w["zdjecia"], "✓")
        self.assertEqual(w["sekrety"], "✓")  # jednorazowe – bez terminu
        self.assertEqual(w["dysk-zewnetrzny"], "✗")


class Kosztorys(unittest.TestCase):
    def test_brak_i_swiezy(self):
        self.assertEqual(K.kosztorys(HUB, DZIS)["stan"], "✗")
        p = HUB / "Koszty" / "Kosztorys_google.json"
        p.parent.mkdir(exist_ok=True)
        p.write_text("{}")
        self.assertEqual(K.kosztorys(HUB, date.today())["stan"], "✓")
        self.assertEqual(K.kosztorys(HUB, date.today() + timedelta(days=5))["stan"], "⚠")


class Dokumenty(unittest.TestCase):
    def test_tylko_odczyt_stanu(self):
        self.assertEqual(K.dokumenty(HUB, DZIS)["stan"], "✗")
        st = HUB / ".dom" / "kopia" / "stan.json"
        st.parent.mkdir(parents=True, exist_ok=True)
        (HUB / "Projekty").mkdir(exist_ok=True)
        (HUB / "Projekty" / "a.pdf").write_text("x")
        st.write_text(json.dumps({"potwierdzone": {}, "potwierdzono": "2026-11-01", "paczki": []}))
        przed = st.read_bytes()
        w = K.dokumenty(HUB, DZIS)
        self.assertEqual(w["stan"], "⚠")  # 1 nowy plik, kopia starsza niż 7 dni
        self.assertIn("zmian od kopii: 1", w["szczegol"])
        self.assertEqual(st.read_bytes(), przed)
        self.assertEqual(K.dokumenty(HUB, date(2026, 11, 5))["stan"], "✓")


class Cicho(unittest.TestCase):
    def test_linia(self):
        self.assertEqual(K.linia_cicha([K.poz("a", "✓", "a"), K.poz("b", "ℹ", "b")]), "")
        linia = K.linia_cicha([K.poz("a", "✓", "a"), K.poz("b", "⚠", "b"), K.poz("c", "✗", "c")])
        self.assertEqual(linia, "[kopie] ✓ 1 · ⚠ 1 (b) · ✗ 1 (c)")


class Potwierdz(unittest.TestCase):
    def test_zapis_i_zla_data(self):
        self.assertEqual(K.main(["potwierdz", "notion", "2026-11-02"]), 0)
        self.assertEqual(K.wczytaj_rejestr(HUB)["notion"], "2026-11-02")
        self.assertEqual(K.main(["potwierdz", "notion", "2999-01-01"]), 1)
        self.assertEqual(K.main(["potwierdz", "notion", "jutro"]), 1)
        self.assertEqual(K.wczytaj_rejestr(HUB)["notion"], "2026-11-02")


if __name__ == "__main__":
    unittest.main(verbosity=1)
