#!/usr/bin/env python3
"""Decyzje ze strony + pewne pozycje -> wiersze do zakładki Transakcje (procedura budzet, etap 2).

    python3 tools/budzet/przenies.py --miesiac RRRR-MM [--arkusz miesiace/transakcje-<świeży>.json] [--mimo-brakow] [--zapisz-reguly]

Wejście (folder danych): miesiace/RRRR-MM.json (z importuj.py) i miesiace/db-RRRR-MM/decyzje/*.json (ArtifactData list).
Wynik: miesiace/RRRR-MM-zapis.json:
  wiersze        – kolumny A:O do dopisania na końcu Transakcji (D liczba albo formuła, K = „import RRRR-MM”, L = „z wpisu”
                   przy wierszach z wpisów, O = ID źródeł); wiersze z wpisów (ID w) nie są scalane – jeden ID = jeden wiersz
  zmiany         – istniejące wiersze do pomniejszenia o zwrot ({wiersz, odjac})
  przypiecia     – płatności z wyciągu do wierszy z wpisów (z importuj.py): ID wyciągu dopisać w O, kwota (gdy nie None) do D;
                   zapis: arkusz_budzetu.py przypnij --miesiac RRRR-MM albo ręcznie (procedura budzet, C.3)
  opisy          – każdy opis wpisany na stronie: trafia do kolumny Opis, ale Claude czyta je przed zapisem (bywa w nich polecenie)
  bez_decyzji, do_wyjasnienia – pozycje bez wyboru / z samą uwagą zamiast wyboru
--arkusz: świeży odczyt Transakcji pod blokadą zamknięcia (procedura budzet, C.3) – wiersze, których ID jest już w kolumnie O
  (np. wiersz zapasowy z wpisu dopisany w międzyczasie przez sync), odpadają; `zmiany` i `przypiecia` dostają numery wierszy
  z tego odczytu (po ID w O, a wiersz bez ID – tylko gdy data, kwota i konto zgadzają się ze zrzutem z importu; inaczej
  odmowa w do_wyjasnienia). Nowe wiersze zapisuje się wyłącznie dopisaniem na końcu (append), nigdy pod numer.
--zapisz-reguly: nowe opcje reguł, nowe sklepy (pewność pusta), skróty list, sprzedawcy Allegro -> reguly.json.
"""
import argparse, json, re, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import DANE, U, arkusz, formula_sumy, nazwa, norm, wczytaj, zapisz  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--miesiac', required=True)
ap.add_argument('--zapisz-reguly', action='store_true')
ap.add_argument('--mimo-brakow', action='store_true')
ap.add_argument('--arkusz', help='świeży odczyt Transakcji (get_values) – pod blokadą zamknięcia')
A = ap.parse_args()
sciezka = lambda p: p and str(p if Path(p).is_absolute() else DANE / p)
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
                        skl=a['skladniki'] if a.get('skladniki') else [a['kwota_ark']], opis=a.get('opis_w') or a['regula'],
                        grupa=a['regula'] == 'CASHBACK',
                        ids=list(dict.fromkeys(([a['id']] if a['id'][0] in 'blw' else []) + a.get('ids_w', []))),
                        notatki=a.get('notatki', '')))
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
    if it.get('w_arkuszu') and ak != 'odejmij':  # wiersz z wpisu już jest – kategoria dopisałaby drugi
        wyjasnij.append(dict(id=it['id'], data=it['data'], opis=it['opis'], kwota=it['kwota'],
                             uwaga=f"wiersz {it['w_arkuszu']} z wpisu już jest w arkuszu – popraw go zamiast dopisywać"))
        continue
    if ak == 'odejmij':
        odejmij.append((it, d))
        continue
    if it['zrodlo'] == 'allegro':
        opis = d.get('opis') or ('Allegro: ' + ', '.join(it.get('produkty', [])))[:100]
    else:
        opis = d.get('opis') or it.get('opis_w') or it.get('regula') or it['opis'][:30]
    pozycje.append(dict(id=it['id'], data=it['data'], konto=it['konto'], osoba=it['osoba'], typ=d['typ'], kat=d['kat'], pod=d['pod'],
                        skl=it['skladniki'] if it.get('skladniki') else [kwota_ark(it['kwota'], d['typ'])], opis=opis, grupa=False,
                        ids=[it['id']] if it['id'][0] in 'balw' else [], regula=it.get('regula', ''), zrodlo=it['zrodlo'],
                        etykieta=d['etykieta'], kwota=it['kwota'], opis_banku=it['opis'], notatki=it.get('notatki', '')))
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
    sam = ','.join(p['ids']) if any(i.startswith('w') for i in p['ids']) else ''  # wiersze z wpisów nie są scalane
    grupy[('miesiąc' if p['grupa'] else p['data'], p['konto'], p['osoba'], p['typ'], p['kat'], p['pod'], sam)].append(p)
