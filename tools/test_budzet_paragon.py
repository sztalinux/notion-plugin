"""Testy paragonów budżetu (POM-30: tools/budzet/paragon.py, grupy w importuj.py i wpis.py) na danych zmyślonych, bez sieci
(python3 tools/test_budzet_paragon.py). Sklepy, pozycje i kwoty są wymyślone."""
import email.message, io, json, os, subprocess, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path

os.environ.setdefault('BUDZET_DANE', tempfile.mkdtemp())
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / 'budzet'))
import arkusz_budzetu as AB  # noqa: E402
import paragon as P  # noqa: E402
import wspolne  # noqa: E402
import test_budzet as TB  # noqa: E402
import test_budzet_arkusz as TA  # noqa: E402

NARZ, wiersz_ark, K, Atrapa = TB.NARZ, TB.wiersz_ark, TA.K, TA.Atrapa

SKROTY = {'zak': ['Wydatek', 'Zakupy', 'Regularne'], 'chem': ['Wydatek', 'Zakupy', 'Chemia'],
          'dom': ['Inwestycja', 'Dom', ''], 'pen': ['Przychód', 'Inne przychody', '']}
UST = dict(konto_zen='K-bank', konto_mbank='K-mb', gotowka_konto='Gotówka', osoba_listy='Osoba B', osoba_wyciagi='Osoba A',
           skroty_kont={'z': 'K-bank', 'g': 'Gotówka', 'pra': 'K-praca'}, skroty_osob={'o': 'Osoba B', 'a': 'Osoba A'},
           konta_list={'praca': 'K-praca'})


class Rozpisanie(unittest.TestCase):
    def test_najwieksze_reszty_suma_co_do_grosza(self):
        self.assertEqual(P.rozloz(-100, [1000, 1000, 1000]), [-34, -33, -33])
        self.assertEqual(P.rozloz(7, [500, 300, 200]), [4, 2, 1])
        for kw, wagi in ((-1, [1, 1, 1]), (-299, [1234, 77, 5]), (13, [999, 1])):
            self.assertEqual(sum(P.rozloz(kw, wagi)), kw)

    def test_rabat_i_kaucja_na_kategorie(self):
        cz = P.rozpisz(['10,00, zak, chleb', '20.00, chem, płyn', '5, zak, ser?', '-3,00, rabat', '1,50, kaucja'], 3350, SKROTY)
        self.assertEqual([(c['kat'], c['pod'], c['grosze']) for c in cz], [('Zakupy', 'Regularne', 1436), ('Zakupy', 'Chemia', 1914)])
        self.assertEqual(sum(c['korekta'] for c in cz), -150)
        self.assertEqual(cz[0]['opisy'], ['chleb', 'ser?'])

    def test_rabat_pod_pozycja_zostaje_w_kategorii(self):
        cz = P.rozpisz(['10, zak', '20, chem', '-2, chem, rabat płyn'], 2800, SKROTY)
        self.assertEqual([c['grosze'] for c in cz], [1000, 1800])

    def test_niezgodna_suma_to_blad(self):
        with self.assertRaisesRegex(P.BladParagonu, 'różnica'):
            P.rozpisz(['10, zak', '20, chem'], 3001, SKROTY)

    def test_nieznany_skrot_i_przychod_to_blad(self):
        with self.assertRaisesRegex(P.BladParagonu, 'nieznany skrót'):
            P.rozpisz(['10, xyz'], 1000, SKROTY)
        with self.assertRaises(P.BladParagonu):
            P.rozpisz(['10, pen'], 1000, SKROTY)
        with self.assertRaises(P.BladParagonu):
            P.rozpisz(['10, zak', '-20, rabat'], -1000, SKROTY)

    def test_separator_tysiecy_i_trzy_miejsca(self):
        self.assertEqual([c['grosze'] for c in P.rozpisz(['1 234,56, zak', '1\u00a0000, chem'], 223456, SKROTY)], [123456, 100000])
        with self.assertRaisesRegex(P.BladParagonu, '2 miejscami'):
            P.rozpisz(['1,234, zak'], 123, SKROTY)

    def test_indeks_id_najwieksza_czesc(self):
        w = [dict(wiersz=2, kwota=10.0, ids=['wp-1', 'b1']), dict(wiersz=3, kwota=30.0, ids=['wp-2', 'b1']),
             dict(wiersz=4, kwota=5.0, ids=['wp-3', 'b1'])]
        self.assertEqual(wspolne.indeks_id(w)['b1']['wiersz'], 3)

    def test_brak_kto_i_czym(self):
        wspolne.U.update(UST)
        for zle in ('', None, 'xyz', 'z, q'):
            with self.assertRaises(P.BladParagonu):
                P.platnosc(zle)
        self.assertEqual(P.platnosc('z, a'), ('z', 'a'))
        self.assertEqual(P.platnosc('gotówka'), ('', ''))

    def test_notatka_wiersza(self):
        w = dict(id='wp1-1', data='2026-12-05', kwota=-14.36, typ='Wydatek', kat='Zakupy', pod='Regularne', konto='K-bank',
                 osoba='Osoba A', opis='Sklep A: chleb', kod='zak', paragon=dict(sklep='Sklep A', suma=33.5, czesci=2))
        self.assertEqual(wspolne.wiersz_wpisu(w)['notatki'], 'z paragonu – Sklep A, razem 33.50, części 2')


