#!/usr/bin/env python3
"""Zdjęcia i dokumenty z telefonu: rozkładanie skrzynki `Zdjęcia/_nowe` do folderów kroków (POM-1, etap C–D).

    python3 tools/zdjecia.py plan --lista <lista.json> [--teraz ISO] [--wyjscie plan.json]   # konektor: lista → plan (na sucho)
    python3 tools/zdjecia.py rozloz [--wykonaj]          # tryb lokalny: <hub>/Zdjęcia/_nowe → foldery kroków na Macu
    python3 tools/zdjecia.py zapisz-ruchy <plan.json> [--kto konektor] [--tylko id,id]   # dziennik ruchów po wykonaniu planu
    python3 tools/zdjecia.py cofnij [--wykonaj]          # plan odwrotny ostatniego przebiegu (lokalnie: wykonuje)
    python3 tools/zdjecia.py slad <plan.json>             # ślad do Notion: dzień → krok → liczba, folder
    python3 tools/zdjecia.py wg-dni                       # Mac: Zdjęcia/_wg dni/RRRR-MM-DD/ z dowiązaniami
    python3 tools/zdjecia.py stan                         # kroki, ostatni przebieg, blokada, liczba ruchów

Reguły (pełny opis dla agentów: docs/zdjecia-i-kopia.md):
- Nic nie jest kasowane ani nadpisywane. Kolizja nazwy przy innej treści → dopisek `_2`; ta sama nazwa i rozmiar →
  duplikat do `_Archiwum/Duplikaty/`. Pusty folder po rozłożeniu → `_Archiwum/Puste foldery/`.
- Data zrobienia: EXIF (tylko lokalnie, `mdls`) → nazwa pliku z telefonu (PXL_ w UTC, IMG_/VID_/RRRRMMDD_ lokalnie) →
  data wgrania (`createdTime`, UTC → czas polski) ze znakiem `~` w prefiksie („data wg wgrania”).
- Plik zmieniony mniej niż 15 min temu albo folder z takim plikiem → następny przebieg (wgrywanie trwa).
- Folder w `_nowe`: nazwa → krok (numer albo słowa z nazwy kroku); słowa „przed zakryciem”, „z miarą”… → podfolder
  `przed zakryciem/`; słowa „faktura”, „WZ”, „dziennik KB”… → dokument. Niepewne → zostaje, pytanie 🔔.
- Luźne pliki: jeden krok w Dzienniku budowy tego dnia → ten krok; inaczej zostają z pytaniem.
- Ponowny przebieg nic nie zmienia (prefiks daty nie jest dokładany drugi raz).

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

REPO = Path(__file__).resolve().parent.parent
HUB = Path(os.environ.get("DOM_HUB") or REPO.parent.parent).expanduser().resolve()
DANE = Path(os.environ.get("ZDJECIA_DANE") or HUB / ".dom" / "zdjecia")
ZDJECIA, NOWE = "Zdjęcia", "_nowe"
PRZED = "przed zakryciem"
ARCH_DUP, ARCH_PUSTE = "_Archiwum/Duplikaty", "_Archiwum/Puste foldery"
SWIEZE_MIN = 15
BLOKADA_H = 2

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


def numer_kroku(s: str):
    m = re.match(r"^\s*(?:krok\s*)?0*(\d{1,2})\b", proste(s))
    return int(m.group(1)) if m else None


def dopasuj_krok(nazwa_folderu: str, kroki: list):
    """(krok | None, powód). Pewne tylko jedno najlepsze dopasowanie; remis albo zero → None."""
    n = numer_kroku(nazwa_folderu)
    if n is not None:
        trafione = [k for k in kroki if numer_kroku(k["nazwa"]) == n]
        if len(trafione) == 1:
            return trafione[0], "numer"
    slowa = _rdzenie(nazwa_folderu) - _rdzenie(" ".join(SLOWA_PRZED))
    if not slowa:
        return None, "brak słów do dopasowania"
    wyniki = sorted(((len(slowa & _rdzenie(k["nazwa"])), i) for i, k in enumerate(kroki)), reverse=True)
    if not wyniki or wyniki[0][0] == 0:
        return None, "żaden krok"
    if len(wyniki) > 1 and wyniki[1][0] == wyniki[0][0]:
        return None, "kilka kroków: " + ", ".join(kroki[i]["nazwa"] for s, i in wyniki if s == wyniki[0][0])
    return kroki[wyniki[0][1]], "słowa"


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
    return f"{dzien['lacznie']} zdjęć: " + "; ".join(czesci)


# ---------- dziennik ruchów, blokada ----------

def _dziennik() -> Path:
    return DANE / "ruchy.jsonl"


def zapisz_ruchy(plan: dict, kto: str, tylko=None) -> int:
    DANE.mkdir(parents=True, exist_ok=True)
    przebieg = plan.get("utworzono") or datetime.now(PL).isoformat(timespec="seconds")
    n = 0
    with _dziennik().open("a", encoding="utf-8") as f:
        for r in plan.get("ruchy") or []:
            if tylko and r.get("id") not in tylko:
                continue
            f.write(json.dumps({"przebieg": przebieg, "czas": datetime.now(PL).isoformat(timespec="seconds"),
                                "kto": kto, "id": r.get("id"), "z": r["z"], "nazwa": r["nazwa"],
                                "do": r["do"], "nowa_nazwa": r["nowa_nazwa"]}, ensure_ascii=False) + "\n")
            n += 1
        for p in plan.get("puste_foldery") or []:
            if tylko:
                continue
            f.write(json.dumps({"przebieg": przebieg, "czas": datetime.now(PL).isoformat(timespec="seconds"),
                                "kto": kto, "folder": p["z"], "do": p["do"]}, ensure_ascii=False) + "\n")
    return n


def wczytaj_ruchy() -> list:
    p = _dziennik()
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def plan_cofniecia(ruchy: list) -> dict:
    """Odwrotność ostatniego przebiegu (najpierw ostatnie ruchy)."""
    if not ruchy:
        return {"przebieg": None, "ruchy": [], "foldery": []}
    ost = ruchy[-1]["przebieg"]
    wybrane = [r for r in ruchy if r["przebieg"] == ost]
    pliki = [{"id": r.get("id"), "z": r["do"], "nazwa": r["nowa_nazwa"], "do": r["z"], "nowa_nazwa": r["nazwa"]}
             for r in reversed(wybrane) if "nazwa" in r]
    foldery = [{"folder": r["folder"].rsplit("/", 1)[-1], "z": r["do"], "do": r["folder"].rsplit("/", 1)[0]}
               for r in wybrane if "folder" in r]
    return {"przebieg": ost, "ruchy": pliki, "foldery": foldery}


class Zajete(Exception):
    pass


class Blokada:
    """Skrypt i konektor nie rozkładają naraz. Blokada starsza niż 2 h jest uznawana za porzuconą."""

    def __init__(self, kto: str):
        self.p, self.kto = DANE / "blokada.json", kto

    def __enter__(self):
        DANE.mkdir(parents=True, exist_ok=True)
        if self.p.exists():
            try:
                b = json.loads(self.p.read_text(encoding="utf-8"))
                if time.time() - b.get("t", 0) < BLOKADA_H * 3600:
                    raise Zajete(f"rozkładanie trwa ({b.get('kto')}, od {b.get('od')})")
            except (ValueError, OSError):
                pass
        self.p.write_text(json.dumps({"kto": self.kto, "t": time.time(),
                                      "od": datetime.now(PL).isoformat(timespec="minutes")}), encoding="utf-8")
        return self

    def __exit__(self, *a):
        try:
            self.p.unlink()
        except OSError:
            pass


# ---------- konfiguracja (kroki) ----------

def wczytaj_konf(sciezka: Path = None) -> dict:
    p = sciezka or DANE / "kroki.json"
    if not p.exists():
        return {"etap": None, "kroki": [], "tematy": [], "dni": {}}
    return json.loads(p.read_text(encoding="utf-8"))


# ---------- tryb lokalny ----------

def exif_mdls(p: Path):
    """Data zrobienia z metadanych Spotlight (JPEG, HEIC, filmy) albo None."""
    try:
        out = subprocess.run(["mdls", "-raw", "-name", "kMDItemContentCreationDate", str(p)],
                             capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    if not out or out == "(null)":
        return None
    try:
        return datetime.strptime(out, "%Y-%m-%d %H:%M:%S %z").isoformat()
    except ValueError:
        return None


def lista_lokalna(hub: Path, exif=exif_mdls) -> dict:
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


def wykonaj_lokalnie(plan: dict, hub: Path) -> int:
    n = 0
    for r in plan["ruchy"]:
        zrodlo = hub / r["z"] / r["nazwa"]
        cel = hub / r["do"] / r["nowa_nazwa"]
        if not zrodlo.exists() or cel.exists():
            continue  # inwestor przeniósł sam albo kolizja – nic nie nadpisujemy
        cel.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(zrodlo), str(cel))
        n += 1
    for p in plan["puste_foldery"]:
        z = hub / p["z"]
        if z.exists() and not any(x for x in z.rglob("*") if x.is_file() and not x.name.startswith(".")):
            cel = hub / p["do"] / z.name
            while cel.exists():
                cel = cel.with_name(_z_numerem(cel.name))
            cel.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(z), str(cel))
    return n


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
    a = sub.add_parser("rozloz")
    a.add_argument("--wykonaj", action="store_true")
    a.add_argument("--kroki")
    a = sub.add_parser("zapisz-ruchy")
    a.add_argument("plan")
    a.add_argument("--kto", default="konektor")
    a.add_argument("--tylko", default="")
    a = sub.add_parser("cofnij")
    a.add_argument("--wykonaj", action="store_true")
    a = sub.add_parser("slad")
    a.add_argument("plan")
    sub.add_parser("wg-dni")
    sub.add_parser("stan")
    a = ap.parse_args(argv)

    if a.cmd == "plan":
        teraz = _iso(a.teraz) if a.teraz else None
        lista = json.loads(Path(a.lista).read_text(encoding="utf-8"))
        konf = wczytaj_konf(Path(a.kroki) if a.kroki else None)
        if not konf.get("kroki"):
            print("[zdjęcia] brak kroków (.dom/zdjecia/kroki.json) – zapisz je z Harmonogramu", file=sys.stderr)
        plan = planuj(lista, konf, teraz)
        wyj = Path(a.wyjscie) if a.wyjscie else DANE / f"plan-{datetime.now(PL):%Y%m%d-%H%M%S}.json"
        wyj.parent.mkdir(parents=True, exist_ok=True)
        wyj.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
        wypisz(plan, True)
        print(f"[zdjęcia] plan: {wyj}")
        return 0
    if a.cmd == "rozloz":
        try:
            with Blokada("skrypt"):
                plan = planuj(lista_lokalna(HUB), wczytaj_konf(Path(a.kroki) if a.kroki else None))
                if a.wykonaj:
                    wykonaj_lokalnie(plan, HUB)
                    zapisz_ruchy(plan, "skrypt")
                wypisz(plan, not a.wykonaj)
        except Zajete as e:
            print(f"[zdjęcia] {e} – następny przebieg")
        return 0
    if a.cmd == "zapisz-ruchy":
        plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
        tylko = {x for x in a.tylko.split(",") if x} or None
        print(f"[zdjęcia] zapisano ruchów: {zapisz_ruchy(plan, a.kto, tylko)}")
        return 0
    if a.cmd == "cofnij":
        c = plan_cofniecia(wczytaj_ruchy())
        if not c["przebieg"]:
            print("[zdjęcia] brak ruchów do cofnięcia")
            return 0
        print(f"[zdjęcia] cofnięcie przebiegu {c['przebieg']}: plików {len(c['ruchy'])}, folderów {len(c['foldery'])}")
        for r in c["ruchy"]:
            print(f"  {r['z']}/{r['nazwa']} → {r['do']}/{r['nowa_nazwa']}")
        for f in c["foldery"]:
            print(f"  folder {f['z']}/{f['folder']} → {f['do']}")
        if a.wykonaj:
            for f in c["foldery"]:
                z, cel = HUB / f["z"] / f["folder"], HUB / f["do"] / f["folder"]
                if z.exists() and not cel.exists():
                    cel.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(z), str(cel))
            for r in c["ruchy"]:
                z, cel = HUB / r["z"] / r["nazwa"], HUB / r["do"] / r["nowa_nazwa"]
                if z.exists() and not cel.exists():
                    cel.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(z), str(cel))
        DANE.mkdir(parents=True, exist_ok=True)
        (DANE / "cofniecie.json").write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
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
              f"blokada: {'tak' if (DANE / 'blokada.json').exists() else 'nie'}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
