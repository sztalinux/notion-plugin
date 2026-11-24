"""Testy synchronizacji wpisów budżetu z arkuszem (tools/budzet/arkusz_budzetu.py) na danych zmyślonych, bez sieci:
atrapa skryptu Apps Script zamiast POST (python3 tools/test_budzet_arkusz.py)."""
import io, json, os, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path

os.environ['BUDZET_DANE'] = tempfile.mkdtemp()
sys.path.insert(0, str(Path(__file__).resolve().parent / 'budzet'))
import arkusz_budzetu as AB  # noqa: E402
import wspolne  # noqa: E402

K = {'url': 'https://atrapa.invalid/exec', 'sekret': 'test'}


class Atrapa:
    """Zakładka Transakcje jako lista wierszy {o: [ID], kwota, ...}; akcje jak w docs/budzet-arkusz.md, sekcja 7."""

    def __init__(self, wiersze=None, wersja=1):
        self.w = list(wiersze or [])
        self.wersja = wersja
        self.wywolania = []

    def numer(self, id_):
        return next((i + 2 for i, r in enumerate(self.w) if id_ in r['o']), None)

    def __call__(self, k, akcja, **d):
        self.wywolania.append(akcja)
        if akcja == 'ping':
            return {'ok': True, 'wersja': self.wersja, 'naglowek_ok': True}
        if akcja == 'odczyt':
            return {'ok': True, 'wiersze': [{'wiersz': i + 2, 'o': ','.join(r['o']), 'data': r['data'], 'kwota': r['kwota']}
                                            for i, r in enumerate(self.w)]}
        wyniki = []
        if akcja == 'dopisz':
            for x in d['wiersze']:
                n = self.numer(x['id'])
                if n is None:
                    self.w.append(dict(x, o=[x['id']]))
                wyniki.append({'id': x['id'], 'ok': True, 'wiersz': n or len(self.w) + 1, 'juz': n is not None})
        elif akcja == 'popraw':
            for x in d['wiersze']:
                n = self.numer(x['id'])
                if n is None:
                    wyniki.append({'id': x['id'], 'ok': False, 'blad': 'brak wiersza z tym ID'})
                    continue
                r = self.w[n - 2]
                kzw = any(not t.startswith('w') for t in r['o'])
                zostaw = r['kwota'] if kzw else x['kwota']
                r.update({kk: v for kk, v in x.items() if kk != 'id'}, kwota=zostaw)
                wyniki.append({'id': x['id'], 'ok': True, 'wiersz': n, 'kwota_z_wyciagu': kzw})
        elif akcja == 'usun':
            for id_ in d['ids']:
                n = self.numer(id_)
                obce = [t for t in self.w[n - 2]['o'] if not t.startswith('w')] if n else []
                if obce:  # płatność z wyciągu – wiersz zostaje bez ID wpisu
                    self.w[n - 2]['o'] = obce
                elif n:
                    del self.w[n - 2]
                wyniki.append({'id': id_, 'ok': True, 'wiersz': n, 'zostal': bool(obce)})
        elif akcja == 'przypnij':
            for p in d['przypiecia']:
                for id_ in p['ids']:
                    r = self.w[self.numer(id_) - 2]
                    r['o'].append(p['id_wyciagu'])
                    if id_ in p['kwoty']:
                        r['kwota'] = p['kwoty'][id_]
                wyniki.append({'id_wyciagu': p['id_wyciagu'], 'ok': True})
        return {'ok': True, 'wyniki': wyniki}


def wpis(id_, data, kwota=-12.5, kat='Zakupy', **dod):
    return dict(dict(id=id_, data=data, tekst=f'{-kwota}, x', kwota=kwota, skladniki=None, konto='Gotówka', osoba='Osoba B',
                     kod='x', typ='Wydatek', kat=kat, pod='Regularne', opis='', budowa='', dodano='2026-12-01 10:00'), **dod)


