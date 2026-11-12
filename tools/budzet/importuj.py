#!/usr/bin/env python3
"""Import miesiąca do budżetu domowego: wyciągi (mBank, ZEN), zamówienia Allegro, listy wydatków (druga osoba, gotówka)
-> propozycja wierszy i decyzje dla strony. Nic nie zapisuje do arkusza. Procedura: plugins/ja/skills/budzet.

    python3 tools/budzet/importuj.py --miesiac RRRR-MM --arkusz miesiace/transakcje-<data>.json \
        [--zen wyciagi/zen.csv] [--mbank wyciagi/mbank.csv] [--allegro listy/allegro-<data>.json] \
        [--lista listy/RRRR-MM-lista.txt] [--gotowka listy/RRRR-MM-gotowka.txt]

Ścieżki względne liczą się od folderu danych (wspolne.DANE). Wynik: miesiace/RRRR-MM.json – wiersze (pewne, po scaleniu),
auto, decyzje (strona), pominiete, juz (z numerem wiersza), braki, salda.
"""
import argparse, hashlib, json, re, statistics, sys
from calendar import monthrange
from collections import Counter, defaultdict
from datetime import date, datetime
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import DANE, DRZEWO, U, arkusz, kw, norm, opcja, rozbij, wczytaj, wyciagi, zapisz  # noqa: E402

ap = argparse.ArgumentParser()
for a in ('miesiac', 'arkusz', 'zen', 'mbank', 'allegro', 'lista', 'gotowka'):
    ap.add_argument('--' + a)
A = ap.parse_args()
sciezka = lambda p: p and str(p if Path(p).is_absolute() else DANE / p)
MIES = A.miesiac
R, M = map(int, MIES.split('-'))
KONIEC = date(R, M, monthrange(R, M)[1])

ark = arkusz(sciezka(A.arkusz))
bank = wyciagi(sciezka(A.zen), sciezka(A.mbank))
KONTA_A = (U.get('konto_zen'), U.get('konto_mbank'))


def wiersz_info(r):
    return dict(wiersz=r['wiersz'], data=r['data'].isoformat() if r['data'] else '', kwota=r['kwota'], konto=r['konto'],
                kategoria=f"{r['kat']} › {r['pod']}" if r['pod'] else r['kat'], typ=r['typ'])


# ---------- dopasowanie do arkusza (wszystkie miesiące): ID importu, 1:1, potem suma 2–4 z ±7 dni
def znak(r):
    return {'Przychód': 1, 'Przelew': 0}.get(r['typ'], -1)


def pasuje(r, t):
    z = znak(r)
    return z == 0 or (z > 0) == (t['kwota'] > 0)


para = {}
po_id = {i: r for r in ark for i in r['ids']}
for t in bank:
    if t['id'] in po_id:
        para[t['id']] = (po_id[t['id']], 'zaimportowane wcześniej')
        po_id[t['id']]['uzyty'] = True
nasze = [r for r in ark if r['konto'] in KONTA_A and r['kwota'] is not None and not r.get('uzyty')]
pozbank = defaultdict(list)
for t in bank:
    if t['id'] not in para:
        pozbank[(t['konto'], t['mies'])].append(t)
for r in nasze:
    k = [t for t in pozbank[(r['konto'], r['mies'])] if t['id'] not in para and abs(t['kwota']) == r['kwota'] and pasuje(r, t)]
    if k:
        t = min(k, key=lambda t: abs((t['data'] - r['data']).days) if r['data'] else 0)
        para[t['id']] = (r, '1:1')
        r['uzyty'] = True
for r in nasze:
    if r.get('uzyty') or r['typ'] == 'Przelew' or not r['data']:
        continue
    k = sorted([t for t in pozbank[(r['konto'], r['mies'])] if t['id'] not in para and pasuje(r, t)
                and abs((t['data'] - r['data']).days) <= 7 and abs(t['kwota']) < r['kwota']],
               key=lambda t: abs((t['data'] - r['data']).days))[:16]
    for n in (2, 3, 4):
        c = next((c for c in combinations(k, n) if abs(sum(abs(t['kwota']) for t in c) - r['kwota']) < 0.005), None)
        if c:
            for t in c:
                para[t['id']] = (r, f'w sumie {n} płatności')
            r['uzyty'] = True
            break