class Pobieranie(unittest.TestCase):
    URL = 'https://prod-files-secure.s3.us-west-2.amazonaws.com/x/y/image.png?X-Amz-Signature=abc#notion_record=1'

    class Odp(io.BytesIO):
        def __init__(self, tresc, typ):
            super().__init__(tresc)
            self.headers = email.message.Message()
            self.headers['Content-Type'] = typ

        def __exit__(self, *a):
            self.close()

    def test_tylko_https_i_hosty_notion(self):
        for zly in ('http://prod-files-secure.s3.us-west-2.amazonaws.com/a.png', 'https://example.com/a.png',
                    'https://prod-files-secure.s3.us-west-2.amazonaws.com.zly.example/a.png'):
            with self.assertRaises(P.BladParagonu):
                P.sprawdz_adres(zly)
        with self.assertRaises(P.BladParagonu):  # przekierowanie poza listę hostów
            P.TylkoTeHosty().redirect_request(None, None, 302, '', {}, 'https://example.com/b.png')
        self.assertNotIn('#', P.sprawdz_adres(self.URL))

    def test_zapis_bez_nadpisywania_i_typ(self):
        kat = Path(tempfile.mkdtemp())
        wolania = []

        def otworz(url, timeout):
            wolania.append(url)
            return self.Odp(b'\x89PNG\r\n\x1a\n' + b'0' * 10, 'image/png')
        p, juz = P.pobierz(self.URL, '2026-12-05', 'abc-1', kat, otworz)
        self.assertEqual((p.name, juz, len(wolania)), ('2026-12-05-abc-1.png', False, 1))
        p2, juz = P.pobierz(self.URL, '2026-12-05', 'abc-1', kat, otworz)
        self.assertEqual((p2, juz, len(wolania)), (p, True, 1))
        with self.assertRaisesRegex(P.BladParagonu, 'nie zdjęcie'):
            P.pobierz(self.URL, '2026-12-05', 'abc-2', kat, lambda u, timeout: self.Odp(b'<html>', 'text/html'))
        with self.assertRaises(P.BladParagonu):
            P.pobierz(self.URL, '2026-12-05', '../x', kat, otworz)
        P.MAX_BAJTOW, stary = 8, P.MAX_BAJTOW
        try:
            with self.assertRaisesRegex(P.BladParagonu, 'większy'):
                P.pobierz(self.URL, '2026-12-05', 'abc-3', kat, otworz)
        finally:
            P.MAX_BAJTOW = stary
        self.assertEqual(sorted(x.name for x in kat.iterdir()), ['2026-12-05-abc-1.png'])

    def test_bledy_bez_adresu_i_typ_po_naglowku(self):
        import http.client
        kat = Path(tempfile.mkdtemp())

        def rzuc(wyj):
            def f(url, timeout):
                raise wyj
            return f
        for wyj in (http.client.IncompleteRead(b'x'), http.client.InvalidURL('zly ' + self.URL), ValueError(self.URL)):
            with self.assertRaises(P.BladParagonu) as e:
                P.pobierz(self.URL, '2026-12-05', 'e1', kat, rzuc(wyj))
            self.assertNotIn('amazonaws', str(e.exception))
        jpg = b'\xff\xd8\xff\xe0' + b'0' * 10
        p, _ = P.pobierz(self.URL, '2026-12-05', 'o1', kat, lambda u, timeout: self.Odp(jpg, 'application/octet-stream'))
        self.assertEqual(p.name, '2026-12-05-o1.jpg')
        heif = b'\x00\x00\x00\x18ftypmif1' + b'0' * 10
        stary = P.shutil.which
        P.shutil.which = lambda n: None  # brak sips -> błąd zamiast ścieżki pliku, którego Read nie przeczyta
        try:
            with self.assertRaisesRegex(P.BladParagonu, 'HEIC'):
                P.pobierz(self.URL, '2026-12-05', 'h1', kat, lambda u, timeout: self.Odp(heif, 'image/heif'))
        finally:
            P.shutil.which = stary
        self.assertTrue((kat / '2026-12-05-h1.heic').exists())


