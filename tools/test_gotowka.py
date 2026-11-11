#!/usr/bin/env python3
"""Testy `wydatki.py gotowka` (licz_gotowke) na zmyślonej kopii arkusza – bez sieci i bez prawdziwych liczb.

    python3 tools/test_gotowka.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wydatki as WY  # noqa: E402

PUSTE = [[""], [""], [""]]   # wiersze 1–3 nad nagłówkami (nagłówki w wierszu 4)
NAG_ETAPY = ["Etap", "Stan", "Umowa z ekipą", "Materiał", "Ekipa (robocizna)", "Inne (sprzęt)", "PLAN razem",
             "Materiał", "Ekipa (robocizna)", "Inne (sprzęt)", "Bez typu", "WYDANE razem", "Pozostało",
             "Do zapłaty ekipie (umowa – wydane ekipa)", "Uwagi / terminy"]
NAG_WYDATKI = ["Data", "Status", "Kwota (zł)", "Etap", "Pozycja", "Typ", "Ilość", "Jedn.", "Cena jedn.", "Sposób"]


def etap(nazwa, umowa, plan, wyd, do_zaplaty_ekipie):
    """plan / wyd = (materiał, ekipa, inne)."""
    return [nazwa, "Stan zero", umowa, *plan, sum(plan), *wyd, 0, sum(wyd), 0, do_zaplaty_ekipie, ""]


def arkusz(etapy, wydatki=(), rezerwa=0.1):
    return {"Etapy": PUSTE + [NAG_ETAPY] + list(etapy) + [["RAZEM"]],
            "Wydatki": PUSTE + [NAG_WYDATKI] + list(wydatki),
            "Podsumowanie": [["PODSUMOWANIE"], ["Rezerwa na stan zero", rezerwa]]}


def po_miesiacu(wynik):
    return {m["miesiac"]: m for m in wynik["miesiace"]}


class Gotowka(unittest.TestCase):
    def test_transza_na_koniec_materialu_na_start(self):
        a = arkusz([etap("03 Płyta", 1000, (500, 1000, 100), (200, 0, 0), 1000)])
        kroki = [{"nr": "03", "od": "2026-12-03", "do": "2026-12-10"},
                 {"nr": "03", "od": "2026-12-28", "do": "2027-01-05"}]
        m = po_miesiacu(WY.licz_gotowke(a, kroki, "2026-11-20"))
        self.assertEqual(m["2026-12"]["material"], 400)      # (500 − 200) + 100, start pierwszego kroku
        self.assertEqual(m["2027-01"]["ekipa"], 1000)        # koniec ostatniego kroku etapu
        self.assertEqual(m["2027-01"]["z_rezerwa"], 1100)

    def test_po_terminie_w_biezacym_miesiacu(self):
        a = arkusz([etap("04 Ściany", 800, (0, 800, 0), (0, 0, 0), 800)])
        m = po_miesiacu(WY.licz_gotowke(a, [{"nr": "04", "od": "2026-09-01", "do": "2026-09-30"}], "2026-11-05"))
        self.assertEqual(list(m), ["2026-11"])
        self.assertEqual(m["2026-11"]["po_terminie"], 800)

    def test_bez_krokow_bez_daty(self):
        a = arkusz([etap("08 Rezerwa", 0, (0, 0, 300), (0, 0, 0), 0)])
        w = WY.licz_gotowke(a, [], "2026-11-05")
        self.assertEqual(po_miesiacu(w)[WY.BEZ_DATY]["material"], 300)
        self.assertEqual(w["bez_terminu"], ["08"])

    def test_do_zaplaty_nie_liczy_sie_podwojnie(self):
        a = arkusz([etap("03 Płyta", 1000, (500, 1000, 0), (0, 0, 0), 1000)],
                   [["2026-12-15", "Do zapłaty", 400, "03 Płyta", "03.1 Ekipa", "Robocizna", "", "", "", "Gotówka"],
                    ["2026-11-02", "Do zapłaty", 100, "03 Płyta", "03.2 Beton", "Materiał", "", "", "", "Przelew"],
                    ["2026-10-01", "Zrealizowane", 999, "03 Płyta", "03.2 Beton", "Materiał", "", "", "", ""]])
        m = po_miesiacu(WY.licz_gotowke(a, [{"nr": "03", "od": "2026-11-10", "do": "2026-11-30"}], "2026-11-05"))
        self.assertEqual(m["2026-12"]["do_zaplaty"], 400)
        self.assertEqual(m["2026-12"]["gotowka"], 400)
        self.assertEqual(m["2026-11"]["do_zaplaty"], 100)
        self.assertEqual(m["2026-11"]["ekipa"], 600)         # 1000 − 400 już w „Do zapłaty”
        self.assertEqual(m["2026-11"]["material"], 400)      # 500 − 100 już w „Do zapłaty”

    def test_obiecany_zwrot_nie_zwieksza_planu(self):
        a = arkusz([etap("03 Płyta", 0, (500, 0, 0), (0, 0, 0), 0)],
                   [["2026-12-01", "Do zapłaty", -50, "03 Płyta", "03.2 Beton", "Materiał", "", "", "", ""]])
        m = po_miesiacu(WY.licz_gotowke(a, [{"nr": "03", "od": "2026-11-10", "do": "2026-11-30"}], "2026-11-05"))
        self.assertEqual(list(m), ["2026-11"])
        self.assertEqual(m["2026-11"]["material"], 500)

    def test_bez_umowy_plan_ekipy(self):
        a = arkusz([etap("05 Izolacje", 0, (0, 700, 0), (0, 200, 0), 0)], rezerwa=0)
        m = po_miesiacu(WY.licz_gotowke(a, [{"nr": "05", "od": "2026-12-01", "do": "2026-12-20"}], "2026-11-05"))
        self.assertEqual(m["2026-12"]["ekipa"], 500)
        self.assertEqual(m["2026-12"]["z_rezerwa"], 500)

    def test_przekroczenie_nie_daje_ujemnych(self):
        a = arkusz([etap("P1 Działka", 0, (0, 0, 100), (0, 0, 150), 0)])
        self.assertEqual(WY.licz_gotowke(a, [], "2026-11-05")["miesiace"], [])

    def test_kolumny_po_naglowkach(self):
        a = arkusz([])
        a["Etapy"][3] = [n for n in NAG_ETAPY if n != "Umowa z ekipą"]
        with self.assertRaises(WY.BladKonfiguracji):
            WY.licz_gotowke(a, [], "2026-11-05")


if __name__ == "__main__":
    unittest.main()