ostatnia = {}
for r in nasze:
    if r['mies'] == MIES and r['data']:
        ostatnia[r['konto']] = max(ostatnia.get(r['konto'], r['data']), r['data'])


def kandydaci(t, n=3):
    """Ręczne sumy w arkuszu, które mogą zawierać tę transakcję (to samo konto i miesiąc, ±3 dni, kwota ≥, niewykorzystane)."""
    k = [r for r in nasze if r['konto'] == t['konto'] and r['data'] and r['mies'] == t['mies'] and not r.get('uzyty')
         and abs((r['data'] - t['data']).days) <= 3 and r['kwota'] >= abs(t['kwota']) - 0.005 and pasuje(r, t) and r['typ'] != 'Przelew']
    k.sort(key=lambda r: (abs((r['data'] - t['data']).days), r['kwota']))
    return [wiersz_info(r) for r in k[:n]]


# ---------- kosztorys budowy (żeby zakupy na budowę nie dublowały się z tym, co inwestor wpisuje od razu)
koszt = []
kj = (DANE.parent.parent / U['kosztorys_json']) if U.get('kosztorys_json') else None  # ścieżka względem folderu budowy
if kj and kj.exists():
    w = json.loads(kj.read_text(encoding='utf-8'))['arkusze'].get('Wydatki', [])
    h = next((i for i, r in enumerate(w) if r[:3] == ['Data', 'Status', 'Kwota (zł)']), None)
    for r in (w[h + 1:] if h is not None else []):
        try:
            koszt.append((kw(r[2]), r[0], r[4] if len(r) > 4 else ''))
        except (ValueError, IndexError):
            pass


def w_kosztorysie(kwota, data):
    def blisko(d):
        try:
            return abs((date.fromisoformat(str(d)[:10]) - date.fromisoformat(data)).days) <= 40
        except ValueError:
            return False
    k = [x for x in koszt if x[0] is not None and abs(abs(kwota) - x[0]) < 0.005 and blisko(x[1])]
    return f'w kosztorysie budowy: {k[0][1]} {k[0][2]}'.strip() if k else 'nie ma w kosztorysie budowy – dodać?'


# ---------- reguły
REG = wczytaj('reguly.json')
REGULY = REG['reguly']
SKROTY = {k: tuple(v) for k, v in REG.get('skroty', {}).items()}
for g in REGULY:
    g['nk'] = norm(g['klucz'])


def regula(t):
    o = t['no']
    k = [g for g in REGULY if g['kierunek'] == t['kier'] and g['nk'] in o]
    if 'CASHBACK' in o:
        k = [g for g in k if g['nk'] == 'CASHBACK'] or k
    return max(k, key=lambda g: len(g['nk'])) if k else None


def kwota_w_arkuszu(kwota, typ):
    if typ == 'Przelew':
        return abs(kwota)
    return round(kwota if typ == 'Przychód' else -kwota, 2)


INNE = opcja('Wydatek', 'Inne wydatki', 'Inne wydatki: inne')
auto, decyzje, pominiete, juz, braki = [], [], [], [], []
teraz = [t for t in bank if t['mies'] == MIES]
if not teraz:
    braki.append('wyciągi bankowe za ten miesiąc (mBank, ZEN)')


def baza(t):
    return dict(id=t['id'], data=t['data'].isoformat(), konto=t['konto'], osoba=t['osoba'], kwota=t['kwota'], opis=t['opis'])


def decyzja(b, **kw_):
    d = dict(b, zrodlo='wyciąg', pewnosc='Pytaj', regula='', propozycja=None, opcje=[], uwaga='', moze_juz=False, kandydaci=[])
    d.update(kw_)
    if d['propozycja'] and d['propozycja']['kat'] == 'Dom' or any(o['kat'] == 'Dom' for o in d['opcje'][:1]):
        d['budowa'] = w_kosztorysie(d['kwota'], d['data'])
    decyzje.append(d)


