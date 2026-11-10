#!/usr/bin/env python3
"""Testy tools/zdjecia.py na zmyślonych plikach i krokach (bez Dysku, bez Notion).

    python3 tools/test_zdjecia.py
"""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

TMP = tempfile.mkdtemp(prefix="zdjecia-test-")
os.environ["ZDJECIA_DANE"] = str(Path(TMP) / "dane")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import zdjecia as Z  # noqa: E402

KONF = {
    "etap": "Etap A",
    "kroki": [
        {"nazwa": "01 Wykop i odbiór dna", "folder": "Zdjęcia/Etap A/01 Wykop i odbiór dna"},
        {"nazwa": "02 Podkład betonowy, folia", "folder": "Zdjęcia/Etap A/02 Podkład betonowy, folia"},
        {"nazwa": "03 Zbrojenie płyty", "folder": "Zdjęcia/Etap A/03 Zbrojenie płyty"},
        {"nazwa": "04 Zbrojenie ścian", "folder": "Zdjęcia/Etap A/04 Zbrojenie ścian"},
    ],
    "tematy": ["Przyłącza"],
    "dni": {"2026-11-18": ["03 Zbrojenie płyty"], "2026-11-19": ["03 Zbrojenie płyty", "04 Zbrojenie ścian"]},
}
TERAZ = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)
STARE = "2026-11-20T10:00:00Z"


def plik(nazwa, folder="", rozmiar=100, utworzono=STARE, zmieniono=None, zrobiono=None, i=[0]):
    i[0] += 1
    return {"id": f"f{i[0]}", "nazwa": nazwa, "folder": folder, "rozmiar": rozmiar, "utworzono": utworzono,
            "zmieniono": zmieniono or utworzono, "zrobiono": zrobiono}


def plan(nowe, istniejace=None, konf=KONF):
    return Z.planuj({"nowe": nowe, "istniejace": istniejace or []}, konf, TERAZ)


class Daty(unittest.TestCase):
    def test_pixel_utc_na_polski(self):
        # 23:30 UTC 17.11 = 00:30 18.11 w Polsce – dzień liczony po polsku
        self.assertEqual(Z.data_zrobienia({"nazwa": "PXL_20261117_233000123.jpg"})[:2], ("2026-11-18", False))

    def test_img_lokalny(self):
        self.assertEqual(Z.data_zrobienia({"nazwa": "IMG_20261118_081500.heic"})[0], "2026-11-18")

    def test_exif_wygrywa(self):
        d = Z.data_zrobienia({"nazwa": "PXL_20261101_100000000.jpg", "zrobiono": "2026-11-18T09:00:00+01:00"})
        self.assertEqual(d, ("2026-11-18", False, "exif"))

    def test_brak_daty_w_pliku_data_wgrania(self):
        d = Z.data_zrobienia({"nazwa": "zdjecie.jpg", "utworzono": "2026-11-18T23:30:00Z"})
        self.assertEqual(d, ("2026-11-19", True, "wgranie"))

    def test_komunikator(self):
        self.assertEqual(Z.data_zrobienia({"nazwa": "Image 2026-11-18 at 14.02.11.jpeg"})[0], "2026-11-18")

    def test_prefiks_nie_dublowany_i_tylda_poprawiana(self):
        self.assertEqual(Z.nowa_nazwa("2026-11-18_a.jpg", "2026-11-18", False), "2026-11-18_a.jpg")
        self.assertEqual(Z.nowa_nazwa("2026-11-19~_a.jpg", "2026-11-18", False), "2026-11-18_a.jpg")
        self.assertEqual(Z.nowa_nazwa("2026-11-19~_a.jpg", "2026-11-19", True), "2026-11-19~_a.jpg")
        self.assertEqual(Z.nowa_nazwa("a.jpg", "2026-11-19", True), "2026-11-19~_a.jpg")


class Dopasowanie(unittest.TestCase):
    def test_numer(self):
        self.assertEqual(Z.dopasuj_krok("krok 3 z miarą", KONF["kroki"])[0]["nazwa"], "03 Zbrojenie płyty")

    def test_slowa_bez_polskich_znakow(self):
        self.assertEqual(Z.dopasuj_krok("zbrojenie plyty", KONF["kroki"])[0]["nazwa"], "03 Zbrojenie płyty")

    def test_nfd_nazwa(self):
        import unicodedata
        nfd = unicodedata.normalize("NFD", "zbrojenie płyty")
        self.assertEqual(Z.dopasuj_krok(nfd, KONF["kroki"])[0]["nazwa"], "03 Zbrojenie płyty")

    def test_remis_nie_zgaduje(self):
        k, powod = Z.dopasuj_krok("zbrojenie", KONF["kroki"])
        self.assertIsNone(k)
        self.assertIn("kilka kroków", powod)

    def test_zaden(self):
        self.assertIsNone(Z.dopasuj_krok("wakacje nad morzem", KONF["kroki"])[0])

    def test_spacja_na_koncu(self):
        self.assertEqual(Z.dopasuj_krok("wykop ", KONF["kroki"])[0]["nazwa"], "01 Wykop i odbiór dna")


