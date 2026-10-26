#!/usr/bin/env python3
"""Odciski znaczenia (embeddingi) informacji Bazy wiedzy i listy „podobne” – tylko na Macu, model lokalny (Ollama).

Odciski leżą w osobnym pliku obok indeksu (`wektory.sqlite`, 600) i nie trafiają do kopii dla czatu; listy
podobnych są tabelą `podobne` w samym indeksie (publikuje je `wiedza.py publikuj`, czyta `szukaj --krotko`
także w czacie, bez tego modułu).

    python3 tools/wiedza_sens.py przelicz [--db ŚCIEŻKA] [--pelny]   # odciski i listy podobnych od ręki, z czasem
    python3 tools/wiedza_sens.py stan [--db ŚCIEŻKA]                  # ile odcisków i list, model, źródło

Zwykle nic nie trzeba uruchamiać: `wiedza.py sync` po pobraniu zmian woła `po_sync` (odciski nowych i zmienionych
informacji, listy przyrostowo); Ollama nie działa → pominięte po cichu. `szukaj --sens` woła `rankingi`.

Konfiguracja (poza repo): `.dom/sens.json` w hubie, np. {"zrodlo": "ollama", "model": "bge-m3"}; brak pliku =
Ollama z bge-m3 pod localhost:11434. "zrodlo": "brak" wyłącza odciski. "bedrock" jest przewidziany, niewdrożony –
wymaga zgody inwestora (nowa usługa zewnętrzna).

Zasady: tylko biblioteka standardowa; jedyne wyjście do sieci to adres Ollamy z konfiguracji (domyślnie
localhost); komunikaty bez treści informacji – tylko liczby, numery WI i nazwy modelu.
"""
import argparse
import array
import contextlib
import hashlib
import json
import operator
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DOMYSLNA = {"zrodlo": "ollama", "model": "bge-m3", "adres": "http://localhost:11434"}
PLIK_KONFIGURACJI = "sens.json"     # w .dom huba
PLIK_WEKTOROW = "wektory.sqlite"    # obok pliku indeksu
SZCZEGOLY_ZN = 400                  # tekst odcisku: teza + „ | ” + szczegóły do tylu znaków
PORCJA = 32                         # tekstów na jedno żądanie /api/embed
CZAS_ZADANIA = 120                  # s na porcję (pierwsze żądanie ładuje model ok. 2 s)
CZAS_SONDY = 2                      # s na sprawdzenie, czy Ollama działa
SASIADOW = 10                       # najwyżej tylu sąsiadów na informację
PODOBNE_MIN = 0.55                  # niżej sąsiad nie trafia na listę (próg wyświetlania jest w wiedza.py)
ZAPIS_CO = 50                       # list podobnych na jedną transakcję (przerwanie nie gubi policzonych)

SCHEMAT_WEKTOROW = """
CREATE TABLE IF NOT EXISTS wektory (wi INTEGER PRIMARY KEY, model TEXT, sha_tekstu TEXT, wektor BLOB,
                                    lista INTEGER DEFAULT 0);  -- lista: 1 = lista podobnych policzona z tym odciskiem
"""


class Niedostepny(Exception):
    """Źródło odcisków nie działa (Ollama wyłączona, brak modelu, "zrodlo": "brak") – sync pomija krok po cichu."""


def konfiguracja(conf: Path) -> dict:
    k = dict(DOMYSLNA)
    with contextlib.suppress(FileNotFoundError):
        k.update(json.loads((Path(conf) / PLIK_KONFIGURACJI).read_text(encoding="utf-8")))
    return k


def tekst_informacji(teza, szczegoly) -> str:
    teza, szczegoly = " ".join((teza or "").split()), " ".join((szczegoly or "").split())[:SZCZEGOLY_ZN]
    return f"{teza} | {szczegoly}" if szczegoly else teza


def sha_tekstu(tekst: str) -> str:
    return hashlib.sha256(tekst.encode("utf-8")).hexdigest()