# --- pary pomijane razem (np. wydatek oddany tego samego dnia), przelewy partnera, pensja, zapowiedziane zwroty
for p in U.get('pary_pomijane', []):
    for t in teraz:
        if norm(p['wydatek']) in t['no'] and abs(t['kwota']) == p['kwota'] and t['id'] not in para:
            z = next((u for u in teraz if u['id'] not in para and norm(p['wplyw']) in u['no'] and u['kwota'] == p['kwota']
                      and u['data'] == t['data'] and not u.get('para')), None)
            if z:
                t['para'] = z['para'] = p['powod']
pp = U.get('przelew_partnera')
if pp:
    o2a_ark = round(sum(r['kwota'] for r in ark if r['mies'] == MIES and r['typ'] == 'Przelew' and r['kat'] == pp['kategoria']
                        and not r.get('uzyty')), 2)
    o2a_bank = [t for t in teraz if t['id'] not in para and norm(pp['klucz']) in t['no'] and t['kwota'] > 0]
    if o2a_bank and round(sum(t['kwota'] for t in o2a_bank), 2) <= o2a_ark + 0.005:
        for t in o2a_bank:
            t['para'] = f"przelew {pp['kategoria']} – suma miesiąca jest już w arkuszu"
pensja = [r for r in ark if r['mies'] == MIES and U.get('pensja') and r['kat'] == U['pensja']['kategoria']]
oczek = wczytaj('oczekujace.json', [])
for t in teraz:
    for o in oczek:
        if o['miesiac'] == MIES and norm(o['klucz']) in t['no'] and t['kier'] == o.get('kierunek', 'wpływ') and not o.get('uzyte'):
            t['para'] = o['powod']
            o['uzyte'] = True

# --- Allegro: zamówienia z listy są źródłem wydatków; płatności w banku tylko je opłacają
AL = U.get('allegro', {})
PLAT = tuple(norm(x) for x in AL.get('platnosci', []))
zam = []
if A.allegro:
    for z in json.loads(Path(sciezka(A.allegro)).read_text(encoding='utf-8'))['zamowienia']:
        if z['data'][:7] == MIES:
            z['id'] = 'a' + hashlib.sha1(f"{z['data']}|{z['sprzedawca']}|{z['suma']}|{'|'.join(z['produkty'])}".encode()).hexdigest()[:10]
            zam.append(z)
allegro_bank = [t for t in teraz if PLAT and any(k in t['no'] for k in PLAT) and 'CASHBACK' not in t['no']]
KARTA, PAY = norm(AL.get('karta_podarunkowa', '-')), norm(AL.get('pay', '-'))
if allegro_bank and not A.allegro:
    braki.append('lista zakupów z Allegro (Moje zakupy → zaznacz i skopiuj tekst)')
if A.allegro:
    otwarte = [z for z in zam if not z.get('zwrocony') and not z['pay']]
    for t in sorted([t for t in allegro_bank if t['kier'] == 'wypływ' and PAY not in t['no'] and KARTA not in t['no']],
                    key=lambda t: t['data']):
        k = [z for z in otwarte if not z.get('oplacone') and -1 <= (t['data'] - date.fromisoformat(z['data'])).days <= 5]
        c = next((c for n in (1, 2, 3, 4) for c in combinations(k, n) if abs(sum(z['suma'] for z in c) + t['kwota']) < 0.005), None)
        if c:
            for z in c:
                z['oplacone'] = t['id']
            t['allegro'] = 'zapłata za zamówienia: ' + ', '.join(f"{z['sprzedawca']} {z['suma']:.2f}" for z in c)
    for z in zam:
        if z.get('oplacone') and z['oplacone'] in para:
            z['juz'] = para[z['oplacone']]

