#!/usr/bin/env python3
"""Paragon ze zdjęcia -> części jednej płatności w pliku wpisów budżetu domowego (POM-30). Procedura: plugins/ja/skills/budzet,
references/paragony.md.

    python3 tools/budzet/paragon.py pobierz --url "<adres pliku z Notion>" --data RRRR-MM-DD --id <id wpisu>
    python3 tools/budzet/paragon.py rozpisz --id <id wpisu> --data RRRR-MM-DD --platnosc "<skrót konta>[, <skrót osoby>]" \
        --sklep "<sklep>" --suma <suma z paragonu> [--budowa <id strony 💸>] [--zdjecie <plik>] [--proba] [--mimo-to] \
        "<kwota>, <skrót kategorii | rabat | kaucja>[, opis]" ...

pobierz: zdjęcie (albo PDF) wpisu -> <dane>/paragony/RRRR-MM-DD-<id>.<roz>; tylko https i hosty z HOSTY_PLIKOW, limit
rozmiaru, bez nadpisywania (plik już jest -> jego ścieżka). Plik zostaje jako dowód.
rozpisz: pozycje odczytane ze zdjęcia (każda z kategorią; pozycja niejasna – najbliższa kategoria i „?” w opisie) ->
suma na kategorię, rabaty i kaucje na cały paragon rozłożone proporcjonalnie metodą największych reszt (grosze, int),
kontrola: suma części = --suma co do grosza. Niezgodność, nieznany skrót albo brak konta -> kod 1, nic się nie zapisuje.
Zapis: jedna część na kategorię, ID w<id>-1…n, pole `grupa` = w<id>, pole `paragon` (sklep, suma, liczba części, zdjęcie).
Ten sam --id zastępuje cały paragon (część, której już nie ma: wysłana -> znak `usuniety`, niewysłana -> znika; zwykły wpis
z ID w<id> też) – ale nie paragon już rozliczony: przypięty do płatności z wyciągu albo z zamkniętego miesiąca (jest
miesiace/RRRR-MM-zapis.json) -> kod 1, poprawka ręcznie w arkuszu. Inna grupa z tą samą datą, sumą i sklepem -> kod 1
(możliwy dubel), chyba że --mimo-to. Zdjęcie wklejone w rozmowę (bez bloku Notion): --id c<RRRRMMDD>-<suma w groszach>.
--budowa: ID strony 💸 dla części Inwestycja › Dom (kosztorys budowy; dom-budowa/skills/koszty/references/wydatek-przeplyw.md).
Usunięcie całego paragonu: wpis.py usun RRRR-MM <id wpisu albo części>.
"""
import argparse, http.client, json, re, shutil, subprocess, sys, urllib.error, urllib.parse, urllib.request
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wspolne  # noqa: E402
from wspolne import U, blokada_wpisow, czytaj_wpisy, miesiace_wpisow, opcja, wczytaj, zapisz_wpisy  # noqa: E402

HOSTY_PLIKOW = ('prod-files-secure.s3.us-west-2.amazonaws.com',)  # adresy z konektora Notion (sprawdzone 18.11.2026)
MAX_BAJTOW = 20 * 1024 * 1024
ROZSZERZENIA = {'image/jpeg': 'jpg', 'image/jpg': 'jpg', 'image/png': 'png', 'image/webp': 'webp', 'image/gif': 'gif',
                'image/heic': 'heic', 'image/heif': 'heic', 'application/pdf': 'pdf'}
MARKI_HEIC = (b'heic', b'heix', b'heim', b'heis', b'hevc', b'hevx', b'mif1', b'msf1', b'heif')
ID = re.compile(r'^[A-Za-z0-9-]{1,64}$')
# kwota: z separatorem tysięcy („1 234,56”) albo bez; więcej niż 2 cyfry po przecinku -> czytelny błąd z grosze()
POZYCJA = re.compile(r'^\s*([+-]?\d{1,3}(?:[ \u00a0]\d{3})+(?:[.,]\d+)?|[+-]?\d+(?:[.,]\d+)?)\s*,\s*([^,]+?)\s*(?:,\s*(.*?))?\s*$')
TYPY_WYDATKU = ('Wydatek', 'Koszt', 'Inwestycja')


class BladParagonu(Exception):
    pass


