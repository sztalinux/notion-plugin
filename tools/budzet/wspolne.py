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


def arkusz(sciezka):
    """Transakcje!A1:O z get_values ({"values": [...]}) -> lista wierszy z numerem wiersza arkusza."""
    out = []
    for i, r in enumerate(json.loads(Path(sciezka).read_text(encoding='utf-8'))['values'][1:], start=2):
        r = r + [''] * (15 - len(r))
        if not r[0] or not r[3]:
            continue
        try:
            d = datetime.strptime(r[0], '%d-%b-%Y').date()
        except ValueError:
            d = None
        out.append(dict(wiersz=i, data=d, typ=r[2], kwota=kw(r[3]), kat=r[4], pod=r[5], konto=r[6], opis=r[8], tag=r[10],
                        mies=r[12], ids=[x for x in r[14].split(',') if x]))
    return out
