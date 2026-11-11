#!/usr/bin/env python3
"""Teczka etapu / transzy do banku (POM-4): składa w jednym folderze dokumenty etapu i wskazuje braki.

    python3 tools/teczka.py zbierz --etap "<Etap>" --od RRRR-MM-DD --do RRRR-MM-DD [opcje]          # na sucho
    python3 tools/teczka.py zbierz --etap "<Etap>" --od … --do … --wykonaj                          # składa folder

Okres (--od, --do) to daty pierwszego i ostatniego kroku etapu z Harmonogramu – podaje je asystent, skrypt nie czyta Notion.
Źródła w folderze budowy (DOM_HUB), wybór wg układu folderów (docs/zdjecia-i-kopia.md):
  Umowy/Protokoły/       protokoły – data w nazwie od --od do --do + --zapas dni (odbiór bywa po ostatnim kroku)
  Faktury/RRRR/          faktury – data w nazwie w okresie
  Dziennik budowy KB/    wpisy kierownika – data w nazwie w okresie
  Dostawy/<Etap>/        WZ, deklaracje, karty produktów – cały folder etapu
  --dodaj ŚCIEŻKA        dowolny plik z folderu budowy (np. skan wyceny, umowa) – do działu „Dodatkowe”
Plik bez daty w nazwie nie trafia do teczki – skrypt nie zgaduje, wypisuje go do sprawdzenia.
Zdjęcia nie są kopiowane (źródłem jest Dysk, na Macu brak miejsca): do spisu idą linki folderów (--zdjecia ETYKIETA=ADRES).
Wynik: <folder budowy>/Teczki/<Etap>/RRRR-MM-DD[_n]/ z działami 1–5 i SPIS.md (składniki, braki, do sprawdzenia).
Nigdy nie nadpisuje i nie kasuje: kolejna teczka tego samego dnia dostaje _2, _3; pliki są kopiowane, źródła zostają.
Lista składników i uwagi o wymaganiach banku: plugins/dom-budowa/skills/etap/references/teczka.md.
"""
import argparse
import os
import re
import shutil
import sys
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kopia import POMIJANE  # noqa: E402  (te same pliki ukryte, tymczasowe i blokady programów biurowych)

REPO = Path(__file__).resolve().parent.parent
HUB = Path(os.environ.get("DOM_HUB") or REPO.parent.parent).expanduser().resolve()
KORZEN_TECZEK = "Teczki"
DATA_W_NAZWIE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
ZAPAS_PROTOKOLU = 14
DZIALY = [  # klucz, folder w teczce, tytuł w spisie
    ("protokoly", "1 Protokoły", "Protokoły odbioru i prób"),
    ("faktury", "2 Faktury", "Faktury"),
    ("kb", "3 Wpisy kierownika", "Wpisy kierownika w dzienniku budowy"),
    ("dostawy", "4 Dostawy", "Dostawy: WZ, deklaracje, karty produktów"),
    ("dodatkowe", "5 Dodatkowe", "Dodatkowe (wskazane ręcznie)"),
]
TYTULY = {k: t for k, _, t in DZIALY}


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def data_z_nazwy(nazwa: str):
    """Data RRRR-MM-DD z początku nazwy pliku (także z `~` – data wg wgrania) albo None."""
    m = DATA_W_NAZWIE.match(nfc(nazwa))
    if not m:
        return None
    try:
        return date.fromisoformat(m.group(1))
    except ValueError:
        return None


def data_arg(tekst: str) -> date:
    try:
        return date.fromisoformat(tekst)
    except ValueError:
        raise argparse.ArgumentTypeError(f"data „{tekst}” – oczekiwano RRRR-MM-DD")


def podfolder(baza: Path, sciezka: str):
    """Katalog `sciezka` pod `baza` – nazwy porównywane po normalizacji (macOS zwraca NFD); brak → None."""
    p = baza
    for czesc in sciezka.split("/"):
        if not p.is_dir():
            return None
        trafione = [d for d in p.iterdir() if d.is_dir() and nfc(d.name) == nfc(czesc)]
        if not trafione:
            return None
        p = trafione[0]
    return p


def pliki_pod(katalog: Path):
    """Wszystkie zwykłe pliki pod katalogiem (bez ukrytych i tymczasowych), posortowane po nazwie."""
    out = []
    for korzen, katalogi, pliki in os.walk(katalog):
        katalogi[:] = sorted(d for d in katalogi if not POMIJANE.search(d))
        out += [Path(korzen) / n for n in sorted(pliki) if not POMIJANE.search(n)]
    return sorted(out, key=lambda p: nfc(p.name))


def wg_dat(pliki, od: date, do: date):
    """(w okresie, bez daty w nazwie); pliki spoza okresu są pomijane."""
    wybrane, bez_daty = [], []
    for p in pliki:
        d = data_z_nazwy(p.name)
        if d is None:
            bez_daty.append(p)
        elif od <= d <= do:
            wybrane.append(p)
    return wybrane, bez_daty


