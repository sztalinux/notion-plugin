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
        # A-5: separator tysięcy i waluta przy kwocie; kropka tysięcy – odmowa zamiast kwoty tysiąc razy mniejszej
        self.assertEqual(wpis.parsuj('1 200,50, zam', sk)['kwota'], -1200.5)
        self.assertEqual((wpis.parsuj(f'12,50 {WAL}, zam', sk)['kwota'], wpis.parsuj(f'12,50 {WAL}, zam', sk)['kod']), (-12.5, 'zam'))
        self.assertEqual(wpis.parsuj(f'1 200 {WAL}, zam', sk)['kwota'], -1200.0)
        for zle in ('1.200,50, zam', '1.200, zam', '1,200.50, zam', '12 5, zam'):
            with self.assertRaises(ValueError, msg=zle):
                wpis.parsuj(zle, sk)


NARZ = Path(__file__).resolve().parent / 'budzet'


class Przeplyw(unittest.TestCase):
    """wpis.py + importuj.py jako procesy na zmyślonych danych w katalogu tymczasowym (BUDZET_DANE; danych produkcyjnych nie dotyka)."""

    def setUp(self):
        self.dane = Path(tempfile.mkdtemp())
        self.ustaw()
        (self.dane / 'kategorie.json').write_text(json.dumps({'Inwestycja': {'Dom': []}, 'Wydatek': {'Inne wydatki': []}}))
        (self.dane / 'reguly.json').write_text(json.dumps({'reguly': [], 'skroty': {'dom': ['Inwestycja', 'Dom', ''],
                                                                                    'pen': ['Przychód', 'Inne przychody', '']}}))
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

    def importuj(self, *dod, mies='2026-10'):
        self.uruchom('importuj.py', '--miesiac', mies, '--arkusz', 'ark.json', *dod)
        return json.loads((self.dane / 'miesiace' / f'{mies}.json').read_text(encoding='utf-8'))

    def zen(self, kwota):
        (self.dane / 'zen.csv').write_text('Naglowek\nTransactions:\n"Date,Transaction type,Description,Settlement amount"\n'
                                           f'"6 Oct 2026,Transfer,""HURTOWNIA TESTOWA"",{kwota},PLN,{kwota},PLN,1,,,,900.00"\n')

    def test_budowa_przelew_i_wyciag_jeden_wiersz(self):
        out = self.uruchom('wpis.py', 'dodaj', '300, z, dom, stal', '--data', '2026-10-05', '--id', 'p1', '--budowa', 'p1')
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

    def test_budowa_bez_konta_gotowka_bez_uwagi(self):
        out = self.uruchom('wpis.py', 'dodaj', '50, dom', '--data', '2026-10-08', '--id', 'p4', '--budowa', 'p4')
        self.assertIn('Gotówka', out)
        self.assertNotIn('uwaga', out)

    def gotowka(self, tekst, ark=None):
        """Lista drugiej osoby z kontem gotówki (osobnej listy gotówki już nie ma – gotówka idzie z wpisów)."""
        self.ustaw(lista_domyslne_konto='Gotówka')
        (self.dane / 'got.txt').write_text(tekst, encoding='utf-8')
        if ark:
            (self.dane / 'ark.json').write_text(json.dumps({'values': [['Data']] + ark}))
        return self.importuj('--lista', 'got.txt')

    def test_lista_gotowki_zwrot_i_przychod(self):
        m = self.gotowka('+50 dom\n100 pen\n')
        self.assertEqual(sorted((w['kat'], w['kwota']) for w in m['wiersze']), [('Dom', -50.0), ('Inne przychody', 100.0)])

    def test_lista_zwrot_juz_w_arkuszu(self):
        wiersz = ['05-Oct-2026', '', 'Inwestycja', '-50', 'Dom', '', 'Gotówka', '', 'zwrot', '', '', '', '2026-10', '', '']
        m = self.gotowka('+50 dom\n', ark=[wiersz])
        self.assertEqual((m['wiersze'], len(m['juz'])), ([], 1))

    def test_lista_oznacza_budowe(self):
        self.uruchom('wpis.py', 'dodaj', '60, dom', '--data', '2026-10-12', '--id', 'p9', '--budowa', 'p9')
        self.assertIn('[budowa]', self.uruchom('wpis.py', 'lista', '2026-10'))

    def test_wpisy_nie_sa_scalane(self):
        """Jeden ID = jeden wiersz (POM-29): zakup i zwrot z dwóch wpisów tego samego dnia to dwa wiersze."""
        self.uruchom('wpis.py', 'dodaj', '300, dom', '--data', '2026-10-09', '--id', 'p5', '--gotowka')
        self.uruchom('wpis.py', 'dodaj', '+50, dom, zwrot', '--data', '2026-10-09', '--id', 'p6', '--gotowka')
        m = self.importuj()
        self.assertEqual(sorted((w['konto'], w['kwota'], tuple(w['zrodla'])) for w in m['wiersze']),
                         [('Gotówka', -50.0, ('wp6',)), ('Gotówka', 300.0, ('wp5',))])
        self.assertNotIn('lista wydatków gotówkowych', ' '.join(m['braki']))

    def proces(self, skrypt, *arg):
        env = dict(os.environ, BUDZET_DANE=str(self.dane))
        r = subprocess.run([sys.executable, str(NARZ / skrypt), *arg], env=env, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def test_a17_zle_wejscie_linia_zamiast_sladu(self):
        """A-17: brak --arkusz, wyciąg bez nagłówka, brak pliku listy, uszkodzona linia wpisów – linia ✗, bez Traceback."""
        for arg, oczek in ((['--miesiac', '2026-10'], '--arkusz'),
                           (['--miesiac', '2026-10', '--arkusz', 'ark.json', '--lista', 'brak.txt'], '✗ --lista: brak pliku'),
                           (['--miesiac', '2026-10', '--arkusz', 'ark.json', '--zen', 'zen.csv'], '✗ zen.csv: brak linii')):
            (self.dane / 'zen.csv').write_text('to nie wyciąg\n')
            kod, out = self.proces('importuj.py', *arg)
            self.assertEqual((kod != 0, oczek in out, 'Traceback' in out), (True, True, False), out)
        self.uruchom('wpis.py', 'dodaj', '10, dom', '--data', '2026-10-05', '--id', 'j1')
        p = self.dane / 'listy' / '2026-10-wpisy.jsonl'
        p.write_text(p.read_text(encoding='utf-8') + '{"kwota": 12, zepsute\n', encoding='utf-8')
        for skrypt, arg in (('wpis.py', ['lista', '2026-10']), ('importuj.py', ['--miesiac', '2026-10', '--arkusz', 'ark.json'])):
            kod, out = self.proces(skrypt, *arg)
            self.assertEqual((kod, '2026-10-wpisy.jsonl: linia 2' in out, 'zepsute' in out, 'Traceback' in out),
                             (1, True, False, False), out)

    def test_sam_zwrot_ujemny(self):
        self.uruchom('wpis.py', 'dodaj', '+40, dom, zwrot', '--data', '2026-10-10', '--id', 'p7', '--gotowka')
        m = self.importuj()
        self.assertEqual([w['kwota'] for w in m['wiersze']], [-40.0])



def wiersz_ark(data, kwota, konto, ids, typ='Wydatek', kat='Zakupy', pod='Regularne'):
    """Wiersz Transakcje A:O jak z get_values (data dd-Mon-RRRR, kwota tekstem z walutą)."""
    from datetime import date
    d = date.fromisoformat(data)
    return [d.strftime('%d-%b-%Y'), 'Zrealizowane', typ, f'{kwota:.2f} ' + WAL, kat, pod, konto, 'Osoba A', 'opis', '',
            f'import {data[:7]}', 'z wpisu', data[:7], data[:4], ids]


class PrzeplywArkusz(unittest.TestCase):
    """POM-29: wpisy z kart przy zamknięciu – przełom miesiąca, przypięcie do wiersza z wpisu, reguła „do dnia X”."""
    ustaw, uruchom, importuj = Przeplyw.ustaw, Przeplyw.uruchom, Przeplyw.importuj

    def setUp(self):
        Przeplyw.setUp(self)
        (self.dane / 'kategorie.json').write_text(json.dumps({'Wydatek': {'Zakupy': ['Regularne'], 'Inne wydatki': []},
                                                             'Inwestycja': {'Dom': []}}))
        (self.dane / 'reguly.json').write_text(json.dumps({'reguly': [dict(
            klucz='SKLEP STALY', kierunek='wypływ', typ='Wydatek', kat='Zakupy', pod='Regularne', pewnosc='Zawsze', opcje=[],
            uwaga='')], 'skroty': {'zak': ['Wydatek', 'Zakupy', 'Regularne'], 'dom': ['Inwestycja', 'Dom', '']}}))

    def zen_wiele(self, *tr):
        linie = ''.join(f'"{d},Card payment,""{o}"",{k},PLN,{k},PLN,1,,,,900.00"\n' for d, o, k in tr)
        (self.dane / 'zen.csv').write_text('Naglowek\nTransactions:\n"Date,Transaction type,Description,Settlement amount"\n' + linie)

    def ark(self, *wiersze):
        (self.dane / 'ark.json').write_text(json.dumps({'values': [['Data']] + list(wiersze)}))

    def wpisz(self, mies, *ws):
        (self.dane / 'listy').mkdir(exist_ok=True)
        (self.dane / 'listy' / f'{mies}-wpisy.jsonl').write_text(''.join(json.dumps(w, ensure_ascii=False) + '\n' for w in ws),
                                                                 encoding='utf-8')

    @staticmethod
    def karta(id_, data, kwota, **dod):
        return dict(dict(id=id_, data=data, tekst=f'{kwota}, z, zak', kwota=-kwota, skladniki=None, konto='K-bank',
                         osoba='Osoba A', kod='zak', typ='Wydatek', kat='Zakupy', pod='Regularne', opis='', budowa=''), **dod)

    def test_przelom_miesiaca_czeka_potem_para(self):
        self.wpisz('2026-10', self.karta('wk1', '2026-10-30', 100.0))
        self.zen_wiele(('29 Oct 2026', 'INNE', '-1.00'))
        m = self.importuj('--zen', 'zen.csv')
        self.assertEqual([d['id'] for d in m['decyzje'] if d['id'] == 'wk1'], [])  # nie na stronę decyzji – czeka
        self.assertTrue(any(p['id'] == 'wk1' and 'czeka' in p['powod'] for p in m['pominiete']))
        self.zen_wiele(('29 Oct 2026', 'INNE', '-1.00'), ('2 Nov 2026', 'SKLEP X', '-100.40'))
        m = self.importuj('--zen', 'zen.csv', mies='2026-11')
        a = [a for a in m['auto'] if a.get('ids_w') == ['wk1']]
        self.assertEqual((len(a), a[0]['kwota_ark']), (1, 100.4))  # kwota z wyciągu, wiersz z kategorią wpisu

    def test_niepelny_wyciag_w_srodku_miesiaca_decyzja_i_brak(self):
        """Czeka tylko wpis z ostatnich 4 dni miesiąca; wcześniejszy bez pary przy krótkim wyciągu – decyzja i „Brakuje”."""
        self.wpisz('2026-10', self.karta('wk5', '2026-10-15', 40.0))
        self.zen_wiele(('12 Oct 2026', 'INNE', '-1.00'))
        m = self.importuj('--zen', 'zen.csv')
        self.assertIn('wk5', [d['id'] for d in m['decyzje']])
        self.assertTrue(any('kończy się 12.10' in b for b in m['braki']))

    def test_przypiecie_do_wiersza_z_wpisu(self):
        self.wpisz('2026-12', self.karta('wk2', '2026-12-30', 50.0))
        self.ark(wiersz_ark('2026-12-30', 50.0, 'K-bank', 'wk2'))
        self.zen_wiele(('2 Jan 2027', 'SKLEP Y', '-50.80'))
        m = self.importuj('--zen', 'zen.csv', mies='2027-01')  # wpis z końca grudnia, płatność ze stycznia
        self.assertEqual((m['auto'], m['wiersze'][:-1] if m['wiersze'] and m['wiersze'][-1]['kwota'] is None else m['wiersze']),
                         ([], []))
        p = m['przypiecia']
        self.assertEqual((len(p), p[0]['wiersze']), (1, [{'id': 'wk2', 'wiersz': 2, 'kwota': 50.8}]))
        self.assertEqual([j['sposob'] for j in m['juz']], ['z wpisu – przypięte do wiersza'])
        ark = json.loads((self.dane / 'ark.json').read_text())
        ark['values'][1][14] = 'wk2,' + p[0]['id_wyciagu']  # po przypięciu: kolejny import nie rusza tego wiersza
        (self.dane / 'ark.json').write_text(json.dumps(ark))
        m = self.importuj('--zen', 'zen.csv', mies='2027-01')
        self.assertEqual((m['przypiecia'], m['auto'], [j['sposob'] for j in m['juz']]), ([], [], ['zaimportowane wcześniej']))

    def test_grupa_przypieta_roznica_na_najwieksza(self):
        g = dict(grupa='paragon-1')
        self.wpisz('2026-12', self.karta('wp-1', '2026-12-10', 30.0, **g), self.karta('wp-2', '2026-12-10', 20.0, **g))
        self.ark(wiersz_ark('2026-12-10', 30.0, 'K-bank', 'wp-1'), wiersz_ark('2026-12-10', 20.0, 'K-bank', 'wp-2'))
        self.zen_wiele(('11 Dec 2026', 'SKLEP Z', '-50.30'), ('30 Dec 2026', 'INNE', '-1.00'))
        m = self.importuj('--zen', 'zen.csv', mies='2026-12')
        self.assertEqual(m['przypiecia'][0]['wiersze'], [{'id': 'wp-1', 'wiersz': 2, 'kwota': 30.3},
                                                        {'id': 'wp-2', 'wiersz': 3, 'kwota': None}])

    def zamknij(self, mies, ark, zen, wpisy):
        self.ark(*ark)
        self.zen_wiele(*zen)
        for m, ws in wpisy.items():
            self.wpisz(m, *ws)
        return self.importuj('--zen', 'zen.csv', mies=mies)

    def test_s1_reczny_wiersz_i_wpis_bez_wiersza_bez_dubla(self):
        """Recenzja POM-29, S1/S1b/S2: płatność zajęta przez ręczny wiersz (1:1, suma) albo po ID – wpis bez wiersza nie
        daje drugiego wiersza ani decyzji z kategorią."""
        x = ('30 Nov 2026', 'X', '-1.00')
        for ark, zen, sposob in (
                ([wiersz_ark('2026-11-10', 100.0, 'K-bank', '')], [('10 Nov 2026', 'SKLEP', '-100.00'), x], '1:1'),
                ([wiersz_ark('2026-11-10', 150.0, 'K-bank', '')],
                 [('10 Nov 2026', 'SKLEP', '-100.00'), ('11 Nov 2026', 'SKLEP2', '-50.00'), x], 'w sumie 2')):
            m = self.zamknij('2026-11', ark, zen, {'2026-11': [self.karta('wa', '2026-11-10', 100.0)]})
            self.assertEqual(m['wiersze'], [])
            self.assertTrue(all(sposob in j['sposob'] for j in m['juz']))
            self.assertNotIn('wa', [d['id'] for d in m['decyzje']])
            self.assertTrue(any(p['id'] == 'wa' and 'już w arkuszu' in p['powod'] for p in m['pominiete']))
        m = self.zamknij('2026-11', [], [('10 Nov 2026', 'SKLEP', '-100.00'), x], {'2026-11': []})
        bid = next(d['id'] for d in m['decyzje'] if abs(d['kwota'] + 100) < 0.01)
        m = self.zamknij('2026-11', [wiersz_ark('2026-11-10', 100.0, 'K-bank', bid)], [('10 Nov 2026', 'SKLEP', '-100.00'), x],
                         {'2026-11': [self.karta('wa', '2026-11-10', 100.0)]})
        self.assertEqual(([j['sposob'] for j in m['juz']], m['wiersze']), (['zaimportowane wcześniej'], []))
        self.assertNotIn('wa', [d['id'] for d in m['decyzje']])

    def test_s3_wpis_czekajacy_nie_ginie(self):
        """S3a: wpis z końca miesiąca przy krótkim wyciągu czeka i jest linia w „Brakuje”; S3b: płatność z poprzedniego
        miesiąca w imporcie kolejnego – wiersz z płatności; bez płatności także w kolejnym – decyzja."""
        wc = {'2026-11': [self.karta('wc', '2026-11-29', 40.0)]}
        m = self.zamknij('2026-11', [], [('25 Nov 2026', 'X', '-1.00')], wc)
        self.assertTrue(any(p['id'] == 'wc' and 'czeka' in p['powod'] for p in m['pominiete']))
        self.assertTrue(any('kończy się 25.11' in b for b in m['braki']))
        m = self.zamknij('2026-12', [], [('25 Nov 2026', 'X', '-1.00'), ('30 Nov 2026', 'SKLEP', '-40.00'),
                                         ('31 Dec 2026', 'X', '-1.00')], wc)
        self.assertEqual([(w['data'], w['kwota']) for w in m['wiersze']], [('2026-11-30', 40.0)])
        m = self.zamknij('2026-12', [], [('25 Nov 2026', 'X', '-1.00'), ('31 Dec 2026', 'X', '-1.00')], wc)
        self.assertIn('wc', [d['id'] for d in m['decyzje']])

    def test_przenies_na_swiezym_odczycie(self):
        """Recenzja POM-29, 4–5 i 14: pod blokadą zamknięcia przenies.py liczy numery ze świeżego odczytu, odrzuca wiersze,
        których ID jest już w O, a zwrot do wiersza bez ID przenosi tylko przy zgodnej treści."""
        reczny = wiersz_ark('2026-12-03', 80.0, 'K-bank', '')
        self.ark(reczny)
        zwrot = dict(id='bzw0000001', data='2026-12-09', konto='K-bank', osoba='Osoba A', kwota=10.0, opis='ZWROT', zrodlo='zwrot',
                     pewnosc='Zwykle', regula='', propozycja=None, opcje=[], uwaga='')
        auto = dict(id='wz9', data='2026-12-04', konto='Gotówka', osoba='Osoba B', typ='Wydatek', kat='Zakupy', pod='Regularne',
                    regula='zak', opis_w='x', kwota_ark=5.0, skladniki=None, ids_w=['wz9'], notatki='z wpisu')
        (self.dane / 'miesiace').mkdir(exist_ok=True)
        (self.dane / 'miesiace' / '2026-12.json').write_text(json.dumps(dict(
            miesiac='2026-12', arkusz_plik='ark.json', auto=[auto], decyzje=[zwrot], wiersze=[], przypiecia=[])))
        db = self.dane / 'miesiace' / 'db-2026-12' / 'decyzje'
        db.mkdir(parents=True)
        (db / 'bzw0000001.json').write_text(json.dumps({'akcja': 'odejmij', 'wiersz': 2}))
        zapis = lambda: json.loads((self.dane / 'miesiace' / '2026-12-zapis.json').read_text(encoding='utf-8'))
        self.uruchom('przenies.py', '--miesiac', '2026-12')
        self.assertEqual(([w[14] for w in zapis()['wiersze']], zapis()['zmiany'][0]['wiersz']), (['wz9'], 2))
        swiezy = self.dane / 'swiezy.json'  # sync dopisał w międzyczasie wiersz z wz9 nad ręcznym (inny układ)
        swiezy.write_text(json.dumps({'values': [['Data'], wiersz_ark('2026-12-04', 5.0, 'Gotówka', 'wz9'), reczny]}))
        self.uruchom('przenies.py', '--miesiac', '2026-12', '--arkusz', 'swiezy.json')
        self.assertEqual((zapis()['wiersze'], zapis()['zmiany'][0]['wiersz']), ([], 3))
        inny = wiersz_ark('2026-12-03', 81.0, 'K-bank', '')  # ktoś zmienił kwotę ręcznego wiersza – odmowa
        swiezy.write_text(json.dumps({'values': [['Data'], inny]}))
        self.uruchom('przenies.py', '--miesiac', '2026-12', '--arkusz', 'swiezy.json')
        self.assertEqual((zapis()['zmiany'], [x['id'] for x in zapis()['do_wyjasnienia']]), ([], ['bzw0000001']))

    def test_regula_do_dnia_x_bez_wierszy_z_wpisow(self):
        self.zen_wiele(('5 Dec 2026', 'SKLEP STALY', '-10.00'), ('30 Dec 2026', 'INNE', '-1.00'))
        self.ark(wiersz_ark('2026-12-20', 99.0, 'K-bank', 'wk3'))  # wiersz z wpisu po dacie płatności
        self.wpisz('2026-12', self.karta('wk3', '2026-12-20', 99.0))
        m = self.importuj('--zen', 'zen.csv', mies='2026-12')
        self.assertEqual([a['regula'] for a in m['auto']], ['SKLEP STALY'])
        self.ark(wiersz_ark('2026-12-20', 99.0, 'K-bank', ''))  # ten sam wiersz wpisany ręcznie – „sprawdź, czy nie siedzi w sumie”
        self.wpisz('2026-12')
        m = self.importuj('--zen', 'zen.csv', mies='2026-12')
        self.assertTrue(any(d['moze_juz'] for d in m['decyzje']))

    def test_wpis_w_arkuszu_bez_pary_decyzja_bez_nowego_wiersza(self):
        self.wpisz('2026-12', self.karta('wk4', '2026-12-05', 70.0))
        self.ark(wiersz_ark('2026-12-05', 70.0, 'K-bank', 'wk4'))
        self.zen_wiele(('30 Dec 2026', 'INNE', '-1.00'))
        m = self.importuj('--zen', 'zen.csv', mies='2026-12')
        d = [d for d in m['decyzje'] if d['id'] == 'wk4'][0]
        self.assertEqual((d['w_arkuszu'], d['kandydaci'][0]['wiersz']), (2, 2))
        db = self.dane / 'miesiace' / 'db-2026-12' / 'decyzje'
        db.mkdir(parents=True)
        (db / 'wk4.json').write_text(json.dumps({'akcja': 'kategoria', 'typ': 'Wydatek', 'kat': 'Zakupy', 'pod': 'Regularne'}))
        self.uruchom('przenies.py', '--miesiac', '2026-12')
        z = json.loads((self.dane / 'miesiace' / '2026-12-zapis.json').read_text(encoding='utf-8'))
        self.assertEqual(([w for w in z['wiersze'] if 'wk4' in w[14]], [x['id'] for x in z['do_wyjasnienia']]), ([], ['wk4']))

    def test_zapas_wiersz_z_zamkniecia_jak_z_synchronizacji(self):
        """Wpis bez wiersza w arkuszu (skrypt nie wdrożony) – zamknięcie daje ten sam wiersz co sync (A:L i O)."""
        self.uruchom('wpis.py', 'dodaj', '30-5, zak, bułki', '--data', '2026-12-03', '--id', 'z1')
        self.importuj(mies='2026-12')
        self.uruchom('przenies.py', '--miesiac', '2026-12')
        z = json.loads((self.dane / 'miesiace' / '2026-12-zapis.json').read_text(encoding='utf-8'))
        w = [w for w in z['wiersze'] if w[14] == 'wz1'][0]
        zapis = json.loads((self.dane / 'listy' / '2026-12-wpisy.jsonl').read_text(encoding='utf-8'))
        sys.path.insert(0, str(NARZ))
        r = wspolne.wiersz_wpisu(zapis)
        self.assertEqual(w[:12] + [w[14]], [r['data'], r['status'], r['typ'], r['kwota'], r['kat'], r['pod'], r['konto'], r['osoba'],
                                            r['opis'], '', r['tag'], r['notatki'], r['id']])

    def decyduj(self, mies, **dec):
        db = self.dane / 'miesiace' / f'db-{mies}' / 'decyzje'
        db.mkdir(parents=True, exist_ok=True)
        for id_, d in dec.items():
            (db / f'{id_}.json').write_text(json.dumps(d))

    def zapis(self, mies):
        return json.loads((self.dane / 'miesiace' / f'{mies}-zapis.json').read_text(encoding='utf-8'))

    def test_a6_zwrot_dzialaniem_z_decyzji_ujemny(self):
        """A-6: zwrot zapisany działaniem z kategorią rozstrzyganą na stronie – ten sam znak co przy znanym skrócie."""
        self.uruchom('wpis.py', 'dodaj', '+30-5, xyz', '--data', '2026-12-03', '--id', 'zw1')
        self.uruchom('wpis.py', 'dodaj', '+30-5, zak', '--data', '2026-12-03', '--id', 'zw2')
        self.importuj(mies='2026-12')
        self.decyduj('2026-12', wzw1={'akcja': 'kategoria', 'typ': 'Wydatek', 'kat': 'Zakupy', 'pod': 'Regularne'})
        self.uruchom('przenies.py', '--miesiac', '2026-12')
        d = {w[14]: w[3] for w in self.zapis('2026-12')['wiersze']}
        self.assertEqual((d['wzw1'], d['wzw2']), ('=-30.00+5.00', '=-30.00+5.00'))

    def sync_atrapa(self, atrapa, **kw):
        """arkusz_budzetu.sync w tym procesie na folderze testu, z atrapą skryptu arkusza zamiast sieci."""
        import io
        from contextlib import redirect_stdout
        import arkusz_budzetu as AB
        import test_budzet_arkusz as TA
        stare, AB.wyslij, wspolne.DANE = wspolne.DANE, atrapa, self.dane
        try:
            with redirect_stdout(io.StringIO()):
                return AB.sync(TA.K, False, **kw)
        finally:
            wspolne.DANE = stare

    def kontrola_atrapa(self, atrapa):
        import arkusz_budzetu as AB
        import test_budzet_arkusz as TA
        stare, AB.wyslij, wspolne.DANE = wspolne.DANE, atrapa, self.dane
        try:
            return AB.kontrola(TA.K)[1]
        finally:
            wspolne.DANE = stare

    def test_a1_wpis_z_recznym_wierszem_nie_wraca_przez_sync(self):
        """A-1: wpis rozstrzygnięty przy zamknięciu bez ID w O (ręczny wiersz, Pomiń) – sync po zamknięciu nic nie dopisuje,
        także gdy krok zamknij-wpisy pominięto; zmiana wpisu po zamknięciu – kontrola, nie popraw."""
        import test_budzet_arkusz as TA
        self.uruchom('wpis.py', 'dodaj', '80, zak, bazar', '--data', '2026-12-05', '--id', 'blokA')  # sync nie działa
        self.uruchom('wpis.py', 'dodaj', '15, xyz', '--data', '2026-12-06', '--id', 'blokB')  # nieznany skrót -> Pomiń
        self.ark([*wiersz_ark('2026-12-05', 80.0, 'Gotówka', '')[:7], 'Osoba B', *wiersz_ark('2026-12-05', 80.0, 'Gotówka', '')[8:]])
        m = self.importuj(mies='2026-12')
        self.assertEqual(m['wpisy_rozstrzygniete'], ['wblokA'])
        self.decyduj('2026-12', wblokB={'akcja': 'pomin'})
        self.uruchom('przenies.py', '--miesiac', '2026-12')
        self.assertEqual((self.zapis('2026-12')['wpisy_rozstrzygniete'], self.zapis('2026-12')['wiersze']), (['wblokA', 'wblokB'], []))
        reczny = dict(o=[], data='2026-12-05', kwota=80.0)
        atrapa = TA.Atrapa([reczny])
        licz, bledy = self.sync_atrapa(atrapa)  # bezpiecznik: bez zamknij-wpisy sync sam oznacza
        self.assertEqual((licz['dopisane'], licz.get('zamkniete'), bledy, atrapa.w), (0, 2, [], [reczny]))
        self.assertIn('0 zapisach', self.uruchom('arkusz_budzetu.py', 'zamknij-wpisy', '--miesiac', '2026-12'))  # idempotentne
        p = self.dane / 'listy' / '2026-12-wpisy.jsonl'
        ws = [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines()]
        self.assertEqual([w['arkusz']['zamkniecie'] for w in ws], ['2026-12', '2026-12'])
        for w in ws:
            w['dodano'] = '2026-01-01 08:00'  # dawno – kontrola zgłosiłaby niewysłany, gdyby znacznik nie działał
        p.write_text(''.join(json.dumps(w, ensure_ascii=False) + '\n' for w in ws), encoding='utf-8')
        self.assertEqual(self.kontrola_atrapa(atrapa), [])
        self.uruchom('wpis.py', 'dodaj', '82, zak, bazar', '--data', '2026-12-05', '--id', 'blokA')  # poprawka po zamknięciu
        licz, bledy = self.sync_atrapa(atrapa)
        self.assertEqual((licz['dopisane'], licz['poprawione'], bledy, atrapa.w), (0, 0, [], [reczny]))
        self.assertTrue(any('zmieniony po zamknięciu' in x and 'wblokA' in x for x in self.kontrola_atrapa(atrapa)))
        self.assertIn('rozstrzygnięty przy zamknięciu', self.uruchom('arkusz_budzetu.py', 'ponow', 'blokA'))
        self.uruchom('arkusz_budzetu.py', 'zamknij-wpisy', 'blokA')  # wiersz poprawiony ręcznie – odśwież znacznik
        self.assertEqual(self.kontrola_atrapa(atrapa), [])

    def test_a1_przenies_na_swiezym_odczycie_wykrywa_dubel(self):
        """A-1: sync dopisał wpis po imporcie, a import dopasował go do ręcznego wiersza – do wyjaśnienia, bez znacznika."""
        self.uruchom('wpis.py', 'dodaj', '80, zak', '--data', '2026-12-05', '--id', 'blokA')
        reczny = [*wiersz_ark('2026-12-05', 80.0, 'Gotówka', '')[:7], 'Osoba B', *wiersz_ark('2026-12-05', 80.0, 'Gotówka', '')[8:]]
        self.ark(reczny)
        self.importuj(mies='2026-12')
        (self.dane / 'swiezy.json').write_text(json.dumps({'values': [['Data'], reczny,
                                                                      wiersz_ark('2026-12-05', 80.0, 'Gotówka', 'wblokA')]}))
        self.uruchom('przenies.py', '--miesiac', '2026-12', '--arkusz', 'swiezy.json')
        z = self.zapis('2026-12')
        self.assertEqual((z['wpisy_rozstrzygniete'], [x['id'] for x in z['do_wyjasnienia']]), ([], ['wblokA']))

    def test_a1_miesiac_zamkniety_starsza_wersja_odmowa(self):
        """A-1, bezpiecznik: plik zapisu bez listy wpisów rozstrzygniętych (starsza wersja) – sync nie dopisuje bez flagi."""
        import test_budzet_arkusz as TA
        self.uruchom('wpis.py', 'dodaj', '80, zak', '--data', '2026-12-05', '--id', 'blokA')
        (self.dane / 'miesiace').mkdir(exist_ok=True)
        (self.dane / 'miesiace' / '2026-12-zapis.json').write_text(json.dumps({'wiersze': [], 'przypiecia': []}))
        atrapa = TA.Atrapa()
        licz, bledy = self.sync_atrapa(atrapa)
        self.assertEqual((licz['dopisane'], len(bledy), atrapa.w), (0, 1, []))
        self.assertIn('--mimo-zamkniecia', bledy[0])
        licz, bledy = self.sync_atrapa(atrapa, mimo_zamkniecia=True)
        self.assertEqual((licz['dopisane'], bledy), (1, []))

    def test_a2_platnosc_inna_kwota_niz_wpis_do_decyzji_z_kandydatem(self):
        """A-2: wpis z karty (wiersz z sync) i płatność tego dnia o innej kwocie (napiwek) z regułą „Zawsze” – nie nowy
        wiersz obok wpisu, tylko decyzja z wierszem wpisu; „Już w arkuszu” przypina płatność do tego wiersza."""
        self.wpisz('2026-12', self.karta('wR1', '2026-12-05', 100.0))
        self.ark(wiersz_ark('2026-12-05', 100.0, 'K-bank', 'wR1'))
        self.zen_wiele(('5 Dec 2026', 'SKLEP STALY', '-115.00'), ('30 Dec 2026', 'INNE', '-1.00'))
        m = self.importuj('--zen', 'zen.csv', mies='2026-12')
        self.assertEqual([a['regula'] for a in m['auto']], [])
        d = [d for d in m['decyzje'] if d['regula'] == 'SKLEP STALY'][0]
        self.assertEqual(([k['wiersz'] for k in d['kandydaci']], 'wR1' in d['uwaga']), ([2], True))
        self.assertIn('115', [x for x in m['decyzje'] if x['id'] == 'wR1'][0]['uwaga'])
        self.decyduj('2026-12', **{d['id']: {'akcja': 'juz', 'wiersz': 2}, 'wR1': {'akcja': 'juz', 'wiersz': 2}})
        self.uruchom('przenies.py', '--miesiac', '2026-12')
        z = self.zapis('2026-12')
        self.assertEqual((z['wiersze'], [(p['id_wyciagu'], p['wiersze']) for p in z['przypiecia']]),
                         ([], [(d['id'], [{'id': 'wR1', 'wiersz': 2, 'kwota': 115.0}])]))
        self.ark()  # wpisu nie ma w arkuszu (sync nie działał) – też decyzja, nie wiersz z reguły obok wpisu
        m = self.importuj('--zen', 'zen.csv', mies='2026-12')
        d = [d for d in m['decyzje'] if d['regula'] == 'SKLEP STALY'][0]
        self.assertEqual((m['auto'], d['kandydaci'], 'przypiecie_wpisu' in d, 'wR1' in d['uwaga']), ([], [], False, True))

    def test_a3_przychod_bez_plusa_paruje_sie_z_wplywem(self):
        """A-3: „100, z, pen” (przychód bez „+”) – w arkuszu +100, więc przy zamknięciu paruje się z wpływem jak „+100”."""
        for kwota in (-100.0, 100.0):
            self.wpisz('2026-12', self.karta('wP1', '2026-12-05', -kwota, typ='Przychód', kat='Inne przychody', pod='', kod='pen'))
            self.ark(wiersz_ark('2026-12-05', 100.0, 'K-bank', 'wP1', typ='Przychód', kat='Inne przychody', pod=''))
            self.zen_wiele(('5 Dec 2026', 'PRACODAWCA', '100.00'), ('30 Dec 2026', 'INNE', '-1.00'))
            m = self.importuj('--zen', 'zen.csv', mies='2026-12')
            self.assertEqual((len(m['przypiecia']), [d['id'] for d in m['decyzje'] if d['kwota'] > 0 or d['id'] == 'wP1'], m['auto']),
                             (1, [], []), kwota)

    def test_a4_wyciag_niepelny_albo_brak_pliku(self):
        """A-4: wyciąg kończący się w połowie miesiąca – linia w „Brakuje” także bez wpisów; podany, a brakujący plik – stop."""
        self.zen_wiele(('3 Dec 2026', 'SKLEP STALY', '-10.00'))
        m = self.importuj('--zen', 'zen.csv', mies='2026-12')
        self.assertTrue(any('K-bank kończy się 03.12' in b for b in m['braki']), m['braki'])
        self.assertTrue(any('wyciąg K-mb brak' in b for b in m['braki']), m['braki'])
        kod, out = Przeplyw.proces(self, 'importuj.py', '--miesiac', '2026-12', '--arkusz', 'ark.json', '--zen', 'zen.csv',
                                   '--mbank', 'wyciagi/mbank-grudzien.csv')
        self.assertEqual((kod, '✗ brak pliku wyciągu' in out, 'Traceback' in out), (1, True, False), out)

    def test_wpis_przenosi_znacznik_i_usuwa_po_wysylce(self):
        self.uruchom('wpis.py', 'dodaj', '10, zak', '--data', '2026-12-30', '--id', 'q1')
        p = self.dane / 'listy' / '2026-12-wpisy.jsonl'
        w = json.loads(p.read_text(encoding='utf-8'))
        w['arkusz'] = {'wiersz': 7, 'skrot': 'x', 'czas': '2026-12-30 10:00'}
        p.write_text(json.dumps(w) + '\n', encoding='utf-8')
        self.uruchom('wpis.py', 'dodaj', '12, zak', '--data', '2027-01-02', '--id', 'q1')  # zmiana daty na inny miesiąc
        self.assertEqual(p.read_text(encoding='utf-8'), '')
        nowy = json.loads((self.dane / 'listy' / '2027-01-wpisy.jsonl').read_text(encoding='utf-8'))
        self.assertEqual((nowy['kwota'], nowy['arkusz']['wiersz']), (-12.0, 7))
        self.assertIn('arkusz_budzetu.py sync', self.uruchom('wpis.py', 'usun', '2027-01', 'q1'))
        self.assertIn('usuniety', (self.dane / 'listy' / '2027-01-wpisy.jsonl').read_text(encoding='utf-8'))
        self.assertIn('2027-01: 0 wpisów', self.uruchom('wpis.py', 'lista', '2027-01'))
        self.uruchom('wpis.py', 'dodaj', '5, zak', '--data', '2027-01-03', '--id', 'q2')
        self.uruchom('wpis.py', 'usun', '2027-01', 'q2')  # niewysłany – znika od razu
        self.assertNotIn('wq2', (self.dane / 'listy' / '2027-01-wpisy.jsonl').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
