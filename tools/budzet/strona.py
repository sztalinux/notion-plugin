#!/usr/bin/env python3
"""Buduje stronę decyzji budżetu: miesiace/*.json (folder danych) -> <dist>/index.html + <dist>/dane.js.

    python3 tools/budzet/strona.py [--dist <folder>]

Domyślny dist: <dane>/strona. Publikacja (Artifact): file_path=<dist>/index.html, files={"dane.js": "<dist>/dane.js"} –
zawsze oba; plik musi leżeć w folderze roboczym sesji albo w jej scratchpadzie (wtedy podaj --dist tam).
Opisy z wyciągów idą na stronę bez końcówek kart i numerów kont."""
import argparse, json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import DANE  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--dist', default=str(DANE / 'strona'))
DIST = Path(ap.parse_args().dist)
DIST.mkdir(parents=True, exist_ok=True)


def czysc(opis):
    o = re.sub(r',?\s*\w{3} CARD: MASTERCARD \*\d+', '', opis)
    o = re.sub(r'CARD: MASTERCARD \*\d*', '', o)
    o = re.sub(r'\b[\dA-F-]{24,}\b', '…', o, flags=re.I)
    o = re.sub(r'\d{10,}', '…', o)
    o = re.sub(r'(Od|Do): ?\S+', '', o)
    return re.sub(r'\s+', ' ', o).strip(' ,')


miesiace = {}
for p in sorted((DANE / 'miesiace').glob('20??-??.json')):
    d = json.loads(p.read_text(encoding='utf-8'))
    for k in ('decyzje', 'pominiete', 'juz'):
        for x in d[k]:
            x['opis'] = czysc(x['opis'])
            for c in x.get('cele') or []:
                c['opis'] = czysc(c['opis'])
            if x.get('regula', '').startswith('BLIK P2P-WYCHODZACY '):
                x['regula'] = 'BLIK P2P'
    for w in d['wiersze']:
        w['opis'] = czysc(w['opis'])
    d.pop('auto', None)
    miesiace[d['miesiac']] = d
(DIST / 'dane.js').write_text('window.BUDZET = ' + json.dumps(dict(miesiace=miesiace), ensure_ascii=False, separators=(',', ':')) + ';\n',
                              encoding='utf-8')
shutil.copy(Path(__file__).with_name('strona.html'), DIST / 'index.html')
print('miesiące:', ', '.join(miesiace), '| dane.js', (DIST / 'dane.js').stat().st_size, 'B |', DIST)
