#!/usr/bin/env python3
"""Testy `wiedza.py publikuj --narzedzia` (opublikuj_narzedzia) na podstawionym GitHubie – bez sieci i sekretów.

    python3 tools/test_wiedza_narzedzia.py
"""
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wiedza as W  # noqa: E402

SEKRETY = {"GITHUB_TOKEN_SYNC": "t", "GITHUB_REPO": "wlasciciel/kopia"}


class GitHub:
    """Zdalne pliki {ścieżka: bajty}; zapisuje PUT-y."""

    def __init__(self, pliki=None, prywatne=True):
        self.pliki, self.prywatne, self.puty = dict(pliki or {}), prywatne, []

    def __call__(self, metoda, url, naglowki, dane=None, timeout=20, termin=None):
        if url.endswith("/repos/wlasciciel/kopia"):
            return {"private": self.prywatne, "visibility": "private" if self.prywatne else "public",
                    "default_branch": "main"}
        sciezka = url.split("/contents/", 1)[1]
        if metoda == "GET":
            if sciezka not in self.pliki:
                raise W.BladHttp(404)
            return {"sha": W.git_blob_sha(self.pliki[sciezka])}
        self.puty.append(sciezka)
        self.pliki[sciezka] = W.base64.b64decode(dane["content"])
        return {}


class Narzedzia(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runner = Path(self.tmp.name) / "runner.py"
        self.runner.write_text("print('nowy')\n")
        self.pytania = Path(self.tmp.name) / "pytania.py"
        self.pytania.write_text("print('pytania')\n")

    def tearDown(self):
        self.tmp.cleanup()

    def uruchom(self, gh, pliki):
        with mock.patch.object(W, "zadanie_http", gh), redirect_stdout(io.StringIO()) as out:
            return W.opublikuj_narzedzia(pliki, SEKRETY), out.getvalue()

    def test_wysyla_rozne_pomija_zgodne(self):
        gh = GitHub({"narzedzia/runner.py": b"print('stary')\n", "narzedzia/pytania.py": self.pytania.read_bytes()})
        ok, out = self.uruchom(gh, [self.runner, self.pytania])
        self.assertTrue(ok)
        self.assertEqual(gh.puty, ["narzedzia/runner.py"])
        self.assertEqual(gh.pliki["narzedzia/runner.py"], self.runner.read_bytes())
        self.assertIn("wysłano 1 (runner.py) · zgodne pytania.py", out)
        self.assertNotIn("wlasciciel", out)

    def test_nowy_plik(self):
        gh = GitHub()
        ok, _ = self.uruchom(gh, [self.pytania])
        self.assertTrue(ok)
        self.assertEqual(gh.puty, ["narzedzia/pytania.py"])

    def test_repo_nieprywatne_nic_nie_wysyla(self):
        gh = GitHub(prywatne=False)
        ok, _ = self.uruchom(gh, [self.runner])
        self.assertFalse(ok)
        self.assertEqual(gh.puty, [])

    def test_obca_nazwa_odrzucona(self):
        inny = Path(self.tmp.name) / "wiedza.py"
        inny.write_text("x\n")
        gh = GitHub()
        ok, out = self.uruchom(gh, [self.runner, inny])
        self.assertFalse(ok)
        self.assertEqual(gh.puty, [])
        self.assertIn("dozwolone pliki", out)


if __name__ == "__main__":
    unittest.main()