for t in sorted(teraz, key=lambda t: (t['data'], t['konto'])):
    b = baza(t)
    if t['id'] in para:
        r, sp = para[t['id']]
        juz.append(dict(b, sposob=sp, w=wiersz_info(r)))
        continue
    if t.get('para'):
        pominiete.append(dict(b, powod=t['para']))
        continue
    g = regula(t)
    if g and g['pewnosc'] == 'Pomiń':
        pominiete.append(dict(b, powod=f"reguła {g['klucz']}: {g['uwaga']}"))
        continue
    if g and U.get('pensja') and g['klucz'] == U['pensja']['klucz'] and pensja:
        juz.append(dict(b, sposob='pensja brutto (przelew + pakiety)', w=wiersz_info(pensja[0])))
        continue
    if A.allegro and t in allegro_bank:
        if KARTA in t['no']:
            pominiete.append(dict(b, powod='karta podarunkowa Allegro – wydatki liczą się z listy zamówień'))
            continue
        if PAY in t['no']:
            if MIES < AL.get('pay_pomijaj_od', '0000-00'):
                decyzja(b, regula='ALLEGROPAY', opcje=[INNE], uwaga='spłata Allegro Pay za zakupy sprzed listy zamówień – '
                        'tych zakupów nie ma w arkuszu; wybierz kategorię albo Pomiń')
            else:
                pominiete.append(dict(b, powod='spłata Allegro Pay – zakupy są już z listy zamówień'))
            continue
        if t.get('allegro'):
            pominiete.append(dict(b, powod=t['allegro']))
            continue
        if t['kier'] == 'wypływ':
            decyzja(b, regula='ALLEGRO', opcje=[INNE], uwaga='płatność Allegro bez zamówienia na liście tego miesiąca '
                    '(zamówienie z innego miesiąca albo innego konta?) – wybierz kategorię albo Pomiń')
            continue
        zw = next((z for z in zam if z.get('zwrocony') and abs(z['suma'] - t['kwota']) < 0.005), None)
        if zw:
            pominiete.append(dict(b, powod=f"zwrot zamówienia {zw['sprzedawca']} – zwrócone zamówienia nie są liczone"))
            continue
    # zwrot: wpływ od sprzedawcy, u którego był wcześniej zakup -> pomniejsz ten zakup
    if t['kier'] == 'wpływ' and not (g and (g['typ'] == 'Przelew' or (g['typ'] == 'Przychód' and g['kat'] != 'Zwroty'))) \
            and 'CASHBACK' not in t['no']:
        slowo = next((w for w in re.split(r'[\s,*]+', t['no']) if len(w) >= 4 and not w.isdigit()
                      and w not in ('PAYPRO', 'POZNAN', 'WARSZAWA')), '')
        zakupy = [u for u in bank if u['kier'] == 'wypływ' and slowo and slowo in u['no'] and 'CASHBACK' not in u['no']
                  and not u.get('allegro') and 0 <= (t['data'] - u['data']).days <= 120 and abs(u['kwota']) >= t['kwota'] - 0.005]
        if zakupy:
            cele = []
            for u in sorted(zakupy, key=lambda u: (t['data'] - u['data']).days)[:3]:
                c = dict(id=u['id'], data=u['data'].isoformat(), kwota=u['kwota'], opis=u['opis'])
                if u['id'] in para:
                    c['wiersz'] = wiersz_info(para[u['id']][0])
                elif u['mies'] != MIES:
                    c['kandydaci'] = kandydaci(u, 2)
                cele.append(c)
            decyzja(b, zrodlo='zwrot', regula=slowo, pewnosc='Zwykle', cele=cele,
                    uwaga='zwrot – pomniejszam zakup, którego dotyczy, zamiast osobnego wiersza')
            continue
    prop = opcja(g['typ'], g['kat'], g['pod']) if g and g['kat'] else None
    opcje = [rozbij(o) for o in (g['opcje'] if g else [])]
    if prop and prop['etykieta'] not in [o['etykieta'] for o in opcje]:
        opcje.insert(0, prop)
    moze_juz = (t['konto'] in ostatnia and t['data'] <= ostatnia[t['konto']]
                and not (g and g['klucz'] in ('CASHBACK', 'REWARD ZONE')))
    pew = (g['pewnosc'] or 'Zwykle') if g else 'Brak'
    if pew == 'Zawsze' and not moze_juz:
        auto.append(dict(b, typ=prop['typ'], kat=prop['kat'], pod=prop['pod'], regula=g['klucz'],
                         kwota_ark=kwota_w_arkuszu(t['kwota'], prop['typ'])))
        continue
    uw = [g['uwaga']] if g and g['uwaga'] else []
    if moze_juz:
        uw.insert(0, f"na tym koncie wpisane ręcznie do {ostatnia[t['konto']].strftime('%d.%m')} – sprawdź, czy nie siedzi w sumie")
    decyzja(b, pewnosc='Zwykle' if pew == 'Zawsze' else pew, regula=g['klucz'] if g else '',
            propozycja=prop if pew in ('Zwykle', 'Zawsze') else None, opcje=opcje, uwaga='; '.join(uw), moze_juz=moze_juz,
            kandydaci=kandydaci(t) if moze_juz else [])