class Plan(unittest.TestCase):
    def test_folder_kroku_i_przed_zakryciem(self):
        p = plan([plik("PXL_20261118_090000000.jpg", "zbrojenie plyty przed zakryciem")])
        r = p["ruchy"][0]
        self.assertEqual(r["do"], "Zdjęcia/Etap A/03 Zbrojenie płyty/przed zakryciem")
        self.assertEqual(r["nowa_nazwa"], "2026-11-18_PXL_20261118_090000000.jpg")
        self.assertEqual(p["puste_foldery"][0]["do"], Z.ARCH_PUSTE)

    def test_luzem_jeden_krok_dnia(self):
        p = plan([plik("PXL_20261118_090000000.jpg")])
        self.assertEqual(p["ruchy"][0]["do"], "Zdjęcia/Etap A/03 Zbrojenie płyty")
        self.assertEqual(p["puste_foldery"], [])

    def test_luzem_dwa_kroki_dnia_czeka(self):
        p = plan([plik("PXL_20261119_090000000.jpg")])
        self.assertEqual(p["ruchy"], [])
        self.assertIn("kilka kroków", p["czeka"][0]["powod"])
        self.assertEqual(len(p["pytania"]), 1)

    def test_luzem_brak_wpisu_dnia(self):
        p = plan([plik("PXL_20261110_090000000.jpg")])
        self.assertIn("brak wpisu", p["czeka"][0]["powod"])

    def test_wgrywanie_trwa(self):
        p = plan([plik("a.jpg", "wykop", zmieniono="2026-11-20T11:55:00Z"), plik("b.jpg", "wykop")])
        self.assertEqual(p["ruchy"], [])
        self.assertEqual(len(p["czeka"]), 2)
        self.assertEqual(p["pytania"], [])

    def test_duplikat_i_kolizja(self):
        ist = [{"folder": "Zdjęcia/Etap A/01 Wykop i odbiór dna", "nazwa": "2026-11-18_a.jpg", "rozmiar": 100},
               {"folder": "Zdjęcia/Etap A/01 Wykop i odbiór dna", "nazwa": "2026-11-18_b.jpg", "rozmiar": 5}]
        p = plan([plik("2026-11-18_a.jpg", "wykop", rozmiar=100), plik("2026-11-18_b.jpg", "wykop", rozmiar=100)], ist)
        ruchy = {r["nazwa"]: r for r in p["ruchy"]}
        self.assertEqual(ruchy["2026-11-18_a.jpg"]["do"], Z.ARCH_DUP)
        self.assertEqual(ruchy["2026-11-18_b.jpg"]["nowa_nazwa"], "2026-11-18_b_2.jpg")
        self.assertEqual(p["podsumowanie"]["duplikaty"], 1)

    def test_dwa_takie_same_w_jednym_przebiegu(self):
        p = plan([plik("x.jpg", "wykop", zrobiono="2026-11-18T09:00:00+01:00", rozmiar=7),
                  plik("x.jpg", "wykop/seria", zrobiono="2026-11-18T09:00:00+01:00", rozmiar=8)])
        nazwy = sorted(r["nowa_nazwa"] for r in p["ruchy"])
        self.assertEqual(nazwy, ["2026-11-18_x.jpg", "2026-11-18_x_2.jpg"])

    def test_faktura(self):
        p = plan([plik("PXL_20261118_090000000.jpg", "faktura beton")])
        self.assertEqual(p["ruchy"][0]["do"], "Faktury/2026")
        self.assertEqual(p["ruchy"][0]["rodzaj"], "faktura")

    def test_wz_do_dostaw_etapu(self):
        p = plan([plik("IMG_20261118_100000.jpg", "WZ stal")])
        self.assertEqual(p["ruchy"][0]["do"], "Dostawy/Etap A")

    def test_dziennik_kb(self):
        p = plan([plik("IMG_20261118_100000.jpg", "dziennik KB")])
        self.assertEqual(p["ruchy"][0]["do"], "Dziennik budowy KB")

    def test_temat(self):
        p = plan([plik("IMG_20261118_100000.jpg", "przyłącza prąd")])
        self.assertEqual(p["ruchy"][0]["do"], "Zdjęcia/Przyłącza")

    def test_prywatne_zostaja(self):
        p = plan([plik("IMG_20261118_100000.jpg", "urodziny")])
        self.assertEqual(p["ruchy"], [])
        self.assertTrue(p["pytania"])

    def test_film_razem_ze_zdjeciem(self):
        p = plan([plik("PXL_20261118_090000000.jpg", "wykop"), plik("PXL_20261118_090000000.mp4", "wykop")])
        self.assertEqual({r["do"] for r in p["ruchy"]}, {"Zdjęcia/Etap A/01 Wykop i odbiór dna"})
        self.assertTrue(any(r["film"] for r in p["ruchy"]))

    def test_pliki_tymczasowe_pomijane(self):
        p = plan([plik(".DS_Store", "wykop"), plik("a.jpg.part", "wykop")])
        self.assertEqual(p["ruchy"] + p["czeka"], [])

    def test_ponowny_przebieg_bez_zmian(self):
        p1 = plan([plik("PXL_20261118_090000000.jpg", "wykop")])
        r = p1["ruchy"][0]
        ist = [{"folder": r["do"], "nazwa": r["nowa_nazwa"], "rozmiar": 100}]
        p2 = plan([], ist)
        self.assertEqual(p2["ruchy"], [])

    def test_slad_i_pole(self):
        p = plan([plik("PXL_20261118_090000000.jpg", "wykop"), plik("PXL_20261118_100000000.jpg", "wykop"),
                  plik("PXL_20261118_110000000.jpg", "zbrojenie plyty z miarą"),
                  plik("PXL_20261118_120000000.jpg", "faktura")])
        s = Z.slad(p)["2026-11-18"]
        self.assertEqual(s["lacznie"], 3)
        self.assertEqual(s["przed_zakryciem"], 1)
        self.assertEqual(len(s["dokumenty"]), 1)
        pole = Z.pole_zdjecia(s, {"Zdjęcia/Etap A/01 Wykop i odbiór dna": "https://example.invalid/f1"})
        self.assertTrue(pole.startswith("3 zdjęć: "))
        self.assertIn("01 Wykop i odbiór dna (2) https://example.invalid/f1", pole)