class Przeplyw30(unittest.TestCase):
    """paragon.py, wpis.py i importuj.py jako procesy na zmyślonych danych w katalogu tymczasowym."""
    uruchom, importuj = TB.Przeplyw.uruchom, TB.Przeplyw.importuj

    def setUp(self):
        self.dane = Path(tempfile.mkdtemp())
        self.ustaw()
        (self.dane / 'kategorie.json').write_text(json.dumps({'Wydatek': {'Zakupy': ['Regularne', 'Chemia'], 'Inne wydatki': []},
                                                             'Inwestycja': {'Dom': []}}))
        (self.dane / 'reguly.json').write_text(json.dumps({'reguly': [], 'skroty': SKROTY}))
        (self.dane / 'ark.json').write_text(json.dumps({'values': [['Data']]}))

    def ustaw(self, **dod):
        (self.dane / 'ustawienia.json').write_text(json.dumps(dict(UST, **dod)))

    def paragon(self, *pozycje, id_='p1', data='2026-12-05', platnosc='z, a', suma='33,50', kod=0, dod=()):
        r = subprocess.run([sys.executable, str(NARZ / 'paragon.py'), 'rozpisz', '--id', id_, '--data', data,
                            '--platnosc', platnosc, '--sklep', 'Sklep A', '--suma', suma, *dod, *pozycje],
                           env=dict(os.environ, BUDZET_DANE=str(self.dane)), capture_output=True, text=True)
        self.assertEqual(r.returncode, kod, r.stdout + r.stderr)
        return r.stdout

    def wpisy(self, mies='2026-12'):
        p = self.dane / 'listy' / f'{mies}-wpisy.jsonl'
        return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines()] if p.exists() else []

    POZ = ('10,00, zak, chleb', '20.00, chem, płyn', '5, zak, ser?', '-3,00, rabat', '1,50, kaucja')

    def test_zapis_grupy_id_i_pola(self):
        out = self.paragon(*self.POZ)
        self.assertIn('suma części = suma paragonu 33.50', out)
        ws = self.wpisy()
        self.assertEqual([(w['id'], w['grupa'], w['kwota'], w['konto'], w['osoba'], w['kat'], w['pod']) for w in ws],
                         [('wp1-1', 'wp1', -14.36, 'K-bank', 'Osoba A', 'Zakupy', 'Regularne'),
                          ('wp1-2', 'wp1', -19.14, 'K-bank', 'Osoba A', 'Zakupy', 'Chemia')])
        self.assertEqual(ws[0]['paragon'], dict(sklep='Sklep A', suma=33.5, czesci=2, zdjecie=''))
        self.assertEqual(ws[0]['opis'], 'Sklep A: chleb, ser?')

    def test_proba_niezgodnosc_i_brak_platnosci_nic_nie_zapisuja(self):
        self.assertIn('próba', self.paragon(*self.POZ, dod=('--proba',)))
        self.assertIn('różnica', self.paragon('10, zak', '20, chem', kod=1))
        self.assertIn('kto i czym', self.paragon(*self.POZ, platnosc='', kod=1))
        self.assertEqual(self.wpisy(), [])

    def test_poprawka_i_usuniecie_calej_grupy(self):
        self.paragon(*self.POZ)
        p = self.dane / 'listy' / '2026-12-wpisy.jsonl'
        ws = self.wpisy()
        for w in ws:
            w['arkusz'] = {'wiersz': 9, 'skrot': 'x', 'czas': '2026-12-05 10:00'}
        p.write_text(''.join(json.dumps(w) + '\n' for w in ws), encoding='utf-8')
        self.assertIn('zastąpiono', self.paragon('33,50, zak, wszystko'))  # druga kategoria znika z odczytu
        ws = {w['id']: w for w in self.wpisy()}
        self.assertEqual((ws['wp1-1']['kwota'], ws['wp1-1']['arkusz']['wiersz'], bool(ws['wp1-2'].get('usuniety'))),
                         (-33.5, 9, True))
        self.assertIn('usunięto (1)', self.uruchom('wpis.py', 'usun', '2026-12', 'p1'))  # ID wpisu = cały paragon
        self.assertTrue(all(w.get('usuniety') for w in self.wpisy()))
        self.paragon(*self.POZ, id_='p2')
        self.assertIn('usunięto (2)', self.uruchom('wpis.py', 'usun', '2026-12', 'wp2-2'))  # ID części = cały paragon
        self.assertEqual([w['id'] for w in self.wpisy() if 'wp2' in w['id']], [])

    def test_rozliczony_paragon_nie_jest_zastepowany(self):
        """Recenzja 1a: przypięty do wyciągu (zamknięcie sąsiedniego miesiąca) albo z zamkniętego miesiąca – odmowa."""
        self.paragon(*self.POZ, data='2026-12-30')
        (self.dane / 'miesiace').mkdir()
        zapis = self.dane / 'miesiace' / '2027-01-zapis.json'
        zapis.write_text(json.dumps({'przypiecia': [{'id_wyciagu': 'b1', 'wiersze': [{'id': 'wp1-1', 'wiersz': 2, 'kwota': None}]}]}))
        self.assertIn('rozliczony', self.paragon('33,50, zak', data='2026-12-30', kod=1))
        self.assertEqual(len(self.wpisy()), 2)
        zapis.unlink()
        (self.dane / 'miesiace' / '2026-12-zapis.json').write_text('{}')
        self.assertIn('zamknięty', self.paragon('33,50, zak', data='2026-12-30', kod=1))
        self.assertIn('próba', self.paragon('33,50, zak', data='2026-12-30', dod=('--proba',)))

    def test_ten_sam_id_wpisu_i_paragonu_bez_dubla(self):
        """Recenzja 2: zwykły wpis z ID bloku zastąpiony paragonem; wpis.py dodaj odmawia ID paragonu; usun zabiera wszystko."""
        self.uruchom('wpis.py', 'dodaj', '33,50, z, zak', '--data', '2026-12-05', '--id', 'p1')
        self.paragon(*self.POZ)
        self.assertEqual(sorted(w['id'] for w in self.wpisy()), ['wp1-1', 'wp1-2'])
        r = subprocess.run([sys.executable, str(NARZ / 'wpis.py'), 'dodaj', '33,50, z, zak', '--data', '2026-12-05', '--id', 'p1'],
                           env=dict(os.environ, BUDZET_DANE=str(self.dane)), capture_output=True, text=True)
        self.assertEqual((r.returncode, 'paragon.py rozpisz' in r.stdout), (1, True))
        p = self.dane / 'listy' / '2026-12-wpisy.jsonl'  # stan po dawnej wersji: wpis i paragon z tym samym ID obok siebie
        p.write_text(p.read_text(encoding='utf-8') + json.dumps(dict(self.wpisy()[0], id='wp1', grupa=None)) + '\n',
                     encoding='utf-8')
        self.assertIn('usunięto (3)', self.uruchom('wpis.py', 'usun', '2026-12', 'p1'))
        self.assertEqual(self.wpisy(), [])

    def test_ten_sam_paragon_drugi_raz_ostrzega(self):
        """Recenzja 8: inna grupa z tą samą datą, sumą i sklepem – kod 1, chyba że --mimo-to."""
        self.paragon(*self.POZ, id_='c20261205-3350')
        self.assertIn('możliwy dubel', self.paragon(*self.POZ, id_='inny', kod=1))
        self.paragon(*self.POZ, id_='inny', dod=('--mimo-to',))
        self.paragon(*self.POZ, id_='c20261205-3350', dod=('--mimo-to',))  # ten sam --id – zastąpienie (drugi już świadomie)
        self.assertEqual(len(self.wpisy()), 4)

    def test_paragon_mieszany_z_budowa(self):
        out = self.paragon('20, zak', '13,50, dom, taśma', dod=('--budowa', 'b123'))
        ws = self.wpisy()
        self.assertEqual([(w['kat'], w['budowa']) for w in ws], [('Zakupy', ''), ('Dom', 'b123')])
        self.assertIn('[budowa]', out)
        self.assertTrue(wspolne.notatka_wpisu(ws[1]).endswith('w kosztorysie budowy (💸)'))
        self.assertIn('żadna część', self.paragon('33,50, zak', dod=('--budowa', 'b9'), id_='p3', kod=1))
        self.assertIn('bez --budowa', self.paragon('20, zak', '13,50, dom', id_='p4', data='2026-12-06'))
        m = self.importuj(mies='2026-12')  # karta bez pary w wyciągu: decyzja bez pytania „nie ma w kosztorysie”
        d = [d for d in m['decyzje'] if d['id'] == 'wp1-2'][0]
        self.assertEqual(d['budowa'], 'z wpisu – w kosztorysie budowy (💸)')
        self.paragon('20, zak', '13,50, dom', dod=('--budowa', 'b5'), id_='p5', platnosc='g', data='2026-12-07')
        m = self.importuj(mies='2026-12')  # gotówka: wiersz z uwagą „w kosztorysie”
        self.assertIn('w kosztorysie budowy (💸)', [w for w in m['wiersze'] if w['kat'] == 'Dom' and w['zrodla'] == ['wp5-2']][0]['uwaga'])

    def lista(self, tekst):
        self.ustaw(lista_domyslne_konto='K-praca')
        (self.dane / 'lista.txt').write_text(tekst, encoding='utf-8')
        return self.importuj('--lista', 'lista.txt', mies='2026-12')

    def test_lista_drugiej_osoby_suma_czesc_bliska(self):
        self.paragon(*self.POZ, platnosc='pra, o')
        m = self.lista('33.50 zak\n')  # = suma paragonu na tym samym koncie -> pominięta
        self.assertTrue(any('już z paragonu' in p['powod'] for p in m['pominiete']))
        self.assertEqual(sorted(w['kwota'] for w in m['wiersze']), [14.36, 19.14])
        m = self.lista('14.36 zak\n')  # = jedna część -> wchodzi normalnie
        self.assertFalse(any('już z' in p['powod'] for p in m['pominiete']))
        self.assertEqual(sorted(w['kwota'] for w in m['wiersze']), [14.36, 14.36, 19.14])
        m = self.lista('36.00 zak\n')  # bliska sumie (do progu), inna -> strona decyzji
        d = [d for d in m['decyzje'] if 'duplikat paragonu' in d['uwaga']]
        self.assertEqual((len(d), len(m['wiersze'])), (1, 2))
        m = self.lista('40.00 zak\n')  # dalej niż próg -> zwykła pozycja
        self.assertEqual(len(m['wiersze']), 3)

    def zen(self, *tr):
        linie = ''.join(f'"{d},Card payment,""{o}"",{k},PLN,{k},PLN,1,,,,900.00"\n' for d, o, k in tr)
        (self.dane / 'zen.csv').write_text('Naglowek\nTransactions:\n"Date,Transaction type,Description,Settlement amount"\n' + linie)

    def test_karta_grupa_bez_wierszy_zapas_z_wyciagu(self):
        """Listopad (przed ARKUSZ_OD): części nie ma w arkuszu – n wierszy z ID wyciągu i części, grosze na największej."""
        self.paragon(*self.POZ, data='2026-11-18')
        self.zen(('19 Nov 2026', 'SKLEP A', '-33.80'))
        m = self.importuj('--zen', 'zen.csv', mies='2026-11')
        self.assertEqual(sorted((a['ids_w'][0], a['kwota_ark']) for a in m['auto'] if a.get('ids_w')),
                         [('wp1-1', 14.36), ('wp1-2', 19.44)])
        self.uruchom('przenies.py', '--miesiac', '2026-11')
        z = json.loads((self.dane / 'miesiace' / '2026-11-zapis.json').read_text(encoding='utf-8'))
        o = sorted(w[14] for w in z['wiersze'] if 'wp1' in w[14])
        self.assertEqual(len(o), 2)
        self.assertTrue(all(x.startswith('b') and x.count(',') == 1 for x in o), o)
        self.assertEqual(sorted(x.split(',')[1] for x in o), ['wp1-1', 'wp1-2'])

    def test_karta_grupa_i_reczny_wiersz_bez_dubla(self):
        """Recenzja POM-29, 1 – dla grup: ręczny wiersz = suma paragonu zajmuje płatność 1:1, części bez wierszy są „już w arkuszu”."""
        self.paragon(*self.POZ, data='2026-11-18')
        self.zen(('19 Nov 2026', 'SKLEP A', '-33.50'))
        (self.dane / 'ark.json').write_text(json.dumps({'values': [['Data'], wiersz_ark('2026-11-19', 33.5, 'K-bank', '')]}))
        m = self.importuj('--zen', 'zen.csv', mies='2026-11')
        self.assertEqual((m['wiersze'], m['decyzje'], [j['sposob'] for j in m['juz']]), ([], [], ['1:1']))
        self.assertEqual(sorted(p['id'] for p in m['pominiete'] if 'już w arkuszu' in p['powod']), ['wp1-1', 'wp1-2'])

    def test_inny_wpis_nie_jest_pokryty_wierszem_wpisu(self):
        """Recenzja 10: płatność przypięta do wiersza innego wpisu nie robi z wpisu bez wiersza „już w arkuszu”."""
        TB.PrzeplywArkusz.wpisz(self, '2026-12', TB.PrzeplywArkusz.karta('wa', '2026-12-10', 50.0),
                                TB.PrzeplywArkusz.karta('wb', '2026-12-10', 50.3))
        self.zen(('10 Dec 2026', 'SKLEP', '-50.00'), ('31 Dec 2026', 'X', '-1.00'))
        (self.dane / 'ark.json').write_text(json.dumps({'values': [['Data'], wiersz_ark('2026-12-10', 50.0, 'K-bank', 'wa')]}))
        m = self.importuj('--zen', 'zen.csv', mies='2026-12')
        self.assertIn('wb', [d['id'] for d in m['decyzje']])
        self.assertFalse(any(p['id'] == 'wb' for p in m['pominiete']))

    def test_niepelny_wiersz_z_id_nie_daje_drugiego(self):
        """Recenzja 7: wiersz po przerwanym dopisz (samo ID w O) – import nie dopisuje drugiego z tym samym ID."""
        self.uruchom('wpis.py', 'dodaj', '20, g, zak', '--data', '2026-12-05', '--id', 'n1')
        (self.dane / 'ark.json').write_text(json.dumps({'values': [['Data'], [''] * 14 + ['wn1']]}))
        m = self.importuj(mies='2026-12')
        self.assertEqual(([w['zrodla'] for w in m['wiersze']], [j['id'] for j in m['juz']]), ([], ['wn1']))

    def test_przenies_odrzucony_zapasowy_daje_przypiecie(self):
        """Recenzja 9: wiersz zapasowy [ID wyciągu, ID wpisu] odrzucony (wpis już w O) – ID wyciągu i kwota na wiersz z sync."""
        self.paragon(*self.POZ, data='2026-11-18')
        self.zen(('19 Nov 2026', 'SKLEP A', '-33.80'))
        self.importuj('--zen', 'zen.csv', mies='2026-11')
        swiezy = {'values': [['Data'], wiersz_ark('2026-11-18', 14.36, 'K-bank', 'wp1-1'),
                             wiersz_ark('2026-11-18', 19.14, 'K-bank', 'wp1-2', kat='Zakupy', pod='Chemia')]}
        (self.dane / 'swiezy.json').write_text(json.dumps(swiezy))
        self.uruchom('przenies.py', '--miesiac', '2026-11', '--arkusz', 'swiezy.json')
        z = json.loads((self.dane / 'miesiace' / '2026-11-zapis.json').read_text(encoding='utf-8'))
        self.assertEqual(z['wiersze'], [])
        p = [p for p in z['przypiecia'] if p['id_wyciagu'].startswith('b')]
        self.assertEqual((len(p), sorted((x['id'], x['wiersz'], x['kwota']) for x in p[0]['wiersze'])),
                         (1, [('wp1-1', 2, None), ('wp1-2', 3, 19.44)]))

    def test_karta_grupa_przelom_miesiaca_przypiecie(self):
        self.paragon(*self.POZ, data='2026-12-30')
        self.zen(('2 Jan 2027', 'SKLEP A', '-33.49'))
        (self.dane / 'ark.json').write_text(json.dumps({'values': [['Data'], wiersz_ark('2026-12-30', 14.36, 'K-bank', 'wp1-1'),
                                                                   wiersz_ark('2026-12-30', 19.14, 'K-bank', 'wp1-2')]}))
        m = self.importuj('--zen', 'zen.csv', mies='2027-01')
        self.assertEqual(m['przypiecia'][0]['wiersze'], [{'id': 'wp1-1', 'wiersz': 2, 'kwota': None},
                                                        {'id': 'wp1-2', 'wiersz': 3, 'kwota': 19.13}])
        self.assertEqual(m['auto'], [])


