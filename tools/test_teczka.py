#!/usr/bin/env python3
"""Testy tools/teczka.py na zmyślonym folderze budowy (bez Dysku i Notion).

    python3 tools/test_teczka.py
"""
import sys
import tempfile
import unicodedata
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import teczka as T  # noqa: E402

OD, DO, DZIS = date(2026, 11, 2), date(2026, 11, 20), date(2026, 11, 25)


def hub_z_plikami(pliki):
    hub = Path(tempfile.mkdtemp(prefix="teczka-test-"))
    for rel in pliki:
        p = hub / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(rel.encode())
    return hub


KOMPLET = ["Umowy/Protokoły/2026-11-21_odbior-plyty.pdf", "Faktury/2026/2026-11-05_hurtownia_FV1.jpg",
           "Faktury/2026/2026-12-01_hurtownia_FV9.jpg", "Dziennik budowy KB/2026-11-10_strona-1.jpg",
           "Dostawy/Etap A/2026-11-06_WZ_beton.jpg", "Dostawy/Etap B/2026-12-01_WZ.jpg"]


class Data(unittest.TestCase):
    def test_z_nazwy(self):
        self.assertEqual(T.data_z_nazwy("2026-11-05_a.jpg"), date(2026, 11, 5))
        self.assertEqual(T.data_z_nazwy("2026-11-05~_a.jpg"), date(2026, 11, 5))
        self.assertIsNone(T.data_z_nazwy("faktura.jpg"))
        self.assertIsNone(T.data_z_nazwy("2026-13-45_a.jpg"))


class Zbieranie(unittest.TestCase):
    def test_wybor_wg_dat_i_etapu(self):
        w = T.zbierz(self.hub(KOMPLET), "Etap A", OD, DO, zdjecia=["Krok 1=https://dysk/x"])
        nazwy = {k: [p.name for p in v] for k, v in w["skladniki"].items()}
        self.assertEqual(nazwy["protokoly"], ["2026-11-21_odbior-plyty.pdf"])  # po --do, ale w zapasie 14 dni
        self.assertEqual(nazwy["faktury"], ["2026-11-05_hurtownia_FV1.jpg"])  # grudniowa poza okresem
        self.assertEqual(nazwy["kb"], ["2026-11-10_strona-1.jpg"])
        self.assertEqual(nazwy["dostawy"], ["2026-11-06_WZ_beton.jpg"])  # tylko folder tego etapu
        self.assertEqual(w["braki"], [])

    def hub(self, pliki):
        return hub_z_plikami(pliki)

    def test_brak_protokolu_to_ostrzezenie(self):
        w = T.zbierz(hub_z_plikami([p for p in KOMPLET if "Protokoły" not in p]), "Etap A", OD, DO, zdjecia=["a=b"])
        self.assertTrue(any(b.startswith("BRAK protokołu odbioru") for b in w["braki"]))

    def test_protokol_poza_zapasem_nie_wchodzi(self):
        w = T.zbierz(hub_z_plikami(["Umowy/Protokoły/2026-12-20_x.pdf"]), "Etap A", OD, DO)
        self.assertEqual(w["skladniki"]["protokoly"], [])

    def test_pusty_folder_budowy_daje_komplet_brakow(self):
        w = T.zbierz(hub_z_plikami([]), "Etap A", OD, DO)
        self.assertEqual(len(w["braki"]), 5)  # protokół, faktury, KB, dostawy, zdjęcia

    def test_bez_daty_nie_wchodzi_i_jest_wypisany(self):
        w = T.zbierz(hub_z_plikami(KOMPLET + ["Faktury/2026/skan.jpg"]), "Etap A", OD, DO)
        self.assertEqual([p.name for p in w["bez_daty"]], ["skan.jpg"])
        self.assertNotIn("skan.jpg", [p.name for p in w["skladniki"]["faktury"]])

    def test_pliki_ukryte_i_tymczasowe_pomijane(self):
        w = T.zbierz(hub_z_plikami(["Faktury/2026/2026-11-05_a.jpg", "Faktury/2026/.DS_Store",
                                     "Faktury/2026/~$2026-11-06_b.docx"]), "Etap A", OD, DO)
        self.assertEqual([p.name for p in w["skladniki"]["faktury"]], ["2026-11-05_a.jpg"])

    def test_nfd_nazwa_folderu_dziala(self):
        nfd = unicodedata.normalize("NFD", "Umowy/Protokoły/2026-11-10_x.pdf")
        w = T.zbierz(hub_z_plikami([nfd]), "Etap A", OD, DO)
        self.assertEqual(len(w["skladniki"]["protokoly"]), 1)

    def test_dodaj_tylko_z_folderu_budowy(self):
        hub = hub_z_plikami(["Umowy/umowa.pdf", ".dom/sekrety.env", "AI/dom/x.md"])
        w = T.zbierz(hub, "Etap A", OD, DO, dodaj=["Umowy/umowa.pdf", ".dom/sekrety.env", "AI/dom/x.md",
                                                    "../poza.txt", "Umowy/nie-ma.pdf"])
        self.assertEqual([p.name for p in w["skladniki"]["dodatkowe"]], ["umowa.pdf"])
        self.assertEqual(len(w["uwagi"]), 4)

    def test_zle_daty(self):
        with self.assertRaises(ValueError):
            T.zbierz(hub_z_plikami([]), "Etap A", DO, OD)