# --- zamówienia Allegro jako wydatki
for z in zam:
    b = dict(id=z['id'], data=z['data'], konto=U.get('konto_zen'), osoba=U.get('osoba_wyciagi'), kwota=-z['suma'],
             opis=f"Allegro · {z['sprzedawca']}", produkty=z['produkty'], pay=z['pay'])
    if z.get('zwrocony'):
        pominiete.append(dict(b, powod='zamówienie zwrócone'))
        continue
    if z.get('juz'):
        r, sp = z['juz']
        juz.append(dict(b, sposob='zapłata kartą wpisana wcześniej ręcznie', w=wiersz_info(r)))
        continue
    prop = rozbij(z['prop']) if z.get('prop') else None
    decyzja(b, zrodlo='allegro', pewnosc='Zwykle' if prop else 'Pytaj', regula='ALLEGRO', propozycja=prop,
            opcje=([prop] if prop else []) + [rozbij(o) for o in z.get('opcje', [])],
            uwaga='Allegro Pay – spłata w kolejnym miesiącu zostanie pominięta' if z['pay'] else '')

# ---------- listy skrótów (druga osoba, gotówka)
KONTA = U.get('konta_list', {})
KONTA_ID = U.get('konta_list_id', {})
NIEZNANE = U.get('nieznane_skroty', {})
hist = defaultdict(list)
for r in ark:
    if r['kwota']:
        hist[(r['konto'], r['kat'], r['pod'])].append(r['kwota'])


def czytaj_liste(plik, domyslne_konto):
    konto, kid, n = domyslne_konto, domyslne_konto, 0
    for l in Path(plik).read_text(encoding='utf-8').splitlines():
        l = l.strip()
        if not l or l.startswith('#'):
            continue
        m = re.match(r'^(\+?)\s*([\d.,]+(?:\s*\+\s*[\d.,]+)*)\s*(.*)$', l)
        if not m:
            k = l.split()[0].lower()
            konto, kid = KONTA.get(k, l), KONTA_ID.get(k, KONTA.get(k, l))
            continue
        n += 1
        plus, liczby, kod = m.group(1), [kw(x) for x in re.split(r'\s*\+\s*', m.group(2))], m.group(3).strip().lower()
        suma = round(sum(liczby), 2)
        tid = 'l' + hashlib.sha1(f'{MIES}|{kid}|{n}|{l}'.encode()).hexdigest()[:10]
        b = dict(id=tid, data=f'{MIES}-01', konto=konto, osoba=U.get('osoba_listy'), kwota=suma if plus else -suma,
                 opis=l, skladniki=liczby if len(liczby) > 1 else None)
        if kod in SKROTY:
            typ, kat, pod = SKROTY[kod]
            prop = opcja(typ, kat, pod)
            h = hist.get((konto, prop['kat'], prop['pod']), [])
            if len(h) >= 3 and suma > 1000 and suma > 3 * statistics.median(h):
                decyzja(b, zrodlo='lista', pewnosc='Zwykle', regula=kod, propozycja=prop, opcje=[prop],
                        uwaga=f'nietypowo duża kwota (zwykle ok. {statistics.median(h):.0f} zł)')
            else:
                auto.append(dict(b, typ=prop['typ'], kat=prop['kat'], pod=prop['pod'], regula=kod, kwota_ark=suma,
                                 **({'budowa': w_kosztorysie(suma, b['data'])} if prop['kat'] == 'Dom' else {})))
        else:
            decyzja(b, zrodlo='lista', regula=kod, opcje=[rozbij(o) for o in NIEZNANE.get(kod, [])],
                    uwaga='nieznany skrót' if kod else 'wpływ bez opisu')


if A.lista:
    czytaj_liste(sciezka(A.lista), U.get('lista_domyslne_konto'))
else:
    braki.append(f"{U.get('etykieta_listy', 'lista wydatków drugiej osoby').lower()}")
