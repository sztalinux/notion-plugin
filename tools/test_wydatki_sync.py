#!/usr/bin/env python3
"""Testy ścieżek `wydatki.py`, które nadpisują albo czyszczą dane w arkuszu: korekta wiersza po ponownym wysłaniu i po
timeoucie, VAT % po dopisaniu, czekanie zwrotów i wycen na nowszy kod Apps Script, przerwanie po błędzie Notion w połowie
oznaczania i `wycofaj` (Wydatki, Cennik, plan) – na atrapach arkusza i Notion z `test_wydatki_pozycje.py`, bez sieci,
bez prawdziwych danych i bez zależności od dzisiejszej daty.

    python3 tools/test_wydatki_sync.py
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wydatki as WY  # noqa: E402
import test_wydatki_pozycje as T  # noqa: E402  (tylko atrapy i strony – bez importu klas testów)

K = T.K


class Arkusz(T.Atrapy):
    """Atrapy z akcją „usun” i odczytem stron Notion (GET /pages/<id>)."""

    def __init__(self, strony=(), usun=None, cennik_ok=True, bledy_dopisz=0, bledy_zmien=0, **kw):
        super().__init__(**kw)
        self.strony = {s["id"]: s for s in strony}
        self.usun = usun or {}   # id → {"wydatki": [wiersze], "cennik": [wiersze]}
        self.cennik_ok, self.bledy_dopisz, self.bledy_zmien = cennik_ok, bledy_dopisz, bledy_zmien
        self.zrodla = {}         # Wydatki: Źródło „notion:<id>” → wiersz (jak kolumna O w arkuszu)

    def arkusz(self, k, akcja, limit=0, **dane):
        if akcja == "ping":
            self.akcje.append((akcja, dane))
            return {"ok": True, "wersja": self.wersja, "cennik_ok": self.cennik_ok}
        if akcja == "dopisz":
            # jak Apps Script: ta sama strona drugi raz = „juz” z jej wierszem; timeout po zapisie (wiersz już jest)
            self.akcje.append((akcja, dane))
            wyniki = []
            for w in dane["wiersze"]:
                if w["rodzaj"] == "Wycena":
                    wyniki.append({"id": w["id"], "ok": True, "arkusz": "Cennik", "wiersz": 7})
                    continue
                juz = w["id"] in self.zrodla
                self.zrodla.setdefault(w["id"], 10 + len(self.zrodla))
                wyniki.append({"id": w["id"], "ok": True, "wiersz": self.zrodla[w["id"]], "juz": juz})
            if self.bledy_dopisz:
                self.bledy_dopisz -= 1
                raise WY.BladArkusza("timeout")
            return {"ok": True, "wyniki": wyniki}
        if akcja == "zmien" and self.bledy_zmien:
            self.akcje.append((akcja, dane))
            self.bledy_zmien -= 1
            raise WY.BladArkusza("timeout")
        if akcja == "usun":
            self.akcje.append((akcja, dane))
            return {"ok": True, "wyniki": [dict({"id": i, "wydatki": [], "cennik": []}, **self.usun.get(i, {}))
                                           for i in dane["ids"]]}
        return super().arkusz(k, akcja, limit, **dane)

    def http(self, metoda, url, naglowki, dane=None, **kw):
        if metoda == "GET" and "/pages/" in url:
            return self.strony[url.rsplit("/", 1)[-1]]
        return super().http(metoda, url, naglowki, dane, **kw)


class Podmiana(unittest.TestCase):
    """Katalog .dom w katalogu tymczasowym i przywracanie podmienionych funkcji modułu."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._stare = WY.W.CONF, WY.arkusz, WY.W.zadanie_http, WY.kolejka
        WY.W.CONF = Path(self.tmp.name)

    def tearDown(self):
        WY.W.CONF, WY.arkusz, WY.W.zadanie_http, WY.kolejka = self._stare
        self.tmp.cleanup()

    def podmien(self, a, strony=()):
        WY.arkusz, WY.W.zadanie_http, WY.kolejka = a.arkusz, a.http, (lambda k: list(strony))