def grosze(tekst):
    try:
        g = Decimal(str(tekst).replace(' ', '').replace('\u00a0', '').replace(',', '.')) * 100
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


def czesci_grupy(w, grupa):
    """Zapis należy do paragonu: część grupy albo zwykły wpis z ID równym grupie (ten sam blok wpisu)."""
    return w.get('grupa') == grupa or w['id'] == grupa


def rozliczenie(grupa, mies_nowy, mimo_to=False, sklep='', suma=None, data=''):
    """Powód odmowy zastąpienia paragonu albo ''. Rozliczony = część przypięta do płatności z wyciągu (przypiecia,
    wiersze z płatności w miesiace/*-zapis.json – także zamknięcia sąsiedniego miesiąca) albo miesiąc paragonu zamknięty
    (jest miesiace/RRRR-MM-zapis.json). Inna grupa z tą samą datą, sumą i sklepem -> BladParagonu (bez --mimo-to)."""
    stare = [(m, w) for m in miesiace_wpisow() for w in czytaj_wpisy(m) if czesci_grupy(w, grupa)]
    ids = {w['id'] for _, w in stare}
    if stare:
        for m in sorted({m for m, _ in stare} | {mies_nowy}):
            if (wspolne.DANE / 'miesiace' / f'{m}-zapis.json').exists():
                return f'miesiąc {m} jest zamknięty'
        for p in sorted((wspolne.DANE / 'miesiace').glob('????-??-zapis.json')):  # wynik zamknięcia (przenies.py), także sąsiedniego
            try:
                z = json.loads(p.read_text(encoding='utf-8'))
            except ValueError:
                continue
            uzyte = {x['id'] for pp in z.get('przypiecia', []) for x in pp.get('wiersze', [])}
            uzyte |= {t.strip() for w in z.get('wiersze', []) if isinstance(w, list) and len(w) > 14 for t in str(w[14]).split(',')}
            if ids & uzyte:
                return f'jest rozliczony z płatnością z wyciągu ({p.name})'
    if not mimo_to and suma is not None:
        for m in miesiace_wpisow():
            for w in czytaj_wpisy(m):
                pa = w.get('paragon') or {}
                if (w.get('grupa') and w['grupa'] != grupa and w['data'] == data and abs(pa.get('suma', -1) - suma) < 0.005
                        and pa.get('sklep', '').strip().lower() == sklep.strip().lower()):
                    raise BladParagonu(f"jest już paragon {w['grupa']} z tą samą datą, sumą i sklepem – możliwy dubel "
                                       '(inne zdjęcie tego samego paragonu?); ten sam paragon = ten sam --id, inny – --mimo-to')
    return ''


def zapisz_grupe(nowe):
    """Zastępuje wszystkie części grupy (każdy miesiąc) i zwykły wpis z ID grupy; znacznik wysyłki zostaje przy tym samym ID."""
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
                if czesci_grupy(w, grupa) and not w.get('usuniety'):
                    if w.get('arkusz'):
                        reszta.append(dict(w, usuniety=teraz))  # części już nie ma – sync usunie jej wiersz
                    continue
                reszta.append(w)
            if m == mies:
                reszta += nowe
            if reszta != ws:
                zapisz_wpisy(m, reszta)
    return sum(1 for ws in miesiace.values() for w in ws if not w.get('usuniety') and (w['id'] in ids or czesci_grupy(w, grupa)))


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


