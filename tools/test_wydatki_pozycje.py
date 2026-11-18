#!/usr/bin/env python3
"""Testy pola „Nowa pozycja” w `wydatki.py` (POM-31): parsowanie, walidacja, `sync` z akcją „dodaj_pozycje”, plik etapów
i blokada sesji – na atrapach arkusza i Notion, bez sieci i bez prawdziwych danych.

    python3 tools/test_wydatki_pozycje.py
"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wydatki as WY  # noqa: E402

K = {"token": "t", "url": "u", "sekret": "s", "sekrety": {}}


def tekst(t):
    return {"rich_text": [{"plain_text": t}]} if t else {"rich_text": []}


def strona(id_, pozycja="", nowa="", typ="Materiał", jedn="szt", ilosc=2, blad=""):
    return {"id": id_, "properties": {
        "Rodzaj": {"select": None}, "Data": {"date": {"start": "2026-11-18"}}, "Kwota": {"number": 100},
        "Pozycja": {"select": {"name": pozycja} if pozycja else None}, "Typ": {"select": {"name": typ}},
        "Ilość": {"number": ilosc}, "Jedn.": {"select": {"name": jedn}}, "Wydatek": {"title": [{"plain_text": "Rzecz X"}]},
        "Nowa pozycja": tekst(nowa), "Błąd": tekst(blad)}}


class Atrapy:
    """Arkusz (akcje Apps Script) i Notion (PATCH stron, schemat bazy) w pamięci."""

    def __init__(self, wersja=5, odpowiedzi=None, timeout=False):
        self.wersja, self.odpowiedzi, self.timeout = wersja, odpowiedzi or {}, timeout
        self.akcje, self.patche, self.dopisane = [], [], []
        self.opcje = [{"id": "o1", "name": "47.1 Pozycja A"}]

    def arkusz(self, k, akcja, limit=0, **dane):
        self.akcje.append((akcja, dane))
        if akcja == "ping":
            return {"ok": True, "wersja": self.wersja, "cennik_ok": True}
        if akcja == "dodaj_pozycje":
            if self.timeout:
                raise WY.BladArkusza("timeout")
            return {"ok": True, "wynik": self.odpowiedzi[dane["pozycja"]["etap"]]}
        if akcja == "pozycje":
            return {"ok": True, "pozycje": [{"lp": "47.1", "etap": "47 E", "klucz": "47.1 Pozycja A"},
                                            {"lp": "47.2", "etap": "47 E", "klucz": "47.2 Szafki, kuchnia"}]}
        if akcja == "dopisz":
            self.dopisane += dane["wiersze"]
            return {"ok": True, "wyniki": [{"id": w["id"], "ok": True, "wiersz": 10, "juz": False} for w in dane["wiersze"]]}
        raise AssertionError(akcja)

    def http(self, metoda, url, naglowki, dane=None, **_):
        if metoda == "GET" and "/data_sources/" in url:
            return {"properties": {"Pozycja": {"select": {"options": self.opcje}}}}
        if metoda == "PATCH" and "/data_sources/" in url:
            self.opcje = dane["properties"]["Pozycja"]["select"]["options"]
            return {}
        if metoda == "PATCH":
            self.patche.append((url.rsplit("/", 1)[-1], dane["properties"]))
            return {}
        raise AssertionError(url)


class NowaPozycjaParsowanie(unittest.TestCase):
    W = {"typ": "Materiał", "jedn": "szt"}

    def test_istniejacy_etap(self):
        p, b = WY.nowa_pozycja("47 | Szafki, kuchnia | Materiał | kpl", self.W)
        self.assertEqual(b, "")
        self.assertEqual((p["etap"], p["nazwa"], p["typ"], p["jedn"], p["nazwa_etapu"]), ("47", "Szafki, kuchnia", "Materiał", "kpl", ""))

    def test_typ_i_jednostka_ze_strony_numer_z_zerem(self):
        p, _ = WY.nowa_pozycja("3 |  Pozycja   X ", self.W)
        self.assertEqual((p["etap"], p["nazwa"], p["typ"], p["jedn"]), ("03", "Pozycja X", "Materiał", "szt"))
        p, _ = WY.nowa_pozycja("P2 | Pozycja Y", {"typ": "Usługa", "jedn": ""})
        self.assertEqual((p["etap"], p["jedn"]), ("P2", "kpl"))

    def test_nowy_etap_z_nazwa_i_stanem(self):
        p, b = WY.nowa_pozycja("41 Etap nowy · SSO | Pozycja Z | Robocizna | m²", self.W)
        self.assertEqual(b, "")
        self.assertEqual((p["etap"], p["nazwa_etapu"], p["stan"]), ("41", "Etap nowy", "SSO"))

    def test_bledy(self):
        for t in ("47", "47 | ", "x | Nazwa", "47 | Nazwa | Inne", "47 | Nazwa | Materiał | m3", "47 | =IMPORTXML(1) | Materiał",
                  "41 Etap · Wszystko | Nazwa", "1 | 2 | 3 | 4 | 5"):
            self.assertIsNone(WY.nowa_pozycja(t, self.W)[0], t)

    def test_blad_lokalny_bez_pozycji_z_nowa(self):
        w = WY.na_wiersz(strona("a", nowa="47 | Szafki | Materiał | kpl"))
        self.assertEqual(WY.blad_lokalny(w), "")
        w = WY.na_wiersz(strona("b"))
        self.assertIn("Nową pozycję", WY.blad_lokalny(w))

    def test_material_stanu_zero_z_nowa_pozycja_wymaga_ilosci(self):
        w = WY.na_wiersz(strona("a", nowa="04 | Pozycja X | Materiał | kg", ilosc=None))
        self.assertIn("ilości", WY.blad_lokalny(w))


class SyncNowaPozycja(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._conf, self._arkusz, self._http, self._kolejka = WY.W.CONF, WY.arkusz, WY.W.zadanie_http, WY.kolejka
        WY.W.CONF = Path(self.tmp.name)

    def tearDown(self):
        WY.W.CONF, WY.arkusz, WY.W.zadanie_http, WY.kolejka = self._conf, self._arkusz, self._http, self._kolejka
        self.tmp.cleanup()

    def uruchom(self, strony, atrapy):
        WY.arkusz, WY.W.zadanie_http, WY.kolejka = atrapy.arkusz, atrapy.http, (lambda k: strony)
        return WY.sync(K, proba=False)

    def test_nowa_pozycja_w_tym_samym_przebiegu(self):
        a = Atrapy(odpowiedzi={"47": {"ok": True, "juz": False, "lp": "47.2", "klucz": "47.2 Szafki, kuchnia", "wiersz": 89}})
        licz, bledy = self.uruchom([strona("a", nowa="47 | Szafki, kuchnia | Materiał | kpl"), strona("b", pozycja="47.1 Pozycja A")], a)
        self.assertEqual(bledy, [])
        self.assertEqual((licz["nowe_pozycje"], licz["dopisane"]), (1, 2))
        self.assertEqual({w["id"]: w["lp"] for w in a.dopisane}, {"a": "47.2", "b": "47.1"})
        pozycja = [p for i, p in a.patche if i == "a" and "Pozycja" in p][0]
        self.assertEqual(pozycja["Pozycja"]["select"]["name"], "47.2 Szafki; kuchnia")   # nazwa opcji bez przecinka
        self.assertEqual(pozycja["Nowa pozycja"], {"rich_text": []})
        self.assertIn("47.2 Szafki; kuchnia", [o["name"] for o in a.opcje])
        self.assertFalse(WY.plik_etapow().exists())

    def test_istniejaca_pozycja_nie_liczy_sie_jako_nowa(self):
        a = Atrapy(odpowiedzi={"47": {"ok": True, "juz": True, "lp": "47.2", "klucz": "47.2 Szafki, kuchnia", "wiersz": 89}})
        licz, _ = self.uruchom([strona("a", nowa="47 | Szafki, kuchnia | Materiał | kpl")], a)
        self.assertEqual((licz["nowe_pozycje"], licz["dopisane"]), (0, 1))

    def test_stary_kod_strony_czekaja(self):
        a = Atrapy(wersja=4)
        licz, bledy = self.uruchom([strona("a", nowa="47 | Szafki | Materiał | kpl"), strona("b", pozycja="47.1 Pozycja A")], a)
        self.assertEqual(licz["czekaja"], 1)
        self.assertEqual([w["id"] for w in a.dopisane], ["b"])
        self.assertTrue(any("wersji 4" in b for b in bledy))
        self.assertNotIn("dodaj_pozycje", [x for x, _ in a.akcje])
        self.assertEqual(a.patche[-1][0], "b")   # strona „a” bez zmian w Notion

    def test_brak_etapu_czeka_bez_bledu_i_trafia_do_pliku(self):
        a = Atrapy(odpowiedzi={"41": {"ok": True, "brak_etapu": True, "etap": "41"}})
        licz, bledy = self.uruchom([strona("a", nowa="41 Etap nowy · SSO | Pozycja Z | Robocizna | m²")], a)
        self.assertEqual(bledy, [])
        self.assertEqual((licz["czekaja_na_etap"], licz["bledy"], licz["dopisane"]), (1, 0, 0))
        (id_, wl), = a.patche
        self.assertEqual(set(wl), {"Błąd"})                       # Arkusz zostaje „Do arkusza” – bez 🔔
        dane = json.loads(WY.plik_etapow().read_text(encoding="utf-8"))
        self.assertEqual(dane["etapy"][0]["etap"], "41")
        self.assertEqual(dane["etapy"][0]["stan"], "SSO")
        self.assertEqual(dane["etapy"][0]["strony"], ["a"])
        # drugi przebieg z tą samą uwagą nie zapisuje Notion ponownie; po dodaniu etapu plik znika
        a2 = Atrapy(odpowiedzi=a.odpowiedzi)
        self.uruchom([strona("a", nowa="41 Etap nowy · SSO | Pozycja Z | Robocizna | m²", blad=wl["Błąd"]["rich_text"][0]["text"]["content"])], a2)
        self.assertEqual(a2.patche, [])
        self.uruchom([], Atrapy())
        self.assertFalse(WY.plik_etapow().exists())

    def test_blad_akcji_to_blad_strony(self):
        a = Atrapy(odpowiedzi={"47": {"ok": False, "blad": "nowa pozycja 47.2: zmieniło się: RAZEM PLAN – wstawiony wiersz usunięty"}})
        licz, bledy = self.uruchom([strona("a", nowa="47 | Szafki | Materiał | kpl")], a)
        self.assertEqual((licz["bledy"], licz["dopisane"]), (1, 0))
        self.assertEqual(a.patche[0][1]["Arkusz"]["select"]["name"], WY.BLAD)

    def test_timeout_zostawia_strone_i_plik(self):
        WY.zapisz_etapy({"41": {"etap": "41", "nazwa": "", "stan": "", "pozycje": [], "strony": ["x"]}})
        a = Atrapy(timeout=True)
        licz, bledy = self.uruchom([strona("a", nowa="47 | Szafki | Materiał | kpl")], a)
        self.assertEqual((licz["dopisane"], licz["bledy"]), (0, 0))
        self.assertTrue(any("timeout" in b for b in bledy))
        self.assertEqual(a.patche, [])
        self.assertTrue(WY.plik_etapow().exists())

    def test_proba_nie_wola_arkusza(self):
        a = Atrapy()
        WY.arkusz, WY.W.zadanie_http, WY.kolejka = a.arkusz, a.http, (lambda k: [strona("a", nowa="47 | Szafki | Materiał | kpl")])
        licz, _ = WY.sync(K, proba=True)
        self.assertEqual((a.akcje, a.patche, licz["bledy"]), ([], [], 0))


class BlokadaEtapu(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._conf = WY.W.CONF
        WY.W.CONF = Path(self.tmp.name)

    def tearDown(self):
        WY.W.CONF = self._conf
        self.tmp.cleanup()

    def test_brak_etapow(self):
        self.assertIn("brak", WY.etapy(zablokuj=True))
        self.assertFalse((WY.plik_etapow().parent / WY.BLOKADA_ETAPU).exists())

    def test_jedna_sesja_naraz_i_porzucona_blokada(self):
        import os
        WY.zapisz_etapy({"41": {"etap": "41", "nazwa": "Etap nowy", "stan": "SSO",
                                "pozycje": [{"nazwa": "Pozycja Z", "typ": "Robocizna", "jedn": "m²"}], "strony": ["a"]}})
        self.assertIn("blokada założona", WY.etapy(zablokuj=True))
        self.assertIn("zajęte", WY.etapy(zablokuj=True))
        blokada = WY.plik_etapow().parent / WY.BLOKADA_ETAPU
        stara = blokada.stat().st_mtime - WY.BLOKADA_WAZNA_S - 10
        os.utime(blokada, (stara, stara))
        self.assertIn("blokada założona", WY.etapy(zablokuj=True))
        WY.etapy(odblokuj=True)
        self.assertFalse(blokada.exists())


class KodAppsScript(unittest.TestCase):
    def test_wersja_kodu_i_akcja(self):
        kod = re.search(r"```javascript\n(.*?)```", WY.DOKUMENTACJA.read_text(encoding="utf-8"), re.S).group(1)
        self.assertEqual(int(re.search(r"var WERSJA = (\d+);", kod).group(1)), WY.WERSJA_POZYCJI)
        self.assertIn("case 'dodaj_pozycje'", kod)
        jedn = re.search(r"var JEDNOSTKI = \[(.*?)\];", kod).group(1)
        self.assertEqual(tuple(re.findall(r"'([^']+)'", jedn)), WY.JEDNOSTKI)


if __name__ == "__main__":
    unittest.main()