def zbierz(hub: Path, etap: str, od: date, do: date, zapas: int = ZAPAS_PROTOKOLU, dodaj=(), zdjecia=()) -> dict:
    """Wybiera składniki teczki. Nic nie zapisuje. Zwraca dane do spisu i raportu."""
    hub = hub.resolve()
    if od > do:
        raise ValueError("--od jest późniejsze niż --do")
    skladniki = {k: [] for k, _, _ in DZIALY}
    bez_daty, braki, uwagi = [], [], []

    kat = podfolder(hub, "Umowy/Protokoły")
    if kat:
        skladniki["protokoly"], nd = wg_dat(pliki_pod(kat), od, do + timedelta(days=zapas))
        bez_daty += nd
    if not skladniki["protokoly"]:
        braki.append("BRAK protokołu odbioru w okresie – bez niego nie ma podstawy do wniosku o transzę ani do płatności "
                     "dla ekipy (etap C, koszty D)")

    kat = podfolder(hub, "Faktury")
    if kat:
        skladniki["faktury"], nd = wg_dat(pliki_pod(kat), od, do)
        bez_daty += nd
    if not skladniki["faktury"]:
        braki.append("brak faktur z okresu (data w nazwie pliku) – sprawdź Faktury/RRRR/ i Wydatki w arkuszu")

    kat = podfolder(hub, "Dziennik budowy KB")
    if kat:
        skladniki["kb"], nd = wg_dat(pliki_pod(kat), od, do)
        bez_daty += nd
    if not skladniki["kb"]:
        braki.append("brak wpisu kierownika budowy z okresu – bank i odbiór zwykle go oczekują")

    kat = None
    dostawy = hub / "Dostawy"
    if dostawy.is_dir():
        wg_nazwy = [d for d in dostawy.iterdir() if d.is_dir() and nfc(d.name).casefold() == nfc(etap).casefold()]
        kat = wg_nazwy[0] if wg_nazwy else None
    if kat:
        skladniki["dostawy"] = pliki_pod(kat)
    if not skladniki["dostawy"]:
        braki.append(f"brak dokumentów dostaw w Dostawy/{etap}/ (WZ betonu, atesty stali, karty produktów)")

    for rel in dodaj:
        p = (hub / rel).resolve()
        if hub not in p.parents or not p.is_file():
            uwagi.append(f"--dodaj: „{rel}” – nie ma takiego pliku w folderze budowy (pominięto)")
        elif any(c.startswith(".") for c in Path(rel).parts) or Path(rel).parts[0] in ("AI",):
            uwagi.append(f"--dodaj: „{rel}” – plik ukryty albo z katalogu roboczego (pominięto)")
        else:
            skladniki["dodatkowe"].append(p)

    if not zdjecia:
        braki.append("brak linków do zdjęć (folder kroków i „przed zakryciem” na Dysku) – podaj --zdjecia ETYKIETA=ADRES")

    return {"etap": etap, "od": od, "do": do, "zapas": zapas, "skladniki": skladniki, "bez_daty": bez_daty,
            "braki": braki, "uwagi": uwagi, "zdjecia": list(zdjecia)}


def bezpieczna_nazwa(s: str) -> str:
    s = re.sub(r'[\\/:*?"<>|]+', "-", nfc(s)).strip(" .")
    return s or "etap"


def folder_teczki(hub: Path, etap: str, dzis: date) -> Path:
    """Nowy, nieistniejący folder Teczki/<Etap>/RRRR-MM-DD[_n] – istniejących nie ruszamy."""
    baza = hub / KORZEN_TECZEK / bezpieczna_nazwa(etap)
    p = baza / dzis.isoformat()
    n = 2
    while p.exists():
        p = baza / f"{dzis.isoformat()}_{n}"
        n += 1
    return p


def rel(hub: Path, p: Path) -> str:
    return nfc(p.relative_to(hub).as_posix())