def rozpoznaj(tresc):
    """Typ pliku po nagłówku (gdy serwer podał application/octet-stream) -> rozszerzenie albo None."""
    if tresc[:3] == b'\xff\xd8\xff':
        return 'jpg'
    if tresc[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    if tresc[:5] == b'%PDF-':
        return 'pdf'
    if tresc[:4] == b'RIFF' and tresc[8:12] == b'WEBP':
        return 'webp'
    if tresc[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    if tresc[4:8] == b'ftyp' and tresc[8:12] in MARKI_HEIC:
        return 'heic'
    return None


def pobierz(url, data, id_, katalog=None, otworz=None):
    """-> ścieżka pliku w <dane>/paragony/; plik już jest -> ta sama ścieżka bez pobierania."""
    wspolne.data_iso(data)
    if not ID.match(id_):
        raise BladParagonu('ID wpisu tylko z liter, cyfr i myślników')
    url = sprawdz_adres(url)
    katalog = Path(katalog or wspolne.DANE / 'paragony')
    juz = sorted(p for p in katalog.glob(f'{data}-{id_}.*') if p.suffix not in ('.tmp', '.heic'))
    if juz:
        return juz[0], True
    otworz = otworz or urllib.request.build_opener(TylkoTeHosty).open
    try:  # komunikaty bez adresu – podpisany adres nie może trafić do śladu ani do 🔔
        with otworz(url, timeout=60) as odp:
            typ = (odp.headers.get('Content-Type') or '').split(';')[0].strip().lower()
            if int(odp.headers.get('Content-Length') or 0) > MAX_BAJTOW:
                raise BladParagonu(f'plik większy niż {MAX_BAJTOW // 2**20} MB')
            tresc = odp.read(MAX_BAJTOW + 1)
    except urllib.error.HTTPError as e:
        raise BladParagonu(f'HTTP {e.code} – adres z konektora wygasa po kilku minutach; pobierz nowy') from None
    except (OSError, http.client.HTTPException, ValueError) as e:
        raise BladParagonu(f'pobieranie: {type(e).__name__}') from None
    if len(tresc) > MAX_BAJTOW:
        raise BladParagonu(f'plik większy niż {MAX_BAJTOW // 2**20} MB')
    roz = rozpoznaj(tresc) or (ROZSZERZENIA.get(typ) if typ != 'application/octet-stream' else None)
    if not roz:
        raise BladParagonu(f'to nie zdjęcie ani PDF ({typ or "brak typu"})')
    katalog.mkdir(parents=True, exist_ok=True)
    cel = katalog / f'{data}-{id_}.{roz}'
    tmp = cel.with_name(cel.name + '.tmp')
    tmp.write_bytes(tresc)
    tmp.replace(cel)
    if roz == 'heic':  # zdjęcie z iPhone'a – Read czyta JPG
        jpg = cel.with_suffix('.jpg')
        if shutil.which('sips'):
            subprocess.run(['sips', '-s', 'format', 'jpeg', str(cel), '--out', str(jpg)], capture_output=True, timeout=60)
        if not jpg.exists():
            raise BladParagonu('zdjęcie HEIC – nie udało się zamienić na JPG (sips); plik został jako dowód, odczyt w sesji')
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
    ap.add_argument('--mimo-to', action='store_true', help='zapisz mimo innego paragonu z tą samą datą, sumą i sklepem')
    a, pozycje = ap.parse_known_args(argv)  # pozycje to reszta argumentów – także „-3,00, rabat” z minusem na początku
    if any(p.startswith('--') for p in pozycje):
        ap.error('nieznana opcja: ' + ', '.join(p for p in pozycje if p.startswith('--')))
    try:
        if a.akcja == 'pobierz':
            if not a.url:
                raise BladParagonu('podaj --url')
            try:
                p, juz = pobierz(a.url, a.data, a.id)
            except ValueError as e:  # np. data – bez treści wyjątku, który mógłby nieść adres
                raise BladParagonu(f'zły argument ({type(e).__name__}) – data RRRR-MM-DD, adres z konektora') from None
            print(('już pobrane: ' if juz else 'pobrano: ') + str(p))
            return 0
        if not ID.match(a.id):
            raise BladParagonu('ID wpisu tylko z liter, cyfr i myślników')
        wspolne.data_iso(a.data)
        if not a.suma or not a.sklep:
            raise BladParagonu('podaj --suma i --sklep (z paragonu)')
        platnosc(a.platnosc)
        czesci = rozpisz(pozycje, grosze(a.suma), wczytaj('reguly.json', {}).get('skroty', {}))
        nowe = zapisy(a, czesci)
        powod = rozliczenie(nowe[0]['grupa'], a.data[:7], a.mimo_to, a.sklep, nowe[0]['paragon']['suma'], a.data)
        if powod and not a.proba:
            raise BladParagonu(f"paragon {nowe[0]['grupa']} {powod} – nie zastępuję go (kwoty w arkuszu są już z wyciągu); "
                               'popraw kategorie ręcznie w arkuszu i odnotuj to w ❓ pod wpisem; nic nie zapisano')
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
