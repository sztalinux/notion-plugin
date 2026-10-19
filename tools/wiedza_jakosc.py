#!/usr/bin/env python3
"""Obserwator jakości wyszukiwania indeksu wiedzy (`tools/wiedza.py szukaj`) – tylko Claude Code na Macu.

Sprawdza, czy `szukaj` nadal znajduje to, co powinien (zbiory oceny), i jak kończą się prawdziwe zapytania (log).
Nie zmienia indeksu ani Notion; indeks otwiera tylko do odczytu.

    python3 tools/wiedza_jakosc.py zloty [--odnowa] [--ustaw-baze]   # przebieg zbiorów oceny → historia, porównanie
    python3 tools/wiedza_jakosc.py dodaj "ZAPYTANIE" --powinno WI-12[,WI-40] [--opis TEKST]
    python3 tools/wiedza_jakosc.py raport [--dni 7]                  # log, trend, ocena ręczna, ALARMY
    python3 tools/wiedza_jakosc.py reczna [--n 30] [--nowa]          # ocena ręczna w terminalu (y/n/s, q = przerwa)
    python3 tools/wiedza_jakosc.py reczna --wczytaj PLIK             # dokończ albo wczytaj zestaw ocen z pliku
    python3 tools/wiedza_jakosc.py notion [--budzet 300]             # raz w miesiącu: porównanie z Notion przez API
    python3 tools/wiedza_jakosc.py przypomnij --cicho                # hook startu: jedna linia, gdy jest coś do zrobienia

Opcje wspólne: --db ŚCIEŻKA (indeks w `<hub>/.dom/wiedza/`; dane obserwatora leżą obok), --json.

Polecenia:
- zloty: zbiory oceny na bieżącym indeksie – known-item (KI: 2–3 rzadkie albo tematyczne słowa wiersza z próby
  warstwowej i ich perturbacje: odmiana, bez polskich znaków, rama pytania, wypełniacz, wstawiony rzadki czasownik,
  odwrócona kolejność, „naturalne”), tematy (nazwa tematu → informacje z relacją do niego), pytania wymyślone
  z predykatami słów (`pytania.json`, przy pierwszym użyciu kopia `tools/wiedza_jakosc_pytania.json`), test
  czasowników (KLUCZOWE8 × wstawiony czasownik) i przypadki inwestora (`dodaj`). Liczy success@12 i MRR (KI; MRR po
  całej liście wyników), P@12 (tematy, pytania), zapisuje przebieg i alarmy w historii, porównuje z poprzednim
  i z bazowym (pierwszy przebieg = baza; --ustaw-baze robi bazą bieżący). --odnowa tworzy zbiór KI od nowa i robi
  bazą nowy przebieg (pytań i przypadków inwestora nie rusza). Wiersze KI, które przestały być widoczne
  (Nieaktualne, Ciekawostka, usunięte), wypadają z oceny („prawda ukryta”).
- dodaj: przypadek „to powinno się znaleźć” – od teraz każdy przebieg sprawdza, czy podane WI są w pierwszej 12.
- raport: liczby z logu zapytań (zero wyników, dopełnienia, wąskie wyniki, kanały, czasy), trend zbiorów oceny,
  ocena ręczna, ostatnie porównanie z Notion, niepotwierdzone alarmy (raport je potwierdza) i lista zapytań z logu
  bez wyników (kandydaci na synonimy).
- reczna: losuje pytania, zapisuje ich 5 pierwszych wyników (WI) i pyta o trafność każdego; tekst wyników pokazuje
  tylko, gdy stdout i stdin to terminal (higiena, nie zabezpieczenie: nie uruchamiaj jej przez `script` ani pty).
  Przerwane – wznawia się od miejsca przerwania; WI, których nie ma już w indeksie, pomija.
- notion: przybliżenie dawnej drogi „prosto do Notion” publicznym API (filtr `contains` na tezie, szczegółach i „dla
  naszej budowy”, AND słów, przy zerze OR) – to nie jest wyszukiwarka Notion MCP. Tylko odczyt, token z sekrety.env
  (nigdy nie drukowany), najwyżej --budzet żądań (z ponowieniami), odstęp 0,35 s; wypisuje i zapisuje same liczby.
- przypomnij: cisza, chyba że minęło 7 dni od ostatniego raportu, są niepotwierdzone alarmy albo obserwator nie działa
  (wtedy najwyżej raz w tygodniu). Raz w tygodniu sam robi przebieg zloty, gdy poprzedni trwał < 10 s; przebieg
  odrzucony (sync zmienił indeks) albo po czasie – kolejna próba po dobie. Zawsze kod 0.

Dane (poza repo, katalog 700, pliki 600, obok indeksu – domyślnie `.dom/wiedza/`):
- `szukaj.log.jsonl` (+ `szukaj.log.1.jsonl`) – log zapytań pisany przez `wiedza.py szukaj`;
- `jakosc/ki.json` (zbiór KI), `jakosc/pytania.json` (pytania i predykaty), `jakosc/wlasne.json` (przypadki z `dodaj`),
  `jakosc/reczna-*.jsonl` (oceny ręczne), `jakosc/historia.sqlite` (przebiegi, wyniki per zapytanie, alarmy).
Wyjście: liczby, numery WI, rangi, czasy i ID zapytań; tekst – wyłącznie zapytania z logu (wpisane przez inwestora
i agentów) oraz, w terminalu, wyniki oceny ręcznej. Zapytań z czatu na telefonie log nie zbiera (kopia w sandboksie).
"""
import argparse
import contextlib
import functools
import hashlib
import json
import os
import random
import re
import sqlite3
import statistics
import sys
import tempfile
import time
import unicodedata
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
TU = Path(__file__).resolve().parent
sys.path.insert(0, str(TU))
try:
    import wiedza as W  # noqa: E402
except Exception:  # noqa: BLE001 – przypomnij (hook) ma milczeć także wtedy
    W = None

DOMYSLNE_PYTANIA = TU / "wiedza_jakosc_pytania.json"
HISTORIA_WERSJA = 2
TOP = 12
KI_WIERSZE = 80                 # wierszy w próbie zbioru KI (ok. 16 zapytań na wiersz)
KI_ZIARNO = 17
CO_ILE_DNI = 7                  # raport, automatyczny przebieg złoty, komunikat o awarii obserwatora
ZLOTY_AUTO_S = 10.0             # przypomnij robi przebieg sam tylko, gdy mieści się w tylu sekundach
PONOW_AUTO_H = 24               # po odrzuconym albo zbyt długim auto-przebiegu
PROG_KI_PKT = 5.0               # alarm: KI success@12 spada o więcej punktów procentowych niż tyle
PROG_TEMATY_PKT = 2             # alarm: suma P@12 tematów spada o więcej niż tyle
PROG_PYTANIE_PKT = 3            # alarm: pytanie traci co najmniej tyle punktów P@12
PROG_ZERO_X = 2.0               # alarm: odsetek zapytań bez wyników ≥ tyle × poprzednie 4 tygodnie …
ZERO_MIN_ODSETEK = 0.05         # … liczone od co najmniej 5% (z 0% każdy przypadek byłby „wzrostem”)
ZERO_MIN_ZAPYTAN = 20           # … i tylko przy tylu zapytaniach w obu okresach
ZERO_POPRZEDNIE_DNI = 28
LUKA_LOGU_DNI = 7               # alarm: ostatni wpis logu starszy niż tyle dni
NOTION_REZERWA = 2              # żądań: krótszej reszty budżetu nie zaczynamy nowego zapytania

FILTR = argparse.Namespace(etap=None, istotnosc=None, status=None, rodzaj=None, temat=None, ciekawostki=False)
PERTURBACJE = ("baza", "odmiana", "bez_diakr", "rama", "wypelniacz", "czasownik_rzadki", "kolejnosc", "naturalne")
RAMY = ("czy {}", "jak {}", "co wiemy o {}", "czy warto {}", "jaki {}", "{} – co z tym")
WYPELNIACZE = ("trzeba", "można", "dobrze", "zawsze", "bardzo", "lepiej", "robić", "potrzebny", "musi", "zrobić")
# czasowniki i przysłówki pytań: szum rzadki (KI) i test czasowników; kolejność po sortowaniu wyznacza ID V..
CZASOWNIKI = ("stać", "leżeć", "postawić", "położyć", "wolno", "wylać", "kłaść", "dać", "użyć", "wybrać",
              "sprawdzić", "zastosować", "kupić", "montować", "wykonać", "zabezpieczyć", "ułożyć", "zmienić",
              "opłaca", "szybko", "dokładnie", "bezpośrednio", "wystarczy", "powinno", "nadaje")
ZAMIANY = (("owie", "ów"), ("ami", "ach"), ("ach", "ami"), ("ego", "ym"), ("emu", "ego"), ("ów", "y"),
           ("ej", "a"), ("ym", "ego"), ("ie", "a"), ("ia", "ii"), ("a", "ę"), ("ę", "a"), ("ą", "a"),
           ("y", "ów"), ("e", "ach"), ("i", "ach"), ("o", "u"), ("u", "em"))
ZESTAW_CZASOWNIKOW = "KLUCZOWE8"
ZESTAWY_STALE = ("KI", "TEMATY", "CZASOWNIKI", "WLASNE")   # pozostałe zestawy to pytania

TABELE = """
CREATE TABLE IF NOT EXISTS meta (klucz TEXT PRIMARY KEY, wartosc TEXT);
CREATE TABLE przebiegi (id INTEGER PRIMARY KEY, ts TEXT NOT NULL, rodzaj TEXT NOT NULL, modul_sha TEXT, odcisk TEXT,
    baza INTEGER NOT NULL DEFAULT 0, metryki TEXT NOT NULL);
CREATE TABLE wyniki (przebieg INTEGER NOT NULL, zestaw TEXT NOT NULL, zapytanie TEXT NOT NULL, wartosc REAL NOT NULL,
    ranga INTEGER, PRIMARY KEY (przebieg, zapytanie));
CREATE TABLE alarmy (klucz TEXT PRIMARY KEY, tekst TEXT NOT NULL, przebieg INTEGER, ts TEXT NOT NULL,
    potwierdzony INTEGER NOT NULL DEFAULT 0);
"""
MIGRACJA_1 = """
ALTER TABLE przebiegi RENAME TO przebiegi_v1;
ALTER TABLE wyniki RENAME TO wyniki_v1;
""" + TABELE + """
INSERT INTO przebiegi SELECT id, ts, rodzaj, modul_sha, indeks_zbudowano, baza, metryki FROM przebiegi_v1;
INSERT INTO wyniki SELECT przebieg, '', zapytanie, wartosc, ranga FROM wyniki_v1;
DROP TABLE przebiegi_v1;
DROP TABLE wyniki_v1;
DELETE FROM meta WHERE klucz = 'alarmy_widziane';
"""


