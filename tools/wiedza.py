#!/usr/bin/env python3
"""Indeks Bazy wiedzy: lokalna kopia czterech baz Notion (Informacje, Tematy, Źródła, Rejestr sprzeczności)
w SQLite FTS5 – tylko do odczytu, Notion zostaje jedynym źródłem prawdy i jedynym miejscem zapisu.

Plik indeksu: `.dom/wiedza/wiedza.sqlite` w folderze-centrum (hub) – domyślnie dwa poziomy nad repozytorium,
albo zmienna DOM_HUB; w czacie podaje się --db <katalog>/wiedza.sqlite.

    python3 tools/wiedza.py sync [--pelny] [--publikuj]   # pobierz zmiany z Notion (hook na starcie: --publikuj --cicho)
    python3 tools/wiedza.py szukaj "ZAPYTANIE" ["ZAPYTANIE 2" …] [--etap …] [--istotnosc …] [--status …] [--rodzaj …]
                                               [--temat …] [--ciekawostki] [--krotko] [--limit 12] [--sens]
    python3 tools/wiedza.py temat "NAZWA" [--lista] [--krotko] [--ciekawostki]   # stan wiedzy, Kluczowe, otwarte SP
    python3 tools/wiedza.py etap "NAZWA" [--czesc k] [--kontrola] [--ciekawostki]   # cała wiedza etapu w częściach
    python3 tools/wiedza.py karty [--do "PYTANIE" ["PYTANIE 2" …]] [--etap …] [--rodzaj pytanie|czynnosc]   # spis kart
    python3 tools/wiedza.py karta KOD [KOD2 …] [--pytanie "A" ["B" …]] [--czesc k] [--ciekawostki]   # karta w częściach
    python3 tools/wiedza.py duplikaty [--od RRRR-MM-DD] [--prog 0.84] [--temat NAZWA] [--sens | --slowa]
    python3 tools/wiedza.py stan                          # liczniki, daty synchronizacji i publikacji
    python3 tools/wiedza.py publikuj [--teraz] [--wymus] [--reset]   # kopia indeksu do prywatnego repo GITHUB_REPO

Opcje wspólne (także po podkomendzie): --db ŚCIEŻKA, --cicho (tylko zmiany i błędy), --json.
publikuj: --teraz bez odstępu 60 min; --wymus wysyła plik indeksu także bez zmian danych (np. po odtworzeniu
repo); --reset zastępuje historię repo jednym commitem z czterema plikami (gdy `stan` ostrzega o rozmiarze).
WIEDZA_DEBUG=1 (tylko ręcznie w terminalu, bez --cicho – traceback może nieść wartości pól): pełny traceback
nieoczekiwanego błędu na stderr zamiast samej nazwy typu i linii.

Zasady:
- Moduł nigdy nie pisze do Notion: wysyła tylko zapytania o wiersze baz (query) i odczyt schematu bazy.
- szukaj, temat, etap, karty, karta, duplikaty i stan działają na samym pliku: bez tokena, bez sieci i bez pliku
  synonimów.
- Karty wiedzy (tabele `karty`, `karty_wi`): gotowe zbiory tez na typowe pytania, wybrane na Macu modelem czytającym
  całą bazę (tools/wiedza_karty.py) – `karty --do` wskazuje karty do pytania, `karta` drukuje tezy karty w częściach;
  kopia indeksu bez kart → `karty` odpowiada „brak” (wtedy szukaj / temat / etap).
- Odciski znaczenia (tools/wiedza_sens.py, Ollama, tylko Mac): sync na końcu (po publikacji) liczy odciski nowych
  i zmienionych informacji (osobny plik `wektory.sqlite`, nie idzie do czatu) i listy podobnych (tabela `podobne`
  w indeksie – idzie do czatu z następną publikacją); Ollama nie działa → krok pominięty po cichu. Z list korzystają `szukaj --krotko` (sekcja
  „podobne do trafień”) i `duplikaty`; `szukaj --sens` (Mac) łączy ranking po słowach z rankingiem po znaczeniu.
- sync i publikuj czytają NOTION_TOKEN, GITHUB_TOKEN_SYNC i GITHUB_REPO z `.dom/sekrety.env` (chmod 600);
  wartości nigdy nie są wypisywane ani zapisywane.
- Dane leżą w `.dom/wiedza/` w hubie (katalog 700, pliki 600), nigdy w repozytorium; bez katalogu `.dom` sync
  kończy się komunikatem i niczego nie tworzy. Uszkodzony indeks domyślny sync odkłada na bok i buduje od nowa.
- sync --cicho (hook na starcie, nocne skrypty) pisze tylko przy zmianach albo błędach, mieści się w limicie
  czasu startu (pobór i publikacja razem) i kończy się kodem 0.
- publikuj wysyła wyłącznie do repo prywatnego (sprawdza to przed wysyłką).
- Komunikaty zawierają tylko numery WI/ZRD/SP, ID stron, nazwy właściwości, liczby i statusy HTTP – nigdy
  wartości pól (te drukują wyłącznie wyniki szukaj, temat, etap, karty, karta i duplikaty).
- Log zapytań: każde `szukaj` na indeksie z `.dom/wiedza/` dopisuje jeden wiersz JSON do `.dom/wiedza/szukaj.log.jsonl`
  (600; czas UTC, kanał z WIEDZA_KANAL albo „claude-code”/„inny”, zapytanie do 500 znaków, tryb, liczby trafień,
  top-5 WI, ms, filtry – bez treści wierszy). Przy 2 MB zostaje jedna starsza kopia `szukaj.log.1.jsonl`. WIEDZA_LOG=0 wyłącza log;
  z --db spoza `.dom/wiedza/` (kopia w czacie) log nie powstaje. Błąd logu nigdy nie zmienia wyniku ani kodu wyjścia.
  Log czyta obserwator jakości `tools/wiedza_jakosc.py`.
"""
import argparse
import base64
import contextlib
import difflib
import hashlib
import heapq
import http.client
import json
import os
import re
import sqlite3
import sys
import time
import traceback
import unicodedata
import urllib.error
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HUB = Path(os.environ.get("DOM_HUB") or REPO.parent.parent).expanduser().resolve()
CONF = HUB / ".dom"
KATALOG = CONF / "wiedza"
DB_DOMYSLNA = KATALOG / "wiedza.sqlite"
SEKRETY = CONF / "sekrety.env"
SYNONIMY = Path(__file__).resolve().parent / "wiedza_synonimy.txt"  # czyta tylko sync; w czacie pliku nie ma
PLIK_LOGU = "szukaj.log.jsonl"          # w KATALOG; czyta tools/wiedza_jakosc.py
PLIK_LOGU_STARY = "szukaj.log.1.jsonl"  # jedna kopia po rotacji
LOG_MAKS_B = 2 * 1024 * 1024
LOG_MAKS_ZAPYTANIE = 500                # znaków zapytania w logu (wklejony akapit nie trafi w całości)

NOTION_API = "https://api.notion.com"
GITHUB_API = "https://api.github.com"
# Działa 2025-09-03 (data sources; sprawdzone sondą schematu). Zapas 2022-06-28 z POST /v1/databases/{id}/query
# wdrażać tylko, gdyby ta wersja zaczęła zwracać błąd wersji.
NOTION_WERSJA = "2025-09-03"
# Kolejność = kolejność synchronizacji. Klucz = tabela SQLite; "numer" = nazwa właściwości unique_id
# (w sondzie "ID" we wszystkich trzech bazach z numerem; Tematy nie mają numeru – kluczem jest ID strony);
# "klucz" = kolumna klucza głównego tabeli.
BAZY = {
    "tematy": {"zrodlo": "718422ca-ed6f-4269-a38f-4e508eff286c", "numer": None, "klucz": "id"},
    "zrodla": {"zrodlo": "35453d82-e38d-4797-840c-d19677c71b54", "numer": "ID", "klucz": "zrd"},
    "sprzecznosci": {"zrodlo": "7589d5f5-2d22-4b85-9138-72cd34d4a1f8", "numer": "ID", "klucz": "sp"},
    "informacje": {"zrodlo": "f78bb02d-6da5-46fb-bea9-c25e15f93117", "numer": "ID", "klucz": "wi"},
}

ODSTEP_NOTION = 0.35        # s między żądaniami do Notion (limit ok. 3 zapytań/s)
ZAPAS_MIN = 5               # filtr przyrostowy: ostatnie `zmieniono` minus tyle minut
PELNY_CO_DNI = 7
PUBLIKACJA_CO_MIN = 60
LIMIT_HISTORII_MB = 500     # powyżej `stan` zaleca publikuj --reset
# Zachowawczy limit treści base64 jednego pliku (base64 to ok. +1/3, więc plik indeksu do ok. 37 MB): duży zapas
# względem limitów plików GitHuba, a limit wysyłki (20 s + 5 s/MB) mieści się w 300 s nocnego skryptu.
LIMIT_PLIKU_MB = 50
SCHEMAT_WERSJA = 1          # PRAGMA user_version; podbij przy zmianie schematu, normalizacji albo treści FTS
ZNACZNIK = 0x57494544       # PRAGMA application_id („WIED”): plik jest indeksem wiedzy – w każdej wersji schematu
BUDZET_CICHO = 110          # s na całe sync --cicho (pobór i publikacja) liczone od startu; hook ma limit 120 s
BUDZET_SENS_CICHO = 20      # s na odciski i listy podobnych po publikacji, w granicach BUDZET_CICHO (po 1 filmie kilka s)
GITHUB_WERSJA = "2022-11-28"
MB = 1024 * 1024
WZORZEC_REPO = re.compile(r"[\w.-]+/[\w.-]+")

LIMIT_RETRY_AFTER = 60      # s, najdłuższe czekanie na 429
PROBY_429 = 5               # łączna liczba prób przy 429
ZAPAS_PROBY = 0.5           # s: krótszej reszty limitu czasu nie zaczynamy żądania
DLUGOSC_KOMUNIKATU = 300
BEARER = re.compile(r"bearer\s+\S+", re.I)

ostatnie_notion = 0.0       # time.monotonic() ostatniego żądania do Notion


def ostrzez(tekst: str):
    print(f"  ! {tekst}")


def blad(tekst: str):
    print(f"  ✗ {tekst}")


def wczytaj_sekrety(plik: Path) -> dict:
    """{KLUCZ: wartość} z wierszy `KLUCZ=wartość`; brak pliku → {}. Wartości nigdy nie są wypisywane."""
    try:
        tekst = plik.read_text(encoding="utf-8")
        tryb = plik.stat().st_mode & 0o777
    except FileNotFoundError:
        return {}
    if tryb & 0o077:
        ostrzez(f"{plik.name} ma uprawnienia {tryb:o} – ustaw chmod 600")
    sekrety = {}
    for linia in tekst.splitlines():
        # kotwica na początku wiersza: komentarze w pliku też zawierają nazwy zmiennych
        m = re.match(r"([A-Za-z_]\w*)=(.*)$", linia)
        if m and m.group(2).strip():
            sekrety[m.group(1)] = m.group(2).strip()
    return sekrety


def redaguj(tekst: str, sekrety: dict, nazwy=()) -> str:
    """Zasłania wartości sekretów (od 8 znaków), każdy nagłówek `Bearer …` i `nazwy` (człony nazwy repo, od 3 znaków,
    bez względu na wielkość liter, tylko jako całe słowa – krótki człon nie psuje reszty komunikatu). Członu krótszego
    niż 3 znaki nie da się sensownie zasłonić: jako całe słowo pasowałby do przypadkowych fragmentów komunikatu."""
    for wartosc in sorted(sekrety.values(), key=len, reverse=True):
        if len(wartosc) >= 8:
            tekst = tekst.replace(wartosc, "***")
    for nazwa in sorted(nazwy, key=len, reverse=True):
        if len(nazwa) >= 3:
            tekst = re.sub(r"(?<![\w-])" + re.escape(nazwa) + r"(?![\w-])", "***", tekst, flags=re.I)
    return BEARER.sub("***", tekst)


def tekst_bledu(e: Exception, sekrety: dict, nazwy=()) -> str:
    """Błąd HTTP lub sieci do komunikatu: najpierw redakcja, potem skrót – przecięta wartość nie zostałaby
    rozpoznana."""
    return redaguj(str(e), sekrety, nazwy)[:DLUGOSC_KOMUNIKATU]


class BladHttp(Exception):
    """Odpowiedź 4xx/5xx; niesie tylko status i pola `code`/`message` z ciała, po redakcji."""

    def __init__(self, status: int, code: str = "", message: str = ""):
        super().__init__(status, code, message)
        self.status, self.code, self.message = status, code, message

    def __str__(self) -> str:
        return " ".join(c for c in (f"HTTP {self.status}", self.code, self.message) if c)


class BladSieci(Exception):
    """Brak połączenia albo przekroczony limit czasu; niesie tylko nazwę typu błędu (bez adresu) albo LIMIT_CZASU,
    gdy wyczerpał się termin polecenia."""


LIMIT_CZASU = "limit czasu startu"


def pola_bledu(cialo: bytes) -> tuple:
    try:
        dane = json.loads(cialo.decode("utf-8", "replace"))
    except ValueError:
        return "", ""
    if not isinstance(dane, dict):
        return "", ""
    return str(dane.get("code") or ""), str(dane.get("message") or "")


def odczekaj_notion():
    global ostatnie_notion
    reszta = ODSTEP_NOTION - (time.monotonic() - ostatnie_notion)
    if reszta > 0:
        time.sleep(reszta)
    ostatnie_notion = time.monotonic()


class BezPrzekierowan(urllib.request.HTTPRedirectHandler):
    """Przekierowanie 3xx kończy się błędem HTTP: urllib przeniósłby nagłówek Authorization także na inny host."""

    def redirect_request(self, *args, **kwargs):
        return None


OTWIERACZ = urllib.request.build_opener(BezPrzekierowan)  # jedyne wyjście do sieci (zadanie_http)


def zadanie_http(metoda: str, url: str, naglowki: dict, dane=None, timeout: float = 20, termin=None) -> dict:
    """Żądanie JSON. Powtarza tylko 429 (Retry-After, najwyżej PROBY_429 prób); 5xx, 3xx i błąd sieci – od razu
    wyjątek. termin = time.monotonic() końca limitu polecenia albo None: każda próba dostaje najwyżej resztę
    czasu, a czekanie na 429, które się w niej nie mieści, kończy się BladHttp(429). Adres nie trafia do błędów –
    ścieżki GitHuba zawierają nazwę prywatnego repo."""
    cialo = None if dane is None else json.dumps(dane).encode("utf-8")
    naglowki = dict(naglowki)
    if cialo is not None:
        naglowki.setdefault("Content-Type", "application/json")
    # ukrywamy dokładnie to, co wysłaliśmy – serwer może odesłać token w treści błędu
    wyslane = {k: v.split(" ", 1)[-1] for k, v in naglowki.items() if k.lower() == "authorization"}
    for proba in range(1, PROBY_429 + 1):
        if url.startswith(NOTION_API):
            odczekaj_notion()
        limit = timeout if termin is None else min(timeout, termin - time.monotonic())  # po odstępie Notion
        if limit < ZAPAS_PROBY:
            raise BladSieci(LIMIT_CZASU)
        zadanie = urllib.request.Request(url, data=cialo, headers=naglowki, method=metoda)
        try:
            with OTWIERACZ.open(zadanie, timeout=limit) as odp:
                tresc = odp.read()
            return json.loads(tresc.decode("utf-8")) if tresc else {}
        except urllib.error.HTTPError as e:
            status, tresc_bledu, retry_after = e.code, e.read(), e.headers.get("Retry-After")
            e.close()
            if status == 429 and proba < PROBY_429:
                try:
                    czekaj = min(max(float(retry_after), 0), LIMIT_RETRY_AFTER)
                except (TypeError, ValueError):
                    czekaj = 1
                if termin is None or time.monotonic() + czekaj + ZAPAS_PROBY < termin:
                    time.sleep(czekaj)
                    continue
            code, message = pola_bledu(tresc_bledu)
            # pełna treść (bez wysłanego tokena); skrót dopiero przy wydruku, po redakcji nazw (tekst_bledu)
            raise BladHttp(status, redaguj(code, wyslane), redaguj(message, wyslane)) from None
        except (OSError, http.client.HTTPException) as e:
            raise BladSieci(type(e).__name__) from None


TABELA_L = str.maketrans({"ł": "l", "Ł": "L"})


def normalizuj(tekst: str) -> str:
    """NFC, ł→l, małe litery – tokenizer unicode61 usuwa diakrytyki, ale „ł” nie ma rozkładu i zostałoby literą."""
    return unicodedata.normalize("NFC", tekst or "").translate(TABELA_L).lower()


def bez_diakrytykow(tekst: str) -> str:
    """Do porównań w temat i duplikaty: najpierw normalizuj (ł), potem NFKD bez znaków łączących."""
    return "".join(z for z in unicodedata.normalize("NFKD", normalizuj(tekst)) if not unicodedata.combining(z))


def wczytaj_synonimy(plik: Path) -> list:
    """Grupy synonimów (listy terminów po normalizuj) z wierszy `termin = syn1, syn2`; brak pliku → []."""
    try:
        tekst = plik.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    grupy = []
    for nr, linia in enumerate(tekst.splitlines(), 1):
        linia = linia.strip()
        if not linia or linia.startswith("#"):
            continue
        if "=" not in linia:
            ostrzez(f"{plik.name}: wiersz {nr} bez „=” – pominięty")
            continue
        termin, reszta = linia.split("=", 1)
        grupa = []
        for t in [termin] + reszta.split(","):
            t = " ".join(normalizuj(t).split())
            if t and t not in grupa:
                grupa.append(t)
        grupy.append(grupa)
    return grupy


def wzorzec_terminu(termin: str) -> str:
    return r"(?<!\w)" + r"\s+".join(re.escape(s) for s in termin.split()) + r"(?!\w)"


def rozwin_synonimy(tekst: str, grupy: list) -> str:
    """Kolumna `slowa`: pozostałe terminy każdej grupy, której termin występuje w tekście jako całe słowo(a)."""
    tekst, slowa = normalizuj(tekst), []
    for grupa in grupy:
        # najpierw tani test podciągu (pierwsze słowo terminu musi wystąpić), regex tylko dla kandydatów
        obecne = [t for t in grupa if t.split()[0] in tekst and re.search(wzorzec_terminu(t), tekst)]
        if obecne:
            slowa += [t for t in grupa if t not in obecne and t not in slowa]
    return " ".join(slowa)


ELEMENT_ZAPYTANIA = re.compile(r'"([^"]*)"|(\S+)')  # fraza w domkniętym cudzysłowie albo zwykły token
NIE_SLOWO = re.compile(r"[\W_]+")
# słowa wypełniające pytań (po bez_diakrytykow) – w zapytaniu AND wycinałyby prawie wszystko albo nic nie wnosiły
STOP_ZAPYTANIA = frozenset("""czy jak co na w z ze do po dla oraz jest sa byc moze mozna ma mam by sie to ten ta te
o od u i a ale lub albo nie tak przy nad pod bez za przez jaki jaka jakie kiedy gdzie ile wiemy wiem warto robic
zrobic potrzebny potrzebna potrzebne potrzeba trzeba nalezy powinien powinna powinno dobrze lepiej najlepiej czym
miedzy pomiedzy moge moga""".split())
TEMAT_OD = 6                # od tylu liter token traci końcówkę odmiany, najwyżej 2 litery: „przerwie” → przerw*
TEMAT_MIN = 5               # tyle liter zostaje co najmniej: 6-literowe tracą 1 („termin” → termi*, nie term*)
# szukaj: mniej widocznych trafień AND → dopełnienie trafieniami OR; tyle co domyślny --limit, bo wąskie AND
# (5–11 trafień) zostawiało pytaniom naturalnym krótką listę bez wierszy pasujących do części słów
DOPELNIJ_PONIZEJ = 12
# szukaj z kilkoma zapytaniami: wyniki łączone przez reciprocal rank fusion – suma 1 / (RRF_K + pozycja) po
# zapytaniach; 60 to wartość z literatury (nie strojona na zbiorze testowym), wiersz z kilku list idzie wyżej
RRF_K = 60
LIMIT_DOMYSLNY = 12
LIMIT_KROTKO = 25           # linia --krotko ma ok. 1/3 długości pełnej: 25 linii to ok. połowa znaków 12 pełnych
KROTKO_TEZA = 220
KROTKO_TEMAT = 30           # znaków nazwy tematu
KROTKO_TEMATOW = 3
KROTKO_ZRODEL = 2
KROTKO_DYLEMAT = 160
TYP_AUTORA_KONIEC = re.compile(r" / | \(")   # „Twórca / popularyzator” → „Twórca”
# --krotko: sekcja „podobne do trafień” z tabeli `podobne` (odciski znaczenia, tools/wiedza_sens.py) – sąsiedzi
# PODOBNE_Z_TRAFIEN pierwszych pokazanych trafień z podobieństwem co najmniej PODOBNE_PROG, najwyżej PODOBNE_LINII
# linii; wartości skalibrowane na zamrożonym zestawie pytań Z1 (2026-10-26)
PODOBNE_PROG = 0.7
PODOBNE_Z_TRAFIEN = 5
PODOBNE_LINII = 8
SENS_LISTA = 50             # szukaj --sens: tyle najbliższych znaczeniem na zapytanie idzie do łączenia RRF
# etap: cała wiedza etapu w częściach – narzędzie czatu ucina wynik powyżej ok. 30 tys. znaków (Z5, 26.10.2026)
ETAP_CZESC_ZNAKOW = 25000
ETAP_WSPOLNY = "Cała budowa"   # tezy tego etapu wchodzą do każdego etapu
ETAP_RODZAJE_KONTROLI = ("kontrola / odbior", "kolejnosc prac")   # --kontrola: te rodzaje z innych etapów (bez_diakrytykow)
# kolejność etapów budowy: spis kart (karty) i porcje tez w tools/wiedza_karty.py; etap spoza listy – na końcu
ETAPY_KOLEJNOSC = ("Projekt i formalności", "Stan zero", "SSO", "Deweloperski", "Wykończenie", "Teren i ogród",
                   ETAP_WSPOLNY)
