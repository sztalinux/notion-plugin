#!/usr/bin/env python3
"""Testy pola „Nowa pozycja” w `wydatki.py` (POM-31): parsowanie, walidacja, `sync` z akcją „dodaj_pozycje”, bezpiecznik
pierwszego użycia, plik spraw dla sesji i blokada – na atrapach arkusza i Notion, bez sieci i bez prawdziwych danych.

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


def strona(id_, pozycja="", nowa="", typ="Materiał", jedn="szt", ilosc=2, blad="", rodzaj="", kwota=100, wiersz=None):
    return {"id": id_, "properties": {
        "Rodzaj": {"select": {"name": rodzaj} if rodzaj else None}, "Wiersz arkusza": {"number": wiersz}, "Data": {"date": {"start": "2026-11-18"}}, "Kwota": {"number": kwota},
        "Pozycja": {"select": {"name": pozycja} if pozycja else None}, "Typ": {"select": {"name": typ}},
        "Ilość": {"number": ilosc}, "Jedn.": {"select": {"name": jedn}}, "Wydatek": {"title": [{"plain_text": "Rzecz X"}]},
        "Nowa pozycja": tekst(nowa), "Błąd": tekst(blad)}}


class Atrapy:
    """Arkusz (akcje Apps Script) i Notion (PATCH stron, schemat bazy) w pamięci."""

    def __init__(self, wersja=5, odpowiedzi=None, timeout=False, ping_timeout=False, plan=None):
        self.wersja, self.odpowiedzi, self.timeout, self.ping_timeout = wersja, odpowiedzi or {}, timeout, ping_timeout
        self.plan = plan   # Kosztorys „dane”: (lp, wiersz, plan ręczny)
        self.akcje, self.patche, self.dopisane = [], [], []
        self.opcje = [{"id": "o1", "name": "47.1 Pozycja A"}]

    def arkusz(self, k, akcja, limit=0, **dane):
        self.akcje.append((akcja, dane))
        if akcja == "ping":
            if self.ping_timeout:
                raise WY.BladArkusza("timeout")
            return {"ok": True, "wersja": self.wersja, "cennik_ok": True}
        if akcja == "dodaj_pozycje":
            if self.timeout:
                raise WY.BladArkusza("timeout")
            wynik = dict(self.odpowiedzi[dane["pozycja"]["etap"]])
            if dane.get("na_sucho") and wynik.get("ok") and not wynik.get("juz") and not wynik.get("brak_etapu"):
                wynik = {"ok": True, "na_sucho": True, "lp": wynik.get("lp"), "wiersz": 1, "suma_etapu": "1:2"}
            return {"ok": True, "wynik": wynik}
        if akcja == "dane":
            lp, wiersz, plan = self.plan
            nag = ["Etap", "Lp", "Pozycja", "PLAN", "Plan ręczny (zł)"]
            wiersze = [[""]] * (wiersz - WY.PIERWSZY_WIERSZ)
            return {"ok": True, "arkusze": {"Kosztorys": [[""], [""], [""], nag] + wiersze + [["E", lp, "X", 0, plan]]}}
        if akcja == "zmien":
            return {"ok": True, "wykonane": len(dane["operacje"])}
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
        self.potwierdz()

    def tearDown(self):
        WY.W.CONF, WY.arkusz, WY.W.zadanie_http, WY.kolejka = self._conf, self._arkusz, self._http, self._kolejka
        self.tmp.cleanup()

    def potwierdz(self):
        WY.nowa_pozycja_polecenie(K, "", proba=False, potwierdz=True)

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
        self.assertFalse(WY.plik_sesji().exists())

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
        dane = json.loads(WY.plik_sesji().read_text(encoding="utf-8"))
        self.assertEqual(dane["etapy"][0]["etap"], "41")
        self.assertEqual(dane["etapy"][0]["stan"], "SSO")
        self.assertEqual(dane["etapy"][0]["strony"], ["a"])
        # drugi przebieg z tą samą uwagą nie zapisuje Notion ponownie; po dodaniu etapu plik znika
        a2 = Atrapy(odpowiedzi=a.odpowiedzi)
        self.uruchom([strona("a", nowa="41 Etap nowy · SSO | Pozycja Z | Robocizna | m²", blad=wl["Błąd"]["rich_text"][0]["text"]["content"])], a2)
        self.assertEqual(a2.patche, [])
        self.uruchom([], Atrapy())
        self.assertFalse(WY.plik_sesji().exists())

    def test_blad_akcji_to_blad_strony(self):
        a = Atrapy(odpowiedzi={"47": {"ok": False, "blad": "nowa pozycja 47.2: zmieniło się: RAZEM PLAN – wstawiony wiersz usunięty"}})
        licz, bledy = self.uruchom([strona("a", nowa="47 | Szafki | Materiał | kpl")], a)
        self.assertEqual((licz["bledy"], licz["dopisane"]), (1, 0))
        self.assertEqual(a.patche[0][1]["Arkusz"]["select"]["name"], WY.BLAD)

    def test_timeout_zostawia_strone_i_plik(self):
        WY.zapisz_sesje({"41": {"etap": "41", "nazwa": "", "stan": "", "pozycje": [], "strony": ["x"]}}, None)
        a = Atrapy(timeout=True)
        licz, bledy = self.uruchom([strona("a", nowa="47 | Szafki | Materiał | kpl")], a)
        self.assertEqual((licz["dopisane"], licz["bledy"]), (0, 0))
        self.assertTrue(any("timeout" in b for b in bledy))
        self.assertEqual(a.patche, [])
        self.assertTrue(WY.plik_sesji().exists())

    def test_10_pozycja_wygrywa_a_pole_jest_czyszczone(self):
        a = Atrapy()
        licz, bledy = self.uruchom([strona("a", pozycja="47.1 Pozycja A", nowa="47 | Szafki | Materiał | kpl")], a)
        self.assertEqual((bledy, licz["dopisane"], licz["nowe_pozycje"]), ([], 1, 0))
        self.assertNotIn("dodaj_pozycje", [x for x, _ in a.akcje])
        self.assertEqual(a.dopisane[0]["lp"], "47.1")
        self.assertEqual(a.patche[-1][1]["Nowa pozycja"], {"rich_text": []})

    def test_11_nowa_pozycja_przy_zwrocie_i_planie_to_blad(self):
        for rodzaj in ("Zwrot", "Plan"):
            a = Atrapy()
            licz, _ = self.uruchom([strona("a", nowa="47 | Szafki | Materiał | kpl", rodzaj=rodzaj)], a)
            self.assertEqual(licz["bledy"], 1, rodzaj)
            self.assertIn("tylko dla Rodzaju Wydatek albo Wycena", a.patche[0][1]["Błąd"]["rich_text"][0]["text"]["content"])

    def plan(self, id_, wiersz_strony, plan_w_arkuszu, wiersz_pozycji=88, lp="47.1"):
        """Strona Plan (kwota 700) na pozycję `lp`; w arkuszu pozycja w wierszu `wiersz_pozycji` z planem ręcznym."""
        a = Atrapy(plan=(lp, wiersz_pozycji, plan_w_arkuszu))
        licz, bledy = self.uruchom([strona(id_, pozycja=f"{lp} Pozycja A", rodzaj="Plan", kwota=700, wiersz=wiersz_strony)], a)
        return licz, bledy, [d["operacje"][0]["a1"] for x, d in a.akcje if x == "zmien"]

    def test_9_plan_wlasny_po_przesunieciu_wiersza(self):
        # strona wpisała plan 47.1 w wierszu 40 (plany.json), wstawienie pozycji przesunęło wiersz na 41 – to nadal jej plan
        self.assertEqual(self.plan("a", None, 0, wiersz_pozycji=40)[2], ["E40"])
        self.assertEqual(json.loads(WY.plik_planow().read_text(encoding="utf-8")), {"a": "47.1"})
        licz, bledy, zapisy = self.plan("a", 40, 500, wiersz_pozycji=41)
        self.assertEqual((bledy, licz["plany"], licz["bledy"], zapisy), ([], 1, 0, ["E41"]))
        licz, _, zapisy = self.plan("b", None, 500, wiersz_pozycji=41)
        self.assertEqual((licz["bledy"], zapisy), (1, []))   # cudzy plan bez „Nadpisz plan” – jak dotąd

    def test_9_strona_sprzed_pliku_planow_ten_sam_wiersz_to_wlasny_plan(self):
        licz, _, zapisy = self.plan("a", 88, 500)
        self.assertEqual((licz["plany"], zapisy), (1, ["E88"]))
        self.assertEqual(json.loads(WY.plik_planow().read_text(encoding="utf-8")), {"a": "47.1"})

    def test_9_wiersz_innej_pozycji_nie_daje_prawa_do_planu(self):
        # R3: strona wpisała kiedyś plan w wierszu 36 (inna pozycja), teraz ma Pozycję 47.1 z planem ręcznym inwestora
        licz, _, zapisy = self.plan("p", 36, 5000)
        self.assertEqual((licz["plany"], licz["bledy"], zapisy), (0, 1, []))
        # to samo, gdy plany.json pamięta inną pozycję tej strony
        WY.zapisz_plany({"p": "03.5"})
        licz, _, zapisy = self.plan("p", 88, 5000)
        self.assertEqual((licz["bledy"], zapisy), (1, []))

    def test_9_nadpisz_plan_przejmuje_plan_od_poprzedniej_strony(self):
        WY.zapisz_plany({"a": "47.1", "c": "03.5"})
        a = Atrapy(plan=("47.1", 88, 500))
        s = strona("b", pozycja="47.1 Pozycja A", rodzaj="Plan", kwota=700)
        s["properties"]["Nadpisz plan"] = {"checkbox": True}
        licz, _ = self.uruchom([s], a)
        self.assertEqual(licz["plany"], 1)
        self.assertEqual(json.loads(WY.plik_planow().read_text(encoding="utf-8")), {"a": "", "b": "47.1", "c": "03.5"})
        self.assertEqual(self.plan("a", 88, 900)[0]["bledy"], 1)   # „a” bez „Nadpisz plan” nie odbiera planu

    def test_9_wydatek_przestawiony_na_plan_nie_nadpisuje(self):
        # R8: Wiersz arkusza = 50 pochodzi z zakładki Wydatki – to nie jest plan tej strony
        licz, _, zapisy = self.plan("w", 50, 5000)
        self.assertEqual((licz["plany"], licz["bledy"], zapisy), (0, 1, []))
        self.assertFalse(WY.plik_planow().exists())

    def test_12_timeout_pingu_nie_wstrzymuje_planow(self):
        a = Atrapy(ping_timeout=True, plan=("47.1", 41, 0))
        with self.assertRaises(WY.BladArkusza):
            self.uruchom([strona("p", pozycja="47.1 Pozycja A", rodzaj="Plan", kwota=700),
                          strona("a", nowa="47 | Szafki | Materiał | kpl")], a)
        self.assertEqual(a.patche[0][0], "p")
        self.assertEqual(a.patche[0][1]["Arkusz"]["select"]["name"], WY.W_ARKUSZU)

    def test_13_swieza_blokada_sesji_strony_etapu_czekaja(self):
        WY.zapisz_sesje({"41": {"etap": "41", "nazwa": "", "stan": "", "pozycje": [], "strony": ["a"]}}, None)
        WY.sesja(zablokuj=True)
        a = Atrapy(odpowiedzi={"41": {"ok": True, "juz": True, "lp": "41.1", "klucz": "41.1 Pozycja Z", "wiersz": 9}})
        licz, bledy = self.uruchom([strona("a", nowa="41 | Pozycja Z | Robocizna | m²")], a)
        self.assertEqual((bledy, licz["czekaja_na_etap"], licz["bledy"]), ([], 1, 0))
        self.assertNotIn("dodaj_pozycje", [x for x, _ in a.akcje])

    def test_13_swieza_blokada_zadnej_pozycji_takze_w_innym_etapie(self):
        # sesja buduje etap 41 (kolumna A pusta) – wstawienie w etapie 47 wciągnęłoby go do sąsiedniego bloku (B-2)
        WY.zapisz_sesje({"41": {"etap": "41", "nazwa": "", "stan": "", "pozycje": [], "strony": ["x"]}},
                        {"pozycje": ["03 | Pozycja Q | Materiał | kpl"], "strony": ["y"]})
        WY.sesja(zablokuj=True)
        przed = WY.plik_sesji().read_text(encoding="utf-8")
        a = Atrapy(odpowiedzi={"47": {"ok": True, "juz": False, "lp": "47.2", "klucz": "47.2 Szafki", "wiersz": 89}})
        licz, bledy = self.uruchom([strona("b", nowa="47 | Szafki | Materiał | kpl"), strona("c", pozycja="47.1 Pozycja A")], a)
        self.assertEqual((bledy, licz["czekaja"], licz["czekaja_na_etap"], licz["nowe_pozycje"]), ([], 1, 0, 0))
        self.assertNotIn("dodaj_pozycje", [x for x, _ in a.akcje])
        self.assertEqual([w["id"] for w in a.dopisane], ["c"])               # zwykły wydatek idzie dalej
        self.assertEqual([i for i, _ in a.patche], ["c"])                    # strona „b” bez dopisku „czeka na etap 47”
        self.assertEqual(WY.plik_sesji().read_text(encoding="utf-8"), przed)  # pierwsze sprawdzenie zostaje na liście
        WY.sesja(odblokuj=True)
        licz, _ = self.uruchom([strona("b", nowa="47 | Szafki | Materiał | kpl")], Atrapy(odpowiedzi=a.odpowiedzi))
        self.assertEqual((licz["nowe_pozycje"], licz["dopisane"]), (1, 1))

    def test_13_etap_bez_pozycji_czeka(self):
        a = Atrapy(odpowiedzi={"41": {"ok": True, "brak_etapu": True, "bez_pozycji": True, "etap": "41"}})
        licz, bledy = self.uruchom([strona("a", nowa="41 | Pozycja Z | Robocizna | m²")], a)
        self.assertEqual((bledy, licz["czekaja_na_etap"], licz["bledy"]), ([], 1, 0))

    def test_14_czekanie_ponad_3_dni_to_kod_1(self):
        a = Atrapy(odpowiedzi={"41": {"ok": True, "brak_etapu": True, "etap": "41"}})
        self.uruchom([strona("a", nowa="41 | Pozycja Z | Robocizna | m²")], a)
        d = json.loads(WY.plik_sesji().read_text(encoding="utf-8"))
        d["etapy"][0]["od"] = "2000-01-01 00:00"
        WY.plik_sesji().write_text(json.dumps(d), encoding="utf-8")
        _, bledy = self.uruchom([strona("a", nowa="41 | Pozycja Z | Robocizna | m²")], Atrapy(odpowiedzi=a.odpowiedzi))
        self.assertTrue(any("ponad 3 dni" in b and "nowy etap 41" in b for b in bledy), bledy)
        self.assertEqual(json.loads(WY.plik_sesji().read_text(encoding="utf-8"))["etapy"][0]["od"], "2000-01-01 00:00")

    def test_15_bez_znacznika_nowa_czeka_istniejaca_przechodzi(self):
        WY.znacznik_sprawdzenia().unlink()
        a = Atrapy(odpowiedzi={"47": {"ok": True, "juz": False, "lp": "47.2", "klucz": "47.2 Szafki", "wiersz": 89},
                               "03": {"ok": True, "juz": True, "lp": "03.5", "klucz": "03.5 Chudziak", "wiersz": 36}})
        licz, bledy = self.uruchom([strona("a", nowa="47 | Szafki | Materiał | kpl"),
                                    strona("b", nowa="03 | Chudziak | Materiał | m³")], a)
        self.assertEqual(bledy, [])
        self.assertTrue(all(d.get("na_sucho") for x, d in a.akcje if x == "dodaj_pozycje"))
        self.assertEqual([w["id"] for w in a.dopisane], ["b"])
        uwaga = [wl for i, wl in a.patche if i == "a"][0]["Błąd"]["rich_text"][0]["text"]["content"]
        self.assertIn("pierwsze sprawdzenie", uwaga)
        d = json.loads(WY.plik_sesji().read_text(encoding="utf-8"))
        self.assertEqual(d["pierwsze_sprawdzenie"]["pozycje"], ["47 | Szafki | Materiał | kpl"])
        self.assertIn("pierwsze sprawdzenie tak", WY.sesja())
        # po potwierdzeniu wstawia naprawdę
        self.potwierdz()
        a2 = Atrapy(odpowiedzi=a.odpowiedzi)
        licz, _ = self.uruchom([strona("a", nowa="47 | Szafki | Materiał | kpl")], a2)
        self.assertEqual(licz["nowe_pozycje"], 1)
        self.assertFalse(WY.plik_sesji().exists())

    def test_15_skrot_w_polu_pelny_tekst_na_liscie_sesji(self):
        # pole „47 | Szafki” (typ i jednostka ze strony) – na liście `sesja` pełny tekst, który przyjmie `nowa-pozycja` (D.3)
        WY.znacznik_sprawdzenia().unlink()
        a = Atrapy(odpowiedzi={"47": {"ok": True, "juz": False, "lp": "47.2", "klucz": "47.2 Szafki", "wiersz": 89}})
        self.uruchom([strona("a", nowa="47 | Szafki")], a)
        tekst_ = json.loads(WY.plik_sesji().read_text(encoding="utf-8"))["pierwsze_sprawdzenie"]["pozycje"][0]
        self.assertEqual(tekst_, "47 | Szafki | Materiał | szt")
        self.assertEqual(WY.nowa_pozycja(tekst_, {"typ": "", "jedn": ""})[1], "")

    def test_proba_nie_wola_arkusza(self):
        a = Atrapy()
        WY.arkusz, WY.W.zadanie_http, WY.kolejka = a.arkusz, a.http, (lambda k: [strona("a", nowa="47 | Szafki | Materiał | kpl")])
        licz, _ = WY.sync(K, proba=True)
        self.assertEqual((a.akcje, a.patche, licz["bledy"]), ([], [], 0))


class PolecenieNowaPozycja(unittest.TestCase):
    def setUp(self):
        self._arkusz = WY.arkusz

    def tearDown(self):
        WY.arkusz = self._arkusz

    def test_8_proba_przy_istniejacej_nazwie_i_niepelnej_odpowiedzi(self):
        a = Atrapy(odpowiedzi={"03": {"ok": True, "juz": True, "lp": "03.17", "klucz": "03.17 Blacha", "wiersz": 44}})
        WY.arkusz = a.arkusz
        self.assertIn("już jest – Lp 03.17", WY.nowa_pozycja_polecenie(K, "03 | Blacha | Materiał | kpl", proba=True))
        odp = {"wynik": {"ok": True, "na_sucho": True}}               # bez spodziewanych pól – bez tracebacku
        WY.arkusz = lambda k, akcja, **d: {"ok": True, "wersja": 5} if akcja == "ping" else dict(odp, ok=True)
        self.assertIn("Lp ?", WY.nowa_pozycja_polecenie(K, "03 | Inna | Materiał | kpl", proba=True))
        odp = {}
        with self.assertRaises(WY.BladArkusza):
            WY.nowa_pozycja_polecenie(K, "03 | Inna | Materiał | kpl", proba=True)


class BlokadaEtapu(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._conf = WY.W.CONF
        WY.W.CONF = Path(self.tmp.name)

    def tearDown(self):
        WY.W.CONF = self._conf
        self.tmp.cleanup()

    def test_nic_nie_czeka(self):
        self.assertIn("nic nie czeka", WY.sesja(zablokuj=True))
        self.assertFalse(WY.blokada_sesji().exists())

    def test_jedna_sesja_naraz_i_porzucona_blokada(self):
        import os
        WY.zapisz_sesje({"41": {"etap": "41", "nazwa": "Etap nowy", "stan": "SSO",
                                "pozycje": [{"nazwa": "Pozycja Z", "typ": "Robocizna", "jedn": "m²"}], "strony": ["a"]}}, None)
        self.assertIn("blokada założona", WY.sesja(zablokuj=True))
        self.assertIn("zajęte", WY.sesja(zablokuj=True))
        blokada = WY.blokada_sesji()
        stara = blokada.stat().st_mtime - WY.BLOKADA_WAZNA_S - 10
        os.utime(blokada, (stara, stara))
        self.assertIn("blokada założona", WY.sesja(zablokuj=True))
        WY.sesja(odblokuj=True)
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