def spis_md(hub: Path, w: dict, dzis: date, skopiowane: dict) -> str:
    """SPIS.md – składniki (nazwa w teczce ← źródło), zdjęcia, braki, do sprawdzenia."""
    L = [f"# Teczka etapu: {w['etap']}",
         "",
         f"- Okres (kroki etapu wg Harmonogramu): {w['od'].isoformat()} – {w['do'].isoformat()}",
         f"- Złożona: {dzis.isoformat()}",
         "- Wymagania banku (lista dokumentów, forma) – **do potwierdzenia z umową kredytową**; "
         "ta teczka to uniwersalny zestaw, nie gwarancja kompletu dla banku.",
         ""]
    for klucz, folder, tytul in DZIALY:
        pliki = skopiowane.get(klucz) or []
        L += [f"## {folder} – {tytul} ({len(pliki)})", ""]
        L += [f"- `{cel}` ← `{zrodlo}`" for cel, zrodlo in pliki] or ["- (brak)"]
        L.append("")
    L += ["## Zdjęcia (linki do folderów na Dysku, pliki nie są kopiowane)", ""]
    L += [f"- {z}" for z in w["zdjecia"]] or ["- (brak linków)"]
    L += ["", "## Braki", ""]
    L += [f"- ⚠ {b}" for b in w["braki"]] or ["- brak braków wykrytych przez skrypt (lista banku i tak do potwierdzenia)"]
    if w["bez_daty"] or w["uwagi"]:
        L += ["", "## Do sprawdzenia (nie trafiło do teczki)", ""]
        L += [f"- bez daty w nazwie: `{rel(hub, p)}`" for p in w["bez_daty"]]
        L += [f"- {u}" for u in w["uwagi"]]
    return "\n".join(L) + "\n"


def zloz(hub: Path, w: dict, dzis: date, wykonaj: bool) -> dict:
    """Kopiuje składniki do teczki (gdy `wykonaj`) i zwraca {folder, skopiowane}. Źródeł nie rusza."""
    hub = hub.resolve()
    cel = folder_teczki(hub, w["etap"], dzis)
    skopiowane = {k: [] for k, _, _ in DZIALY}
    for klucz, folder, _ in DZIALY:
        zajete = set()
        for zrodlo in w["skladniki"][klucz]:
            nazwa, n = nfc(zrodlo.name), 2
            while nazwa.casefold() in zajete:
                nazwa = f"{zrodlo.stem}_{n}{zrodlo.suffix}"
                n += 1
            zajete.add(nazwa.casefold())
            wpis = (f"{folder}/{nazwa}", rel(hub, zrodlo))
            skopiowane[klucz].append(wpis)
            if wykonaj:
                (cel / folder).mkdir(parents=True, exist_ok=True)
                kopia = cel / folder / nazwa
                shutil.copy2(zrodlo, kopia)
                if kopia.stat().st_size != zrodlo.stat().st_size:
                    raise OSError(f"kopia {wpis[0]} ma inny rozmiar niż źródło – przerwano")
    if wykonaj:
        cel.mkdir(parents=True, exist_ok=True)
        (cel / "SPIS.md").write_text(spis_md(hub, w, dzis, skopiowane), encoding="utf-8")
    return {"folder": cel, "skopiowane": skopiowane}


def raport(hub: Path, w: dict, z: dict, wykonaj: bool) -> str:
    L = [f"Teczka etapu „{w['etap']}”, okres {w['od']} – {w['do']}" + ("" if wykonaj else "  [NA SUCHO – nic nie zapisano]")]
    for klucz, _, _ in DZIALY:
        pliki = z["skopiowane"][klucz]
        L.append(f"  {TYTULY[klucz]}: {len(pliki)}")
        L += [f"      {cel}  ←  {zrodlo}" for cel, zrodlo in pliki[:8]]
        if len(pliki) > 8:
            L.append(f"      … i {len(pliki) - 8} więcej")
    L += [f"  ⚠ {b}" for b in w["braki"]]
    L += [f"  ? bez daty w nazwie (nie wchodzi): {rel(hub, p)}" for p in w["bez_daty"]]
    L += [f"  ? {u}" for u in w["uwagi"]]
    cel = z["folder"].relative_to(hub).as_posix()
    L.append(f"  → {cel}/ (SPIS.md w środku)" if wykonaj else f"  → powstałaby: {cel}/  (dodaj --wykonaj)")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("zbierz", help="wybierz składniki etapu i (z --wykonaj) złóż folder teczki")
    a.add_argument("--etap", required=True)
    a.add_argument("--od", required=True, type=data_arg)
    a.add_argument("--do", required=True, type=data_arg)
    a.add_argument("--zapas", type=int, default=ZAPAS_PROTOKOLU, help="dni po --do, w których szukamy protokołu (14)")
    a.add_argument("--dodaj", action="append", default=[], metavar="ŚCIEŻKA", help="plik z folderu budowy do działu 5")
    a.add_argument("--zdjecia", action="append", default=[], metavar="ETYKIETA=ADRES", help="link folderu zdjęć do spisu")
    a.add_argument("--wykonaj", action="store_true")
    arg = ap.parse_args(argv)
    bledy = []
    try:
        w = zbierz(HUB, arg.etap, arg.od, arg.do, arg.zapas, arg.dodaj, arg.zdjecia)
        z = zloz(HUB, w, datetime.now().date(), arg.wykonaj)
        print(raport(HUB, w, z, arg.wykonaj))
    except (ValueError, OSError) as e:
        bledy.append(str(e))
    for b in bledy:
        print(f"✗ {b}")
    return 1 if bledy else 0


if __name__ == "__main__":
    sys.exit(main())
