#!/usr/bin/env python3
"""Decyzje ze strony + pewne pozycje -> wiersze do zakładki Transakcje (procedura budzet, etap 2).

    python3 tools/budzet/przenies.py --miesiac RRRR-MM [--mimo-brakow] [--zapisz-reguly]

Wejście (folder danych): miesiace/RRRR-MM.json (z importuj.py) i miesiace/db-RRRR-MM/decyzje/*.json (ArtifactData list).
Wynik: miesiace/RRRR-MM-zapis.json:
  wiersze        – kolumny A:O do dopisania na końcu Transakcji (D liczba albo formuła, K = „import RRRR-MM”, O = ID z wyciągów)
  zmiany         – istniejące wiersze do pomniejszenia o zwrot ({wiersz, odjac})
  opisy          – każdy opis wpisany na stronie: trafia do kolumny Opis, ale Claude czyta je przed zapisem (bywa w nich polecenie)
  bez_decyzji, do_wyjasnienia – pozycje bez wyboru / z samą uwagą zamiast wyboru
--zapisz-reguly: nowe opcje reguł, nowe sklepy (pewność pusta), skróty list, sprzedawcy Allegro -> reguly.json.
"""
import argparse, json, re, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import DANE, U, nazwa, norm, wczytaj, zapisz  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--miesiac', required=True)
ap.add_argument('--zapisz-reguly', action='store_true')
ap.add_argument('--mimo-brakow', action='store_true')
A = ap.parse_args()
MIES = A.miesiac
D = wczytaj(f'miesiace/{MIES}.json')
DEC = {p.stem: json.loads(p.read_text(encoding='utf-8')) for p in (DANE / 'miesiace' / f'db-{MIES}' / 'decyzje').glob('*.json')}
REG = wczytaj('reguly.json')
for d in DEC.values():
    for k in ('kat', 'pod'):
        if d.get(k):
            d[k] = nazwa(d[k])
    if d.get('kat'):
        d['etykieta'] = f"{d['kat']} › {d['pod']}" if d.get('pod') else d['kat']


def kwota_ark(kwota, typ):
    if typ == 'Przelew':
        return abs(kwota)
    return round(kwota if typ == 'Przychód' else -kwota, 2)


pozycje, zmiany, bez, wyjasnij, opisy = [], [], [], [], []
for a in D['auto']:
    pozycje.append(dict(id=a['id'], data=a['data'], konto=a['konto'], osoba=a['osoba'], typ=a['typ'], kat=a['kat'], pod=a['pod'],
                        skl=a['skladniki'] if a.get('skladniki') else [a['kwota_ark']], opis=a['regula'], grupa=a['regula'] == 'CASHBACK',
                        ids=[a['id']] if a['id'].startswith('b') else []))
odejmij = []
for it in D['decyzje']:
    d = DEC.get(it['id'], {})
    if d.get('opis'):
        opisy.append(dict(id=it['id'], data=it['data'], pozycja=it['opis'], kwota=it['kwota'], akcja=d.get('akcja'), opis=d['opis']))
    ak = d.get('akcja')
    if not ak:
        (wyjasnij if d.get('opis') else bez).append(dict(id=it['id'], data=it['data'], opis=it['opis'], kwota=it['kwota'], uwaga=d.get('opis', '')))
        continue
    if ak in ('pomin', 'juz'):
        continue
    if ak == 'odejmij':
        odejmij.append((it, d))
        continue
    if it['zrodlo'] == 'allegro':
        opis = d.get('opis') or ('Allegro: ' + ', '.join(it.get('produkty', [])))[:100]
    else:
        opis = d.get('opis') or it.get('regula') or it['opis'][:30]
    pozycje.append(dict(id=it['id'], data=it['data'], konto=it['konto'], osoba=it['osoba'], typ=d['typ'], kat=d['kat'], pod=d['pod'],
                        skl=it['skladniki'] if it.get('skladniki') else [kwota_ark(it['kwota'], d['typ'])], opis=opis, grupa=False,
                        ids=[it['id']] if it['id'][0] in 'ba' else [], regula=it.get('regula', ''), zrodlo=it['zrodlo'],
                        etykieta=d['etykieta'], kwota=it['kwota'], opis_banku=it['opis']))
