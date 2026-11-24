#!/usr/bin/env python3
"""Import miesiąca do budżetu domowego: wyciągi (mBank, ZEN), zamówienia Allegro, lista wydatków drugiej osoby, wydatki
z wpisów (gotówka tylko z wpisów) -> propozycja wierszy i decyzje dla strony. Nic nie zapisuje do arkusza.
Procedura: plugins/ja/skills/budzet.

    python3 tools/budzet/importuj.py --miesiac RRRR-MM --arkusz miesiace/transakcje-<data>.json \
        [--zen wyciagi/zen.csv] [--mbank wyciagi/mbank.csv] [--allegro listy/allegro-<data>.json] \
        [--lista listy/RRRR-MM-lista.txt] [--wpisy listy/RRRR-MM-wpisy.jsonl] [--salda-wpisane]

Ścieżki względne liczą się od folderu danych (wspolne.DANE). Wpisy (wpis.py) czyta też bez --wpisy, jeśli plik miesiąca istnieje.
Wpis z karty (konto z wyciągiem) paruje się z płatnością do złotówki różnicy, ±4 dni, także przez przełom miesiąca (końcówka poprzedniego
i początek następnego pliku wpisów). Wpis już w arkuszu (ID w kolumnie O) nie daje nowego wiersza: płatność przypina się do
jego wiersza (`przypiecia` – ID wyciągu do kolumny O, kwota z wyciągu do D). Wpis bez pary z ostatnich dni miesiąca, gdy
wyciąg jeszcze ich nie obejmuje, czeka (pominiete) – rozstrzygnie import kolejnego miesiąca. Wiersze z wpisów (ID z prefiksem
w) nie liczą się do „wpisane ręcznie do dnia X” i nie są scalane. Pole `grupa` zapisu łączy części jednej płatności (paragon,
paragon.py): płatność z wyciągu = suma grupy przypina się do wszystkich części (różnica na największej); pozycja listy drugiej
osoby = suma paragonu na tym samym koncie -> pominięta, kwota bliska sumie (do pięciu złotych) -> decyzja, równa jednej części
-> wchodzi (chyba że jest też bliska sumie – wtedy decyzja).
Wynik: miesiace/RRRR-MM.json – wiersze (pewne, po scaleniu), auto, decyzje (strona), pominiete, juz (z numerem wiersza),
przypiecia, braki, salda.
"""
import argparse, hashlib, json, re, statistics, sys
from calendar import monthrange
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import (DANE, DRZEWO, U, arkusz, czytaj_jsonl, czytaj_wpisy, indeks_id, kw, kwota_pozycji, nazwa, norm, notatka_wpisu,  # noqa: E402
                     opcja, rozbij, skladniki_arkusza, wczytaj, wyciagi, z_wpisu, zapisz)

ap = argparse.ArgumentParser()
for a in ('miesiac', 'arkusz'):
    ap.add_argument('--' + a, required=True)
for a in ('zen', 'mbank', 'allegro', 'lista', 'wpisy'):
    ap.add_argument('--' + a)
ap.add_argument('--salda-wpisane', action='store_true', help='salda drugiej osoby są już w zakładce Konta')
A = ap.parse_args()
sciezka = lambda p: p and str(p if Path(p).is_absolute() else DANE / p)
for a in ('arkusz', 'allegro', 'lista'):  # podana ścieżka bez pliku (literówka) – stop, nie cichy brak danych
    if getattr(A, a) and not Path(sciezka(getattr(A, a))).exists():
        raise SystemExit(f'✗ --{a}: brak pliku {sciezka(getattr(A, a))}')
MIES = A.miesiac
R, M = map(int, MIES.split('-'))
KONIEC = date(R, M, monthrange(R, M)[1])

ark = arkusz(sciezka(A.arkusz))
for r in ark:  # miesiąc wiersza z daty (A), nie z kolumny M – pusta albo nieprzeciągnięta formuła M nie wyklucza wiersza
    if r['data']:
        r['mies'] = r['data'].strftime('%Y-%m')
bank = wyciagi(sciezka(A.zen), sciezka(A.mbank))
KONTA_A = (U.get('konto_zen'), U.get('konto_mbank'))


def wiersz_info(r):
    return dict(wiersz=r['wiersz'], data=r['data'].isoformat() if r['data'] else '', kwota=r['kwota'], konto=r['konto'],
                kategoria=f"{r['kat']} › {r['pod']}" if r['pod'] else r['kat'], typ=r['typ'])


# ---------- dopasowanie do arkusza (wszystkie miesiące): ID importu, 1:1, potem suma 2–4 z ±7 dni
def znak(r):
    return {'Przychód': 1, 'Przelew': 0}.get(r['typ'], -1)


def pasuje(r, t):
    z = znak(r)
    return z == 0 or (z > 0) == (t['kwota'] > 0)


para = {}
po_id = indeks_id(ark)
for t in bank:
    if t['id'] in po_id:
        para[t['id']] = (po_id[t['id']], 'zaimportowane wcześniej')
        po_id[t['id']]['uzyty'] = True

# ---------- wpisy (wpis.py); karty: para z płatnością do złotówki różnicy, ±4 dni, także przez przełom miesiąca. Wpis, który ma już
# wiersz w arkuszu (ID w w kolumnie O), paruje się przed wierszami ręcznymi (ma pierwszeństwo, a do „wpisane ręcznie do dnia X”
# się nie liczy); wpis tylko w pliku – dopiero po nich, jak przed POM-29: płatność zajęta przez ręczny wiersz = wpis już w arkuszu
PRZELOM = 4
POCZ = date(R, M, 1)
POPRZ = f'{R - (M == 1)}-{(M - 2) % 12 + 1:02d}'
NAST = f'{R + (M == 12)}-{M % 12 + 1:02d}'
if A.wpisy:
    pw = Path(sciezka(A.wpisy))
    WPISY = [w for w in czytaj_jsonl(pw) if not w.get('usuniety')] if pw.exists() else []
else:
    WPISY = czytaj_wpisy(MIES)
dzien_wpisu = lambda w: date.fromisoformat(w['data'])
SASIEDNIE = ([w for w in czytaj_wpisy(POPRZ) if dzien_wpisu(w) >= POCZ - timedelta(days=PRZELOM)]
             + [w for w in czytaj_wpisy(NAST) if dzien_wpisu(w) <= KONIEC + timedelta(days=PRZELOM)])
def kierunek_wpisu(w):
    """Kwota wpisu ze znakiem przepływu: przychód to wpływ także zapisany bez „+” (w arkuszu i tak wartość bezwzględna)."""
    return abs(w['kwota']) if w['typ'] == 'Przychód' else w['kwota']


