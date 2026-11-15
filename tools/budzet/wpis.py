#!/usr/bin/env python3
"""Wydatek z wpisu (Dziennik, rozmowa) -> plik miesiąca budżetu domowego `listy/RRRR-MM-wpisy.jsonl` w folderze danych.
Nic nie zapisuje do arkusza: zamknięcie miesiąca (`importuj.py`) czyta plik jak listę – gotówka i konta bez wyciągu to
wiersze, konta z wyciągiem to podpowiedź kategorii i opisu dla transakcji z wyciągu. Procedura: plugins/ja/skills/budzet.

    python3 tools/budzet/wpis.py dodaj "<kwota>[, konto][, osoba], <kategoria>[, opis]" --data RRRR-MM-DD [--id ID] [--budowa ID]
    python3 tools/budzet/wpis.py lista RRRR-MM
    python3 tools/budzet/wpis.py usun RRRR-MM ID

Skróty kont i osób: ustawienia.json (`skroty_kont`, `skroty_osob`); kategorii: reguly.json (`skroty`). Bez konta – gotówka;
gotówka i konta drugiej osoby zawsze na drugą osobę. Kwota z „+” = wpływ, działanie („5300-580”) zostaje formułą.
--id: ID wpisu (blok/strona w Notion, strona 💸) – ten sam ID nadpisuje zapis zamiast dodawać drugi.
--budowa: ID strony w kolejce 💸 – wydatek na budowę, już w kosztorysie.
"""
import argparse, hashlib, json, re, sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import DANE, U, kw, opcja, wczytaj  # noqa: E402

KWOTA = re.compile(r'^(\+?)\s*(\d[\d.]*(?:\s*[+-]\s*\d[\d.]*)*)$')


def konta_drugiej():
    return set(U.get('konta_list', {}).values()) | {U.get('gotowka_konto', 'Gotówka')}


def parsuj(tekst, skroty=None):
    """'200, pra, o, zam, opis' -> dict (kwota ujemna = wydatek). Błąd formatu -> ValueError z powodem."""
    skroty = skroty if skroty is not None else wczytaj('reguly.json', {}).get('skroty', {})
    sk_konta = {k.lower(): v for k, v in U.get('skroty_kont', {}).items()}
    sk_osoby = {k.lower(): v for k, v in U.get('skroty_osob', {}).items()}
    pola = [p.strip() for p in tekst.split(',')]
    if len(pola) > 1 and re.fullmatch(r'\d{1,2}', pola[1]) and re.fullmatch(r'\+?\d+', pola[0]):
        pola[:2] = [pola[0] + '.' + pola[1]]  # „212,54, zam” – przecinek dziesiętny
    m = KWOTA.match(pola[0].replace(' ', ''))
    if not m:
        raise ValueError(f'pierwsze pole to nie kwota: „{pola[0]}”')
    liczby = [-kw(x) if z == '-' else kw(x) for z, x in re.findall(r'([+-]?)(\d[\d.]*)', m.group(2))]
    suma = round(sum(liczby), 2)
    i, konto, osoba = 1, None, None
    if i < len(pola) and pola[i].lower() in sk_konta:
        konto, i = sk_konta[pola[i].lower()], i + 1
    if i < len(pola) and pola[i].lower() in sk_osoby:
        osoba, i = sk_osoby[pola[i].lower()], i + 1
    kod = pola[i].lower() if i < len(pola) else ''
    opis = ', '.join(p for p in pola[i + 1:] if p)
    konto = konto or U.get('gotowka_konto', 'Gotówka')
    if konto in konta_drugiej():
        osoba = U.get('osoba_listy', osoba)
    elif not osoba:
        osoba = U.get('osoba_wyciagi', '')
    kat = skroty.get(kod)
    o = opcja(*kat) if kat else None
    return dict(kwota=suma if m.group(1) else -suma, skladniki=liczby if len(liczby) > 1 else None, konto=konto, osoba=osoba,
                kod=kod, typ=o['typ'] if o else '', kat=o['kat'] if o else '', pod=o['pod'] if o else '', opis=opis)


def plik(mies):
    return DANE / 'listy' / f'{mies}-wpisy.jsonl'


def czytaj(mies):
    p = plik(mies)
    return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()] if p.exists() else []


def zapisz_wszystkie(mies, wpisy):
    p = plik(mies)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(''.join(json.dumps(w, ensure_ascii=False) + '\n' for w in wpisy), encoding='utf-8')


def opis_wpisu(w):
    kat = f"{w['kat']} › {w['pod']}" if w['pod'] else (w['kat'] or f"nieznany skrót „{w['kod']}”")
    return f"{w['data']} {w['kwota']:+.2f} {w['konto']} {w['osoba']} {kat}" + (f" – {w['opis']}" if w['opis'] else '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('akcja', choices=('dodaj', 'lista', 'usun'))
    ap.add_argument('arg')
    ap.add_argument('id_usun', nargs='?')
    ap.add_argument('--data')
    ap.add_argument('--id')
    ap.add_argument('--budowa', default='')
    A = ap.parse_args()
    if A.akcja == 'lista':
        ws = czytaj(A.arg)
        for w in ws:
            print(w['id'], opis_wpisu(w))
        print(f'{A.arg}: {len(ws)} wpisów')
        return
    if A.akcja == 'usun':
        ws = czytaj(A.arg)
        reszta = [w for w in ws if w['id'] not in (A.id_usun, 'w' + str(A.id_usun))]
        zapisz_wszystkie(A.arg, reszta)
        print('usunięto' if len(reszta) < len(ws) else f'✗ brak wpisu {A.id_usun}')
        return
    d = A.data or date.today().isoformat()
    try:
        date.fromisoformat(d)
        w = parsuj(A.arg)
    except ValueError as e:
        print(f'✗ {e}')
        sys.exit(1)
    w = dict(id='w' + (A.id or hashlib.sha1(f'{d}|{A.arg}'.encode()).hexdigest()[:10]), data=d, tekst=A.arg, **w,
             budowa=A.budowa, dodano=datetime.now().strftime('%Y-%m-%d %H:%M'))
    mies = d[:7]
    ws = czytaj(mies)
    stary = next((x for x in ws if x['id'] == w['id']), None)
    ws = [x for x in ws if x['id'] != w['id']] + [w]
    zapisz_wszystkie(mies, ws)
    print(('zaktualizowano: ' if stary else 'dopisano: ') + opis_wpisu(w))
    if not w['kat']:
        print(f"uwaga: nieznany skrót kategorii „{w['kod']}” – przy zamknięciu miesiąca będzie pytanie na stronie decyzji")


if __name__ == '__main__':
    main()