class SynchronizacjaGrupy(unittest.TestCase):
    def setUp(self):
        self.stare = wspolne.DANE
        wspolne.DANE = Path(tempfile.mkdtemp())
        wspolne.U.update(UST)
        self.atrapa = Atrapa()
        AB.wyslij = self.atrapa

    def tearDown(self):
        wspolne.DANE = self.stare
        P.wczytaj = wspolne.wczytaj

    def rozpisz(self, *poz):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(P.main(['rozpisz', '--id', 'p1', '--data', '2026-12-05', '--platnosc', 'z', '--sklep', 'Sklep A',
                                     '--suma', '33.50', *poz]), 0)

    def test_grupa_jednym_wywolaniem_potem_poprawka(self):
        P.wczytaj = lambda nazwa, d=None: {'skroty': SKROTY}
        self.rozpisz('10, zak', '20, chem', '3.50, zak')
        licz, bledy = AB.sync(K, False)
        self.assertEqual((licz['dopisane'], bledy, self.atrapa.wywolania.count('dopisz')), (2, [], 1))
        self.rozpisz('33.50, zak')
        licz, bledy = AB.sync(K, False)
        self.assertEqual((licz['poprawione'], licz['usuniete'], bledy), (1, 1, []))
        self.assertEqual([(r['o'], r['kwota']) for r in self.atrapa.w], [(['wp1-1'], 33.5)])
        self.assertEqual([w['id'] for w in wspolne.czytaj_wpisy('2026-12', z_usunietymi=True)], ['wp1-1'])

    def test_bezpiecznik_czesc_przypieta_do_wyciagu(self):
        """Recenzja 1b: grupa przypięta w arkuszu – nowa kwota części i usunięcie części to błąd sync, nie sukces."""
        P.wczytaj = lambda nazwa, d=None: {'skroty': SKROTY}
        self.rozpisz('10, zak', '20, chem', '3.50, zak')
        AB.sync(K, False)
        for r in self.atrapa.w:
            r['o'].append('b00000000aa')
        self.rozpisz('20, zak', '13.50, chem')  # inne kwoty
        licz, bledy = AB.sync(K, False)
        self.assertEqual(licz['bledy'], 2, bledy)
        self.assertTrue(all('przypięta do płatności' in b and 'wp1-' in b for b in bledy))
        self.rozpisz('33.50, zak')
        with redirect_stdout(io.StringIO()):
            licz, bledy = AB.sync(K, False)
        self.assertTrue(any('wp1-2' in b and 'zostaje' in b for b in bledy), bledy)

    def test_blokada_czeka_na_sync(self):
        """Recenzja 4: blokada zaloz nie wchodzi w trwający sync (flock) – po limicie błąd; potem zakłada i odnawia."""
        AB.CZEKAJ_NA_SYNC_S, stary = 1, AB.CZEKAJ_NA_SYNC_S
        try:
            with AB.trwa_sync():
                with self.assertRaisesRegex(AB.BladArkusza, 'sync trwa'):
                    AB.blokada('zaloz')
            self.assertIsNone(AB.blokada_zamkniecia())
            AB.blokada('zaloz')
            self.assertIsNotNone(AB.blokada_zamkniecia())
        finally:
            AB.CZEKAJ_NA_SYNC_S = stary
            AB.blokada('zdejmij')


if __name__ == '__main__':
    unittest.main()