czesci = defaultdict(list)
for w in WPISY + SASIEDNIE:
    if w['konto'] in KONTA_A:
        czesci[(w['konto'], w.get('grupa') or w['id'])].append(w)
jednostki = []
for (konto, _), cz in czesci.items():
    wr = [po_id.get(w['id']) for w in cz]
    if all(r and any(not i.startswith('w') for i in r['ids']) for r in wr):
        continue  # wszystkie części już przypięte do płatności przy wcześniejszym zamknięciu
    jednostki.append(dict(konto=konto, czesci=cz, wiersze=wr, kwota=round(sum(kierunek_wpisu(w) for w in cz), 2),
                          data=min(dzien_wpisu(w) for w in cz)))


def kandydaci_wpisu(u, wolne):
    return [t for t in bank if (t['id'] not in para) == wolne and not t.get('jednostka') and t['konto'] == u['konto']
            and (t['kwota'] > 0) == (u['kwota'] > 0) and abs(abs(t['kwota']) - abs(u['kwota'])) <= 1.0
            and abs((t['data'] - u['data']).days) <= PRZELOM]


def najblizsza(u, k):
    return min(k, key=lambda t: (abs(abs(t['kwota']) - abs(u['kwota'])), abs((t['data'] - u['data']).days)))


def paruj_wpisy(z_wierszem):
    for u in sorted(jednostki, key=lambda u: u['data']):
        if bool(any(u['wiersze'])) != z_wierszem or u.get('t') or u.get('pokryty'):
            continue
        k = kandydaci_wpisu(u, True)
        if k:
            t = najblizsza(u, k)
            t['jednostka'], u['t'] = u, t
            if t['mies'] == MIES and z_wierszem:
                para[t['id']] = (next(r for r in u['wiersze'] if r), 'z wpisu – przypięte do wiersza')
        elif not z_wierszem:
            # płatność już w ręcznym wierszu (po ID, 1:1, ≈1:1, w sumie) – wpis jest w tym wierszu; wiersz innego wpisu się nie
            # liczy (wpis o podobnej kwocie bez wiersza idzie wtedy na stronę decyzji)
            k = [t for t in kandydaci_wpisu(u, False) if not z_wpisu(para[t['id']][0])]
            if k:
                t = najblizsza(u, k)
                t['jednostka'], u['pokryty'] = u, para[t['id']]


paruj_wpisy(True)

nasze = [r for r in ark if r['konto'] in KONTA_A and r['kwota'] is not None and not r.get('uzyty') and not z_wpisu(r)]
pozbank = defaultdict(list)
for t in bank:
    if t['id'] not in para and not t.get('jednostka'):
        pozbank[(t['konto'], t['mies'])].append(t)
        pozbank[t['konto']].append(t)
for r in nasze:
    k = [t for t in pozbank[(r['konto'], r['mies'])] if t['id'] not in para and abs(t['kwota']) == r['kwota'] and pasuje(r, t)]
    if k:
        t = min(k, key=lambda t: abs((t['data'] - r['data']).days) if r['data'] else 0)
        para[t['id']] = (r, '1:1')
        r['uzyty'] = True
for r in nasze:  # ręcznie wpisane z zaokrągleniem albo literówką: do złotówki różnicy, ±3 dni, jedyny kandydat
    if r.get('uzyty') or r['typ'] == 'Przelew' or not r['data']:
        continue
    k = [t for t in pozbank[(r['konto'], r['mies'])] if t['id'] not in para and pasuje(r, t)
         and abs(abs(t['kwota']) - r['kwota']) <= 1.0 and abs((t['data'] - r['data']).days) <= 3]
    if len(k) == 1:
        para[k[0]['id']] = (r, f"≈1:1 (w arkuszu {r['kwota']:.2f})")
        r['uzyty'] = True
for r in nasze:
    if r.get('uzyty') or r['typ'] == 'Przelew' or not r['data']:
        continue
    k = sorted([t for t in pozbank[(r['konto'], r['mies'])] if t['id'] not in para and pasuje(r, t)
                and abs((t['data'] - r['data']).days) <= 7 and abs(t['kwota']) < r['kwota']],
               key=lambda t: abs((t['data'] - r['data']).days))[:16]
    for n in (2, 3, 4):
        c = next((c for c in combinations(k, n) if abs(sum(abs(t['kwota']) for t in c) - r['kwota']) < 0.005), None)
        if c:
            for t in c:
                para[t['id']] = (r, f'w sumie {n} płatności')
            r['uzyty'] = True
            break
# ręczny wiersz z końca miesiąca, płatność zaksięgowana 1.–3. dnia następnego (albo odwrotnie): 1:1 przez przełom – dopiero
# po wszystkich dopasowaniach w miesiącu i tylko gdy wyciąg konta obejmuje dzień wiersza (inaczej własna płatność wiersza
# mogła być poza plikiem, a płatność z sąsiedniego miesiąca to osobny zakup)
# Wiersz PO płatności (ręczny wiersz z 1.–3. dnia, płatność z końca poprzedniego miesiąca) – tylko gdy wyciąg sięga co
# najmniej 3 dni za dzień wiersza: inaczej własna płatność wiersza może być jeszcze poza plikiem, a ta z końca miesiąca to
# osobny zakup (wchodzi jak dotąd, nie znika jako „już w arkuszu”).
PRZELOM_1_1 = 3
POCZATEK_WYCIAGU, KONIEC_WYCIAGU = {}, {}
for t in bank:
    POCZATEK_WYCIAGU[t['konto']] = min(POCZATEK_WYCIAGU.get(t['konto'], t['data']), t['data'])
    KONIEC_WYCIAGU[t['konto']] = max(KONIEC_WYCIAGU.get(t['konto'], t['data']), t['data'])
for r in nasze:
    if r.get('uzyty') or not r['data'] or POCZATEK_WYCIAGU.get(r['konto'], r['data']) > r['data']:
        continue
    po_wierszu = KONIEC_WYCIAGU.get(r['konto'], r['data']) >= r['data'] + timedelta(days=PRZELOM_1_1)
    k = [t for t in pozbank[r['konto']] if t['id'] not in para and t['mies'] != r['mies'] and abs(t['kwota']) == r['kwota']
         and pasuje(r, t) and abs((t['data'] - r['data']).days) <= PRZELOM_1_1 and (t['data'] >= r['data'] or po_wierszu)]
    if k:
        t = min(k, key=lambda t: abs((t['data'] - r['data']).days))
        para[t['id']] = (r, '1:1 (przez przełom miesiąca)')
        r['uzyty'] = True

paruj_wpisy(False)

