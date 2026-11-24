#!/usr/bin/env python3
"""Testy ścieżek `wydatki.py`, które nadpisują albo czyszczą dane w arkuszu: `wycofaj` (Wydatki, Cennik, plan) – na atrapach
arkusza i Notion z `test_wydatki_pozycje.py`, bez sieci, bez prawdziwych danych i bez zależności od dzisiejszej daty.

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

    def __init__(self, strony=(), usun=None, **kw):
        super().__init__(**kw)
        self.strony = {s["id"]: s for s in strony}
        self.usun = usun or {}   # id → {"wydatki": [wiersze], "cennik": [wiersze]}

    def arkusz(self, k, akcja, limit=0, **dane):
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


class Wycofaj(Podmiana):
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


if __name__ == "__main__":
    unittest.main()
