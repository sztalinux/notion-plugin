"""Wspólne funkcje importu budżetu domowego (procedura `budzet` w pluginie ja).

Kod jest ogólny; wszystko, co osobiste (konta, osoby, kategorie, reguły, wyciągi, decyzje), leży POZA repo w folderze
danych: `<hub>/.dom/budzet/` (hub = folder budowy, dwa poziomy nad repo; nadpisuje go zmienna BUDZET_DANE albo DOM_HUB).
Pliki danych: ustawienia.json, kategorie.json, reguly.json, oczekujace.json, wyciagi/, listy/, miesiace/.
"""
import csv, hashlib, json, os, re, unicodedata
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HUB = Path(os.environ.get('DOM_HUB', REPO.parent.parent)).expanduser()
DANE = Path(os.environ.get('BUDZET_DANE', HUB / '.dom' / 'budzet')).expanduser()


def wczytaj(nazwa, domyslnie=None):
    p = DANE / nazwa
    if not p.exists():
        if domyslnie is not None:
            return domyslnie
        raise SystemExit(f'brak pliku danych {p} – folder danych budżetu: {DANE}')
    return json.loads(p.read_text(encoding='utf-8'))


def zapisz(nazwa, obiekt):
    p = DANE / nazwa
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obiekt, ensure_ascii=False, indent=1), encoding='utf-8')


U = wczytaj('ustawienia.json', {})
DRZEWO = wczytaj('kategorie.json', {})
TYP_KATEGORII = {k: t for t, ks in DRZEWO.items() for k in ks}
ZMIANY_NAZW = U.get('zmiany_nazw', {})


def nazwa(s):
    """Stare nazwy kategorii (sprzed poprawek literówek) -> obecne."""
    return ZMIANY_NAZW.get(s, s) if s else s


def norm(s):
    s = s.replace('ł', 'l').replace('Ł', 'L')
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', s.upper()).strip()


def kw(s):
    s = str(s).replace('zł', '').replace('PLN', '').replace('\xa0', '').replace(' ', '').strip()
    if not s:
        return None
    s = s.replace(',', '') if (',' in s and '.' in s) else s.replace(',', '.')
    return round(float(s), 2)


def opcja(typ, kat, pod):
    kat, pod = nazwa(kat), nazwa(pod)
    return dict(typ=typ, kat=kat, pod=pod, etykieta=f'{kat} › {pod}' if pod else kat)


def rozbij(etykieta):
    """'Zakupy › Regularne' -> opcja z typem z drzewa kategorii."""
    kat, _, pod = [x.strip() for x in etykieta.partition('›')]
    kat = nazwa(kat)
    return opcja(TYP_KATEGORII.get(kat, ''), kat, pod)


def wyciagi(zen=None, mbank=None):
    """Transakcje ze wszystkich miesięcy w plikach; id stabilne między uruchomieniami (hash pól + numer powtórzenia).
    ZEN: CSV z liniami po „Transactions:” (każda linia to CSV w cudzysłowie, z saldem); mBank: CSV „;” od „#Data operacji”."""
    bank = []
    if zen and Path(zen).exists():
        lines = Path(zen).read_text(encoding='utf-8-sig').splitlines()
        st = next(i for i, l in enumerate(lines) if l.startswith('Transactions:')) + 2
        for l in lines[st:]:
            if not l.strip():
                continue
            o = next(csv.reader([l]))
            f = next(csv.reader([o[0]])) if len(o) == 1 else o
            if len(f) < 4:
                continue
            bank.append(dict(konto=U.get('konto_zen', 'ZEN'), data=datetime.strptime(f[0], '%d %b %Y').date(),
                             opis=re.sub(r'\s+', ' ', f[2]).strip(), kwota=kw(f[3]), saldo=kw(f[11]) if len(f) > 11 and f[11] else None))
    if mbank and Path(mbank).exists():
        lines = Path(mbank).read_text(encoding='utf-8-sig').splitlines()
        st = next(i for i, l in enumerate(lines) if l.startswith('#Data operacji')) + 1
        for l in lines[st:]:
            f = next(csv.reader([l], delimiter=';'))
            if len(f) < 5 or not re.match(r'\d{4}-\d{2}-\d{2}', f[0]):
                continue
            bank.append(dict(konto=U.get('konto_mbank', 'mBank'), data=date.fromisoformat(f[0]),
                             opis=re.sub(r'\s+', ' ', f[1]).strip(), kwota=kw(f[4]), saldo=None))
    seen = {}
    for t in bank:
        base = f"{t['konto']}|{t['data']}|{t['kwota']}|{t['opis']}"
        seen[base] = seen.get(base, 0) + 1
        t['id'] = 'b' + hashlib.sha1(f'{base}|{seen[base]}'.encode()).hexdigest()[:10]
        t['osoba'] = U.get('osoba_wyciagi', '')
        t['kier'] = 'wpływ' if t['kwota'] > 0 else 'wypływ'
        t['mies'] = t['data'].strftime('%Y-%m')
        t['no'] = norm(t['opis'])
    return bank


# ---------- wpisy (wpis.py) – pliki listy/RRRR-MM-wpisy.jsonl i ich wiersze w arkuszu (POM-29)
# Wpisy z datą od tego dnia idą do arkusza od razu (arkusz_budzetu.py sync); starsze – przy zamknięciu miesiąca.
ARKUSZ_OD = U.get('arkusz_od', '2026-12-01')
POMIJANE_W_SKROCIE = ('dodano', 'arkusz', 'usuniety')