ostatnia = {}
for r in nasze:
    if r['mies'] == MIES and r['data']:
        ostatnia[r['konto']] = max(ostatnia.get(r['konto'], r['data']), r['data'])


def kandydaci(t, n=3):
    """Ręczne sumy w arkuszu, które mogą zawierać tę transakcję (to samo konto i miesiąc, ±3 dni, kwota ≥ minus złotówka, niewykorzystane)."""
    k = [r for r in nasze if r['konto'] == t['konto'] and r['data'] and r['mies'] == t['mies'] and not r.get('uzyty')
         and abs((r['data'] - t['data']).days) <= 3 and r['kwota'] >= abs(t['kwota']) - 1.0 and pasuje(r, t) and r['typ'] != 'Przelew']
    k.sort(key=lambda r: (abs((r['data'] - t['data']).days), r['kwota']))
    return [wiersz_info(r) for r in k[:n]]


# ---------- kosztorys budowy (żeby zakupy na budowę nie dublowały się z tym, co inwestor wpisuje od razu)
koszt = []
kj = (DANE.parent.parent / U['kosztorys_json']) if U.get('kosztorys_json') else None  # ścieżka względem folderu budowy
if kj and kj.exists():
    w = json.loads(kj.read_text(encoding='utf-8'))['arkusze'].get('Wydatki', [])
    h = next((i for i, r in enumerate(w) if r[:3] == ['Data', 'Status', 'Kwota (zł)']), None)
    for r in (w[h + 1:] if h is not None else []):
        try:
            koszt.append((kw(r[2]), r[0], r[4] if len(r) > 4 else ''))
        except (ValueError, IndexError):
            pass


def w_kosztorysie(kwota, data):
    def blisko(d):
        try:
            return abs((date.fromisoformat(str(d)[:10]) - date.fromisoformat(data)).days) <= 40
        except ValueError:
            return False
    k = [x for x in koszt if x[0] is not None and abs(abs(kwota) - x[0]) < 0.005 and blisko(x[1])]
    return f'w kosztorysie budowy: {k[0][1]} {k[0][2]}'.strip() if k else 'nie ma w kosztorysie budowy – dodać?'


# ---------- reguły
REG = wczytaj('reguly.json')
REGULY = REG['reguly']
SKROTY = {k: tuple(v) for k, v in REG.get('skroty', {}).items()}
for g in REGULY:
    g['nk'] = norm(g['klucz'])


def regula(t):
    o = t['no']
    k = [g for g in REGULY if g['kierunek'] == t['kier'] and g['nk'] in o]
    if 'CASHBACK' in o:
        k = [g for g in k if g['nk'] == 'CASHBACK'] or k
    return max(k, key=lambda g: len(g['nk'])) if k else None


def kwota_w_arkuszu(kwota, typ):
    if typ == 'Przelew':
        return abs(kwota)
    return round(kwota if typ == 'Przychód' else -kwota, 2)


INNE = opcja('Wydatek', 'Inne wydatki', 'Inne wydatki: inne')
auto, decyzje, pominiete, juz, braki = [], [], [], [], []
teraz = [t for t in bank if t['mies'] == MIES]
if not teraz:
    braki.append('wyciągi bankowe za ten miesiąc (mBank, ZEN)')


def baza(t):
    return dict(id=t['id'], data=t['data'].isoformat(), konto=t['konto'], osoba=t['osoba'], kwota=t['kwota'], opis=t['opis'])


def decyzja(b, **kw_):
    d = dict(b, zrodlo='wyciąg', pewnosc='Pytaj', regula='', propozycja=None, opcje=[], uwaga='', moze_juz=False, kandydaci=[])
    d.update(kw_)
    if not d.get('budowa') and (d['propozycja'] and d['propozycja']['kat'] == 'Dom' or any(o['kat'] == 'Dom' for o in d['opcje'][:1])):
        d['budowa'] = w_kosztorysie(d['kwota'], d['data'])
    decyzje.append(d)


def baza_wpisu(w):
    return dict(id=w['id'], data=w['data'], konto=w['konto'], osoba=w['osoba'], kwota=w['kwota'], opis=w['tekst'],
                skladniki=w.get('skladniki'), wpis=True, opis_w=w['opis'] or w['kod'], notatki=notatka_wpisu(w),
                **({'budowa': 'z wpisu – w kosztorysie budowy (💸)'} if w.get('budowa') else {}))


def wiersz_z_wpisu(w, kwota_ark=None, b=None):
    """Nowy wiersz z wpisu (zapas, gdy wpisu nie ma w arkuszu) albo decyzja, gdy skrót kategorii jest nieznany."""
    b = b or baza_wpisu(w)
    if not w['kat']:
        decyzja(b, zrodlo='lista', regula=w['kod'], uwaga='z wpisu – nieznany skrót kategorii')
        return
    ark = kwota_pozycji(w['kwota'], w['typ']) if kwota_ark is None else kwota_ark
    auto.append(dict(b, typ=w['typ'], kat=w['kat'], pod=w['pod'], regula=w['kod'], opis_w=w['opis'] or w['kod'],
                     kwota_ark=ark, skladniki=skladniki_arkusza(ark, w.get('skladniki')), ids_w=[w['id']],
                     notatki=notatka_wpisu(w), **({'budowa': 'z wpisu – w kosztorysie budowy (💸)'} if w.get('budowa') else {})))


def przypiecie(u, t):
    """Płatność t do części jednostki u -> (kwoty części w arkuszu, przypięcie do wierszy z wpisów albo None, gdy wierszy
    nie ma). Kwota z wyciągu wygrywa; różnicę grupy bierze największa część."""
    pary = list(zip(u['czesci'], u['wiersze']))
    kw_cz = {w['id']: (r['kwota'] if r and r['kwota'] is not None else kwota_pozycji(w['kwota'], w['typ'])) for w, r in pary}
    najw = max(u['czesci'], key=lambda w: abs(kw_cz[w['id']]))
    roznica = round(kwota_pozycji(t['kwota'], najw['typ']) - sum(kw_cz.values()), 2)
    if abs(roznica) >= 0.005:
        kw_cz[najw['id']] = round(kw_cz[najw['id']] + roznica, 2)
    w_ark = [(w, r) for w, r in pary if r]
    if not w_ark:
        return kw_cz, None
    return kw_cz, dict(id_wyciagu=t['id'], data=t['data'].isoformat(), konto=t['konto'], kwota_wyciagu=t['kwota'], opis=t['opis'],
                       wiersze=[dict(id=w['id'], wiersz=r['wiersz'],
                                     kwota=kw_cz[w['id']] if r['kwota'] is None or abs(kw_cz[w['id']] - r['kwota']) >= 0.005 else None)
                                for w, r in w_ark])


