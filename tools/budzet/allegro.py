#!/usr/bin/env python3
"""Lista „Moje zakupy” z Allegro (tekst skopiowany ze strony) -> JSON zamówień (procedura budzet).

    python3 tools/budzet/allegro.py listy/allegro-<data>.txt listy/allegro-<data>.json

Ścieżki względne – od folderu danych budżetu. `prop` (propozycja kategorii) wypełnia się z wcześniejszych wyborów
dla tego sprzedawcy (reguly.json → allegro_sprzedawcy); resztę uzupełnia Claude na podstawie nazw produktów."""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import DANE, wczytaj  # noqa: E402

MIES = {'sty': 1, 'lut': 2, 'mar': 3, 'kwi': 4, 'maj': 5, 'cze': 6, 'lip': 7, 'sie': 8, 'wrz': 9, 'paź': 10, 'paz': 10, 'lis': 11, 'gru': 12}


def kw(s):
    return round(float(s.replace('\xa0', '').replace(' ', '').replace('zł', '').replace(',', '.')), 2)


def parsuj(tekst):
    linie = [l.strip() for l in tekst.splitlines()]
    bloki, cur = [], None
    for l in linie:
        if l.startswith('Zaznacz zakup:'):
            cur = [l]
            bloki.append(cur)
        elif cur is not None:
            cur.append(l)
    out = []
    for b in bloki:
        z = dict(data='', sprzedawca='', suma=None, pay=False, zwrocony=False, produkty=[], prop='', opcje=[])
        for i, l in enumerate(b):
            m = re.match(r'^(\d{1,2}) (\w{3})\w* (\d{4}), \d{1,2}:\d{2}$', l)
            if m and not z['data']:
                z['data'] = f"{m.group(3)}-{MIES[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
            if l in ('Od', 'z') and not z['sprzedawca']:
                z['sprzedawca'] = next((x for x in b[i + 1:] if x), '')
            m = re.match(r'^(\d+) × [\d\s,]+ zł$', l)
            if m:
                nazwa = next((x for x in reversed(b[:i]) if x and not x.startswith('Gwarancja')), '')
                z['produkty'].append(nazwa + (f' ×{m.group(1)}' if m.group(1) != '1' else ''))
            if l.startswith('Razem'):
                kw_ = next((x for x in b[i + 1:] if re.match(r'^[\d\s]+,\d{2} zł$', x)), None)
                z['suma'] = kw(kw_) if kw_ else None
            if l == 'Zakup zwrócony':
                z['zwrocony'] = True
            if l == 'Zakup przez Allegro Pay':
                z['pay'] = True
        if z['data'] and z['suma'] is not None:
            out.append(z)
    return out


if __name__ == '__main__':
    we, wy = (Path(p) if Path(p).is_absolute() else DANE / p for p in sys.argv[1:3])
    zam = parsuj(we.read_text(encoding='utf-8'))
    znani = wczytaj('reguly.json', {}).get('allegro_sprzedawcy', {})
    for z in zam:
        z['prop'] = znani.get(z['sprzedawca'], '')
    wy.write_text(json.dumps(dict(zrodlo=we.name, zamowienia=zam), ensure_ascii=False, indent=1), encoding='utf-8')
    print(len(zam), 'zamówień,', sum(1 for z in zam if z['zwrocony']), 'zwróconych, suma', round(sum(z['suma'] for z in zam), 2))
