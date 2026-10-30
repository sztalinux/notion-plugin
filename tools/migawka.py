#!/usr/bin/env python3
"""Migawka Notatnika budowy i zadań (TASKS) dla czatu bez Notion: otwarte wpisy obu baz w jednym pliku Markdown,
zapisanym lokalnie (`.dom/wiedza/migawka.md` w hubie) i opublikowanym do prywatnego repo kopii (GITHUB_REPO)
obok indeksu wiedzy – czat pobiera go tą samą drogą co `wiedza.sqlite`. Tylko odczyt Notion (token integracji
NOTION_TOKEN z `.dom/sekrety.env`), nigdy zapis.

    python3 tools/migawka.py [--cicho] [--bez-publikacji] [--json]

Zasady: komunikaty niosą tylko liczby, nazwy pól i statusy HTTP – treść wpisów idzie wyłącznie do pliku migawki.
Baza nieudostępniona integracji (404) nie przerywa pracy: plik dostaje linię „niedostępna”, a stderr ostrzeżenie.
Wywołuje go przebieg godzinowy na Macu (skrypt poza repo) – ręcznie po zmianach w Notatniku, gdy telefon ma je widzieć od razu.
"""
import argparse
import base64
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wiedza as W  # noqa: E402 – wspólne HTTP, sekrety, GitHub

PLIK = "migawka.md"
PLIK_JSON = "migawka.json"
BAZY = {
    "notatnik": {
        "nazwa": "Notatnik budowy", "zrodlo": "7423414a-707b-415f-8751-c6ab7ebb6753",
        "filtr": {"and": [{"property": "Status", "select": {"does_not_equal": "Zrobione"}},
                          {"property": "Status", "select": {"does_not_equal": "Odrzucone"}}]},
        "sort": [{"property": "Etap", "direction": "ascending"}, {"property": "Typ", "direction": "ascending"}],
        "pola": ["Typ", "Status", "Priorytet", "Etap", "Branża", "Do kogo", "Kiedy", "Name", "Notatka", "Źródło"],
    },
    "zadania": {
        "nazwa": "Zadania (TASKS)", "zrodlo": "2a9f5982-09e7-81be-91e8-000b0e10a05e",
        "filtr": {"and": [{"property": "Status", "status": {"does_not_equal": "DONE"}},
                          {"property": "Status", "status": {"does_not_equal": "ARCHIVED"}}]},
        "sort": [{"property": "When", "direction": "ascending"}],
        "pola": ["Obszar", "Status", "Priority", "Kategoria", "When", "Kto", "Name", "Desc"],
    },
}
CZYTAJ = {"title": W.czytaj_tekst, "rich_text": W.czytaj_tekst, "select": W.czytaj_select, "status": W.czytaj_select,
          "multi_select": W.czytaj_multi, "date": W.czytaj_date, "checkbox": lambda w: "tak" if w.get("checkbox") else ""}


def pobierz(klucz: str, token: str) -> list:
    """Strony bazy po filtrze (stronicowanie); BladHttp 404 → None (baza nieudostępniona integracji)."""
    b = BAZY[klucz]
    url = f"{W.NOTION_API}/v1/data_sources/{b['zrodlo']}/query"
    naglowki = {"Authorization": "Bearer " + token, "Notion-Version": W.NOTION_WERSJA}
    cialo = {"page_size": 100, "filter": b["filtr"], "sorts": b["sort"]}
    strony = []
    while True:
        try:
            odp = W.zadanie_http("POST", url, naglowki, cialo)
        except W.BladHttp as e:
            if e.status == 404:
                return None
            raise
        strony += odp.get("results") or []
        if not odp.get("has_more") or not odp.get("next_cursor"):
            return strony
        cialo["start_cursor"] = odp["next_cursor"]


def wiersz(klucz: str, strona: dict) -> dict:
    wlasciwosci = strona.get("properties") or {}
    w = {}
    for pole in BAZY[klucz]["pola"]:
        p = wlasciwosci.get(pole)
        w[pole] = W.jedna_linia(CZYTAJ.get(p["type"], lambda x: "")(p)) if p else "–"
    w["url"] = strona.get("url") or ""
    w["zmieniono"] = strona.get("last_edited_time") or ""
    return w


def linia(klucz: str, w: dict) -> str:
    czesci = [w[p] if w[p] != "–" else "–" for p in BAZY[klucz]["pola"]]
    return " · ".join(czesci) + f" · {w['url'] or '–'}"