class Synchronizacja(unittest.TestCase):
    def setUp(self):
        wspolne.DANE = Path(tempfile.mkdtemp())
        self.atrapa = Atrapa()
        AB.wyslij = self.atrapa

    def zapisz(self, mies, *ws):
        wspolne.zapisz_wpisy(mies, list(ws))

    def plik(self, mies):
        return {w['id']: w for w in wspolne.czytaj_wpisy(mies, z_usunietymi=True)}

    def sync(self, proba=False, k=K):
        with redirect_stdout(io.StringIO()) as out:
            licz, bledy = AB.sync(k, proba)
        return licz, bledy, out.getvalue()

    def test_brak_skryptu_to_zapas(self):
        self.zapisz('2026-12', wpis('w1', '2026-12-02'))
        licz, bledy, out = self.sync(k={'url': None, 'sekret': None})
        self.assertIn('nieskonfigurowane', out)
        self.assertEqual((bledy, self.atrapa.wywolania), ([], []))
        self.assertNotIn('arkusz', self.plik('2026-12')['w1'])
        with redirect_stdout(io.StringIO()):
            os.environ['BUDZET_ARKUSZ_URL'] = ''
            try:
                self.assertEqual(AB.main(['sync', '--cicho']), 0)  # automat nie zgłasza braku konfiguracji jako błędu
                self.assertEqual(AB.main(['kontrola', '--cicho']), 0)
            finally:
                del os.environ['BUDZET_ARKUSZ_URL']

    def test_tylko_od_grudnia_i_znacznik(self):
        self.zapisz('2026-11', wpis('wl', '2026-11-30'))
        self.zapisz('2026-12', wpis('w1', '2026-12-02'), wpis('w2', '2026-12-03', kat=''))
        licz, bledy, _ = self.sync()
        self.assertEqual((licz['dopisane'], licz['bez_kategorii'], bledy), (1, 1, []))
        self.assertEqual([r['id'] for r in self.atrapa.w], ['w1'])
        zn = self.plik('2026-12')['w1']['arkusz']
        self.assertEqual((zn['wiersz'], zn['skrot']), (2, wspolne.skrot(self.plik('2026-12')['w1'])))
        self.assertNotIn('arkusz', self.plik('2026-11')['wl'])
        self.atrapa.wywolania.clear()
        licz, _, _ = self.sync()  # drugi przebieg: nic do wysłania, bez połączenia
        self.assertEqual((licz['dopisane'], self.atrapa.wywolania), (0, []))

    def test_reczna_poprawka_zostaje_zmiana_wpisu_poprawia(self):
        self.zapisz('2026-12', wpis('w1', '2026-12-02'))
        self.sync()
        self.atrapa.w[0]['opis'] = 'poprawione ręcznie'
        ws = self.plik('2026-12')
        ws['w1']['dodano'] = '2026-12-05 08:00'  # ponowny przebieg tego samego wpisu – skrót bez zmian
        self.zapisz('2026-12', *ws.values())
        self.sync()
        self.assertEqual(self.atrapa.w[0]['opis'], 'poprawione ręcznie')
        ws['w1'].update(kwota=-20.0, tekst='20, x')
        self.zapisz('2026-12', *ws.values())
        licz, _, _ = self.sync()
        self.assertEqual((licz['poprawione'], self.atrapa.w[0]['kwota'], len(self.atrapa.w)), (1, 20.0, 1))

    def test_id_juz_w_arkuszu_tylko_znacznik(self):
        self.atrapa.w.append({'o': ['w1'], 'kwota': 12.5, 'data': '2026-12-02'})
        self.zapisz('2026-12', wpis('w1', '2026-12-02'))
        licz, _, _ = self.sync()
        self.assertEqual((licz['juz_w_arkuszu'], len(self.atrapa.w)), (1, 1))
        self.assertIn('arkusz', self.plik('2026-12')['w1'])

    def test_usuniecie_czysci_wiersz(self):
        self.zapisz('2026-12', wpis('w1', '2026-12-02'), wpis('w2', '2026-12-02'))
        self.sync()
        ws = self.plik('2026-12')
        ws['w1']['usuniety'] = '2026-12-03 09:00'
        self.zapisz('2026-12', *ws.values())
        self.assertEqual(list(wspolne.czytaj_wpisy('2026-12')), [ws['w2']])  # zamknięcie i lista nie widzą usuniętego
        licz, _, _ = self.sync()
        self.assertEqual((licz['usuniete'], [r['id'] for r in self.atrapa.w]), (1, ['w2']))
        self.assertEqual(list(self.plik('2026-12')), ['w2'])

    def test_kwota_z_wyciagu_wygrywa_przy_poprawce(self):
        self.zapisz('2026-12', wpis('w1', '2026-12-02', konto='K-bank'))
        self.sync()
        self.atrapa.w[0]['o'].append('b0000000001')
        self.atrapa.w[0]['kwota'] = 12.9
        ws = self.plik('2026-12')
        ws['w1']['opis'] = 'nowy opis'
        self.zapisz('2026-12', *ws.values())
        self.sync()
        self.assertEqual((self.atrapa.w[0]['kwota'], self.atrapa.w[0]['opis']), (12.9, 'nowy opis'))

    def test_proba_nic_nie_zapisuje(self):
        self.atrapa.w.append({'o': ['w1'], 'kwota': 12.5, 'data': '2026-12-02'})
        self.zapisz('2026-12', wpis('w1', '2026-12-02'), wpis('w2', '2026-12-02'))
        licz, _, out = self.sync(proba=True)
        self.assertEqual((licz['dopisane'], licz['juz_w_arkuszu']), (1, 1))
        self.assertIn('już w arkuszu 2026-12-02 w1 (wiersz 2)', out)
        self.assertEqual(set(self.atrapa.wywolania), {'ping', 'odczyt'})
        self.assertTrue(all('arkusz' not in w for w in self.plik('2026-12').values()))

    def test_stary_kod_skryptu_czeka(self):
        AB.wyslij = self.atrapa = Atrapa(wersja=0)
        self.zapisz('2026-12', wpis('w1', '2026-12-02'))
        with self.assertRaises(AB.BladArkusza):
            self.sync()
        self.assertNotIn('arkusz', self.plik('2026-12')['w1'])

    def test_kontrola(self):
        self.zapisz('2026-12', wpis('w1', '2026-12-02'), wpis('w2', '2026-12-02'), wpis('w3', '2026-12-02'))
        self.sync()
        self.atrapa.w = [r for r in self.atrapa.w if r['id'] == 'w2']  # w1 skasowany ręcznie, w3 – niżej niewysłany
        self.atrapa.w.append({'o': ['wobcy'], 'kwota': 5, 'data': '2026-12-04'})
        ws = self.plik('2026-12')
        del ws['w3']['arkusz']
        ws['w3']['dodano'] = '2026-01-01 08:00'  # w3 niewysłany od dawna
        self.zapisz('2026-12', *ws.values())
        licz, problemy = AB.kontrola(K)
        self.assertEqual(len(problemy), 3, problemy)
        self.assertTrue(any('brak wiersza' in p and 'w1' in p for p in problemy))
        self.assertTrue(any('niewysłany' in p and 'w3' in p for p in problemy))
        self.assertTrue(any('wobcy' in p for p in problemy))

    def test_kontrola_bez_polaczenia_nie_zglasza(self):
        def blad(k, akcja, **d):
            raise AB.BladArkusza('timeout', siec=True)
        AB.wyslij = blad
        os.environ.update(BUDZET_ARKUSZ_URL=K['url'], BUDZET_ARKUSZ_SEKRET=K['sekret'])
        try:
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(AB.main(['kontrola', '--cicho']), 0)
                self.assertEqual(AB.main(['sync', '--cicho']), 0)  # nic do wysłania – bez połączenia
                self.zapisz('2026-12', wpis('w1', '2026-12-02'))
                self.assertEqual(AB.main(['sync', '--cicho']), 1)  # sync zgłasza trwały problem
        finally:
            del os.environ['BUDZET_ARKUSZ_URL'], os.environ['BUDZET_ARKUSZ_SEKRET']
        self.assertIn('kontrola pominięta', out.getvalue())

    def test_usun_wiersz_z_platnoscia_zostaje(self):
        self.atrapa.w.append(dict(wpis('w1', '2026-12-02'), o=['w1', 'b00000000aa'], kwota=12.5))
        self.zapisz('2026-12', dict(wpis('w1', '2026-12-02'), arkusz={'wiersz': 2, 'skrot': 'x', 'czas': 'x'}, usuniety='2026-12-03 10:00'))
        licz, bledy, out = self.sync()
        self.assertEqual((licz['usuniete'], bledy, self.atrapa.w[0]['o'], self.plik('2026-12')), (1, [], ['b00000000aa'], {}))
        self.assertIn('zostaje – ma płatność z wyciągu', out)

    def test_kontrola_trwaly_blad_zglasza(self):
        def blad(k, akcja, **d):
            raise AB.BladArkusza('zły sekret')
        AB.wyslij = blad
        os.environ.update(BUDZET_ARKUSZ_URL=K['url'], BUDZET_ARKUSZ_SEKRET=K['sekret'])
        try:
            with redirect_stdout(io.StringIO()):
                self.assertEqual(AB.main(['kontrola', '--cicho']), 1)
        finally:
            del os.environ['BUDZET_ARKUSZ_URL'], os.environ['BUDZET_ARKUSZ_SEKRET']

    def test_juz_w_arkuszu_dostaje_biezaca_tresc(self):
        """Recenzja POM-29, 3: ID już w O (ponow, zamknięcie) – popraw bieżącą treścią, dopiero potem znacznik."""
        self.atrapa.w.append(dict(wpis('w1', '2026-12-02', kwota=-12.5), o=['w1'], kwota=12.5, opis='stary'))
        self.zapisz('2026-12', wpis('w1', '2026-12-02', kwota=-15.0))
        licz, _, _ = self.sync()
        self.assertEqual((licz['juz_w_arkuszu'], self.atrapa.wywolania[-1], self.atrapa.w[0]['kwota']), (1, 'popraw', -15.0 * -1))
        self.assertTrue(self.plik('2026-12')['w1']['arkusz'])

    def test_blokada_zamkniecia(self):
        self.zapisz('2026-12', wpis('w1', '2026-12-02'))
        AB.blokada('zaloz')
        with redirect_stdout(io.StringIO()) as out:
            licz, bledy = AB.sync(K, False)
        self.assertEqual((self.atrapa.wywolania, bledy), ([], []))
        self.assertIn('zamknięcie miesiąca w toku', out.getvalue())
        p = AB.plik_blokady()
        os.utime(p, (p.stat().st_atime - 3700, p.stat().st_mtime - 3700))  # porzucona po 60 min – sync ją ignoruje
        self.assertEqual(AB.sync(K, False)[0]['dopisane'], 1)
        AB.blokada('zaloz')
        AB.blokada('zdejmij')
        self.assertIsNone(AB.blokada_zamkniecia())

    def test_ponow(self):
        self.zapisz('2026-12', wpis('w1', '2026-12-02'))
        self.sync()
        self.atrapa.w.clear()
        self.assertEqual(AB.ponow(['1']), 1)  # ID bez prefiksu w też działa
        licz, _, _ = self.sync()
        self.assertEqual((licz['dopisane'], len(self.atrapa.w)), (1, 1))

    def test_a11_ponow_na_usunietym_nie_zdejmuje_znacznika(self):
        """A-11: „dopisz ponownie” na zapisie usuniętym – znacznik zostaje, sync usuwa wiersz (nie utyka)."""
        self.zapisz('2026-12', wpis('wU1', '2026-12-02'))
        self.sync()
        ws = self.plik('2026-12')
        ws['wU1']['usuniety'] = '2026-12-03 09:00'
        self.zapisz('2026-12', *ws.values())
        usuniete = []
        self.assertEqual((AB.ponow(['wU1'], usuniete), usuniete), (0, ['wU1']))
        licz, _, _ = self.sync()
        self.assertEqual((licz['usuniete'], self.atrapa.w, self.plik('2026-12')), (1, [], {}))

    def test_przypnij_z_pliku_zamkniecia(self):
        self.zapisz('2026-12', wpis('wp-1', '2026-12-02', kwota=-30.0), wpis('wp-2', '2026-12-02', kwota=-20.0))
        self.sync()
        wspolne.zapisz('miesiace/2026-12-zapis.json', {'przypiecia': [{'id_wyciagu': 'b00000000aa', 'wiersze': [
            {'id': 'wp-1', 'wiersz': 2, 'kwota': 30.3}, {'id': 'wp-2', 'wiersz': 3, 'kwota': None}]}]})
        licz, bledy = AB.przypnij(K, '2026-12', False)
        self.assertEqual((licz['zrobione'], bledy), (1, []))
        self.assertEqual([(r['o'], r['kwota']) for r in self.atrapa.w], [(['wp-1', 'b00000000aa'], 30.3), (['wp-2', 'b00000000aa'], 20.0)])
        self.atrapa.wywolania.clear()
        AB.przypnij(K, '2026-12', False)  # zrobione nie idą drugi raz
        self.assertEqual(self.atrapa.wywolania, [])

    def test_wiersz_jak_przy_zamknieciu(self):
        w = wpis('w1', '2026-12-02', kwota=-25.0, skladniki=[30.0, -5.0], budowa='p1', kat='Dom', pod='', typ='Inwestycja')
        r = wspolne.wiersz_wpisu(w)
        self.assertEqual((r['kwota'], r['notatki'], r['tag'], r['opis']), ('=30.00-5.00', 'z wpisu – w kosztorysie budowy (💸)',
                                                                           'import 2026-12', 'x'))
        self.assertEqual(wspolne.wiersz_wpisu(wpis('w2', '2026-12-02', kwota=40.0))['kwota'], -40.0)  # zwrot ujemny


if __name__ == '__main__':
    unittest.main()