def wydatek(id_, vat=None, status="", **kw):
    """Strona na pozycję 47.1 z polami VAT % i Płatność (puste Płatność = Zrealizowane)."""
    s = T.strona(id_, pozycja="47.1 Pozycja A", **kw)
    s["properties"]["VAT %"] = {"number": vat}
    s["properties"]["Płatność"] = {"select": {"name": status} if status else None}
    return s


def stany(a, id_):
    """Kolejne wartości pola Arkusz zapisane w Notion dla strony."""
    return [wl["Arkusz"]["select"]["name"] for i, wl in a.patche if i == id_ and "Arkusz" in wl]


def zakresy(a):
    """Zakresy A1 wszystkich operacji „zmien” po kolei."""
    return [o["a1"] for x, d in a.akcje if x == "zmien" for o in d["operacje"]]


class Korekta(Podmiana):
    def sync(self, a, strony):
        self.podmien(a, strony)
        return WY.sync(K, proba=False)

    def test_ponowne_wyslanie_poprawia_wiersz_bez_dopisania(self):
        a = Arkusz()
        licz, bledy = self.sync(a, [wydatek("a", status="Do zapłaty")])
        self.assertEqual((bledy, licz["dopisane"], stany(a, "a")), ([], 1, [WY.W_ARKUSZU]))
        s = wydatek("a", status="Zrealizowane")
        licz, bledy = self.sync(a, [s])
        self.assertEqual((bledy, licz["dopisane"], licz["poprawione"]), ([], 0, 1))
        self.assertEqual(a.zrodla, {"a": 10})                                       # bez drugiego wiersza
        self.assertEqual(zakresy(a), ["A10:H10", "J10:M10", "P10"])
        a_h = [o for x, d in a.akcje if x == "zmien" for o in d["operacje"]][0]["wartosci"]
        self.assertEqual(a_h, [["2026-11-18", "Zrealizowane", 100, "47 E", "47.1 Pozycja A", "Materiał", 2, "szt"]])
        self.assertEqual(a.patche[-1][1]["Wiersz arkusza"], {"number": 10})

    def test_timeout_po_zapisie_nastepny_sync_poprawia_zamiast_dublowac(self):
        a = Arkusz(bledy_dopisz=1)
        licz, bledy = self.sync(a, [wydatek("a")])
        self.assertTrue(any("timeout" in b for b in bledy))
        self.assertEqual((licz["dopisane"], a.patche), (0, []))                   # strona zostaje „Do arkusza”
        licz, bledy = self.sync(a, [wydatek("a")])
        self.assertEqual((bledy, licz["dopisane"], licz["poprawione"], a.zrodla), ([], 0, 1, {"a": 10}))

    def test_korekta_pozycji_spoza_kosztorysu_to_blad_strony(self):
        a = Arkusz()
        a.zrodla["a"] = 10
        s = T.strona("a", pozycja="47.9 Pozycja Z")
        licz, _ = self.sync(a, [s])
        self.assertEqual((licz["bledy"], licz["poprawione"], stany(a, "a")), (1, 0, [WY.BLAD]))
        self.assertEqual(zakresy(a), [])

    def test_nowy_wiersz_z_vat_w_arkuszu_dopiero_po_zapisie_kolumny_p(self):
        a = Arkusz()
        licz, bledy = self.sync(a, [wydatek("a", vat=23)])
        self.assertEqual((bledy, licz["dopisane"], stany(a, "a")), ([], 1, [WY.W_ARKUSZU]))
        self.assertEqual([o["wartosci"] for x, d in a.akcje if x == "zmien" for o in d["operacje"]], [[[0.23]]])

    def test_blad_zapisu_vat_strona_zostaje_do_arkusza_i_wraca_korekta(self):
        a = Arkusz(bledy_zmien=1)
        licz, bledy = self.sync(a, [wydatek("a", vat=8)])
        self.assertTrue(any(b.startswith("VAT %") for b in bledy), bledy)
        self.assertEqual((licz["dopisane"], stany(a, "a")), (1, []))
        licz, bledy = self.sync(a, [wydatek("a", vat=8)])
        self.assertEqual((bledy, licz["poprawione"], stany(a, "a")), ([], 1, [WY.W_ARKUSZU]))
        self.assertEqual(zakresy(a)[-1], "P10")

    def test_blad_notion_w_polowie_oznaczania_przerywa_a_ponowienie_nie_dubluje(self):
        a = Arkusz()
        zapisy = []

        def http(metoda, url, naglowki, dane=None, **kw):
            if metoda == "PATCH" and "/pages/" in url:
                zapisy.append(url)
                if len(zapisy) == 2:
                    raise WY.W.BladHttp(502, "bad_gateway")
            return a.http(metoda, url, naglowki, dane, **kw)
        self.podmien(a, [wydatek("a"), wydatek("b")])
        WY.W.zadanie_http = http
        with self.assertRaises(WY.W.BladHttp):
            WY.sync(K, proba=False)
        self.assertEqual((stany(a, "a"), stany(a, "b")), ([WY.W_ARKUSZU], []))
        licz, bledy = self.sync(a, [wydatek("b")])                                # „a” już poza kolejką
        self.assertEqual((bledy, licz["dopisane"], licz["poprawione"], a.zrodla), ([], 0, 1, {"a": 10, "b": 11}))