# --- wpisy z kart: przypięcie płatności do wierszy z wpisów, wiersz z wpisu bez arkusza (zapas), czekające, decyzje
ZASIEG = {}
for t in bank:
    ZASIEG[t['konto']] = max(ZASIEG.get(t['konto'], t['data']), t['data'])
przypiecia, obsluzone, czeka, niepelne = [], set(), 0, {}
# wpisy rozstrzygnięte bez ID w kolumnie O (ręczny wiersz, reguła Pomiń, decyzja Pomiń / Już) – zamknięcie oznacza je
# znacznikiem (arkusz_budzetu.py zamknij-wpisy), inaczej sync dopisałby je drugi raz
rozstrzygniete = set()
for u in sorted(jednostki, key=lambda u: u['data']):
    t, pary = u.get('t'), list(zip(u['czesci'], u['wiersze']))
    if u.get('pokryty'):
        r, sp = u['pokryty']
        rozstrzygniete.update(w['id'] for w, _ in pary)  # także część z sąsiedniego miesiąca – jest w tym ręcznym wierszu
        for w, _ in pary:
            if w['data'][:7] == MIES:
                pominiete.append(dict(baza_wpisu(w), powod=f"z wpisu – płatność już w arkuszu (wiersz {r['wiersz']}, {sp})"))
        continue
    # płatność z tego miesiąca albo – dla wpisu z końca poprzedniego, który tam czekał – z poprzedniego (nie zaimportowana)
    if t is not None and (t['mies'] == MIES or (t['mies'] == POPRZ and u['data'] < POCZ)):
        if not any(u['wiersze']) and len(pary) == 1 and t['mies'] == MIES:
            t['wpis'] = u['czesci'][0]  # wpisu nie ma w arkuszu: wiersz z płatności z kategorią wpisu (pętla wyciągu)
            continue
        kw_cz, p = przypiecie(u, t)
        if p:
            przypiecia.append(p)
        else:
            obsluzone.add(t['id'])
        for w, r in pary:
            if not r:
                wiersz_z_wpisu(w, kw_cz[w['id']], dict(baza(t), id=t['id'], wpis=True, opis_w=w['opis'] or w['kod'],
                                                       notatki=notatka_wpisu(w)))
        continue
    if t is not None:  # płatność w wyciągu innego miesiąca – do wiersza przypnie ją zamknięcie tamtego miesiąca
        for w, r in pary:
            if not r and w['data'][:7] == MIES:
                wiersz_z_wpisu(w)
        continue
    if u['data'] > KONIEC:
        continue  # początek następnego miesiąca bez pary w tym – rozstrzygnie import następnego
    pokryte = u['konto'] in ZASIEG and ZASIEG[u['konto']] >= u['data'] + timedelta(days=PRZELOM)
    if not pokryte and u['data'] >= KONIEC - timedelta(days=PRZELOM - 1):
        if u['konto'] not in ZASIEG or ZASIEG[u['konto']] < KONIEC:
            niepelne[u['konto']] = ZASIEG.get(u['konto'])
        for w, r in pary:  # ostatnie dni miesiąca: para może być w wyciągu kolejnego – import kolejnego wczyta ten plik
            czeka += 1
            pominiete.append(dict(baza_wpisu(w), powod='z wpisu – wyciąg nie obejmuje jeszcze 4 dni po wpisie; czeka na import '
                                                         'kolejnego miesiąca' + (f" (wiersz {r['wiersz']})" if r else '')))
        continue
    if not pokryte:
        niepelne[u['konto']] = ZASIEG.get(u['konto'])
    for w, r in pary:
        if r:
            decyzja(baza_wpisu(w), zrodlo='lista', regula=w['kod'], kandydaci=[wiersz_info(r)], w_arkuszu=r['wiersz'],
                    uwaga=f"wiersz {r['wiersz']} z wpisu – w wyciągu nie ma takiej płatności (do złotówki różnicy, ±4 dni); „Już w arkuszu” "
                          'zostawia wiersz; usunięcie albo inne konto opisz w polu opisu')
        else:
            prop = opcja(w['typ'], w['kat'], w['pod']) if w['kat'] else None
            decyzja(baza_wpisu(w), zrodlo='lista', regula=w['kod'], opcje=[prop] if prop else [],
                    uwaga='z wpisu – w wyciągu nie ma takiej płatności (±4 dni); inne konto albo inny miesiąc? Pomiń, jeśli to duplikat')

# wpisy z kart bez pary (inna kwota niż płatność o więcej niż złotówkę – napiwek, literówka): płatność z tego samego konta
# ±1 dzień nie wchodzi sama obok wpisu – decyzja bez propozycji (jawny wybór, nie „Zatwierdź propozycje”) z wierszem wpisu
# jako kandydatem. Tylko wpisy z zamykanego miesiąca (płatności też są z niego), więc okno nie sięga przez przełom: wpis
# z 1.–4. dnia następnego miesiąca nie ściąga płatności z 30., a wpis z końca poprzedniego – z 1. dnia. Wpis ze znacznikiem
# zamknięcia (rozstrzygnięty ręcznym wierszem) się nie liczy.
BEZ_PARY = [u for u in jednostki if not u.get('t') and not u.get('pokryty') and u['data'].strftime('%Y-%m') == MIES
            and not all((w.get('arkusz') or {}).get('zamkniecie') for w in u['czesci'])]


def wpis_bez_pary(t):
    k = [u for u in BEZ_PARY if u['konto'] == t['konto'] and (u['kwota'] > 0) == (t['kwota'] > 0)
         and abs((u['data'] - t['data']).days) <= 1]
    return min(k, key=lambda u: (abs((u['data'] - t['data']).days), abs(abs(u['kwota']) - abs(t['kwota'])))) if k else None


# --- pary pomijane razem (np. wydatek oddany tego samego dnia), przelewy partnera, pensja, zapowiedziane zwroty
for p in U.get('pary_pomijane', []):
    for t in teraz:
        if norm(p['wydatek']) in t['no'] and abs(t['kwota']) == p['kwota'] and t['id'] not in para:
            z = next((u for u in teraz if u['id'] not in para and norm(p['wplyw']) in u['no'] and u['kwota'] == p['kwota']
                      and u['data'] == t['data'] and not u.get('para')), None)
            if z:
                t['para'] = z['para'] = p['powod']
