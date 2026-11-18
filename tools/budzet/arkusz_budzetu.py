#!/usr/bin/env python3
"""Wydatki z wpisów (pliki listy/RRRR-MM-wpisy.jsonl) -> arkusz Google „Budżet domowy”, zakładka Transakcje – bez AI, na Macu.
Instrukcja, interfejs i kod Apps Script: docs/budzet-arkusz.md. Procedura: plugins/ja/skills/budzet.

    python3 tools/budzet/arkusz_budzetu.py sync [--proba] [--cicho]   # nowe i zmienione zapisy od ARKUSZ_OD -> wiersze; usunięte -> usuń
    python3 tools/budzet/arkusz_budzetu.py kontrola [--cicho]          # zapis bez wiersza / wiersz bez zapisu (tylko odczyt)
    python3 tools/budzet/arkusz_budzetu.py ponow <id> [...]            # czyści znacznik – następny sync dopisze wiersz od nowa
    python3 tools/budzet/arkusz_budzetu.py przypnij --miesiac RRRR-MM [--proba]   # przypięcia z miesiace/RRRR-MM-zapis.json
    python3 tools/budzet/arkusz_budzetu.py sprawdz                     # sekrety i ping (wersja kodu, nagłówki)
    python3 tools/budzet/arkusz_budzetu.py kod | LANG=en_US.UTF-8 pbcopy   # kod Apps Script do schowka

Znacznik wysyłki w zapisie: pole `arkusz` = {wiersz, skrot, czas}; wysyłane są tylko zapisy bez znacznika albo ze zmienionym
skrótem treści (wspolne.skrot), więc ręczna poprawka wiersza w arkuszu zostaje, dopóki nie zmieni się wpis. Wiersz szuka
skrypt po ID w kolumnie O. Brak konfiguracji (BUDZET_ARKUSZ_URL, BUDZET_ARKUSZ_SEKRET w <hub>/.dom/sekrety.env; zmienne
środowiska o tych nazwach nadpisują plik) -> sync i kontrola kończą się kodem 0 jedną linią: zapisy czekają w pliku,
zamknięcie miesiąca dopisze je po ID. Komunikaty niosą tylko liczby, daty i ID – bez kwot i opisów.
"""
import argparse, json, os, re, sys, time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import (ARKUSZ_OD, HUB, blokada_wpisow, czytaj_wpisy, miesiace_wpisow, skrot, wczytaj,  # noqa: E402
                     wiersz_wpisu, zapisz, zapisz_wpisy)

WERSJA_MIN = 1          # minimalna wersja kodu Apps Script (WERSJA w docs/budzet-arkusz.md)
LIMIT_S = 90            # Apps Script bywa wolny przy zimnym starcie
PACZKA = 25
ZALEGLE_H = 24          # kontrola: niewysłane albo nieusunięte dłużej -> problem
DOKUMENTACJA = Path(__file__).resolve().parents[2] / 'docs' / 'budzet-arkusz.md'
ETYKIETA = '[budzet-arkusz]'


class BladKonfiguracji(Exception):
    pass


class BladArkusza(Exception):
    pass


def konfiguracja():
    if os.environ.get('BUDZET_ARKUSZ_URL') is not None:
        return {'url': os.environ.get('BUDZET_ARKUSZ_URL'), 'sekret': os.environ.get('BUDZET_ARKUSZ_SEKRET')}
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import wiedza as W  # wspólny czytnik sekretów (ostrzega o uprawnieniach pliku, wartości nie wypisuje)
    s = W.wczytaj_sekrety(HUB / '.dom' / 'sekrety.env')
    return {'url': s.get('BUDZET_ARKUSZ_URL'), 'sekret': s.get('BUDZET_ARKUSZ_SEKRET')}


def skonfigurowane(k):
    return bool(k.get('url') and k.get('sekret'))


