#!/usr/bin/env python3
"""Wydatek z wpisu (Dziennik, rozmowa) -> plik miesiąca budżetu domowego `listy/RRRR-MM-wpisy.jsonl` w folderze danych.
Sam skrypt nie łączy się z siecią. Zapisy z datą od `ARKUSZ_OD` (wspolne.py, 1.12.2026) wysyła do arkusza
`arkusz_budzetu.py sync` (automat po przebiegu, w Claude Code agent zaraz po zapisie) – znacznik wysyłki w polu `arkusz`.
Starsze zapisy i te, których skrypt arkusza nie przyjął, dopisuje zamknięcie miesiąca (`importuj.py`) po ID.
Procedura: plugins/ja/skills/budzet.

    python3 tools/budzet/wpis.py dodaj "<kwota>[, konto][, osoba], <kategoria>[, opis]" --data RRRR-MM-DD [--id ID] [--budowa ID] [--gotowka]
    python3 tools/budzet/wpis.py lista RRRR-MM
    python3 tools/budzet/wpis.py usun RRRR-MM ID

Skróty kont i osób: ustawienia.json (`skroty_kont`, `skroty_osob`); kategorii: reguly.json (`skroty`). Bez konta – gotówka;
gotówka i konta drugiej osoby zawsze na drugą osobę. Kwota z „+” = wpływ, działanie („5300-580”) zostaje formułą.
--id: ID wpisu (blok/strona w Notion, strona 💸) – ten sam ID nadpisuje zapis zamiast dodawać drugi (także gdy zmieni się
miesiąc daty); znacznik wysyłki zostaje, więc synchronizacja poprawi wiersz w arkuszu zamiast dopisać drugi.
--budowa: ID strony w kolejce 💸 – wydatek na budowę, już w kosztorysie. Bez konta w treści – gotówka (brak informacji = gotówka).
--gotowka: wymusza gotówkę (strona 💸 ze Sposobem = Gotówka), także przy --budowa.
usun: zapis już wysłany do arkusza dostaje znak `usuniety` – synchronizacja usuwa jego wiersz i dopiero wtedy zapis z pliku.
Pole `grupa` – części jednego paragonu (zapisuje je paragon.py); zamknięcie miesiąca paruje płatność z wyciągu z sumą grupy.
usun z ID części albo ID wpisu paragonu usuwa cały paragon.
"""
import argparse, hashlib, re, sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import (U, blokada_wpisow, czytaj_wpisy, data_iso, kw, miesiace_wpisow, opcja, wczytaj,  # noqa: E402
                     zapisz_wpisy)

KWOTA = re.compile(r'^(\+?)\s*(\d[\d.]*(?:\s*[+-]\s*\d[\d.]*)*)$')
WALUTA = re.compile(r'^(.*\d)\s*(?:zł|zl|pln)$', re.I)


def konta_drugiej():
    return set(U.get('konta_list', {}).values()) | {U.get('gotowka_konto', 'Gotówka')}


def bez_waluty(pole):
    m = WALUTA.match(pole)
    return m.group(1) if m else pole


def pole_kwoty(pole):
    """Pierwsze pole: bez „zł”, separator tysięcy („1 200”) zdjęty; inna spacja między cyframi -> ValueError."""
    s = re.sub(r'(?<=\d)[   ](?=\d{3}(?!\d))', '', bez_waluty(pole))
    if re.search(r'\d[\s  ]+\d', s):
        raise ValueError(f'niejednoznaczna kwota „{pole}”')
    return s


def parsuj(tekst, skroty=None, wymus_konto=None):
    """'200, pra, o, zam, opis' -> dict (kwota ujemna = wydatek). Błąd formatu -> ValueError z powodem.
    wymus_konto – zawsze to konto (bez konta w treści – gotówka)."""
    skroty = skroty if skroty is not None else wczytaj('reguly.json', {}).get('skroty', {})
    sk_konta = {k.lower(): v for k, v in U.get('skroty_kont', {}).items()}
    sk_osoby = {k.lower(): v for k, v in U.get('skroty_osob', {}).items()}
    pola = [p.strip() for p in tekst.split(',')]
    pola[0] = pole_kwoty(pola[0])
    if len(pola) > 1 and re.fullmatch(r'\d{1,2}', bez_waluty(pola[1])) and re.fullmatch(r'\+?\d+', pola[0]):
        pola[:2] = [pola[0] + '.' + bez_waluty(pola[1])]  # „212,54, zam” – przecinek dziesiętny
    if re.search(r'[.,]\d{3}', pola[0]):  # „1.200,50” – kropka tysięcy albo trzy cyfry po przecinku
        raise ValueError(f'niejednoznaczna kwota „{pola[0]}” – zapisz bez kropki tysięcy')
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
    if re.fullmatch(r'[\d\s.,]+(?:zł|zl|pln)?', kod):  # „1,200.50, zak” – reszta kwoty wzięta za skrót kategorii
        raise ValueError(f'niejednoznaczna kwota – „{kod}” wygląda na część kwoty')
    opis = ', '.join(p for p in pola[i + 1:] if p)
    konto = wymus_konto or konto or U.get('gotowka_konto', 'Gotówka')
    if konto in konta_drugiej():
        osoba = U.get('osoba_listy', osoba)
    elif not osoba:
        osoba = U.get('osoba_wyciagi', '')
    kat = skroty.get(kod)
    o = opcja(*kat) if kat else None
    return dict(kwota=suma if m.group(1) else -suma, skladniki=liczby if len(liczby) > 1 else None, konto=konto, osoba=osoba,
                kod=kod, typ=o['typ'] if o else '', kat=o['kat'] if o else '', pod=o['pod'] if o else '', opis=opis)