pp = U.get('przelew_partnera')
if pp:
    o2a_ark = round(sum(r['kwota'] or 0 for r in ark if r['mies'] == MIES and r['typ'] == 'Przelew' and r['kat'] == pp['kategoria']
                        and not r.get('uzyty')), 2)
    o2a_bank = [t for t in teraz if t['id'] not in para and norm(pp['klucz']) in t['no'] and t['kwota'] > 0]
    if o2a_bank and round(sum(t['kwota'] for t in o2a_bank), 2) <= o2a_ark + 0.005:
        for t in o2a_bank:
            t['para'] = f"przelew {pp['kategoria']} – suma miesiąca jest już w arkuszu"
pensja = [r for r in ark if r['mies'] == MIES and U.get('pensja') and r['kat'] == U['pensja']['kategoria']]
oczek = wczytaj('oczekujace.json', [])
for t in teraz:
    for o in oczek:
        if o['miesiac'] == MIES and norm(o['klucz']) in t['no'] and t['kier'] == o.get('kierunek', 'wpływ') and not o.get('uzyte'):
            t['para'] = o['powod']
            o['uzyte'] = True

# --- Allegro: zamówienia z listy są źródłem wydatków; płatności w banku tylko je opłacają
AL = U.get('allegro', {})
PLAT = tuple(norm(x) for x in AL.get('platnosci', []))
zam = []
if A.allegro:
    for z in json.loads(Path(sciezka(A.allegro)).read_text(encoding='utf-8'))['zamowienia']:
        if z['data'][:7] == MIES:
            z['id'] = 'a' + hashlib.sha1(f"{z['data']}|{z['sprzedawca']}|{z['suma']}|{'|'.join(z['produkty'])}".encode()).hexdigest()[:10]
            zam.append(z)
allegro_bank = [t for t in teraz if PLAT and any(k in t['no'] for k in PLAT) and 'CASHBACK' not in t['no']]
KARTA, PAY = norm(AL.get('karta_podarunkowa', '-')), norm(AL.get('pay', '-'))
if allegro_bank and not A.allegro:
    braki.append('lista zakupów z Allegro (Moje zakupy → zaznacz i skopiuj tekst)')
if A.allegro:
    otwarte = [z for z in zam if not z.get('zwrocony') and not z['pay']]
    for t in sorted([t for t in allegro_bank if t['kier'] == 'wypływ' and PAY not in t['no'] and KARTA not in t['no']],
                    key=lambda t: t['data']):
        k = [z for z in otwarte if not z.get('oplacone') and -1 <= (t['data'] - date.fromisoformat(z['data'])).days <= 5]
        c = next((c for n in (1, 2, 3, 4) for c in combinations(k, n) if abs(sum(z['suma'] for z in c) + t['kwota']) < 0.005), None)
        if c:
            for z in c:
                z['oplacone'] = t['id']
            t['allegro'] = 'zapłata za zamówienia: ' + ', '.join(f"{z['sprzedawca']} {z['suma']:.2f}" for z in c)
    for z in zam:
        if z.get('oplacone') and z['oplacone'] in para:
            z['juz'] = para[z['oplacone']]

for t in sorted(teraz, key=lambda t: (t['data'], t['konto'])):
    b = baza(t)
    if t['id'] in obsluzone:
        continue
    if t['id'] in para:
        r, sp = para[t['id']]
        juz.append(dict(b, sposob=sp, w=wiersz_info(r)))
        continue
    if t.get('para'):
        pominiete.append(dict(b, powod=t['para']))
        continue
    w = t.get('wpis')
    if w and not w['kat']:
        b['ids_w'] = [w['id']]  # wpis bez kategorii: jego ID idzie z płatnością (wiersz) albo do rozstrzygniętych (Pomiń)
    if w and w['kat']:
        auto.append(dict(b, typ=w['typ'], kat=w['kat'], pod=w['pod'], regula=w['kod'], opis_w=w['opis'] or w['kod'],
                         kwota_ark=kwota_w_arkuszu(t['kwota'], w['typ']), ids_w=[w['id']], notatki=notatka_wpisu(w),
                         **({'budowa': 'z wpisu – w kosztorysie budowy (💸)'} if w.get('budowa') else {})))
        continue
    g = regula(t)
    if g and g['pewnosc'] == 'Pomiń':
        pominiete.append(dict(b, powod=f"reguła {g['klucz']}: {g['uwaga']}"))
        continue
    if g and U.get('pensja') and g['klucz'] == U['pensja']['klucz'] and pensja:
        juz.append(dict(b, sposob='pensja brutto (przelew + pakiety)', w=wiersz_info(pensja[0])))
        continue
    if A.allegro and t in allegro_bank:
        if KARTA in t['no']:
            pominiete.append(dict(b, powod='karta podarunkowa Allegro – wydatki liczą się z listy zamówień'))
            continue
        if PAY in t['no']:
            if MIES < AL.get('pay_pomijaj_od', '0000-00'):
                decyzja(b, regula='ALLEGROPAY', opcje=[INNE], uwaga='spłata Allegro Pay za zakupy sprzed listy zamówień – '
                        'tych zakupów nie ma w arkuszu; wybierz kategorię albo Pomiń')
            else:
                pominiete.append(dict(b, powod='spłata Allegro Pay – zakupy są już z listy zamówień'))
            continue
        if t.get('allegro'):
            pominiete.append(dict(b, powod=t['allegro']))
            continue
        if t['kier'] == 'wypływ':
            decyzja(b, regula='ALLEGRO', opcje=[INNE], uwaga='płatność Allegro bez zamówienia na liście tego miesiąca '
                    '(zamówienie z innego miesiąca albo innego konta?) – wybierz kategorię albo Pomiń')
            continue
        zw = next((z for z in zam if z.get('zwrocony') and abs(z['suma'] - t['kwota']) < 0.005), None)
        if zw:
            pominiete.append(dict(b, powod=f"zwrot zamówienia {zw['sprzedawca']} – zwrócone zamówienia nie są liczone"))
            continue
    u_bp = wpis_bez_pary(t)
    if u_bp:
        _, przyp_u = przypiecie(u_bp, t)
        ids_u = [w['id'] for w in u_bp['czesci']]
        for d in decyzje:
            if d['id'] in ids_u:
                d['uwaga'] += (f"; w wyciągu jest płatność {t['data'].strftime('%d.%m')} {abs(t['kwota']):.2f} (inna kwota) – "
                               'jeśli to ta, przy niej wybierz „Już w arkuszu”')
    # zwrot: wpływ od sprzedawcy, u którego był wcześniej zakup -> pomniejsz ten zakup (wpływ przy wpisie bez pary – wyżej)
    if not u_bp and t['kier'] == 'wpływ' and not (g and (g['typ'] == 'Przelew' or (g['typ'] == 'Przychód' and g['kat'] != 'Zwroty'))) \
            and 'CASHBACK' not in t['no']:
        slowo = next((w for w in re.split(r'[\s,*]+', t['no']) if len(w) >= 4 and not w.isdigit()
                      and w not in ('PAYPRO', 'POZNAN', 'WARSZAWA')), '')
        zakupy = [u for u in bank if u['kier'] == 'wypływ' and slowo and slowo in u['no'] and 'CASHBACK' not in u['no']
                  and not u.get('allegro') and 0 <= (t['data'] - u['data']).days <= 120 and abs(u['kwota']) >= t['kwota'] - 0.005]
        if zakupy:
            cele = []
            for u in sorted(zakupy, key=lambda u: (t['data'] - u['data']).days)[:3]:
                c = dict(id=u['id'], data=u['data'].isoformat(), kwota=u['kwota'], opis=u['opis'])
                if u['id'] in para:
                    c['wiersz'] = wiersz_info(para[u['id']][0])
                elif u['mies'] != MIES:
                    c['kandydaci'] = kandydaci(u, 2)
                cele.append(c)
            decyzja(b, zrodlo='zwrot', regula=slowo, pewnosc='Zwykle', cele=cele,
                    uwaga='zwrot – pomniejszam zakup, którego dotyczy, zamiast osobnego wiersza')
            continue
    prop = opcja(g['typ'], g['kat'], g['pod']) if g and g['kat'] else None
    opcje = [rozbij(o) for o in (g['opcje'] if g else [])]
    if prop and prop['etykieta'] not in [o['etykieta'] for o in opcje]:
        opcje.insert(0, prop)
    moze_juz = (t['konto'] in ostatnia and t['data'] <= ostatnia[t['konto']]
                and not (g and g['klucz'] in ('CASHBACK', 'REWARD ZONE')))
    pew = (g['pewnosc'] or 'Zwykle') if g else 'Brak'
    if pew == 'Zawsze' and not moze_juz and not u_bp:
        auto.append(dict(b, typ=prop['typ'], kat=prop['kat'], pod=prop['pod'], regula=g['klucz'],
                         kwota_ark=kwota_w_arkuszu(t['kwota'], prop['typ'])))
        continue
    uw = [g['uwaga']] if g and g['uwaga'] else []
    if w:
        uw.insert(0, f"wpis: {w['tekst']}")
    kand = kandydaci(t) if moze_juz else []
    if u_bp:
        kand = [wiersz_info(r) for r in u_bp['wiersze'] if r] + kand
        uw.insert(0, f"może to wpis {', '.join(ids_u)} ({abs(u_bp['kwota']):.2f}, {u_bp['data'].strftime('%d.%m')}) – kwota inna; "
                     + ('„Już w arkuszu” przy jego wierszu przypnie płatność (kwota z wyciągu)' if przyp_u else
                        'wpisu nie ma w arkuszu – wybierz kategorię tylko raz: tu albo przy wpisie (drugie Pomiń)'))
    if moze_juz:
        uw.insert(0, f"na tym koncie wpisane ręcznie do {ostatnia[t['konto']].strftime('%d.%m')} – sprawdź, czy nie siedzi w sumie")
    decyzja(b, pewnosc='Zwykle' if pew == 'Zawsze' else pew, regula=g['klucz'] if g else '',
            propozycja=prop if pew in ('Zwykle', 'Zawsze') and not u_bp else None, opcje=opcje, uwaga='; '.join(uw), moze_juz=moze_juz,
            kandydaci=kand, **({'przypiecie_wpisu': przyp_u} if u_bp and przyp_u else {}))