# karty wiedzy: czat na telefonie czyta w całości ok. 75 tys. znaków – tyle razem kart doradza nagłówek spisu
KARTY_RAZEM_ZNAKOW = 75000
KARTY_TOP = 60              # karty --do: tyle pierwszych trafień (RRF zapytań) liczy się do dopasowania kart
KARTY_DOPASOWANYCH = 12     # karty --do: najwyżej tyle kart w sekcji dopasowania
KARTY_POZA = 15             # karty --do: najwyżej tyle numerów trafień spoza wszystkich kart
KARTY_OPIS_ZNAKOW = 200     # spis kart: opis karty skrócony (pełny opis w karta i --json)
KARTY_PYTANIE_ZNAKOW = 110  # spis kart: przykładowe pytanie skrócone
DOPELNIENIE_TOP = 40        # karta --pytanie: dopełnienie z tylu pierwszych trafień (RRF zapytań) …
DOPELNIENIE_LINII = 20      # … najwyżej tyle tez spoza karty
RODZAJE_KART = ("pytanie", "czynnosc")
TYTUL_SP_KARTY = "Otwarte sprzeczności"
ZRODLO_WIECEJ = "wiecej"    # karty_wi.zrodlo rozszerzenia karty (tezy pokrewne poza rdzeniem, `karta --wiecej`)
BRAK_KART = "# karty: brak w tej kopii indeksu – użyj szukaj / temat / etap"


def termin_tokenu(slowo: str, prefiks: bool) -> str:
    """Token → "temat"*: dłuższe słowa z samych liter bez końcówki, żeby forma odmieniona łapała podstawową
    („roboczej” → robocz*); jawny prefiks z `*` zostaje bez zmian."""
    if not prefiks and slowo.isalpha() and len(slowo) >= TEMAT_OD:
        slowo = slowo[:max(TEMAT_MIN, len(slowo) - 2)]
    return '"%s"*' % slowo


def terminy_zapytania(zapytanie: str) -> tuple:
    """(terminy, same_stop): lista (termin FTS, forma pełna) albo ("OR", None) – "OR" tylko między dwoma terminami.
    Forma pełna to "słowo"* tokenu, któremu termin_tokenu uciął końcówkę (premia formy dokładnej w szukaj), inaczej
    None. Frazy i operator `OR` (wielkimi literami) rozpoznawane na surowym wejściu – po normalizuj byłby zwykłym „or”.
    Potem każdy element osobno: normalizuj, znaki spoza liter i cyfr → odstęp (niedomknięty cudzysłów, `-`, `*`,
    `NEAR(` przestają być składnią); token → "temat"* (termin_tokenu), fraza bez * i bez zmian. Słowa wypełniające
    (STOP_ZAPYTANIA) wypadają, chyba że zapytanie składa się tylko z nich (same_stop); nie dotyczy to fraz ani
    tokenów z `*`."""
    terminy = []  # (termin FTS, forma pełna, czy słowo wypełniające)
    for m in ELEMENT_ZAPYTANIA.finditer(zapytanie or ""):
        fraza, token = m.groups()
        if token == "OR":
            terminy.append(("OR", None, False))
        elif fraza is not None:
            slowa = NIE_SLOWO.sub(" ", normalizuj(fraza)).split()
            if slowa:
                terminy.append(('"%s"' % " ".join(slowa), None, False))
        else:
            prefiks = token.endswith("*")
            for s in NIE_SLOWO.sub(" ", normalizuj(token)).split():
                termin, pelna = termin_tokenu(s, prefiks), '"%s"*' % s
                terminy.append((termin, pelna if pelna != termin else None,
                                not prefiks and bez_diakrytykow(s) in STOP_ZAPYTANIA))
    same_stop = all(stop for t, _, stop in terminy if t != "OR")
    czyste = []
    for t, pelna, stop in terminy:
        if (same_stop or not stop) and (t != "OR" or (czyste and czyste[-1][0] != "OR")):
            czyste.append((t, pelna))
    if czyste and czyste[-1][0] == "OR":
        czyste.pop()
    return czyste, same_stop


def zbuduj_zapytanie_fts(zapytanie: str, tryb: str = "AND"):
    """Ciąg MATCH dla informacje_fts albo None, gdy nie zostaje żaden termin; tryb "AND" albo "OR" (terminy jak
    w terminy_zapytania). Tryb "OR" z samych słów wypełniających → None: każde z nich trafia przypadkowo („na…”, „w…”)."""
    terminy, same_stop = terminy_zapytania(zapytanie)
    if not terminy or (same_stop and tryb == "OR"):
        return None
    if tryb == "OR":
        return " OR ".join(t for t, _ in terminy if t != "OR")
    return " ".join(t for t, _ in terminy)


def czytaj_tekst(w: dict) -> str:
    return "".join(s.get("plain_text") or "" for s in w.get(w["type"]) or [])


def czytaj_select(w: dict) -> str:
    return (w.get(w["type"]) or {}).get("name") or ""


def czytaj_multi(w: dict) -> str:
    return "; ".join(o.get("name") or "" for o in w.get("multi_select") or [])


def czytaj_relacje(w: dict) -> list:
    return [r["id"] for r in w.get("relation") or []]


def czytaj_unique_id(w: dict):
    return (w.get("unique_id") or {}).get("number")


def czytaj_checkbox(w: dict) -> int:
    return 1 if w.get("checkbox") else 0


def czytaj_date(w: dict) -> str:
    return (w.get("date") or {}).get("start") or ""


def czytaj_url(w: dict) -> str:
    return w.get("url") or ""


# Czytnik wybierany po typie właściwości, nie po nazwie: Branża i Etap bywają select albo multi_select (Rejestr),
# a Status może być typu status. Typ spoza listy (rollup, formuła) → None.
CZYTNIKI = {"title": czytaj_tekst, "rich_text": czytaj_tekst, "select": czytaj_select, "status": czytaj_select,
            "multi_select": czytaj_multi, "relation": czytaj_relacje, "unique_id": czytaj_unique_id,
            "checkbox": czytaj_checkbox, "date": czytaj_date, "url": czytaj_url}

# kolumna ← właściwość Notion (nazwy jak w notion-wiedza.md, potwierdzone sondą). Nazwa z „*” na końcu = dopasowanie
# po początku: właściwość Rejestru „Pytanie do …” ma w nazwie imię inwestora, którego nie ma w repo.
# Rollupy (Potwierdzenia, Data informacji) i relacje od strony Tematów i Źródeł nie są czytane.
MAPOWANIE = {
    "tematy": {"nazwa": "Temat", "w_skrocie": "W skrócie", "stan_wiedzy": "Stan wiedzy", "etap": "Etap",
               "branza": "Branża", "kluczowe_dla": "Kluczowe dla"},
    "zrodla": {"tytul": "Rozmowa", "data": "Data", "forma": "Forma", "kto": "Kto", "z_kim": "Z kim",
               "najwazniejsze": "Najważniejsze", "link": "Link", "typ_autora": "Typ autora",
               "konflikt": "Konflikt interesów", "wiarygodnosc": "Wiarygodność"},
    "sprzecznosci": {"dylemat": "Dylemat", "status": "Status", "rodzaj": "Rodzaj", "branza": "Branża", "etap": "Etap",
                     "priorytet": "Priorytet", "stanowisko_a": "Stanowisko A", "stanowisko_b": "Stanowisko B",
                     "kontekst": "Kontekst naszej budowy", "opcje": "Opcje", "rekomendacja": "Rekomendacja asystenta",
                     "pytanie": "Pytanie do*", "decyzja": "Decyzja", "uzasadnienie": "Uzasadnienie",
                     "konsekwencje": "Konsekwencje", "data_decyzji": "Data decyzji"},
    "informacje": {"teza": "Informacja", "szczegoly": "Szczegóły", "dla_nas": "Dla naszej budowy",
                   "fragment": "Fragment", "rodzaj": "Rodzaj", "etap": "Etap", "branza": "Branża",
                   "istotnosc": "Istotność", "status": "Status", "dotyczy_nas": "Dotyczy nas",
                   "moj_komentarz": "Mój komentarz", "wrazliwe_na_czas": "Wrażliwe na czas", "pokazano": "Pokazano"},
}
# relacje czytane wyłącznie od strony Informacji: tabela relacji ← (właściwość, kolumna z ID strony po drugiej stronie)
RELACJE = {"informacje_tematy": ("Tematy", "temat_id"), "informacje_zrodla": ("Źródła", "zrd_id"),
           "informacje_sp": ("Sprzeczności", "sp_id"), "informacje_notatnik": ("Notatnik", "notatnik_id")}


class BladMapowania(Exception):
    """Strona nie pasuje do mapowania (brak właściwości); komunikat zawiera tylko nazwy baz i właściwości."""


def wlasciwosc(baza: str, wlasciwosci: dict, nazwa: str) -> dict:
    if nazwa.endswith("*"):
        pasujace = [n for n in wlasciwosci if n.startswith(nazwa[:-1])]
        if len(pasujace) != 1:
            raise BladMapowania(f"{baza}: {len(pasujace)} właściwości o nazwie zaczynającej się od „{nazwa[:-1]}”")
        nazwa = pasujace[0]
    if nazwa not in wlasciwosci:
        raise BladMapowania(f"{baza}: brak właściwości „{nazwa}”")
    return wlasciwosci[nazwa]


def wartosc(w: dict):
    czytnik = CZYTNIKI.get(w.get("type"))
    return czytnik(w) if czytnik else None


def wlasciwosc_numeru(baza: str, wlasciwosci: dict) -> dict:
    """Właściwość unique_id po nazwie z BAZY, a gdy nazwa się różni – pierwsza tego typu."""
    w = wlasciwosci.get(BAZY[baza]["numer"])
    if not w or w.get("type") != "unique_id":
        w = next((v for v in wlasciwosci.values() if v.get("type") == "unique_id"), None)
    if w is None:
        raise BladMapowania(f"{baza}: brak właściwości typu unique_id")
    return w


def mapuj_strone(baza: str, strona: dict):
    """Strona z odpowiedzi API → (kolumny, relacje) albo None, gdy stronę pomijamy (kosz, archiwum, obiekt inny niż
    strona, brak numeru). kolumny: {kolumna tabeli `baza`: wartość} – komplet kolumn tabeli; relacje: {tabela relacji:
    [ID stron]} tylko dla informacji, dla pozostałych baz {}."""
    if strona.get("object") != "page" or strona.get("in_trash") or strona.get("archived"):
        return None
    wlasciwosci = strona.get("properties") or {}
    kolumny = {"id": strona["id"]}
    klucz = BAZY[baza]["klucz"]
    if klucz != "id":
        numer = czytaj_unique_id(wlasciwosc_numeru(baza, wlasciwosci))
        if numer is None:
            ostrzez(f"{baza}: strona {strona['id']} bez numeru – pominięta")
            return None
        kolumny[klucz] = numer
    for kolumna, nazwa in MAPOWANIE[baza].items():
        kolumny[kolumna] = wartosc(wlasciwosc(baza, wlasciwosci, nazwa))
    kolumny["notion_url"] = strona.get("url") or ""
    kolumny["zmieniono"] = strona.get("last_edited_time") or ""
    relacje = {}
    if baza == "informacje":
        kolumny["dodano"] = strona.get("created_time") or ""
        for tabela, (nazwa, _) in RELACJE.items():
            w = wlasciwosc(baza, wlasciwosci, nazwa)
            if w.get("has_more"):
                ostrzez(f"WI-{kolumny['wi']}: relacja „{nazwa}” ma więcej powiązań, niż zwraca API – w indeksie część")
            relacje[tabela] = czytaj_relacje(w) if w.get("type") == "relation" else []
    return kolumny, relacje


SCHEMAT = """
CREATE TABLE tematy      (id TEXT PRIMARY KEY, nazwa TEXT, w_skrocie TEXT, stan_wiedzy TEXT, etap TEXT, branza TEXT,
                          kluczowe_dla TEXT, notion_url TEXT, zmieniono TEXT);
CREATE TABLE zrodla      (zrd INTEGER PRIMARY KEY, id TEXT UNIQUE, tytul TEXT, data TEXT, forma TEXT, kto TEXT, z_kim TEXT,
                          najwazniejsze TEXT, link TEXT, typ_autora TEXT, konflikt TEXT, wiarygodnosc TEXT, notion_url TEXT,
                          zmieniono TEXT);
CREATE TABLE sprzecznosci(sp INTEGER PRIMARY KEY, id TEXT UNIQUE, dylemat TEXT, status TEXT, rodzaj TEXT, branza TEXT,
                          etap TEXT, priorytet TEXT, stanowisko_a TEXT, stanowisko_b TEXT, kontekst TEXT, opcje TEXT,
                          rekomendacja TEXT, pytanie TEXT, decyzja TEXT, uzasadnienie TEXT, konsekwencje TEXT,
                          data_decyzji TEXT, notion_url TEXT, zmieniono TEXT);
CREATE TABLE informacje  (wi INTEGER PRIMARY KEY, id TEXT UNIQUE, teza TEXT, szczegoly TEXT, dla_nas TEXT, fragment TEXT,
                          rodzaj TEXT, etap TEXT, branza TEXT, istotnosc TEXT, status TEXT, dotyczy_nas TEXT,
                          moj_komentarz TEXT, wrazliwe_na_czas INTEGER, pokazano TEXT, notion_url TEXT, dodano TEXT,
                          zmieniono TEXT);
CREATE TABLE informacje_tematy   (wi INTEGER, temat_id TEXT, PRIMARY KEY (wi, temat_id));
CREATE TABLE informacje_zrodla   (wi INTEGER, zrd_id TEXT, PRIMARY KEY (wi, zrd_id));
CREATE TABLE informacje_sp       (wi INTEGER, sp_id TEXT, PRIMARY KEY (wi, sp_id));
CREATE TABLE informacje_notatnik (wi INTEGER, notatnik_id TEXT, PRIMARY KEY (wi, notatnik_id));
CREATE TABLE sync_stan   (baza TEXT PRIMARY KEY, ostatnie_zmieniono TEXT, wierszy INTEGER, zsynchronizowano TEXT);
CREATE TABLE meta        (klucz TEXT PRIMARY KEY, wartosc TEXT);
CREATE VIRTUAL TABLE informacje_fts USING fts5(teza, tematy, szczegoly, dla_nas, slowa,
                          tokenize='unicode61 remove_diacritics 2');  -- rowid = wi
"""
# Listy podobnych (tools/wiedza_sens.py) – dopisane do schematu 1 bez przebudowy: indeks bez tej tabeli dostaje ją
# przy otwarciu do zapisu (otworz_db), a odczyt (kopia w czacie sprzed zmiany) działa bez niej. Poza hashem
# danych – zmianę list niesie meta.podobne_policzone.
SCHEMAT_PODOBNE = """
CREATE TABLE IF NOT EXISTS podobne (wi INTEGER, wi_podobne INTEGER, podobienstwo REAL,
                          PRIMARY KEY (wi, wi_podobne)) WITHOUT ROWID;
"""
# Karty wiedzy (tools/wiedza_karty.py: zbiory WI na typowe pytania; zrodlo wpisu – model, tag albo wzorzec) –
# dopisane do schematu 1 tak samo jak `podobne`. Poza hashem danych – zmianę kart niesie meta.karty_zbudowano.
SCHEMAT_KARTY = """
CREATE TABLE IF NOT EXISTS karty (kod TEXT PRIMARY KEY, rodzaj TEXT, nazwa TEXT, etap TEXT, opis TEXT, pytania TEXT,
                          zbudowano TEXT, pokrycie REAL, pokrycie_k REAL, pokrycie_opis TEXT);
CREATE TABLE IF NOT EXISTS karty_wi (kod TEXT, wi INTEGER, zrodlo TEXT, PRIMARY KEY (kod, wi)) WITHOUT ROWID;
"""
SCHEMAT += SCHEMAT_PODOBNE + SCHEMAT_KARTY
# tabele dopisywane do indeksu schematu 1 bez przebudowy (otworz_db): ich brak nie kasuje danych
DOPISYWANE = frozenset({"podobne", "karty", "karty_wi"})
# treść indeksu do hasha publikacji; sync_stan, meta i FTS (pochodna) poza nim
TABELE_DANYCH = ("tematy", "zrodla", "sprzecznosci", "informacje",
                 "informacje_tematy", "informacje_zrodla", "informacje_sp", "informacje_notatnik")


class BladIndeksu(Exception):
    """Pliku indeksu nie da się użyć (brak, inna wersja schematu, brak FTS5, obcy plik); komunikat bez wartości
    pól."""


def sprawdz_fts5() -> bool:
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE VIRTUAL TABLE t USING fts5(x)")
        return True
    except sqlite3.OperationalError:
        return False
    finally:
        conn.close()


# obiekty schematu bez wewnętrznych SQLite (sqlite_…); ten sam zbiór porównuje otworz_db i usuwa utworz_schemat
BEZ_WEWNETRZNYCH = "name NOT LIKE 'sqlite\\_%' ESCAPE '\\'"
NAZWY_OBIEKTOW = f"SELECT name FROM sqlite_master WHERE {BEZ_WEWNETRZNYCH}"
# Obiekty schematu 1, zamrożone: indeks zbudowany przed znacznikiem (ZNACZNIK) rozpoznajemy po nich i po wersji 1
NAZWY_V1 = frozenset("""tematy zrodla sprzecznosci informacje informacje_tematy informacje_zrodla informacje_sp
informacje_notatnik sync_stan meta informacje_fts informacje_fts_data informacje_fts_idx informacje_fts_content
informacje_fts_docsize informacje_fts_config""".split())
NIEZBEDNE_V1 = {"meta", "sync_stan", "informacje"}


def nazwy_schematu() -> set:
    """Nazwy obiektów, które zakłada SCHEMAT, razem z tabelami pomocniczymi FTS5 – z próbnej bazy w pamięci."""
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(SCHEMAT)
        return {n for (n,) in conn.execute(NAZWY_OBIEKTOW)}
    finally:
        conn.close()


def uszkodzony(e: BaseException) -> bool:
    """Plik nie jest bazą albo ma zepsute strony: sqlite3 zgłasza wtedy sam DatabaseError; podklasy (zajęta baza,
    brak dostępu, błąd zapytania – OperationalError i inne) to nie uszkodzenie."""
    return type(e) is sqlite3.DatabaseError


def utworz_schemat(conn: sqlite3.Connection):
    """Tabele od nowa w jednej transakcji: usuwa wszystkie obiekty spoza wewnętrznych SQLite – widoki, wyzwalacze
    i indeksy, potem tabele wirtualne (ich tabele pomocnicze znikają razem z nimi), na końcu zwykłe; obcy obiekt,
    który by został, wywoływałby przebudowę przy każdym otwarciu. Zakłada SCHEMAT, ustawia user_version
    i ZNACZNIK. Pusta meta (brak ostatni_pelny) wymusza pełny sync."""
    obiekty = conn.execute(
        f"SELECT type, name FROM sqlite_master WHERE {BEZ_WEWNETRZNYCH} AND type IN ('view', 'trigger', 'index', "
        "'table') ORDER BY type = 'table', sql LIKE 'CREATE VIRTUAL TABLE%' DESC").fetchall()
    usun = "".join('DROP %s IF EXISTS "%s";' % (typ.upper(), nazwa.replace('"', '""')) for typ, nazwa in obiekty)
    conn.executescript(f"BEGIN; {usun} {SCHEMAT}; PRAGMA user_version = {SCHEMAT_WERSJA}; "
                       f"PRAGMA application_id = {ZNACZNIK}; COMMIT;")


def plik_indeksu(conn: sqlite3.Connection, nazwy: set) -> bool:
    """Niepusty plik jest indeksem wiedzy, gdy ma ZNACZNIK (dowolna wersja i lista tabel – wolno go przebudować) albo
    jest indeksem schematu 1 sprzed znacznika: user_version 1, obiekty z NAZWY_V1, w tym NIEZBEDNE_V1. Każdy inny,
    także z user_version 0, jest obcy – własny indeks ustawia wersję w tej samej transakcji co tabele."""
    if conn.execute("PRAGMA application_id").fetchone()[0] == ZNACZNIK:
        return True
    return (conn.execute("PRAGMA user_version").fetchone()[0] == 1 and nazwy <= NAZWY_V1
            and NIEZBEDNE_V1 <= nazwy)