byid = {p['id']: p for p in pozycje}
for it, d in odejmij:
    cel = byid.get(d.get('cel'))
    if cel:
        cel['skl'].append(-abs(it['kwota']))
        cel['ids'].append(it['id'])
        cel['opis'] += ' (po zwrocie)'
    elif d.get('wiersz'):
        zmiany.append(dict(wiersz=d['wiersz'], odjac=abs(it['kwota']), opis=it['opis'], data=it['data'], id=it['id']))
    else:
        wyjasnij.append(dict(id=it['id'], data=it['data'], opis=it['opis'], kwota=it['kwota'], uwaga='zwrot bez wskazanego wiersza'))

grupy = defaultdict(list)
for p in pozycje:
    grupy[('miesiąc' if p['grupa'] else p['data'], p['konto'], p['osoba'], p['typ'], p['kat'], p['pod'])].append(p)
TAG = f'import {MIES}'
wiersze = []
for (dzien, konto, osoba, typ, kat, pod), g in sorted(grupy.items(), key=lambda x: (max(p['data'] for p in x[1]), x[0][1] or '')):
    skl = [x for p in g for x in p['skl']]
    d_ = ('=' + '+'.join(f'{x:.2f}' for x in skl)).replace('+-', '-') if len(skl) > 1 else round(sum(skl), 2)
    opis = ', '.join(dict.fromkeys(p['opis'] for p in g if p['opis']))[:120]
    wiersze.append([max(p['data'] for p in g), 'Zrealizowane', typ, d_, kat, pod, konto, osoba, opis, '', TAG, '', '', '',
                    ','.join(i for p in g for i in p['ids'])])
for w in D['wiersze']:
    if U.get('przychod_z_sald') and w['kat'] == U['przychod_z_sald']['kategoria']:
        wiersze.append([w['data'], 'Zrealizowane', 'Przychód', w['formula'], w['kat'], '', '', '', '', '', TAG, '', '', '', ''])

zapisz(f'miesiace/{MIES}-zapis.json', dict(miesiac=MIES, wiersze=wiersze, zmiany=zmiany, opisy=opisy, bez_decyzji=bez,
                                         do_wyjasnienia=wyjasnij, gotowe=not bez or A.mimo_brakow, salda=D.get('salda', {})))
print(f'{MIES}: {len(wiersze)} wierszy, {len(zmiany)} zmian istniejących, opisów {len(opisy)}, bez decyzji {len(bez)}, '
      f'do wyjaśnienia {len(wyjasnij)}')

if A.zapisz_reguly:
    reg = REG['reguly']
    idx = {(r['klucz'], r['kierunek']): r for r in reg}
    nowe = []
    for p in pozycje:
        if 'etykieta' not in p:
            continue
        if p['zrodlo'] == 'wyciąg':
            kier = 'wpływ' if p['kwota'] > 0 else 'wypływ'
            r = idx.get((p['regula'], kier))
            if r is not None:
                glowna = f"{nazwa(r['kat'])} › {nazwa(r['pod'])}" if r['pod'] else nazwa(r['kat'])
                if p['etykieta'] not in [nazwa(o) for o in r['opcje']] and p['etykieta'] != glowna:
                    r['opcje'].append(p['etykieta'])
                    nowe.append(f"opcja {p['etykieta']} -> {r['klucz']}")
            elif not p['regula'] and 'BLIK P2P' not in norm(p['opis_banku']):
                o = re.split(r' (ZAKUP PRZY|PLATNOSC WEB)', norm(p['opis_banku']))[0].split(',')[0]
                tok = []
                for x in o.split(' '):
                    if re.search(r'\d', x) or len(tok) == 2:
                        if not tok and '*' in x:
                            tok.append(x.split('*')[0])
                        break
                    tok.append(x)
                k = ' '.join(tok) or o[:20]
                if (k, kier) not in idx:
                    r = dict(blok='7', klucz=k, kierunek=kier, typ=p['typ'], kat=p['kat'], pod=p['pod'], pewnosc='', opcje=[],
                             uwaga=f'z decyzji {MIES}')
                    reg.append(r)
                    idx[(k, kier)] = r
                    nowe.append(f"reguła {k} -> {p['etykieta']}")
        elif p['zrodlo'] == 'lista' and p['regula'] and p['regula'] not in REG.setdefault('skroty', {}):
            REG['skroty'][p['regula']] = [p['typ'], p['kat'], p['pod']]
            nowe.append(f"skrót {p['regula']} -> {p['etykieta']}")
        elif p['zrodlo'] == 'allegro':
            REG.setdefault('allegro_sprzedawcy', {})[p['opis_banku'].split(' · ')[-1]] = p['etykieta']
    zapisz('reguly.json', REG)
    print('reguły:', len(nowe), 'zmian;', '; '.join(nowe[:30]))
