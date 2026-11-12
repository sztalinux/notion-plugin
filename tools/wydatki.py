#!/usr/bin/env python3
"""Wydatki z Notion do arkusza Google „Kosztorys” – bez AI, na Macu (launchd przez automaty/przeglad.py).

    python3 tools/wydatki.py sync [--proba] [--cicho]   # wiersze „Do arkusza” (i z pustym Arkusz) → Wydatki / Cennik
    python3 tools/wydatki.py pozycje [--cicho]          # lista pozycji z arkusza Kosztorys → opcje pola Pozycja w Notion
    python3 tools/wydatki.py pobierz [--cicho] [--gdy-starsza H]   # wartości arkusza (JSON) do <hub>/Koszty/Kosztorys_google.json
    python3 tools/wydatki.py wycofaj <id strony> [...]  # usuwa wydatek z arkusza (i Cennika), w Notion „Nie wysyłać”
    python3 tools/wydatki.py sprawdz                    # konfiguracja, dostęp do bazy i do arkusza
    python3 tools/wydatki.py kod | LANG=en_US.UTF-8 pbcopy             # kod Apps Script do schowka (z docs/wydatki-arkusz.md)
    python3 tools/wydatki.py migruj <zmiany.json>        # zmiana układu na arkuszu (cofanie: Plik → Historia wersji)

Przepływ: przebieg Dziennika (agent) albo inwestor dodaje w Notion wiersz z Arkusz = „Do arkusza”; `sync` wysyła takie
wiersze do aplikacji Apps Script przypiętej do arkusza (kod i instrukcja: docs/wydatki-arkusz.md), a ta dopisuje je
w pierwszym wolnym wierszu arkusza Wydatki (bez nadpisywania kolumn z formułami). Wynik wraca do Notion: „W arkuszu”
z numerem wiersza albo „Błąd” z powodem. Ponowne wysłanie tej samej strony nie dubluje wiersza (kolumna Źródło
= notion:<id strony>). Strona już dopisana, która wróci do kolejki (zmienione pola + Arkusz = „Do arkusza”), poprawia swój
wiersz (pola wpisywane A:H, J:M – np. „Do zapłaty” → „Zrealizowane”); korekta z Notion nadpisuje ręczne zmiany tego wiersza
w arkuszu. Rodzaj „Zwrot” (pieniądze oddane – różnica VAT, zwrot towaru) to wiersz Wydatków z kwotą ujemną i bez ilości
(kod Apps Script ≥ 4, inaczej czeka w kolejce); VAT % strony wydatku trafia do kolumny P (zapis akcją „zmien”).
Rodzaj „Wycena” (oferta dostawcy, cena za jednostkę w polu Kwota) idzie do arkusza Cennik;
ponowne wysłanie tej samej strony aktualizuje jej wiersz (np. Status wyceny = Wybrana). Rodzaj „Plan” (plan całej pozycji
brutto) nie idzie do Apps Script jako wiersz – `sync` wpisuje go w Kosztorys „Plan ręczny” (kolumna i wiersz po nagłówkach),
inny plan nadpisuje tylko strona, która go ustawiła, albo z „Nadpisz plan”. Każde wysłanie czyści pole Zgłoszono (pytanie
o błąd we Wpisach zakłada przebieg Claude, nie ten skrypt). Wyceny wymagają kodu Apps Script
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
LIMIT_ODCZYTU_S = 300       # „dane” (cały arkusz) – Google bywa wolny godzinami; Apps Script i tak kończy po 6 min
PIERWSZY_WIERSZ = 5         # pierwszy wiersz danych w zakładkach (nagłówki w wierszu 4) – jak w Apps Script
PACZKA = 25                 # wierszy w jednym żądaniu do arkusza
WERSJA_WYCEN = 2            # minimalna wersja kodu Apps Script, która zapisuje wyceny do Cennika
WERSJA_ZWROTOW = 4          # minimalna wersja kodu Apps Script, która przyjmuje kwotę ujemną (Rodzaj „Zwrot”)
ZWROT = "Zwrot"
KOL_VAT = "P"               # Wydatki: VAT % (wpisuje sync z pola VAT %); Q – kwota netto (formuła)
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

def arkusz(k: dict, akcja: str, limit: int = 0, **dane) -> dict:
    """POST do aplikacji Apps Script. Google odpowiada przekierowaniem 302 na wynik – domyślny urllib idzie za nim
    GET-em bez ciała, czyli tak, jak wymaga Apps Script; nagłówka Authorization nie ma, więc nic nie wycieka."""
    cialo = json.dumps(dict(dane, sekret=k["sekret"], akcja=akcja)).encode("utf-8")
    zadanie = urllib.request.Request(k["url"], data=cialo, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(zadanie, timeout=limit or LIMIT_ARKUSZA_S) as odp:
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
    """Strona Notion → wiersz do wysłania. Zwrot: kwota zawsze ujemna (w Notion wpisuje się ją dodatnio) i bez ilości –
    to jedyne miejsce zmiany znaku, więc dopisanie i korekta wiersza dostają tę samą wartość."""
    p = strona.get("properties") or {}
    data = ((p.get("Data") or {}).get("date") or {}).get("start") or ""
    wazna = ((p.get("Ważna do") or {}).get("date") or {}).get("start") or ""
    w = {
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
        "nadpisz": bool((p.get("Nadpisz plan") or {}).get("checkbox")),
        "wiersz_ark": (p.get("Wiersz arkusza") or {}).get("number"),
    }
    if w["rodzaj"] == ZWROT:
        if isinstance(w["kwota"], (int, float)):
            w["kwota"] = -abs(w["kwota"])
        w["ilosc"], w["jedn"] = None, ""
    return w


def blad_lokalny(w: dict) -> str:
    if w["rodzaj"] == "Plan":
        if not isinstance(w["kwota"], (int, float)) or w["kwota"] < 0:
            return "plan bez kwoty (pole Kwota, zł brutto za całą pozycję)"
        if not w["lp"] or w["lp"] == ZASTEPCZA:
            return "plan bez pozycji – wybierz z listy Pozycja"
        return ""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", w["data"]):
        return "brak daty"
    if not isinstance(w["kwota"], (int, float)) or (w["kwota"] >= 0 if w["rodzaj"] == ZWROT else w["kwota"] <= 0):
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
    if w["rodzaj"] != ZWROT and w["typ"] == "Materiał" and not (w["ilosc"] and w["jedn"]) and "02" <= w["lp"][:2] <= "08":
        return "materiał stanu zero bez ilości albo jednostki – wpisz Ilość i Jedn."
    return ""


def oznacz(k: dict, id_: str, stan: str, wiersz=None, blad: str = ""):
    wl = {"Arkusz": {"select": {"name": stan}},
          "Błąd": {"rich_text": [{"type": "text", "text": {"content": blad[:300]}}] if blad else []},
          "Zgłoszono": {"date": None}}   # nowy wynik = nowe zgłoszenie we Wpisach, jeśli znów błąd
    if wiersz:
        wl["Wiersz arkusza"] = {"number": wiersz}
    W.zadanie_http("PATCH", f"{W.NOTION_API}/v1/pages/{id_}", naglowki(k), {"properties": wl})


# ---------------------------------------------------------------- polecenia

def sync(k: dict, proba: bool) -> tuple:
    """→ (liczniki, błędy krytyczne). Błąd pojedynczego wiersza trafia do Notion, nie przerywa reszty."""
    wymagaj(k, "token") if proba else wymagaj(k, "token", "url", "sekret")
    wiersze = [na_wiersz(s) for s in kolejka(k)]
    licz = {"w_kolejce": len(wiersze), "dopisane": 0, "poprawione": 0, "wyceny": 0, "plany": 0, "bledy": 0, "czekaja": 0}
    bledy = []
    do_wyslania = []
    for w in wiersze:
        b = blad_lokalny(w)
        if b:
            licz["bledy"] += 1
            if proba:
                print(f"  ✗ {w['id']} {w['lp'] or '–'}: {b}")   # pełne id – pierwsze znaki powtarzają się w całej przestrzeni Notion
            else:
                oznacz(k, w["id"], BLAD, blad=b)
        else:
            do_wyslania.append(w)
    if proba:
        for w in do_wyslania:
            print(f"  → {w['id']} {w['rodzaj']} {w['data']} poz. {w['lp'] or '–'} {w['typ'] or w['status_wyceny'] or ''} – wysłałbym")
        return licz, bledy
    plany = [w for w in do_wyslania if w["rodzaj"] == "Plan"]
    do_wyslania = [w for w in do_wyslania if w["rodzaj"] != "Plan"]   # Apps Script wziąłby je za wydatki
    if plany:
        try:
            wyslij_plany(k, plany, licz)
        except BladArkusza as e:
            bledy.append(f"plany: {e} – strony zostają w kolejce")
    ping = arkusz(k, "ping") if any(w["rodzaj"] in ("Wycena", ZWROT) for w in do_wyslania) else {}
    wersja = ping.get("wersja") or 1
    if any(w["rodzaj"] == ZWROT for w in do_wyslania) and wersja < WERSJA_ZWROTOW:
        # starszy kod odrzuciłby kwotę ujemną jako „brak kwoty” – zwroty czekają w kolejce na nowe wdrożenie
        czekaja = [w for w in do_wyslania if w["rodzaj"] == ZWROT]
        do_wyslania = [w for w in do_wyslania if w["rodzaj"] != ZWROT]
        licz["czekaja"] += len(czekaja)
        bledy.append(f"{len(czekaja)} zwrotów czeka: arkusz ma kod w wersji {wersja} – wklej nowy kod i zrób nową wersję "
                     "wdrożenia (docs/wydatki-arkusz.md, sekcja 7)")
    if any(w["rodzaj"] == "Wycena" for w in do_wyslania):
        if wersja < WERSJA_WYCEN or not ping.get("cennik_ok"):
            czekaja = [w for w in do_wyslania if w["rodzaj"] == "Wycena"]
            do_wyslania = [w for w in do_wyslania if w["rodzaj"] != "Wycena"]
            licz["czekaja"] += len(czekaja)
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
        nowe_z_vat = []   # nowy wiersz z VAT % – „W arkuszu” dopiero po zapisie kolumny P
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
                    if po_id[r["id"]]["vat"] is not None:
                        nowe_z_vat.append(r)
                        continue
                oznacz(k, r["id"], W_ARKUSZU, wiersz=r.get("wiersz"))
            else:
                licz["bledy"] += 1
                oznacz(k, r["id"], BLAD, blad=str(r.get("blad") or "odrzucone przez arkusz"))
        if nowe_z_vat:
            try:
                arkusz(k, "zmien", operacje=[op_vat(po_id[r["id"]], r["wiersz"]) for r in nowe_z_vat])
            except BladArkusza as e:
                # strony zostają „Do arkusza” – następny sync trafi w korektę wiersza i dopisze VAT
                bledy.append(f"VAT %: {e} – {len(nowe_z_vat)} stron zostaje w kolejce")
                continue
            for r in nowe_z_vat:
                oznacz(k, r["id"], W_ARKUSZU, wiersz=r.get("wiersz"))
    return licz, bledy


def op_vat(w: dict, wiersz: int) -> dict:
    """Wydatki kol. P = VAT % strony jako ułamek (23 → 0,23, format procentowy); brak stawki czyści komórkę."""
    v = w["vat"]
    return {"op": "zakres", "arkusz": "Wydatki", "a1": f"{KOL_VAT}{wiersz}",
            "wartosci": [["" if v is None else (v / 100 if v > 1 else v)]]}


def popraw_wiersz(k: dict, w: dict, wiersz: int, mapa: dict) -> str:
    """Nadpisuje pola wpisywane (A:H, J:M, P) wiersza Wydatków danymi strony Notion – formuły I, N, Q oraz Źródło
    zostają. Zwraca opis błędu albo ''."""
    p = mapa.get(w["lp"])
    if not p:
        return f"pozycja {w['lp']} nie istnieje w Kosztorysie"
    a_h = [[w["data"], w["status"], w["kwota"], p["etap"], p["klucz"], w["typ"] or "",
            "" if w["ilosc"] is None else w["ilosc"], w["jedn"] or ""]]
    j_m = [[w["sposob"] or "", w["opis"] or "", w["dostawca"] or "", w["notatki"] or ""]]
    arkusz(k, "zmien", operacje=[{"op": "zakres", "arkusz": "Wydatki", "a1": f"A{wiersz}:H{wiersz}", "wartosci": a_h},
                                  {"op": "zakres", "arkusz": "Wydatki", "a1": f"J{wiersz}:M{wiersz}", "wartosci": j_m},
                                  op_vat(w, wiersz)])
    return ""


def kolumna_a1(nr: int) -> str:
    """0 → A, 25 → Z, 26 → AA."""
    s = ""
    nr += 1
    while nr:
        nr, r = divmod(nr - 1, 26)
        s = chr(65 + r) + s
    return s


def mapa_planu(k: dict) -> dict:
    """Z żywego arkusza Kosztorys: kolumna „Plan ręczny…”, „Ilość plan × cena wybrana” (po nagłówkach, nie po literach)
    i wiersz każdej pozycji (Lp) z bieżącą wartością planu ręcznego."""
    dane = arkusz(k, "dane", limit=LIMIT_ODCZYTU_S)["arkusze"]["Kosztorys"]
    nag = [str(x).strip() for x in dane[PIERWSZY_WIERSZ - 2]]
    def kol(poczatek):
        return next((i for i, n in enumerate(nag) if n.startswith(poczatek)), None)
    k_plan, k_lp, k_oferta = kol("Plan ręczny"), kol("Lp"), kol("Ilość plan × cena")
    if k_plan is None or k_lp is None:
        raise BladArkusza("Kosztorys bez kolumny „Plan ręczny” albo „Lp” w wierszu nagłówków")
    pozycje_ = {}
    for nr, w in enumerate(dane[PIERWSZY_WIERSZ - 1:], start=PIERWSZY_WIERSZ):
        lp = str(w[k_lp] if k_lp < len(w) else "").strip()
        if lp:
            pozycje_[lp] = {"wiersz": nr, "plan": w[k_plan] if k_plan < len(w) else "",
                            "oferta": w[k_oferta] if k_oferta is not None and k_oferta < len(w) else ""}
    return {"kolumna": kolumna_a1(k_plan), "pozycje": pozycje_}


def liczba(x):
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def wyslij_plany(k: dict, plany: list, licz: dict):
    """Rodzaj „Plan” → komórka „Plan ręczny” pozycji w Kosztorysie. Pusta albo równa – zapis; inna wartość – tylko gdy ta
    strona już tę komórkę ustawiła (Wiersz arkusza) albo ma zaznaczone „Nadpisz plan”; inaczej Błąd z pytaniem."""
    m = mapa_planu(k)
    for w in plany:
        p = m["pozycje"].get(w["lp"])
        if not p:
            licz["bledy"] += 1
            oznacz(k, w["id"], BLAD, blad=f"pozycja {w['lp']} nie istnieje w Kosztorysie")
            continue
        obecny = liczba(p["plan"])
        wlasny = w["wiersz_ark"] == p["wiersz"]
        if obecny not in (None, 0) and obecny != w["kwota"] and not (wlasny or w["nadpisz"]):
            licz["bledy"] += 1
            oznacz(k, w["id"], BLAD, blad=f"pozycja {w['lp']} ma już inny plan ręczny – zaznacz „Nadpisz plan”, "
                                          "jeśli ten ma go zastąpić")
            continue
        if obecny != w["kwota"]:
            a1 = f"{m['kolumna']}{p['wiersz']}"
            arkusz(k, "zmien", operacje=[{"op": "zakres", "arkusz": "Kosztorys", "a1": a1, "wartosci": [[w["kwota"]]]}])
        uwaga = ("uwaga: pozycja ma wybraną ofertę – PLAN liczy się z oferty × ilość, plan ręczny jest zapasowy"
                 if (liczba(p["oferta"]) or 0) > 0 else "")
        licz["plany"] += 1
        oznacz(k, w["id"], W_ARKUSZU, wiersz=p["wiersz"], blad=uwaga)


def strona(k: dict, id_: str) -> dict:
    return W.zadanie_http("GET", f"{W.NOTION_API}/v1/pages/{id_}", naglowki(k))


def wycofaj(k: dict, ids: list) -> dict:
    """Czyści wiersze tych stron w arkuszu (Wydatki i Cennik) i ustawia w Notion Arkusz = „Nie wysyłać”."""
    wymagaj(k, "token", "url", "sekret")
    ids = [i.strip() for i in ids if i.strip()]
    licz = {"stron": len(ids), "wiersze_wydatkow": 0, "wiersze_cennika": 0, "plany": 0}
    plany = [w for w in (na_wiersz(strona(k, i)) for i in ids) if w["rodzaj"] == "Plan"]
    if plany:
        # plan wycofany = pusta komórka „Plan ręczny”, ale tylko gdy nadal stoi tam kwota z tej strony
        m = mapa_planu(k)
        for w in plany:
            p = m["pozycje"].get(w["lp"])
            if p and liczba(p["plan"]) == w["kwota"]:
                arkusz(k, "zmien", operacje=[{"op": "zakres", "arkusz": "Kosztorys",
                                              "a1": f"{m['kolumna']}{p['wiersz']}", "wartosci": [[""]]}])
                licz["plany"] += 1
        id_planow = {w["id"].replace("-", "") for w in plany}
        ids = [i for i in ids if i.replace("-", "") not in id_planow]
        for w in plany:
            W.zadanie_http("PATCH", f"{W.NOTION_API}/v1/pages/{w['id']}", naglowki(k),
                           {"properties": {"Arkusz": {"select": {"name": "Nie wysyłać"}}, "Wiersz arkusza": {"number": None}}})
    wyniki = arkusz(k, "usun", ids=ids)["wyniki"] if ids else []
    wiersze_vat = [n for r in wyniki for n in r.get("wydatki") or []]
    if wiersze_vat:   # kol. P wpisuje sync, nie Apps Script – czyści ją też ten skrypt
        arkusz(k, "zmien", operacje=[{"op": "zakres", "arkusz": "Wydatki", "a1": f"{KOL_VAT}{n}", "wartosci": [[""]]}
                                     for n in wiersze_vat])
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


def pobierz(k: dict, gdy_starsza_h: float = 0) -> Path:
    """Kopia wartości arkusza. gdy_starsza_h > 0 – tylko gdy kopia jest starsza (ponowienie po nieudanym odczycie
    wieczornym w szybkich przebiegach)."""
    cel = W.HUB / "Koszty" / PLIK_KOPII
    if gdy_starsza_h and cel.exists() and time.time() - cel.stat().st_mtime < gdy_starsza_h * 3600:
        return cel
    wymagaj(k, "url", "sekret")
    wynik = arkusz(k, "dane", limit=LIMIT_ODCZYTU_S)
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
    ap.add_argument("--gdy-starsza", type=float, default=0, metavar="H",
                    help="pobierz: tylko gdy kopia jest starsza niż H godzin")
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
            cel = pobierz(k, a.gdy_starsza)
            wiek_h = (time.time() - cel.stat().st_mtime) / 3600
            linia = (f"pobierz: zapisano {cel.name} ({cel.stat().st_size // 1024} KB)" if wiek_h < 0.1
                     else f"pobierz: kopia świeża ({wiek_h:.0f} h), pominięto")
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