def otworz_db(sciezka: Path, zapis: bool) -> sqlite3.Connection:
    """Odczyt: tylko do odczytu (URI mode=ro), pliku nie tworzy; brak pliku albo inna wersja schematu → BladIndeksu.
    Zapis (sync): tworzy plik (katalog musi istnieć); niepusty plik, który nie jest indeksem (plik_indeksu) →
    BladIndeksu i plik nietknięty; uszkodzony (quick_check) → sqlite3.DatabaseError; indeks bieżącej wersji, któremu
    brakuje tylko tabel z DOPISYWANE (listy podobnych, karty), dostaje je bez przebudowy; przy innej wersji albo innym
    zestawie tabel – tabele od nowa; indeks sprzed znacznika dostaje ZNACZNIK bez przebudowy.
    timeout=5 to busy_timeout 5000 ms; dziennik DELETE (bez WAL) – czat pobiera jeden plik."""
    sciezka = Path(sciezka)
    if zapis:
        if not sprawdz_fts5():
            raise BladIndeksu(f"SQLite {sqlite3.sqlite_version} bez FTS5 – indeks wymaga FTS5")
        conn = sqlite3.connect(str(sciezka), timeout=5)
        try:
            # przed pierwszym zapisem (PRAGMA journal_mode pisze do pliku): przebudowa kasuje tabele, więc wolno ją
            # zrobić tylko na pliku pustym albo na indeksie wiedzy – cudzej bazy nie ruszamy
            nazwy = {n for (n,) in conn.execute(NAZWY_OBIEKTOW)}
            if nazwy and not plik_indeksu(conn, nazwy):
                raise BladIndeksu(f"{sciezka.name}: plik nie jest indeksem wiedzy – nie nadpisuję go")
            if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise sqlite3.DatabaseError("quick_check")
            conn.execute("PRAGMA journal_mode = DELETE")
            wersja = conn.execute("PRAGMA user_version").fetchone()[0]
            schemat = nazwy_schematu()
            if wersja == SCHEMAT_WERSJA and nazwy < schemat and schemat - nazwy <= DOPISYWANE:
                # brakuje tylko tabel dopisywanych – CREATE IF NOT EXISTS bez przebudowy, dane zostają
                with conn:
                    conn.executescript(SCHEMAT_PODOBNE + SCHEMAT_KARTY)
                nazwy = {n for (n,) in conn.execute(NAZWY_OBIEKTOW)}
            if wersja != SCHEMAT_WERSJA or nazwy != schemat:
                if nazwy:
                    powod = (f"w schemacie {wersja}, wymagany {SCHEMAT_WERSJA}" if wersja != SCHEMAT_WERSJA
                             else "z innym zestawem tabel")
                    ostrzez(f"indeks {powod} – tabele od nowa, pełny sync")
                utworz_schemat(conn)
            elif conn.execute("PRAGMA application_id").fetchone()[0] != ZNACZNIK:
                conn.execute(f"PRAGMA application_id = {ZNACZNIK}")
        except BaseException:
            conn.close()
            raise
        return conn
    if not sciezka.is_file():
        raise BladIndeksu(f"brak pliku indeksu {sciezka} – uruchom sync (na Macu)")
    conn = sqlite3.connect(sciezka.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
    wersja = conn.execute("PRAGMA user_version").fetchone()[0]
    if wersja != SCHEMAT_WERSJA:
        conn.close()
        if wersja < SCHEMAT_WERSJA:
            raise BladIndeksu("indeks w starszym schemacie – uruchom sync (na Macu)")
        raise BladIndeksu("indeks w nowszym schemacie – zaktualizuj wiedza.py")
    return conn


def hash_danych(conn: sqlite3.Connection) -> str:
    """SHA-256 treści indeksu (TABELE_DANYCH w kolejności klucza głównego), wersji schematu, meta.synonimy_sha,
    meta.podobne_policzone (czas ostatniej zmiany list podobnych) i meta.karty_zbudowano (czas zapisu kart). Zmiana
    samego czasu synchronizacji lub publikacji (reszta meta, sync_stan) nie zmienia hasha."""
    h = hashlib.sha256()
    wersja = conn.execute("PRAGMA user_version").fetchone()[0]
    meta = meta_bazy(conn)
    h.update(json.dumps([wersja, meta.get("synonimy_sha")] + [
        meta[k] for k in ("podobne_policzone", "karty_zbudowano") if k in meta]).encode("utf-8"))
    for tabela in TABELE_DANYCH:
        h.update(f"\n#{tabela}".encode("utf-8"))
        # kolumna 1 to klucz główny tabel głównych; w tabelach relacji kluczem jest para (1, 2)
        for wiersz in conn.execute(f"SELECT * FROM {tabela} ORDER BY 1, 2"):
            h.update(b"\n" + json.dumps(list(wiersz), ensure_ascii=False).encode("utf-8"))
    return h.hexdigest()


def git_blob_sha(bajty: bytes) -> str:
    """SHA-1 obiektu blob gita – porównanie pliku lokalnego z `sha` z GitHuba bez pobierania treści."""
    return hashlib.sha1(b"blob %d\0" % len(bajty) + bajty).hexdigest()


@contextlib.contextmanager
def blokada(plik_bazy: Path):
    """Wyłączna blokada `<plik bazy>.lock` na czas polecenia; zwraca True, gdy wzięta, False, gdy trzyma ją inny
    proces. Bierze ją raz polecenie najwyższego poziomu (sync albo publikuj) – flock należy do otwartego pliku,
    więc ponowne wzięcie w tym samym procesie by się nie udało; publikacja w sync --publikuj działa pod tą."""
    import fcntl  # leniwie: polecenia odczytu działają też tam, gdzie fcntl nie ma
    plik = open(str(plik_bazy) + ".lock", "a")
    try:
        try:
            fcntl.flock(plik, fcntl.LOCK_EX | fcntl.LOCK_NB)
            wzieta = True
        except BlockingIOError:
            wzieta = False
        yield wzieta
    finally:
        plik.close()  # zamknięcie zwalnia blokadę


class BladPoboru(Exception):
    """Pobór bazy z Notion nie powiódł się; niesie nazwę bazy i przyczynę (BladHttp albo BladSieci)."""

    def __init__(self, baza: str, przyczyna: Exception):
        super().__init__(baza, przyczyna)
        self.baza, self.przyczyna = baza, przyczyna


def teraz_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def na_czas(tekst: str) -> datetime:
    """Czas ISO (także z końcówką Z z API – Python 3.9 jej nie przyjmuje) → datetime."""
    return datetime.fromisoformat(tekst.replace("Z", "+00:00"))


def starsze_niz(tekst, okres: timedelta) -> bool:
    return not tekst or datetime.now(timezone.utc) - na_czas(tekst) > okres


def pobierz_baze(baza: str, token: str, od, termin) -> list:
    """Wszystkie strony bazy rosnąco po last_edited_time (stronicowanie has_more/next_cursor); od=None → bez filtra
    (tryb pełny); termin – jak w zadanie_http."""
    url = f"{NOTION_API}/v1/data_sources/{BAZY[baza]['zrodlo']}/query"
    naglowki = {"Authorization": "Bearer " + token, "Notion-Version": NOTION_WERSJA}
    cialo = {"page_size": 100, "sorts": [{"timestamp": "last_edited_time", "direction": "ascending"}]}
    if od:
        cialo["filter"] = {"timestamp": "last_edited_time", "last_edited_time": {"on_or_after": od}}
    strony = []
    while True:
        odp = zadanie_http("POST", url, naglowki, cialo, termin=termin)
        strony += odp.get("results") or []
        if not odp.get("has_more") or not odp.get("next_cursor"):
            return strony
        cialo["start_cursor"] = odp["next_cursor"]


def pobierz(token: str, filtry: dict, termin) -> dict:
    """{baza: strony} dla wszystkich baz w kolejności BAZY; błąd dowolnej bazy przerywa całość przed zapisem."""
    pobrane = {}
    for baza in BAZY:
        try:
            pobrane[baza] = pobierz_baze(baza, token, filtry.get(baza), termin)
        except (BladHttp, BladSieci) as e:
            raise BladPoboru(baza, e) from None
    return pobrane


def wiersz_po_id(conn: sqlite3.Connection, baza: str, id_: str):
    kursor = conn.execute(f"SELECT * FROM {baza} WHERE id = ?", (id_,))
    wiersz = kursor.fetchone()
    return None if wiersz is None else dict(zip([k[0] for k in kursor.description], wiersz))


def relacje_informacji(conn: sqlite3.Connection, wi: int) -> dict:
    return {t: {i for (i,) in conn.execute(f"SELECT {k} FROM {t} WHERE wi = ?", (wi,))}
            for t, (_, k) in RELACJE.items()}


def usun_relacje_informacji(conn: sqlite3.Connection, wi: int):
    for tabela in RELACJE:
        conn.execute(f"DELETE FROM {tabela} WHERE wi = ?", (wi,))


def zsynchronizuj_baze(conn: sqlite3.Connection, baza: str, strony, pelny: bool) -> dict:
    """Zapis stron jednej bazy w transakcji wołającego (bez commitu i bez FTS). Nowy = brak `id` w tabeli;
    zmieniony = inna wartość dowolnej kolumny albo (informacje) inny zbiór ID w relacjach; identyczny – pominięty.
    W trybie pełnym usuwa wiersze spoza listingu (pusty listing → bez usuwania, z ostrzeżeniem).
    Wynik: {"nowe", "zmienione", "usuniete": liczby}."""
    klucz = BAZY[baza]["klucz"]
    wynik = {"nowe": 0, "zmienione": 0, "usuniete": 0}
    widziane = set()
    for strona in strony:
        zmapowana = mapuj_strone(baza, strona)
        if zmapowana is None:
            continue
        kolumny, relacje = zmapowana
        relacje = {t: set(ids) for t, ids in relacje.items()}
        widziane.add(kolumny["id"])
        stary = wiersz_po_id(conn, baza, kolumny["id"])
        if stary == kolumny and (baza != "informacje" or relacje_informacji(conn, stary["wi"]) == relacje):
            continue
        wynik["nowe" if stary is None else "zmienione"] += 1
        if baza == "informacje":
            if stary is not None:
                usun_relacje_informacji(conn, stary["wi"])
            for tabela, ids in relacje.items():
                conn.executemany(f"INSERT OR IGNORE INTO {tabela} VALUES (?, ?)", [(kolumny["wi"], i) for i in ids])
        nazwy = list(kolumny)
        conn.execute(f"INSERT OR REPLACE INTO {baza} ({', '.join(nazwy)}) VALUES ({', '.join('?' * len(nazwy))})",
                     [kolumny[n] for n in nazwy])
    if pelny:
        nieobecne = [(i, k) for i, k in conn.execute(f"SELECT id, {klucz} FROM {baza}") if i not in widziane]
        if nieobecne and not widziane:
            ostrzez(f"{baza}: pusty listing w trybie pełnym – usuwanie pominięte (sprawdź dostęp integracji)")
            nieobecne = []
        for id_, numer in nieobecne:
            if baza == "informacje":
                usun_relacje_informacji(conn, numer)
            if baza == "tematy":
                conn.execute("DELETE FROM informacje_tematy WHERE temat_id = ?", (id_,))
            conn.execute(f"DELETE FROM {baza} WHERE id = ?", (id_,))
        wynik["usuniete"] = len(nieobecne)
    return wynik


def przebuduj_fts(conn: sqlite3.Connection, grupy: list):
    """informacje_fts od nowa (rowid = WI): tekst po normalizuj, tematy po nazwie, `slowa` z synonimów.
    Pełna przebudowa (ok. 0,2 s na 1,5 tys. informacji) zamiast śledzenia, które wiersze zmieniła zmiana tematu."""
    tematy = {}
    for wi, nazwa in conn.execute("SELECT it.wi, t.nazwa FROM informacje_tematy it JOIN tematy t "
                                  "ON t.id = it.temat_id ORDER BY t.nazwa"):
        tematy.setdefault(wi, []).append(nazwa or "")
    conn.execute("DELETE FROM informacje_fts")
    for wi, *pola in conn.execute("SELECT wi, teza, szczegoly, dla_nas FROM informacje").fetchall():
        teza, szczegoly, dla_nas = (p or "" for p in pola)
        nazwy = "; ".join(tematy.get(wi, []))
        slowa = rozwin_synonimy(" ".join((teza, nazwy, szczegoly, dla_nas)), grupy)
        conn.execute("INSERT INTO informacje_fts (rowid, teza, tematy, szczegoly, dla_nas, slowa) "
                     "VALUES (?, ?, ?, ?, ?, ?)",
                     (wi, normalizuj(teza), normalizuj(nazwy), normalizuj(szczegoly), normalizuj(dla_nas), slowa))


def sha_synonimow() -> str:
    try:
        bajty = SYNONIMY.read_bytes()
    except FileNotFoundError:
        bajty = b""
    return hashlib.sha256(bajty).hexdigest()


def zapisz_pobrane(conn: sqlite3.Connection, pobrane: dict, pelny: bool) -> dict:
    """Zapis całego poboru ({baza: strony}) w jednej krótkiej transakcji – błąd → rollback, nic nie zapisane:
    bazy w kolejności BAZY, przebudowa FTS (gdy zmienił się którykolwiek wiersz albo plik synonimów), sync_stan,
    meta.zbudowano, meta.synonimy_sha i przy pełnym meta.ostatni_pelny.
    Wynik: {"nowe", "zmienione", "usuniete": suma po bazach, "wierszy": {baza: liczba wierszy}}."""
    suma = {"nowe": 0, "zmienione": 0, "usuniete": 0, "wierszy": {}}
    teraz = teraz_iso()
    sha = sha_synonimow()
    with conn:
        for baza in BAZY:
            wynik = zsynchronizuj_baze(conn, baza, pobrane.get(baza, []), pelny)
            for licznik in ("nowe", "zmienione", "usuniete"):
                suma[licznik] += wynik[licznik]
        if suma["nowe"] + suma["zmienione"] + suma["usuniete"] or meta_bazy(conn).get("synonimy_sha") != sha:
            przebuduj_fts(conn, wczytaj_synonimy(SYNONIMY))
        for baza in BAZY:
            ostatnie, wierszy = conn.execute(f"SELECT MAX(zmieniono), COUNT(*) FROM {baza}").fetchone()
            conn.execute("INSERT OR REPLACE INTO sync_stan VALUES (?, ?, ?, ?)", (baza, ostatnie, wierszy, teraz))
            suma["wierszy"][baza] = wierszy
        meta = [("zbudowano", teraz), ("synonimy_sha", sha)] + ([("ostatni_pelny", teraz)] if pelny else [])
        conn.executemany("INSERT OR REPLACE INTO meta VALUES (?, ?)", meta)
    return suma


def linia_raportu(wynik: dict, pelny: bool, sekundy: float) -> str:
    zmiany = wynik["nowe"] + wynik["zmienione"] + wynik["usuniete"]
    opis = f"+{wynik['nowe']} nowe, ~{wynik['zmienione']} zmienione" if zmiany else "bez zmian"
    if wynik["usuniete"]:
        opis += f", −{wynik['usuniete']} usunięte"
    n, czas = wynik["wierszy"], f"{sekundy:.1f}".replace(".", ",")
    return (f"[wiedza] sync{' (pełny)' if pelny else ''}: {opis} · informacje {n['informacje']}, "
            f"tematy {n['tematy']}, źródła {n['zrodla']}, SP {n['sprzecznosci']} · {czas} s")


def synchronizuj(conn: sqlite3.Connection, a, token: str, start: float, termin):
    """Kroki 2–9 syncu pod blokadą: tryb, pobór do pamięci (BladPoboru, gdy się nie uda albo minie termin), jedna
    transakcja zapisu, linia raportu."""
    pelny = a.pelny or starsze_niz(meta_bazy(conn).get("ostatni_pelny"), timedelta(days=PELNY_CO_DNI))
    filtry = {}
    if not pelny:
        for baza, ostatnie in conn.execute("SELECT baza, ostatnie_zmieniono FROM sync_stan"):
            if ostatnie:
                filtry[baza] = (na_czas(ostatnie) - timedelta(minutes=ZAPAS_MIN)).isoformat()
    wynik = zapisz_pobrane(conn, pobierz(token, filtry, termin), pelny)
    if not a.cicho or wynik["nowe"] + wynik["zmienione"] + wynik["usuniete"]:
        print(linia_raportu(wynik, pelny, time.monotonic() - start))


def w_worktree() -> bool:
    """Kopia repo w .claude/worktrees/… (sesja równoległa): sync i publikuj nic nie robią także wtedy, gdy DOM_HUB
    wskazuje prawdziwy hub – niedokończony kod nie może przebudować indeksu ani trafić do czatu."""
    return REPO.parent.name == "worktrees" and REPO.parent.parent.name == ".claude"


def sciezka_bazy(a) -> Path:
    return Path(a.db) if a.db else DB_DOMYSLNA


@contextlib.contextmanager
def prywatne_pliki():
    """Pliki i katalogi tworzone przez sync i publikuj (indeks, blokada, kopia do wysyłki) tylko dla właściciela –
    indeks zawiera dane osób trzecich. Maska wraca po poleceniu (ważne, gdy moduł jest importowany)."""
    stara = os.umask(0o077)
    try:
        yield
    finally:
        os.umask(stara)


def przygotuj_katalog(sciezka: Path) -> bool:
    """Katalog pliku bazy: domyślny zakłada (700, .dom już istnieje), inny musi istnieć – --db nie tworzy katalogów."""
    if sciezka == DB_DOMYSLNA:
        KATALOG.mkdir(mode=0o700, exist_ok=True)
        return True
    if sciezka.parent.is_dir():
        return True
    blad(f"--db: katalog {sciezka.parent} nie istnieje – nic nie utworzono")
    return False


def zaostrz_uprawnienia(sciezka: Path):
    """Indeks domyślny: katalog 700, pliki w nim (baza, blokada, kopie) 600 – także utworzone wcześniej z inną maską
    albo przeniesione z kopii. Bez zmiany, gdy już tak jest; katalogów i plików spoza domyślnej ścieżki (--db)
    nie dotyka. To higiena, nie warunek syncu: błąd (np. plik innego właściciela) daje ostrzeżenie i idziemy dalej."""
    if sciezka != DB_DOMYSLNA:
        return
    try:
        pliki = [p for p in KATALOG.iterdir() if p.is_file() and not p.is_symlink()]
    except OSError:
        ostrzez(f"{KATALOG.name}: nie da się odczytać listy plików – uprawnienia sprawdź ręcznie")
        pliki = []
    for p, tryb in [(KATALOG, 0o700)] + [(p, 0o600) for p in pliki]:
        try:
            if p.stat().st_mode & 0o777 != tryb:
                os.chmod(p, tryb)
        except OSError:
            ostrzez(f"{p.name}: nie da się ustawić uprawnień {tryb:o} – ustaw ręcznie")


def otworz_do_zapisu(sciezka: Path) -> sqlite3.Connection:
    """otworz_db do zapisu; uszkodzony indeks domyślny odkłada na bok jako `<plik>.uszkodzony-RRRRMMDD-GGMMSS`
    (zostają 2 najnowsze) i zakłada pusty – następny pobór jest pełny, bo Notion jest źródłem prawdy. Plik spoza
    domyślnej ścieżki (--db) nie jest przenoszony: wyjątek idzie dalej."""
    try:
        return otworz_db(sciezka, zapis=True)
    except sqlite3.DatabaseError as e:
        if not uszkodzony(e) or sciezka != DB_DOMYSLNA:
            raise
    odlozony = sciezka.with_name(f"{sciezka.name}.uszkodzony-{datetime.now():%Y%m%d-%H%M%S}")
    sciezka.replace(odlozony)
    with contextlib.suppress(FileNotFoundError):  # gorący dziennik należy do starego pliku
        sciezka.with_name(sciezka.name + "-journal").unlink()
    for stary in sorted(sciezka.parent.glob(sciezka.name + ".uszkodzony-*"))[:-2]:
        stary.unlink()
    print(f"[wiedza] indeks uszkodzony – odłożony jako {odlozony.name}, budowa od nowa pełnym sync")
    return otworz_db(sciezka, zapis=True)


def zglos_wyjatek(e: BaseException, przedrostek: str = "", cicho: bool = False):
    """Nieoczekiwany wyjątek: tylko typ i linia, bo treść i traceback mogą nieść wartości pól. Pełny traceback na
    stderr tylko z WIEDZA_DEBUG=1 przy ręcznym uruchomieniu: bez --cicho i ze stderr w terminalu – zmienna
    wyeksportowana na stałe nie może wpuścić wartości pól do wyjścia hooka."""
    blad(f"{przedrostek}{type(e).__name__} (linia {linia_bledu(e)})")
    if os.environ.get("WIEDZA_DEBUG") == "1" and not cicho and sys.stderr.isatty():
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)


def licz_odciski(conn: sqlite3.Connection, sciezka: Path, cicho: bool, termin):
    """Hak syncu po publikacji: odciski nowych i zmienionych informacji i listy podobnych (tools/wiedza_sens.py,
    Ollama na Macu). Po, nie przed: wysyłka indeksu (ok. 13 MB) zajmuje prawie cały BUDZET_CICHO, więc każda sekunda
    przed nią odkładałaby kopię dla czatu; zmienione listy (meta.podobne_policzone w hashu) wysyła następna
    publikacja. Brak modułu albo źródło niedostępne (Ollama nie działa) → nic, także bez --cicho; inny błąd – jedna
    linia, sync i tak kończy się sukcesem. Pod --cicho najwyżej BUDZET_SENS_CICHO s i nie po terminie (niepoliczone
    – na następny sync), bez linii raportu. Pierwsze pełne liczenie (kilka minut): `wiedza_sens.py przelicz` albo
    sync bez --cicho."""
    try:
        import wiedza_sens
    except ImportError:
        return
    koniec = None
    if cicho:
        koniec = time.monotonic() + BUDZET_SENS_CICHO
        if termin is not None:
            koniec = min(koniec, termin)
    try:
        linia = wiedza_sens.po_sync(conn, sciezka, CONF, koniec)
    except wiedza_sens.Niedostepny:
        return
    except Exception as e:  # noqa: BLE001 – odciski są dodatkiem, sync już zapisał dane
        zglos_wyjatek(e, "odciski: ", cicho)
        return
    if linia and not cicho:
        print(linia)


