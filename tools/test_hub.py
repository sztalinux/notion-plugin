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


def srodowisko(**dodatki) -> dict:
    """Środowisko procesu bez zmiennych, które kierują dane gdzie indziej (DOM_HUB, *_DANE, adres arkusza, atrapy)."""
    env = {k: v for k, v in os.environ.items()
           if k not in OBCE and not k.startswith(("WIEDZA_", "BUDZET_ARKUSZ_", "WYDATKI_"))}
    env.update(dodatki)
    return env


class Narzedzia(unittest.TestCase):
    """Prawdziwe narzędzia skopiowane do atrapy głównej kopii i kopii roboczej; procesy bez DOM_HUB."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="hub-narz-")).resolve()
        cls.budowa, cls.glowna, cls.robocza = atrapa(cls.tmp)
        bez = shutil.ignore_patterns("__pycache__", "test_*")
        for kopia in (cls.glowna, cls.robocza):
            shutil.copytree(TU, kopia / "tools", ignore=bez)
        (cls.tmp / "wejscie.txt").write_text("", encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def uruchom(self, kopia: Path, *argv, **env) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(kopia / "tools" / argv[0]), *argv[1:]], cwd=str(self.tmp),
                              env=srodowisko(**env), capture_output=True, text=True, timeout=60)

    def bez_sladu(self):
        self.assertFalse((self.budowa / ".dom").exists(), "zapis w folderze budowy z kopii roboczej")
        self.assertFalse((self.glowna / ".claude" / ".dom").exists(), "śmieciowe .dom w AI/dom/.claude (F-8)")

    def test_folder_budowy_wszystkich_narzedzi(self):
        kod = ("import sys; sys.path[:0] = [sys.argv[1], sys.argv[1] + '/budzet']\n"
               "import dokumenty, kopia, kopie, teczka, wiedza, zdjecia, wspolne\n"
               "print({str(m.HUB) for m in (dokumenty, kopia, kopie, teczka, wiedza, zdjecia, wspolne)})")
        r = subprocess.run([sys.executable, "-c", kod, str(self.robocza / "tools")], cwd=str(self.tmp),
                           env=srodowisko(), capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), repr({str(self.budowa)}))
        self.bez_sladu()

    def test_odmowa_zapisu_z_kopii_roboczej(self):
        polecenia = [
            ("zdjecia.py", "rozloz", "--wykonaj"), ("zdjecia.py", "cofnij"), ("zdjecia.py", "odblokuj"),
            ("kopia.py", "paczka", "--wykonaj"), ("kopia.py", "wgrane"), ("kopia.py", "aplikacja", "--wykonaj"),
            ("kopie.py", "potwierdz", "notion"),
            ("teczka.py", "zbierz", "--etap", "x", "--od", "2026-01-01", "--do", "2026-01-02", "--wykonaj"),
            ("dokumenty.py",), ("dokumenty.py", "wgrane"), ("dokumenty.py", "ustaw", "a.pdf", "--opis", "x"),
            ("wydatki.py", "sync"), ("wydatki.py", "sesja", "--zablokuj"), ("wydatki.py", "pobierz"),
            ("wiedza_karty.py", "zapisz"), ("wiedza_jakosc.py", "raport"), ("migawka.py",),
            ("budzet/wpis.py", "dodaj", "10, zak", "--data", "2026-12-05", "--id", "t1"),
            ("budzet/importuj.py", "--miesiac", "2026-11", "--arkusz", "a.json"),
            ("budzet/przenies.py", "--miesiac", "2026-11"), ("budzet/strona.py",),
            ("budzet/allegro.py", str(self.tmp / "wejscie.txt"), "a.json"),
            ("budzet/arkusz_budzetu.py", "sync"),
            ("budzet/paragon.py", "pobierz", "--url", "x", "--data", "2026-12-05", "--id", "p1"),
        ]
        for argv in polecenia:
            with self.subTest(polecenie=" ".join(argv)):
                r = self.uruchom(self.robocza, *argv)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertEqual(r.stdout.strip(), hub.ODMOWA)
                self.bez_sladu()

    def test_tryby_tylko_czytajace_dzialaja(self):
        r = self.uruchom(self.robocza, "kopia.py", "stan")  # F-8: dawniej zapisywał .claude/.dom/kopia/stan.json
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn(hub.ODMOWA, r.stdout)
        r = self.uruchom(self.robocza, "wiedza.py", "sync")  # sync z kopii roboczej nadal nic nie robi
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("worktree", r.stdout)
        for argv in (("zdjecia.py", "stan"), ("budzet/wpis.py", "lista", "2026-12"),
                     ("wydatki.py", "sesja"), ("budzet/arkusz_budzetu.py", "kod")):
            with self.subTest(polecenie=" ".join(argv)):
                r = self.uruchom(self.robocza, *argv)
                self.assertNotIn(hub.ODMOWA, r.stdout)
        self.bez_sladu()

    def test_jawne_dane_poza_folderem_budowy(self):
        dane = self.tmp / "dane-budzetu"
        r = self.uruchom(self.robocza, "budzet/wpis.py", "dodaj", "10, zak", "--data", "2026-12-05", "--id", "t1",
                         BUDZET_DANE=str(dane))
        self.assertNotIn(hub.ODMOWA, r.stdout)
        inny = self.tmp / "inny-hub"
        r = self.uruchom(self.robocza, "kopie.py", "potwierdz", "notion", DOM_HUB=str(inny))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((inny / ".dom" / "kopie-zapasowe.json").is_file())
        self.bez_sladu()


class GlownaKopia(unittest.TestCase):
    def test_glowna_kopia_zapisuje_w_folderze_budowy(self):
        tmp = Path(tempfile.mkdtemp(prefix="hub-glowna-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        budowa, glowna, _ = atrapa(tmp)
        shutil.copytree(TU, glowna / "tools", ignore=shutil.ignore_patterns("__pycache__", "test_*"))
        r = subprocess.run([sys.executable, str(glowna / "tools" / "kopie.py"), "potwierdz", "notion"], cwd=str(tmp),
                           env=srodowisko(), capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((budowa / ".dom" / "kopie-zapasowe.json").is_file())
        self.assertFalse((glowna / ".claude" / ".dom").exists())


if __name__ == "__main__":
    unittest.main(verbosity=1)