def _post(k: dict, sciezka: str, dane: dict, timeout: float) -> dict:
    zadanie = urllib.request.Request(k["adres"].rstrip("/") + sciezka, data=json.dumps(dane).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(zadanie, timeout=timeout) as r:
        return json.loads(r.read())


def sprawdz_zrodlo(k: dict):
    """Niedostepny, gdy odcisków nie da się policzyć: źródło inne niż ollama, Ollama nie odpowiada albo nie ma
    modelu (pobierz go: `ollama pull bge-m3`)."""
    if k.get("zrodlo") != "ollama":
        raise Niedostepny(f"źródło odcisków: {k.get('zrodlo')}")
    try:
        with urllib.request.urlopen(k["adres"].rstrip("/") + "/api/tags", timeout=CZAS_SONDY) as r:
            modele = {m.get("name", "").split(":")[0] for m in json.loads(r.read()).get("models", [])}
    except (OSError, ValueError) as e:
        raise Niedostepny("Ollama nie działa") from e
    if k["model"].split(":")[0] not in modele:
        raise Niedostepny(f"brak modelu {k['model']} w Ollamie")


def odciski(teksty: list, k: dict) -> list:
    """Odciski (listy float, długość 1) dla tekstów, w tej samej kolejności."""
    try:
        wynik = _post(k, "/api/embed", {"model": k["model"], "input": teksty}, CZAS_ZADANIA)["embeddings"]
    except urllib.error.URLError as e:
        if isinstance(e.reason, ConnectionRefusedError):
            raise Niedostepny("Ollama nie działa") from e
        raise
    if len(wynik) != len(teksty):
        raise ValueError(f"Ollama zwróciła {len(wynik)} odcisków na {len(teksty)} tekstów")
    return [znormalizuj(w) for w in wynik]


def znormalizuj(w) -> list:
    dlugosc = sum(x * x for x in w) ** 0.5 or 1.0
    return [x / dlugosc for x in w]


def do_blob(w) -> bytes:
    return array.array("f", w).tobytes()


def z_blob(b: bytes) -> list:
    a = array.array("f")
    a.frombytes(b)
    return a.tolist()


def iloczyn(a, b) -> float:
    return sum(map(operator.mul, a, b))


def plik_wektorow(sciezka_bazy: Path) -> Path:
    return Path(sciezka_bazy).with_name(PLIK_WEKTOROW)


def otworz_wektory(sciezka: Path, zapis: bool = True) -> sqlite3.Connection:
    if not zapis:
        if not sciezka.is_file():
            raise Niedostepny("brak pliku odcisków – policzy je sync na Macu")
        return sqlite3.connect(sciezka.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
    conn = sqlite3.connect(str(sciezka), timeout=5)
    conn.executescript(SCHEMAT_WEKTOROW)
    return conn


def teksty_indeksu(conn: sqlite3.Connection) -> dict:
    return {wi: tekst_informacji(t, s) for wi, t, s in conn.execute("SELECT wi, teza, szczegoly FROM informacje")}


def uzupelnij_wektory(conn: sqlite3.Connection, cw: sqlite3.Connection, k: dict, termin=None) -> dict:
    """Odciski brakujących, zmienionych (sha) i liczonych innym modelem; odciski usuniętych informacji kasuje.
    Porcjami po PORCJA, każda we własnej transakcji – przerwanie (termin, błąd) nie gubi policzonych.
    → {"policzone", "usuniete", "brakuje"} (brakuje = zostało na następny raz)."""
    teksty = teksty_indeksu(conn)
    stare = {wi: (m, s) for wi, m, s in cw.execute("SELECT wi, model, sha_tekstu FROM wektory")}
    usuniete = [wi for wi in stare if wi not in teksty]
    with cw:
        cw.executemany("DELETE FROM wektory WHERE wi = ?", [(wi,) for wi in usuniete])
    do_policzenia = [wi for wi in sorted(teksty) if stare.get(wi) != (k["model"], sha_tekstu(teksty[wi]))]
    policzone = 0
    for start in range(0, len(do_policzenia), PORCJA):
        if termin is not None and time.monotonic() > termin:
            break
        porcja = do_policzenia[start:start + PORCJA]
        wektory = odciski([teksty[wi] for wi in porcja], k)
        with cw:
            cw.executemany("INSERT OR REPLACE INTO wektory (wi, model, sha_tekstu, wektor, lista) VALUES (?, ?, ?, ?, 0)",
                           [(wi, k["model"], sha_tekstu(teksty[wi]), do_blob(w)) for wi, w in zip(porcja, wektory)])
        policzone += len(porcja)
    return {"policzone": policzone, "usuniete": len(usuniete), "brakuje": len(do_policzenia) - policzone}


def wczytaj_wektory(cw: sqlite3.Connection, model: str, numery=None) -> dict:
    return {wi: z_blob(b) for wi, b in cw.execute("SELECT wi, wektor FROM wektory WHERE model = ?", (model,))
            if numery is None or wi in numery}


def teraz_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def przelicz_podobne(conn: sqlite3.Connection, cw: sqlite3.Connection, k: dict, termin=None) -> dict:
    """Listy podobnych (tabela `podobne` indeksu) dla informacji z nowym albo zmienionym odciskiem (lista = 0),
    przyrostowo: lista takiej informacji od nowa (iloczyn z wszystkimi odciskami), a ona sama dopisana do list
    innych, gdy mieści się w ich SASIADOW. Informacja usunięta albo zmieniona znika z cudzych list – te listy
    liczone są od nowa, żeby nie zostały krótsze, niż powinny. Odciski są znormalizowane, więc iloczyn = cosinus.
    → {"policzone", "brakuje", "zmiana"}; meta indeksu: podobne_policzone (czas zmiany), podobne_model,
    podobne_brakuje."""
    wektory = wczytaj_wektory(cw, k["model"], set(teksty_indeksu(conn)))
    gotowe = {wi for (wi,) in cw.execute("SELECT wi FROM wektory WHERE lista = 1 AND model = ?", (k["model"],))
              if wi in wektory}
    model_listy = dict(conn.execute("SELECT klucz, wartosc FROM meta")).get("podobne_model")
    if model_listy and model_listy != k["model"]:
        gotowe = set()
    listy = {}
    for wi, p, s in conn.execute("SELECT wi, wi_podobne, podobienstwo FROM podobne"):
        listy.setdefault(wi, {})[p] = s
    nieaktualne = set(listy) - gotowe | {p for l in listy.values() for p in l} - gotowe
    zmiana = False
    # informacja bez aktualnej listy albo nieaktualna na cudzej liście: wiersze z nią znikają, a listy, które ją
    # miały, liczone są od nowa
    do_listy = set(wektory) - gotowe
    for wi in list(listy):
        if wi in nieaktualne:
            del listy[wi]
            zmiana = True
            continue
        if any(p in nieaktualne for p in listy[wi]):
            listy[wi] = {p: s for p, s in listy[wi].items() if p not in nieaktualne}
            if wi in wektory:
                do_listy.add(wi)
            zmiana = True
    numery = sorted(wektory)
    macierz = [wektory[wi] for wi in numery]
    kolejka = sorted(do_listy)
    policzone = 0
    for start in range(0, len(kolejka), ZAPIS_CO):
        if termin is not None and time.monotonic() > termin:
            break
        porcja = kolejka[start:start + ZAPIS_CO]
        for wi in porcja:
            v = wektory[wi]
            podob = [(iloczyn(v, w), n) for n, w in zip(numery, macierz) if n != wi]
            najlepsze = sorted((p for p in podob if p[0] >= PODOBNE_MIN), reverse=True)[:SASIADOW]
            listy[wi] = {n: round(s, 4) for s, n in najlepsze}
            # nowa informacja na cudzych listach (lista już policzona i ma miejsce albo słabszego sąsiada)
            for s, n in podob:
                if s < PODOBNE_MIN or n in do_listy and n not in gotowe or wi in listy.get(n, {}):
                    continue
                cudza = listy.setdefault(n, {})
                if len(cudza) < SASIADOW:
                    cudza[wi] = round(s, 4)
                else:
                    slaby = min(cudza, key=lambda x: (cudza[x], -x))
                    if s > cudza[slaby]:
                        del cudza[slaby]
                        cudza[wi] = round(s, 4)
            gotowe.add(wi)
        zapisz_listy(conn, listy)
        with cw:
            cw.executemany("UPDATE wektory SET lista = 1 WHERE wi = ?", [(wi,) for wi in porcja])
        policzone += len(porcja)
        zmiana = True
    brakuje = len(set(teksty_indeksu(conn)) - gotowe)
    meta = {"podobne_model": k["model"], "podobne_brakuje": str(brakuje)}
    if zmiana:
        zapisz_listy(conn, listy)
        meta["podobne_policzone"] = teraz_iso()
    with conn:
        conn.executemany("INSERT OR REPLACE INTO meta VALUES (?, ?)", list(meta.items()))
    return {"policzone": policzone, "brakuje": brakuje, "zmiana": zmiana}


def zapisz_listy(conn: sqlite3.Connection, listy: dict):
    with conn:
        conn.execute("DELETE FROM podobne")
        conn.executemany("INSERT INTO podobne (wi, wi_podobne, podobienstwo) VALUES (?, ?, ?)",
                         [(wi, p, s) for wi, l in sorted(listy.items()) for p, s in sorted(l.items())])


def po_sync(conn: sqlite3.Connection, sciezka_bazy: Path, conf: Path, termin=None) -> str:
    """Krok syncu po zapisie pobranych zmian: odciski i listy podobnych do terminu. Źródło niedostępne → "" (cisza);
    inaczej linia raportu (pusta, gdy nic się nie zmieniło). Inne błędy idą do wołającego."""
    k = konfiguracja(conf)
    sprawdz_zrodlo(k)
    start = time.monotonic()
    with contextlib.closing(otworz_wektory(plik_wektorow(sciezka_bazy))) as cw:
        w = uzupelnij_wektory(conn, cw, k, termin)
        p = przelicz_podobne(conn, cw, k, termin)
    if not (w["policzone"] or w["usuniete"] or p["zmiana"] or w["brakuje"] or p["brakuje"]):
        return ""
    czas = f"{time.monotonic() - start:.1f}".replace(".", ",")
    reszta = w["brakuje"] or p["brakuje"]
    return (f"[wiedza] odciski {k['model']}: +{w['policzone']}, −{w['usuniete']} · listy podobnych: {p['policzone']}"
            + (f" · zostało {reszta} na następny sync" if reszta else "") + f" · {czas} s")


def rankingi(sciezka_bazy: Path, zapytania: list, conf: Path) -> list:
    """szukaj --sens: dla każdego zapytania [(WI, podobieństwo)] wszystkich informacji z odciskiem bieżącego
    modelu, malejąco. Niedostepny – brak źródła, pliku odcisków albo odcisków tego modelu."""
    k = konfiguracja(conf)
    with contextlib.closing(otworz_wektory(plik_wektorow(sciezka_bazy), zapis=False)) as cw:
        wektory = wczytaj_wektory(cw, k["model"])
    if not wektory:
        raise Niedostepny("brak odcisków modelu " + k["model"])
    sprawdz_zrodlo(k)
    wynik = []
    for v in odciski([" ".join(q.split()) for q in zapytania], k):
        wynik.append(sorted(((wi, iloczyn(v, w)) for wi, w in wektory.items()), key=lambda p: (-p[1], p[0])))
    return wynik


def cmd_przelicz(a) -> int:
    import wiedza as W  # leniwie: wiedza.py importuje ten moduł tylko w sync i szukaj --sens
    sciezka = W.sciezka_bazy(a)
    if W.w_worktree() and not a.db:
        print("[wiedza] uruchomiono z worktree – przeliczenie pominięte (podaj --db kopii)")
        return 1
    with W.prywatne_pliki(), W.blokada(sciezka) as wzieta:
        if not wzieta:
            print("[wiedza] trwa sync albo publikacja – przeliczenie pominięte")
            return 0
        with contextlib.closing(W.otworz_db(sciezka, zapis=True)) as conn:
            k = konfiguracja(W.CONF)
            try:
                sprawdz_zrodlo(k)
            except Niedostepny as e:
                print(f"[wiedza] {e} – odcisków nie policzono")
                return 1
            with contextlib.closing(otworz_wektory(plik_wektorow(sciezka))) as cw:
                if a.pelny:
                    with cw:
                        cw.execute("UPDATE wektory SET lista = 0")
                t0 = time.monotonic()
                w = uzupelnij_wektory(conn, cw, k)
                t1 = time.monotonic()
                p = przelicz_podobne(conn, cw, k)
                t2 = time.monotonic()
    print(f"[wiedza] odciski {k['model']}: +{w['policzone']}, −{w['usuniete']} · {t1 - t0:.1f} s · listy podobnych: "
          f"{p['policzone']} · {t2 - t1:.1f} s".replace(".", ","))
    return 0


def cmd_stan(a) -> int:
    import wiedza as W
    sciezka = W.sciezka_bazy(a)
    k = konfiguracja(W.CONF)
    try:
        sprawdz_zrodlo(k)
        zrodlo = "działa"
    except Niedostepny as e:
        zrodlo = str(e)
    with contextlib.closing(W.otworz_db(sciezka, zapis=False)) as conn:
        meta = W.meta_bazy(conn)
        informacji = conn.execute("SELECT COUNT(*) FROM informacje").fetchone()[0]
        list_ = W.podobne_w_indeksie(conn)
    odciskow = 0
    with contextlib.suppress(Niedostepny):
        with contextlib.closing(otworz_wektory(plik_wektorow(sciezka), zapis=False)) as cw:
            odciskow = cw.execute("SELECT COUNT(*) FROM wektory WHERE model = ?", (k["model"],)).fetchone()[0]
    print(f"# odciski: źródło {k['zrodlo']} ({zrodlo}) · model {k['model']} · {odciskow}/{informacji} informacji")
    print(f"listy podobnych: {list_} wierszy · policzone {W.lokalnie(meta.get('podobne_policzone'))} · model "
          f"{meta.get('podobne_model') or '–'} · bez listy {meta.get('podobne_brakuje') or '–'}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="polecenie", metavar="POLECENIE", required=True)
    p = sub.add_parser("przelicz", help="odciski i listy podobnych od ręki (z czasem)")
    p.add_argument("--db", type=Path, help="plik indeksu (domyślnie .dom/wiedza/wiedza.sqlite w hubie)")
    p.add_argument("--pelny", action="store_true", help="wszystkie listy podobnych od nowa (odciski tylko zmienione)")
    p = sub.add_parser("stan", help="ile odcisków i list podobnych, model, czy źródło działa")
    p.add_argument("--db", type=Path)
    a = ap.parse_args(argv)
    return {"przelicz": cmd_przelicz, "stan": cmd_stan}[a.polecenie](a)


if __name__ == "__main__":
    sys.exit(main())
