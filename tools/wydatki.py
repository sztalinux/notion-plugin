#!/usr/bin/env python3
"""Wydatki z Notion do arkusza Google „Kosztorys” – bez AI, na Macu (launchd przez automaty/przeglad.py).

    python3 tools/wydatki.py sync [--proba] [--cicho]   # wiersze „Do arkusza” (i z pustym Arkusz) → Wydatki / Cennik
    python3 tools/wydatki.py pozycje [--cicho]          # lista pozycji z arkusza Kosztorys → opcje pola Pozycja w Notion
    python3 tools/wydatki.py pobierz [--cicho]          # wartości arkusza (JSON) do <hub>/Koszty/Kosztorys_google.json
    python3 tools/wydatki.py wycofaj <id strony> [...]  # usuwa wydatek z arkusza (i Cennika), w Notion „Nie wysyłać”
    python3 tools/wydatki.py sprawdz                    # konfiguracja, dostęp do bazy i do arkusza
    python3 tools/wydatki.py kod | pbcopy               # kod Apps Script do schowka (z docs/wydatki-arkusz.md)
    python3 tools/wydatki.py migruj <zmiany.json>        # zmiana układu na arkuszu (cofanie: Plik → Historia wersji)

Przepływ: przebieg Dziennika (agent) albo inwestor dodaje w Notion wiersz z Arkusz = „Do arkusza”; `sync` wysyła takie
wiersze do aplikacji Apps Script przypiętej do arkusza (kod i instrukcja: docs/wydatki-arkusz.md), a ta dopisuje je
w pierwszym wolnym wierszu arkusza Wydatki (bez nadpisywania kolumn z formułami). Wynik wraca do Notion: „W arkuszu”
z numerem wiersza albo „Błąd” z powodem. Ponowne wysłanie tej samej strony nie dubluje wiersza (kolumna Źródło
= notion:<id strony>). Strona już dopisana, która wróci do kolejki (zmienione pola + Arkusz = „Do arkusza”), poprawia swój
wiersz (pola wpisywane A:H, J:M – np. „Do zapłaty” → „Zrealizowane”); korekta z Notion nadpisuje ręczne zmiany tego wiersza
w arkuszu. Rodzaj „Wycena” (oferta dostawcy, cena za jednostkę w polu Kwota) idzie do arkusza Cennik;
ponowne wysłanie tej samej strony aktualizuje jej wiersz (np. Status wyceny = Wybrana). Wyceny wymagają kodu Apps Script
w wersji ≥ 2 i Cennika w nowym układzie (ping: cennik_ok) – inaczej czekają w kolejce.
Zmiany układu arkusza (kolumny, formuły, kolory) idą bez ponownego importu: plik zmian JSON z operacjami
(akcja „zmien” w Apps Script). Skrypt ma dostęp tylko do tego arkusza (@OnlyCurrentDoc) – bez kopii na Dysku; zmianę
cofa się z historii wersji arkusza.

Sekrety (`<hub>/.dom/sekrety.env`, chmod 600): ARKUSZ_URL (adres wdrożenia /exec), ARKUSZ_SEKRET (ten sam co
właściwość SEKRET w Apps Script), NOTION_TOKEN_WYDATKI albo NOTION_TOKEN (integracja z prawem odczytu i zmiany treści
w bazie). Zmienne WYDATKI_ARKUSZ_URL i WYDATKI_ARKUSZ_SEKRET nadpisują sekrety (testy na makiecie). Komunikaty niosą tylko liczby, numery pozycji
i statusy – bez kwot i opisów.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wiedza as W  # noqa: E402 – wspólne sekrety, HTTP do Notion, HUB

ZRODLO = os.environ.get("WYDATKI_ZRODLO") or "72cff09c-609b-405d-a32c-263271b3b59c"  # 💸 Wydatki → arkusz (DOM)
DO_ARKUSZA, W_ARKUSZU, BLAD = "Do arkusza", "W arkuszu", "Błąd"
ZASTEPCZA = "00.0"          # opcja-zaślepka Pozycji sprzed pierwszego `pozycje`
LIMIT_ARKUSZA_S = 90        # Apps Script bywa wolny przy zimnym starcie
PACZKA = 25                 # wierszy w jednym żądaniu do arkusza
WERSJA_WYCEN = 2            # minimalna wersja kodu Apps Script, która zapisuje wyceny do Cennika
PLIK_KOPII = "Kosztorys_google.json"
DOKUMENTACJA = Path(__file__).resolve().parent.parent / "docs" / "wydatki-arkusz.md"
LP = re.compile(r"^(\d{1,2})\.(\d+)$|^(P\d)\.(\d+)$")


class BladKonfiguracji(Exception):
    pass


class BladArkusza(Exception):
    pass


def konfiguracja() -> dict:
    s = W.wczytaj_sekrety(W.SEKRETY)
    k = {
        "sekrety": s,
        "token": s.get("NOTION_TOKEN_WYDATKI") or s.get("NOTION_TOKEN"),
        "url": os.environ.get("WYDATKI_ARKUSZ_URL") or s.get("ARKUSZ_URL"),
        "sekret": os.environ.get("WYDATKI_ARKUSZ_SEKRET") or s.get("ARKUSZ_SEKRET"),
    }
    return k


def wymagaj(k: dict, *pola):
    brak = [p for p in pola if not k.get(p)]
    nazwy = {"token": "NOTION_TOKEN", "url": "ARKUSZ_URL", "sekret": "ARKUSZ_SEKRET"}
    if brak:
        raise BladKonfiguracji("brak w .dom/sekrety.env: " + ", ".join(nazwy[b] for b in brak))


# ---------------------------------------------------------------- arkusz (Apps Script)

def arkusz(k: dict, akcja: str, **dane) -> dict:
    """POST do aplikacji Apps Script. Google odpowiada przekierowaniem 302 na wynik – domyślny urllib idzie za nim
    GET-em bez ciała, czyli tak, jak wymaga Apps Script; nagłówka Authorization nie ma, więc nic nie wycieka."""
    cialo = json.dumps(dict(dane, sekret=k["sekret"], akcja=akcja)).encode("utf-8")
    zadanie = urllib.request.Request(k["url"], data=cialo, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(zadanie, timeout=LIMIT_ARKUSZA_S) as odp:
            tresc = odp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        raise BladArkusza(f"HTTP {e.code}") from None
    except OSError as e:
        raise BladArkusza(type(e).__name__) from None
    try:
        wynik = json.loads(tresc)
    except ValueError:
        # strona logowania Google zamiast JSON = wdrożenie bez dostępu „Każdy”
        raise BladArkusza("odpowiedź nie jest JSON – sprawdź, czy wdrożenie ma dostęp „Każdy”") from None
    if not wynik.get("ok"):
        raise BladArkusza(str(wynik.get("blad") or "błąd bez opisu")[:200])
    return wynik


# ---------------------------------------------------------------- Notion

def naglowki(k: dict) -> dict:
    return {"Authorization": "Bearer " + k["token"], "Notion-Version": W.NOTION_WERSJA}


def kolejka(k: dict) -> list:
    url = f"{W.NOTION_API}/v1/data_sources/{ZRODLO}/query"
    # puste Arkusz też idzie: wiersz dodany z telefonu nie ma wartości domyślnej; „Nie wysyłać” = świadome wyłączenie
    cialo = {"page_size": 100, "filter": {"or": [{"property": "Arkusz", "select": {"equals": DO_ARKUSZA}},
                                                 {"property": "Arkusz", "select": {"is_empty": True}}]},
             "sorts": [{"timestamp": "created_time", "direction": "ascending"}]}
    strony = []
    while True:
        odp = W.zadanie_http("POST", url, naglowki(k), cialo)
        strony += odp.get("results") or []
        if not odp.get("has_more") or not odp.get("next_cursor"):
            return strony
        cialo["start_cursor"] = odp["next_cursor"]


def tekst(w: dict) -> str:
    return "".join(c.get("plain_text", "") for c in (w.get("title") or w.get("rich_text") or [])).strip()


def wybor(w: dict) -> str:
    return ((w.get("select") or {}).get("name") or "").strip()


def numer_pozycji(nazwa: str) -> str:
    """„3.5 Chudziak…” / „03.5” → „03.5”; „P1.1 …” → „P1.1”; reszta → ''."""
    pierwsze = (nazwa.split() or [""])[0]
    m = LP.match(pierwsze)
    if not m:
        return ""
    if m.group(1):
        return f"{int(m.group(1)):02d}.{m.group(2)}"
    return f"{m.group(3)}.{m.group(4)}"


def na_wiersz(strona: dict) -> dict:
    p = strona.get("properties") or {}
    data = ((p.get("Data") or {}).get("date") or {}).get("start") or ""
    wazna = ((p.get("Ważna do") or {}).get("date") or {}).get("start") or ""
    return {
        "rodzaj": wybor(p.get("Rodzaj") or {}) or "Wydatek",
        "status_wyceny": wybor(p.get("Status wyceny") or {}),
        "cena_podana": wybor(p.get("Cena podana") or {}),
        "wazna_do": wazna[:10],
        "vat": (p.get("VAT %") or {}).get("number"),
        "id": strona["id"],
        "data": data[:10],
        "status": wybor(p.get("Płatność") or {}) or "Zrealizowane",
        "kwota": (p.get("Kwota") or {}).get("number"),
        "lp": numer_pozycji(wybor(p.get("Pozycja") or {})),
        "typ": wybor(p.get("Typ") or {}),
        "ilosc": (p.get("Ilość") or {}).get("number"),
        "jedn": wybor(p.get("Jedn.") or {}),
        "sposob": wybor(p.get("Sposób") or {}),
        "opis": tekst(p.get("Wydatek") or {}),
        "dostawca": tekst(p.get("Dostawca / nr FV") or {}),
        "notatki": tekst(p.get("Notatki") or {}),
    }


def blad_lokalny(w: dict) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", w["data"]):
        return "brak daty"
    if not isinstance(w["kwota"], (int, float)) or w["kwota"] <= 0:
        return "brak kwoty" if w["rodzaj"] != "Wycena" else "brak ceny za jednostkę (pole Kwota)"
    if w["rodzaj"] == "Wycena":
        if not w["jedn"]:
            return "wycena bez jednostki – wpisz Jedn."
        if not w["opis"]:
            return "wycena bez nazwy (Wydatek)"
        if w["cena_podana"] == "Netto" and w["vat"] is None:
            return "cena netto bez stawki – wpisz VAT %"
        if w["lp"] == ZASTEPCZA:
            w["lp"] = ""
        return ""
    if not w["lp"] or w["lp"] == ZASTEPCZA:
        return "brak pozycji – wybierz z listy Pozycja"
    if w["typ"] == "Materiał" and not w["ilosc"] and "02" <= w["lp"][:2] <= "08":
        return "materiał stanu zero bez ilości – wpisz Ilość i Jedn."
    return ""


def oznacz(k: dict, id_: str, stan: str, wiersz=None, blad: str = ""):
    wl = {"Arkusz": {"select": {"name": stan}},
          "Błąd": {"rich_text": [{"type": "text", "text": {"content": blad[:300]}}] if blad else []}}
    if wiersz:
        wl["Wiersz arkusza"] = {"number": wiersz}
    W.zadanie_http("PATCH", f"{W.NOTION_API}/v1/pages/{id_}", naglowki(k), {"properties": wl})


# ---------------------------------------------------------------- polecenia

def sync(k: dict, proba: bool) -> tuple:
    """→ (liczniki, błędy krytyczne). Błąd pojedynczego wiersza trafia do Notion, nie przerywa reszty."""
    wymagaj(k, "token") if proba else wymagaj(k, "token", "url", "sekret")
    wiersze = [na_wiersz(s) for s in kolejka(k)]
    licz = {"w_kolejce": len(wiersze), "dopisane": 0, "poprawione": 0, "wyceny": 0, "bledy": 0, "czekaja": 0}
    bledy = []
    do_wyslania = []
    for w in wiersze:
        b = blad_lokalny(w)
        if b:
            licz["bledy"] += 1
            if proba:
                print(f"  ✗ {w['id'][:8]} {w['lp'] or '–'}: {b}")
            else:
                oznacz(k, w["id"], BLAD, blad=b)
        else:
            do_wyslania.append(w)
    if proba:
        for w in do_wyslania:
            print(f"  → {w['id'][:8]} {w['rodzaj']} {w['data']} poz. {w['lp'] or '–'} {w['typ'] or w['status_wyceny'] or ''} – wysłałbym")
        return licz, bledy
    if any(w["rodzaj"] == "Wycena" for w in do_wyslania):
        ping = arkusz(k, "ping")
        wersja = ping.get("wersja") or 1
        if wersja < WERSJA_WYCEN or not ping.get("cennik_ok"):
            czekaja = [w for w in do_wyslania if w["rodzaj"] == "Wycena"]
            do_wyslania = [w for w in do_wyslania if w["rodzaj"] != "Wycena"]
            licz["czekaja"] = len(czekaja)
            powod = (f"arkusz ma kod w wersji {wersja} – wklej nowy kod i zrób nową wersję wdrożenia"
                     if wersja < WERSJA_WYCEN else "Cennik w starym układzie – najpierw zmiana układu (migruj)")
            bledy.append(f"{len(czekaja)} wycen czeka: {powod} (docs/wydatki-arkusz.md)")
    po_id = {w["id"]: w for w in do_wyslania}
    mapa = None
    for i in range(0, len(do_wyslania), PACZKA):
        paczka = do_wyslania[i:i + PACZKA]
        try:
            wyniki = arkusz(k, "dopisz", wiersze=paczka)["wyniki"]
        except BladArkusza as e:
            bledy.append(f"arkusz: {e}")
            break
        for r in wyniki:
            if r.get("ok"):
                if r.get("arkusz") == "Cennik":
                    licz["wyceny"] += 1
                elif r.get("juz"):
                    # strona była już w arkuszu i wróciła do kolejki = korekta (np. „Do zapłaty” → „Zrealizowane”)
                    try:
                        if mapa is None:
                            mapa = {p["lp"]: p for p in arkusz(k, "pozycje")["pozycje"]}
                        blad = popraw_wiersz(k, po_id[r["id"]], r["wiersz"], mapa)
                    except BladArkusza as e:
                        bledy.append(f"korekta wiersza {r.get('wiersz')}: {e} – strona zostaje w kolejce")
                        continue
                    if blad:
                        licz["bledy"] += 1
                        oznacz(k, r["id"], BLAD, wiersz=r.get("wiersz"), blad=blad)
                        continue
                    licz["poprawione"] += 1
                else:
                    licz["dopisane"] += 1
                oznacz(k, r["id"], W_ARKUSZU, wiersz=r.get("wiersz"))
            else:
                licz["bledy"] += 1
                oznacz(k, r["id"], BLAD, blad=str(r.get("blad") or "odrzucone przez arkusz"))
    return licz, bledy


def popraw_wiersz(k: dict, w: dict, wiersz: int, mapa: dict) -> str:
    """Nadpisuje pola wpisywane (A:H, J:M) wiersza Wydatków danymi strony Notion – formuły I i N oraz Źródło zostają.
    Zwraca opis błędu albo ''."""
    p = mapa.get(w["lp"])
    if not p:
        return f"pozycja {w['lp']} nie istnieje w Kosztorysie"
    a_h = [[w["data"], w["status"], w["kwota"], p["etap"], p["klucz"], w["typ"] or "",
            "" if w["ilosc"] is None else w["ilosc"], w["jedn"] or ""]]
    j_m = [[w["sposob"] or "", w["opis"] or "", w["dostawca"] or "", w["notatki"] or ""]]
    arkusz(k, "zmien", operacje=[{"op": "zakres", "arkusz": "Wydatki", "a1": f"A{wiersz}:H{wiersz}", "wartosci": a_h},
                                  {"op": "zakres", "arkusz": "Wydatki", "a1": f"J{wiersz}:M{wiersz}", "wartosci": j_m}])
    return ""


def wycofaj(k: dict, ids: list) -> dict:
    """Czyści wiersze tych stron w arkuszu (Wydatki i Cennik) i ustawia w Notion Arkusz = „Nie wysyłać”."""
    wymagaj(k, "token", "url", "sekret")
    ids = [i.strip() for i in ids if i.strip()]
    wyniki = arkusz(k, "usun", ids=ids)["wyniki"]
    licz = {"stron": len(ids), "wiersze_wydatkow": 0, "wiersze_cennika": 0}
    for r in wyniki:
        licz["wiersze_wydatkow"] += len(r.get("wydatki") or [])
        licz["wiersze_cennika"] += len(r.get("cennik") or [])
        W.zadanie_http("PATCH", f"{W.NOTION_API}/v1/pages/{r['id']}", naglowki(k),
                       {"properties": {"Arkusz": {"select": {"name": "Nie wysyłać"}}, "Wiersz arkusza": {"number": None}}})
    return licz


def migruj(k: dict, plik_zmian: Path) -> dict:
    """Plik zmian: {"opis": "...", "operacje": [...]}. Operacje idą paczkami (limit czasu Apps Script); cofanie zmiany –
    Plik → Historia wersji w arkuszu."""
    wymagaj(k, "url", "sekret")
    operacje = json.loads(plik_zmian.read_text(encoding="utf-8"))["operacje"]
    wykonane = 0
    for i in range(0, len(operacje), 30):
        wykonane += arkusz(k, "zmien", operacje=operacje[i:i + 30])["wykonane"]
    return {"operacje": wykonane, "z": len(operacje)}


def nazwa_opcji(p: dict) -> str:
    """Opcja Notion: bez przecinków (zakazane w nazwach opcji), do 100 znaków; skrypt czyta z niej tylko numer."""
    return re.sub(r"\s+", " ", p["klucz"].replace(",", ";")).strip()[:100]


def pozycje(k: dict) -> dict:
    wymagaj(k, "token", "url", "sekret")
    lista = arkusz(k, "pozycje")["pozycje"]
    zrodlo = W.zadanie_http("GET", f"{W.NOTION_API}/v1/data_sources/{ZRODLO}", naglowki(k))
    obecne = (((zrodlo.get("properties") or {}).get("Pozycja") or {}).get("select") or {}).get("options") or []
    po_numerze = {numer_pozycji(o["name"]): o for o in obecne}
    opcje, nowe = [], 0
    for p in lista:
        lp = numer_pozycji(p["lp"])
        if not lp:
            continue
        stara = po_numerze.pop(lp, None)
        if stara:
            opcje.append({"id": stara["id"], "name": stara["name"]})   # zostaje z nazwą sprzed zmiany – wybrane wartości w wierszach się nie psują
        else:
            opcje.append({"name": nazwa_opcji(p), "color": "default"})
            nowe += 1
    # opcje spoza arkusza zostają (mogą być wybrane w starych wierszach) – poza zaślepką
    opcje += [{"id": o["id"], "name": o["name"]} for lp, o in po_numerze.items() if lp and lp != ZASTEPCZA]
    W.zadanie_http("PATCH", f"{W.NOTION_API}/v1/data_sources/{ZRODLO}", naglowki(k),
                   {"properties": {"Pozycja": {"select": {"options": opcje}}}})
    return {"pozycje": len(lista), "nowe_opcje": nowe}


def pobierz(k: dict) -> Path:
    wymagaj(k, "url", "sekret")
    wynik = arkusz(k, "dane")
    cel = W.HUB / "Koszty" / PLIK_KOPII
    tymczasowy = cel.with_suffix(".tmp")
    tymczasowy.write_text(json.dumps({"nazwa": wynik.get("nazwa"), "pobrano": time.strftime("%Y-%m-%d %H:%M"),
                                      "arkusze": wynik["arkusze"]}, ensure_ascii=False), encoding="utf-8")
    tymczasowy.replace(cel)
    return cel


def sprawdz(k: dict) -> list:
    bledy = []
    for pole, nazwa in (("token", "NOTION_TOKEN"), ("url", "ARKUSZ_URL"), ("sekret", "ARKUSZ_SEKRET")):
        print(f"{nazwa}: {'jest' if k.get(pole) else 'BRAK'}")
        if not k.get(pole):
            bledy.append(f"brak {nazwa} w .dom/sekrety.env")
    if k.get("token"):
        try:
            print(f"baza 💸 Wydatki: dostęp OK, w kolejce {len(kolejka(k))}")
        except (W.BladHttp, W.BladSieci) as e:
            bledy.append("baza 💸 Wydatki: " + W.tekst_bledu(e, k["sekrety"]))
    if k.get("url") and k.get("sekret"):
        try:
            p = arkusz(k, "ping")
            print(f"arkusz: OK („{p.get('arkusz')}”, wierszy z kwotą: {p.get('wydatki')}, kod w wersji {p.get('wersja') or 1},"
                  f" Cennik {'w nowym układzie' if p.get('cennik_ok') else 'w starym układzie'})")
        except BladArkusza as e:
            bledy.append(f"arkusz: {e}")
    return bledy


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("polecenie", choices=["sync", "pozycje", "pobierz", "wycofaj", "sprawdz", "kod", "migruj"])
    ap.add_argument("ids", nargs="*", help="wycofaj: id stron Notion; migruj: plik zmian JSON")
    ap.add_argument("--proba", action="store_true", help="sync: tylko pokaż, co poszłoby do arkusza (bez zapisu)")
    ap.add_argument("--cicho", action="store_true", help="jedna linia wyniku (dla automatów)")
    a = ap.parse_args(argv)
    if a.polecenie == "kod":
        m = re.search(r"```javascript\n(.*?)```", DOKUMENTACJA.read_text(encoding="utf-8"), re.S)
        if not m:
            print(f"  ✗ brak bloku kodu w {DOKUMENTACJA.name}", file=sys.stderr)
            return 1
        sys.stdout.write(m.group(1))
        return 0
    if a.polecenie in ("wycofaj", "migruj") and not a.ids:
        ap.error(f"{a.polecenie}: brak argumentu (id stron / plik zmian)")
    k = konfiguracja()
    t0 = time.monotonic()
    bledy = []
    try:
        if a.polecenie == "sprawdz":
            bledy = sprawdz(k)
            linia = "sprawdz: OK" if not bledy else "sprawdz: są problemy"
        elif a.polecenie == "sync":
            licz, bledy = sync(k, a.proba)
            linia = ("sync" + (" (próba)" if a.proba else "") + ": " +
                     ", ".join(f"{n} {v}" for n, v in licz.items()))
        elif a.polecenie == "wycofaj":
            w = wycofaj(k, a.ids)
            linia = "wycofaj: " + ", ".join(f"{n} {v}" for n, v in w.items())
        elif a.polecenie == "migruj":
            w = migruj(k, Path(a.ids[0]))
            linia = f"migruj: wykonano {w['operacje']} z {w['z']} operacji"
        elif a.polecenie == "pozycje":
            w = pozycje(k)
            linia = f"pozycje: {w['pozycje']} w arkuszu, nowe opcje w Notion {w['nowe_opcje']}"
        else:
            cel = pobierz(k)
            linia = f"pobierz: zapisano {cel.name} ({cel.stat().st_size // 1024} KB)"
    except BladKonfiguracji as e:
        print(f"[wydatki] nieskonfigurowane – {e} (docs/wydatki-arkusz.md)")
        return 2
    except BladArkusza as e:
        bledy.append(f"arkusz: {e}")
        linia = a.polecenie + ": przerwane"
    except (W.BladHttp, W.BladSieci) as e:
        bledy.append("Notion: " + W.tekst_bledu(e, k["sekrety"]))
        linia = a.polecenie + ": przerwane"
    print(f"[wydatki] {linia} · {time.monotonic() - t0:.0f} s")
    for b in bledy:
        print(f"  ✗ {b}", file=sys.stderr if a.cicho else sys.stdout)
    return 1 if bledy else 0


if __name__ == "__main__":
    sys.exit(main())