def markdown(dane: dict, kiedy: str) -> str:
    tekst = [f"# Migawka Notatnika i zadań · stan {W.lokalnie(kiedy)} (kopia tylko do odczytu; zapisy – przez Skrzynkę)", ""]
    for klucz, b in BAZY.items():
        wiersze = dane[klucz]
        if wiersze is None:
            tekst += [f"## {b['nazwa']}: niedostępna (baza nieudostępniona integracji Notion)", ""]
            continue
        tekst += [f"## {b['nazwa']} – otwarte ({len(wiersze)})", "Kolumny: " + " · ".join(b["pola"]) + " · link", ""]
        tekst += [linia(klucz, w) for w in wiersze] + [""]
    return "\n".join(tekst)


def opublikuj(tresc: bytes, sekrety: dict, cicho: bool, tresc_json: bytes = None) -> bool:
    """Publikuje migawkę .md (czat) i – gdy podano – migawka.json (tryb głęboki w GitHub Actions czyta Notatnik z niej)."""
    token, repo = sekrety.get("GITHUB_TOKEN_SYNC"), sekrety.get("GITHUB_REPO")
    if not token or not repo:
        W.ostrzez("brak GITHUB_TOKEN_SYNC albo GITHUB_REPO – publikacja pominięta")
        return False
    naglowki = {"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": W.GITHUB_WERSJA}
    ukryj = repo.split("/")
    try:
        if W.galaz_prywatnego_repo(repo, naglowki, None) is None:
            W.blad("GITHUB_REPO nie jest repo prywatnym – publikacja wstrzymana")
            return False
        ok, wyslane = True, []
        for nazwa, dane in ((PLIK, tresc), (PLIK_JSON, tresc_json)):
            if dane is None:
                continue
            sha_lokalny = W.git_blob_sha(dane)
            sha_zdalny = W.sha_na_githubie(repo, naglowki, nazwa, None)
            if sha_zdalny == sha_lokalny:
                continue
            if W.wyslij_plik(repo, naglowki, nazwa, base64.b64encode(dane).decode("ascii"), sha_lokalny, sha_zdalny,
                             f"migawka {W.lokalnie(W.teraz_iso())}", None):
                wyslane.append(f"{nazwa} {W.rozmiar_opis(len(dane))}")
            else:
                ok = False
        if not cicho:
            print("[migawka] publikacja: " + (", ".join("wysłano " + w for w in wyslane) if wyslane else "bez zmian"))
        return ok
    except (W.BladHttp, W.BladSieci) as e:
        W.blad(f"GitHub: {W.tekst_bledu(e, sekrety, ukryj)}")
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cicho", action="store_true", help="tylko błędy i ostrzeżenia")
    ap.add_argument("--bez-publikacji", action="store_true", help="tylko plik lokalny")
    ap.add_argument("--json", action="store_true", help="liczniki jako JSON")
    a = ap.parse_args(argv)
    start = time.monotonic()
    sekrety = W.wczytaj_sekrety(W.SEKRETY)
    token = sekrety.get("NOTION_TOKEN")
    if not token:
        W.blad(f"brak NOTION_TOKEN w .dom/{W.SEKRETY.name}")
        return 1
    if not W.KATALOG.is_dir():
        W.blad(f"brak katalogu {W.KATALOG} – uruchom najpierw wiedza.py sync")
        return 1
    dane, liczniki = {}, {}
    for klucz, b in BAZY.items():
        try:
            strony = pobierz(klucz, token)
        except (W.BladHttp, W.BladSieci) as e:
            W.blad(f"Notion, {b['nazwa']}: {W.tekst_bledu(e, sekrety)}")
            return 1
        if strony is None:
            W.ostrzez(f"{b['nazwa']}: 404 – udostępnij bazę integracji Notion (… → Connections); migawka bez niej")
            dane[klucz], liczniki[klucz] = None, None
            continue
        dane[klucz] = [wiersz(klucz, s) for s in strony]
        liczniki[klucz] = len(strony)
    kiedy = W.teraz_iso()
    tresc = markdown(dane, kiedy).encode("utf-8")
    plik = W.KATALOG / PLIK
    plik.write_bytes(tresc)
    plik.chmod(0o600)
    plik_json = W.KATALOG / PLIK_JSON
    tresc_json = json.dumps({"stan": kiedy, "liczniki": liczniki, "bazy": dane}, ensure_ascii=False).encode("utf-8")
    plik_json.write_bytes(tresc_json)
    plik_json.chmod(0o600)
    ok = True if a.bez_publikacji else opublikuj(tresc, sekrety, a.cicho, tresc_json)
    if a.json:
        W.wypisz_json({"stan": kiedy, "liczniki": liczniki, "znakow": len(tresc), "opublikowano": ok and not a.bez_publikacji})
    elif not a.cicho:
        opis = " · ".join(f"{BAZY[k]['nazwa']}: {'niedostępna' if n is None else n}" for k, n in liczniki.items())
        print(f"[migawka] {opis} · {W.rozmiar_opis(len(tresc))} · {time.monotonic() - start:.1f} s")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