class BladJakosci(Exception):
    """Komunikat dla inwestora (bez wartości pól)."""


class PrzekroczonyCzas(Exception):
    pass


class IndeksZmieniony(Exception):
    """Sync zmienił dane indeksu w trakcie przebiegu (hooki startu działają równolegle) – przebieg nie jest zapisywany."""


class BudzetWyczerpany(Exception):
    pass


def teraz() -> datetime:
    return datetime.now(timezone.utc)


def teraz_iso() -> str:
    return teraz().isoformat(timespec="seconds")


def dawno(ts, dni: float) -> bool:
    """Brak, nieczytelny, starszy niż `dni` albo z przyszłości (zły zegar) → True."""
    try:
        wiek = teraz() - W.na_czas(ts)
    except (TypeError, ValueError, AttributeError):
        return True
    return wiek > timedelta(days=dni) or wiek < timedelta(0)


def skrot(tekst: str, n: int = 4) -> str:
    return hashlib.sha256(tekst.encode("utf-8")).hexdigest()[:n]


# ------------------------------------------------------------------ miejsca i pliki
class Miejsca:
    """Ścieżki obserwatora dla indeksu z --db albo domyślnego."""

    def __init__(self, a):
        self.baza = W.sciezka_bazy(a)
        katalog = self.baza.parent
        self.dane = katalog / "jakosc"
        self.log, self.log_stary = katalog / W.PLIK_LOGU, katalog / W.PLIK_LOGU_STARY
        self.historia = self.dane / "historia.sqlite"
        self.ki, self.pytania, self.wlasne = self.dane / "ki.json", self.dane / "pytania.json", self.dane / "wlasne.json"
        self.awaria = self.dane / ".awaria"

    def dozwolone(self) -> bool:
        """Dane obserwatora (słowa wierszy, zapytania inwestora) tylko w `<hub>/.dom/wiedza/` poza repo."""
        katalog = self.baza.resolve().parent
        return (katalog.name == "wiedza" and katalog.parent.name == ".dom"
                and W.REPO.resolve() not in katalog.parents)

    def przygotuj(self):
        """Katalog danych (700) – tylko obok istniejącego indeksu; katalogu indeksu nigdy nie tworzy."""
        if not self.dozwolone():
            raise BladJakosci("dane obserwatora zapisuję tylko obok indeksu w <hub>/.dom/wiedza/ (poza repo) – "
                              "--db wskazuje inne miejsce")
        if not self.baza.is_file():
            raise BladJakosci(f"brak pliku indeksu {self.baza.name} – uruchom python3 tools/wiedza.py sync")
        self.dane.mkdir(mode=0o700, exist_ok=True)
        zaostrz(self.dane)


def zaostrz(katalog: Path):
    """Katalog 700, pliki w nim 600 (także przeniesione albo skopiowane); błąd tylko pomija plik."""
    for p, tryb in [(katalog, 0o700)] + [(p, 0o600) for p in katalog.iterdir() if p.is_file() and not p.is_symlink()]:
        with contextlib.suppress(OSError):
            if p.stat().st_mode & 0o777 != tryb:
                os.chmod(p, tryb)


def zapisz_plik(plik: Path, tekst: str):
    """Zapis przez unikalny plik tymczasowy (600) i os.replace – równoległe procesy nie depczą sobie po plikach."""
    fd, tymczasowy = tempfile.mkstemp(dir=str(plik.parent), prefix=plik.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(tekst)
        os.replace(tymczasowy, str(plik))
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tymczasowy)
        raise


def zapisz_json(plik: Path, obiekt):
    zapisz_plik(plik, json.dumps(obiekt, ensure_ascii=False))


def zapisz_jsonl(plik: Path, wiersze: list):
    zapisz_plik(plik, "".join(json.dumps(w, ensure_ascii=False) + "\n" for w in wiersze))