def plik_wpisow(mies):
    return DANE / 'listy' / f'{mies}-wpisy.jsonl'


def czytaj_wpisy(mies, z_usunietymi=False):
    """Zapisy z pliku miesiąca; usunięte (czekają na wyczyszczenie wiersza w arkuszu) tylko z z_usunietymi."""
    p = plik_wpisow(mies)
    ws = [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()] if p.exists() else []
    return ws if z_usunietymi else [w for w in ws if not w.get('usuniety')]


def zapisz_wpisy(mies, wpisy):
    p = plik_wpisow(mies)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix('.tmp')
    tmp.write_text(''.join(json.dumps(w, ensure_ascii=False) + '\n' for w in wpisy), encoding='utf-8')
    tmp.replace(p)


def miesiace_wpisow():
    return sorted(p.name[:7] for p in (DANE / 'listy').glob('????-??-wpisy.jsonl'))


class blokada_wpisow:
    """Wyłączny dostęp do plików wpisów (wpis.py i synchronizacja z arkuszem nie nadpiszą sobie zmian)."""

    def __enter__(self):
        import fcntl
        (DANE / 'listy').mkdir(parents=True, exist_ok=True)
        self.f = open(DANE / 'listy' / '.wpisy.lock', 'w')
        fcntl.flock(self.f, fcntl.LOCK_EX)
        return self

    def __exit__(self, *a):
        self.f.close()


def skrot(w):
    """Skrót treści zapisu – zmienia się tylko, gdy zmieni się wpis (nie przy ponownym przebiegu ani wysyłce)."""
    tresc = {k: v for k, v in w.items() if k not in POMIJANE_W_SKROCIE}
    return hashlib.sha1(json.dumps(tresc, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]


def kwota_pozycji(kwota, typ):
    """Kwota w arkuszu dla pozycji listy / wpisu: wydatek dodatni, zwrot („+”) ujemny – zwrot pomniejsza zakup.
    Przychód i przelew – wartość bezwzględna (listy zapisują je bez „+”)."""
    return abs(kwota) if typ in ('Przychód', 'Przelew') else round(-kwota, 2)


def skladniki_arkusza(kwota_ark, skladniki):
    """Składniki działania („30-5”) ze znakiem arkusza albo None, gdy nie sumują się do kwoty."""
    if not skladniki:
        return None
    if abs(round(sum(skladniki), 2) - kwota_ark) < 0.005:
        return skladniki
    skl = [-x for x in skladniki]
    return skl if abs(round(sum(skl), 2) - kwota_ark) < 0.005 else None


def formula_sumy(skl):
    return ('=' + '+'.join(f'{x:.2f}' for x in skl)).replace('+-', '-')


def notatka_wpisu(w):
    p = w.get('paragon')
    n = f"z paragonu – {p['sklep']}, razem {p['suma']:.2f}, części {p['czesci']}" if p else 'z wpisu'
    return n + (' – w kosztorysie budowy (💸)' if w.get('budowa') else '')


def wiersz_wpisu(w):
    """Zapis z pliku -> wiersz zakładki Transakcje (A:L i O) – ten sam dla synchronizacji i zamknięcia miesiąca."""
    ark = kwota_pozycji(w['kwota'], w['typ'])
    skl = skladniki_arkusza(ark, w.get('skladniki'))
    return dict(id=w['id'], data=w['data'], status='Zrealizowane', typ=w['typ'],
                kwota=formula_sumy(skl) if skl and len(skl) > 1 else ark, kat=w['kat'], pod=w['pod'], konto=w['konto'],
                osoba='' if w['typ'] == 'Przelew' else w['osoba'], opis=w['opis'] or w['kod'], tag=f"import {w['data'][:7]}",
                notatki=notatka_wpisu(w))


def z_wpisu(r):
    """Wiersz arkusza z wpisu (ID z prefiksem w w kolumnie O)."""
    return any(i.startswith('w') for i in r['ids'])


def arkusz(sciezka):
    """Transakcje!A1:O z get_values ({"values": [...]}) -> lista wierszy z numerem wiersza arkusza."""
    out = []
    for i, r in enumerate(json.loads(Path(sciezka).read_text(encoding='utf-8'))['values'][1:], start=2):
        r = r + [''] * (15 - len(r))
        ids = [x.strip() for x in r[14].split(',') if x.strip()]
        if not ids and (not r[0] or not r[3]):
            continue  # wiersz z ID zostaje nawet niepełny (przerwane dopisz) – inaczej import dopisałby drugi z tym ID
        try:
            d = datetime.strptime(r[0], '%d-%b-%Y').date()
        except ValueError:
            d = None
        try:
            kwota = kw(r[3]) if r[3] else None
        except ValueError:
            kwota = None
        out.append(dict(wiersz=i, data=d, typ=r[2], kwota=kwota, kat=r[4], pod=r[5], konto=r[6], opis=r[8], tag=r[10],
                        mies=r[12], ids=ids))
    return out


def indeks_id(wiersze):
    """ID z kolumny O -> wiersz. ID wyciągu w kilku wierszach (grupa paragonu) -> wiersz największej części, bo zwrot
    i korekta trafiają w największą część."""
    out = {}
    for r in wiersze:
        for i in r['ids']:
            if i not in out or abs(r['kwota'] or 0) > abs(out[i]['kwota'] or 0):
                out[i] = r
    return out