def cmd_sync(a) -> int:
    """Kody: 0 przy sukcesie i warunkach miękkich (worktree, brak .dom, tokena, sieci, zajęta blokada, limit czasu,
    Notion 5xx/429); błąd twardy (HTTP 4xx, mapowanie, baza, obcy plik --db) → 1, a z --cicho 0 (hook i nocne
    skrypty). Pod --cicho termin BUDZET_CICHO od startu obejmuje pobór i publikację."""
    start = time.monotonic()
    termin = start + BUDZET_CICHO if a.cicho else None
    if w_worktree():
        if not a.cicho:
            print("[wiedza] uruchomiono z worktree – sync pominięty, nic nie utworzono")
        return 0
    if not CONF.is_dir():
        print("[wiedza] brak katalogu .dom w hubie (np. worktree) – sync pominięty, nic nie utworzono")
        return 0
    sekrety = wczytaj_sekrety(SEKRETY)
    token = sekrety.get("NOTION_TOKEN")
    if not token:
        print(f"[wiedza] brak NOTION_TOKEN w .dom/{SEKRETY.name} – sync pominięty")
        return 0
    twardy = 0 if a.cicho else 1
    sciezka = sciezka_bazy(a)
    with prywatne_pliki():
        if not przygotuj_katalog(sciezka):
            return twardy
        with blokada(sciezka) as wzieta:
            if not wzieta:
                if not a.cicho:
                    print("[wiedza] trwa inny sync albo publikacja – sync pominięty")
                return 0
            conn = None
            try:
                conn = otworz_do_zapisu(sciezka)
                zaostrz_uprawnienia(sciezka)
                synchronizuj(conn, a, token, start, termin)
                if a.publikuj:
                    # pod blokadą tego syncu; błąd publikacji nie zmienia kodu wyjścia sync
                    try:
                        opublikuj(conn, sciezka, sekrety, cicho=a.cicho, termin=termin)
                    except Exception as e:  # noqa: BLE001 – treść wyjątku może nieść wartości pól
                        zglos_wyjatek(e, "publikacja: ", a.cicho)
                licz_odciski(conn, sciezka, a.cicho, termin)
                return 0
            except BladPoboru as e:
                przyczyna = tekst_bledu(e.przyczyna, sekrety)
                if isinstance(e.przyczyna, BladSieci):
                    if str(e.przyczyna) == LIMIT_CZASU or (termin is not None and time.monotonic() >= termin):
                        print(f"[wiedza] sync nie zmieścił się w limicie czasu startu ({BUDZET_CICHO} s, {e.baza}) – "
                              "nic nie zapisano")
                    else:
                        print(f"[wiedza] brak połączenia z Notion ({przyczyna}) – sync pominięty, nic nie zapisano")
                    return 0
                if e.przyczyna.status == 429 or e.przyczyna.status >= 500:
                    print(f"[wiedza] Notion niedostępny ({e.baza}: {przyczyna}) – sync pominięty, nic nie zapisano")
                    return 0
                print("[wiedza] sync przerwany – nic nie zapisano")
                blad(f"Notion, {e.baza}: {przyczyna}")
                return twardy
            except (BladIndeksu, BladMapowania) as e:
                print("[wiedza] sync przerwany – nic nie zapisano")
                blad(str(e))
                return twardy
            except sqlite3.DatabaseError as e:
                print("[wiedza] sync przerwany – nic nie zapisano")
                if uszkodzony(e):
                    blad(f"{sciezka.name}: plik nie jest bazą SQLite albo jest uszkodzony – nie nadpisuję go")
                else:
                    zglos_wyjatek(e, "plik indeksu: ", a.cicho)
                return twardy
            finally:
                if conn is not None:
                    conn.close()


README = """# Indeks Bazy wiedzy – kopia tylko do odczytu

Stan: {stan} · {informacji} informacji. Pliki publikuje `wiedza.py publikuj` z komputera inwestora; źródłem prawdy
jest Notion, a każda publikacja nadpisuje te pliki – nie edytuj ich tutaj.

Czat: `<GITHUB_REPO>` i `<TOKEN>` (token tylko do odczytu) wstaw ze strony „🔑 Asystent – dostęp” w Notion.

    curl -sf -H "Authorization: Bearer <TOKEN>" -H "Accept: application/vnd.github.raw" \\
      -o /tmp/wiedza.sqlite https://api.github.com/repos/<GITHUB_REPO>/contents/wiedza.sqlite
    curl -sf -H "Authorization: Bearer <TOKEN>" -H "Accept: application/vnd.github.raw" \\
      -o /tmp/wiedza.py https://api.github.com/repos/<GITHUB_REPO>/contents/wiedza.py
    python3 /tmp/wiedza.py szukaj "ZAPYTANIE" --db /tmp/wiedza.sqlite [--etap "Stan zero"] [--limit 12]
    python3 /tmp/wiedza.py temat "NAZWA" --db /tmp/wiedza.sqlite
    python3 /tmp/wiedza.py stan --db /tmp/wiedza.sqlite

Karty wiedzy (gotowe zbiory tez na typowe pytania): `karty --do "PYTANIE"` wskazuje pasujące karty, a `karta KOD
--pytanie "PYTANIE" --czesc 1` czyta kartę w częściach; kopia bez kart odpowiada „brak” – wtedy szukaj / temat / etap.
"""


def plik_kopii(sciezka: Path) -> Path:
    """Kopia do wysłania obok pliku bazy; stała nazwa wystarcza, bo publikacja działa pod blokadą."""
    return sciezka.with_name(f"{sciezka.stem}.publikacja.sqlite")


def usun_plik(plik: Path):
    for p in (plik, plik.with_name(plik.name + "-journal")):
        with contextlib.suppress(FileNotFoundError):
            p.unlink()


def limit_wysylki(bajty_base64: int) -> float:
    """Czas na wysyłkę pliku: 20 s + 5 s na MB base64 (łącze ok. 1,5 Mbit/s). To także zachowawcza miara, czy
    wysyłka zmieści się w reszcie terminu: w Pythonie 3.9 limit gniazda SSL dotyczy każdego kawałka osobno,
    więc sam nie ogranicza czasu całej wysyłki."""
    return 20 + 5 * bajty_base64 / MB


def rozmiar_opis(bajty: int) -> str:
    if bajty >= MB:
        return f"{bajty / MB:.1f} MB".replace(".", ",")
    return f"{max(1, round(bajty / 1024))} KB"


def galaz_prywatnego_repo(repo: str, naglowki: dict, termin):
    """Gałąź domyślna repo z GET /repos; None, gdy repo nie jest prywatne – wtedy nic nie wysyłamy."""
    dane = zadanie_http("GET", f"{GITHUB_API}/repos/{repo}", naglowki, termin=termin)
    # repo `internal` (GitHub Enterprise) też ma private true – widzi je cała organizacja
    if dane.get("private") is not True or dane.get("visibility", "private") != "private":
        return None
    return dane.get("default_branch") or "main"


def sha_na_githubie(repo: str, naglowki: dict, nazwa: str, termin):
    """`sha` pliku z GET Contents API (pliki ponad 1 MB przychodzą bez treści, z `sha`); 404 → None (nowy plik)."""
    try:
        return zadanie_http("GET", f"{GITHUB_API}/repos/{repo}/contents/{nazwa}", naglowki, termin=termin).get("sha")
    except BladHttp as e:
        if e.status == 404:
            return None
        raise


def wyslij_plik(repo: str, naglowki: dict, nazwa: str, tresc: str, sha_lokalny: str, sha_zdalny,
                wiadomosc: str, termin) -> bool:
    """PUT Contents API (gałąź domyślna). Konflikt sha (409/422) → ponowne GET i jedna powtórka, drugi konflikt →
    False z komunikatem. Zdalny sha równy lokalnemu po konflikcie = sukces: wcześniejszy PUT doszedł, a zgubiła
    się tylko odpowiedź."""
    url = f"{GITHUB_API}/repos/{repo}/contents/{nazwa}"
    cialo = {"message": wiadomosc, "content": tresc}
    for proba in (1, 2):
        cialo.pop("sha", None)
        if sha_zdalny:
            cialo["sha"] = sha_zdalny
        try:
            zadanie_http("PUT", url, naglowki, cialo, timeout=limit_wysylki(len(tresc)), termin=termin)
            return True
        except BladHttp as e:
            if e.status not in (409, 422):
                raise
            if proba == 2:
                ostrzez(f"{nazwa}: konflikt sha na GitHubie po powtórce – pominięty, wyśle go następna publikacja")
                return False
        sha_zdalny = sha_na_githubie(repo, naglowki, nazwa, termin)
        if sha_zdalny == sha_lokalny:
            return True
    return False