# --- zamówienia Allegro jako wydatki
for z in zam:
    b = dict(id=z['id'], data=z['data'], konto=U.get('konto_zen'), osoba=U.get('osoba_wyciagi'), kwota=-z['suma'],
             opis=f"Allegro · {z['sprzedawca']}", produkty=z['produkty'], pay=z['pay'])
    if z.get('zwrocony'):
        pominiete.append(dict(b, powod='zamówienie zwrócone'))
        continue
    if z.get('juz'):
        r, sp = z['juz']
        juz.append(dict(b, sposob='zapłata kartą wpisana wcześniej ręcznie', w=wiersz_info(r)))
        continue
    prop = rozbij(z['prop']) if z.get('prop') else None
    decyzja(b, zrodlo='allegro', pewnosc='Zwykle' if prop else 'Pytaj', regula='ALLEGRO', propozycja=prop,
            opcje=([prop] if prop else []) + [rozbij(o) for o in z.get('opcje', [])],
            uwaga='Allegro Pay – spłata w kolejnym miesiącu zostanie pominięta' if z['pay'] else '')

if teraz:  # każde konto z wyciągiem, także bez wpisów: transakcji spoza zakresu pliku nie wczyta import żadnego miesiąca
    for konto in KONTA_A:
        if konto and konto not in niepelne and ZASIEG.get(konto, POCZ) < KONIEC:
            niepelne[konto] = ZASIEG.get(konto)
for konto, koniec in sorted(niepelne.items()):
    braki.append(f"wyciąg {konto} " + (f"kończy się {koniec.strftime('%d.%m')}" if koniec else 'brak') +
                 ' – pobierz cały miesiąc (wpisy z kart bez pary są na stronie decyzji albo czekają na kolejny import)')

# ---------- lista skrótów drugiej osoby (gotówka tylko z wpisów)
KONTA = U.get('konta_list', {})
KONTA_ID = U.get('konta_list_id', {})
NIEZNANE = U.get('nieznane_skroty', {})
hist = defaultdict(list)
for r in ark:
    if r['kwota']:
        hist[(r['konto'], r['kat'], r['pod'])].append(r['kwota'])


PS_KAT = U.get('przychod_z_sald', {}).get('kategoria')
# ręcznie wpisane wiersze tego miesiąca (gotówka, konta drugiej osoby) – lista i wpisy nie mogą ich zdublować
nasze_l = [r for r in ark if r['konto'] not in KONTA_A and r['mies'] == MIES and r['kwota'] is not None and not r['ids']
           and r['typ'] != 'Przelew' and r['kat'] != PS_KAT]


def juz_w_arkuszu(b, kod):
    if b['id'] in po_id:
        return po_id[b['id']], 'zaimportowane wcześniej'
    kat = SKROTY.get(kod)
    oczek = kwota_pozycji(b['kwota'], kat[0]) if kat else abs(b['kwota'])
    for r in nasze_l:
        if not r.get('uzyty') and r['konto'] == b['konto'] and abs(r['kwota'] - oczek) < 0.005 \
                and (not kat or nazwa(kat[1]) == r['kat']):
            r['uzyty'] = True
            return r, 'wpisane wcześniej ręcznie'
    return None