def wyslij(k, akcja, **dane):
    """POST do aplikacji Apps Script (Google odpowiada przekierowaniem 302 na wynik – urllib idzie za nim GET-em)."""
    cialo = json.dumps(dict(dane, sekret=k['sekret'], akcja=akcja)).encode('utf-8')
    zad = urllib.request.Request(k['url'], data=cialo, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(zad, timeout=LIMIT_S) as odp:
            tresc = odp.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        raise BladArkusza(f'HTTP {e.code}') from None
    except OSError as e:
        raise BladArkusza(type(e).__name__) from None
    try:
        wynik = json.loads(tresc)
    except ValueError:
        raise BladArkusza('odpowiedź nie jest JSON – sprawdź, czy wdrożenie ma dostęp „Każdy”') from None
    if not wynik.get('ok'):
        raise BladArkusza(str(wynik.get('blad') or 'błąd bez opisu')[:200])
    return wynik


def ping(k):
    p = wyslij(k, 'ping')
    if (p.get('wersja') or 0) < WERSJA_MIN:
        raise BladArkusza(f"arkusz ma kod w wersji {p.get('wersja')} – wklej nowy kod (docs/budzet-arkusz.md, sekcja 6)")
    if not p.get('naglowek_ok'):
        raise BladArkusza('nagłówki Transakcji inne niż oczekiwane – nic nie zapisano (docs/budzet-arkusz.md, sekcja 5)')
    return p


def w_arkuszu(k):
    """ID -> numer wiersza z kolumny O (tokeny po przecinku) oraz wiersze z ID wpisu: [(wiersz, id, data)]."""
    mapa, wpisowe = {}, []
    for r in wyslij(k, 'odczyt')['wiersze']:
        for t in (x.strip() for x in str(r['o']).split(',')):
            if t:
                mapa[t] = r['wiersz']
                if t.startswith('w'):
                    wpisowe.append((r['wiersz'], t, str(r.get('data') or '')))
    return mapa, wpisowe


def teraz():
    return datetime.now().strftime('%Y-%m-%d %H:%M')


def zapisy():
    """[(miesiąc, zapis)] dotyczące arkusza: data od ARKUSZ_OD albo już wysłane (znacznik), także usunięte."""
    out = []
    for m in miesiace_wpisow():
        for w in czytaj_wpisy(m, z_usunietymi=True):
            if w['data'] >= ARKUSZ_OD or w.get('arkusz'):
                out.append((m, w))
    return out


def plan():
    """-> (dopisz, popraw, usun, bez kategorii) – listy (miesiąc, zapis)."""
    dop, pop, usu, bez = [], [], [], []
    for m, w in zapisy():
        zn = w.get('arkusz')
        if w.get('usuniety'):
            if zn:
                usu.append((m, w))
        elif not w.get('kat'):
            bez.append((m, w))  # nieznany skrót kategorii – wiersz doda zamknięcie miesiąca po decyzji
        elif not zn:
            dop.append((m, w))
        elif zn.get('skrot') != skrot(w):
            pop.append((m, w))
    return dop, pop, usu, bez


def zapisz_wyniki(znaczniki, usuniete):
    """Znaczniki {id: znacznik} i usunięte ID -> pliki, pod blokadą, po ponownym odczycie (wpis.py mógł coś zmienić)."""
    if not znaczniki and not usuniete:
        return
    with blokada_wpisow():
        for m in miesiace_wpisow():
            ws = czytaj_wpisy(m, z_usunietymi=True)
            zmiana = False
            for w in ws:
                if w['id'] in znaczniki and not w.get('usuniety'):
                    w['arkusz'] = znaczniki[w['id']]
                    zmiana = True
            reszta = [w for w in ws if not (w['id'] in usuniete and w.get('usuniety'))]
            if zmiana or len(reszta) != len(ws):
                zapisz_wpisy(m, reszta)


def sync(k, proba):
    dop, pop, usu, bez = plan()
    licz = {'dopisane': 0, 'juz_w_arkuszu': 0, 'poprawione': 0, 'usuniete': 0, 'bez_kategorii': len(bez), 'bledy': 0}
    bledy = []
    if not skonfigurowane(k):
        n = len(dop) + len(pop) + len(usu)
        print(f'{ETYKIETA} sync: nieskonfigurowane (brak BUDZET_ARKUSZ_URL / BUDZET_ARKUSZ_SEKRET w .dom/sekrety.env) – '
              f'{n} zapisów czeka w pliku; zamknięcie miesiąca dopisze je po ID (docs/budzet-arkusz.md)')
        if proba:
            for akcja, lista in (('dopisz', dop), ('popraw', pop), ('usuń', usu)):
                for _, w in lista:
                    print(f"  → {akcja} {w['data']} {w['id']}")
        return licz, bledy
    if not (dop or pop or usu):
        return licz, bledy
    ping(k)
    if proba:
        mapa, _ = w_arkuszu(k)
        for _, w in dop:
            if w['id'] in mapa:
                licz['juz_w_arkuszu'] += 1
                print(f"  = już w arkuszu {w['data']} {w['id']} (wiersz {mapa[w['id']]}) – tylko znacznik")
            else:
                licz['dopisane'] += 1
                print(f"  → dopisz {w['data']} {w['id']}")
        for akcja, lista, klucz in (('popraw', pop, 'poprawione'), ('usuń', usu, 'usuniete')):
            for _, w in lista:
                licz[klucz] += 1
                print(f"  → {akcja} {w['data']} {w['id']}" + (f" (wiersz {mapa[w['id']]})" if w['id'] in mapa else ' – brak wiersza'))
        return licz, bledy
    znaczniki, usuniete = {}, set()
    for akcja, lista in (('dopisz', dop), ('popraw', pop)):
        for i in range(0, len(lista), PACZKA):
            paczka = [w for _, w in lista[i:i + PACZKA]]
            try:
                wyniki = wyslij(k, akcja, wiersze=[wiersz_wpisu(w) for w in paczka])['wyniki']
            except BladArkusza as e:
                bledy.append(f'{akcja}: {e} – zapisy czekają w pliku')
                break
            po_id = {w['id']: w for w in paczka}
            for r in wyniki:
                if r.get('ok'):
                    znaczniki[r['id']] = {'wiersz': r.get('wiersz'), 'skrot': skrot(po_id[r['id']]), 'czas': teraz()}
                    licz['juz_w_arkuszu' if r.get('juz') else ('dopisane' if akcja == 'dopisz' else 'poprawione')] += 1
                else:
                    licz['bledy'] += 1
                    bledy.append(f"{akcja} {po_id[r['id']]['data']} {r['id']}: {str(r.get('blad'))[:120]}")
    if usu:
        try:
            for r in wyslij(k, 'usun', ids=[w['id'] for _, w in usu])['wyniki']:
                if r.get('ok'):
                    usuniete.add(r['id'])
                    licz['usuniete'] += 1
                else:
                    licz['bledy'] += 1
                    bledy.append(f"usuń {r['id']}: {str(r.get('blad'))[:120]}")
        except BladArkusza as e:
            bledy.append(f'usuń: {e} – zapisy czekają w pliku')
    zapisz_wyniki(znaczniki, usuniete)
    return licz, bledy


def kontrola(k):
    """-> (liczniki, problemy); tylko odczyt."""
    zs = zapisy()
    licz = {'zapisy': sum(1 for _, w in zs if not w.get('usuniety')), 'w_arkuszu': 0}
    if not skonfigurowane(k):
        czeka = sum(1 for _, w in zs if not w.get('arkusz') and not w.get('usuniety'))
        print(f'{ETYKIETA} kontrola: nieskonfigurowane – {czeka} zapisów od {ARKUSZ_OD} czeka w pliku')
        return licz, []
    mapa, wpisowe = w_arkuszu(k)
    granica = (datetime.now() - timedelta(hours=ZALEGLE_H)).strftime('%Y-%m-%d %H:%M')
    problemy = []
    znane = {w['id'] for _, w in zs} | {w['id'] for m in miesiace_wpisow() for w in czytaj_wpisy(m, z_usunietymi=True)}
    for _, w in zs:
        if w.get('usuniety'):
            if w['id'] in mapa and w['usuniety'] < granica:
                problemy.append(f"usunięty we wpisach, wiersz {mapa[w['id']]} wciąż w arkuszu: {w['data']} {w['id']}")
            continue
        if w['id'] in mapa:
            licz['w_arkuszu'] += 1
        elif w.get('arkusz'):
            problemy.append(f"brak wiersza w arkuszu (był {w['arkusz'].get('wiersz')}): {w['data']} {w['id']}")
        elif w.get('kat') and w.get('dodano', '') < granica:
            problemy.append(f"niewysłany od ponad {ZALEGLE_H} h: {w['data']} {w['id']}")
    for wiersz, id_, data in wpisowe:
        if data >= ARKUSZ_OD and id_ not in znane:
            problemy.append(f'wiersz {wiersz} z ID wpisu, którego nie ma w plikach: {data} {id_}')
    return licz, problemy


def ponow(ids):
    ids = set(ids) | {'w' + i for i in ids}
    n = 0
    with blokada_wpisow():
        for m in miesiace_wpisow():
            ws = czytaj_wpisy(m, z_usunietymi=True)
            hit = [w for w in ws if w['id'] in ids and w.get('arkusz')]
            for w in hit:
                del w['arkusz']
            if hit:
                zapisz_wpisy(m, ws)
                n += len(hit)
    return n


def przypnij(k, mies, proba):
    nazwa = f'miesiace/{mies}-zapis.json'
    z = wczytaj(nazwa)
    lista = [p for p in z.get('przypiecia', []) if not p.get('zrobione')]
    licz = {'przypiecia': len(lista), 'zrobione': 0, 'bledy': 0}
    bledy = []
    if not lista:
        return licz, bledy
    zad = [{'id_wyciagu': p['id_wyciagu'], 'ids': [x['id'] for x in p['wiersze']],
            'kwoty': {x['id']: x['kwota'] for x in p['wiersze'] if x.get('kwota') is not None}} for p in lista]
    if proba:
        for p in zad:
            print(f"  → przypnij {p['id_wyciagu']} do {', '.join(p['ids'])}" + (' (z kwotą)' if p['kwoty'] else ''))
        return licz, bledy
    ping(k)
    wyniki = wyslij(k, 'przypnij', przypiecia=zad)['wyniki']
    for p, r in zip(lista, wyniki):
        if r.get('ok'):
            p['zrobione'] = teraz()
            licz['zrobione'] += 1
        else:
            licz['bledy'] += 1
            bledy.append(f"przypnij {p['id_wyciagu']}: {str(r.get('blad'))[:120]}")
    zapisz(nazwa, z)
    return licz, bledy


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('polecenie', choices=['sync', 'kontrola', 'ponow', 'przypnij', 'sprawdz', 'kod'])
    ap.add_argument('ids', nargs='*', help='ponow: ID zapisów')
    ap.add_argument('--proba', action='store_true', help='sync, przypnij: tylko pokaż, co poszłoby do arkusza')
    ap.add_argument('--cicho', action='store_true', help='jedna linia wyniku (dla automatów)')
    ap.add_argument('--miesiac', help='przypnij: RRRR-MM')
    a = ap.parse_args(argv)
    if a.polecenie == 'kod':
        m = re.search(r'```javascript\n(.*?)```', DOKUMENTACJA.read_text(encoding='utf-8'), re.S)
        if not m:
            print(f'  ✗ brak bloku kodu w {DOKUMENTACJA.name}', file=sys.stderr)
            return 1
        sys.stdout.write(m.group(1))
        return 0
    if a.polecenie == 'ponow':
        if not a.ids:
            ap.error('ponow: podaj ID zapisów')
        print(f'{ETYKIETA} ponow: wyczyszczono znacznik w {ponow(a.ids)} zapisach – następny sync dopisze wiersze')
        return 0
    if a.polecenie == 'przypnij' and not a.miesiac:
        ap.error('przypnij: podaj --miesiac RRRR-MM')
    k = konfiguracja()
    t0 = time.monotonic()
    bledy = []
    try:
        if a.polecenie == 'sync':
            licz, bledy = sync(k, a.proba)
            linia = 'sync' + (' (próba)' if a.proba else '') + ': ' + ', '.join(f'{n} {v}' for n, v in licz.items())
        elif a.polecenie == 'kontrola':
            licz, problemy = kontrola(k)
            linia = 'kontrola: ' + ', '.join(f'{n} {v}' for n, v in licz.items()) + f', problemy {len(problemy)}'
            bledy = ['; '.join(problemy)] if problemy else []  # jedna linia ✗ – automat przenosi ją do komunikatu 🔔
        else:
            if not skonfigurowane(k):
                raise BladKonfiguracji('brak BUDZET_ARKUSZ_URL / BUDZET_ARKUSZ_SEKRET w .dom/sekrety.env')
            if a.polecenie == 'sprawdz':
                p = ping(k)
                linia = (f"sprawdz: OK („{p.get('arkusz')}”, kod w wersji {p.get('wersja')}, wierszy {p.get('wierszy')}, "
                         f"strefa {p.get('strefa')})")
            else:
                licz, bledy = przypnij(k, a.miesiac, a.proba)
                linia = 'przypnij' + (' (próba)' if a.proba else '') + ': ' + ', '.join(f'{n} {v}' for n, v in licz.items())
    except BladKonfiguracji as e:
        print(f'{ETYKIETA} nieskonfigurowane – {e} (docs/budzet-arkusz.md, sekcja 6)')
        return 2
    except BladArkusza as e:
        bledy.append(f'arkusz: {e}')
        linia = a.polecenie + ': przerwane'
    print(f'{ETYKIETA} {linia} · {time.monotonic() - t0:.0f} s')
    for b in bledy:
        print(f'  ✗ {b}', file=sys.stderr if a.cicho else sys.stdout)
    return 1 if bledy else 0


if __name__ == '__main__':
    sys.exit(main())
