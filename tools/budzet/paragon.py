#!/usr/bin/env python3
"""Paragon ze zdjęcia -> części jednej płatności w pliku wpisów budżetu domowego (POM-30). Procedura: plugins/ja/skills/budzet,
references/paragony.md.

    python3 tools/budzet/paragon.py pobierz --url "<adres pliku z Notion>" --data RRRR-MM-DD --id <id wpisu>
    python3 tools/budzet/paragon.py rozpisz --id <id wpisu> --data RRRR-MM-DD --platnosc "<skrót konta>[, <skrót osoby>]" \
        --sklep "<sklep>" --suma <suma z paragonu> [--budowa <id strony 💸>] [--zdjecie <plik>] [--proba] \
        "<kwota>, <skrót kategorii | rabat | kaucja>[, opis]" ...

pobierz: zdjęcie (albo PDF) wpisu -> <dane>/paragony/RRRR-MM-DD-<id>.<roz>; tylko https i hosty z HOSTY_PLIKOW, limit
rozmiaru, bez nadpisywania (plik już jest -> jego ścieżka). Plik zostaje jako dowód.
rozpisz: pozycje odczytane ze zdjęcia (każda z kategorią; pozycja niejasna – najbliższa kategoria i „?” w opisie) ->
suma na kategorię, rabaty i kaucje na cały paragon rozłożone proporcjonalnie metodą największych reszt (grosze, int),
kontrola: suma części = --suma co do grosza. Niezgodność, nieznany skrót albo brak konta -> kod 1, nic się nie zapisuje.
Zapis: jedna część na kategorię, ID w<id>-1…n, pole `grupa` = w<id>, pole `paragon` (sklep, suma, liczba części, zdjęcie).
Ten sam --id zastępuje cały paragon (część, której już nie ma: wysłana -> znak `usuniety`, niewysłana -> znika).
--budowa: ID strony 💸 dla części Inwestycja › Dom (kosztorys budowy; dom-budowa/skills/koszty/references/wydatek-przeplyw.md).
Usunięcie całego paragonu: wpis.py usun RRRR-MM <id wpisu albo części>.
"""
import argparse, re, shutil, subprocess, sys, urllib.error, urllib.parse, urllib.request
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import DANE, U, blokada_wpisow, czytaj_wpisy, miesiace_wpisow, opcja, wczytaj, zapisz_wpisy  # noqa: E402

HOSTY_PLIKOW = ('prod-files-secure.s3.us-west-2.amazonaws.com',)  # adresy z konektora Notion (sprawdzone 18.11.2026)
MAX_BAJTOW = 20 * 1024 * 1024
ROZSZERZENIA = {'image/jpeg': 'jpg', 'image/jpg': 'jpg', 'image/png': 'png', 'image/webp': 'webp', 'image/gif': 'gif',
                'image/heic': 'heic', 'image/heif': 'heif', 'application/pdf': 'pdf'}
ID = re.compile(r'^[A-Za-z0-9-]{1,64}$')
POZYCJA = re.compile(r'^\s*([+-]?\d+(?:[.,]\d{1,2})?)\s*,\s*([^,]+?)\s*(?:,\s*(.*?))?\s*$')
TYPY_WYDATKU = ('Wydatek', 'Koszt', 'Inwestycja')


class BladParagonu(Exception):
    pass


def grosze(tekst):
    try:
        g = Decimal(str(tekst).replace(' ', '').replace(',', '.')) * 100
    except InvalidOperation:
        raise BladParagonu(f'to nie kwota: „{tekst}”') from None
    if g != g.to_integral_value():
        raise BladParagonu(f'kwota z więcej niż 2 miejscami po przecinku: „{tekst}”')
    return int(g)


def zl(g):
    return f'{g / 100:.2f}'