def pozycja(b, kod, budowa=''):
    """Jedna pozycja listy albo wpisu (gotówka, konta drugiej osoby): już w arkuszu / pewna / decyzja."""
    j = juz_w_arkuszu(b, kod)
    if j:
        juz.append(dict(b, sposob=j[1], w=wiersz_info(j[0])))
        if b.get('wpis') and j[1] != 'zaimportowane wcześniej':
            rozstrzygniete.add(b['id'])
        return
    suma, konto = abs(b['kwota']), b['konto']
    if kod not in SKROTY:
        decyzja(b, zrodlo='lista', regula=kod, opcje=[rozbij(o) for o in NIEZNANE.get(kod, [])],
                uwaga='nieznany skrót' if kod else 'wpływ bez opisu')
        return
    typ, kat, pod = SKROTY[kod]
    prop = opcja(typ, kat, pod)
    h = hist.get((konto, prop['kat'], prop['pod']), [])
    bud = {'budowa': budowa} if budowa else ({'budowa': w_kosztorysie(suma, b['data'])} if prop['kat'] == 'Dom' else {})
    if len(h) >= 3 and suma > 1000 and suma > 3 * statistics.median(h):
        decyzja(b, zrodlo='lista', pewnosc='Zwykle', regula=kod, propozycja=prop, opcje=[prop],
                uwaga=f'nietypowo duża kwota (zwykle ok. {statistics.median(h):.0f} zł)')
        decyzje[-1].update(bud)
    else:
        ark_k = kwota_pozycji(b['kwota'], prop['typ'])
        skl = skladniki_arkusza(ark_k, b.get('skladniki'))  # zwrot rozpisany działaniem: składniki ze znakiem arkusza
        auto.append(dict(b, typ=prop['typ'], kat=prop['kat'], pod=prop['pod'], regula=kod, kwota_ark=ark_k, skladniki=skl, **bud))


WPISY_L = [w for w in WPISY if w['konto'] not in KONTA_A]
# paragony (pole grupa): lista drugiej osoby ma całe zapłacone kwoty, więc porównuje się z sumą paragonu, nie z częścią
PARAGONY_L = {}
for w in WPISY_L:
    if w.get('grupa'):
        g = PARAGONY_L.setdefault(w['grupa'], dict(konto=w['konto'], kwota=0.0, data=w['data'],
                                                   sklep=(w.get('paragon') or {}).get('sklep', '')))
        g['kwota'] = round(g['kwota'] + w['kwota'], 2)
BLISKO_PARAGONU = 5.0


def paragon_listy(b, konto, tol):
    return next((g for g in PARAGONY_L.values() if not g.get('para') and g['konto'] == konto
                 and abs(g['kwota'] - b['kwota']) <= tol), None)


LICZBA_L = r'(?:\d{1,3}(?:[ \u00a0\u202f]\d{3})+(?!\d)(?:[.,]\d{1,2})?|\d[\d.,]*)'  # „1 234,56” albo „12,50”


def bez_tysiecy(s):
    return re.sub(r'(?<=\d)[ \u00a0\u202f](?=\d{3}(?!\d))', '', s)


def czytaj_liste(plik, domyslne_konto):
    konto, kid, n = domyslne_konto, domyslne_konto, Counter()
    for l in Path(plik).read_text(encoding='utf-8').splitlines():
        l = l.strip()
        if not l or l.startswith('#'):
            continue
        m = re.match(rf'^(\+?)\s*({LICZBA_L}(?:\s*[+-]\s*{LICZBA_L})*)\s*(.*)$', l)
        k = l.split()[0].lower()
        if not m and (k in KONTA or k in KONTA_ID or not re.search(r'\d', l)):  # nagłówek konta (linia bez cyfr – nazwa konta)
            konto, kid = KONTA.get(k, l), KONTA_ID.get(k, KONTA.get(k, l))
            continue
        n[(kid, l)] += 1  # ID nie zależy od pozycji linii – dopisanie linii nie zmienia ID pozostałych
        tid = 'l' + hashlib.sha1(f'{MIES}|{kid}|{l}|{n[(kid, l)]}'.encode()).hexdigest()[:10]
        if not m:  # „-40 zak” albo linia z cyfrą nie do odczytania – nie nagłówek (zmieniłby konto następnych pozycji)
            mm = re.match(rf'^-\s*({LICZBA_L})\s*(.*)$', l)
            kod = mm.group(2).strip().lower() if mm else ''
            decyzja(dict(id=tid, data=f'{MIES}-01', konto=konto, osoba=U.get('osoba_listy'), opis=l, skladniki=None,
                         kwota=-kw(bez_tysiecy(mm.group(1))) if mm else 0.0),
                    zrodlo='lista', regula=kod, opcje=[opcja(*SKROTY[kod])] if kod in SKROTY else [],
                    uwaga='„-” na początku – zwrot zapisuje się z „+”; wydatek: wybierz kategorię, zwrot: opisz w polu opisu'
                    if mm else 'nie rozumiem linii listy – opisz w polu opisu albo Pomiń')
            continue
        plus, kod = m.group(1), m.group(3).strip().lower()
        liczby = [-kw(x) if z == '-' else kw(x) for z, x in re.findall(r'([+-]?)\s*(\d[\d.,]*)', bez_tysiecy(m.group(2)))]
        suma = round(sum(liczby), 2)
        b = dict(id=tid, data=f'{MIES}-01', konto=konto, osoba=U.get('osoba_listy'), kwota=suma if plus else -suma,
                 opis=l, skladniki=liczby if len(liczby) > 1 else None)
        g = paragon_listy(b, konto, 0.005)
        if g:
            g['para'] = tid
            pominiete.append(dict(b, powod=f"już z paragonu {g['data']} ({g['sklep']})"))
            continue
        w = next((w for w in WPISY_L if not w.get('para') and not w.get('grupa') and w['konto'] == konto
                  and abs(w['kwota'] - b['kwota']) < 0.005), None)
        if w:
            w['para'] = tid
            pominiete.append(dict(b, powod=f"już z wpisu {w['data']}" + (f" ({w['opis']})" if w['opis'] else '')))
            continue
        g = paragon_listy(b, konto, BLISKO_PARAGONU)
        if g:  # kwota bliska sumie paragonu, ale inna – nie wpisuje się sama
            decyzja(b, zrodlo='lista', regula=kod, opcje=[opcja(*SKROTY[kod])] if kod in SKROTY else [],
                    uwaga=f"możliwy duplikat paragonu {g['data']} ({g['sklep']}, razem {abs(g['kwota']):.2f}; różnica "
                          f"{abs(g['kwota'] - b['kwota']):.2f}) – Pomiń, jeśli to ten sam zakup")
            continue
        pozycja(b, kod)