def znajdz(id_):
    """(miesiąc, zapis) z dowolnego pliku miesiąca – także usunięty – albo (None, None)."""
    for m in miesiace_wpisow():
        for w in czytaj_wpisy(m, z_usunietymi=True):
            if w['id'] == id_:
                return m, w
    return None, None


def opis_wpisu(w):
    kat = f"{w['kat']} › {w['pod']}" if w['pod'] else (w['kat'] or f"nieznany skrót „{w['kod']}”")
    return (f"{w['data']} {w['kwota']:+.2f} {w['konto']} {w['osoba']} {kat}" + (' [budowa]' if w.get('budowa') else '')
            + (f" – {w['opis']}" if w['opis'] else ''))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('akcja', choices=('dodaj', 'lista', 'usun'))
    ap.add_argument('arg')
    ap.add_argument('id_usun', nargs='?')
    ap.add_argument('--data')
    ap.add_argument('--id')
    ap.add_argument('--budowa', default='')
    ap.add_argument('--gotowka', action='store_true', help='wymuś gotówkę (Sposób = Gotówka na stronie 💸)')
    A = ap.parse_args()
    if A.akcja == 'lista':
        ws = czytaj_wpisy(A.arg, z_usunietymi=True)
        for w in ws:
            print(w['id'], opis_wpisu(w) + (' [usunięty – czeka na usunięcie z arkusza]' if w.get('usuniety') else
                                             ' [w arkuszu]' if w.get('arkusz') else ''))
        print(f"{A.arg}: {sum(1 for w in ws if not w.get('usuniety'))} wpisów")
        return
    if A.akcja == 'usun':
        with blokada_wpisow():
            ws = czytaj_wpisy(A.arg, z_usunietymi=True)
            ids = (A.id_usun, 'w' + str(A.id_usun))
            trafione = [w for w in ws if (w['id'] in ids or w.get('grupa') in ids) and not w.get('usuniety')]
            if not trafione:
                print(f'✗ brak wpisu {A.id_usun}')
                return
            # wszystko, co pasuje (zwykły wpis i paragon z tym ID); część paragonu – znika cały paragon, nie jedna kategoria
            grupy = {w['grupa'] for w in trafione if w.get('grupa')}
            cele = [w for w in ws if not w.get('usuniety') and (w in trafione or w.get('grupa') in grupy)]
            teraz = datetime.now().strftime('%Y-%m-%d %H:%M')
            for w in cele:
                if w.get('arkusz'):
                    w['usuniety'] = teraz
            zapisz_wpisy(A.arg, [w for w in ws if not (w in cele and not w.get('arkusz'))])
            print(f'usunięto ({len(cele)})' + (' – wiersze w arkuszu znikną przy synchronizacji (arkusz_budzetu.py sync)'
                                              if any(w.get('arkusz') for w in cele) else ''))
        return
    d = A.data or date.today().isoformat()
    try:
        data_iso(d)
        gotowka = U.get('gotowka_konto', 'Gotówka')
        w = parsuj(A.arg, wymus_konto=gotowka if A.gotowka else None)
    except ValueError as e:
        print(f'✗ {e}')
        sys.exit(1)
    w = dict(id='w' + (A.id or hashlib.sha1(f'{d}|{A.arg}'.encode()).hexdigest()[:10]), data=d, tekst=A.arg, **w,
             budowa=A.budowa, dodano=datetime.now().strftime('%Y-%m-%d %H:%M'))
    mies = d[:7]
    with blokada_wpisow():
        if any(x.get('grupa') == w['id'] and not x.get('usuniety') for m in miesiace_wpisow() for x in czytaj_wpisy(m)):
            print(f"✗ ID {w['id']} należy do paragonu – zmień go przez paragon.py rozpisz (ten sam --id), nie wpis.py dodaj")
            sys.exit(1)
        m_stary, stary = znajdz(w['id'])
        if stary and stary.get('arkusz'):
            w['arkusz'] = stary['arkusz']  # wiersz już w arkuszu – synchronizacja go poprawi, nie dopisze drugiego
        if m_stary and m_stary != mies:
            zapisz_wpisy(m_stary, [x for x in czytaj_wpisy(m_stary, z_usunietymi=True) if x['id'] != w['id']])
        zapisz_wpisy(mies, [x for x in czytaj_wpisy(mies, z_usunietymi=True) if x['id'] != w['id']] + [w])
    print(('zaktualizowano: ' if stary and not stary.get('usuniety') else 'dopisano: ') + opis_wpisu(w))
    if not w['kat']:
        print(f"uwaga: nieznany skrót kategorii „{w['kod']}” – przy zamknięciu miesiąca będzie pytanie na stronie decyzji")


if __name__ == '__main__':
    main()