if A.gotowka:
    czytaj_liste(sciezka(A.gotowka), U.get('gotowka_konto', 'Gotówka'))
else:
    braki.append(f"lista wydatków gotówkowych (Osoba = {U.get('osoba_listy')})")

# ---------- scalanie pewnych: ten sam dzień, konto i kategoria -> formuła; cashback – jeden wiersz na miesiąc
grupy = defaultdict(list)
for a in auto:
    grupy[('miesiąc' if a['regula'] == 'CASHBACK' else a['data'], a['konto'], a['typ'], a['kat'], a['pod'])].append(a)
wiersze = []
for (dzien, konto, typ, kat, pod), g in sorted(grupy.items(), key=lambda x: (max(a['data'] for a in x[1]), x[0][1] or '')):
    skl = [x for a in g for x in (a['skladniki'] if a.get('skladniki') else [a['kwota_ark']])]
    wiersze.append(dict(data=max(a['data'] for a in g), konto=konto, osoba=g[0]['osoba'], typ=typ, kat=kat, pod=pod,
                        kwota=round(sum(skl), 2), formula=('=' + '+'.join(f'{x:.2f}' for x in skl)).replace('+-', '-') if len(skl) > 1 else None,
                        opis=', '.join(sorted({a['regula'] for a in g})), zrodla=[a['id'] for a in g],
                        uwaga='; '.join(a['budowa'] for a in g if a.get('budowa'))))

# ---------- koniec miesiąca: przychód liczony z sald (zakładka Konta) i pozycji „do dodania” z zakładki roku
ps = U.get('przychod_z_sald')
if ps:
    kol = lambda n: chr(ord('A') + n)
    w = ps['wiersz_konta']
    wiersze.append(dict(data=KONIEC.isoformat(), konto='', osoba='', typ='Przychód', kat=ps['kategoria'], pod='', kwota=None,
                        formula=f"=(Konta!${kol(M + 1)}${w}-Konta!${kol(M)}${w})+XLOOKUP(\"{ps['etykieta_roku']}\", '{R}'!A:A, '{R}'!{kol(M + 2)}:{kol(M + 2)})",
                        opis='', zrodla=[], uwaga=f'liczy się z sald w zakładce Konta (kolumna „{M + 1}”)'))
    braki.append(f'salda kont drugiej osoby w zakładce Konta, kolumna „{M + 1}” (stan na 1. dzień następnego miesiąca) – '
                 f'z nich liczy się wiersz {ps["kategoria"]}')

# ---------- salda kont z wyciągów (do zakładki Konta, kolumna następnego miesiąca)
salda = {}
zen_m = [t for t in teraz if t['konto'] == U.get('konto_zen') and t.get('saldo') is not None]
if zen_m:
    salda[U['konto_zen']] = dict(saldo=zen_m[-1]['saldo'], skad='saldo PLN z ostatniej operacji miesiąca')
mb = [t for t in teraz if t['konto'] == U.get('konto_mbank')]
if mb:
    salda[U['konto_mbank']] = dict(zmiana=round(sum(t['kwota'] for t in mb), 2), skad='saldo z poprzedniej kolumny Konta + zmiana w miesiącu')

drzewo = [dict(typ=t, kat=k, pod=p) for t, ks in DRZEWO.items() for k, p in ks.items()]
zapisz(f'miesiace/{MIES}.json', dict(miesiac=MIES, wygenerowano=datetime.now().strftime('%Y-%m-%d %H:%M'), wiersze=wiersze,
                                     auto=auto, decyzje=decyzje, pominiete=pominiete, juz=juz, braki=braki, salda=salda,
                                     kategorie=drzewo, etykieta_listy=U.get('etykieta_listy', 'Lista wydatków'),
                                     ostatni_wiersz=max((r['wiersz'] for r in ark), default=1),
                                     ostatnia={k: v.isoformat() for k, v in ostatnia.items()}))
print(f"{MIES}: wyciąg {len(teraz)} (już w arkuszu {len(juz)}, pominięte {len(pominiete)}), Allegro {len(zam)} zamówień, "
      f"pewne {len(auto)} -> {len(wiersze)} wierszy, decyzje {len(decyzje)} {dict(Counter(d['zrodlo'] for d in decyzje))}; "
      f"braki: {len(braki)}")
