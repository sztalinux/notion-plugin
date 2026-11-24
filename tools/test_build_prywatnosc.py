#!/usr/bin/env python3
"""Testy kontroli prywatności publicznego repo (`tools/build.py` i hooki `.githooks/`) na zmyślonych danych.

    python3 tools/test_build_prywatnosc.py

Hooki: kopia plików repo w katalogu tymczasowym (`<tmp>/hub/AI/dom` – folder budowy liczony domyślnie dwa poziomy
wyżej, bez DOM_HUB), zmyślona lista słów w `<tmp>/hub/.dom/zakazane-w-repo.txt`, lokalne zdalne repo `<tmp>/remote.git`.
Prawdziwa lista słów nie jest czytana. „§” rozcina zmyślone wartości w źródle, żeby sam plik testu przechodził kontrolę.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TU = Path(__file__).resolve().parent
ZRODLO = TU.parent
sys.path.insert(0, str(TU))
import build  # noqa: E402


def z(s: str) -> str:
    return s.replace("§", "")


ASCII, OGONEK, DWA = z("plumb§atek"), z("Żwir§kowo"), z("Jan Zmyś§lak")  # zmyślone wpisy listy
LISTA = f"# zmyślona lista testowa\n{ASCII}\n{OGONEK}\n{DWA}\n"
BLAD_LISTY = "słowo z listy zakazanych"


class Lista(unittest.TestCase):
    """F-3 (a), (b): dopasowanie bez ogonków na granicy słowa, wpisy wielowyrazowe – na zmyślonej liście."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="prywatnosc-lista-"))
        (cls.tmp / "lista.txt").write_text(LISTA, encoding="utf-8")
        cls.stara = build.ZAKAZANE
        build.ZAKAZANE = cls.tmp / "lista.txt"
        cls.zak = build.zakazane_slowa()

    @classmethod
    def tearDownClass(cls):
        build.ZAKAZANE = cls.stara
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def lapie(self, tekst):
        return any(BLAD_LISTY in b for b in build.sprawdz_tekst("x", z(tekst), self.zak))

    def test_lapie(self):
        for t in ("plumb§atek", "PLUMB§ATEK", "plumb§atekowi",
                  "plumb§ątek", "Plumb§ątek, sprawa", "u pana Plumb§ątek.",  # (a) wpis ASCII, w tekście ogonek
                  "Żwir§kowo", "zwir§kowo", "ZWIR§KOWO",
                  "Jan Zmyś§lak", "Jan Zmys§lak", "Zmyś§lak Jan", "Zmys§lak  Jan", "Jan-Zmyś§lak",
                  "**Jan** Zmyś§lak", "Jan_Zmyś§lak", "Jan\u00a0Zmyś§lak", "JAN ZMYŚ§LAK",
                  "Jan Zmy\u200b§ślak", "JanZmyś§lak.md", "Zmys§lak, Jan"):
            self.assertTrue(self.lapie(t), z(t))

    def test_dwie_linie(self):
        b = build.sprawdz_tekst("x", z("wstęp\nrozmowa: Jan\nZmyś§lak powiedział\nkoniec"), self.zak)
        self.assertEqual(b, ["x:2: słowo z listy zakazanych – repo jest publiczne, usuń lub uogólnij"])

    def test_zwykly_tekst_przechodzi(self):
        for t in ("Jan", "Zmyślona historia", "pan Jan i pani Ewa", "plumbum", "atek", "zaplumbowany",
                  "Żwir i kowadło", "żwirek", "kowo", "Jan Zmyślony", "N zł"):
            self.assertFalse(self.lapie(t), t)

    def test_prefiks_tokenu_tylko_doslownie(self):
        """Wpis z „_” (prefiks tokenu) nie jest rozbijany na słowa – nazwa usługi w zwykłym zdaniu przechodzi."""
        zak = self.zak + [z("abc§d_efg§h_")]
        self.assertFalse(build.sprawdz_tekst("x", z("klucz Abc§d Efg§h w komentarzu"), zak))
        self.assertTrue(build.sprawdz_tekst("x", z("abc§d_efg§h_1234"), zak))

    def test_osoba(self):
        self.assertTrue(build.sprawdz_osobe("autor", z("Plumb§ątek"), "1+x@users.noreply.github.com", self.zak))
        self.assertEqual(build.sprawdz_osobe("autor", "tester", "1+x@users.noreply.github.com", self.zak), [])


