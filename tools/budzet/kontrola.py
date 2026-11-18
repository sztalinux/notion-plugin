#!/usr/bin/env python3
"""Kontrola zakładki Transakcje przed podsumowaniem miesiąca (procedura budzet, etap 2). Nic nie zmienia w arkuszu.

    python3 tools/budzet/kontrola.py --arkusz miesiace/transakcje-<data>.json [--rok RRRR]

Wejście: get_values Transakcje!A1:O (zapisany jak przy imporcie). Wypisuje problemy z numerem wiersza – każdy z nich psuje
sumy zakładki roku albo przychód drugiej osoby liczony z sald:
  kwota jako tekst albo pusta · ten sam wiersz dwa razy · wydatek z konta drugiej osoby bez jej Osoby (i odwrotnie) ·
  przychód bez Osoby · przelew z Osobą · zła para kategoria–podkategoria · wiersz przychodu z sald brak / dwa razy w miesiącu.
Kod wyjścia 0 także przy problemach (to lista do przejrzenia, nie błąd skryptu).
"""
import argparse, json, sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import DANE, DRZEWO, U, kw  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--arkusz', required=True)
ap.add_argument('--rok', type=int)
A = ap.parse_args()
p = Path(A.arkusz if Path(A.arkusz).is_absolute() else DANE / A.arkusz)
wiersze = json.loads(p.read_text(encoding='utf-8'))['values'][1:]

DRUGA = U.get('osoba_listy', '')
KONTA_DRUGIEJ = set(U.get('konta_list', {}).values()) | {U.get('gotowka_konto', 'Gotówka')}
KONTA_A = {U.get('konto_zen'), U.get('konto_mbank')} - {None}
PS = U.get('przychod_z_sald', {}).get('kategoria')
problemy = defaultdict(list)
klucze = Counter()
ps_mies = Counter()
rows = []
for i, r in enumerate(wiersze, start=2):
    r = r + [''] * (15 - len(r))
    data, _, typ, kwota, kat, pod, konto, osoba = r[:8]
    if not data:
        continue
    try:
        d = datetime.strptime(data, '%d-%b-%Y').date()
    except ValueError:
        problemy['data nie jest datą'].append(f'{i}: {data}')
        continue
    if A.rok and d.year != A.rok:
        continue
    rows.append((i, r))
    if not kwota.strip():
        problemy['pusta kwota'].append(f'{i}: {data} {typ} {kat}')
    elif 'zł' not in kwota:
        problemy['kwota jako tekst (nie wchodzi do sum) – wpisz liczbę'].append(f'{i}: „{kwota}” {kat}')
    klucze[(data, typ, kwota, kat, pod, konto, osoba, r[8], r[14])] += 1  # O: dwa wpisy o tej samej treści to nie duplikat
    if typ in ('Wydatek', 'Koszt', 'Inwestycja'):
        if konto in KONTA_DRUGIEJ and osoba != DRUGA:
            problemy['wydatek z konta drugiej osoby bez jej Osoby (zaniża jej przychód)'].append(f'{i}: {data} {konto} {kat} Osoba „{osoba}”')
        elif konto in KONTA_A and osoba == DRUGA:
            problemy['wydatek z konta z wyciągu przypisany drugiej osobie'].append(f'{i}: {data} {konto} {kat}')
        elif not osoba:
            problemy['wydatek bez Osoby (nie wchodzi do wierszy osób w zakładce roku)'].append(f'{i}: {data} {konto} {kat}')
    if typ == 'Przychód' and kat != PS:
        if not osoba:
            problemy['przychód bez Osoby (wpływ na konto drugiej osoby liczy się wtedy podwójnie)'].append(f'{i}: {data} {kat}')
        elif konto in KONTA_DRUGIEJ and osoba != DRUGA:
            problemy['przychód na koncie drugiej osoby z inną Osobą'].append(f'{i}: {data} {konto} {kat}')
    if typ == 'Przelew' and osoba:
        problemy['przelew z Osobą (przelewy liczą się tylko przez swoje wiersze)'].append(f'{i}: {data} {kat} Osoba „{osoba}”')
    if kat == PS:
        ps_mies[(d.year, d.month)] += 1
    if typ in DRZEWO and kat:
        podk = DRZEWO[typ].get(kat)
        if podk is None:
            problemy['kategoria spoza zakładki Kategorie'].append(f'{i}: {typ} › {kat}')
        elif pod and isinstance(podk, list) and pod not in podk:
            problemy['zła para kategoria–podkategoria'].append(f'{i}: {kat} › {pod}')
    elif typ and typ not in DRZEWO:
        problemy['nieznany Typ'].append(f'{i}: {typ}')

for k, n in klucze.items():
    if n > 1:
        problemy['ten sam wiersz kilka razy (duplikat?)'].append(f'{n}× {k[0]} {k[1]} {k[2]} {k[3]} {k[5]}')
if PS:
    mies = sorted({(datetime.strptime(r[0], '%d-%b-%Y').date().year, datetime.strptime(r[0], '%d-%b-%Y').date().month)
                   for _, r in rows})
    for ym in mies[:-1]:  # bieżący (ostatni) miesiąc jeszcze otwarty
        if ps_mies[ym] != 1:
            problemy[f'wiersz {PS}: powinien być dokładnie jeden w miesiącu'].append(f'{ym[0]}-{ym[1]:02d}: {ps_mies[ym]}')

if not problemy:
    print(f'kontrola: {len(rows)} wierszy, bez problemów')
for tytul, lista in problemy.items():
    print(f'✗ {tytul}: {len(lista)}')
    for x in lista[:15]:
        print('   ', x)
    if len(lista) > 15:
        print(f'    … i {len(lista) - 15} więcej')