class StawkaVat(Podmiana):
    def test_ulamek_i_procent_daja_to_samo_w_wydatkach_i_cenniku(self):
        # Apps Script dzieli VAT % przez 100 (Cennik F) – ułamek 0,08 musi do niego dojść jako 8
        for vat in (8, 0.08):
            a = Arkusz(wersja=5)
            w = T.strona("c", rodzaj="Wycena", kwota=12)
            w["properties"]["VAT %"] = {"number": vat}
            self.podmien(a, [wydatek("a", vat=vat * 23 / 8), w])
            licz, bledy = WY.sync(K, proba=False)
            self.assertEqual((bledy, licz["dopisane"], licz["wyceny"]), ([], 1, 1), vat)
            wyslane = {w_["id"]: w_["vat"] for x, d in a.akcje if x == "dopisz" for w_ in d["wiersze"]}
            self.assertEqual(wyslane["c"], 8, vat)
            self.assertEqual([o["wartosci"] for x, d in a.akcje if x == "zmien" for o in d["operacje"]], [[[0.23]]], vat)


class Czekanie(Podmiana):
    def test_zwrot_przy_kodzie_3_czeka_a_wydatek_idzie(self):
        a = Arkusz(wersja=3)
        self.podmien(a, [wydatek("z", rodzaj="Zwrot", kwota=50, ilosc=None), wydatek("a")])
        licz, bledy = WY.sync(K, proba=False)
        self.assertEqual((licz["czekaja"], licz["dopisane"], list(a.zrodla)), (1, 1, ["a"]))
        self.assertTrue(any("zwrotów czeka" in b and "wersji 3" in b for b in bledy), bledy)
        self.assertEqual(stany(a, "z"), [])

    def test_zwrot_przy_kodzie_4_idzie_z_kwota_ujemna(self):
        a = Arkusz(wersja=4)
        self.podmien(a, [wydatek("z", rodzaj="Zwrot", kwota=50, ilosc=None)])
        licz, bledy = WY.sync(K, proba=False)
        self.assertEqual((bledy, licz["dopisane"]), ([], 1))
        wiersz = [w for x, d in a.akcje if x == "dopisz" for w in d["wiersze"]][0]
        self.assertEqual((wiersz["kwota"], wiersz["ilosc"], wiersz["jedn"]), (-50, None, ""))

    def test_wycena_czeka_przy_kodzie_1_i_przy_starym_cenniku(self):
        for a, powod in ((Arkusz(wersja=1), "wersji 1"), (Arkusz(wersja=5, cennik_ok=False), "starym układzie")):
            s = T.strona("c", rodzaj="Wycena", kwota=12)
            self.podmien(a, [s])
            licz, bledy = WY.sync(K, proba=False)
            self.assertEqual((licz["czekaja"], licz["wyceny"], a.patche), (1, 0, []), powod)
            self.assertTrue(any("wycen czeka" in b and powod in b for b in bledy), bledy)
        a = Arkusz(wersja=2)
        self.podmien(a, [T.strona("c", rodzaj="Wycena", kwota=12)])
        licz, bledy = WY.sync(K, proba=False)
        self.assertEqual((bledy, licz["wyceny"], stany(a, "c")), ([], 1, [WY.W_ARKUSZU]))