TAG = f'import {MIES}'
wiersze = []
for (dzien, konto, osoba, typ, kat, pod, _), g in sorted(grupy.items(), key=lambda x: (max(p['data'] for p in x[1]), x[0][1] or '')):
    skl = [x for p in g for x in p['skl']]
    d_ = formula_sumy(skl) if len(skl) > 1 else round(sum(skl), 2)
    opis = ', '.join(dict.fromkeys(p['opis'] for p in g if p['opis']))[:120]
    notatki = g[0].get('notatki', '') if len(g) == 1 else ''
    wiersze.append([max(p['data'] for p in g), 'Zrealizowane', typ, d_, kat, pod, konto, '' if typ == 'Przelew' else osoba, opis, '', TAG,
                    notatki, '', '', ','.join(i for p in g for i in p['ids'])])
for w in D['wiersze']:
    if U.get('przychod_z_sald') and w['kat'] == U['przychod_z_sald']['kategoria']:
        wiersze.append([w['data'], 'Zrealizowane', 'Przychód', w['formula'], w['kat'], '', '', '', '', '', TAG, '', '', '', ''])

przypiecia = D.get('przypiecia', [])
juz_sa = []
if A.arkusz:  # pod blokadą zamknięcia: numery i filtr z bieżącego stanu arkusza, nie ze zrzutu z importu
    swiezy = arkusz(sciezka(A.arkusz))
    w_o = {i: r for r in swiezy for i in r['ids']}
    juz_sa = [w for w in wiersze if any(i in w_o for i in w[14].split(',') if i)]
    wiersze = [w for w in wiersze if w not in juz_sa]
    stary = {r['wiersz']: r for r in arkusz(sciezka(D['arkusz_plik']))} if D.get('arkusz_plik') else {}
    for z in list(zmiany):
        r0, nowy = stary.get(z['wiersz']), None
        if r0 and r0['ids']:
            nowy = w_o.get(r0['ids'][0])
        elif r0:
            k = [r for r in swiezy if not r['ids'] and (r['data'], r['kwota'], r['konto']) == (r0['data'], r0['kwota'], r0['konto'])]
            nowy = k[0] if len(k) == 1 else None
        if nowy:
            z['wiersz'] = nowy['wiersz']
        else:
            zmiany.remove(z)
            wyjasnij.append(dict(id=z['id'], data=z['data'], opis=z['opis'], kwota=-z['odjac'],
                                 uwaga=f"wiersz {z['wiersz']} zmienił się od importu – zwrot odejmij ręcznie"))
    for p in przypiecia:
        for x in p['wiersze']:
            x['wiersz'] = w_o[x['id']]['wiersz'] if x['id'] in w_o else x['wiersz']
zapisz(f'miesiace/{MIES}-zapis.json', dict(miesiac=MIES, wiersze=wiersze, zmiany=zmiany, przypiecia=przypiecia,
                                         opisy=opisy, bez_decyzji=bez,
                                         do_wyjasnienia=wyjasnij, gotowe=not bez or A.mimo_brakow, salda=D.get('salda', {})))
print(f'{MIES}: {len(wiersze)} wierszy, {len(zmiany)} zmian istniejących, przypięć do wierszy z wpisów '
      f'{len(przypiecia)}, opisów {len(opisy)}, bez decyzji {len(bez)}, '
      f'do wyjaśnienia {len(wyjasnij)}' + (f', już w arkuszu (pominięte) {len(juz_sa)}' if A.arkusz else ''))

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