def czytaj_json(plik: Path, domyslnie):
    """Brak pliku → domyślnie; nieczytelny JSON → BladJakosci (decyzję podejmuje wołający)."""
    try:
        return json.loads(plik.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return domyslnie
    except (ValueError, UnicodeDecodeError):
        raise BladJakosci(f"{plik.name}: nieczytelny JSON") from None


def czytaj_jsonl(plik: Path) -> list:
    wynik = []
    for linia in plik.read_text(encoding="utf-8", errors="replace").splitlines():
        with contextlib.suppress(ValueError):
            if linia.strip():
                obiekt = json.loads(linia)
                if isinstance(obiekt, dict):
                    wynik.append(obiekt)
    return wynik


@contextlib.contextmanager
def blokada_przebiegu(m: Miejsca):
    """Wyłączna blokada `jakosc/.przebieg.lock` (inna niż blokada syncu): True – wzięta, False – trwa inny przebieg."""
    import fcntl
    fd = os.open(str(m.dane / ".przebieg.lock"), os.O_WRONLY | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            wzieta = True
        except BlockingIOError:
            wzieta = False
        yield wzieta
    finally:
        os.close(fd)


# ------------------------------------------------------------------ historia
def zestaw_z_id(zid: str) -> str:
    """Zestaw starego (schemat 1) ID wyniku – nowe wyniki mają zestaw zapisany wprost."""
    if zid.startswith("KI-"):
        return "KI"
    if zid.startswith("T-"):
        return "TEMATY"
    if re.fullmatch(r"V\d+-\d+", zid):
        return "CZASOWNIKI"
    if re.fullmatch(r"W\d+", zid):
        return "WLASNE"
    return zid.rsplit("-", 1)[0]


def otworz_historie(m: Miejsca) -> sqlite3.Connection:
    h = sqlite3.connect(str(m.historia), timeout=10)
    try:
        wersja = h.execute("PRAGMA user_version").fetchone()[0]
        if wersja > HISTORIA_WERSJA:
            raise BladJakosci("historia w nowszym schemacie – zaktualizuj wiedza_jakosc.py")
        if wersja < HISTORIA_WERSJA:
            with h:
                # instrukcje po kolei w jednej transakcji IMMEDIATE (executescript zatwierdziłby ją wcześniej)
                h.execute("BEGIN IMMEDIATE")
                wersja = h.execute("PRAGMA user_version").fetchone()[0]  # inny proces mógł już zmigrować
                for instrukcja in ({0: TABELE, 1: MIGRACJA_1}.get(wersja, "")).split(";"):
                    if instrukcja.strip():
                        h.execute(instrukcja)
                if wersja == 1:
                    stare = [z for (z,) in h.execute("SELECT DISTINCT zapytanie FROM wyniki")]
                    h.executemany("UPDATE wyniki SET zestaw = ? WHERE zapytanie = ?",
                                  [(zestaw_z_id(z), z) for z in stare])
                h.execute(f"PRAGMA user_version = {HISTORIA_WERSJA}")
        return h
    except BaseException:
        h.close()
        raise


def meta(h, klucz, domyslnie=None):
    r = h.execute("SELECT wartosc FROM meta WHERE klucz = ?", (klucz,)).fetchone()
    return r[0] if r else domyslnie


def ustaw_meta(h, klucz, wartosc):
    with h:
        h.execute("INSERT OR REPLACE INTO meta VALUES (?, ?)", (klucz, wartosc))


def przebiegi(h, rodzaj: str, limit: int = 2) -> list:
    return [{"id": i, "ts": ts, "baza": bool(b), "metryki": json.loads(mt)} for i, ts, b, mt in h.execute(
        "SELECT id, ts, baza, metryki FROM przebiegi WHERE rodzaj = ? ORDER BY id DESC LIMIT ?", (rodzaj, limit))]


def przebieg_bazowy(h):
    r = h.execute("SELECT id, ts, metryki FROM przebiegi WHERE rodzaj = 'zloty' AND baza = 1 "
                  "ORDER BY id DESC LIMIT 1").fetchone()
    return {"id": r[0], "ts": r[1], "metryki": json.loads(r[2])} if r else None


def wartosci(h, przebieg: int) -> dict:
    return {z: (zs, w) for zs, z, w in h.execute("SELECT zestaw, zapytanie, wartosc FROM wyniki WHERE przebieg = ?",
                                                  (przebieg,))}


def porownaj(nowe: dict, stare: dict) -> dict:
    wspolne = set(nowe) & set(stare)
    lepsze = sorted(k for k in wspolne if nowe[k][1] > stare[k][1])
    gorsze = sorted(k for k in wspolne if nowe[k][1] < stare[k][1])
    return {"lepsze": lepsze, "gorsze": gorsze, "remis": len(wspolne) - len(lepsze) - len(gorsze),
            "tylko_nowe": len(set(nowe) - set(stare))}


def alarmy_przebiegu(h, akt: int) -> list:
    """[(klucz, tekst)] przebiegu `akt` względem poprzedniego i bazowego – tylko na wspólnych ID zapytań."""
    poprzedni = h.execute("SELECT MAX(id) FROM przebiegi WHERE rodzaj = 'zloty' AND id < ?", (akt,)).fetchone()[0]
    baza = przebieg_bazowy(h)
    nowe, wynik = wartosci(h, akt), []
    for nazwa, inny in (("poprzedni", poprzedni), ("baza", baza["id"] if baza else None)):
        if inny is None or inny == akt or (nazwa == "baza" and inny == poprzedni):
            continue
        stare = wartosci(h, inny)
        wsp = set(nowe) & set(stare)

        def suma(zestaw, w):
            return sum(w[k][1] for k in wsp if w[k][0] == zestaw)
        n_ki = sum(1 for k in wsp if nowe[k][0] == "KI")
        etykieta = f"względem {'poprzedniego' if nazwa == 'poprzedni' else 'bazy'} #{inny}"
        if n_ki and 100 * (suma("KI", stare) - suma("KI", nowe)) / n_ki > PROG_KI_PKT:
            wynik.append((f"ki12-{nazwa}#{akt}", f"KI success@12 spadło o "
                                                 f"{100 * (suma('KI', stare) - suma('KI', nowe)) / n_ki:.1f} pkt "
                                                 f"{etykieta} (#{akt}, próg {PROG_KI_PKT:g})"))
        if suma("TEMATY", stare) - suma("TEMATY", nowe) > PROG_TEMATY_PKT:
            wynik.append((f"tematy-{nazwa}#{akt}", f"tematy P@12 spadły o "
                                                   f"{suma('TEMATY', stare) - suma('TEMATY', nowe):.0f} {etykieta}"))
        pytania = sorted(k for k in wsp if nowe[k][0] not in ZESTAWY_STALE
                         and stare[k][1] - nowe[k][1] >= PROG_PYTANIE_PKT)
        if pytania:
            wynik.append((f"pytania-{nazwa}#{akt}", f"{len(pytania)} pytań straciło ≥ {PROG_PYTANIE_PKT} pkt P@12 "
                                                    f"{etykieta}: " + ", ".join(pytania[:10])))
        wlasne = sorted(k for k in wsp if nowe[k][0] == "WLASNE" and nowe[k][1] < stare[k][1])
        if wlasne:
            wynik.append((f"wlasne-{nazwa}#{akt}", f"przypadki inwestora gorsze {etykieta}: " + ", ".join(wlasne)))
    return wynik


def zapisz_alarmy(h, alarmy: list, przebieg=None):
    with h:
        h.executemany("INSERT OR IGNORE INTO alarmy (klucz, tekst, przebieg, ts) VALUES (?, ?, ?, ?)",
                      [(k, t, przebieg, teraz_iso()) for k, t in alarmy])


def otwarte_alarmy(h) -> list:
    return [{"klucz": k, "tekst": t, "ts": ts} for k, t, ts in h.execute(
        "SELECT klucz, tekst, ts FROM alarmy WHERE potwierdzony = 0 ORDER BY ts, klucz")]


# ------------------------------------------------------------------ korpus (tylko w pamięci, nigdy nie drukowany)
class Korpus:
    def __init__(self, conn):
        self.nazwy_tematow = dict(conn.execute("SELECT id, nazwa FROM tematy"))
        self.tematy_wi = {}
        for wi, tid in conn.execute("SELECT wi, temat_id FROM informacje_tematy"):
            self.tematy_wi.setdefault(wi, set()).add(tid)
        self.tekst, self.widoczny, self.warstwa, self.pola = {}, {}, {}, {}
        for wi, teza, szcz, dla, ist, st, etap in conn.execute(
                "SELECT wi, teza, szczegoly, dla_nas, istotnosc, status, etap FROM informacje"):
            nazwy = [self.nazwy_tematow.get(t) or "" for t in self.tematy_wi.get(wi, ())]
            self.pola[wi] = (teza or "", szcz or "")
            self.tekst[wi] = W.bez_diakrytykow(" ".join([teza or "", szcz or "", dla or ""] + nazwy))
            self.widoczny[wi] = W.normalizuj(st) != "nieaktualne" and W.normalizuj(ist) != "ciekawostka"
            self.warstwa[wi] = (W.normalizuj(ist), W.normalizuj(etap))
        self.n = len(self.tekst)

    def predykat(self, wzory: list):
        rx = [re.compile(r"\b(?:%s)" % w) for w in wzory]
        return lambda wi: all(r.search(self.tekst.get(wi, "")) for r in rx)

    def trafne(self, pred) -> set:
        return {wi for wi in self.tekst if self.widoczny[wi] and pred(wi)}

    def tematy(self) -> list:
        """[(ID, nazwa – tylko w pamięci, zbiór widocznych WI z relacją)] – ID stałe: skrót ID strony tematu."""
        wynik = []
        for tid, nazwa in sorted(self.nazwy_tematow.items()):
            oczek = {wi for wi, ts in self.tematy_wi.items() if tid in ts and self.widoczny.get(wi)}
            if oczek and (nazwa or "").strip():
                wynik.append(("T-" + skrot(tid, 6), nazwa, oczek))
        return wynik


def odcisk_indeksu(conn) -> str:
    """Stan danych indeksu: sync bez zmian go nie zmienia (w przeciwieństwie do meta.zbudowano)."""
    stan = sorted(conn.execute("SELECT baza, ostatnie_zmieniono, wierszy FROM sync_stan"))
    dane = [stan, W.meta_bazy(conn).get("synonimy_sha"), conn.execute("PRAGMA user_version").fetchone()[0]]
    return skrot(json.dumps(dane, ensure_ascii=False), 16)


# ------------------------------------------------------------------ zbiory
def odmien(s: str) -> str:
    for koncowka, zamiana in ZAMIANY:
        if s.endswith(koncowka) and len(s) - len(koncowka) >= 3:
            return s[:len(s) - len(koncowka)] + zamiana
    return s + ("u" if s[-1] not in "aeiouyąę" else "")


def deterministycznie(*czesci) -> int:
    return int(hashlib.sha256("|".join(map(str, czesci)).encode()).hexdigest(), 16)


def df_slowa(conn, slowo: str) -> int:
    termin = W.termin_tokenu(W.normalizuj(slowo), False)
    return conn.execute("SELECT COUNT(*) FROM informacje_fts WHERE informacje_fts MATCH ?", (termin,)).fetchone()[0]


def zbuduj_ki(conn, K: Korpus, wierszy: int = KI_WIERSZE, ziarno: int = KI_ZIARNO) -> dict:
    """Zbiór known-item: próba warstwowa (istotność × etap) widocznych wierszy; z tezy i szczegółów 2–3 słowa
    o najmniejszym df (2 – 15% N, „rzadkie”) albo df 5–100 („tematyczne”), do tego perturbacje. Prawda = wiersz.
    ID = wiersz, tryb, perturbacja i skrót zapytania: po odnowieniu to samo ID znaczy to samo zapytanie."""
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS temp.slownik USING fts5vocab(main, informacje_fts, row)")
    df = dict(conn.execute("SELECT term, doc FROM temp.slownik"))
    rzadkie_cz = [v for v in sorted(set(CZASOWNIKI)) if 3 <= df_slowa(conn, v) <= 40]
    widoczne = [wi for wi in sorted(K.tekst) if K.widoczny[wi]]
    warstwy = {}
    for wi in widoczne:
        warstwy.setdefault(K.warstwa[wi], []).append(wi)
    los = random.Random(ziarno)
    proba = []
    for klucz in sorted(warstwy):
        grupa = warstwy[klucz]
        proba += los.sample(grupa, min(max(1, round(wierszy * len(grupa) / max(1, len(widoczne)))), len(grupa)))
    zapytania = []
    for wi in sorted(set(proba)):
        teza, szcz = K.pola[wi]
        kand = {}
        for s in re.findall(r"\w+", W.normalizuj(teza + " " + szcz)):
            b = W.bez_diakrytykow(s)
            d = df.get(b, 0)
            if s.isalpha() and len(s) >= 4 and b not in W.STOP_ZAPYTANIA and 2 <= d <= 0.15 * K.n and b not in kand:
                kand[b] = (d, s)
        if len(kand) < 2:
            continue
        po_df = sorted(kand.values())
        ile = 2 + deterministycznie(wi, "ile") % 2
        for tryb, toks in (("r", [s for _, s in po_df[:ile]]), ("t", [s for d, s in po_df if 5 <= d <= 100][:ile])):
            if len(toks) < 2:
                continue
            szum = [v for v in rzadkie_cz if not re.search(r"\b" + W.bez_diakrytykow(v)[:4], K.tekst[wi])]
            h = deterministycznie(wi, tryb)
            rama, wyp = RAMY[h % len(RAMY)], WYPELNIACZE[h % len(WYPELNIACZE)]
            warianty = {"baza": " ".join(toks), "odmiana": " ".join(odmien(t) for t in toks),
                        "bez_diakr": W.bez_diakrytykow(" ".join(toks)), "rama": rama.format(" ".join(toks)),
                        "wypelniacz": " ".join(toks[:1] + [wyp] + toks[1:]), "kolejnosc": " ".join(reversed(toks))}
            if szum:
                cz = szum[h % len(szum)]
                warianty["czasownik_rzadki"] = " ".join(toks[:1] + [cz] + toks[1:])
                warianty["naturalne"] = rama.format(" ".join([odmien(toks[0]), cz] + [odmien(t) for t in toks[1:]]))
            for pert, q in warianty.items():
                zapytania.append({"id": f"KI-{wi}-{tryb}-{pert}-{skrot(q)}", "wi": wi, "tryb": tryb, "pert": pert,
                                  "q": q})
    return {"wersja": 2, "utworzono": teraz_iso(), "informacji": K.n,
            "wierszy": len({z["wi"] for z in zapytania}), "ziarno": ziarno, "zapytania": zapytania}


def uaktualnij_ki(m: Miejsca, ki: dict) -> dict:
    """Zbiór KI w wersji 1 (ID bez skrótu zapytania): nowe ID w pliku i te same zmiany w historii."""
    if ki.get("wersja", 1) >= 2:
        return ki
    zmiany = []
    for z in ki["zapytania"]:
        nowe = f"{z['id']}-{skrot(z['q'])}"
        zmiany.append((nowe, z["id"]))
        z["id"] = nowe
    h = otworz_historie(m)
    try:
        with h:
            h.executemany("UPDATE wyniki SET zapytanie = ? WHERE zapytanie = ?", zmiany)
    finally:
        h.close()
    ki["wersja"] = 2
    zapisz_json(m.ki, ki)
    return ki


def wczytaj_pytania(m: Miejsca, ostrzezenia: list) -> dict:
    """Zestawy pytań z danych; brak pliku → kopia domyślnego z tools/; nieczytelny → domyślny w pamięci."""
    if not m.pytania.exists() and DOMYSLNE_PYTANIA.is_file():
        zapisz_plik(m.pytania, DOMYSLNE_PYTANIA.read_text(encoding="utf-8"))
    try:
        zestawy = czytaj_json(m.pytania, {}).get("zestawy", {})
        for lista in zestawy.values():
            for p in lista:
                re.compile(r"\b(?:%s)" % "|".join(p["wzory"]))
                str(p["q"])
        return zestawy
    except (BladJakosci, AttributeError, KeyError, TypeError, re.error):
        ostrzezenia.append("pytania.json nieczytelny – używam domyślnego zestawu z tools/ (plik zostaje)")
        return json.loads(DOMYSLNE_PYTANIA.read_text(encoding="utf-8")).get("zestawy", {})


def zbiory_oceny(m: Miejsca, conn, K: Korpus, odnowa: bool, ostrzezenia: list) -> tuple:
    """({zestaw: [(ID, zapytanie, miara, prawda)]}, ukrytych wierszy KI, zbiór KI)."""
    ki = None
    if not odnowa:
        try:
            ki = czytaj_json(m.ki, None)
            if ki is not None:
                if not all(isinstance(z.get("q"), str) and isinstance(z.get("wi"), int) and "id" in z
                           for z in ki["zapytania"]):
                    raise KeyError("zapytania")
                ki = uaktualnij_ki(m, ki)
        except (BladJakosci, KeyError, TypeError):
            ostrzezenia.append("ki.json nieczytelny – zbiór KI od nowa (porównania KI tylko na wspólnych ID)")
            ki = None
    if ki is None:
        ki = zbuduj_ki(conn, K)
        zapisz_json(m.ki, ki)
    widoczne = [z for z in ki["zapytania"] if K.widoczny.get(z["wi"])]
    zb = {"KI": [(z["id"], z["q"], "ki", z["wi"]) for z in widoczne],
          "TEMATY": [(t, nazwa, "zbior", oczek) for t, nazwa, oczek in K.tematy()]}
    pytania = wczytaj_pytania(m, ostrzezenia)
    pamiec = {}

    def prawda(wzory):
        klucz = tuple(wzory)
        if klucz not in pamiec:
            pred = K.predykat(wzory)
            pamiec[klucz] = (pred, len(K.trafne(pred)))
        return pamiec[klucz]
    for nazwa, lista in pytania.items():
        if nazwa not in ZESTAWY_STALE:
            zb[nazwa] = [(f"{nazwa}-{j + 1:02d}", p["q"], "pred", prawda(p["wzory"])) for j, p in enumerate(lista)]
    if ZESTAW_CZASOWNIKOW in pytania:
        zb["CZASOWNIKI"] = []
        for vi, v in enumerate(sorted(set(CZASOWNIKI))):
            for qi, p in enumerate(pytania[ZESTAW_CZASOWNIKOW]):
                slowa = p["q"].split()
                zb["CZASOWNIKI"].append((f"V{vi:02d}-{qi}", " ".join(["czy", slowa[0], v] + slowa[1:]), "pred",
                                         prawda(p["wzory"])))
    try:
        zb["WLASNE"] = [(w["id"], w["q"], "wlasne", set(w["wi"])) for w in czytaj_json(m.wlasne, [])]
    except (BladJakosci, KeyError, TypeError):
        ostrzezenia.append("wlasne.json nieczytelny – przypadki inwestora pominięte (plik zostaje)")
    return {k: v for k, v in zb.items() if v}, len({z["wi"] for z in ki["zapytania"]} - {z["wi"] for z in widoczne}), ki


@contextlib.contextmanager
def szybka_normalizacja():
    """normalizuj to czysta funkcja: w serii tysięcy zapytań zapamiętane wyniki dają te same listy WI kilka razy
    szybciej (wybierz normalizuje pola filtrów wszystkich wierszy przy każdym wywołaniu)."""
    oryginal = W.normalizuj
    W.normalizuj = functools.lru_cache(maxsize=None)(oryginal)
    try:
        yield
    finally:
        W.normalizuj = oryginal


def szukaj_listy(conn, q: str) -> list:
    return W.wyszukaj(conn, q, FILTR)[0] if W.zbuduj_zapytanie_fts(q, "AND") else []


def ocen_zapytanie(lista: list, miara: str, prawda) -> tuple:
    """(wartość, ranga, P@12): ki – trafienie w TOP (1/0) i ranga wiersza; zbior/pred – P@12 przeskalowane do 12
    trafnych możliwych (zbiór prawdy mniejszy niż 12 po ukryciu wierszy nie daje fałszywego spadku); wlasne – udział
    WI w TOP. Prawda pred to (predykat, liczba trafnych widocznych)."""
    top = lista[:TOP]
    if miara == "ki":
        r = lista.index(prawda) + 1 if prawda in lista else None
        return (1.0 if r is not None and r <= TOP else 0.0), r, None
    if miara in ("zbior", "pred"):
        p12 = sum(x in prawda for x in top) if miara == "zbior" else sum(1 for x in top if prawda[0](x))
        mozliwe = min(TOP, len(prawda) if miara == "zbior" else prawda[1])
        return (TOP * p12 / mozliwe if mozliwe else 0.0), None, p12
    rangi = [lista.index(w) + 1 for w in prawda if w in lista]
    return sum(1 for r in rangi if r <= TOP) / max(1, len(prawda)), (min(rangi) if rangi else None), None


def uruchom_zbiory(conn, zb: dict, termin=None) -> tuple:
    """({ID: (zestaw, wartość, ranga)}, {ID: (liczba trafień, P@12)}, sekundy) – przez wiedza.wyszukaj w procesie."""
    wart, trafien = {}, {}
    t0 = time.monotonic()
    with szybka_normalizacja():
        for i, (zestaw, (zid, q, miara, prawda)) in enumerate((n, z) for n, lista in zb.items() for z in lista):
            if termin is not None and i % 50 == 0 and time.monotonic() > termin:
                raise PrzekroczonyCzas()
            lista = szukaj_listy(conn, q)
            wartosc, ranga, p12 = ocen_zapytanie(lista, miara, prawda)
            wart[zid] = (zestaw, wartosc, ranga)
            trafien[zid] = (len(lista), p12)
    return wart, trafien, time.monotonic() - t0


def metryki_zbiorow(zb: dict, wart: dict, trafien: dict, K: Korpus, sekundy: float, ukryte: int) -> dict:
    met = {"czas_s": round(sekundy, 2), "informacji": K.n, "zero": sum(1 for n, _ in trafien.values() if n == 0),
           "skala": 2}
    if "KI" in zb:
        ids = [z[0] for z in zb["KI"]]
        met["ki"] = {"n": len(ids), "s12": round(100 * sum(wart[i][1] for i in ids) / len(ids), 2),
                     "mrr": round(sum(1 / wart[i][2] for i in ids if wart[i][2]) / len(ids), 4),
                     "wierszy": len({z[3] for z in zb["KI"]}), "prawda_ukryta": ukryte,
                     "perturbacje": {p: round(100 * statistics.mean(wart[i][1] for i in ids if f"-{p}-" in i), 1)
                                     for p in PERTURBACJE if any(f"-{p}-" in i for i in ids)}}
    for nazwa, lista in zb.items():
        if nazwa == "WLASNE":
            met["wlasne"] = {"n": len(lista), "znalezione": sum(1 for z in lista if wart[z[0]][1] >= 1)}
        elif nazwa == "TEMATY":
            met["tematy"] = {"n": len(lista), "p12": sum(trafien[z[0]][1] for z in lista),
                             "maks": sum(min(TOP, len(z[3])) for z in lista)}
        elif nazwa != "KI":
            met.setdefault("pytania", {})[nazwa] = {"n": len(lista), "p12": sum(trafien[z[0]][1] for z in lista),
                                                    "maks": TOP * len(lista)}
    return met


def przeskaluj_stare(m: Miejsca, zb: dict):
    """Przebiegi zloty sprzed schematu 2 trzymały surowe P@12 tematów i pytań; jednorazowo przelicza je na skalę
    12 możliwych trafnych (bieżące zbiory prawdy), żeby porównania z bazą nie mieszały jednostek."""
    mozliwe = {zid: min(TOP, len(prawda) if miara == "zbior" else prawda[1])
               for lista in zb.values() for zid, _, miara, prawda in lista if miara in ("zbior", "pred")}
    h = otworz_historie(m)
    try:
        stare = [(i, json.loads(mt)) for i, mt in h.execute("SELECT id, metryki FROM przebiegi WHERE rodzaj = 'zloty'")
                 if json.loads(mt).get("skala") != 2]
        with h:
            for nr, met in stare:
                if "prawda_ukryta" not in met.get("ki", {}):   # przebieg ze schematu 1 (surowe P@12)
                    h.executemany("UPDATE wyniki SET wartosc = ? * wartosc / ? WHERE przebieg = ? AND zapytanie = ?",
                                  [(TOP, n, nr, zid) for zid, n in mozliwe.items() if n])
                h.execute("UPDATE przebiegi SET metryki = ? WHERE id = ?", (json.dumps(dict(met, skala=2)), nr))
    finally:
        h.close()


def zapisz_przebieg(m: Miejsca, rodzaj: str, met: dict, wart: dict, odcisk: str, ustaw_baze: bool = False) -> tuple:
    """(numer przebiegu, czy baza, alarmy) – przebieg, wyniki i alarmy w jednej transakcji."""
    modul = skrot(Path(W.__file__).read_text(encoding="utf-8"), 12)
    h = otworz_historie(m)
    try:
        with h:
            h.execute("BEGIN IMMEDIATE")
            baza = rodzaj == "zloty" and (ustaw_baze or przebieg_bazowy(h) is None)
            if baza:
                h.execute("UPDATE przebiegi SET baza = 0 WHERE rodzaj = 'zloty'")
            nr = h.execute("INSERT INTO przebiegi (ts, rodzaj, modul_sha, odcisk, baza, metryki) VALUES "
                           "(?, ?, ?, ?, ?, ?)", (teraz_iso(), rodzaj, modul, odcisk, int(baza), json.dumps(met))
                           ).lastrowid
            h.executemany("INSERT INTO wyniki VALUES (?, ?, ?, ?, ?)",
                          [(nr, zs, k, v, r) for k, (zs, v, r) in wart.items()])
        alarmy = alarmy_przebiegu(h, nr) if rodzaj == "zloty" else []
        zapisz_alarmy(h, alarmy, nr)
        return nr, baza, alarmy
    finally:
        h.close()


# ------------------------------------------------------------------ log
def poprawny_rekord(r: dict) -> bool:
    return (isinstance(r.get("ts"), str) and isinstance(r.get("trafien"), int) and isinstance(r.get("q"), str)
            and isinstance(r.get("ms"), (int, float)) and isinstance(r.get("tryb"), str))


def czytaj_log(m: Miejsca, od: datetime) -> list:
    """Rekordy logu od `od`; wiersze uszkodzone albo z polami innego typu są pomijane."""
    wynik = []
    for plik in (m.log_stary, m.log):
        if not plik.is_file():
            continue
        for r in czytaj_jsonl(plik):
            with contextlib.suppress(ValueError, TypeError, AttributeError):
                if poprawny_rekord(r) and W.na_czas(r["ts"]) >= od:
                    wynik.append(r)
    return wynik


def statystyki_logu(rekordy: list) -> dict:
    n = len(rekordy)
    if not n:
        return {"n": 0}
    kanaly = {}
    for r in rekordy:
        kanaly[str(r.get("kanal"))] = kanaly.get(str(r.get("kanal")), 0) + 1
    ms = sorted(float(r["ms"]) for r in rekordy)
    return {"n": n, "kanaly": kanaly, "zero": sum(r["trafien"] == 0 for r in rekordy) / n,
            "dopelnienie": sum(r["tryb"] in ("AND+dopelnienie", "OR-only") for r in rekordy) / n,
            "or_only": sum(r["tryb"] == "OR-only" for r in rekordy) / n,
            "waskie": sum(0 < r["trafien"] < 5 for r in rekordy) / n,
            "mediana_trafien": statistics.median(r["trafien"] for r in rekordy),
            "ms_mediana": round(statistics.median(ms), 1), "ms_p90": round(ms[min(n - 1, int(0.9 * n))], 1)}


def alarmy_logu(m: Miejsca, dni: int) -> tuple:
    """(alarmy, statystyki okna, statystyki poprzednich 4 tygodni, rekordy okna)."""
    granica = teraz() - timedelta(days=dni)
    wszystkie = czytaj_log(m, granica - timedelta(days=ZERO_POPRZEDNIE_DNI))
    okno = [r for r in wszystkie if W.na_czas(r["ts"]) >= granica]
    s, s0 = statystyki_logu(okno), statystyki_logu([r for r in wszystkie if W.na_czas(r["ts"]) < granica])
    wynik = []
    if (s["n"] >= ZERO_MIN_ZAPYTAN and s0["n"] >= ZERO_MIN_ZAPYTAN
            and s["zero"] >= PROG_ZERO_X * max(s0["zero"], ZERO_MIN_ODSETEK)):
        wynik.append((f"zero#{teraz():%G-W%V}", f"zapytania bez wyników: {100 * s['zero']:.0f}% wobec "
                                                f"{100 * s0['zero']:.0f}% w poprzednich 4 tygodniach"))
    if not wszystkie:
        wszystkie = czytaj_log(m, datetime.min.replace(tzinfo=timezone.utc))
    ostatni = max((W.na_czas(r["ts"]) for r in wszystkie), default=None)
    if ostatni is not None and teraz() - ostatni > timedelta(days=LUKA_LOGU_DNI):
        wynik.append((f"log#{ostatni:%Y-%m-%d}", f"luka w logu: ostatnie zapytanie {(teraz() - ostatni).days} dni "
                                                 "temu (WIEDZA_LOG=0? brak sesji i nocnych przebiegów?)"))
    return wynik, s, s0, okno


# ------------------------------------------------------------------ zloty
def przebieg_zloty(m: Miejsca, odnowa: bool = False, ustaw_baze: bool = False, termin=None) -> dict:
    """Przebieg pod blokadą przebiegu (wołający); odrzucony, gdy sync zmienił dane indeksu w trakcie."""
    ostrzezenia = []
    with contextlib.closing(W.otworz_db(m.baza, zapis=False)) as conn:
        odcisk = odcisk_indeksu(conn)
        K = Korpus(conn)
        zb, ukryte, ki = zbiory_oceny(m, conn, K, odnowa, ostrzezenia)
        wart, trafien, sek = uruchom_zbiory(conn, zb, termin)
        if odcisk_indeksu(conn) != odcisk:
            raise IndeksZmieniony("dane indeksu zmieniły się w trakcie przebiegu (sync) – uruchom zloty ponownie")
    met = metryki_zbiorow(zb, wart, trafien, K, sek, ukryte)
    przeskaluj_stare(m, zb)
    nr, baza, alarmy = zapisz_przebieg(m, "zloty", met, wart, odcisk, ustaw_baze or odnowa)
    zaostrz(m.dane)
    return {"id": nr, "baza": baza, "metryki": met, "alarmy": alarmy, "ostrzezenia": ostrzezenia,
            "ki_informacji": ki.get("informacji")}


def opis_metryk(met: dict) -> str:
    cz = []
    if "ki" in met:
        cz.append(f"KI success@12 {met['ki']['s12']:.1f}% · MRR {met['ki']['mrr']:.3f}"
                  + (f" (prawda ukryta: {met['ki']['prawda_ukryta']} wierszy)" if met["ki"].get("prawda_ukryta") else ""))
    if "tematy" in met:
        cz.append(f"tematy P@12 {met['tematy']['p12']}/{met['tematy']['maks']}")
    pyt = {k: v for k, v in met.get("pytania", {}).items() if k != "CZASOWNIKI"}
    if pyt:
        cz.append("pytania P@12 " + ", ".join(f"{k} {v['p12']}/{v['maks']}" for k, v in pyt.items()))
    if "CZASOWNIKI" in met.get("pytania", {}):
        v = met["pytania"]["CZASOWNIKI"]
        cz.append(f"czasowniki {v['p12']}/{v['maks']}")
    if "wlasne" in met:
        cz.append(f"przypadki inwestora {met['wlasne']['znalezione']}/{met['wlasne']['n']}")
    cz.append(f"zero wyników {met['zero']}")
    return " · ".join(cz)


def opis_porownania(etykieta: str, p: dict) -> str:
    def lista(ids):
        return ", ".join(ids[:15]) + (f" … (+{len(ids) - 15})" if len(ids) > 15 else "")
    tekst = f"  vs {etykieta}: lepsze {len(p['lepsze'])}, gorsze {len(p['gorsze'])}, bez zmian {p['remis']}"
    tekst += (f" · kod szukaj: {'zmieniony' if p['kod_zmieniony'] else 'bez zmian'}, dane indeksu: "
              f"{'zmienione' if p['indeks_zmieniony'] else 'bez zmian'}")
    if p["tylko_nowe"]:
        tekst += f" (nowe ID {p['tylko_nowe']} – porównanie na wspólnych)"
    if p["gorsze"]:
        tekst += f"\n    gorsze: {lista(p['gorsze'])}"
    if p["lepsze"]:
        tekst += f"\n    lepsze: {lista(p['lepsze'])}"
    return tekst


def zmiany_miedzy(h, akt: int, inny: int) -> dict:
    """Czy między przebiegami zmienił się kod szukaj (wiedza.py) albo dane indeksu – podpowiedź do alarmu."""
    a, b = (h.execute("SELECT modul_sha, odcisk FROM przebiegi WHERE id = ?", (i,)).fetchone() for i in (akt, inny))
    return {"kod_zmieniony": a[0] != b[0], "indeks_zmieniony": a[1] != b[1]}


def porownania(h, akt: int) -> dict:
    nowe, wynik = wartosci(h, akt), {}
    poprzedni = h.execute("SELECT MAX(id) FROM przebiegi WHERE rodzaj = 'zloty' AND id < ?", (akt,)).fetchone()[0]
    baza = przebieg_bazowy(h)
    if poprzedni:
        wynik[f"poprzedni #{poprzedni}"] = dict(porownaj(nowe, wartosci(h, poprzedni)), **zmiany_miedzy(h, akt, poprzedni))
    if baza and baza["id"] not in (akt, poprzedni):
        wynik[f"baza #{baza['id']} ({baza['ts'][:10]})"] = dict(porownaj(nowe, wartosci(h, baza["id"])),
                                                              **zmiany_miedzy(h, akt, baza["id"]))
    return wynik


def cmd_zloty(a) -> int:
    m = Miejsca(a)
    m.przygotuj()
    with blokada_przebiegu(m) as wolna:
        if not wolna:
            print("[jakosc] inny przebieg obserwatora trwa – spróbuj za chwilę")
            return 0
        wynik = przebieg_zloty(m, a.odnowa, a.ustaw_baze)
    h = otworz_historie(m)
    try:
        por = porownania(h, wynik["id"])
    finally:
        h.close()
    met = wynik["metryki"]
    if a.json:
        W.wypisz_json({"przebieg": wynik["id"], "baza": wynik["baza"], "metryki": met,
                       "alarmy": [t for _, t in wynik["alarmy"]], "porownania": por})
        return 0
    for o in wynik["ostrzezenia"]:
        W.ostrzez(o)
    rozmiary = ({"KI": met["ki"]["n"]} if "ki" in met else {})
    rozmiary.update({"tematy": met["tematy"]["n"]} if "tematy" in met else {})
    rozmiary.update({k: v["n"] for k, v in met.get("pytania", {}).items()})
    rozmiary.update({"inwestor": met["wlasne"]["n"]} if "wlasne" in met else {})
    print(f"[jakosc] przebieg złoty #{wynik['id']}{' (BAZA)' if wynik['baza'] else ''} · {met['czas_s']:.1f} s · "
          f"indeks: {met['informacji']} informacji · zbiory: " + ", ".join(f"{k} {v}" for k, v in rozmiary.items()))
    print("  " + opis_metryk(met))
    if "ki" in met:
        print("  KI wg perturbacji [%]: " + ", ".join(f"{k} {v:.1f}" for k, v in met["ki"]["perturbacje"].items()))
    n0 = wynik["ki_informacji"]
    if n0 and abs(met["informacji"] - n0) > 0.1 * n0:
        W.ostrzez(f"liczba informacji zmieniła się o ponad 10% od utworzenia zbioru KI ({n0} → {met['informacji']}) "
                  "– rozważ zloty --odnowa (nowy przebieg stanie się bazą)")
    for etykieta, p in por.items():
        print(opis_porownania(etykieta, p))
    print("\n".join(f"  ALARM: {t}" for _, t in wynik["alarmy"]) or "  alarmy: brak")
    return 0


# ------------------------------------------------------------------ dodaj
def numery_wi(tekst: str) -> list:
    numery = []
    for czesc in tekst.split(","):
        mt = re.fullmatch(r"\s*(?:WI-?)?(\d+)\s*", czesc, re.I)
        if not mt:
            raise BladJakosci(f"--powinno: „{czesc.strip()}” to nie numer WI (np. WI-12,WI-40)")
        numery.append(int(mt.group(1)))
    return list(dict.fromkeys(numery))


def cmd_dodaj(a) -> int:
    if W.zbuduj_zapytanie_fts(a.zapytanie, "AND") is None:
        raise BladJakosci("puste zapytanie – podaj słowa")
    numery = numery_wi(a.powinno)
    m = Miejsca(a)
    m.przygotuj()
    with contextlib.closing(W.otworz_db(m.baza, zapis=False)) as conn:
        istniejace = {wi: (st, ist) for wi, st, ist in conn.execute("SELECT wi, status, istotnosc FROM informacje")}
        brak = [n for n in numery if n not in istniejace]
        if brak:
            raise BladJakosci("brak w indeksie: " + ", ".join(f"WI-{n}" for n in brak) + " – nic nie dodano")
        lista = szukaj_listy(conn, a.zapytanie)
    ukryte = [n for n in numery if W.normalizuj(istniejace[n][0]) == "nieaktualne"
              or W.normalizuj(istniejace[n][1]) == "ciekawostka"]
    with blokada_przebiegu(m) as wolna:
        if not wolna:
            raise BladJakosci("trwa przebieg obserwatora – spróbuj za chwilę")
        wlasne = czytaj_json(m.wlasne, [])
        nr = max([int(w["id"][1:]) for w in wlasne] or [0]) + 1
        wpis = {"id": f"W{nr:02d}", "q": a.zapytanie, "wi": numery, "opis": a.opis or "", "dodano": teraz_iso()}
        zapisz_json(m.wlasne, wlasne + [wpis])
    zaostrz(m.dane)
    wart = ocen_zapytanie(lista, "wlasne", set(numery))[0]
    if a.json:
        W.wypisz_json({"id": wpis["id"], "wi": numery, "w_top12": wart, "ukryte": ukryte})
        return 0
    pozycje = ", ".join(f"WI-{n}: {lista.index(n) + 1 if n in lista else '–'}" for n in numery)
    print(f"[jakosc] dodano {wpis['id']} ({', '.join(f'WI-{n}' for n in numery)}) – sprawdzany w każdym przebiegu "
          f"zloty; teraz w pierwszej {TOP}: {round(wart * len(numery))}/{len(numery)} (pozycje: {pozycje})")
    if ukryte:
        W.ostrzez("Nieaktualne/Ciekawostka – szukaj domyślnie ich nie pokazuje: "
                  + ", ".join(f"WI-{n}" for n in ukryte))
    return 0


# ------------------------------------------------------------------ raport
def ocena_reczna(m: Miejsca) -> dict:
    zestawy = sorted(m.dane.glob("reczna-*.jsonl")) if m.dane.is_dir() else []
    if not zestawy:
        return {}
    wynik = {"zestawy": len(zestawy)}
    for nazwa, pliki in (("ostatni", zestawy[-1:]), ("razem", zestawy)):
        oceny = [o for p in pliki for w in czytaj_jsonl(p) for o in (w.get("oceny") or [])]
        tak, nie = oceny.count("y"), oceny.count("n")
        wynik[nazwa] = {"ocen": tak + nie, "pominieto": oceny.count("s") + oceny.count("x"),
                        "brak": oceny.count(None), "trafne_proc": round(100 * tak / (tak + nie), 1) if tak + nie else None}
    wynik["ostatni"]["plik"] = zestawy[-1].name
    return wynik


def proc(x) -> str:
    return "–" if x is None or x == "–" else f"{x:.0f}%"


def raport_dane(m: Miejsca, dni: int) -> dict:
    alarmy_l, s, s0, okno = alarmy_logu(m, dni)
    dane = {"dni": dni, "log": s, "log_poprzednie_4_tyg": {"n": s0["n"], "zero": s0.get("zero")},
            "zero_zapytania": list(dict.fromkeys(r["q"] for r in okno if r["trafien"] == 0)),
            "reczna": ocena_reczna(m), "alarmy": [{"klucz": k, "tekst": t} for k, t in alarmy_l]}
    try:
        h = otworz_historie(m)
    except (sqlite3.DatabaseError, BladJakosci) as e:
        dane["historia_blad"] = type(e).__name__
        return dane
    try:
        zapisz_alarmy(h, alarmy_l)
        p, baza = przebiegi(h, "zloty", 1), przebieg_bazowy(h)
        if p:
            dane["zloty"] = {"id": p[0]["id"], "ts": p[0]["ts"], "metryki": p[0]["metryki"], "porownania":
                             porownania(h, p[0]["id"]), "baza": baza["id"] if baza else None}
        n = przebiegi(h, "notion", 1)
        if n:
            dane["notion"] = {"id": n[0]["id"], "ts": n[0]["ts"], "metryki": n[0]["metryki"]}
        dane["alarmy"] = otwarte_alarmy(h)
        with h:
            h.execute("UPDATE alarmy SET potwierdzony = 1 WHERE potwierdzony = 0")
            h.execute("INSERT OR REPLACE INTO meta VALUES ('raport_ts', ?)", (teraz_iso(),))
    except sqlite3.DatabaseError as e:
        dane["historia_blad"] = type(e).__name__
    finally:
        h.close()
    return dane


def cmd_raport(a) -> int:
    m = Miejsca(a)
    m.przygotuj()
    d = raport_dane(m, a.dni)
    zaostrz(m.dane)
    if a.json:
        W.wypisz_json(d)
        return 0
    s = d["log"]
    print(f"# jakość wyszukiwania · ostatnie {a.dni} dni · {teraz().astimezone():%Y-%m-%d %H:%M}")
    if s["n"]:
        print(f"log: zapytań {s['n']} (" + ", ".join(f"{k} {v}" for k, v in sorted(s["kanaly"].items()))
              + f") · zero wyników {proc(100 * s['zero'])} · dopełnienie {proc(100 * s['dopelnienie'])} (samo OR "
              f"{proc(100 * s['or_only'])}) · wąskie (<5) {proc(100 * s['waskie'])} · mediana trafień "
              f"{s['mediana_trafien']:g} · czas mediana {s['ms_mediana']:g} ms, p90 {s['ms_p90']:g} ms")
        s0 = d["log_poprzednie_4_tyg"]
        if s0["n"]:
            print(f"  poprzednie 4 tygodnie: zapytań {s0['n']}, zero wyników {proc(100 * s0['zero'])}")
    else:
        print("log: brak zapytań (kanał czatu na telefonie nie jest logowany)")
    if "historia_blad" in d:
        print(f"historia: nieczytelna ({d['historia_blad']}) – odłóż jakosc/historia.sqlite na bok, "
              "następny zloty założy nową")
    z = d.get("zloty")
    if z:
        print(f"zbiór złoty #{z['id']} ({z['ts'][:10]}, baza #{z['baza']}): {opis_metryk(z['metryki'])}")
        for etykieta, p in z["porownania"].items():
            print(opis_porownania(etykieta, p))
        if dawno(z["ts"], 2 * CO_ILE_DNI):
            W.ostrzez(f"ostatni przebieg złoty starszy niż {2 * CO_ILE_DNI} dni – uruchom zloty")
    elif "historia_blad" not in d:
        print("zbiór złoty: brak przebiegów – uruchom python3 tools/wiedza_jakosc.py zloty")
    r = d["reczna"]
    if r:
        o = r["ostatni"]
        print(f"ocena ręczna ({o['plik']}): ocen {o['ocen']}, trafne {proc(o['trafne_proc'])} · pominięte "
              f"{o['pominieto']} · do oceny {o['brak']}; wszystkie zestawy ({r['zestawy']}): trafne "
              f"{proc(r['razem']['trafne_proc'])} z {r['razem']['ocen']}")
    if "notion" in d:
        print(f"Notion (API, {d['notion']['ts'][:10]}): {opis_notion(d['notion']['metryki'])}")
    if d["zero_zapytania"]:
        print(f"zapytania z logu bez wyników ({len(d['zero_zapytania'])}) – kandydaci na synonim albo informację:")
        for q in d["zero_zapytania"][:20]:
            print(f"  - {W.skroc(q, 120)}")
    print("\n".join(f"ALARM: {x['tekst']}" for x in d["alarmy"]) or "alarmy: brak")
    return 0


# ------------------------------------------------------------------ ocena ręczna
def zapytania_do_oceny(m: Miejsca, n: int) -> list:
    kand = [(f"{z}-{j + 1:02d}", p["q"]) for z, lista in wczytaj_pytania(m, []).items() for j, p in enumerate(lista)]
    with contextlib.suppress(BladJakosci, KeyError, TypeError):
        kand += [(w["id"], w["q"]) for w in czytaj_json(m.wlasne, [])]
    z_logu = [r["q"] for r in czytaj_log(m, teraz() - timedelta(days=30)) if r["trafien"] > 0]
    kand += [(f"L{i + 1:02d}", q) for i, q in enumerate(dict.fromkeys(q for q in z_logu if q))]
    random.Random(f"{teraz():%Y-%m-%d}").shuffle(kand)
    return kand[:n]


def cmd_reczna(a) -> int:
    m = Miejsca(a)
    m.przygotuj()
    terminal = sys.stdout.isatty() and sys.stdin.isatty() and not a.json
    with contextlib.closing(W.otworz_db(m.baza, zapis=False)) as conn:
        if a.wczytaj:
            zrodlo = Path(a.wczytaj).expanduser()
            wiersze = [w for w in czytaj_jsonl(zrodlo) if isinstance(w.get("wi"), list) and "id" in w]
            if not wiersze:
                raise BladJakosci(f"{zrodlo.name}: brak wierszy zestawu oceny (id, q, wi, oceny)")
            plik = zrodlo if zrodlo.parent.resolve() == m.dane.resolve() else m.dane / f"reczna-{zrodlo.stem}.jsonl"
            if plik.is_file():   # wczytany wcześniej – wznów kopię z ocenami
                wiersze = czytaj_jsonl(plik)
        else:
            otwarte = [p for p in sorted(m.dane.glob("reczna-*.jsonl"))
                       if any(None in (w.get("oceny") or []) for w in czytaj_jsonl(p))]
            if otwarte and not a.nowa:
                plik, wiersze = otwarte[-1], czytaj_jsonl(otwarte[-1])
            else:
                plik = m.dane / f"reczna-{teraz().astimezone():%Y%m%d-%H%M%S}.jsonl"
                with szybka_normalizacja():
                    wiersze = [{"zestaw": plik.stem, "id": zid, "q": q, "wi": szukaj_listy(conn, q)[:5]}
                               for zid, q in zapytania_do_oceny(m, a.n)]
        istnieja = {wi for (wi,) in conn.execute("SELECT wi FROM informacje")}
        zniknely = 0
        for w in wiersze:
            w["oceny"] = (list(w.get("oceny") or []) + [None] * len(w["wi"]))[:len(w["wi"])]
            for j, wi in enumerate(w["wi"]):
                if w["oceny"][j] is None and wi not in istnieja:
                    w["oceny"][j], zniknely = "x", zniknely + 1   # x – wiersza nie ma już w indeksie
        zapisz_jsonl(plik, wiersze)
        zaostrz(m.dane)
        brak = sum(o is None for w in wiersze for o in w["oceny"])
        podpowiedz = (f"; {zniknely} wyników nie ma już w indeksie – pominięte (nowy zestaw: reczna --nowa)"
                      if zniknely else "")
        if not terminal:
            if a.json:
                W.wypisz_json({"plik": plik.name, "zapytan": len(wiersze), "do_oceny": brak, "zniknelo": zniknely})
            else:
                print(f"[jakosc] ocena ręczna {plik.name}: zapytań {len(wiersze)}, do oceny {brak}{podpowiedz} – "
                      "tekst wyników pokazuję tylko w terminalu; uruchom to polecenie samodzielnie")
            return 0
        print(f"ocena ręczna {plik.name}: do oceny {brak}{podpowiedz}. Dla każdego wyniku: y = trafny, n = nietrafny, "
              "s = pomiń, q = przerwij (wznowisz tym samym poleceniem)")
        for i, w in enumerate(wiersze, 1):
            if None not in w["oceny"]:
                continue
            print(f"\n[{i}/{len(wiersze)}] {w['id']}: {w['q']}")
            for j, wi in enumerate(w["wi"]):
                if w["oceny"][j] is not None:
                    continue
                opis = W.opisz_informacje(conn, [wi])[0]
                print(f"    {j + 1}. WI-{wi} · {W.jedna_linia(opis['istotnosc'])} · {W.jedna_linia(opis['teza'])} · T: "
                      + ("; ".join(W.jedna_linia(t) for t in opis["tematy"]) or "–"))
                odp = ""
                while odp not in ("y", "n", "s", "q"):
                    odp = input("      trafny? [y/n/s/q] ").strip().lower()[:1]
                if odp == "q":
                    print(f"przerwano – zapisane w {plik.name}")
                    return 0
                w["oceny"][j] = odp
                zapisz_jsonl(plik, wiersze)
    print(f"\nkoniec zestawu {plik.name} – wynik w raporcie")
    return 0


# ------------------------------------------------------------------ porównanie z Notion
class LicznikZadan:
    """Zamiast W.OTWIERACZ: liczy każde wyjście do sieci (także powtórki po 429) i pilnuje budżetu."""

    def __init__(self, otwieracz, budzet: int):
        self.otwieracz, self.budzet, self.zadan = otwieracz, budzet, 0

    def open(self, *args, **kwargs):
        if self.zadan >= self.budzet:
            raise BudzetWyczerpany()
        self.zadan += 1
        return self.otwieracz.open(*args, **kwargs)


def slowa_notion(q: str) -> list:
    """Słowa zapytania jak w szukaj (bez wypełniaczy, końcówka ucięta), ale z polskimi znakami i „ł” – filtr
    `contains` w Notion rozróżnia diakrytyki."""
    slowa = []
    for mt in W.ELEMENT_ZAPYTANIA.finditer(q or ""):
        fraza, token = mt.groups()
        if token == "OR":
            continue
        tekst = unicodedata.normalize("NFC", fraza if fraza is not None else token).lower()
        for s in W.NIE_SLOWO.sub(" ", tekst).split():
            stop = W.bez_diakrytykow(s) in W.STOP_ZAPYTANIA
            if s.isalpha() and len(s) >= W.TEMAT_OD:
                s = s[:max(W.TEMAT_MIN, len(s) - 2)]
            slowa.append((s, stop))
    tresciowe = [s for s, stop in slowa if not stop]
    return list(dict.fromkeys(tresciowe or [s for s, _ in slowa]))


class Notion:
    def __init__(self, token: str):
        self.naglowki = {"Authorization": "Bearer " + token, "Notion-Version": W.NOTION_WERSJA}
        self.zrodlo = W.BAZY["informacje"]["zrodlo"]
        pola = W.MAPOWANIE["informacje"]
        self.pola = [(pola["teza"], "title"), (pola["szczegoly"], "rich_text"), (pola["dla_nas"], "rich_text")]
        self.numer = W.BAZY["informacje"]["numer"]
        sch = W.zadanie_http("GET", f"{W.NOTION_API}/v1/data_sources/{self.zrodlo}", self.naglowki)
        wl = sch.get("properties") or {}
        if self.numer not in wl or not all(p in wl for p, _ in self.pola):
            raise BladJakosci("schemat bazy Informacji w Notion bez wymaganych właściwości")
        self.qs = urllib.parse.urlencode([("filter_properties[]", wl[self.numer]["id"])])

    def zapytaj(self, filtr: dict) -> set:
        url = f"{W.NOTION_API}/v1/data_sources/{self.zrodlo}/query?{self.qs}"
        cialo, wynik = {"page_size": 100, "filter": filtr}, set()
        while True:
            odp = W.zadanie_http("POST", url, self.naglowki, cialo)
            for s in odp.get("results") or []:
                nr = (((s.get("properties") or {}).get(self.numer) or {}).get("unique_id") or {}).get("number")
                if nr is not None:
                    wynik.add(nr)
            if not odp.get("has_more") or not odp.get("next_cursor"):
                return wynik
            cialo["start_cursor"] = odp["next_cursor"]

    def szukaj(self, q: str) -> tuple:
        filtry = [{"or": [{"property": p, typ: {"contains": s}} for p, typ in self.pola]} for s in slowa_notion(q)]
        if not filtry:
            return set(), "pusto"
        wynik = self.zapytaj({"and": filtry} if len(filtry) > 1 else filtry[0])
        if wynik or len(filtry) == 1:
            return wynik, "AND"
        return self.zapytaj({"or": filtry}), "OR"


def zadania_notion(m: Miejsca, K: Korpus) -> list:
    """Kolejność = priorytet przy budżecie: NL13, NOWE24, KI (co 8. zapytanie bazowe trybu tematycznego, najwyżej
    25, z jego wersją naturalną), EXTRA50."""
    pytania = wczytaj_pytania(m, [])
    zad = []

    def pyt(zestaw):
        zad.extend((f"{zestaw}-{j + 1:02d}", p["q"], None, K.predykat(p["wzory"]))
                   for j, p in enumerate(pytania.get(zestaw, [])))
    pyt("NL13")
    pyt("NOWE24")
    ki = [z for z in uaktualnij_ki(m, czytaj_json(m.ki, {"wersja": 2, "zapytania": []}))["zapytania"]
          if K.widoczny.get(z["wi"])]
    naturalne = {(z["wi"], z["tryb"]): z for z in ki if z["pert"] == "naturalne"}
    for z in [z for z in ki if z["tryb"] == "t" and z["pert"] == "baza"][::8][:25]:
        zad.append((z["id"], z["q"], z["wi"], None))
        n = naturalne.get((z["wi"], z["tryb"]))
        if n:
            zad.append((n["id"], n["q"], n["wi"], None))
    pyt("EXTRA50")
    return zad


def opis_notion(nm: dict) -> str:
    nm = {k: "–" if v is None else v for k, v in nm.items()}
    return (f"żądań {nm['zadan']}/{nm['budzet']}, zapytań {nm['zapytan']} (nieukończone {nm['nieukonczone']}) · "
            f"KI {nm['ki_n']}: Notion znalazł {nm['ki_notion_jest']} (≤ 12 wierszy {nm['ki_notion_12']}; mediana "
            f"zbioru {nm['ki_notion_mediana']}), indeks success@12 {nm['ki_indeks_12']} · pytania {nm['pyt_n']}: "
            f"Notion pełność {proc(nm['pyt_notion_pelnosc'])}, precyzja {proc(nm['pyt_notion_precyzja'])} (mediana "
            f"{nm['pyt_notion_mediana']} wierszy), indeks P@12 {proc(nm['pyt_indeks_p12'])}, pełność "
            f"{proc(nm['pyt_indeks_pelnosc'])} · czas Notion mediana {nm['s_mediana']} s, p90 {nm['s_p90']} s")


def metryki_notion(wyniki: dict, czasy: list, licznik, nieukonczone: int, K: Korpus) -> dict:
    ki = [v for k, v in wyniki.items() if k.startswith("KI-")]
    py = [v for k, v in wyniki.items() if not k.startswith("KI-")]
    ref = sum(v["ref"] for v in py)
    return {"budzet": licznik.budzet, "zadan": licznik.zadan, "zapytan": len(wyniki), "nieukonczone": nieukonczone,
            "ki_n": len(ki), "ki_notion_jest": sum(v["jest"] for v in ki),
            "ki_notion_12": sum(v["jest"] and v["n"] <= TOP for v in ki),
            "ki_notion_mediana": statistics.median([v["n"] for v in ki]) if ki else None,
            "ki_indeks_12": sum(v["indeks12"] for v in ki), "pyt_n": len(py),
            "pyt_notion_pelnosc": 100 * sum(v["traf"] for v in py) / ref if ref else None,
            "pyt_notion_precyzja": 100 * sum(v["traf"] for v in py) / max(1, sum(v["n"] for v in py)) if py else None,
            "pyt_notion_mediana": statistics.median([v["n"] for v in py]) if py else None,
            "pyt_notion_or": sum(v["tryb"] == "OR" for v in py),
            "pyt_indeks_p12": 100 * sum(v["ix_p12"] for v in py) / (TOP * len(py)) if py else None,
            "pyt_indeks_pelnosc": 100 * sum(v["ix_traf"] for v in py) / ref if ref else None,
            "s_mediana": round(statistics.median(czasy), 2) if czasy else None,
            "s_p90": round(sorted(czasy)[int(0.9 * (len(czasy) - 1))], 2) if czasy else None, "informacji": K.n}


def cmd_notion(a) -> int:
    if a.budzet < 10:
        raise BladJakosci("--budzet: co najmniej 10 żądań")
    m = Miejsca(a)
    m.przygotuj()
    with contextlib.redirect_stdout(sys.stderr if a.json else sys.stdout):  # ostrzeżenie o uprawnieniach przed JSON-em
        token = W.wczytaj_sekrety(W.SEKRETY).get("NOTION_TOKEN")
    if not token:
        raise BladJakosci("brak NOTION_TOKEN w sekrety.env – porównanie z Notion niemożliwe")
    licznik = LicznikZadan(W.OTWIERACZ, a.budzet)
    wyniki, czasy, nieukonczone = {}, [], 0
    with blokada_przebiegu(m) as wolna:
        if not wolna:
            raise BladJakosci("trwa przebieg obserwatora – spróbuj za chwilę")
        W.OTWIERACZ = licznik
        try:
            with contextlib.closing(W.otworz_db(m.baza, zapis=False)) as conn:
                odcisk, K = odcisk_indeksu(conn), Korpus(conn)
                if not m.ki.is_file():
                    zapisz_json(m.ki, zbuduj_ki(conn, K))
                zad = zadania_notion(m, K)
                try:
                    notion = Notion(token)
                except (W.BladHttp, W.BladSieci) as e:
                    raise BladJakosci("Notion: " + W.tekst_bledu(e, {"t": token})) from None
                with szybka_normalizacja():
                    for zid, q, wi, pred in zad:
                        if licznik.budzet - licznik.zadan < NOTION_REZERWA:
                            break
                        t0 = time.monotonic()
                        try:
                            zbior, tryb = notion.szukaj(q)
                        except BudzetWyczerpany:
                            nieukonczone += 1
                            break
                        except (W.BladHttp, W.BladSieci):
                            nieukonczone += 1
                            continue
                        czasy.append(time.monotonic() - t0)
                        widoczne = {x for x in zbior if K.widoczny.get(x)}
                        lista = szukaj_listy(conn, q)
                        if wi is not None:
                            r = lista.index(wi) + 1 if wi in lista else None
                            wyniki[zid] = {"jest": wi in zbior, "n": len(widoczne), "indeks12": r is not None and r <= TOP}
                        else:
                            prawda = K.trafne(pred)
                            wyniki[zid] = {"traf": len(widoczne & prawda), "n": len(widoczne), "ref": len(prawda),
                                           "ix_p12": sum(1 for x in lista[:TOP] if pred(x)),
                                           "ix_traf": len(prawda & set(lista)), "tryb": tryb}
        finally:
            W.OTWIERACZ = licznik.otwieracz
        met = metryki_notion(wyniki, czasy, licznik, nieukonczone, K)
        if not wyniki:
            raise BladJakosci(f"żadne zapytanie do Notion się nie udało (żądań {licznik.zadan}, nieukończone "
                              f"{nieukonczone}) – przebieg nie zapisany")
        wart = {k: ("KI" if k.startswith("KI-") else zestaw_z_id(k),
                    float(v["jest"]) if "jest" in v else v["traf"] / max(1, v["ref"]), None) for k, v in wyniki.items()}
        nr, _, _ = zapisz_przebieg(m, "notion", met, wart, odcisk)
    zaostrz(m.dane)
    if a.json:
        W.wypisz_json({"przebieg": nr, "metryki": met})
    else:
        print(f"[jakosc] porównanie z Notion #{nr} (przybliżenie API, nie wyszukiwarka MCP): {opis_notion(met)}")
    return 0


# ------------------------------------------------------------------ przypomnienie (hook startu)
def auto_zloty(m: Miejsca, h) -> str:
    """Raz w tygodniu przebieg złoty w hooku – tylko gdy poprzedni zmieścił się w ZLOTY_AUTO_S i nie było nieudanej
    próby w ostatniej dobie. Zwraca dopisek do linii przypomnienia albo ""."""
    ostatni = przebiegi(h, "zloty", 1)
    if ostatni and not dawno(ostatni[0]["ts"], CO_ILE_DNI):
        return ""
    if not dawno(meta(h, "zloty_auto_nieudany"), PONOW_AUTO_H / 24):
        return ""
    if ostatni and ostatni[0]["metryki"].get("czas_s", 0) >= ZLOTY_AUTO_S:
        return "przebieg złoty należny – uruchom python3 tools/wiedza_jakosc.py zloty"
    with blokada_przebiegu(m) as wolna:
        if not wolna:
            return ""
        try:
            przebieg_zloty(m, termin=time.monotonic() + ZLOTY_AUTO_S)
            return ""
        except PrzekroczonyCzas:
            ustaw_meta(h, "zloty_auto_nieudany", teraz_iso())
            return f"przebieg złoty nie mieści się w {ZLOTY_AUTO_S:g} s – uruchom python3 tools/wiedza_jakosc.py zloty"
        except (IndeksZmieniony, sqlite3.OperationalError, W.BladIndeksu):
            ustaw_meta(h, "zloty_auto_nieudany", teraz_iso())
            return ""


def przypomnienie(a, m: Miejsca) -> str:
    m.przygotuj()
    h = otworz_historie(m)
    try:
        dopisek = auto_zloty(m, h)
        zapisz_alarmy(h, alarmy_logu(m, CO_ILE_DNI)[0])
        alarmy = len(otwarte_alarmy(h))
        raport_ts = meta(h, "raport_ts")
    finally:
        h.close()
    with contextlib.suppress(OSError):
        m.awaria.unlink()
    if a.json:
        W.wypisz_json({"raport_do_przegladu": dawno(raport_ts, CO_ILE_DNI), "alarmy": alarmy, "dopisek": dopisek})
        return ""
    if dawno(raport_ts, CO_ILE_DNI):
        linia = "[jakosc] raport tygodniowy do przeglądu: python3 tools/wiedza_jakosc.py raport" + (
            f" – alarmy: {alarmy}" if alarmy else "")
    elif alarmy:
        linia = f"[jakosc] alarmy jakości wyszukiwania: {alarmy} – python3 tools/wiedza_jakosc.py raport"
    elif dopisek:
        return f"[jakosc] {dopisek}"
    else:
        return "" if a.cicho else f"[jakosc] nic do zrobienia: ostatni raport {str(raport_ts)[:10]}"
    return linia + (f"; {dopisek}" if dopisek else "")


def cmd_przypomnij(a) -> int:
    """Zawsze kod 0. Bez blokady syncu: hooki startu działają równolegle. Awaria obserwatora → najwyżej raz
    w tygodniu jedna linia z typem błędu (znacznik `jakosc/.awaria`), żeby hook nie milczał w nieskończoność."""
    if W.w_worktree():
        return 0
    m = Miejsca(a)
    if not m.baza.is_file() or not m.dozwolone():
        return 0
    try:
        linia = przypomnienie(a, m)
    except Exception as e:  # noqa: BLE001
        try:
            ostatnio = m.awaria.read_text(encoding="utf-8").strip()
        except OSError:
            ostatnio = None
        if not dawno(ostatnio, CO_ILE_DNI):
            return 0
        with contextlib.suppress(OSError):
            zapisz_plik(m.awaria, teraz_iso())
        linia = f"[jakosc] obserwator nie działa: {type(e).__name__} – python3 tools/wiedza_jakosc.py raport"
    if linia:
        print(linia)
    return 0


# ------------------------------------------------------------------ CLI
def zbuduj_parser() -> argparse.ArgumentParser:
    wspolne = argparse.ArgumentParser(add_help=False)
    wspolne.add_argument("--db", type=Path, help="plik indeksu w <hub>/.dom/wiedza/ (domyślnie wiedza.sqlite tam)")
    wspolne.add_argument("--json", action="store_true", help="wynik jako JSON")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="polecenie", metavar="POLECENIE", required=True)
    p = sub.add_parser("zloty", parents=[wspolne], help="przebieg zbiorów oceny, porównanie z poprzednim i bazą")
    p.add_argument("--odnowa", action="store_true", help="nowy zbiór known-item z bieżącego indeksu (nowa baza)")
    p.add_argument("--ustaw-baze", action="store_true", help="ten przebieg staje się bazą porównań")
    p = sub.add_parser("dodaj", parents=[wspolne], help="przypadek inwestora: zapytanie i WI, które ma znaleźć")
    p.add_argument("zapytanie", help="zapytanie tak, jak je wpisujesz")
    p.add_argument("--powinno", required=True, help="numery WI po przecinku, np. WI-12,WI-40")
    p.add_argument("--opis", help="krótka notatka (zostaje w danych, nie jest drukowana)")
    p = sub.add_parser("raport", parents=[wspolne], help="raport tygodniowy: log, trend, ocena ręczna, alarmy")
    p.add_argument("--dni", type=int, default=CO_ILE_DNI, help=f"okno logu w dniach (domyślnie {CO_ILE_DNI})")
    p = sub.add_parser("reczna", parents=[wspolne], help="ocena ręczna wyników w terminalu (wznawialna)")
    p.add_argument("--n", type=int, default=30, help="liczba zapytań w nowym zestawie (domyślnie 30)")
    p.add_argument("--nowa", action="store_true", help="nowy zestaw zamiast wznowienia niedokończonego")
    p.add_argument("--wczytaj", help="plik JSONL zestawu (id, q, wi, oceny) do dokończenia albo wczytania")
    p = sub.add_parser("notion", parents=[wspolne], help="miesięczne porównanie z Notion przez API (tylko odczyt)")
    p.add_argument("--budzet", type=int, default=300, help="najwyżej tyle żądań do Notion (domyślnie 300)")
    p = sub.add_parser("przypomnij", parents=[wspolne], help="hook startu: linia, gdy raport albo alarmy czekają")
    p.add_argument("--cicho", action="store_true", help="nic nie pisz, gdy nic nie czeka")
    return ap


POLECENIA = {"zloty": cmd_zloty, "dodaj": cmd_dodaj, "raport": cmd_raport, "reczna": cmd_reczna,
             "notion": cmd_notion, "przypomnij": cmd_przypomnij}


def main(argv=None) -> int:
    a = zbuduj_parser().parse_args(argv)
    if W is None:
        if a.polecenie == "przypomnij":
            return 0
        print("  ✗ brak modułu wiedza.py obok wiedza_jakosc.py")
        return 1
    try:
        with W.prywatne_pliki():
            return POLECENIA[a.polecenie](a)
    except Exception as e:  # noqa: BLE001 – treść wyjątku może nieść wartości pól
        if a.polecenie == "przypomnij":
            return 0
        if isinstance(e, (BladJakosci, IndeksZmieniony, W.BladIndeksu)):
            W.blad(str(e))
        else:
            W.blad(f"{type(e).__name__} (linia {W.linia_bledu(e, __file__)})")
        return 1


if __name__ == "__main__":
    sys.exit(main())