class JakoTekst(unittest.TestCase):
    """F-1: UTF-16 bez BOM czytany jako tekst, binarne → None."""

    def test_utf16_bez_bom(self):
        for kod in ("utf-16-le", "utf-16-be"):
            self.assertEqual(build.jako_tekst("notatka: zażółć gęślą\n".encode(kod)), "notatka: zażółć gęślą\n")

    def test_binarne(self):
        self.assertIsNone(build.jako_tekst(b"PK\x03\x04\x14\x00\x00\x00\x08\x00abc\x00\x01"))
        self.assertIsNone(build.jako_tekst(b"\x00\x00\x00\x01Bud1\x00\x00\x10\x00\x00\x00\x08\x00a\x00b"))


def git_env() -> dict:
    env = {k: v for k, v in os.environ.items()
           if k not in ("DOM_HUB", "DOM_BEZ_LISTY") and not k.startswith("GIT_")}
    env.update(GIT_AUTHOR_NAME="tester", GIT_COMMITTER_NAME="tester",
               GIT_AUTHOR_EMAIL="1+tester@users.noreply.github.com",
               GIT_COMMITTER_EMAIL="1+tester@users.noreply.github.com")
    return env


class Hooki(unittest.TestCase):
    """Hooki pre-commit, commit-msg i pre-push w prawdziwym repo git (katalog tymczasowy)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="prywatnosc-hooki-"))
        cls.lista = cls.tmp / "hub" / ".dom" / "zakazane-w-repo.txt"
        cls.lista.parent.mkdir(parents=True)
        cls.lista.write_text(LISTA, encoding="utf-8")
        cls.repo = cls.tmp / "hub" / "AI" / "dom"
        cls.repo.mkdir(parents=True)
        cls.env = git_env()
        pliki = subprocess.run(["git", "ls-files", "-z"], cwd=ZRODLO, capture_output=True, text=True,
                               check=True).stdout.split("\0")
        for p in filter(None, pliki):
            src, dst = ZRODLO / p, cls.repo / p
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_symlink():
                os.symlink(os.readlink(src), dst)
            elif src.is_file():
                shutil.copy2(src, dst)
        cls.git("init", "-q", "-b", "main")
        for k, v in (("core.hooksPath", ".githooks"), ("commit.gpgsign", "false"), ("tag.gpgsign", "false")):
            cls.git("config", k, v)
        cls.git("add", "-A")
        cls.git("commit", "-q", "--no-verify", "-m", "stan wyjściowy (kopia plików repo)")  # przygotowanie testu
        subprocess.run(["git", "init", "-q", "--bare", str(cls.tmp / "remote.git")], check=True, capture_output=True)
        cls.git("remote", "add", "origin", str(cls.tmp / "remote.git"))
        cls.git("push", "-q", "--no-verify", "origin", "main")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def git(cls, *args, cwd=None, sprawdz=True):
        r = subprocess.run(["git", *args], cwd=cwd or cls.repo, capture_output=True, text=True, env=cls.env)
        if sprawdz and r.returncode:
            raise AssertionError(f"git {' '.join(args)}: {r.stdout}{r.stderr}")
        return r

    def setUp(self):
        assert str(self.repo).startswith(str(self.tmp))
        self.git("checkout", "-q", "-f", "main")
        self.git("reset", "-q", "--hard", "origin/main")
        self.git("clean", "-q", "-fdx")
        self.lista.write_text(LISTA, encoding="utf-8")

    def plik(self, sciezka, tresc, cwd=None):
        p = (cwd or self.repo) / sciezka
        p.parent.mkdir(parents=True, exist_ok=True)
        (p.write_bytes if isinstance(tresc, bytes) else p.write_text)(tresc)
        return p

    def commit(self, *sciezki, wiadomosc="docs: próba", cwd=None, bez_hookow=False):
        self.git("add", "-f", "--", *sciezki, cwd=cwd)
        return self.git("commit", "-q", *(["--no-verify"] if bez_hookow else []), "-m", wiadomosc, cwd=cwd, sprawdz=False)

    def push(self, *args):
        return self.git("push", "-q", "origin", *args, sprawdz=False)

    def zablokowany(self, r, *teksty):
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, out)
        for t in teksty:
            self.assertIn(t, out)

    def przeszedl(self, r):
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    # --- ścieżki, które muszą przechodzić -------------------------------------------------------------
    def test_czysty_commit_i_push_nowej_galezi(self):
        self.plik("docs/czysty.md", "Zwykła notatka o procedurze, N zł.\n")
        self.plik(".DS_Store", b"\x00\x00\x00\x01Bud1\x00\x00\x10\x00")  # ignorowany przez git – nie blokuje
        self.przeszedl(self.commit("docs/czysty.md"))
        self.git("checkout", "-q", "-b", "czysta-galaz")
        self.przeszedl(self.push("czysta-galaz"))

    # --- F-20: pre-commit, commit-msg, pre-push --------------------------------------------------------
    def test_pre_commit_slowo_w_tresci(self):
        self.plik("docs/n.md", z(f"Rozmowa z {DWA[:3]} Zmyś§lak\n"))
        self.zablokowany(self.commit("docs/n.md"), BLAD_LISTY, "Commit zablokowany")

    def test_commit_msg(self):
        self.plik("docs/czysty.md", "Zwykła notatka.\n")
        self.zablokowany(self.commit("docs/czysty.md", wiadomosc=f"docs: ustalenia z {ASCII}"),
                         "wiadomość commita", "popraw wiadomość commita")

    def test_brak_listy_blokuje(self):
        self.lista.unlink()
        self.plik("docs/czysty.md", "Zwykła notatka.\n")
        self.zablokowany(self.commit("docs/czysty.md"), "brak listy słów zakazanych")

    def test_pre_push_nowa_galaz_bez_upstreamu(self):
        self.git("checkout", "-q", "-b", "bez-upstreamu")
        self.plik("docs/n.md", f"notatka {OGONEK}\n")
        self.przeszedl(self.commit("docs/n.md", bez_hookow=True))
        self.zablokowany(self.push("bez-upstreamu"), BLAD_LISTY, "Push zablokowany")

    def test_pre_push_scalenie_z_trescia_z_konfliktu(self):
        self.plik("docs/s.md", "linia wspólna\n")
        self.przeszedl(self.commit("docs/s.md"))
        self.git("checkout", "-q", "-b", "boczna")
        self.plik("docs/s.md", "wersja boczna\n")
        self.przeszedl(self.commit("docs/s.md"))
        self.git("checkout", "-q", "main")
        self.plik("docs/s.md", "wersja główna\n")
        self.przeszedl(self.commit("docs/s.md"))
        self.git("merge", "-q", "boczna", sprawdz=False)
        self.plik("docs/s.md", f"rozwiązane z {ASCII}\n")
        self.git("add", "docs/s.md")
        self.przeszedl(self.git("commit", "-q", "--no-verify", "--no-edit", sprawdz=False))
        self.zablokowany(self.push("HEAD:refs/heads/scalenie"), "docs/s.md:1: " + BLAD_LISTY, "Push zablokowany")

    # --- F-1: treść nieczytelna jako tekst -------------------------------------------------------------
    def test_binarne_i_nieznane(self):
        zip_bez_rozszerzenia = b"PK\x03\x04\x14\x00\x00\x00\x08\x00" + ASCII.encode() + b"\x00\x01\x02"
        for sciezka, tresc in (("docs/kosztorys.xlsm", b"PK\x03\x04 arkusz"), ("docs/kosztorys", zip_bez_rozszerzenia),
                               ("docs/notatka.txt", f"notatka {OGONEK}\n".encode("utf-16-le"))):
            with self.subTest(sciezka):
                self.setUp()
                self.plik(sciezka, tresc)
                self.zablokowany(self.commit(sciezka), "Commit zablokowany")
                self.przeszedl(self.commit(sciezka, bez_hookow=True))
                self.zablokowany(self.push("HEAD:refs/heads/binarne"), sciezka, "Push zablokowany")

    def test_utf16_bez_bom_czysty_przechodzi(self):
        self.plik("docs/notatka.txt", "Zwykła notatka w UTF-16.\n".encode("utf-16-le"))
        self.przeszedl(self.commit("docs/notatka.txt"))

    def test_ignorowany_binarny_wymuszony_do_indeksu(self):
        self.plik(".DS_Store", b"\x00\x00\x00\x01Bud1\x00\x00\x10\x00")
        self.zablokowany(self.commit(".DS_Store"), ".DS_Store", "Commit zablokowany")

    # --- F-2: nazwy plików, gałęzi, tagów i treść tagów ------------------------------------------------
    def test_nazwa_pliku(self):
        sciezka = f"docs/oferta-{ASCII}.md"
        self.plik(sciezka, "Czysta treść.\n")
        self.zablokowany(self.commit(sciezka), "(nazwa)", BLAD_LISTY)
        self.przeszedl(self.commit(sciezka, bez_hookow=True))
        self.zablokowany(self.push("HEAD:refs/heads/nazwa-pliku"), "(nazwa)", "Push zablokowany")

    def test_nazwa_galezi_na_wypchnietym_commicie(self):
        self.git("branch", f"oferta-{ASCII}")
        self.zablokowany(self.push(f"oferta-{ASCII}"), BLAD_LISTY, "Push zablokowany")
        self.zablokowany(self.push(f"HEAD:refs/heads/oferta-{OGONEK}"), BLAD_LISTY, "Push zablokowany")

    def test_tag_adnotowany(self):
        self.git("tag", "-a", "v-test", "-m", f"wydanie po rozmowie z {DWA}")
        self.zablokowany(self.push("v-test"), "tag", BLAD_LISTY, "Push zablokowany")
        self.git("tag", "-a", "v-czysty", "-m", "wydanie testowe")
        self.przeszedl(self.push("v-czysty"))
        self.git("tag", f"v-{ASCII}")
        self.zablokowany(self.push(f"v-{ASCII}"), BLAD_LISTY, "Push zablokowany")

    # --- F-17: treść z indeksu --------------------------------------------------------------------------
    def test_pre_commit_tresc_z_indeksu(self):
        self.plik("docs/probka.txt", f"notatka {OGONEK}\n")
        self.git("add", "docs/probka.txt")
        self.plik("docs/probka.txt", "czysta treść na dysku\n")
        self.zablokowany(self.git("commit", "-q", "-m", "docs: próbka", sprawdz=False), "docs/probka.txt", BLAD_LISTY)

    # --- kopia robocza git (worktree), folder budowy bez DOM_HUB --------------------------------------
    def test_worktree(self):
        wt = self.repo / ".claude" / "worktrees" / "wt"
        self.git("worktree", "add", "-q", "-b", "wt-test", str(wt))
        try:
            self.plik("docs/n.md", f"notatka {OGONEK}\n", cwd=wt)
            self.zablokowany(self.commit("docs/n.md", cwd=wt), BLAD_LISTY)
            self.plik("docs/n.md", "czysta notatka\n", cwd=wt)
            self.przeszedl(self.commit("docs/n.md", cwd=wt))
        finally:
            self.git("worktree", "remove", "--force", str(wt), sprawdz=False)
            self.git("branch", "-q", "-D", "wt-test", sprawdz=False)

    # --- F-16: odesłania do nieistniejącej procedury ---------------------------------------------------
    def test_usuniety_skill(self):
        shutil.rmtree(self.repo / "plugins" / "ja" / "skills" / "suple")
        r = subprocess.run([sys.executable, "tools/build.py", "--tylko-walidacja"], cwd=self.repo,
                           capture_output=True, text=True, env=self.env)
        self.zablokowany(r, "AGENTS.md: odesłanie do nieistniejącej procedury plugins/ja/skills/suple/SKILL.md",
                         "skills/ja/SKILL.md: mapa procedur wskazuje nieistniejącą procedurę `suple`")


if __name__ == "__main__":
    unittest.main()
