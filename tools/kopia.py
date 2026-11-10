#!/usr/bin/env python3
"""Kopia dokumentów budowy Mac → Dysk Google (POM-1, etap E). Nic nie kasuje, nic nie nadpisuje.

    python3 tools/kopia.py stan [--cicho]        # tryb (aplikacja / paczka), zmiany od ostatniej potwierdzonej kopii
    python3 tools/kopia.py paczka [--wykonaj]    # tryb paczki: <hub>/_Na Dysk/RRRR-MM-DD/ + SPIS.txt (domyślnie na sucho)
    python3 tools/kopia.py wgrane [RRRR-MM-DD]   # inwestor wgrał paczkę → stan potwierdzony
    python3 tools/kopia.py aplikacja [--wykonaj] # tryb aplikacji: kopiuje zmiany do lokalnego folderu Dysku
    python3 tools/kopia.py sprawdz-dysk <lista.json>   # lista z konektora (nazwy, ścieżki) → czy na Dysku nie ma .dom/AI/sekretów

Foldery kopiowane (lista dozwolona): DOZWOLONE niżej. Nigdy: `.dom`, `AI`, `Wiedza*`, `_Przychodzące`, `_Do claude.ai`,
`_Na Dysk`, `Zdjęcia` (zdjęcia mają źródło na Dysku), pliki ukryte, tymczasowe i blokady programów biurowych.
Stan: `<hub>/.dom/kopia/stan.json` – potwierdzone pliki (ścieżka, rozmiar, sha256) i paczki czekające na wgranie.
Paczka niewgrana → następna zawiera też jej zmiany (porównanie zawsze z ostatnim potwierdzonym stanem).
Tryb wykrywany sam: lokalny folder Dysku w `~/Library/CloudStorage/GoogleDrive-*/Mój dysk|My Drive/Dom`
albo zmienna DYSK_DOM; brak → paczka. Pełny opis: docs/zdjecia-i-kopia.md.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HUB = Path(os.environ.get("DOM_HUB") or REPO.parent.parent).expanduser().resolve()
STAN_DIR = Path(os.environ.get("KOPIA_DANE") or HUB / ".dom" / "kopia")
DOZWOLONE = ("Projekty", "Dokumenty", "Umowy", "Faktury", "Wyceny", "Materiały", "Koszty", "Media", "Dostawy",
             "Dziennik budowy KB")
NIGDY = (".dom", "AI", "Wiedza", "_Przychodzące", "_Do claude.ai", "_Na Dysk", "Zdjęcia", "_Archiwum", "_Kopie")
POMIJANE = re.compile(r"^(\.|~\$|\.~lock)|\.(tmp|part|crdownload|lock)$|^Thumbs\.db$|^Kosztorys_google\.json$", re.I)
# Kosztorys_google.json – kopia wartości żywego arkusza (wydatki.py pobierz), nadpisywana co wieczór; arkusz i tak jest na Dysku
ZAKAZANE_NA_DYSKU = re.compile(r"(^|/)(\.dom|AI|\.git)(/|$)|sekrety|\.env$|token", re.I)


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def dozwolony(rel: str) -> bool:
    """Ścieżka względem folderu budowy – czy wolno ją skopiować na Dysk."""
    czesci = nfc(rel).split("/")
    return (czesci[0] in DOZWOLONE
            and not any(POMIJANE.search(c) or c in NIGDY or c.startswith("Wiedza") for c in czesci))


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for kawalek in iter(lambda: f.read(1 << 20), b""):
            h.update(kawalek)
    return h.hexdigest()


def skanuj(hub: Path, poprzedni: dict = None) -> dict:
    """{ścieżka: {"rozmiar", "mtime", "sha256"}} dla dozwolonych folderów; sha liczony tylko dla zmienionych."""
    poprzedni, out = poprzedni or {}, {}
    for folder in DOZWOLONE:
        baza = hub / folder
        if not baza.is_dir():
            continue
        for korzen, katalogi, pliki in os.walk(baza):
            katalogi[:] = [d for d in katalogi if not POMIJANE.search(d) and d not in NIGDY]
            for n in pliki:
                p = Path(korzen) / n
                rel = nfc(p.relative_to(hub).as_posix())
                if not dozwolony(rel):
                    continue
                st = p.stat()
                stary = poprzedni.get(rel)
                if stary and stary.get("rozmiar") == st.st_size and stary.get("mtime") == int(st.st_mtime):
                    out[rel] = stary
                else:
                    out[rel] = {"rozmiar": st.st_size, "mtime": int(st.st_mtime), "sha256": sha(p)}
    return out


def roznice(potwierdzone: dict, teraz: dict) -> dict:
    """nowe / zmienione / przeniesione (po treści) / usunięte – względem potwierdzonego stanu."""
    po_tresci = {}
    for s, v in potwierdzone.items():
        po_tresci.setdefault(v.get("sha256"), []).append(s)
    nowe, zmienione, przeniesione = [], [], []
    for s, v in sorted(teraz.items()):
        stary = potwierdzone.get(s)
        if stary is None:
            skad = [x for x in po_tresci.get(v["sha256"], []) if x not in teraz]
            (przeniesione.append({"z": skad[0], "do": s}) if skad else nowe.append(s))
        elif stary.get("sha256") != v["sha256"]:
            zmienione.append(s)
    przeniesione_z = {p["z"] for p in przeniesione}
    usuniete = sorted(s for s in potwierdzone if s not in teraz and s not in przeniesione_z)
    return {"nowe": nowe, "zmienione": zmienione, "przeniesione": przeniesione, "usuniete": usuniete}


def wczytaj_stan() -> dict:
    p = STAN_DIR / "stan.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    stan = {"potwierdzone": {}, "potwierdzono": None, "paczki": []}
    for start in sorted(STAN_DIR.glob("paczka-*.json")):  # pierwsza paczka (10.11.2026) jako punkt wyjścia
        d = json.loads(start.read_text(encoding="utf-8"))
        for f in d.get("pliki") or []:
            stan["potwierdzone"][nfc(f["sciezka"])] = {"rozmiar": f["rozmiar"], "mtime": None, "sha256": f["sha256"]}
        stan["potwierdzono"] = d.get("utworzono")
    return stan


def zapisz_stan(stan: dict):
    STAN_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STAN_DIR / "stan.json.tmp"
    tmp.write_text(json.dumps(stan, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    tmp.replace(STAN_DIR / "stan.json")


def folder_dysku():
    env = os.environ.get("DYSK_DOM")
    if env:
        p = Path(env).expanduser()
        return p if p.is_dir() else None
    for konto in sorted((Path.home() / "Library" / "CloudStorage").glob("GoogleDrive-*")):
        for moj in ("Mój dysk", "My Drive"):
            p = konto / moj / "Dom"
            if p.is_dir():
                return p
    return None


def zbuduj_paczke(hub: Path, r: dict, teraz: dict, data: str, wykonaj: bool) -> dict:
    cel = hub / "_Na Dysk" / data
    pliki = r["nowe"] + r["zmienione"] + [p["do"] for p in r["przeniesione"]]
    spis = [f"Paczka kopii dokumentów {data} – wgraj CAŁY folder do Dom/_Kopie na Dysku.",
            f"Plików: {len(pliki)}, bajtów: {sum(teraz[s]['rozmiar'] for s in pliki)}", ""]
    spis += [f"NOWY       {s}" for s in r["nowe"]] + [f"ZMIENIONY  {s}" for s in r["zmienione"]]
    spis += [f"PRZENIESIONY {p['z']} → {p['do']}" for p in r["przeniesione"]]
    spis += [f"USUNIĘTY NA MACU (na Dysku do _Archiwum) {s}" for s in r["usuniete"]]
    if wykonaj and (pliki or r["usuniete"]):
        while cel.exists():
            cel = cel.with_name(cel.name + "-b")
        for s in pliki:
            dst = cel / s
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(hub / s, dst)
        cel.mkdir(parents=True, exist_ok=True)
        (cel / "SPIS.txt").write_text("\n".join(spis) + "\n", encoding="utf-8")
    return {"folder": str(cel.relative_to(hub)), "pliki": pliki, "spis": spis}


def kopiuj_do_aplikacji(hub: Path, dysk: Path, r: dict, wykonaj: bool, data: str) -> list:
    """Tryb aplikacji: nowe/zmienione → Dysk; poprzednia wersja i usunięte → _Archiwum/RRRR-MM-DD; nic nie kasuje."""
    log = []
    arch = dysk / "_Archiwum" / data
    for s in r["zmienione"] + r["usuniete"]:
        stary = dysk / s
        if stary.exists():
            log.append(f"archiwum: {s}")
            if wykonaj:
                (arch / s).parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(stary), str(arch / s))
    for p in r["przeniesione"]:
        z, do = dysk / p["z"], dysk / p["do"]
        log.append(f"przeniesiony: {p['z']} → {p['do']}")
        if wykonaj and z.exists() and not do.exists():
            do.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(z), str(do))
    for s in r["nowe"] + r["zmienione"] + [p["do"] for p in r["przeniesione"]]:
        do = dysk / s
        if do.exists() and s not in r["zmienione"]:
            continue
        log.append(f"kopia: {s}")
        if wykonaj:
            do.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(hub / s, do)
    return log


def tylko_na_dysku(dysk: Path, teraz: dict) -> list:
    out = []
    for folder in DOZWOLONE:
        b = dysk / folder
        if not b.is_dir():
            continue
        for p in b.rglob("*"):
            if p.is_file() and not POMIJANE.search(p.name):
                rel = nfc(p.relative_to(dysk).as_posix())
                if rel not in teraz:
                    out.append(rel)
    return sorted(out)


def sprawdz_liste(lista: list) -> list:
    """Ścieżki z listy konektora, które nie powinny być na Dysku."""
    return [x for x in lista if ZAKAZANE_NA_DYSKU.search(nfc(x if isinstance(x, str) else x.get("sciezka", "")))]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("stan")
    a.add_argument("--cicho", action="store_true")
    a = sub.add_parser("paczka")
    a.add_argument("--wykonaj", action="store_true")
    a = sub.add_parser("wgrane")
    a.add_argument("data", nargs="?")
    a = sub.add_parser("aplikacja")
    a.add_argument("--wykonaj", action="store_true")
    a = sub.add_parser("sprawdz-dysk")
    a.add_argument("lista")
    a = ap.parse_args(argv)
    data = datetime.now().strftime("%Y-%m-%d")
    stan = wczytaj_stan()

    if a.cmd == "sprawdz-dysk":
        zle = sprawdz_liste(json.loads(Path(a.lista).read_text(encoding="utf-8")))
        print("[kopia] na Dysku: " + ("✗ " + ", ".join(map(str, zle)) if zle else "brak .dom, AI i sekretów ✓"))
        return 1 if zle else 0

    teraz = skanuj(HUB, {**stan["potwierdzone"], **stan.get("ostatni_skan", {})})
    stan["ostatni_skan"] = teraz
    r = roznice({k: v for k, v in stan["potwierdzone"].items() if dozwolony(k)}, teraz)
    n = len(r["nowe"]) + len(r["zmienione"]) + len(r["przeniesione"]) + len(r["usuniete"])
    dysk = folder_dysku()

    if a.cmd == "stan":
        czeka = [p["data"] for p in stan.get("paczki", []) if not p.get("wgrana")]
        linia = (f"[kopia] tryb: {'aplikacja' if dysk else 'paczka'} · potwierdzona: {stan.get('potwierdzono') or 'nigdy'} · "
                 f"zmian od niej: {n} (nowe {len(r['nowe'])}, zmienione {len(r['zmienione'])}, "
                 f"przeniesione {len(r['przeniesione'])}, usunięte {len(r['usuniete'])})"
                 + (f" · paczki do wgrania: {', '.join(czeka)}" if czeka else ""))
        if not (a.cicho and n == 0 and not czeka):
            print(linia)
        zapisz_stan(stan)
        return 0
    if a.cmd == "paczka":
        if n == 0:
            print("[kopia] aktualna – brak zmian od ostatniej potwierdzonej kopii")
            zapisz_stan(stan)
            return 0
        p = zbuduj_paczke(HUB, r, teraz, data, a.wykonaj)
        print(("[kopia] paczka gotowa: " if a.wykonaj else "[kopia] PLAN paczki (na sucho): ") + p["folder"])
        print("\n".join("  " + x for x in p["spis"][1:]))
        if a.wykonaj:
            stan.setdefault("paczki", []).append({"data": data, "folder": p["folder"], "wgrana": False,
                                                  "pliki": {s: teraz[s] for s in teraz}})
        zapisz_stan(stan)
        return 0
    if a.cmd == "wgrane":
        czeka = [p for p in stan.get("paczki", []) if not p.get("wgrana") and (not a.data or p["data"] == a.data)]
        if not czeka:
            print("[kopia] brak paczki czekającej na wgranie")
            return 0
        ost = czeka[-1]
        for p in czeka:
            p["wgrana"] = True
        stan["potwierdzone"] = ost["pliki"]
        stan["potwierdzono"] = ost["data"]
        for p in stan["paczki"]:
            p.pop("pliki", None) if p.get("wgrana") else None
        zapisz_stan(stan)
        print(f"[kopia] potwierdzona kopia z {ost['data']} (folder {ost['folder']} na Macu można usunąć po sprawdzeniu)")
        return 0
    if a.cmd == "aplikacja":
        if not dysk:
            print("[kopia] brak lokalnego folderu Dysku – użyj trybu paczki (`kopia.py paczka`)")
            return 1
        log = kopiuj_do_aplikacji(HUB, dysk, r, a.wykonaj, data)
        for x in tylko_na_dysku(dysk, teraz):
            log.append(f"tylko na Dysku (pobierz na Maca ręcznie): {x}")
        print(("[kopia] wykonano:" if a.wykonaj else "[kopia] PLAN (na sucho):") + f" {len(log)} pozycji")
        print("\n".join("  " + x for x in log))
        if a.wykonaj:
            stan["potwierdzone"], stan["potwierdzono"] = teraz, data
        zapisz_stan(stan)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