def resetuj_historie(repo: str, naglowki: dict, zakodowane: dict, wiadomosc: str, galaz: str):
    """Historia repo od nowa (publikuj --reset): blob każdego z czterech plików, drzewo z dokładnie nimi (bez
    base_tree – drzewo z samym indeksem usunęłoby kod potrzebny czatowi), commit bez rodzica, wymuszone
    przestawienie gałęzi domyślnej. Błąd w środku niczego nie zmienia – gałąź przestawia dopiero ostatnie żądanie.
    GitHub odzyskuje miejsce z opóźnieniem."""
    git = f"{GITHUB_API}/repos/{repo}/git"
    wpisy = []
    for nazwa, tresc in zakodowane.items():
        blob = zadanie_http("POST", f"{git}/blobs", naglowki, {"content": tresc, "encoding": "base64"},
                            timeout=limit_wysylki(len(tresc)))
        wpisy.append({"path": nazwa, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    drzewo = zadanie_http("POST", f"{git}/trees", naglowki, {"tree": wpisy})["sha"]
    commit = zadanie_http("POST", f"{git}/commits", naglowki,
                          {"message": wiadomosc + " (reset historii)", "tree": drzewo, "parents": []})["sha"]
    zadanie_http("PATCH", f"{git}/refs/heads/{galaz}", naglowki, {"sha": commit, "force": True})


def zapisz_meta_kopii(kopia: Path, wartosci: dict) -> bytes:
    """Dane publikacji w kopii przed wysłaniem – opublikowany plik niesie własną datę i hash, więc `stan` w czacie
    pokazuje prawdę o kopii; meta jest poza hashem."""
    c = sqlite3.connect(str(kopia))
    try:
        c.execute("PRAGMA journal_mode = DELETE")
        with c:
            c.executemany("INSERT OR REPLACE INTO meta VALUES (?, ?)", list(wartosci.items()))
    finally:
        c.close()
    return kopia.read_bytes()


def opublikuj(conn: sqlite3.Connection, sciezka: Path, sekrety: dict, teraz: bool = False, wymus: bool = False,
              reset: bool = False, cicho: bool = False, termin=None) -> bool:
    """Kopia indeksu, wiedza.py, synonimów i README do prywatnego repo GITHUB_REPO, pod blokadą wołającego
    (cmd_publikuj albo cmd_sync). Najpierw GET /repos: repo nieprywatne → nic nie wysyła. Plik indeksu (z README)
    przy zmianie hash_danych, najwyżej raz na PUBLIKACJA_CO_MIN (teraz, wymus, reset i zmiana schematu omijają
    odstęp; wymus i reset wysyłają go także bez zmiany danych); kod i synonimy po porównaniu sha z GitHubem.
    reset: jeden commit bez rodzica z czterema plikami zamiast PUT-ów. termin – jak w zadanie_http (sync --cicho):
    plik, którego wysyłka nie mieści się w reszcie czasu, czeka na następną publikację.
    Wynik False = błąd (publikuj → kod 1)."""
    start = time.monotonic()
    token, repo = sekrety.get("GITHUB_TOKEN_SYNC"), sekrety.get("GITHUB_REPO")
    if not token or not repo:
        print(f"[wiedza] brak GITHUB_TOKEN_SYNC albo GITHUB_REPO w .dom/{SEKRETY.name} – publikacja pominięta")
        return False
    if not WZORZEC_REPO.fullmatch(repo):
        blad("GITHUB_REPO: oczekiwany format właściciel/repo – publikacja pominięta")
        return False
    informacji = conn.execute("SELECT COUNT(*) FROM informacje").fetchone()[0]
    if not informacji:
        print("[wiedza] indeks bez informacji – publikacja pominięta (uruchom sync)")
        return False
    ukryj = repo.split("/")  # komunikaty GitHuba bywają z nazwą konta albo repo
    naglowki = {"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": GITHUB_WERSJA}
    kopia = plik_kopii(sciezka)
    usun_plik(kopia)  # zostaje po przerwanej publikacji
    pliki, wartosci, wyslane, odlozone, ok = {}, {}, [], [], True  # pliki: nazwa → bajty w kolejności wysyłki
    try:
        galaz = galaz_prywatnego_repo(repo, naglowki, termin)
        if galaz is None:
            blad("GITHUB_REPO wskazuje repo, które nie jest prywatne – publikacja wstrzymana "
                 "(indeks zawiera dane osób trzecich)")
            return False
        meta = meta_bazy(conn)
        h = hash_danych(conn)
        schemat = str(conn.execute("PRAGMA user_version").fetchone()[0])
        nowy_schemat = meta.get("opublikowano_schemat") != schemat
        indeks_zmieniony = h != meta.get("opublikowano_sha")
        odlozony = (indeks_zmieniony and not (teraz or wymus or reset or nowy_schemat)
                    and not starsze_niz(meta.get("opublikowano_kiedy"), timedelta(minutes=PUBLIKACJA_CO_MIN)))
        z_indeksem = wymus or reset or (indeks_zmieniony and not odlozony)
        kod = {"wiedza.py": Path(__file__).read_bytes()}
        if SYNONIMY.is_file():
            kod["wiedza_synonimy.txt"] = SYNONIMY.read_bytes()
        zdalne = {} if reset else {n: sha_na_githubie(repo, naglowki, n, termin) for n in kod}
        do_wyslania = list(kod) if reset else [n for n in kod if zdalne[n] != git_blob_sha(kod[n])]
        if not z_indeksem and not do_wyslania:
            if not cicho:
                powod = "kopia aktualna"
                if odlozony:
                    nastepna = na_czas(meta["opublikowano_kiedy"]) + timedelta(minutes=PUBLIKACJA_CO_MIN)
                    powod = (f"indeks odłożony do {lokalnie(nastepna.isoformat())} (raz na {PUBLIKACJA_CO_MIN} min;"
                             f" --teraz wysyła od razu)")
                print(f"[wiedza] publikacja: wysłano 0 – {powod}")
            return True
        kiedy = teraz_iso()
        if z_indeksem and termin is not None:
            # przed VACUUM INTO: kopia nie jest większa niż plik bazy, base64 to ok. +1/3
            bajty = conn.execute("PRAGMA page_count").fetchone()[0] * conn.execute("PRAGMA page_size").fetchone()[0]
            if time.monotonic() + limit_wysylki(bajty * 4 // 3) > termin:
                odlozone.append("wiedza.sqlite")
                z_indeksem = False
        if z_indeksem:
            if not reset:
                for n in ("wiedza.sqlite", "README.md"):
                    zdalne[n] = sha_na_githubie(repo, naglowki, n, termin)
            conn.execute("VACUUM INTO ?", (str(kopia),))
            wartosci = {"opublikowano_kiedy": kiedy, "opublikowano_sha": h, "opublikowano_schemat": schemat,
                        "publikacje_liczba": str(int(meta.get("publikacje_liczba") or 0) + 1)}
            pliki["wiedza.sqlite"] = zapisz_meta_kopii(kopia, wartosci)
            pliki["README.md"] = README.format(stan=lokalnie(meta.get("zbudowano")),
                                               informacji=informacji).encode("utf-8")
        for n in do_wyslania:
            pliki[n] = kod[n]
        zakodowane = {n: base64.b64encode(b).decode("ascii") for n, b in pliki.items()}
        za_duze = [n for n, t in zakodowane.items() if len(t) > LIMIT_PLIKU_MB * MB]
        if za_duze:
            blad(f"{', '.join(za_duze)}: ponad {LIMIT_PLIKU_MB} MB po base64 – publikacja pominięta")
            return False
        wiadomosc = f"indeks {lokalnie(kiedy)} · {informacji} inf."
        if reset:
            resetuj_historie(repo, naglowki, zakodowane, wiadomosc, galaz)
            wyslane = list(pliki)
        else:
            for nazwa, tresc in zakodowane.items():
                if nazwa == "README.md" and "wiedza.sqlite" not in wyslane:
                    continue  # README opisuje plik indeksu – idzie tylko razem z nim
                if nazwa == "wiedza.py" and nowy_schemat and indeks_zmieniony and "wiedza.sqlite" not in wyslane:
                    # nowy kod w czacie odrzuciłby zdalny plik indeksu w starym schemacie
                    ostrzez("wiedza.py wstrzymany – nowy schemat, a plik indeksu nie został wysłany")
                    continue
                if termin is not None and time.monotonic() + limit_wysylki(len(tresc)) > termin:
                    odlozone.append(nazwa)
                    continue
                try:
                    if wyslij_plik(repo, naglowki, nazwa, tresc, git_blob_sha(pliki[nazwa]), zdalne.get(nazwa),
                                   wiadomosc, termin):
                        wyslane.append(nazwa)
                    else:
                        ok = False
                except (BladHttp, BladSieci) as e:
                    blad(f"GitHub, {nazwa}: {tekst_bledu(e, sekrety, ukryj)}")
                    ok = False
        if wyslane:
            zapis = dict(wartosci) if "wiedza.sqlite" in wyslane else {}
            historia = 0 if reset else float(meta.get("historia_mb") or 0) * MB  # surowe bajty od ostatniego resetu
            zapis["historia_mb"] = f"{(historia + sum(len(pliki[n]) for n in wyslane)) / MB:.2f}"
            with conn:
                conn.executemany("INSERT OR REPLACE INTO meta VALUES (?, ?)", list(zapis.items()))
    except (BladHttp, BladSieci) as e:
        blad(f"GitHub: {tekst_bledu(e, sekrety, ukryj)} – publikacja przerwana, lokalne dane publikacji bez zmian")
        return False
    finally:
        usun_plik(kopia)
    if odlozone:
        print(f"[wiedza] publikacja: {', '.join(odlozone)} odłożone – wysyłka nie mieści się w limicie czasu startu "
              "(zrobi ją następny sync --publikuj albo publikuj)")
    if wyslane or not cicho:
        opis = ", ".join(f"{n} {rozmiar_opis(len(pliki[n]))}" for n in wyslane)
        czas = f"{time.monotonic() - start:.1f}".replace(".", ",")
        print(f"[wiedza] publikacja{' (reset historii)' if reset else ''}: wysłano {len(wyslane)}"
              + (f" – {opis}" if opis else "") + f" · {czas} s")
    return ok


def cmd_publikuj(a) -> int:
    """Samodzielna publikacja pod własną blokadą. Kody: 0 – wysłano albo nie było czego, zajęta blokada;
    1 – worktree, brak .dom, tokena albo repo, repo nieprywatne, brak lub inny schemat pliku indeksu, błąd wysyłki."""
    if w_worktree():
        print("[wiedza] uruchomiono z worktree – publikacja pominięta, nic nie utworzono")
        return 1
    if not CONF.is_dir():
        print("[wiedza] brak katalogu .dom w hubie (np. worktree) – publikacja pominięta, nic nie utworzono")
        return 1
    sekrety = wczytaj_sekrety(SEKRETY)
    sciezka = sciezka_bazy(a)
    # tylko odczyt: zapis przy innej wersji schematu skasowałby tabele, a brak pliku by go utworzył
    otworz_db(sciezka, zapis=False).close()
    with prywatne_pliki(), blokada(sciezka) as wzieta:
        if not wzieta:
            if not a.cicho:
                print("[wiedza] trwa sync albo inna publikacja – publikacja pominięta")
            return 0
        zaostrz_uprawnienia(sciezka)
        with contextlib.closing(sqlite3.connect(str(sciezka), timeout=5)) as conn:
            return 0 if opublikuj(conn, sciezka, sekrety, teraz=a.teraz, wymus=a.wymus, reset=a.reset,
                                  cicho=a.cicho) else 1


# Polecenia odczytu: sam plik indeksu (tryb ro) – bez sekretów, sieci, synonimów, blokady i bez dotykania huba
# przy --db. Wartości pól drukuje wyłącznie właściwy wynik polecenia.
OTWARTE_SP = ("czeka na decyzję", "do sprawdzenia u projektanta")  # Status Rejestru po normalizuj
FILTRY_SZUKAJ = ("etap", "istotnosc", "status", "rodzaj")
# duplikaty: słowa funkcyjne (≥ 5 liter, po bez_diakrytykow), które nie świadczą o podobieństwie tez
STOP_SLOWA = frozenset("""ktory ktora ktore ktorej ktorego ktorych ktorym ktorymi przez przed miedzy ponad okolo
takze rowniez jednak tylko bardzo wtedy zawsze gdzie kiedy nalezy trzeba jesli jezeli wiecej mniej czyli sobie
nawet dlatego powinien powinna powinno zamiast""".split())
# duplikaty: token obecny w więcej niż max(CZESTOSC_MIN, CZESTOSC_UDZIAL × liczba tez) tezach jest pospolity
# (przy 1,5 tys. informacji: ponad 0,08 × 1500 = 120 tez). Kandydatów na parę szuka SONDA_RZADKIE najrzadszych
# niepospolitych tokenów tezy (krótkie listy), a teza z mniej niż 3 takimi – SONDA_POSPOLITE najrzadszych w ogóle;
# wspólne tokeny liczone na pełnych zbiorach. Kandydat, którego sama długość wyklucza próg (górna granica ratio:
# 2·min(la, lb) / (la + lb)), odpada; SequenceMatcher (drogi) dostaje najwyżej KANDYDACI_NA_TEZE pozostałych
# z największą liczbą wspólnych tokenów, a przy remisie najbliższych długością – dłuższe tezy zawierające wszystkie
# tokeny krótkiej nie wypchną jej bliskiej kopii.
CZESTOSC_MIN = 50
CZESTOSC_UDZIAL = 0.08
DUPLIKATY_PROG_SLOWA = 0.82
# Po znaczeniu: kalibracja 26.10.2026 na parach ocenionych przez sędziego Z6 – podobieństwo nie odróżnia duplikatu
# od informacji bliskiej tematem (przy każdym progu ok. 1 na 10 par to duplikat), więc to lista kandydatów do decyzji;
# próg trzyma ją krótką (ok. 50 par w całej bazie)
DUPLIKATY_PROG_SENS = 0.84
SONDA_RZADKIE = 8
SONDA_POSPOLITE = 2
KANDYDACI_NA_TEZE = 5


def otworz_do_odczytu(a) -> sqlite3.Connection:
    return otworz_db(sciezka_bazy(a), zapis=False)


def meta_bazy(conn: sqlite3.Connection) -> dict:
    return dict(conn.execute("SELECT klucz, wartosc FROM meta"))


def lokalnie(tekst) -> str:
    """Czas ISO z bazy (UTC) → lokalne „RRRR-MM-DD GG:MM”; brak → „–”."""
    return na_czas(tekst).astimezone().strftime("%Y-%m-%d %H:%M") if tekst else "–"


def jedna_linia(tekst) -> str:
    """Wartość do linii wyniku: bez złamań wiersza (rich_text bywa wielowierszowy); pusta → „–”."""
    return " ".join((tekst or "").split()) or "–"


def skroc(tekst, n: int) -> str:
    tekst = jedna_linia(tekst)
    return tekst if len(tekst) <= n else tekst[:n - 1] + "…"


def wypisz_json(obiekt):
    print(json.dumps(obiekt, ensure_ascii=False))


def opisz_informacje(conn: sqlite3.Connection, numery) -> list:
    """Informacje w kształcie wyniku JSON, w kolejności `numery`; puste pola → "", relacje do stron spoza indeksu
    (np. usuniętego źródła) pominięte. Tekst linii powstaje z tych samych słowników (linia_informacji)."""
    tematy = dict(conn.execute("SELECT id, nazwa FROM tematy"))
    zrodla = {r[0]: r[1:] for r in conn.execute("SELECT id, zrd, tytul, kto, typ_autora, wiarygodnosc FROM zrodla")}
    numery_sp = dict(conn.execute("SELECT id, sp FROM sprzecznosci"))
    wyniki = []
    for wi in numery:
        istotnosc, etap, status, teza, komentarz, url = (x or "" for x in conn.execute(
            "SELECT istotnosc, etap, status, teza, moj_komentarz, notion_url FROM informacje WHERE wi = ?",
            (wi,)).fetchone())
        rel = relacje_informacji(conn, wi)
        zr = sorted((zrodla[i] for i in rel["informacje_zrodla"] if i in zrodla), key=lambda z: z[0])
        wyniki.append({
            "wi": wi, "istotnosc": istotnosc, "etap": etap, "status": status, "teza": teza,
            "tematy": sorted(tematy[i] or "" for i in rel["informacje_tematy"] if i in tematy),
            "zrodla": [{"zrd": n, "tytul": t or "", "kto": k or "", "typ_autora": ta or "", "wiarygodnosc": w or ""}
                       for n, t, k, ta, w in zr],
            "sp": sorted(numery_sp[i] for i in rel["informacje_sp"] if i in numery_sp),
            "notatnik": bool(rel["informacje_notatnik"]), "komentarz": komentarz, "notion_url": url})
    return wyniki


def linia_informacji(w: dict) -> str:
    """Linia wyniku dla agenta; „Kto” każdego źródła obowiązkowe (ten sam autor to nie potwierdzenie)."""
    zrodla = ", ".join(f"ZRD-{z['zrd']} „{skroc(z['tytul'], 60)}” (Kto: {jedna_linia(z['kto'])}; "
                       f"{jedna_linia(z['typ_autora'])}; {jedna_linia(z['wiarygodnosc'])})" for z in w["zrodla"])
    czesci = [f"WI-{w['wi']}", jedna_linia(w["istotnosc"]), jedna_linia(w["etap"]), jedna_linia(w["status"]),
              jedna_linia(w["teza"]), "T: " + ("; ".join(jedna_linia(t) for t in w["tematy"]) or "–"),
              zrodla or "ZRD: – (Kto: –)"]
    if w["notatnik"]:
        czesci.append("ustalenie w Notatniku")
    if w["sp"]:
        czesci.append(", ".join(f"SP-{n}" for n in w["sp"]))
    czesci.append(w["notion_url"] or "–")
    linia = " · ".join(czesci)
    if w["komentarz"].strip():
        linia += " · 💬 komentarz inwestora: " + jedna_linia(w["komentarz"])
    return linia


def skrot_listy(elementy: list, n: int) -> str:
    return "; ".join(elementy[:n]) + (f" +{len(elementy) - n}" if len(elementy) > n else "")


def linia_krotka(w: dict, znacznik: str = "") -> str:
    """Linia --krotko dla czatu: teza skrócona, bez tytułów źródeł, „Kto”, komentarza i linku (są w `temat`
    i w Notion). Status tylko inny niż „Nowe”; SP-n, „źr: Notatnik” i sam znak 💬 zostają – na nich opierają się
    reguły procedury `wiedza` (sprzeczności, ustalenia, komentarz inwestora)."""
    zrodla = [f"ZRD-{z['zrd']} {jedna_linia(TYP_AUTORA_KONIEC.split(z['typ_autora'])[0])}/"
              f"{jedna_linia(z['wiarygodnosc'][:1])}" for z in w["zrodla"]]
    if w["notatnik"]:
        zrodla.append("Notatnik")
    czesci = [f"WI-{w['wi']}" + (f" {znacznik}" if znacznik else ""), jedna_linia(w["istotnosc"]),
              jedna_linia(w["etap"])]
    if normalizuj(w["status"]) not in ("", "nowe"):
        czesci.append(jedna_linia(w["status"]))
    czesci += [skroc(w["teza"], KROTKO_TEZA),
               "T: " + (skrot_listy([skroc(t, KROTKO_TEMAT) for t in w["tematy"]], KROTKO_TEMATOW) or "–"),
               "źr: " + (skrot_listy(zrodla, KROTKO_ZRODEL) or "–")]
    if w["sp"]:
        czesci.append(", ".join(f"SP-{n}" for n in w["sp"]))
    if w["komentarz"].strip():
        czesci.append("💬")
    return " · ".join(czesci)


def otwarte_sp(conn: sqlite3.Connection, numery: set) -> list:
    """Sprzeczności z `numery` o Statusie „Czeka na decyzję” albo „Do sprawdzenia u projektanta”, rosnąco."""
    return [{"sp": sp, "status": status or "", "dylemat": dylemat or "", "notion_url": url or ""}
            for sp, status, dylemat, url in conn.execute(
                "SELECT sp, status, dylemat, notion_url FROM sprzecznosci ORDER BY sp")
            if sp in numery and normalizuj(status) in OTWARTE_SP]


def otwarte_sp_trafien(conn: sqlite3.Connection, trafienia: list, wyniki: list) -> list:
    """Otwarte SP wszystkich trafień, nie tylko pokazanych (--limit): najpierw z pokazanych wyników w kolejności
    pierwszego wystąpienia, potem tylko z dalszych trafień rosnąco; w_widocznych – SP niesie pokazany wynik."""
    trafienia = set(trafienia)
    otwarte = {s["sp"]: s for s in otwarte_sp(conn, {sp for wi, sp in conn.execute(
        "SELECT x.wi, s.sp FROM informacje_sp x JOIN sprzecznosci s ON s.id = x.sp_id") if wi in trafienia})}
    widoczne = list(dict.fromkeys(n for w in wyniki for n in w["sp"] if n in otwarte))
    dalsze = [n for n in otwarte if n not in widoczne]
    return ([dict(otwarte[n], w_widocznych=True) for n in widoczne]
            + [dict(otwarte[n], w_widocznych=False) for n in dalsze])


def podobne_w_indeksie(conn: sqlite3.Connection):
    """Liczba wierszy tabeli `podobne`; None, gdy jej nie ma (kopia sprzed list podobnych)."""
    if not conn.execute("SELECT 1 FROM sqlite_master WHERE name = 'podobne'").fetchone():
        return None
    return conn.execute("SELECT COUNT(*) FROM podobne").fetchone()[0]


def podobne_trafien(conn: sqlite3.Connection, pokazane: list, a) -> list:
    """[(WI, WI trafienia, podobieństwo)] – sąsiedzi PODOBNE_Z_TRAFIEN pierwszych pokazanych trafień od
    PODOBNE_PROG, bez pokazanych i bez powtórzeń, po tych samych filtrach co trafienia; najpierw sąsiedzi
    wyższego trafienia, w nim wg podobieństwa. Bez tabeli `podobne` → []."""
    if not podobne_w_indeksie(conn):
        return []
    ocen, juz, wynik = filtr_szukaj(conn, a), set(pokazane), []
    for wi in pokazane[:PODOBNE_Z_TRAFIEN]:
        for p, s in conn.execute("SELECT wi_podobne, podobienstwo FROM podobne WHERE wi = ? AND podobienstwo >= ? "
                                 "ORDER BY podobienstwo DESC, wi_podobne", (wi, PODOBNE_PROG)):
            if p not in juz and ocen(p) == "":
                juz.add(p)
                wynik.append((p, wi, s))
    return wynik[:PODOBNE_LINII]


def opisz_podobne(conn: sqlite3.Connection, podobne: list) -> list:
    """Opisy sąsiadów (opisz_informacje) z polami podobne_do i podobienstwo – do --json i linii ≈WI-n."""
    return [dict(w, podobne_do=do, podobienstwo=s)
            for w, (_, do, s) in zip(opisz_informacje(conn, [p for p, _, _ in podobne]), podobne)]


def linia_sp(s: dict, krotko: bool = False) -> str:
    if krotko:
        return f"SP-{s['sp']} · {jedna_linia(s['status'])} · {skroc(s['dylemat'], KROTKO_DYLEMAT)}"
    return f"SP-{s['sp']} · {jedna_linia(s['status'])} · {jedna_linia(s['dylemat'])} · {s['notion_url'] or '–'}"


def wi_tematow(conn: sqlite3.Connection, nazwa: str) -> set:
    """WI informacji powiązanych z tematem, którego nazwa zawiera `nazwa` (bez wielkości liter i diakrytyków)."""
    szukana = bez_diakrytykow(nazwa).strip()
    return {wi for wi, n in conn.execute(
        "SELECT it.wi, t.nazwa FROM informacje_tematy it JOIN tematy t ON t.id = it.temat_id")
            if szukana in bez_diakrytykow(n)}


def oceny_bm25(conn: sqlite3.Connection, mecz: str) -> dict:
    """{WI: bm25} trafień ciągu MATCH (wagi kolumn teza, tematy, szczegóły, dla nas, synonimy; mniej = lepiej)."""
    return dict(conn.execute("SELECT rowid, bm25(informacje_fts, 3.0, 2.0, 1.0, 1.0, 1.5) FROM informacje_fts "
                             "WHERE informacje_fts MATCH ?", (mecz,)))


def filtr_szukaj(conn: sqlite3.Connection, a):
    """Funkcja WI → None (nie przechodzi filtrów --etap/--istotnosc/--status/--rodzaj/--temat albo nie ma jej
    w indeksie), "nieaktualne" / "ciekawostki" (pomijane domyślnie; jawny filtr --status / --istotnosc albo
    --ciekawostki to wyłącza) albo "" (widoczna)."""
    pola = {wi: [normalizuj(x) for x in r] for wi, *r in conn.execute(
        f"SELECT wi, {', '.join(FILTRY_SZUKAJ)} FROM informacje")}
    filtry = {f: normalizuj(getattr(a, f)) for f in FILTRY_SZUKAJ if getattr(a, f) is not None}
    temat = wi_tematow(conn, a.temat) if a.temat is not None else None

    def ocen(wi):
        wartosci = dict(zip(FILTRY_SZUKAJ, pola.get(wi) or ()))
        if not wartosci or any(wartosci[f] != v for f, v in filtry.items()) or (temat is not None and wi not in temat):
            return None
        if wartosci["status"] == "nieaktualne" and "status" not in filtry:
            return "nieaktualne"
        if wartosci["istotnosc"] == "ciekawostka" and not (a.ciekawostki or "istotnosc" in filtry):
            return "ciekawostki"
        return ""
    return ocen


def wybierz(conn: sqlite3.Connection, mecz: str, a) -> tuple:
    """(widoczne WI wg bm25 rosnąco – najlepsze ma najmniejszą wartość, liczniki pominiętych, {WI: bm25}) dla ciągu
    MATCH, po filtrach (filtr_szukaj)."""
    ocen = filtr_szukaj(conn, a)
    oceny = oceny_bm25(conn, mecz)
    widoczne, pominieto = [], {"nieaktualne": 0, "ciekawostki": 0}
    for wi in sorted(oceny, key=lambda w: (oceny[w], w)):
        powod = ocen(wi)
        if powod:
            pominieto[powod] += 1
        elif powod is not None:
            widoczne.append(wi)
    return widoczne, pominieto, oceny


def z_premia_formy_dokladnej(conn: sqlite3.Connection, widoczne: list, oceny: dict, pelne: list) -> list:
    """Trafienia AND od nowa wg bm25 z dodanym bm25 pełnych form przyciętych słów: przycięty temat („termi*”)
    łapie też inne słowa („terminal”), więc wiersz z dokładnie tym słowem, o które pytano, idzie wyżej."""
    if not pelne or len(widoczne) < 2:
        return widoczne
    suma = {wi: oceny[wi] for wi in widoczne}
    for pelna in pelne:
        for wi, wynik in oceny_bm25(conn, pelna).items():
            if wi in suma:
                suma[wi] += wynik
    return sorted(widoczne, key=lambda wi: (suma[wi], wi))


def pokrycie(conn: sqlite3.Connection, terminy: list) -> dict:
    """{WI: ile różnych terminów zapytania zawiera wiersz} – w dowolnej kolumnie, także w synonimach `slowa`."""
    licznik = {}
    for termin in dict.fromkeys(terminy):
        for (wi,) in conn.execute("SELECT rowid FROM informacje_fts WHERE informacje_fts MATCH ?", (termin,)):
            licznik[wi] = licznik.get(wi, 0) + 1
    return licznik


def wyszukaj(conn: sqlite3.Connection, zapytanie: str, a) -> tuple:
    """(WI w kolejności wyniku, liczniki pominiętych, czy dopasowanie częściowe, liczba pełnych trafień AND).
    Mniej niż DOPELNIJ_PONIZEJ widocznych trafień AND i ≥ 2 terminy treściowe (OR inne niż AND, nie same słowa
    wypełniające) → za trafieniami AND dopisane pozostałe trafienia OR (dopasowanie częściowe od pozycji pelnych + 1),
    najpierw te z większą liczbą terminów, potem wg bm25: w samym bm25 rzadkie słowo spoza tematu („stać”) wygrywa
    z wierszami pasującymi do dwóch słów tematycznych. Liczniki pominiętych z OR, bo trafienia OR obejmują AND."""
    return wyszukaj_poziomy(conn, zapytanie, a)[:4]


def wyszukaj_poziomy(conn: sqlite3.Connection, zapytanie: str, a, odetnij: bool = False) -> tuple:
    """Jak wyszukaj, z piątym elementem: poziomy dopełnienia albo None (bez dopełnienia) – {"slow": n terminów,
    "prog": ⌈n/2⌉, "polowa": ile dopisanych wierszy ma co najmniej próg terminów, "dowolne": ile mniej,
    "odciete": czy `dowolne` odcięto}. Kolejność się nie zmienia (dopisane idą od największej liczby terminów), więc
    poziom „co najmniej ⌈n/2⌉” stoi zawsze przed „którekolwiek”. odetnij (pojedyncze zapytanie z --krotko): wiersze
    poniżej progu wypadają, gdy pełne trafienia i poziom progu razem dają co najmniej DOPELNIJ_PONIZEJ – szum
    pojedynczych słów nie zajmuje wtedy miejsca na liście ani w sekcji sprzeczności."""
    terminy, _ = terminy_zapytania(zapytanie)
    mecz, mecz_or = zbuduj_zapytanie_fts(zapytanie, "AND"), zbuduj_zapytanie_fts(zapytanie, "OR")
    widoczne, pominieto, oceny = wybierz(conn, mecz, a)
    widoczne = z_premia_formy_dokladnej(conn, widoczne, oceny, [p for _, p in terminy if p])
    czesciowe, pelnych, poziom = False, len(widoczne), None
    if len(widoczne) < DOPELNIJ_PONIZEJ and mecz_or is not None and mecz_or != mecz:
        widoczne_or, pominieto_or, _ = wybierz(conn, mecz_or, a)
        juz = set(widoczne)
        dalsze = [wi for wi in widoczne_or if wi not in juz]
        if dalsze:
            tresciowe = list(dict.fromkeys(t for t, _ in terminy if t != "OR"))
            licznik = pokrycie(conn, tresciowe)
            dalsze.sort(key=lambda wi: -licznik.get(wi, 0))  # sortowanie stabilne: przy remisie zostaje bm25
            prog = -(-len(tresciowe) // 2)
            polowa = sum(1 for wi in dalsze if licznik.get(wi, 0) >= prog)
            poziom = {"slow": len(tresciowe), "prog": prog, "polowa": polowa, "dowolne": len(dalsze) - polowa,
                      "odciete": False}
            if odetnij and poziom["dowolne"] and pelnych + polowa >= DOPELNIJ_PONIZEJ:
                dalsze, poziom["odciete"] = dalsze[:polowa], True
            widoczne, pominieto, czesciowe = widoczne + dalsze, pominieto_or, True
    return widoczne, pominieto, czesciowe, pelnych, poziom


def opis_poziomu(poziom) -> str:
    """Dopisek nagłówka po „dopasowanie częściowe od pozycji k”: ile wierszy z którego poziomu dopełnienia."""
    if not poziom:
        return ""
    czesci = []
    if poziom["prog"] > 1:
        czesci.append(f"co najmniej {poziom['prog']} z {poziom['slow']} słów – {poziom['polowa']}")
    if poziom["dowolne"] or poziom["prog"] <= 1:
        czesci.append(f"którekolwiek słowo – {poziom['dowolne']}" + (" odcięte" if poziom["odciete"] else ""))
    return ": " + ", ".join(czesci)


def zapisz_log_szukaj(a, start: float, widoczne: list, czesciowe: bool, pelnych: int, zapytanie: str = None,
                      wiele: int = 1):
    """Jeden wiersz logu zapytań (opis w nagłówku modułu); przy kilku zapytaniach – wiersz na każde, z polem
    `wiele` (ile zapytań w wywołaniu). Najlepsza próba: nic nie drukuje, nie tworzy katalogów i nie rzuca wyjątków."""
    try:
        if os.environ.get("WIEDZA_LOG") == "0" or not KATALOG.is_dir():
            return
        if sciezka_bazy(a).resolve().parent != KATALOG.resolve():
            return
        zapytanie = a.zapytanie[0] if zapytanie is None else zapytanie
        terminy, same_stop = terminy_zapytania(zapytanie)
        tryb = ("stop" if same_stop else "AND" if not czesciowe
                else "OR-only" if pelnych == 0 else "AND+dopelnienie")
        kanal = os.environ.get("WIEDZA_KANAL") or ("claude-code" if os.environ.get("CLAUDECODE") else "inny")
        filtry = {f: getattr(a, f) for f in FILTRY_SZUKAJ + ("temat",) if getattr(a, f) is not None}
        if a.ciekawostki:
            filtry["ciekawostki"] = True
        if a.limit != 12:
            filtry["limit"] = a.limit
        if a.krotko:
            filtry["krotko"] = True
        if getattr(a, "sens", False):
            filtry["sens"] = True
        rekord = {"ts": teraz_iso(), "kanal": kanal[:20], "q": zapytanie[:LOG_MAKS_ZAPYTANIE],
                  "n_terminow": sum(1 for t, _ in terminy if t != "OR"), "tryb": tryb, "trafien": len(widoczne),
                  "pelnych": pelnych, "pokazano": min(a.limit, len(widoczne)), "top5": widoczne[:5],
                  "ms": round((time.perf_counter() - start) * 1000, 1), "filtry": filtry}
        if wiele > 1:
            rekord["wiele"] = wiele
        linia = (json.dumps(rekord, ensure_ascii=False) + "\n").encode("utf-8")
        import fcntl  # leniwie, jak w blokada()
        plik = KATALOG / PLIK_LOGU
        for _ in range(3):
            # blokada na otwartym pliku: rotację robi jeden proces, a ten, który czekał na stary plik, otwiera nowy
            fd = os.open(str(plik), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX)
                stan = os.fstat(fd)
                if not plik.exists() or os.stat(str(plik)).st_ino != stan.st_ino:
                    continue
                if stan.st_size > LOG_MAKS_B:
                    os.replace(str(plik), str(KATALOG / PLIK_LOGU_STARY))
                    continue
                os.write(fd, linia)  # jeden zapis na wiersz: równoległe procesy nie przeplatają wierszy
                return
            finally:
                os.close(fd)
    except Exception:  # noqa: BLE001 – log jest dodatkiem, wynik szukaj ma być taki sam jak bez niego
        pass


def cmd_szukaj(a) -> int:
    start = time.perf_counter()
    if all(zbuduj_zapytanie_fts(q, "AND") is None for q in a.zapytanie):
        blad("puste zapytanie – podaj słowa do wyszukania")
        return 1
    if a.limit is None:
        a.limit = LIMIT_KROTKO if a.krotko else LIMIT_DOMYSLNY
    if a.limit < 1:
        blad("--limit musi być co najmniej 1")
        return 1
    if len(a.zapytanie) > 1 or a.sens:
        return szukaj_wiele(a, start)
    with contextlib.closing(otworz_do_odczytu(a)) as conn:
        widoczne, pominieto, czesciowe, pelnych, poziom = wyszukaj_poziomy(conn, a.zapytanie[0], a, odetnij=a.krotko)
        wyniki = opisz_informacje(conn, widoczne[:a.limit])
        podobne = opisz_podobne(conn, podobne_trafien(conn, widoczne[:a.limit], a)) if a.krotko else None
        sprzecznosci = otwarte_sp_trafien(conn, widoczne, wyniki)
        stan = meta_bazy(conn).get("zbudowano") or ""
        informacji = conn.execute("SELECT COUNT(*) FROM informacje").fetchone()[0]
    zapisz_log_szukaj(a, start, widoczne, czesciowe, pelnych)
    if a.json:
        wynik = {"stan": stan, "zapytanie": a.zapytanie[0], "czesciowe": czesciowe, "pelnych": pelnych,
                 "trafien": len(widoczne), "pominieto": pominieto, "wyniki": wyniki, "sprzecznosci": sprzecznosci,
                 "poziom": poziom}
        if podobne is not None:
            wynik["podobne"] = podobne
        wypisz_json(wynik)
        return 0
    pominiete = ", ".join(f"{k} {n}" for k, n in pominieto.items() if n)
    naglowek = f"# indeks: stan {lokalnie(stan)} · {informacji} informacji · zapytanie: {a.zapytanie[0]}"
    naglowek += "".join(f" · {f}: {getattr(a, f)}" for f in FILTRY_SZUKAJ + ("temat",) if getattr(a, f) is not None)
    naglowek += f" · trafień: {len(widoczne)}"
    if len(widoczne) > a.limit:
        naglowek += f" (pokazano {a.limit})"
    if czesciowe:
        naglowek += f" (dopasowanie częściowe od pozycji {pelnych + 1}{opis_poziomu(poziom)})"
    if pominiete:
        naglowek += f" (pominięto: {pominiete})"
    print(naglowek)
    wypisz_wyniki(a, wyniki, {}, sprzecznosci, pominiete, podobne)
    return 0


def wypisz_wyniki(a, wyniki: list, znaczniki: dict, sprzecznosci: list, pominiete: str, podobne=None):
    """Linie wyników (pełne albo --krotko, ze znacznikiem zapytań przy kilku), sekcja podobnych (--krotko), sekcja
    otwartych SP i stopka. --krotko: SP niesione tylko przez dalsze trafienia – same numery w jednej linii (pełne
    linie: `temat`, Notion)."""
    for w in wyniki:
        znacznik = znaczniki.get(w["wi"], "")
        if a.krotko:
            print(linia_krotka(w, znacznik))
        else:
            numer = f"WI-{w['wi']}"
            print(numer + (f" {znacznik}" if znacznik else "") + linia_informacji(w)[len(numer):])
    if podobne:
        print("## Podobne do trafień (po znaczeniu; ≈WI-n – podobna do trafienia WI-n)")
        for w in podobne:
            print(linia_krotka(w, f"≈WI-{w['podobne_do']}"))
    if sprzecznosci:
        dalsze = [s for s in sprzecznosci if not s["w_widocznych"]]
        print("## Otwarte sprzeczności w trafieniach"
              + (f" ({len(dalsze)} tylko w dalszych trafieniach)" if dalsze else ""))
        for s in sprzecznosci:
            if a.krotko and not s["w_widocznych"]:
                continue
            print(linia_sp(s, a.krotko) + ("" if s["w_widocznych"] else " · (tylko w dalszych trafieniach)"))
        if a.krotko and dalsze:
            print("tylko w dalszych trafieniach: " + ", ".join(f"SP-{s['sp']}" for s in dalsze))
    if pominiete:
        print(f"# pominięto: {pominiete} – ciekawostki pokaże --ciekawostki, nieaktualne --status Nieaktualne")


def punkty_rrf(listy: dict) -> dict:
    """{numer zapytania: [WI w kolejności]} → {WI: [suma 1 / (RRF_K + pozycja), najwyższa pozycja,
    [numery zapytań]]}."""
    punkty = {}
    for nr, lista in listy.items():
        for poz, wi in enumerate(lista, 1):
            p = punkty.setdefault(wi, [0.0, poz, []])
            p[0] += 1 / (RRF_K + poz)
            p[1] = min(p[1], poz)
            p[2].append(nr)
    return punkty


def polacz_rrf(listy: dict) -> list:
    """{numer zapytania: [WI w kolejności]} → [(WI, [numery zapytań, które go znalazły])] wg sumy 1 / (RRF_K +
    pozycja) (punkty_rrf); remis – lepsza najwyższa pozycja, potem mniejszy numer WI."""
    punkty = punkty_rrf(listy)
    return [(wi, punkty[wi][2]) for wi in sorted(punkty, key=lambda w: (-punkty[w][0], punkty[w][1], w))]


def rankingi_sens(a, zapytania: list) -> tuple:
    """szukaj --sens (tylko Mac): (rankingi po znaczeniu z tools/wiedza_sens.py albo None, dopisek do nagłówka).
    Brak modułu (czat), Ollama wyłączona, brak odcisków albo inny błąd → None i zwykłe szukanie po słowach."""
    try:
        import wiedza_sens
    except ImportError:
        return None, "sens: niedostępny (tylko na Macu) – same słowa"
    try:
        return wiedza_sens.rankingi(sciezka_bazy(a), zapytania, CONF), "sens: tak"
    except wiedza_sens.Niedostepny as e:
        return None, f"sens: niedostępny ({e}) – same słowa"
    except Exception as e:  # noqa: BLE001 – szukanie ma działać bez odcisków; treść wyjątku bez wartości pól
        return None, f"sens: błąd {type(e).__name__} – same słowa"


def szukaj_wiele(a, start: float) -> int:
    """szukaj z kilkoma zapytaniami albo z --sens: każde osobno (dopełnienie bez odcięcia), wyniki połączone bez
    duplikatów (polacz_rrf), przy linii znacznik `[1,3]` – numery zapytań (w kolejności podania), które ją znalazły
    po słowach albo po znaczeniu (--sens: druga lista RRF na zapytanie, SENS_LISTA najbliższych).
    Zapytanie bez terminów (np. samo „OR” albo znaki interpunkcji) jest pomijane z dopiskiem w nagłówku."""
    numery = [(nr, q) for nr, q in enumerate(a.zapytanie, 1) if zbuduj_zapytanie_fts(q, "AND") is not None]
    sens, opis_sens = rankingi_sens(a, [q for _, q in numery]) if a.sens else (None, "")
    with contextlib.closing(otworz_do_odczytu(a)) as conn:
        listy, opisy = {}, []
        ocen = filtr_szukaj(conn, a) if sens else None
        for i, (nr, q) in enumerate(numery):
            t0 = time.perf_counter()
            widoczne, pominieto, czesciowe, pelnych, poziom = wyszukaj_poziomy(conn, q, a)
            listy[nr] = widoczne
            opisy.append({"nr": nr, "zapytanie": q, "trafien": len(widoczne), "czesciowe": czesciowe,
                          "pelnych": pelnych, "poziom": poziom, "pominieto": pominieto})
            if sens:
                # ranking po znaczeniu jako osobna lista RRF (klucz -nr), po tych samych filtrach
                listy[-nr] = [wi for wi, _ in sens[i] if ocen(wi) == ""][:SENS_LISTA]
            zapisz_log_szukaj(a, t0, widoczne, czesciowe, pelnych, q, len(a.zapytanie))
        polaczone = [(wi, sorted(set(abs(nr) for nr in nr_list))) for wi, nr_list in polacz_rrf(listy)]
        wyniki = opisz_informacje(conn, [wi for wi, _ in polaczone[:a.limit]])
        podobne = (opisz_podobne(conn, podobne_trafien(conn, [wi for wi, _ in polaczone[:a.limit]], a))
                   if a.krotko else None)
        sprzecznosci = otwarte_sp_trafien(conn, [wi for wi, _ in polaczone], wyniki)
        stan = meta_bazy(conn).get("zbudowano") or ""
        informacji = conn.execute("SELECT COUNT(*) FROM informacje").fetchone()[0]
    znaczniki = {wi: "[" + ",".join(map(str, nr)) + "]" for wi, nr in polaczone}
    puste = [nr for nr in range(1, len(a.zapytanie) + 1) if nr not in listy]
    if a.json:
        wynik = {"stan": stan, "zapytania": opisy, "puste": puste, "trafien": len(polaczone),
                 "wyniki": [dict(w, zapytania=listy_nr) for w, (_, listy_nr) in zip(wyniki, polaczone)],
                 "sprzecznosci": sprzecznosci}
        if podobne is not None:
            wynik["podobne"] = podobne
        if a.sens:
            wynik["sens"] = opis_sens
        wypisz_json(wynik)
        return 0
    segmenty = []
    for o in opisy:
        s = f"{o['nr']}) {o['zapytanie']} – trafień {o['trafien']}"
        if o["czesciowe"]:
            s += f" (częściowe od {o['pelnych'] + 1}{opis_poziomu(o['poziom'])})"
        pom = ", ".join(f"{k} {n}" for k, n in o["pominieto"].items() if n)
        if pom:
            s += f" (pominięto: {pom})"
        segmenty.append(s)
    naglowek = f"# indeks: stan {lokalnie(stan)} · {informacji} informacji · zapytania: " + " · ".join(segmenty)
    if puste:
        naglowek += " · puste (bez słów): " + ", ".join(map(str, puste))
    naglowek += "".join(f" · {f}: {getattr(a, f)}" for f in FILTRY_SZUKAJ + ("temat",) if getattr(a, f) is not None)
    if a.sens:
        naglowek += f" · {opis_sens}"
    naglowek += f" · razem bez powtórzeń: {len(polaczone)}"
    if len(polaczone) > a.limit:
        naglowek += f" (pokazano {a.limit})"
    print(naglowek)
    wypisz_wyniki(a, wyniki, znaczniki, sprzecznosci, "", podobne)
    if any(n for o in opisy for n in o["pominieto"].values()):
        print("# pominięto (liczby przy zapytaniach) – ciekawostki pokaże --ciekawostki, nieaktualne --status Nieaktualne")
    return 0


def cmd_temat(a) -> int:
    szukana = bez_diakrytykow(a.nazwa).strip()
    if not szukana:
        blad("pusta nazwa tematu")
        return 1
    with contextlib.closing(otworz_do_odczytu(a)) as conn:
        pasujace = [t for t in conn.execute(
            "SELECT id, nazwa, stan_wiedzy, etap, w_skrocie, notion_url FROM tematy ORDER BY nazwa")
                    if szukana in bez_diakrytykow(t[1])]
        # nazwa równa zapytaniu wygrywa z dłuższymi, które ją zawierają („Drenaż” obok „Drenaż opaskowy”)
        dokladne = [t for t in pasujace if bez_diakrytykow(t[1]).strip() == szukana]
        if len(dokladne) == 1:
            pasujace = dokladne
        if len(pasujace) != 1:
            kandydaci = [{"nazwa": t[1] or "", "notion_url": t[5] or ""} for t in pasujace]
            if a.json:
                wypisz_json({"kandydaci": kandydaci})
            else:
                print(f"# temat „{a.nazwa}”: " + (f"{len(kandydaci)} pasujących – podaj dokładniejszą nazwę"
                                                  if kandydaci else "brak pasującego tematu"))
                for k in kandydaci:
                    print(f"{jedna_linia(k['nazwa'])} · {k['notion_url'] or '–'}")
            return 0
        id_, nazwa, stan_wiedzy, etap, w_skrocie, url = (x or "" for x in pasujace[0])
        aktualne = [(wi, normalizuj(ist), normalizuj(st)) for wi, ist, st in conn.execute(
            "SELECT i.wi, i.istotnosc, i.status FROM informacje i JOIN informacje_tematy it ON it.wi = i.wi "
            "WHERE it.temat_id = ? ORDER BY i.wi", (id_,)) if normalizuj(st) != "nieaktualne"]
        istotnosci = Counter(ist for _, ist, _ in aktualne)
        statusy = Counter(st for _, _, st in aktualne)
        liczniki = {"kluczowe": istotnosci["kluczowe"], "wazne": istotnosci["ważne"],
                    "ciekawostki": istotnosci["ciekawostka"], "sporne": statusy["sporne"], "nowe": statusy["nowe"]}
        kluczowe = opisz_informacje(conn, [wi for wi, ist, _ in aktualne if ist == "kluczowe"])
        # --lista: wszystkie widoczne (jak szukaj: bez Ciekawostek, chyba że --ciekawostki) – Kluczowe, Ważne,
        # pozostałe, na końcu Ciekawostki; w grupie rosnąco po WI
        kolejnosc = {"kluczowe": 0, "ważne": 1, "ciekawostka": 3}
        lista = None
        if a.lista:
            wszystkie = sorted(aktualne, key=lambda x: (kolejnosc.get(x[1], 2), x[0]))
            lista = opisz_informacje(conn, [wi for wi, ist, _ in wszystkie if ist != "ciekawostka" or a.ciekawostki])
        # znane ograniczenie: SP powiązane tylko z Tematem (bez informacji tematu) tu nie wystąpią
        sp = otwarte_sp(conn, {n for (n,) in conn.execute(
            "SELECT s.sp FROM informacje_sp x JOIN informacje_tematy it ON it.wi = x.wi "
            "JOIN sprzecznosci s ON s.id = x.sp_id WHERE it.temat_id = ?", (id_,))})
        stan = meta_bazy(conn).get("zbudowano") or ""
    if a.json:
        wynik = {"stan": stan, "nazwa": nazwa, "stan_wiedzy": stan_wiedzy, "etap": etap, "w_skrocie": w_skrocie,
                 "liczniki": liczniki, "kluczowe": kluczowe, "sp": sp, "notion_url": url}
        if lista is not None:
            wynik["informacje"] = lista
        wypisz_json(wynik)
        return 0
    print(f"# indeks: stan {lokalnie(stan)} · temat: {jedna_linia(nazwa)} · {url or '–'}")
    print(f"Stan wiedzy: {jedna_linia(stan_wiedzy)} · Etap: {jedna_linia(etap)}")
    print(f"W skrócie: {jedna_linia(w_skrocie)}")
    print(f"Liczniki (bez nieaktualnych): Kluczowe {liczniki['kluczowe']} · Ważne {liczniki['wazne']} · "
          f"Ciekawostki {liczniki['ciekawostki']} · Sporne {liczniki['sporne']} · Nowe {liczniki['nowe']}")
    linia = linia_krotka if a.krotko else linia_informacji
    if lista is None:
        print("## Kluczowe")
        for w in kluczowe:
            print(linia(w))
    else:
        print(f"## Wszystkie informacje tematu ({len(lista)}; Kluczowe, Ważne, pozostałe" + (
            ", Ciekawostki)" if a.ciekawostki else f"; bez Ciekawostek: {liczniki['ciekawostki']} – --ciekawostki)"))
        for w in lista:
            print(linia(w))
    print("## Otwarte sprzeczności tematu")
    for s in sp:
        print(linia_sp(s, a.krotko))
    return 0


def linia_etapu(w: dict, z_etapem: bool) -> str:
    """Linia `etap`: pełna teza (bez skracania – czat czyta ją zamiast Notion), bez tematów (są w nagłówku sekcji)
    i bez źródeł; Etap tylko w sekcjach spoza etapu; Status inny niż „Nowe”, „Notatnik” (ustalenie), SP-n i 💬
    zostają – na nich opierają się reguły procedury `wiedza`."""
    czesci = [f"WI-{w['wi']}", jedna_linia(w["istotnosc"])] + ([jedna_linia(w["etap"])] if z_etapem else [])
    if normalizuj(w["status"]) not in ("", "nowe"):
        czesci.append(jedna_linia(w["status"]))
    czesci.append(jedna_linia(w["teza"]))
    if w["notatnik"]:
        czesci.append("Notatnik")
    if w["sp"]:
        czesci.append(", ".join(f"SP-{n}" for n in w["sp"]))
    if w["komentarz"].strip():
        czesci.append("💬")
    return " · ".join(czesci)


def dopasuj_etap(conn: sqlite3.Connection, nazwa: str):
    """Nazwa etapu z indeksu pasująca do `nazwa` (bez wielkości liter i diakrytyków; równa wygrywa z zawierającą);
    (etap, []) albo (None, lista nazw etapów), gdy pasuje kilka albo żaden."""
    szukana = bez_diakrytykow(nazwa).strip()
    etapy = sorted(e for (e,) in conn.execute("SELECT DISTINCT etap FROM informacje") if e)
    pasujace = [e for e in etapy if szukana and szukana in bez_diakrytykow(e)]
    dokladne = [e for e in pasujace if bez_diakrytykow(e).strip() == szukana]
    if len(dokladne) == 1:
        return dokladne[0], []
    return (pasujace[0], []) if len(pasujace) == 1 else (None, etapy)


def sekcje_etapu(conn: sqlite3.Connection, etap: str, a) -> list:
    """[(nagłówek sekcji, [opisy informacji], czy linie mają Etap)]: najpierw WSZYSTKIE Kluczowe (etapu, „Cała budowa”
    i innych etapów – czat na telefonie czyta w całości tylko pierwsze części, więc to, co najważniejsze, idzie na początek),
    potem Ważne etapu i „Cała budowa” pogrupowane tematami (teza raz, pod pierwszym tematem alfabetycznie, rosnąco po WI),
    a z --kontrola także Ważne rodzaju Kontrola / odbiór i Kolejność prac z innych etapów. Nieaktualne pominięte;
    Ciekawostki tylko z --ciekawostki (wewnątrz etapu, na końcu tematu)."""
    etapy = {bez_diakrytykow(e) for e in etapy_zbioru(etap)}
    kolejnosc = {"kluczowe": 0, "ważne": 1, "ciekawostka": 3}
    tematy_wi = {}
    for wi, nazwa in conn.execute("SELECT it.wi, t.nazwa FROM informacje_tematy it JOIN tematy t ON t.id = it.temat_id"):
        tematy_wi.setdefault(wi, []).append(nazwa or "")
    kluczowe, w_etapie, kontrola_inne = [], {}, []
    for wi, ist, st, et, rodzaj in conn.execute(
            "SELECT wi, istotnosc, status, etap, rodzaj FROM informacje ORDER BY wi"):
        ist_n, rodzaj_n, w_zbiorze = normalizuj(ist), bez_diakrytykow(rodzaj), bez_diakrytykow(et) in etapy
        if normalizuj(st) == "nieaktualne" or ist_n not in kolejnosc:
            continue
        if ist_n == "kluczowe":
            kluczowe.append((0 if w_zbiorze else 1, wi))
        elif w_zbiorze:
            if ist_n != "ciekawostka" or a.ciekawostki:
                temat = min(tematy_wi.get(wi) or ["(bez tematu)"])
                w_etapie.setdefault(temat, []).append((kolejnosc[ist_n], wi))
        elif a.kontrola and ist_n == "ważne" and rodzaj_n in ETAP_RODZAJE_KONTROLI:
            kontrola_inne.append(wi)
    sekcje = []
    if kluczowe:
        numery = [wi for _, wi in sorted(kluczowe)]
        sekcje.append((f"## Kluczowe – {' + '.join(etapy_zbioru(etap))} i inne etapy ({len(numery)})",
                       opisz_informacje(conn, numery), True))
    for temat in sorted(w_etapie, key=bez_diakrytykow):
        numery = [wi for _, wi in sorted(w_etapie[temat])]
        sekcje.append((f"## {jedna_linia(temat)} – Ważne ({len(numery)})", opisz_informacje(conn, numery), False))
    if a.kontrola:
        sekcje.append((f"## Kontrola / odbiór i Kolejność prac z innych etapów – Ważne ({len(kontrola_inne)})",
                       opisz_informacje(conn, kontrola_inne), True))
    return sekcje


def etapy_zbioru(etap: str) -> list:
    """Etapy wchodzące do zbioru `etap`: on sam i ETAP_WSPOLNY (raz, gdy to ten sam)."""
    return [etap] if bez_diakrytykow(etap) == bez_diakrytykow(ETAP_WSPOLNY) else [etap, ETAP_WSPOLNY]


def podziel_na_czesci(sekcje: list, sp: list, tytul_sp: str = "Otwarte sprzeczności etapu") -> list:
    """Linie wyniku (nagłówki sekcji, linie tez, na końcu otwarte SP pod nagłówkiem `tytul_sp`) pocięte na części po
    najwyżej ETAP_CZESC_ZNAKOW znaków, bez dzielenia linii; część zaczynająca się w środku sekcji dostaje jej nagłówek
    z „(c.d.)”."""
    linie = []
    for naglowek, informacje, z_etapem in sekcje:
        linie.append((naglowek, naglowek))
        linie += [(naglowek, linia_etapu(w, z_etapem)) for w in informacje]
    if sp:
        naglowek = f"## {tytul_sp} ({len(sp)})"
        linie.append((naglowek, naglowek))
        linie += [(naglowek, linia_sp(s, krotko=True)) for s in sp]
    czesci, biezaca, znakow = [], [], 0
    for sekcja, linia in linie:
        if biezaca and znakow + len(linia) + 1 > ETAP_CZESC_ZNAKOW:
            czesci.append(biezaca)
            biezaca, znakow = [], 0
        if not biezaca and linia != sekcja:
            biezaca.append(sekcja + " (c.d.)")
            znakow += len(sekcja) + 8
        biezaca.append(linia)
        znakow += len(linia) + 1
    if biezaca:
        czesci.append(biezaca)
    return czesci


def cmd_etap(a) -> int:
    if a.czesc is not None and a.czesc < 1:
        blad("--czesc musi być co najmniej 1")
        return 1
    with contextlib.closing(otworz_do_odczytu(a)) as conn:
        etap, etapy = dopasuj_etap(conn, a.nazwa)
        if etap is None:
            if a.json:
                wypisz_json({"etapy": etapy})
            else:
                print(f"# etap „{a.nazwa}”: brak jednoznacznego etapu – dostępne: " + " · ".join(etapy))
            return 0
        sekcje = sekcje_etapu(conn, etap, a)
        numery = [w["wi"] for _, informacje, _ in sekcje for w in informacje]
        sp = otwarte_sp(conn, {sp for wi, sp in conn.execute(
            "SELECT x.wi, s.sp FROM informacje_sp x JOIN sprzecznosci s ON s.id = x.sp_id") if wi in set(numery)})
        stan = meta_bazy(conn).get("zbudowano") or ""
    czesci = podziel_na_czesci(sekcje, sp)
    if a.czesc is not None and a.czesc > len(czesci):
        blad(f"--czesc {a.czesc}: wynik ma {len(czesci)} części")
        return 1
    istotnosci = Counter(normalizuj(w["istotnosc"]) for _, informacje, _ in sekcje for w in informacje)
    liczniki = {"tez": len(numery), "kluczowe": istotnosci["kluczowe"], "wazne": istotnosci["ważne"],
                "ciekawostki": istotnosci["ciekawostka"], "sekcje": [(n, len(i)) for n, i, _ in sekcje],
                "znakow": sum(len(l) + 1 for c in czesci for l in c), "czesci": len(czesci)}
    if a.json:
        wynik = {"stan": stan, "etap": etap, "etapy": etapy_zbioru(etap), "kontrola": a.kontrola,
                 "liczniki": liczniki, "czesc": a.czesc, "sp": sp,
                 "sekcje": [{"naglowek": n, "informacje": i} for n, i, _ in sekcje]}
        wypisz_json(wynik)
        return 0
    naglowek = (f"# indeks: stan {lokalnie(stan)} · etap: {' + '.join(etapy_zbioru(etap))}"
                + (" + kontrola i kolejność z innych etapów" if a.kontrola else "")
                + f" · tez: {liczniki['tez']} (Kluczowe {liczniki['kluczowe']}, Ważne {liczniki['wazne']}"
                + (f", Ciekawostki {liczniki['ciekawostki']}" if a.ciekawostki else "")
                + f") · znaków: {liczniki['znakow'] // 1000} tys. · części: {len(czesci)}")
    if a.czesc is None:
        print(naglowek + " (wszystkie naraz; na czacie --czesc 1 … " + str(len(czesci)) + ")")
        for czesc in czesci:
            print("\n".join(czesc))
    else:
        print(naglowek + f" · część {a.czesc}/{len(czesci)}"
              + (" (ostatnia)" if a.czesc == len(czesci) else f" – dalej --czesc {a.czesc + 1}"))
        print("\n".join(czesci[a.czesc - 1]))
    return 0


def kolejnosc_etapu(etap) -> int:
    """Pozycja etapu w ETAPY_KOLEJNOSC (bez wielkości liter i diakrytyków); etap spoza listy – za wszystkimi."""
    znane = [bez_diakrytykow(e) for e in ETAPY_KOLEJNOSC]
    e = bez_diakrytykow(etap)
    return znane.index(e) if e in znane else len(znane)


def karty_w_indeksie(conn: sqlite3.Connection) -> bool:
    """Indeks ma tabele kart i co najmniej jedną kartę; kopia sprzed kart (albo bez zapisanych kart) – False."""
    if conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE name IN ('karty', 'karty_wi')").fetchone()[0] != 2:
        return False
    return conn.execute("SELECT COUNT(*) FROM karty").fetchone()[0] > 0


def liczniki_kart(conn: sqlite3.Connection, meta: dict) -> dict:
    """{"kart", "pytania", "czynnosci", "zbudowano"} – zero kart, gdy indeks nie ma tabel kart."""
    rodzaje = Counter()
    if conn.execute("SELECT 1 FROM sqlite_master WHERE name = 'karty'").fetchone():
        rodzaje = Counter(r for (r,) in conn.execute("SELECT rodzaj FROM karty"))
    return {"kart": sum(rodzaje.values()), "pytania": rodzaje["pytanie"], "czynnosci": rodzaje["czynnosc"],
            "zbudowano": meta.get("karty_zbudowano")}


def wczytaj_karty(conn: sqlite3.Connection) -> dict:
    """{kod: karta}: pola tabeli `karty` (pytania jako lista) i `wi` – zbiór WI karty, które są w indeksie i nie mają
    Statusu „Nieaktualne” (wpis do usuniętej informacji wypada)."""
    karty = {}
    for kod, rodzaj, nazwa, etap, opis, pytania, zbudowano, pokrycie_, pokrycie_k, pokrycie_opis in conn.execute(
            "SELECT kod, rodzaj, nazwa, etap, opis, pytania, zbudowano, pokrycie, pokrycie_k, pokrycie_opis "
            "FROM karty"):
        try:
            lista = json.loads(pytania or "[]")
        except ValueError:
            lista = []
        karty[kod] = {"kod": kod, "rodzaj": rodzaj or "", "nazwa": nazwa or "", "etap": etap or "", "opis": opis or "",
                      "pytania": [p for p in lista if isinstance(p, str)] if isinstance(lista, list) else [],
                      "zbudowano": zbudowano or "", "pokrycie": pokrycie_, "pokrycie_k": pokrycie_k,
                      "pokrycie_opis": pokrycie_opis or "", "wi": set(), "wiecej": set()}
    # zrodlo "wiecej" = rozszerzenie karty (tezy pokrewne poza rdzeniem; `karta --wiecej`), reszta = rdzeń karty
    for kod, wi, zrodlo, status in conn.execute("SELECT k.kod, k.wi, k.zrodlo, i.status FROM karty_wi k "
                                                "JOIN informacje i ON i.wi = k.wi"):
        if kod in karty and normalizuj(status) != "nieaktualne":
            karty[kod]["wiecej" if zrodlo == ZRODLO_WIECEJ else "wi"].add(wi)
    return karty


def kolejnosc_kart(karty) -> list:
    """Karty wg ETAPY_KOLEJNOSC, potem nazwy (bez diakrytyków), potem kodu."""
    return sorted(karty, key=lambda k: (kolejnosc_etapu(k["etap"]), bez_diakrytykow(k["nazwa"]), k["kod"]))


def sekcje_karty(opisy: list, etap: str, ciekawostki: bool) -> list:
    """[(nagłówek sekcji, [opisy informacji], True)] dla tez karty (opisy z opisz_informacje, bez Nieaktualnych):
    najpierw wszystkie Kluczowe – z etapu karty i „Cała budowa”, potem z innych etapów (czat czyta najpierw początek),
    potem pozostałe bez Ciekawostek pogrupowane pierwszym tematem alfabetycznie (teza raz; Istotność spoza listy –
    razem z Ważnymi), na końcu Ciekawostki (tylko `ciekawostki`). W grupie rosnąco po WI; linie z Etapem, bo karta
    łączy etapy."""
    etapy = {bez_diakrytykow(e) for e in etapy_zbioru(etap)}
    kluczowe, wazne, ciekaw = [], {}, []
    for w in sorted(opisy, key=lambda o: o["wi"]):
        ist = normalizuj(w["istotnosc"])
        if ist == "kluczowe":
            kluczowe.append((0 if bez_diakrytykow(w["etap"]) in etapy else 1, w["wi"], w))
        elif ist == "ciekawostka":
            ciekaw.append(w)
        else:
            wazne.setdefault(w["tematy"][0] if w["tematy"] else "(bez tematu)", []).append(w)
    sekcje = []
    if kluczowe:
        sekcje.append((f"## Kluczowe ({len(kluczowe)})", [w for *_, w in sorted(kluczowe, key=lambda x: x[:2])], True))
    for temat in sorted(wazne, key=bez_diakrytykow):
        sekcje.append((f"## {jedna_linia(temat)} – Ważne ({len(wazne[temat])})", wazne[temat], True))
    if ciekawostki and ciekaw:
        sekcje.append((f"## Ciekawostki ({len(ciekaw)})", ciekaw, True))
    return sekcje


def sp_sekcji(conn: sqlite3.Connection, sekcje: list) -> list:
    """Otwarte SP tez pokazanych w sekcjach (pole `sp` opisów informacji)."""
    return otwarte_sp(conn, {n for _, informacje, _ in sekcje for w in informacje for n in w["sp"]})


def rozmiar_karty(conn: sqlite3.Connection, opisy: list, etap: str) -> dict:
    """Liczniki i rozmiar karty tak, jak ją pokaże `karta` bez opcji (te same sekcje i podział na części): tez (bez
    Ciekawostek), kluczowe, wazne (z Istotnością spoza listy), ciekawostki (ukryte), znakow, czesci."""
    sekcje = sekcje_karty(opisy, etap, False)
    czesci = podziel_na_czesci(sekcje, sp_sekcji(conn, sekcje), TYTUL_SP_KARTY)
    ist = Counter(normalizuj(w["istotnosc"]) for w in opisy)
    tez = len(opisy) - ist["ciekawostka"]
    return {"tez": tez, "kluczowe": ist["kluczowe"], "wazne": tez - ist["kluczowe"], "ciekawostki": ist["ciekawostka"],
            "znakow": sum(len(linia) + 1 for c in czesci for linia in c), "czesci": len(czesci)}


def trafienia_rrf(conn: sqlite3.Connection, zapytania: list, limit: int) -> tuple:
    """(pierwsze `limit` WI z polacz_rrf wyników wyszukaj_poziomy dla każdego zapytania – jak szukaj z kilkoma
    zapytaniami, bez filtrów, bez Nieaktualnych i Ciekawostek; {WI: punkty RRF}). Zapytanie bez słów pominięte."""
    a = argparse.Namespace(etap=None, istotnosc=None, status=None, rodzaj=None, temat=None, ciekawostki=False,
                           limit=limit, krotko=False, sens=False)
    listy = {nr: wyszukaj_poziomy(conn, q, a)[0] for nr, q in enumerate(zapytania, 1)
             if zbuduj_zapytanie_fts(q, "AND") is not None}
    punkty = punkty_rrf(listy)
    return [wi for wi, _ in polacz_rrf(listy)][:limit], {wi: p[0] for wi, p in punkty.items()}


def dopelnienie_karty(conn: sqlite3.Connection, zapytania: list, karta: set) -> list:
    """Dopełnienie karty z szukania: z pierwszych DOPELNIENIE_TOP trafień (trafienia_rrf) te spoza karty, najwyżej
    DOPELNIENIE_LINII – ta sama lista w `karta --pytanie` i w pomiarze kart (tools/wiedza_karty.py pomiar)."""
    top, _ = trafienia_rrf(conn, zapytania, DOPELNIENIE_TOP)
    return [wi for wi in top if wi not in karta][:DOPELNIENIE_LINII]


def procent(x) -> str:
    return "–" if x is None else f"{round(100 * x)}%"


def linia_karty(k: dict, r: dict) -> str:
    """Linia spisu `karty`: kod, etap, nazwa, liczniki i rozmiar (rozmiar_karty), pokrycie (gdy zmierzone), opis;
    karta pytań – także pierwsze przykładowe pytanie."""
    tys = max(1, round(r["znakow"] / 1000)) if r["znakow"] else 0
    czesci = [k["kod"], jedna_linia(k["etap"]), jedna_linia(k["nazwa"]),
              f"tez {r['tez']} (K {r['kluczowe']})" + (f" +{r['ciekawostki']} ciek." if r["ciekawostki"] else "")
              + (f" +{len(k['wiecej'])} więcej" if k.get("wiecej") else ""),
              f"~{tys} tys. zn.", f"{r['czesci']} cz."]
    if k["pokrycie"] is not None:
        czesci.append(f"pokrycie {procent(k['pokrycie'])} / K {procent(k['pokrycie_k'])}")
    czesci.append(skroc(jedna_linia(k["opis"]), KARTY_OPIS_ZNAKOW))
    if k["rodzaj"] == "pytanie" and k["pytania"]:
        czesci.append(f"np. „{skroc(jedna_linia(k['pytania'][0]), KARTY_PYTANIE_ZNAKOW)}”")
    return " · ".join(czesci)


def opis_pokrycia(k: dict) -> str:
    """Pokrycie karty wobec wzorca do nagłówka `karta` (zapisuje je tools/wiedza_karty.py pomiar --zapisz)."""
    if k["pokrycie"] is None:
        return "pokrycie: niemierzone" + (" (karta czynności – tagi modelu)" if k["rodzaj"] == "czynnosc" else "")
    return (f"pokrycie {procent(k['pokrycie'])} trafnych / {procent(k['pokrycie_k'])} Kluczowych"
            + (f" ({jedna_linia(k['pokrycie_opis'])})" if k["pokrycie_opis"] else ""))


def karta_json(k: dict, rozmiar: dict = None) -> dict:
    wynik = dict(k, wi=sorted(k["wi"]), wiecej=sorted(k.get("wiecej") or ()))
    if rozmiar is not None:
        wynik["rozmiar"] = rozmiar
    return wynik


def pasuje_karta(k: dict, a) -> bool:
    """Filtr spisu: --rodzaj równy; --etap jako część nazwy etapu (bez wielkości liter i diakrytyków) – karty
    „Cała budowa” pasują do każdego etapu."""
    if a.rodzaj and k["rodzaj"] != a.rodzaj:
        return False
    if a.etap:
        etap = bez_diakrytykow(k["etap"])
        return bez_diakrytykow(a.etap).strip() in etap or etap == bez_diakrytykow(ETAP_WSPOLNY)
    return True


def cmd_karty(a) -> int:
    if a.do is not None and all(zbuduj_zapytanie_fts(q, "AND") is None for q in a.do):
        blad("--do: puste zapytanie – podaj słowa pytania")
        return 1
    with contextlib.closing(otworz_do_odczytu(a)) as conn:
        if not karty_w_indeksie(conn):
            if a.json:
                wypisz_json({"karty": [], "brak": True})
            else:
                print(BRAK_KART)
            return 0
        meta = meta_bazy(conn)
        liczniki = liczniki_kart(conn, meta)
        wybrane = [k for k in kolejnosc_kart(wczytaj_karty(conn).values()) if pasuje_karta(k, a)]
        opisy = {w["wi"]: w for w in opisz_informacje(conn, sorted({wi for k in wybrane for wi in k["wi"]}))}
        rozmiary = {k["kod"]: rozmiar_karty(conn, [opisy[wi] for wi in sorted(k["wi"])], k["etap"]) for k in wybrane}
        top, punkty = trafienia_rrf(conn, a.do, KARTY_TOP) if a.do else ([], {})
    dopasowanie = None
    if a.do:
        w_top = set(top)
        trafione = [(sum(punkty[wi] for wi in k["wi"] & w_top), len(k["wi"] & w_top), k) for k in wybrane]
        najlepsze = [t for t in sorted(trafione, key=lambda t: (-t[0], -t[1])) if t[1]][:KARTY_DOPASOWANYCH]
        w_kartach = set().union(*(k["wi"] for k in wybrane))
        kody_najlepszych = {k["kod"] for _, _, k in najlepsze}
        dopasowanie = {"zapytania": a.do, "top": len(top),
                       "karty": [{"kod": k["kod"], "trafien": n, "waga": round(waga, 4)} for waga, n, k in najlepsze],
                       "poza": [wi for wi in top if wi not in w_kartach],
                       "pozostale": [k["kod"] for k in wybrane if k["kod"] not in kody_najlepszych]}
    if a.json:
        wypisz_json({"stan": meta.get("zbudowano") or "", "liczniki": liczniki,
                     "karty": [karta_json(k, rozmiary[k["kod"]]) for k in wybrane], "dopasowanie": dopasowanie})
        return 0
    naglowek = (f"# indeks: stan {lokalnie(meta.get('zbudowano'))} · karty: {liczniki['kart']} (pytania "
                f"{liczniki['pytania']}, czynności {liczniki['czynnosci']}) · zbudowano {lokalnie(liczniki['zbudowano'])}"
                f" · wybieraj karty do ok. {KARTY_RAZEM_ZNAKOW // 1000} tys. znaków razem; czytaj: karta KOD [KOD2] "
                '--pytanie "A" "B" --czesc 1')
    filtry = [f"{n}: {v}" for n, v in (("etap", a.etap), ("rodzaj", a.rodzaj)) if v]
    print(naglowek + (" · filtr: " + ", ".join(filtry) if filtry else ""))
    if dopasowanie is None:
        for rodzaj, tytul in (("pytanie", "## Karty pytań"), ("czynnosc", "## Karty czynności")):
            karty = [k for k in wybrane if k["rodzaj"] == rodzaj]
            if karty:
                print(tytul)
                for k in karty:
                    print(linia_karty(k, rozmiary[k["kod"]]))
        return 0
    print(f"## Dopasowanie do pytania (trafień w karcie / {len(top)})")
    for _, n, k in najlepsze:
        print(f"trafień {n}/{len(top)} · " + linia_karty(k, rozmiary[k["kod"]]))
    if not najlepsze:
        print("żadna karta nie ma trafień – użyj szukaj")
    poza = dopasowanie["poza"]
    print(f"trafienia poza wszystkimi kartami: {len(poza)}"
          + (" – " + ", ".join(f"WI-{wi}" for wi in poza[:KARTY_POZA]) if poza else "")
          + (f" … (+{len(poza) - KARTY_POZA})" if len(poza) > KARTY_POZA else ""))
    if dopasowanie["pozostale"]:
        print("## Pozostałe karty")
        print(" · ".join(dopasowanie["pozostale"]))
    return 0


def cmd_karta(a) -> int:
    if a.czesc is not None and a.czesc < 1:
        blad("--czesc musi być co najmniej 1")
        return 1
    if a.pytanie is not None and all(zbuduj_zapytanie_fts(q, "AND") is None for q in a.pytanie):
        blad("--pytanie: puste zapytanie – podaj słowa do wyszukania")
        return 1
    with contextlib.closing(otworz_do_odczytu(a)) as conn:
        if not karty_w_indeksie(conn):
            if a.json:
                wypisz_json({"karty": [], "brak": True})
            else:
                print(BRAK_KART)
            return 0
        karty = wczytaj_karty(conn)
        kody = list(dict.fromkeys(a.kod))
        nieznane = [k for k in kody if k not in karty]
        if nieznane:
            for kod in nieznane:
                podobne = difflib.get_close_matches(kod, sorted(karty), n=5, cutoff=0.4)
                blad(f"karta „{kod}”: nie ma takiej karty – "
                     + ("podobne: " + " · ".join(podobne) if podobne else "spis kart: karty"))
            return 1
        warstwa = "wiecej" if a.wiecej else "wi"
        numery = sorted(set().union(*(karty[k][warstwa] for k in kody)))
        rozszerzenie = sum(len(karty[k]["wiecej"]) for k in kody)
        opisy = opisz_informacje(conn, numery)
        # Ciekawostki karty domyślnie widoczne (sekcja na końcu): karta jest już wyborem, a wzorzec liczy je jako trafne
        pokaz_ciekawostki = not a.bez_ciekawostek
        sekcje = sekcje_karty(opisy, karty[kody[0]]["etap"], pokaz_ciekawostki)
        dopelnienie = None
        if a.pytanie:
            dopelnienie = dopelnienie_karty(conn, a.pytanie, set(numery))
            sekcje.append((f"## Dopełnienie z szukania ({len(dopelnienie)})", opisz_informacje(conn, dopelnienie), True)
                          if dopelnienie else
                          ("## Dopełnienie z szukania: brak – szukanie nic nie dodaje do karty", [], True))
        sp = sp_sekcji(conn, sekcje)
        stan = meta_bazy(conn).get("zbudowano") or ""
    czesci = podziel_na_czesci(sekcje, sp, TYTUL_SP_KARTY)
    if a.czesc is not None and czesci and a.czesc > len(czesci):
        blad(f"--czesc {a.czesc}: wynik ma {len(czesci)} części")
        return 1
    ist = Counter(normalizuj(w["istotnosc"]) for w in opisy)
    ciekaw = ist["ciekawostka"]
    liczniki = {"tez": len(opisy) - (0 if pokaz_ciekawostki else ciekaw), "kluczowe": ist["kluczowe"],
                "wazne": len(opisy) - ist["kluczowe"] - ciekaw, "ciekawostki": ciekaw,
                "dopelnienie": None if dopelnienie is None else len(dopelnienie),
                "znakow": sum(len(linia) + 1 for c in czesci for linia in c), "czesci": len(czesci)}
    if a.json:
        wypisz_json({"stan": stan, "karty": [karta_json(karty[k]) for k in kody], "liczniki": liczniki,
                     "czesc": a.czesc, "sp": sp, "dopelnienie": dopelnienie, "wiecej": a.wiecej,
                     "sekcje": [{"naglowek": n, "informacje": i} for n, i, _ in sekcje]})
        return 0
    pokrycia = [opis_pokrycia(karty[k]) for k in kody]
    pokrycia = pokrycia[0] if len(set(pokrycia)) == 1 else "; ".join(f"{k}: {p}" for k, p in zip(kody, pokrycia))
    naglowek = (f"# indeks: stan {lokalnie(stan)} · karta: "
                + " + ".join(f"{k} „{jedna_linia(karty[k]['nazwa'])}”" for k in kody)
                + (" (rozszerzenie – tezy pokrewne poza rdzeniem)" if a.wiecej else "")
                + f" · tez {liczniki['tez']} (Kluczowe {liczniki['kluczowe']}, Ważne {liczniki['wazne']}"
                + (f", Ciekawostki {ciekaw}" if pokaz_ciekawostki else "") + ")"
                + (f" (+{ciekaw} ciekawostek ukrytych – bez --bez-ciekawostek)" if ciekaw and not pokaz_ciekawostki else "")
                + f" · znaków {liczniki['znakow'] // 1000} tys. · części {len(czesci)} · {pokrycia}"
                + (f" · dopełnienie {len(dopelnienie)}" if dopelnienie is not None else "")
                + (f" · rozszerzenie: +{rozszerzenie} tez pokrewnych (karta KOD --wiecej, po przeczytaniu rdzenia)"
                   if rozszerzenie and not a.wiecej else ""))
    if not czesci:
        print(naglowek + (" · rozszerzenie puste" if a.wiecej else " · karta pusta – użyj szukaj / temat / etap"))
    elif a.czesc is None:
        print(naglowek + f" (wszystkie naraz; na czacie --czesc 1 … {len(czesci)})")
        for czesc in czesci:
            print("\n".join(czesc))
    else:
        print(naglowek + f" · część {a.czesc}/{len(czesci)}"
              + (" (ostatnia)" if a.czesc == len(czesci) else f" – dalej --czesc {a.czesc + 1}"))
        print("\n".join(czesci[a.czesc - 1]))
    return 0


def dzien_lokalny(tekst):
    """`dodano` (UTC z API) → data lokalna; bez zamiany para z granicy doby wypadłaby z --od o dzień."""
    return na_czas(tekst).astimezone().date() if tekst else None


def tokeny_tezy(tekst: str) -> set:
    """Tokeny tezy już po bez_diakrytykow: co najmniej 5 znaków, bez liczb i stop-słów."""
    return {t for t in NIE_SLOWO.sub(" ", tekst).split() if len(t) >= 5 and not t.isdigit() and t not in STOP_SLOWA}


def pary_podobne(conn: sqlite3.Connection, tezy: dict, nowe: set, prog: float) -> list:
    """duplikaty po znaczeniu: [(podobieństwo, WI mniejsze, WI większe)] z tabeli `podobne` od progu, obie
    informacje w `tezy`, co najmniej jedna w `nowe`; para raz (lista bywa jednostronna – wyższa wartość)."""
    pary = {}
    for wi, p, s in conn.execute("SELECT wi, wi_podobne, podobienstwo FROM podobne WHERE podobienstwo >= ?", (prog,)):
        if wi in tezy and p in tezy and (wi in nowe or p in nowe):
            klucz = (min(wi, p), max(wi, p))
            pary[klucz] = max(pary.get(klucz, 0.0), s)
    return [(s, x, y) for (x, y), s in pary.items()]


def cmd_duplikaty(a) -> int:
    od = None
    if a.od:
        try:
            od = date.fromisoformat(a.od)
        except ValueError:
            blad("--od: podaj datę w formacie RRRR-MM-DD")
            return 1
    if a.prog is not None and not 0 < a.prog <= 1:
        blad("--prog: podaj liczbę z przedziału (0, 1]")
        return 1
    with contextlib.closing(otworz_do_odczytu(a)) as conn:
        # po znaczeniu, gdy indeks ma listy podobnych; --slowa albo kopia bez list – po słowach jak dotąd
        sens = not a.slowa and bool(podobne_w_indeksie(conn))
        if a.prog is None:
            a.prog = DUPLIKATY_PROG_SENS if sens else DUPLIKATY_PROG_SLOWA
        temat = wi_tematow(conn, a.temat) if a.temat is not None else None
        tezy = {}  # WI → (teza, teza po bez_diakrytykow, data lokalna dodania); bez „Nieaktualne”
        for wi, teza, status, dodano in conn.execute("SELECT wi, teza, status, dodano FROM informacje ORDER BY wi"):
            if normalizuj(status) != "nieaktualne" and (temat is None or wi in temat):
                tezy[wi] = (teza or "", bez_diakrytykow(teza), dzien_lokalny(dodano))
        zrodla = {}
        for wi, zrd in conn.execute("SELECT x.wi, z.zrd FROM informacje_zrodla x JOIN zrodla z ON z.id = x.zrd_id "
                                    "ORDER BY z.zrd"):
            zrodla.setdefault(wi, []).append(zrd)
        stan = meta_bazy(conn).get("zbudowano") or ""
        # --od przed parowaniem: kandydaci tylko dla nowych tez; para obu nowych liczona raz (od mniejszego WI)
        nowe = {wi for wi, (_, _, dodano) in tezy.items() if od is None or (dodano and dodano >= od)}
        pary = pary_podobne(conn, tezy, nowe, a.prog) if sens else pary_po_slowach(tezy, nowe, a.prog)
    pary.sort(key=lambda p: (-p[0], p[1], p[2]))
    metoda = "znaczenie" if sens else "słowa" + (" (brak list podobnych)" if a.sens else "")
    if a.json:
        wypisz_json({"stan": stan, "prog": a.prog, "od": a.od, "metoda": metoda, "pary": [
            {"wi_a": x, "wi_b": y, "ratio": round(r, 4), "teza_a": tezy[x][0], "teza_b": tezy[y][0],
             "zrodla_a": zrodla.get(x, []), "zrodla_b": zrodla.get(y, [])} for r, x, y in pary]})
        return 0
    print(f"# indeks: stan {lokalnie(stan)} · duplikaty ({metoda}): próg {a.prog}" + (f" · od {a.od}" if a.od else "")
          + (f" · temat: {a.temat}" if a.temat is not None else ""))
    for r, x, y in pary:
        zr = [", ".join(f"ZRD-{n}" for n in zrodla.get(w, [])) or "–" for w in (x, y)]
        print(f"WI-{x} ↔ WI-{y} · {r:.2f} · {skroc(tezy[x][0], 80)} | {skroc(tezy[y][0], 80)} · "
              f"źródła: {zr[0]} / {zr[1]}")
    print(f"# par: {len(pary)}")
    return 0


def pary_po_slowach(tezy: dict, nowe: set, prog: float) -> list:
    """duplikaty po słowach (difflib, bez autojunk – ten zaniżał ratio długich tez): [(ratio, WI, WI)]."""
    # indeks odwrócony token → WI zamiast porównywać każdą parę; kandydaci z najrzadszych tokenów (CZESTOSC_*,
    # SONDA_*), bo długie listy tokenów pospolitych dawały kwadratowo wiele kandydatów
    tokeny = {wi: tokeny_tezy(znormalizowana) for wi, (_, znormalizowana, _) in tezy.items()}
    czestosc = Counter(t for ts in tokeny.values() for t in ts)
    limit = max(CZESTOSC_MIN, CZESTOSC_UDZIAL * len(tezy))
    indeks = {}
    for wi, ts in tokeny.items():
        for t in ts:
            indeks.setdefault(t, []).append(wi)
    pary = []
    for x in sorted(nowe):
        kolejnosc = sorted(tokeny[x], key=lambda t: (czestosc[t], t))
        rzadkie = [t for t in kolejnosc if czestosc[t] <= limit]
        sonda = rzadkie[:SONDA_RZADKIE] if len(rzadkie) >= 3 else kolejnosc[:SONDA_POSPOLITE]
        kandydaci = {y for t in sonda for y in indeks[t] if y != x and (y not in nowe or y > x)}
        lx = len(tezy[x][1])
        wspolne = ((len(tokeny[x] & tokeny[y]), abs(lx - len(tezy[y][1])), y) for y in kandydaci
                   if 2 * min(lx, len(tezy[y][1])) >= prog * (lx + len(tezy[y][1])))
        for n, _, y in heapq.nlargest(KANDYDACI_NA_TEZE, wspolne, key=lambda p: (p[0], -p[1], -p[2])):
            if n < 3:
                break
            p, q = min(x, y), max(x, y)
            miara = difflib.SequenceMatcher(None, tezy[p][1], tezy[q][1], autojunk=False)
            if miara.quick_ratio() >= prog:  # górne ograniczenie ratio – tańsze odsianie
                r = miara.ratio()
                if r >= prog:
                    pary.append((r, p, q))
    return pary


def cmd_stan(a) -> int:
    sciezka = sciezka_bazy(a)
    fts5 = sprawdz_fts5()
    with contextlib.closing(otworz_db(sciezka, zapis=False)) as conn:
        liczniki = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                    for t in ("informacje", "tematy", "zrodla", "sprzecznosci")}
        liczniki["fts"] = conn.execute("SELECT COUNT(*) FROM informacje_fts").fetchone()[0] if fts5 else None
        sync = sorted(({"baza": b, "ostatnie_zmieniono": o, "wierszy": w, "zsynchronizowano": z}
                       for b, o, w, z in conn.execute("SELECT * FROM sync_stan")),
                      key=lambda s: list(BAZY).index(s["baza"]) if s["baza"] in BAZY else len(BAZY))
        meta = meta_bazy(conn)
        # nigdy nie opublikowano → brak opublikowano_sha → kopia nieaktualna
        aktualna = meta.get("opublikowano_sha") == hash_danych(conn)
        schemat = conn.execute("PRAGMA user_version").fetchone()[0]
        podobne = {"wierszy": podobne_w_indeksie(conn), "policzone": meta.get("podobne_policzone"),
                   "model": meta.get("podobne_model"), "bez_listy": meta.get("podobne_brakuje")}
        karty = liczniki_kart(conn, meta)
    dane = {"liczniki": liczniki, "sync_stan": sync, "zbudowano": meta.get("zbudowano"),
            "ostatni_pelny": meta.get("ostatni_pelny"), "opublikowano_kiedy": meta.get("opublikowano_kiedy"),
            "publikacje_liczba": int(meta.get("publikacje_liczba") or 0),
            "historia_mb": round(float(meta.get("historia_mb") or 0), 1), "kopia_aktualna": aktualna,
            "rozmiar_mb": round(sciezka.stat().st_size / MB, 2), "sqlite": sqlite3.sqlite_version,
            "fts5": fts5, "schemat": schemat, "podobne": podobne, "karty": karty}
    if a.json:
        wypisz_json(dane)
        return 0
    rozmiar, historia = (str(dane[k]).replace(".", ",") for k in ("rozmiar_mb", "historia_mb"))
    print(f"# indeks wiedzy: {sciezka.name} · {rozmiar} MB · schemat {schemat} · "
          f"SQLite {dane['sqlite']} · FTS5: {'tak' if fts5 else 'nie'}")
    print(f"liczniki: informacje {liczniki['informacje']} · tematy {liczniki['tematy']} · źródła {liczniki['zrodla']}"
          f" · SP {liczniki['sprzecznosci']} · FTS {'–' if liczniki['fts'] is None else liczniki['fts']}")
    for s in sync:
        print(f"sync {s['baza']}: wierszy {s['wierszy']} · ostatnia zmiana {lokalnie(s['ostatnie_zmieniono'])} · "
              f"zsynchronizowano {lokalnie(s['zsynchronizowano'])}")
    print(f"zbudowano: {lokalnie(dane['zbudowano'])} · ostatni pełny sync: {lokalnie(dane['ostatni_pelny'])}")
    print(f"publikacja: {lokalnie(dane['opublikowano_kiedy'])} · publikacji {dane['publikacje_liczba']} · "
          f"historia ok. {historia} MB · kopia aktualna: {'tak' if aktualna else 'nie'}")
    if podobne["wierszy"] is None:
        print("listy podobnych: brak (indeks sprzed list – `szukaj --krotko` bez sekcji podobnych)")
    else:
        print(f"listy podobnych: {podobne['wierszy']} wierszy · policzone {lokalnie(podobne['policzone'])} · model "
              f"{podobne['model'] or '–'} · informacji bez listy {podobne['bez_listy'] or '–'}")
    if karty["kart"]:
        print(f"karty: {karty['kart']} (pytania {karty['pytania']}, czynności {karty['czynnosci']}) · zbudowano "
              f"{lokalnie(karty['zbudowano'])}")
    else:
        print("karty: brak")
    if dane["historia_mb"] > LIMIT_HISTORII_MB:
        ostrzez(f"historia prywatnego repo ponad {LIMIT_HISTORII_MB} MB – uruchom publikuj --reset "
                "(jeden commit z bieżącymi plikami zamiast całej historii)")
    return 0


def zbuduj_parser() -> argparse.ArgumentParser:
    wspolne = argparse.ArgumentParser(add_help=False)
    wspolne.add_argument("--db", type=Path, help="plik indeksu (domyślnie .dom/wiedza/wiedza.sqlite w hubie)")
    wspolne.add_argument("--cicho", action="store_true", help="tylko zmiany i błędy")
    wspolne.add_argument("--json", action="store_true", help="wynik jako JSON")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="polecenie", metavar="POLECENIE", required=True)
    p = sub.add_parser("sync", parents=[wspolne], help="pobierz zmiany z Notion do indeksu")
    p.add_argument("--pelny", action="store_true", help="pełny listing i usunięcie wierszy nieobecnych w Notion")
    p.add_argument("--publikuj", action="store_true",
                   help="po udanym syncu publikacja jak `publikuj` (pod tą samą blokadą; z --cicho w limicie czasu)")
    p = sub.add_parser("szukaj", parents=[wspolne],
                       help=f"szukanie w Informacjach (AND; poniżej {DOPELNIJ_PONIZEJ} trafień dopełnione przez OR)")
    p.add_argument("zapytanie", nargs="+",
                   help='słowa (prefiks*), "fraza" albo OR między słowami; kilka zapytań w osobnych cudzysłowach – '
                        "każde osobno, wyniki połączone bez powtórzeń, przy linii numery zapytań [1,3]")
    p.add_argument("--etap", help="równy Etap")
    p.add_argument("--istotnosc", help="równa Istotność (włącza też ciekawostki)")
    p.add_argument("--status", help="równy Status (włącza też nieaktualne)")
    p.add_argument("--rodzaj", help="równy Rodzaj")
    p.add_argument("--temat", help="część nazwy tematu")
    p.add_argument("--ciekawostki", action="store_true", help="pokaż też Istotność „Ciekawostka”")
    p.add_argument("--krotko", action="store_true",
                   help=f"zwarta linia (teza do {KROTKO_TEZA} zn., tematy, typ autora/wiarygodność; bez tytułów, Kto, "
                        f"linków) – dla czatu; domyślny limit {LIMIT_KROTKO}; pod trafieniami do {PODOBNE_LINII} "
                        "podobnych po znaczeniu (≈WI-n)")
    p.add_argument("--sens", action="store_true",
                   help="tylko Mac: ranking po słowach łączony z rankingiem po znaczeniu (Ollama); bez niej same słowa")
    p.add_argument("--limit", type=int,
                   help=f"najwyżej tyle linii (domyślnie {LIMIT_DOMYSLNY}, z --krotko {LIMIT_KROTKO})")
    p = sub.add_parser("temat", parents=[wspolne], help="stan wiedzy, liczniki, Kluczowe i otwarte SP tematu")
    p.add_argument("nazwa", help="nazwa tematu albo jej część")
    p.add_argument("--lista", action="store_true",
                   help="wszystkie widoczne informacje tematu zamiast samych Kluczowych")
    p.add_argument("--krotko", action="store_true", help="zwarte linie jak w szukaj --krotko")
    p.add_argument("--ciekawostki", action="store_true", help="z --lista: także Istotność „Ciekawostka”")
    p = sub.add_parser("etap", parents=[wspolne],
                       help=f"cała wiedza etapu (najpierw wszystkie Kluczowe, potem Ważne etapu i „{ETAP_WSPOLNY}” wg tematów, "
                            f"otwarte SP) w częściach po ok. {ETAP_CZESC_ZNAKOW // 1000} tys. znaków")
    p.add_argument("nazwa", help="nazwa etapu albo jej część (np. „Stan zero”)")
    p.add_argument("--czesc", type=int, help="numer części do pokazania (bez – wszystko naraz)")
    p.add_argument("--kontrola", action="store_true",
                   help="dołóż Ważne rodzaju Kontrola / odbiór i Kolejność prac z innych etapów (pytania „co sprawdzić "
                        "przed kolejnym etapem”)")
    p.add_argument("--ciekawostki", action="store_true", help="także Istotność „Ciekawostka” wewnątrz etapu")
    p = sub.add_parser("karty", parents=[wspolne],
                       help="spis kart wiedzy (gotowe zbiory tez na typowe pytania, wybrane modelem z całej bazy) "
                            "i dopasowanie kart do pytania")
    p.add_argument("--do", nargs="+", metavar="PYTANIE",
                   help=f"pytanie (kilka – w osobnych cudzysłowach): najwyżej {KARTY_DOPASOWANYCH} kart z największą "
                        f"wagą trafień wśród {KARTY_TOP} pierwszych wyników szukania i numery trafień spoza kart")
    p.add_argument("--etap", help=f"tylko karty etapu (część nazwy; karty „{ETAP_WSPOLNY}” zawsze)")
    p.add_argument("--rodzaj", choices=RODZAJE_KART, help="tylko karty pytań albo czynności")
    p = sub.add_parser("karta", parents=[wspolne],
                       help="wszystkie tezy karty (najpierw Kluczowe, potem Ważne wg tematów, otwarte SP) w częściach "
                            f"po ok. {ETAP_CZESC_ZNAKOW // 1000} tys. znaków")
    p.add_argument("kod", nargs="+", help="kod karty ze spisu `karty` (kilka – suma tez bez powtórzeń)")
    p.add_argument("--czesc", type=int, help="numer części do pokazania (bez – wszystko naraz)")
    p.add_argument("--pytanie", nargs="+", metavar="ZAPYTANIE",
                   help=f"dopełnienie z szukania: najwyżej {DOPELNIENIE_LINII} tez spoza karty z {DOPELNIENIE_TOP} "
                        "pierwszych wyników tych zapytań (brak = szukanie nic nie dodaje do karty)")
    p.add_argument("--ciekawostki", action="store_true", help=argparse.SUPPRESS)   # dziś domyślne; zostaje dla zgodności
    p.add_argument("--bez-ciekawostek", action="store_true",
                   help="ukryj Istotność „Ciekawostka” (domyślnie karta pokazuje je w sekcji na końcu – są jej częścią)")
    p.add_argument("--wiecej", action="store_true",
                   help="rozszerzenie karty zamiast rdzenia: tezy pokrewne (ocena 1 modelu) – czytaj po rdzeniu, gdy "
                        "inwestor chce „więcej” albo pytanie wykracza poza rdzeń")
    p = sub.add_parser("duplikaty", parents=[wspolne],
                       help="kandydaci na duplikaty: pary z list podobnych (po znaczeniu), bez list – po słowach")
    p.add_argument("--od", help="RRRR-MM-DD: co najmniej jedna z pary dodana od tej daty (lokalnie)")
    p.add_argument("--prog", type=float, help=f"minimalne podobieństwo (domyślnie {DUPLIKATY_PROG_SENS} po znaczeniu, "
                                              f"{DUPLIKATY_PROG_SLOWA} po słowach)")
    p.add_argument("--temat", help="tylko informacje tematu (część nazwy)")
    tryb = p.add_mutually_exclusive_group()
    tryb.add_argument("--sens", action="store_true",
                      help="po znaczeniu z list podobnych (domyślnie, gdy są; bez list – po słowach z dopiskiem)")
    tryb.add_argument("--slowa", action="store_true", help="po słowach (difflib) także wtedy, gdy są listy podobnych")
    sub.add_parser("stan", parents=[wspolne], help="liczniki, daty synchronizacji i publikacji, wersje")
    p = sub.add_parser("publikuj", parents=[wspolne],
                       help="kopia indeksu, wiedza.py i synonimów do prywatnego repo z GITHUB_REPO")
    p.add_argument("--teraz", action="store_true",
                   help=f"bez odstępu {PUBLIKACJA_CO_MIN} min (plik indeksu i tak tylko po zmianie danych)")
    p.add_argument("--wymus", action="store_true",
                   help="plik indeksu i README także bez zmiany danych (np. po odtworzeniu prywatnego repo)")
    p.add_argument("--reset", action="store_true",
                   help="historia repo od nowa: jeden commit bez rodzica z czterema plikami (gdy `stan` ostrzega)")
    return ap


# nazwa podkomendy → cmd_*(args) -> kod wyjścia
POLECENIA = {"sync": cmd_sync, "szukaj": cmd_szukaj, "temat": cmd_temat, "etap": cmd_etap, "karty": cmd_karty,
             "karta": cmd_karta, "duplikaty": cmd_duplikaty, "stan": cmd_stan, "publikuj": cmd_publikuj}


def linia_bledu(e: BaseException, plik: str = __file__) -> int:
    """Ostatnia linia pliku `plik` (domyślnie tego) na ścieżce wyjątku."""
    tb, linia = e.__traceback__, 0
    while tb is not None:
        if tb.tb_frame.f_code.co_filename == plik:
            linia = tb.tb_lineno
        tb = tb.tb_next
    return linia


def main(argv=None) -> int:
    a = zbuduj_parser().parse_args(argv)
    try:
        return POLECENIA[a.polecenie](a)
    except (BladIndeksu, BladMapowania) as e:
        blad(str(e))
        return 1
    except Exception as e:  # noqa: BLE001 – treść wyjątku i traceback mogą nieść wartości pól
        if uszkodzony(e):
            blad("indeks uszkodzony – uruchom sync (na Macu)")
        else:
            zglos_wyjatek(e, cicho=getattr(a, "cicho", False))
        return 0 if a.polecenie == "sync" and a.cicho else 1  # hook startu nie może blokować sesji


if __name__ == "__main__":
    sys.exit(main())