def rozloz(kwota, wagi):
    """Kwota (grosze, ze znakiem) na części proporcjonalnie do wag (grosze > 0) metodą największych reszt; suma = kwota."""
    s = sum(wagi)
    a = abs(kwota)
    baza = [a * w // s for w in wagi]
    reszty = [a * w % s for w in wagi]
    for i in sorted(range(len(wagi)), key=lambda i: (-reszty[i], -wagi[i], i))[:a - sum(baza)]:
        baza[i] += 1
    return [b if kwota >= 0 else -b for b in baza]


def rozpisz(pozycje, suma, skroty):
    """pozycje: teksty „kwota, skrót|rabat|kaucja[, opis]”; suma: grosze z paragonu; skroty: reguly.json → skroty.
    -> lista części [{kod, typ, kat, pod, grosze, opisy, korekta}] w kolejności pierwszego wystąpienia kategorii."""
    czesci, ogolne = {}, 0
    for p in pozycje:
        m = POZYCJA.match(p)
        if not m:
            raise BladParagonu(f'pozycja nie ma formatu „kwota, kategoria[, opis]”: „{p}”')
        g, kod, opis = grosze(m.group(1)), m.group(2).strip().lower(), (m.group(3) or '').strip()
        if kod == 'rabat':
            ogolne -= abs(g)
            continue
        if kod == 'kaucja':
            ogolne += g
            continue
        if kod not in skroty:
            raise BladParagonu(f'nieznany skrót kategorii „{kod}” – wybierz najbliższy ze skrótów (reguly.json)')
        o = opcja(*skroty[kod])
        if o['typ'] not in TYPY_WYDATKU:
            raise BladParagonu(f'„{kod}” to {o["typ"]} – pozycje paragonu to wydatki')
        c = czesci.setdefault((o['typ'], o['kat'], o['pod']), dict(kod=kod, typ=o['typ'], kat=o['kat'], pod=o['pod'], grosze=0,
                                                                  opisy=[], korekta=0))
        c['grosze'] += g
        if opis and g > 0:  # rabat pod pozycją nie trafia do opisu
            c['opisy'].append(opis)
    lista = list(czesci.values())
    if not lista:
        raise BladParagonu('brak pozycji z kategorią')
    if any(c['grosze'] <= 0 for c in lista):
        raise BladParagonu('kategoria z sumą ≤ 0 (rabat większy niż pozycje?) – sprawdź odczyt')
    for c, k in zip(lista, rozloz(ogolne, [c['grosze'] for c in lista]) if ogolne else [0] * len(lista)):
        c['korekta'] = k
        c['grosze'] += k
    razem = sum(c['grosze'] for c in lista)
    if razem != suma:
        raise BladParagonu(f'suma części {zl(razem)} ≠ suma paragonu {zl(suma)} (różnica {zl(razem - suma)}) – '
                           'brakuje pozycji albo zły odczyt; nic nie zapisano')
    if any(c['grosze'] <= 0 for c in lista):
        raise BladParagonu('część ≤ 0 po rozłożeniu rabatu – sprawdź odczyt')
    return lista


def platnosc(tekst):
    """„z” / „z, a” / „g” / „gotówka” -> (skrót konta albo '', skrót osoby albo ''); brak konta -> BladParagonu."""
    pola = [p.strip().lower() for p in (tekst or '').split(',') if p.strip()]
    sk_konta = {k.lower() for k in U.get('skroty_kont', {})}
    sk_osoby = {k.lower() for k in U.get('skroty_osob', {})}
    if not pola or (pola[0] not in sk_konta and pola[0] not in ('gotówka', 'gotowka')):
        raise BladParagonu('brak „kto i czym” (konto ze skrótów kont albo „gotówka”) – paragon czeka na odpowiedź (❓)')
    if len(pola) > 2 or (len(pola) == 2 and pola[1] not in sk_osoby):
        raise BladParagonu(f'nieznana osoba „{", ".join(pola[1:])}” – skróty osób z ustawienia.json')
    return ('' if pola[0] in ('gotówka', 'gotowka') else pola[0]), (pola[1] if len(pola) == 2 else '')


def opis_czesci(sklep, c, limit=120):
    s = f"{sklep}: {', '.join(c['opisy'])}" if c['opisy'] else sklep
    return s if len(s) <= limit else s[:limit - 1] + '…'


def zapisy(a, czesci):
    """Części -> zapisy pliku wpisów (te same pola co wpis.py, plus grupa i paragon)."""
    import wpis
    konto, osoba = platnosc(a.platnosc)
    grupa = 'w' + a.id
    budowa_bez_dom = a.budowa and not any(c['kat'] == 'Dom' for c in czesci)
    if budowa_bez_dom:
        raise BladParagonu('--budowa podane, a żadna część nie jest Inwestycja › Dom')
    out = []
    for i, c in enumerate(czesci, 1):
        tekst = ', '.join(x for x in (zl(c['grosze']), konto, osoba, c['kod'], opis_czesci(a.sklep, c)) if x)
        w = wpis.parsuj(tekst, skroty={c['kod']: [c['typ'], c['kat'], c['pod']]})
        out.append(dict(id=f'{grupa}-{i}', data=a.data, tekst=tekst, **w, budowa=a.budowa if c['kat'] == 'Dom' else '',
                        grupa=grupa, paragon=dict(sklep=a.sklep, suma=round(grosze(a.suma) / 100, 2), czesci=len(czesci),
                                                  zdjecie=a.zdjecie or ''),
                        dodano=datetime.now().strftime('%Y-%m-%d %H:%M')))
    return out


def zapisz_grupe(nowe):
    """Zastępuje wszystkie części grupy (każdy miesiąc); znacznik wysyłki zostaje przy tym samym ID."""
    grupa, mies = nowe[0]['grupa'], nowe[0]['data'][:7]
    ids = {w['id'] for w in nowe}
    with blokada_wpisow():
        miesiace = {m: czytaj_wpisy(m, z_usunietymi=True) for m in sorted(set(miesiace_wpisow()) | {mies})}
        stare = {w['id']: w for ws in miesiace.values() for w in ws if w['id'] in ids}  # jak wpis.py: także usunięte
        for w in nowe:
            if stare.get(w['id'], {}).get('arkusz'):
                w['arkusz'] = stare[w['id']]['arkusz']  # synchronizacja poprawi wiersz, nie dopisze drugiego
        teraz = datetime.now().strftime('%Y-%m-%d %H:%M')
        for m, ws in miesiace.items():
            reszta = []
            for w in ws:
                if w['id'] in ids:
                    continue  # część zastąpiona nową (także gdy zmienił się miesiąc daty)
                if w.get('grupa') == grupa and not w.get('usuniety'):
                    if w.get('arkusz'):
                        reszta.append(dict(w, usuniety=teraz))  # części już nie ma – sync usunie jej wiersz
                    continue
                reszta.append(w)
            if m == mies:
                reszta += nowe
            if reszta != ws:
                zapisz_wpisy(m, reszta)
    return sum(1 for w in stare.values() if not w.get('usuniety'))


class TylkoTeHosty(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        sprawdz_adres(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def sprawdz_adres(url):
    u = urllib.parse.urlsplit(url)
    if u.scheme != 'https':
        raise BladParagonu('adres pliku musi być https')
    if (u.hostname or '') not in HOSTY_PLIKOW:
        raise BladParagonu(f'host „{u.hostname}” spoza listy plików Notion (HOSTY_PLIKOW w paragon.py) – nic nie pobrano')
    return urllib.parse.urlunsplit((u.scheme, u.netloc, u.path, u.query, ''))


def pobierz(url, data, id_, katalog=None, otworz=None):
    """-> ścieżka pliku w <dane>/paragony/; plik już jest -> ta sama ścieżka bez pobierania."""
    date.fromisoformat(data)
    if not ID.match(id_):
        raise BladParagonu('ID wpisu tylko z liter, cyfr i myślników')
    url = sprawdz_adres(url)
    katalog = Path(katalog or DANE / 'paragony')
    juz = sorted(p for p in katalog.glob(f'{data}-{id_}.*') if not p.name.endswith('.tmp'))
    if juz:
        return next((p for p in juz if p.suffix != '.heic'), juz[0]), True
    otworz = otworz or urllib.request.build_opener(TylkoTeHosty).open
    try:
        with otworz(url, timeout=60) as odp:
            typ = (odp.headers.get('Content-Type') or '').split(';')[0].strip().lower()
            if typ not in ROZSZERZENIA:
                raise BladParagonu(f'to nie zdjęcie ani PDF ({typ or "brak typu"})')
            if int(odp.headers.get('Content-Length') or 0) > MAX_BAJTOW:
                raise BladParagonu(f'plik większy niż {MAX_BAJTOW // 2**20} MB')
            tresc = odp.read(MAX_BAJTOW + 1)
    except urllib.error.HTTPError as e:
        raise BladParagonu(f'HTTP {e.code} – adres z konektora wygasa po kilku minutach; pobierz nowy') from None
    except OSError as e:
        raise BladParagonu(f'pobieranie: {type(e).__name__}') from None
    if len(tresc) > MAX_BAJTOW:
        raise BladParagonu(f'plik większy niż {MAX_BAJTOW // 2**20} MB')
    katalog.mkdir(parents=True, exist_ok=True)
    cel = katalog / f'{data}-{id_}.{ROZSZERZENIA[typ]}'
    tmp = cel.with_name(cel.name + '.tmp')
    tmp.write_bytes(tresc)
    tmp.replace(cel)
    if cel.suffix in ('.heic', '.heif') and shutil.which('sips'):  # zdjęcie z iPhone'a – Read czyta JPG
        jpg = cel.with_suffix('.jpg')
        subprocess.run(['sips', '-s', 'format', 'jpeg', str(cel), '--out', str(jpg)], capture_output=True, timeout=60)
        if jpg.exists():
            return jpg, False
    return cel, False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('akcja', choices=('pobierz', 'rozpisz'))
    ap.add_argument('--url')
    ap.add_argument('--data', required=True)
    ap.add_argument('--id', required=True, help='ID bloku / strony wpisu (bez prefiksu w)')
    ap.add_argument('--platnosc', help='skrót konta [, skrót osoby]; „gotówka” albo skrót konta gotówki')
    ap.add_argument('--sklep', default='')
    ap.add_argument('--suma', help='suma z paragonu (SUMA / do zapłaty)')
    ap.add_argument('--budowa', default='', help='ID strony 💸 dla części Inwestycja › Dom')
    ap.add_argument('--zdjecie', default='', help='plik z pobierz (zostaje w polu paragon)')
    ap.add_argument('--proba', action='store_true', help='pokaż rozpisanie, nic nie zapisuj')
    a, pozycje = ap.parse_known_args(argv)  # pozycje to reszta argumentów – także „-3,00, rabat” z minusem na początku
    if any(p.startswith('--') for p in pozycje):
        ap.error('nieznana opcja: ' + ', '.join(p for p in pozycje if p.startswith('--')))
    try:
        if a.akcja == 'pobierz':
            if not a.url:
                raise BladParagonu('podaj --url')
            p, juz = pobierz(a.url, a.data, a.id)
            print(('już pobrane: ' if juz else 'pobrano: ') + str(p))
            return 0
        if not ID.match(a.id):
            raise BladParagonu('ID wpisu tylko z liter, cyfr i myślników')
        date.fromisoformat(a.data)
        if not a.suma or not a.sklep:
            raise BladParagonu('podaj --suma i --sklep (z paragonu)')
        platnosc(a.platnosc)
        czesci = rozpisz(pozycje, grosze(a.suma), wczytaj('reguly.json', {}).get('skroty', {}))
        nowe = zapisy(a, czesci)
    except (BladParagonu, ValueError) as e:
        print(f'✗ {e}')
        return 1
    for w, c in zip(nowe, czesci):
        kat = f"{w['kat']} › {w['pod']}" if w['pod'] else w['kat']
        print(f"{w['id']} {w['typ']} {kat} {zl(c['grosze'])}" + (f" (rabat/kaucja {zl(c['korekta'])})" if c['korekta'] else '')
              + (' [budowa]' if w['budowa'] else '') + f" – {w['opis']}")
    print(f"suma części = suma paragonu {zl(grosze(a.suma))} ✓, {len(nowe)} części, {nowe[0]['konto']} / {nowe[0]['osoba']}")
    if a.proba:
        print('próba – nic nie zapisano')
        return 0
    if any(c['kat'] == 'Dom' for c in czesci) and not a.budowa:
        print('uwaga: część Inwestycja › Dom bez --budowa – najpierw strona 💸 (wydatek-przeplyw.md), potem rozpisz z --budowa')
    stare = zapisz_grupe(nowe)
    print(('zastąpiono paragon' if stare else 'zapisano paragon') + f" {nowe[0]['grupa']} ({len(nowe)} części)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