class Skladanie(unittest.TestCase):
    def test_na_sucho_nic_nie_tworzy(self):
        hub = hub_z_plikami(KOMPLET)
        z = T.zloz(hub, T.zbierz(hub, "Etap A", OD, DO), DZIS, False)
        self.assertFalse((hub / "Teczki").exists())
        self.assertEqual(len(z["skopiowane"]["faktury"]), 1)

    def test_wykonaj_kopiuje_i_zostawia_zrodla(self):
        hub = hub_z_plikami(KOMPLET)
        w = T.zbierz(hub, "Etap A", OD, DO, zdjecia=["Krok 1=https://dysk/x"])
        z = T.zloz(hub, w, DZIS, True)
        cel = z["folder"]
        self.assertEqual(cel.relative_to(hub.resolve()).as_posix(), "Teczki/Etap A/2026-11-25")
        self.assertTrue((cel / "2 Faktury" / "2026-11-05_hurtownia_FV1.jpg").exists())
        self.assertTrue((hub / "Faktury/2026/2026-11-05_hurtownia_FV1.jpg").exists())
        spis = (cel / "SPIS.md").read_text(encoding="utf-8")
        self.assertIn("do potwierdzenia z umową kredytową", spis)
        self.assertIn("https://dysk/x", spis)

    def test_druga_teczka_tego_samego_dnia_nie_nadpisuje(self):
        hub = hub_z_plikami(KOMPLET)
        w = T.zbierz(hub, "Etap A", OD, DO)
        pierwsza = T.zloz(hub, w, DZIS, True)["folder"]
        (pierwsza / "SPIS.md").write_text("moje uwagi", encoding="utf-8")
        druga = T.zloz(hub, w, DZIS, True)["folder"]
        self.assertEqual(druga.name, "2026-11-25_2")
        self.assertEqual((pierwsza / "SPIS.md").read_text(encoding="utf-8"), "moje uwagi")

    def test_ta_sama_nazwa_w_dziale_dostaje_sufiks(self):
        hub = hub_z_plikami(["Faktury/2026/2026-11-05_a.jpg", "Faktury/2027/2026-11-05_a.jpg"])
        z = T.zloz(hub, T.zbierz(hub, "Etap A", OD, DO), DZIS, True)
        self.assertEqual([c for c, _ in z["skopiowane"]["faktury"]],
                         ["2 Faktury/2026-11-05_a.jpg", "2 Faktury/2026-11-05_a_2.jpg"])

    def test_nazwa_etapu_bez_znakow_sciezki(self):
        self.assertEqual(T.bezpieczna_nazwa("Stan zero / SSO: A"), "Stan zero - SSO- A")


if __name__ == "__main__":
    unittest.main()
