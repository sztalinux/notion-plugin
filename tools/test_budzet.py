"""Testy parserów budżetu na danych zmyślonych (python3 tools/test_budzet.py)."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

os.environ['BUDZET_DANE'] = tempfile.mkdtemp()
sys.path.insert(0, str(Path(__file__).resolve().parent / 'budzet'))
import allegro  # noqa: E402
import wpis  # noqa: E402
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

    def test_wpis(self):
        wspolne.U.update(skroty_kont={'pra': 'K-praca', 'z': 'K-bank'}, skroty_osob={'o': 'Osoba B', 'a': 'Osoba A'},
                         konta_list={'praca': 'K-praca'}, gotowka_konto='Gotówka', osoba_listy='Osoba B', osoba_wyciagi='Osoba A',
                         konto_zen='K-bank')
        sk = {'zam': ['Koszt', 'Praca', 'Zamówienia'], 'dom': ['Inwestycja', 'Dom', '']}
        w = wpis.parsuj('200, pra, o, zam, przykład', sk)
        self.assertEqual((w['kwota'], w['konto'], w['osoba'], w['kat'], w['pod'], w['opis']),
                         (-200.0, 'K-praca', 'Osoba B', 'Praca', 'Zamówienia', 'przykład'))
        w = wpis.parsuj('150, z, a, dom, test', sk)
        self.assertEqual((w['konto'], w['osoba'], w['typ'], w['kat']), ('K-bank', 'Osoba A', 'Inwestycja', 'Dom'))
        w = wpis.parsuj('12,50, zam', sk)  # bez konta: gotówka i druga osoba; przecinek dziesiętny
        self.assertEqual((w['kwota'], w['konto'], w['osoba']), (-12.5, 'Gotówka', 'Osoba B'))
        w = wpis.parsuj('10, z, o, zam', sk)  # konto z wyciągiem z osobą podaną wprost
        self.assertEqual(w['osoba'], 'Osoba B')
        w = wpis.parsuj('+100, pra, nieznany', sk)
        self.assertEqual((w['kwota'], w['kat'], w['kod']), (100.0, '', 'nieznany'))
        w = wpis.parsuj('30-5, zam', sk)
        self.assertEqual((w['kwota'], w['skladniki']), (-25.0, [30.0, -5.0]))
        with self.assertRaises(ValueError):
            wpis.parsuj('abc, zam', sk)


NARZ = Path(__file__).resolve().parent / 'budzet'


class Przeplyw(unittest.TestCase):
    """wpis.py + importuj.py jako procesy na zmyślonych danych w katalogu tymczasowym (BUDZET_DANE; danych produkcyjnych nie dotyka)."""

    def setUp(self):
        self.dane = Path(tempfile.mkdtemp())
        self.ustaw(konto_budowy='K-bank')
        (self.dane / 'kategorie.json').write_text(json.dumps({'Inwestycja': {'Dom': []}, 'Wydatek': {'Inne wydatki': []}}))
        (self.dane / 'reguly.json').write_text(json.dumps({'reguly': [], 'skroty': {'dom': ['Inwestycja', 'Dom', '']}}))
        (self.dane / 'ark.json').write_text(json.dumps({'values': [['Data']]}))

    def ustaw(self, **dod):
        u = dict(konto_zen='K-bank', konto_mbank='K-mb', gotowka_konto='Gotówka', osoba_listy='Osoba B',
                 osoba_wyciagi='Osoba A', skroty_kont={'z': 'K-bank'})
        u.update(dod)
        (self.dane / 'ustawienia.json').write_text(json.dumps(u))

    def uruchom(self, skrypt, *arg):
        env = dict(os.environ, BUDZET_DANE=str(self.dane))
        r = subprocess.run([sys.executable, str(NARZ / skrypt), *arg], env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def importuj(self, *dod):
        self.uruchom('importuj.py', '--miesiac', '2026-10', '--arkusz', 'ark.json', *dod)
        return json.loads((self.dane / 'miesiace' / '2026-10.json').read_text(encoding='utf-8'))

    def zen(self, kwota):
        (self.dane / 'zen.csv').write_text('Naglowek\nTransactions:\n"Date,Transaction type,Description,Settlement amount"\n'
                                           f'"6 Oct 2026,Transfer,""HURTOWNIA TESTOWA"",{kwota},PLN,{kwota},PLN,1,,,,900.00"\n')

    def test_budowa_przelew_i_wyciag_jeden_wiersz(self):
        out = self.uruchom('wpis.py', 'dodaj', '300, dom, stal', '--data', '2026-10-05', '--id', 'p1', '--budowa', 'p1')
        self.assertIn('K-bank', out)
        self.zen('-300.00')
        m = self.importuj('--zen', 'zen.csv')
        self.assertEqual([(w['konto'], w['kat'], w['kwota']) for w in m['wiersze']], [('K-bank', 'Dom', 300.0)])
        self.assertEqual(m['decyzje'], [])

    def test_budowa_gotowka_jeden_wiersz(self):
        self.uruchom('wpis.py', 'dodaj', '120, dom, piasek', '--data', '2026-10-05', '--id', 'p2', '--budowa', 'p2', '--gotowka')
        m = self.importuj()
        self.assertEqual([(w['konto'], w['kat'], w['kwota']) for w in m['wiersze']], [('Gotówka', 'Dom', 120.0)])

    def test_ten_sam_id_jeden_wpis(self):
        for _ in range(2):
            self.uruchom('wpis.py', 'dodaj', '80, dom', '--data', '2026-10-07', '--id', 'p3', '--budowa', 'p3')
        self.assertIn('2026-10: 1 wpisów', self.uruchom('wpis.py', 'lista', '2026-10'))

    def test_brak_konta_budowy_gotowka_z_uwaga(self):
        self.ustaw()
        out = self.uruchom('wpis.py', 'dodaj', '50, dom', '--data', '2026-10-08', '--id', 'p4', '--budowa', 'p4')
        self.assertIn('Gotówka', out)
        self.assertIn('konto_budowy', out)

    def test_ustaw_konto_budowy(self):
        self.ustaw()
        self.assertIn('konto_budowy = K-bank', self.uruchom('wpis.py', 'ustaw-konto-budowy', 'z'))
        u = json.loads((self.dane / 'ustawienia.json').read_text(encoding='utf-8'))
        self.assertEqual((u['konto_budowy'], u['osoba_listy']), ('K-bank', 'Osoba B'))  # reszta ustawień zostaje
        self.assertIn('K-bank', self.uruchom('wpis.py', 'dodaj', '70, dom', '--data', '2026-10-11', '--id', 'p8', '--budowa', 'p8'))
        r = subprocess.run([sys.executable, str(NARZ / 'wpis.py'), 'ustaw-konto-budowy', 'xyz'],
                           env=dict(os.environ, BUDZET_DANE=str(self.dane)), capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)

    def test_zwrot_pomniejsza_wydatek(self):
        self.uruchom('wpis.py', 'dodaj', '300, dom', '--data', '2026-10-09', '--id', 'p5', '--gotowka')
        self.uruchom('wpis.py', 'dodaj', '+50, dom, zwrot', '--data', '2026-10-09', '--id', 'p6', '--gotowka')
        m = self.importuj()
        self.assertEqual([(w['konto'], w['kwota']) for w in m['wiersze']], [('Gotówka', 250.0)])

    def test_sam_zwrot_ujemny(self):
        self.uruchom('wpis.py', 'dodaj', '+40, dom, zwrot', '--data', '2026-10-10', '--id', 'p7', '--gotowka')
        m = self.importuj()
        self.assertEqual([w['kwota'] for w in m['wiersze']], [-40.0])


if __name__ == '__main__':
    unittest.main()
