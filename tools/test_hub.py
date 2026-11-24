#!/usr/bin/env python3
"""Testy tools/hub.py (F-8): folder budowy z głównej kopii i z kopii roboczej git, DOM_HUB, odmowa zapisu z kopii
roboczej. Wszystko w katalogu tymczasowym: atrapa `<tmp>/Dom/AI/dom` (katalog .git) i kopii roboczej
`<tmp>/Dom/AI/dom/.claude/worktrees/x` (plik .git „gitdir: …/.git/worktrees/x”); prawdziwych danych nie dotyka."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TU = Path(__file__).resolve().parent
sys.path.insert(0, str(TU))
import build  # noqa: E402
import hub  # noqa: E402

# zmienne, które mogłyby skierować narzędzie poza atrapę albo zdjąć blokadę – w testach odmowy ich nie ma
OBCE = ("DOM_HUB", "BUDZET_DANE", "ZDJECIA_DANE", "KOPIA_DANE", "DYSK_DOM")


def atrapa(tmp: Path, wzgledna: bool = False) -> tuple:
    """(folder budowy, główna kopia, kopia robocza) – układ jak u inwestora, w `tmp`."""
    budowa = tmp / "Dom"
    glowna = budowa / "AI" / "dom"
    (glowna / ".git" / "worktrees" / "x").mkdir(parents=True)
    robocza = glowna / ".claude" / "worktrees" / "x"
    robocza.mkdir(parents=True)
    cel = "../../../.git/worktrees/x" if wzgledna else str(glowna / ".git" / "worktrees" / "x")
    (robocza / ".git").write_text(f"gitdir: {cel}\n", encoding="utf-8")
    return budowa.resolve(), glowna.resolve(), robocza.resolve()


class FolderBudowy(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hub-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.budowa, self.glowna, self.robocza = atrapa(self.tmp)
        env = mock.patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop("DOM_HUB", None)

    def test_glowna_kopia_dwa_poziomy_wyzej(self):
        self.assertEqual(hub.folder_budowy(self.glowna), self.budowa)
        self.assertFalse(hub.kopia_robocza(self.glowna))

    def test_kopia_robocza_trafia_w_folder_budowy(self):
        self.assertEqual(hub.folder_budowy(self.robocza), self.budowa)
        self.assertTrue(hub.kopia_robocza(self.robocza))
        self.assertNotEqual(hub.folder_budowy(self.robocza), self.glowna / ".claude")

    def test_wzgledny_gitdir(self):
        budowa, glowna, robocza = atrapa(self.tmp / "w", wzgledna=True)
        self.assertEqual(hub.folder_budowy(robocza), budowa)
        self.assertTrue(hub.kopia_robocza(robocza))

    def test_dom_hub_ustawione_puste_nieustawione(self):
        inny = self.tmp / "inny"
        os.environ["DOM_HUB"] = str(inny)
        self.assertEqual(hub.folder_budowy(self.robocza), inny.resolve())
        self.assertEqual(hub.domyslny_hub(self.robocza), self.budowa)  # zabezpieczenia nie idą za DOM_HUB
        os.environ["DOM_HUB"] = ""
        self.assertEqual(hub.folder_budowy(self.robocza), self.budowa)
        del os.environ["DOM_HUB"]
        self.assertEqual(hub.folder_budowy(self.robocza), self.budowa)

    def test_zgodnosc_z_build(self):
        budowa2, glowna2, robocza2 = atrapa(self.tmp / "w", wzgledna=True)
        prawdziwe = TU.parent
        for root in (self.glowna, self.robocza, glowna2, robocza2, prawdziwe):
            with self.subTest(root=str(root)):
                self.assertEqual(hub.glowna_kopia(root).resolve(), build.glowna_kopia(root).resolve())
                self.assertEqual(hub.folder_budowy(root), build.glowna_kopia(root).parent.parent.resolve())

    def test_tylko_odczyt(self):
        dane = self.budowa / ".dom" / "x"
        self.assertTrue(hub.tylko_odczyt(self.robocza, dane))
        self.assertTrue(hub.tylko_odczyt(self.robocza, self.budowa))
        self.assertFalse(hub.tylko_odczyt(self.glowna, dane))                # główna kopia – zapis normalny
        self.assertFalse(hub.tylko_odczyt(self.robocza, self.tmp / "gdzie"))  # cel poza folderem budowy (np. BUDZET_DANE)
        os.environ["DOM_HUB"] = str(self.budowa)
        self.assertFalse(hub.tylko_odczyt(self.robocza, dane))               # jawne DOM_HUB – decyzja wywołującego

    def test_zapis_zablokowany_wypisuje_jedna_linie(self):
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertTrue(hub.zapis_zablokowany(self.robocza, self.budowa / ".dom"))
            self.assertFalse(hub.zapis_zablokowany(self.glowna, self.budowa / ".dom"))
        self.assertEqual(out.getvalue(), hub.ODMOWA + "\n")


if __name__ == "__main__":
    unittest.main(verbosity=1)