if A.lista:
    czytaj_liste(sciezka(A.lista), U.get('lista_domyslne_konto'))
else:
    braki.append(f"{U.get('etykieta_listy', 'lista wydatków drugiej osoby').lower()}")

for w in WPISY_L:  # gotówka i konta drugiej osoby: ID w kolumnie O -> już w arkuszu, inaczej wiersz (zapas) albo decyzja
    pozycja(baza_wpisu(w), w['kod'], 'z wpisu – w kosztorysie budowy (💸)' if w.get('budowa') else '')

# ---------- scalanie pewnych: ten sam dzień, konto i kategoria -> formuła; cashback – jeden wiersz na miesiąc
# wiersze z wpisów (ID w) nie są scalane – jeden ID = jeden wiersz
grupy = defaultdict(list)
for a in auto:
    sam = ','.join(a.get('ids_w') or [a['id']]) if (a.get('ids_w') or a['id'].startswith('w')) else ''
    grupy[('miesiąc' if a['regula'] == 'CASHBACK' else a['data'], a['konto'], a['typ'], a['kat'], a['pod'], sam)].append(a)
wiersze = []
for (dzien, konto, typ, kat, pod, _), g in sorted(grupy.items(), key=lambda x: (max(a['data'] for a in x[1]), x[0][1] or '')):
    skl = [x for a in g for x in (a['skladniki'] if a.get('skladniki') else [a['kwota_ark']])]
    wiersze.append(dict(data=max(a['data'] for a in g), konto=konto, osoba='' if typ == 'Przelew' else g[0]['osoba'], typ=typ, kat=kat, pod=pod,
                        kwota=round(sum(skl), 2), formula=('=' + '+'.join(f'{x:.2f}' for x in skl)).replace('+-', '-') if len(skl) > 1 else None,
                        opis=', '.join(sorted({a.get('opis_w') or a['regula'] for a in g})), zrodla=[a['id'] for a in g],
                        uwaga='; '.join(a['budowa'] for a in g if a.get('budowa'))))

# ---------- koniec miesiąca: przychód liczony z sald (zakładka Konta) i pozycji „do dodania” z zakładki roku
ps = U.get('przychod_z_sald')
if ps and M == 12:
    braki.append(f'grudzień: wiersz {ps["kategoria"]} potrzebuje sald na 1.01 i zakładki nowego roku – '
                 'dopisz go ręcznie (procedura budzet, references/arkusz.md, „Nowy rok”)')
elif ps:
    kol = lambda n: chr(ord('A') + n)
    w = ps['wiersz_konta']
    wiersze.append(dict(data=KONIEC.isoformat(), konto='', osoba='', typ='Przychód', kat=ps['kategoria'], pod='', kwota=None,
                        formula=f"=(Konta!${kol(M + 1)}${w}-Konta!${kol(M)}${w})+XLOOKUP(\"{ps['etykieta_roku']}\", '{R}'!A:A, '{R}'!{kol(M + 2)}:{kol(M + 2)})",
                        opis='', zrodla=[], uwaga=f'liczy się z sald w zakładce Konta (kolumna „{M + 1}”)'))
    if not A.salda_wpisane:
        braki.append(f'salda kont drugiej osoby w zakładce Konta, kolumna „{M + 1}” (stan na 1. dzień następnego miesiąca) – '
                     f'z nich liczy się wiersz {ps["kategoria"]}')

# ---------- salda kont z wyciągów (do zakładki Konta, kolumna następnego miesiąca)
salda = {}
zen_m = [t for t in teraz if t['konto'] == U.get('konto_zen') and t.get('saldo') is not None]
if zen_m:
    salda[U['konto_zen']] = dict(saldo=zen_m[-1]['saldo'], skad='saldo PLN z ostatniej operacji miesiąca')
mb = [t for t in teraz if t['konto'] == U.get('konto_mbank')]
if mb:
    salda[U['konto_mbank']] = dict(zmiana=round(sum(t['kwota'] for t in mb), 2), skad='saldo z poprzedniej kolumny Konta + zmiana w miesiącu')

# korekty salda konta z Allegro: należności i zobowiązania na koniec miesiąca, których nie ma jeszcze w wyciągu
kor = []
pay_dlug = round(sum(z['suma'] for z in zam if z['pay'] and not z.get('zwrocony')), 2)
if pay_dlug:
    kor.append(dict(kwota=-pay_dlug, opis='zakupy Allegro Pay z tego miesiąca – spłata w kolejnym'))
for o in oczek:
    if o['miesiac'] == NAST and o.get('kwota') and o.get('kierunek', 'wpływ') == 'wpływ':
        kor.append(dict(kwota=o['kwota'], opis='należność: ' + o['powod'][:80]))
karta = round(sum(-t['kwota'] for t in allegro_bank if A.allegro and KARTA in t['no'] and t['kwota'] < 0), 2)
if karta:
    kor.append(dict(kwota=None, opis=f'karta podarunkowa Allegro kupiona za {karta:.2f} – dopisz niewydaną resztę (zapytaj inwestora)'))
if kor:
    salda['korekty'] = dict(konto=U.get('konto_zen'), pozycje=kor)

for x in pominiete + juz:
    rozstrzygniete.update(x.get('ids_w') or [])
drzewo = [dict(typ=t, kat=k, pod=p) for t, ks in DRZEWO.items() for k, p in ks.items()]
zapisz(f'miesiace/{MIES}.json', dict(miesiac=MIES, wygenerowano=datetime.now().strftime('%Y-%m-%d %H:%M'), arkusz_plik=A.arkusz,
                                     wiersze=wiersze,
                                     auto=auto, decyzje=decyzje, pominiete=pominiete, juz=juz, przypiecia=przypiecia,
                                     braki=braki, salda=salda, wpisy_rozstrzygniete=sorted(rozstrzygniete),
                                     kategorie=drzewo, etykieta_listy=U.get('etykieta_listy', 'Lista wydatków'),
                                     ostatni_wiersz=max((r['wiersz'] for r in ark), default=1),
                                     ostatnia={k: v.isoformat() for k, v in ostatnia.items()}))
print(f"{MIES}: wyciąg {len(teraz)} (już w arkuszu {len(juz)}, pominięte {len(pominiete)}), Allegro {len(zam)} zamówień, "
      f"pewne {len(auto)} -> {len(wiersze)} wierszy, decyzje {len(decyzje)} {dict(Counter(d['zrodlo'] for d in decyzje))}; "
      f"przypięte do wierszy z wpisów {len(przypiecia)}, wpisy czekające {czeka}; braki: {len(braki)}")