class Lokalnie(unittest.TestCase):
    def setUp(self):
        self.hub = Path(tempfile.mkdtemp(prefix="hub-", dir=TMP))
        n = self.hub / "Zdjęcia" / "_nowe"
        (n / "wykop").mkdir(parents=True)
        (n / "wykop" / "PXL_20261118_090000000.jpg").write_bytes(b"a" * 10)
        (n / "nieznane").mkdir()
        (n / "nieznane" / "PXL_20261118_090000000.jpg").write_bytes(b"b" * 10)
        stare = datetime(2026, 11, 20, 10, tzinfo=timezone.utc).timestamp()
        for p in n.rglob("*.jpg"):
            os.utime(p, (stare, stare))

    def test_rozloz_cofnij(self):
        lista = Z.lista_lokalna(self.hub, exif=lambda p: None)
        p = Z.planuj(lista, KONF, TERAZ)
        self.assertEqual(len(p["ruchy"]), 1)
        self.assertEqual(Z.wykonaj_lokalnie(p, self.hub), 1)
        cel = self.hub / "Zdjęcia/Etap A/01 Wykop i odbiór dna/2026-11-18_PXL_20261118_090000000.jpg"
        self.assertTrue(cel.exists())
        self.assertTrue((self.hub / "_Archiwum/Puste foldery/wykop").exists())
        self.assertTrue((self.hub / "Zdjęcia/_nowe/nieznane/PXL_20261118_090000000.jpg").exists())
        Z.zapisz_ruchy(p, "skrypt")
        c = Z.plan_cofniecia(Z.wczytaj_ruchy())
        self.assertEqual(len(c["ruchy"]), 1)
        self.assertEqual(c["ruchy"][0]["do"], "Zdjęcia/_nowe/wykop")
        # ponowny przebieg: nic do zrobienia poza czekającym
        p2 = Z.planuj(Z.lista_lokalna(self.hub, exif=lambda p: None), KONF, TERAZ)
        self.assertEqual(p2["ruchy"], [])

    def test_wg_dni(self):
        p = Z.planuj(Z.lista_lokalna(self.hub, exif=lambda p: None), KONF, TERAZ)
        Z.wykonaj_lokalnie(p, self.hub)
        self.assertEqual(Z.wg_dni(self.hub), 1)
        self.assertEqual(Z.wg_dni(self.hub), 0)
        self.assertTrue(any((self.hub / "Zdjęcia/_wg dni/2026-11-18").iterdir()))

    def test_blokada(self):
        with Z.Blokada("skrypt"):
            with self.assertRaises(Z.Zajete):
                with Z.Blokada("konektor"):
                    pass


if __name__ == "__main__":
    unittest.main(verbosity=1)
