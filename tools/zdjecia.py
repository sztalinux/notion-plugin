#!/usr/bin/env python3
"""Zdjęcia i dokumenty z telefonu: rozkładanie skrzynki `Zdjęcia/_nowe` do folderów kroków (POM-1, etap C–D).

    python3 tools/zdjecia.py plan --lista <lista.json> [--teraz ISO] [--wyjscie plan.json] [--zablokuj]   # konektor: lista → plan (na sucho)
    python3 tools/zdjecia.py rozloz [--wykonaj]          # tryb lokalny: <hub>/Zdjęcia/_nowe → foldery kroków na Macu
    python3 tools/zdjecia.py zapisz-ruchy <plan.json> [--kto konektor] [--tylko id,id]   # dziennik ruchów po wykonaniu planu
    python3 tools/zdjecia.py odblokuj                    # zdejmij blokadę (porzucony przebieg albo plan bez „ok”)
    python3 tools/zdjecia.py cofnij [--wykonaj|--zrobione]   # plan odwrotny ostatniego niecofniętego przebiegu
    python3 tools/zdjecia.py slad <plan.json>             # ślad do Notion: dzień → krok → liczba, folder
    python3 tools/zdjecia.py wg-dni                       # Mac: Zdjęcia/_wg dni/RRRR-MM-DD/ z dowiązaniami
    python3 tools/zdjecia.py stan                         # kroki, ostatni przebieg, blokada, liczba ruchów

Reguły (pełny opis dla agentów: plugins/dom-budowa/skills/dziennik/references/zdjecia-i-kopia.md):
- Nic nie jest kasowane ani nadpisywane. Kolizja nazwy przy innej treści → dopisek `_2`; ta sama nazwa i rozmiar →
  duplikat do `_Archiwum/Duplikaty/`. Pusty folder po rozłożeniu → `_Archiwum/Puste foldery/`.
- Data zrobienia: EXIF (tylko lokalnie, `mdls`) → nazwa pliku z telefonu (PXL_ w UTC, IMG_/VID_/RRRRMMDD_ lokalnie) →
  data wgrania (`createdTime`, UTC → czas polski) ze znakiem `~` w prefiksie („data wg wgrania”).
- Plik zmieniony mniej niż 15 min temu albo folder z takim plikiem → następny przebieg (wgrywanie trwa).
- Folder w `_nowe`: nazwa → krok (numer albo słowa z nazwy kroku); słowa „przed zakryciem”, „z miarą”… → podfolder
  `przed zakryciem/`; słowa „faktura”, „WZ”, „dziennik KB”… → dokument. Niepewne → zostaje, pytanie 🔔.
- Luźne pliki: jeden krok w Dzienniku budowy tego dnia → ten krok; inaczej zostają z pytaniem.
- Ponowny przebieg nic nie zmienia (prefiks daty nie jest dokładany drugi raz).
- Dziennik ruchów (`ruchy.jsonl`): tryb lokalny dopisuje każdy ruch zaraz po wykonaniu (przerwany przebieg da się cofnąć);
  konektor – `zapisz-ruchy --tylko` (pusty folder razem z ostatnim swoim plikiem). Blokada: `rozloz` i `cofnij --wykonaj`
  (skrypt, 2 h) oraz `plan --zablokuj` przy planie z ruchami (konektor, 30 min, ponowny plan ją odświeża; zdejmuje ją
  `zapisz-ruchy` albo `odblokuj`) – skrypt i konektor nie rozkładają naraz.

Wejście planu (`--lista`, JSON): {"nowe": [{"id", "nazwa", "folder" ("" = luzem), "mime", "rozmiar", "utworzono",
"zmieniono", "zrobiono"?}], "istniejace": [{"folder": "<ścieżka od Dom>", "nazwa", "rozmiar"}]}. Kroki i dni:
`<hub>/.dom/zdjecia/kroki.json` = {"etap": "Stan zero", "kroki": [{"nazwa": "01 …", "folder": "Zdjęcia/Stan zero/01 …"}],
"tematy": ["Przyłącza"], "dni": {"RRRR-MM-DD": ["01 …"]}} – zapisuje go asystent z Harmonogramu i Dziennika budowy.
Tylko biblioteka standardowa Pythona 3.9; w repo żadnych nazw kroków ani identyfikatorów Dysku (te w `.dom/`).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    PL = ZoneInfo("Europe/Warsaw")
except Exception:  # pragma: no cover – brak bazy stref: przybliżenie CET
    PL = timezone(timedelta(hours=1))

import hub

REPO = Path(__file__).resolve().parent.parent
HUB = hub.folder_budowy(REPO)
DANE = Path(os.environ.get("ZDJECIA_DANE") or HUB / ".dom" / "zdjecia")
ZDJECIA, NOWE = "Zdjęcia", "_nowe"
PRZED = "przed zakryciem"
ARCH_DUP, ARCH_PUSTE = "_Archiwum/Duplikaty", "_Archiwum/Puste foldery"
SWIEZE_MIN = 15
BLOKADA_H = 2  # skrypt; blokada konektora (plan --zablokuj) – BLOKADA_KONEKTOR_MIN
BLOKADA_KONEKTOR_MIN = 30

SLOWA_PRZED = ("przed zakryciem", "z miara", "z miarka", "przed zalaniem", "przed zasypka", "przed betonowaniem")
DOKUMENTY = [  # (słowa w nazwie folderu, rodzaj, folder docelowy – {r} rok, {etap} etap)
    (("faktura", "faktury", "paragon", "rachunek", "korekta"), "faktura", "Faktury/{r}"),
    (("dziennik kb", "dziennik budowy", "wpis kierownika", "kb"), "dziennik KB", "Dziennik budowy KB"),
    (("protokol",), "protokół", "Umowy/Protokoły"),
    (("wz", "deklaracja", "deklaracje", "karta", "etykieta", "atest", "dostawa"), "dostawa", "Dostawy/{etap}"),
]
OBRAZ = re.compile(r"\.(jpe?g|heic|heif|png|webp|dng)$", re.I)
FILM = re.compile(r"\.(mp4|mov|3gp|m4v)$", re.I)
TYMCZASOWE = re.compile(r"^(\.|~\$|\.~lock)|\.(tmp|part|crdownload)$", re.I)
PREFIKS = re.compile(r"^(\d{4}-\d{2}-\d{2})(~?)_")
NAZWY_TELEFONU = [  # (wzorzec, strefa: "utc" | "lokalna")
    (re.compile(r"^PXL_(\d{8})_(\d{6})"), "utc"),
    (re.compile(r"^(?:IMG|VID|PANO|MVIMG)_(\d{8})_(\d{6})"), "lokalna"),
    (re.compile(r"^(?:Screenshot_)?(\d{8})[_-](\d{6})"), "lokalna"),
    (re.compile(r"(\d{4}-\d{2}-\d{2}) at (\d{2})\.(\d{2})\.(\d{2})"), "lokalna"),  # komunikatory
]


# ---------- tekst ----------

def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s or "")


def proste(s: str) -> str:
    """Do porównań: NFC, małe litery, bez polskich znaków i interpunkcji, pojedyncze spacje, bez spacji na końcach."""
    s = unicodedata.normalize("NFKD", nfc(s).replace("ł", "l").replace("Ł", "L"))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s)).strip()


def bezpieczna(s: str) -> str:
    """Nazwa folderu/pliku bez znaków niedozwolonych i spacji na końcach."""
    return re.sub(r"[\\/:*?\"<>|]", "-", nfc(s)).strip().rstrip(".")


def ma_slowo(tekst: str, slowa) -> bool:
    t = f" {proste(tekst)} "
    return any(f" {proste(w)} " in t for w in slowa)


# ---------- daty ----------

def _iso(s: str):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=PL)


def data_z_nazwy(nazwa: str):
    """Czas zrobienia z nazwy pliku z telefonu (czas polski) albo None."""
    for wz, strefa in NAZWY_TELEFONU:
        m = wz.search(nazwa)
        if not m:
            continue
        try:
            if len(m.groups()) == 4:
                d = datetime.strptime(f"{m.group(1)} {m.group(2)}{m.group(3)}{m.group(4)}", "%Y-%m-%d %H%M%S")
            else:
                d = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
        except ValueError:
            continue
        if not 2000 <= d.year <= 2100:
            continue
        return (d.replace(tzinfo=timezone.utc) if strefa == "utc" else d.replace(tzinfo=PL)).astimezone(PL)
    return None


def data_zrobienia(plik: dict):
    """(data RRRR-MM-DD, przybliżona?, źródło). Dzień zawsze wg czasu polskiego."""
    d = _iso(plik.get("zrobiono") or "")
    if d:
        return d.astimezone(PL).date().isoformat(), False, "exif"
    d = data_z_nazwy(nfc(plik.get("nazwa", "")))
    if d:
        return d.date().isoformat(), False, "nazwa"
    d = _iso(plik.get("utworzono") or "") or _iso(plik.get("zmieniono") or "")
    if d:
        return d.astimezone(PL).date().isoformat(), True, "wgranie"
    return None, True, "brak"


def nowa_nazwa(nazwa: str, data: str, przyblizona: bool) -> str:
    """Prefiks daty; plik z prefiksem zostaje, `~` poprawiany na dokładną datę, gdy ją znamy."""
    nazwa = bezpieczna(nazwa)
    m = PREFIKS.match(nazwa)
    if m:
        if m.group(2) and data and not przyblizona:
            return f"{data}_{nazwa[m.end():]}"
        return nazwa
    if not data:
        return nazwa
    return f"{data}{'~' if przyblizona else ''}_{nazwa}"


# ---------- dopasowanie do kroku ----------

def _rdzenie(s: str):
    return {w[:5] for w in proste(s).split() if len(w) >= 4 and not w.isdigit()}


DATA_NA_POCZATKU = re.compile(r"^\s*(?:krok\s*)?\d{1,2}[.\-/_]\d", re.I)  # „8.11 zbrojenie” = data, nie krok 8


def numer_kroku(s: str):
    if DATA_NA_POCZATKU.match(nfc(s)):
        return None
    m = re.match(r"^\s*(?:krok\s*)?0*(\d{1,2})\b", proste(s))
    return int(m.group(1)) if m else None


def _po_slowach(nazwa_folderu: str, kroki: list):
    """(krok | None, powód) – dopasowanie po rdzeniach słów z nazwy kroku."""
    slowa = _rdzenie(nazwa_folderu) - _rdzenie(" ".join(SLOWA_PRZED))
    if not slowa:
        return None, "brak słów do dopasowania"
    wyniki = sorted(((len(slowa & _rdzenie(k["nazwa"])), i) for i, k in enumerate(kroki)), reverse=True)
    if not wyniki or wyniki[0][0] == 0:
        return None, "żaden krok"
    if len(wyniki) > 1 and wyniki[1][0] == wyniki[0][0]:
        return None, "kilka kroków: " + ", ".join(kroki[i]["nazwa"] for s, i in wyniki if s == wyniki[0][0])
    return kroki[wyniki[0][1]], "słowa"


def dopasuj_krok(nazwa_folderu: str, kroki: list):
    """(krok | None, powód). Pewne tylko jedno najlepsze dopasowanie; remis albo zero → None.
    Numer kroku wygrywa, chyba że słowa jednoznacznie wskazują inny krok – wtedy pytanie."""
    n = numer_kroku(nazwa_folderu)
    if n is not None:
        trafione = [k for k in kroki if numer_kroku(k["nazwa"]) == n]
        if len(trafione) == 1:
            ze_slow, _ = _po_slowach(nazwa_folderu, kroki)
            if ze_slow is not None and ze_slow is not trafione[0]:
                return None, f"numer wskazuje „{trafione[0]['nazwa']}”, słowa – „{ze_slow['nazwa']}”"
            return trafione[0], "numer"
    return _po_slowach(nazwa_folderu, kroki)


def rodzaj_dokumentu(nazwa_folderu: str):
    for slowa, rodzaj, cel in DOKUMENTY:
        if ma_slowo(nazwa_folderu, slowa):
            return rodzaj, cel
    return None, None


def dopasuj_temat(nazwa_folderu: str, tematy: list):
    p = proste(nazwa_folderu)
    for t in tematy or []:
        if proste(t) == p or (proste(t) and proste(t) in p):
            return t
    return None


# ---------- plan ----------

def _swiezy(plik: dict, teraz: datetime) -> bool:
    d = _iso(plik.get("zmieniono") or "") or _iso(plik.get("utworzono") or "")
    return bool(d and teraz - d < timedelta(minutes=SWIEZE_MIN))


def planuj(lista: dict, konf: dict, teraz: datetime = None) -> dict:
    """Plan ruchów bez wykonywania. Zwraca {"ruchy", "czeka", "pytania", "puste_foldery", "podsumowanie"}."""
    teraz = teraz or datetime.now(timezone.utc)
    kroki, tematy, dni = konf.get("kroki") or [], konf.get("tematy") or [], konf.get("dni") or {}
    etap = konf.get("etap") or "Bez etapu"
    zajete = {}  # (folder, nazwa proste) -> rozmiar
    for e in lista.get("istniejace") or []:
        zajete[(nfc(e["folder"]).strip(), proste(e["nazwa"]))] = e.get("rozmiar")
    nowe = [p for p in (lista.get("nowe") or []) if not TYMCZASOWE.search(nfc(p.get("nazwa", "")))]
    grupy = {}
    for p in nowe:
        grupy.setdefault(nfc(p.get("folder") or "").strip(), []).append(p)

    ruchy, czeka, pytania, puste = [], [], [], []

    def cel_dla(folder_nowe: str, plik: dict, data: str):
        """(folder docelowy, rodzaj, powód) albo (None, None, powód)."""
        if folder_nowe:
            rodzaj, wzor = rodzaj_dokumentu(folder_nowe)
            if rodzaj:
                return wzor.format(r=(data or "")[:4] or "bez daty", etap=etap), rodzaj, "dokument: " + rodzaj
            krok, powod = dopasuj_krok(folder_nowe, kroki)
            if krok:
                cel = krok["folder"] + (f"/{PRZED}" if ma_slowo(folder_nowe, SLOWA_PRZED) else "")
                return cel, "zdjęcie", f"krok ({powod})"
            temat = dopasuj_temat(folder_nowe, tematy)
            if temat:
                return f"{ZDJECIA}/{bezpieczna(temat)}", "zdjęcie", "temat"
            return None, None, powod
        if not data:
            return None, None, "brak daty"
        dzien = dni.get(data) or []
        if len(dzien) == 1:
            krok = next((k for k in kroki if proste(k["nazwa"]) == proste(dzien[0])), None)
            if krok:
                return krok["folder"], "zdjęcie", "jedyny krok dnia w Dzienniku"
        return None, None, ("brak wpisu w Dzienniku budowy z tego dnia" if not dzien
                            else "kilka kroków tego dnia: " + ", ".join(dzien))

    for folder_nowe, pliki in sorted(grupy.items()):
        if any(_swiezy(p, teraz) for p in pliki):
            for p in pliki:
                czeka.append({"id": p.get("id"), "nazwa": p.get("nazwa"), "folder": folder_nowe,
                              "powod": "wgrywanie trwa (zmiana < 15 min)"})
            continue
        przeniesione = 0
        for p in sorted(pliki, key=lambda x: nfc(x.get("nazwa", ""))):
            nazwa = nfc(p.get("nazwa", ""))
            data, przybl, zrodlo = data_zrobienia(p)
            cel, rodzaj, powod = cel_dla(folder_nowe, p, data)
            if not cel:
                czeka.append({"id": p.get("id"), "nazwa": nazwa, "folder": folder_nowe, "data": data, "powod": powod})
                continue
            nn = nowa_nazwa(nazwa, data, przybl)
            klucz = (cel, proste(nn))
            if klucz in zajete:
                if zajete[klucz] is not None and zajete[klucz] == p.get("rozmiar"):
                    cel, rodzaj, powod = ARCH_DUP, "duplikat", "ta sama nazwa i rozmiar już są w " + cel
                    klucz = (cel, proste(nn))
                    while klucz in zajete:
                        nn = _z_numerem(nn)
                        klucz = (cel, proste(nn))
                else:
                    while klucz in zajete:
                        nn = _z_numerem(nn)
                        klucz = (cel, proste(nn))
                    powod += "; inna treść pod tą samą nazwą → numer"
            zajete[klucz] = p.get("rozmiar")
            ruchy.append({"id": p.get("id"), "z": f"{ZDJECIA}/{NOWE}" + (f"/{folder_nowe}" if folder_nowe else ""),
                          "nazwa": nazwa, "do": cel, "nowa_nazwa": nn, "data": data, "data_zrodlo": zrodlo,
                          "przyblizona": przybl, "rodzaj": rodzaj, "powod": powod,
                          "film": bool(FILM.search(nazwa))})
            przeniesione += 1
        if folder_nowe and przeniesione == len(pliki):
            puste.append({"z": f"{ZDJECIA}/{NOWE}/{folder_nowe}", "do": ARCH_PUSTE})

    for c in czeka:
        if c["powod"].startswith("wgrywanie"):
            continue
        pytania.append(_pytanie(c, kroki))
    podsum = {
        "ruchy": len(ruchy), "czeka": len(czeka),
        "zdjecia": sum(1 for r in ruchy if r["rodzaj"] == "zdjęcie"),
        "dokumenty": sum(1 for r in ruchy if r["rodzaj"] not in ("zdjęcie", "duplikat")),
        "duplikaty": sum(1 for r in ruchy if r["rodzaj"] == "duplikat"),
        "data_wg_wgrania": sum(1 for r in ruchy if r["przyblizona"]),
    }
    return {"utworzono": teraz.astimezone(PL).isoformat(timespec="seconds"), "ruchy": ruchy, "czeka": czeka,
            "pytania": _scal_pytania(pytania), "puste_foldery": puste, "podsumowanie": podsum}


def _z_numerem(nazwa: str) -> str:
    stem, kropka, ext = nazwa.rpartition(".")
    if not kropka:
        stem, ext = nazwa, ""
    m = re.match(r"^(.*)_(\d+)$", stem)
    stem = f"{m.group(1)}_{int(m.group(2)) + 1}" if m else f"{stem}_2"
    return f"{stem}.{ext}" if ext else stem


def _pytanie(c: dict, kroki: list) -> str:
    gdzie = f"folder „{c['folder']}”" if c.get("folder") else f"luźne zdjęcie {c.get('nazwa')}"
    return f"{gdzie} ({c.get('data') or 'bez daty'}): {c['powod']} – do którego kroku?"


def _scal_pytania(pytania: list) -> list:
    out = []
    for p in pytania:
        if p not in out:
            out.append(p)
    return out


def slad(plan: dict) -> dict:
    """Ślad do Notion: {data: {"lacznie": n, "kroki": {folder: n}, "dokumenty": [...], "przed_zakryciem": n}}."""
    dni = {}
    for r in plan.get("ruchy") or []:
        if r["rodzaj"] == "duplikat":
            continue
        d = dni.setdefault(r.get("data") or "bez daty", {"lacznie": 0, "kroki": {}, "dokumenty": [], "przed_zakryciem": 0})
        if r["rodzaj"] == "zdjęcie":
            folder = r["do"][:-len("/" + PRZED)] if r["do"].endswith("/" + PRZED) else r["do"]
            d["lacznie"] += 1
            d["kroki"][folder] = d["kroki"].get(folder, 0) + 1
            if r["do"].endswith("/" + PRZED):
                d["przed_zakryciem"] += 1
        else:
            d["dokumenty"].append(f"{r['do']}/{r['nowa_nazwa']}")
    return dict(sorted(dni.items()))


def pole_zdjecia(dzien: dict, linki: dict = None) -> str:
    """Treść pola „Zdjęcia” w Dzienniku budowy: łączna liczba na początku (czyta ją pulpit), potem kroki z linkami."""
    linki = linki or {}
    czesci = []
    for folder, n in dzien["kroki"].items():
        nazwa = folder.rsplit("/", 1)[-1]
        czesci.append(f"{nazwa} ({n})" + (f" {linki[folder]}" if linki.get(folder) else ""))
    return f"{dzien['lacznie']} zdj.: " + "; ".join(czesci)


# ---------- dziennik ruchów, blokada ----------

def _dziennik() -> Path:
    return DANE / "ruchy.jsonl"


def _teraz() -> str:
    return datetime.now(PL).isoformat(timespec="seconds")


def _przebieg(plan: dict) -> str:
    return plan.get("utworzono") or _teraz()


def _wpis_pliku(r: dict, przebieg: str, kto: str) -> dict:
    return {"przebieg": przebieg, "czas": _teraz(), "kto": kto, "id": r.get("id"), "z": r["z"], "nazwa": r["nazwa"],
            "do": r["do"], "nowa_nazwa": r["nowa_nazwa"]}


def _wpis_folderu(p: dict, przebieg: str, kto: str, w_archiwum: str = None) -> dict:
    """Wpis pustego folderu; `w_archiwum` tylko gdy nazwa w archiwum jest inna (dopisek `_2`). Stary format = bez niego."""
    w = {"przebieg": przebieg, "czas": _teraz(), "kto": kto, "folder": p["z"], "do": p["do"]}
    if w_archiwum and w_archiwum != p["z"].rsplit("/", 1)[-1]:
        w["w_archiwum"] = w_archiwum
    return w


def _dopisz(wpisy: list):
    if not wpisy:
        return
    DANE.mkdir(parents=True, exist_ok=True)
    with _dziennik().open("a", encoding="utf-8") as f:
        for w in wpisy:
            f.write(json.dumps(w, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _caly_folder(p: dict, ruchy: list, tylko) -> bool:
    """Konektor (`--tylko`): pusty folder idzie do dziennika, gdy wykonano wszystkie ruchy plików z niego."""
    z_folderu = [r for r in ruchy if r["z"] == p["z"] or r["z"].startswith(p["z"] + "/")]
    return bool(z_folderu) and all(r.get("id") in tylko for r in z_folderu)


def zapisz_ruchy(plan: dict, kto: str, tylko=None) -> tuple:
    """Dziennik ruchów po wykonaniu planu konektorem. Zwraca (plików, folderów)."""
    przebieg, ruchy = _przebieg(plan), plan.get("ruchy") or []
    pliki = [_wpis_pliku(r, przebieg, kto) for r in ruchy if not tylko or r.get("id") in tylko]
    foldery = [_wpis_folderu(p, przebieg, kto) for p in plan.get("puste_foldery") or []
               if not tylko or _caly_folder(p, ruchy, tylko)]
    _dopisz(pliki + foldery)
    return len(pliki), len(foldery)


def wczytaj_ruchy() -> list:
    p = _dziennik()
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def plan_cofniecia(ruchy: list) -> dict:
    """Odwrotność ostatniego przebiegu (najpierw ostatnie ruchy)."""
    cofniete = {r["przebieg"] for r in ruchy if r.get("cofniety")}
    ruchy = [r for r in ruchy if r["przebieg"] not in cofniete]
    if not ruchy:
        return {"przebieg": None, "ruchy": [], "foldery": []}
    ost = ruchy[-1]["przebieg"]
    wybrane = [r for r in ruchy if r["przebieg"] == ost]
    pliki = [{"id": r.get("id"), "z": r["do"], "nazwa": r["nowa_nazwa"], "do": r["z"], "nowa_nazwa": r["nazwa"]}
             for r in reversed(wybrane) if "nazwa" in r]
    foldery = []  # "folder" = nazwa w archiwum (stary format: jak w _nowe), "nowa_nazwa" = nazwa po powrocie do _nowe
    for r in wybrane:
        if "folder" in r:
            rodzic, nazwa = r["folder"].rsplit("/", 1)
            foldery.append({"folder": r.get("w_archiwum") or nazwa, "z": r["do"], "do": rodzic, "nowa_nazwa": nazwa})
    return {"przebieg": ost, "ruchy": pliki, "foldery": foldery}


def oznacz_cofniety(przebieg: str, kto: str):
    """Po wykonaniu cofnięcia: kolejne `cofnij` bierze wcześniejszy przebieg."""
    DANE.mkdir(parents=True, exist_ok=True)
    with _dziennik().open("a", encoding="utf-8") as f:
        f.write(json.dumps({"przebieg": przebieg, "cofniety": True, "kto": kto,
                            "czas": datetime.now(PL).isoformat(timespec="seconds")}, ensure_ascii=False) + "\n")


class Zajete(Exception):
    pass


def _blokada():
    """(treść blokady, aktywna?) albo (None, False). Konektor – 30 min, skrypt – 2 h; starsza = porzucona."""
    try:
        b = json.loads((DANE / "blokada.json").read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return None, False
    if not isinstance(b, dict):
        return None, False
    zycie = BLOKADA_KONEKTOR_MIN * 60 if b.get("kto") == "konektor" else BLOKADA_H * 3600
    return b, time.time() - b.get("t", 0) < zycie


def _blokada_aktywna():
    b, aktywna = _blokada()
    return b if aktywna else None


def opis_blokady() -> str:
    """Do `stan`: nie | <kto> od <czas> | porzucona (<kto> od <czas>)."""
    b, aktywna = _blokada()
    if b is None:
        return "porzucona (nieczytelna) – `zdjecia.py odblokuj`" if (DANE / "blokada.json").exists() else "nie"
    kto_od = f"{b.get('kto')} od {b.get('od')}"
    return kto_od if aktywna else f"porzucona ({kto_od}) – `zdjecia.py odblokuj`"


def zablokuj(kto: str, odswiez: bool = False):
    """Zakłada blokadę; aktywna blokada → Zajete. `odswiez`: blokadę tego samego wykonawcy przedłuża."""
    b = _blokada_aktywna()
    if b and not (odswiez and b.get("kto") == kto):
        raise Zajete(f"rozkładanie trwa ({b.get('kto')}, od {b.get('od')})")
    DANE.mkdir(parents=True, exist_ok=True)
    (DANE / "blokada.json").write_text(json.dumps({"kto": kto, "t": time.time(),
                                                   "od": datetime.now(PL).isoformat(timespec="minutes")}),
                                       encoding="utf-8")


def odblokuj(kto: str = None) -> bool:
    """Zdejmuje blokadę (z `kto` – tylko założoną przez tego wykonawcę). True, gdy zdjęto."""
    p = DANE / "blokada.json"
    if not p.exists():
        return False
    if kto:
        try:
            if json.loads(p.read_text(encoding="utf-8")).get("kto") != kto:
                return False
        except (ValueError, OSError, AttributeError):
            pass
    try:
        p.unlink()
    except OSError:
        return False
    return True


class Blokada:
    """Skrypt i konektor nie rozkładają naraz. Blokada starsza niż 2 h jest uznawana za porzuconą."""

    def __init__(self, kto: str):
        self.kto = kto

    def __enter__(self):
        zablokuj(self.kto)
        return self

    def __exit__(self, *a):
        odblokuj()


# ---------- konfiguracja (kroki) ----------

def wczytaj_konf(sciezka: Path = None) -> dict:
    p = sciezka or DANE / "kroki.json"
    if not p.exists():
        return {"etap": None, "kroki": [], "tematy": [], "dni": {}}
    return json.loads(p.read_text(encoding="utf-8"))


# ---------- tryb lokalny ----------

def _data_mdls(s: str):
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        return None


def exif_mdls(p: Path):
    """Data zrobienia z metadanych Spotlight (JPEG, HEIC, filmy) albo None. Plik bez EXIF ma w Spotlight datę
    utworzenia pliku (skopiowania, rozpakowania) – taka data to nie data zrobienia, więc None."""
    try:
        out = subprocess.run(["mdls", "-raw", "-name", "kMDItemContentCreationDate", "-name", "kMDItemFSCreationDate",
                              str(p)], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    # -raw: wartości rozdzielone bajtem NUL, alfabetycznie wg nazwy atrybutu (nie wg kolejności -name):
    # kMDItemContentCreationDate < kMDItemFSCreationDate. Trzeci atrybut zmieni indeksy.
    wartosci = (out or "").split("\0")
    tresc = _data_mdls(wartosci[0])
    if not tresc:
        return None
    plik = _data_mdls(wartosci[1]) if len(wartosci) > 1 else None
    if plik and abs((tresc - plik).total_seconds()) <= 1:
        return None
    return tresc.isoformat()


def lista_lokalna(hub: Path, exif=None) -> dict:
    exif = exif or exif_mdls
    baza = hub / ZDJECIA / NOWE
    nowe, istniejace = [], []
    if baza.exists():
        for p in sorted(baza.rglob("*")):
            if not p.is_file() or TYMCZASOWE.search(p.name):
                continue
            rel = p.parent.relative_to(baza).as_posix()
            st = p.stat()
            nowe.append({"id": str(p.relative_to(hub)), "nazwa": nfc(p.name), "folder": "" if rel == "." else nfc(rel),
                         "rozmiar": st.st_size,
                         "zmieniono": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
                         "utworzono": datetime.fromtimestamp(st.st_birthtime if hasattr(st, "st_birthtime")
                                                             else st.st_ctime, timezone.utc).isoformat(),
                         "zrobiono": exif(p) if (OBRAZ.search(p.name) or FILM.search(p.name)) else None})
    for korzen in ("Zdjęcia", "Faktury", "Dostawy", "Dziennik budowy KB", "Umowy/Protokoły", "_Archiwum"):
        k = hub / korzen
        if not k.exists():
            continue
        for p in k.rglob("*"):
            if p.is_file() and NOWE not in p.relative_to(hub).parts:
                istniejace.append({"folder": nfc(p.parent.relative_to(hub).as_posix()), "nazwa": nfc(p.name),
                                   "rozmiar": p.stat().st_size})
    return {"nowe": nowe, "istniejace": istniejace}


def wykonaj_lokalnie(plan: dict, hub: Path, kto: str = "skrypt") -> int:
    """Ruchy planu na Macu. Każdy wykonany ruch trafia do dziennika zaraz po przeniesieniu (pominięty – nie)."""
    przebieg, n = _przebieg(plan), 0
    for r in plan["ruchy"]:
        zrodlo = hub / r["z"] / r["nazwa"]
        cel = hub / r["do"] / r["nowa_nazwa"]
        if not zrodlo.exists() or cel.exists():
            continue  # inwestor przeniósł sam albo kolizja – nic nie nadpisujemy
        cel.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(zrodlo), str(cel))
        _dopisz([_wpis_pliku(r, przebieg, kto)])
        n += 1
    for p in plan["puste_foldery"]:
        z = hub / p["z"]
        if z.exists() and not any(x for x in z.rglob("*") if x.is_file() and not x.name.startswith(".")):
            cel = hub / p["do"] / z.name
            while cel.exists():
                cel = cel.with_name(_z_numerem(cel.name))
            cel.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(z), str(cel))
            _dopisz([_wpis_folderu(p, przebieg, kto, cel.name)])
    return n


def cofnij_lokalnie(c: dict, hub: Path) -> list:
    """Wykonuje plan cofnięcia na Macu; zwraca konflikty (puste = cofnięte w całości). Plik, którego nie ma w miejscu
    po rozłożeniu, a jest w miejscu wyjściowym – uznany za cofnięty wcześniej (ponowne `cofnij` dokańcza resztę)."""
    konflikty = []
    for f in c["foldery"]:  # pusty folder: zostaje w archiwum, gdy w _nowe jest już folder o tej nazwie – nie konflikt
        z, cel = hub / f["z"] / f["folder"], hub / f["do"] / f["nowa_nazwa"]
        if z.exists() and not cel.exists():
            cel.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(z), str(cel))
    for r in c["ruchy"]:
        z, cel = hub / r["z"] / r["nazwa"], hub / r["do"] / r["nowa_nazwa"]
        if z.exists() and not cel.exists():
            cel.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(z), str(cel))
        elif z.exists():
            konflikty.append(f"{r['z']}/{r['nazwa']}: w {r['do']} jest już plik {r['nowa_nazwa']} (nic nie nadpisuję)")
        elif not cel.exists():
            konflikty.append(f"{r['z']}/{r['nazwa']}: nie ma pliku (przeniesiony albo przemianowany ręcznie?)")
    return konflikty


def wg_dni(hub: Path) -> int:
    """Zdjęcia/_wg dni/RRRR-MM-DD/ – dowiązania do zdjęć z prefiksem daty (widok dnia bez zajmowania miejsca)."""
    baza, widok, n = hub / ZDJECIA, hub / ZDJECIA / "_wg dni", 0
    if not baza.exists():
        return 0
    for p in baza.rglob("*"):
        if not p.is_file() or "_wg dni" in p.parts or NOWE in p.parts:
            continue
        m = PREFIKS.match(p.name)
        if not m:
            continue
        cel = widok / m.group(1) / f"{p.parent.name} – {p.name}"
        if cel.is_symlink() or cel.exists():
            continue
        cel.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(os.path.relpath(p, cel.parent), cel)
        n += 1
    return n


# ---------- wypisywanie ----------

def wypisz(plan: dict, na_sucho: bool):
    s = plan["podsumowanie"]
    print(f"[zdjęcia] {'PLAN (na sucho)' if na_sucho else 'wykonano'}: ruchów {s['ruchy']} "
          f"(zdjęcia {s['zdjecia']}, dokumenty {s['dokumenty']}, duplikaty {s['duplikaty']}), czeka {s['czeka']}"
          + (f", data wg wgrania {s['data_wg_wgrania']}" if s["data_wg_wgrania"] else ""))
    for r in plan["ruchy"]:
        print(f"  {r['z']}/{r['nazwa']} → {r['do']}/{r['nowa_nazwa']}  [{r['powod']}]")
    for p in plan["puste_foldery"]:
        print(f"  pusty folder {p['z']} → {p['do']}")
    for q in plan["pytania"]:
        print(f"  ❓ {q}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("plan")
    a.add_argument("--lista", required=True)
    a.add_argument("--kroki")
    a.add_argument("--teraz")
    a.add_argument("--wyjscie")
    a.add_argument("--zablokuj", action="store_true", help="konektor: załóż blokadę na czas przebiegu (zdejmuje zapisz-ruchy)")
    a = sub.add_parser("rozloz")
    a.add_argument("--wykonaj", action="store_true")
    a.add_argument("--kroki")
    a = sub.add_parser("zapisz-ruchy")
    a.add_argument("plan")
    a.add_argument("--kto", default="konektor")
    a.add_argument("--tylko", default=None, help="id wykonanych ruchów po przecinku")
    a = sub.add_parser("cofnij")
    a.add_argument("--wykonaj", action="store_true", help="lokalnie: przenieś pliki z powrotem")
    a.add_argument("--zrobione", action="store_true", help="konektor: cofnięcie wykonane – zapisz w dzienniku ruchów")
    a = sub.add_parser("slad")
    a.add_argument("plan")
    sub.add_parser("wg-dni")
    sub.add_parser("stan")
    sub.add_parser("odblokuj")
    a = ap.parse_args(argv)
    # cele zapisu poleceń; rozloz i cofnij zapisują blokadę albo plan cofnięcia także na sucho
    cele = {"rozloz": [HUB, DANE], "cofnij": [HUB, DANE], "zapisz-ruchy": [DANE], "odblokuj": [DANE]}
    if a.cmd == "plan":
        cele["plan"] = [DANE if a.zablokuj or not a.wyjscie else Path(a.wyjscie)]
    if a.cmd in cele and hub.zapis_zablokowany(REPO, *cele[a.cmd]):
        return 1

    if a.cmd == "plan":
        teraz = _iso(a.teraz) if a.teraz else None
        lista = json.loads(Path(a.lista).read_text(encoding="utf-8"))
        konf = wczytaj_konf(Path(a.kroki) if a.kroki else None)
        if not konf.get("kroki"):
            print("[zdjęcia] brak kroków (.dom/zdjecia/kroki.json) – zapisz je z Harmonogramu", file=sys.stderr)
        plan = planuj(lista, konf, teraz)
        blokuj = a.zablokuj and bool(plan["ruchy"])  # blokada tylko po udanym planie z ruchami
        if blokuj:
            try:
                zablokuj("konektor", odswiez=True)
            except Zajete as e:
                print(f"[zdjęcia] {e} – nie rozkładaj teraz, spróbuj po zakończeniu przebiegu skryptu; "
                      "porzucona blokada → `zdjecia.py odblokuj`", file=sys.stderr)
                return 1
        try:
            wyj = Path(a.wyjscie) if a.wyjscie else DANE / f"plan-{datetime.now(PL):%Y%m%d-%H%M%S}.json"
            wyj.parent.mkdir(parents=True, exist_ok=True)
            wyj.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
        except BaseException:
            if blokuj:
                odblokuj("konektor")
            raise
        wypisz(plan, True)
        print(f"[zdjęcia] plan: {wyj}")
        if blokuj:
            print(f"[zdjęcia] blokada: konektor, {BLOKADA_KONEKTOR_MIN} min (zdejmie ją `zapisz-ruchy`; bez „ok” – "
                  "`zdjecia.py odblokuj`)")
        elif a.zablokuj:
            print("[zdjęcia] brak ruchów – blokady nie zakładam")
        return 0
    if a.cmd == "rozloz":
        try:
            with Blokada("skrypt"):
                plan = planuj(lista_lokalna(HUB), wczytaj_konf(Path(a.kroki) if a.kroki else None))
                n = wykonaj_lokalnie(plan, HUB, "skrypt") if a.wykonaj else None
                wypisz(plan, not a.wykonaj)
                if n is not None and n != len(plan["ruchy"]):
                    print(f"[zdjęcia] przeniesiono {n} z {len(plan['ruchy'])} – reszta pominięta (brak źródła "
                          "albo cel już istnieje); w dzienniku ruchów tylko wykonane")
        except Zajete as e:
            print(f"[zdjęcia] {e} – następny przebieg (porzucona blokada → `zdjecia.py odblokuj`)")
        return 0
    if a.cmd == "zapisz-ruchy":
        plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
        tylko = None
        if a.tylko is not None:
            tylko = {x.strip() for x in a.tylko.split(",") if x.strip()}
            if not tylko:
                print("[zdjęcia] --tylko bez identyfikatorów – nic nie zapisuję (nic nie wykonano? blokadę zdejmij "
                      "`zdjecia.py odblokuj`)", file=sys.stderr)
                return 1
        pliki, foldery = zapisz_ruchy(plan, a.kto, tylko)
        print(f"[zdjęcia] zapisano ruchów: {pliki}" + (f", pustych folderów: {foldery}" if foldery else ""))
        if odblokuj(a.kto):
            print("[zdjęcia] blokada zdjęta")
        return 0
    if a.cmd == "odblokuj":
        print("[zdjęcia] blokada zdjęta" if odblokuj() else "[zdjęcia] brak blokady")
        return 0
    if a.cmd == "cofnij":
        c = plan_cofniecia(wczytaj_ruchy())
        if not c["przebieg"]:
            print("[zdjęcia] brak ruchów do cofnięcia")
            return 0
        if a.zrobione:
            oznacz_cofniety(c["przebieg"], "konektor")
            print(f"[zdjęcia] przebieg {c['przebieg']} oznaczony jako cofnięty")
            return 0
        print(f"[zdjęcia] cofnięcie przebiegu {c['przebieg']}: plików {len(c['ruchy'])}, folderów {len(c['foldery'])}"
              " (najpierw foldery, potem pliki)")
        for r in c["ruchy"]:
            print(f"  {r['z']}/{r['nazwa']} → {r['do']}/{r['nowa_nazwa']}")
        for f in c["foldery"]:
            print(f"  folder {f['z']}/{f['folder']} → {f['do']}/{f['nowa_nazwa']}")
        (DANE / "cofniecie.json").write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
        if a.wykonaj:
            try:
                with Blokada("skrypt"):
                    konflikty = cofnij_lokalnie(c, HUB)
                    if not konflikty:
                        oznacz_cofniety(c["przebieg"], "skrypt")
            except Zajete as e:
                print(f"[zdjęcia] {e} – cofnij po zakończeniu przebiegu (porzucona blokada → `zdjecia.py odblokuj`)")
                return 1
            if konflikty:
                print(f"[zdjęcia] nie cofnięto {len(konflikty)} – przebieg NIE jest oznaczony jako cofnięty:")
                for k in konflikty:
                    print(f"  ✗ {k}")
                print("  Rozwiąż je i powtórz `cofnij --wykonaj` (cofnięte już pliki pominie) albo zamknij przebieg "
                      "`cofnij --zrobione`.")
                return 1
        return 0
    if a.cmd == "slad":
        plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
        s = slad(plan)
        for d, v in s.items():
            print(f"{d}: {pole_zdjecia(v) if v['lacznie'] else '0 zdjęć'}"
                  + (f" | przed zakryciem: {v['przed_zakryciem']}" if v["przed_zakryciem"] else "")
                  + (f" | dokumenty: {', '.join(v['dokumenty'])}" if v["dokumenty"] else ""))
        return 0
    if a.cmd == "wg-dni":
        print(f"[zdjęcia] nowych dowiązań: {wg_dni(HUB)}")
        return 0
    if a.cmd == "stan":
        konf, ruchy = wczytaj_konf(), wczytaj_ruchy()
        print(f"[zdjęcia] etap: {konf.get('etap')}, kroków: {len(konf.get('kroki') or [])}, "
              f"ruchów w dzienniku: {len(ruchy)}, ostatni przebieg: {ruchy[-1]['przebieg'] if ruchy else '–'}, "
              f"blokada: {opis_blokady()}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
