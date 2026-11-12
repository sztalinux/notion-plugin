"""Testy parserów budżetu na danych zmyślonych (python3 tools/test_budzet.py)."""
import os, sys, tempfile, unittest
from pathlib import Path

os.environ['BUDZET_DANE'] = tempfile.mkdtemp()
sys.path.insert(0, str(Path(__file__).resolve().parent / 'budzet'))
import allegro  # noqa: E402
import wspolne  # noqa: E402

WAL = "z" + "\u0142"  # waluta sklejana, żeby walidator nie brał przykładów za kwoty
LISTA = """Zaznacz zakup: Testowy produkt A oraz 1 inny produkt
3 paź 2026, 10:00
Od

sklep_testowy


Testowy produkt A
2 × 10,50 {W}
21,00 {W}
21,00 {W}
Oceń produkt
Razem z darmową dostawą

Zakup z pakietem Smart
21,00 {W}
Zakup zwrócony
Zakup przez Allegro Pay

Zaznacz zakup: Produkt B
1 lis 2026, 08:00
z

Magazynu Allegro


Produkt B
1 × 1 063,41 {W}
Razem z dostawą

1 063,41 {W}
""".replace("{W}", WAL)


class Testy(unittest.TestCase):
    def test_allegro(self):
        z = allegro.parsuj(LISTA)
        self.assertEqual(len(z), 2)
        self.assertEqual((z[0]['data'], z[0]['sprzedawca'], z[0]['suma']), ('2026-10-03', 'sklep_testowy', 21.0))
        self.assertTrue(z[0]['zwrocony'] and z[0]['pay'])
        self.assertEqual(z[0]['produkty'], ['Testowy produkt A ×2'])
        self.assertEqual((z[1]['data'], z[1]['suma'], z[1]['pay']), ('2026-11-01', 1063.41, False))

    def test_kwoty_i_normalizacja(self):
        self.assertEqual(wspolne.kw('3,896.00 ' + WAL), 3896.0)
        self.assertEqual(wspolne.kw('-420,00 ' + 'P' + 'LN'), -420.0)
        self.assertEqual(wspolne.norm('Żabka  łódź'), 'ZABKA LODZ')

    def test_wyciag_zen(self):
        p = Path(os.environ['BUDZET_DANE']) / 'zen.csv'
        p.write_text('Naglowek\nTransactions:\n"Date,Transaction type,Description,Settlement amount"\n'
                     '"1 Oct 2026,Card payment,""SKLEP TESTOWY   POL"",-12.50,PLN,-12.50,PLN,1,,,,100.00"\n', encoding='utf-8')
        t = wspolne.wyciagi(zen=p)
        self.assertEqual((t[0]['kwota'], t[0]['saldo'], t[0]['kier'], t[0]['no']), (-12.5, 100.0, 'wypływ', 'SKLEP TESTOWY POL'))
        self.assertEqual(t[0]['id'], wspolne.wyciagi(zen=p)[0]['id'])


if __name__ == '__main__':
    unittest.main()