class Wycofaj(Podmiana):
    def test_wydatek_i_wycena_czyszcza_wiersze_i_kolumne_p(self):
        a = Arkusz(strony=[wydatek("a"), T.strona("c", rodzaj="Wycena", kwota=12)],
                   usun={"a": {"wydatki": [10]}, "c": {"cennik": [7]}})
        self.podmien(a)
        licz = WY.wycofaj(K, ["a", "c"])
        self.assertEqual((licz["wiersze_wydatkow"], licz["wiersze_cennika"], licz["plany"]), (1, 1, 0))
        self.assertEqual(zakresy(a), ["P10"])
        self.assertNotIn("dane", [x for x, _ in a.akcje])                          # bez planów – bez odczytu Kosztorysu
        self.assertEqual((stany(a, "a"), stany(a, "c")), (["Nie wysyłać"], ["Nie wysyłać"]))
        self.assertEqual(a.patche[0][1]["Wiersz arkusza"], {"number": None})

    def test_plan_z_inna_kwota_w_komorce_zostaje(self):
        s = T.strona("p", pozycja="47.1 Pozycja A", rodzaj="Plan", kwota=700, wiersz=88)
        a = Arkusz(strony=[s], plan=("47.1", 88, 900))
        self.podmien(a)
        licz = WY.wycofaj(K, ["p"])
        self.assertEqual((licz["plany"], zakresy(a), stany(a, "p")), (0, [], ["Nie wysyłać"]))


class WycofajPlan(Podmiana):
    def test_plan_czysci_komorke_i_wpis_w_planach(self):
        s = T.strona("p", pozycja="47.1 Pozycja A", rodzaj="Plan", kwota=700, wiersz=88)
        WY.zapisz_plany({"p": "47.1", "q": "03.5"})
        a = Arkusz(strony=[s], plan=("47.1", 88, 700))
        self.podmien(a)
        licz = WY.wycofaj(K, ["p"])
        self.assertEqual(licz["plany"], 1)
        self.assertIn(("zmien", {"operacje": [{"op": "zakres", "arkusz": "Kosztorys", "a1": "E88", "wartosci": [[""]]}]}),
                      a.akcje)
        self.assertEqual(json.loads(WY.plik_planow().read_text(encoding="utf-8")), {"q": "03.5"})
        self.assertEqual(a.patche[-1][1]["Arkusz"]["select"]["name"], "Nie wysyłać")

    def test_plan_ktory_byl_wydatkiem_czysci_tez_wiersz_wydatkow(self):
        # R6: strona dopisała wiersz 50 w Wydatkach jako Wydatek, potem dostała Rodzaj Plan
        id_ = "12345678-aaaa-bbbb-cccc-1234567890ab"
        s = T.strona(id_, pozycja="47.1 Pozycja A", rodzaj="Plan", kwota=700, wiersz=50)
        a = Arkusz(strony=[s], plan=("47.1", 88, 0), usun={id_: {"wydatki": [50]}})
        self.podmien(a)
        licz = WY.wycofaj(K, [id_])
        self.assertEqual((licz["wiersze_wydatkow"], licz["plany"]), (1, 0))
        self.assertIn(("usun", {"ids": [id_]}), a.akcje)
        self.assertIn(("zmien", {"operacje": [{"op": "zakres", "arkusz": "Wydatki", "a1": "P50", "wartosci": [[""]]}]}),
                      a.akcje)
        self.assertEqual([i for i, _ in a.patche], [id_])   # jeden zapis w Notion, nie dwa


if __name__ == "__main__":
    unittest.main()
