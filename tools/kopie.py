#!/usr/bin/env python3
"""Stan kopii zapasowych (POM-21): co ma kopię, gdzie i z kiedy. Plan i progi: docs/kopie-zapasowe.md.

    python3 tools/kopie.py stan [--cicho] [--json]   # tylko odczyt; --cicho: jedna linia, nic gdy wszystko aktualne
    python3 tools/kopie.py potwierdz <pozycja> [RRRR-MM-DD]   # inwestor zrobił kopię ręczną → data do rejestru

`stan` niczego nie zmienia: nie zapisuje stanu `kopia.py`, nie robi `git fetch`, git czyta bez blokad (`--no-optional-locks`),
Time Machine tylko `tmutil destinationinfo` (bez montowania), z `.dom` czyta tylko `kopia/stan.json` i rejestr `kopie-zapasowe.json` (daty) – sekretów nie czyta.
`potwierdz` zapisuje wyłącznie datę w rejestrze `<hub>/.dom/kopie-zapasowe.json`.
Pozycja: ✓ aktualna · ⚠ po terminie albo z zaległością (niewypchnięte commity, zmiany od kopii) · ✗ brak kopii · ℹ informacja.
Kod wyjścia 0 także przy ⚠/✗ (to wynik kontroli, nie błąd); 1 = błąd narzędzia. Brak gita albo uszkodzony plik stanu
lub rejestru → pozycja z czytelnym opisem (co poprawić), nie wyjątek.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import kopia  # noqa: E402  – te same reguły folderów i porównanie co kopia dokumentów

HUB = Path(os.environ.get("DOM_HUB") or REPO.parent.parent).expanduser().resolve()
REJESTR = "kopie-zapasowe.json"

# Kopie ręczne: klucz → (opis, gdzie leży kopia, termin w dniach; None = jednorazowo). Progi: docs/kopie-zapasowe.md, 3.
RECZNE = {
    "dysk-zewnetrzny": ("cały folder budowy z .dom, AI i źródłami wiedzy + pamięć asystenta i automaty launchd",
                        "dysk zewnętrzny", 7),
    "notion": ("eksport całego obszaru Notion (Markdown i CSV)", "dysk zewnętrzny", 30),
    "kosztorys-xlsx": ("plik xlsx arkusza kosztorysu (z formułami)", "dysk zewnętrzny", 30),
    "zdjecia": ("zdjęcia z Dysku – trzecia kopia", "dysk zewnętrzny", 30),
    "proba-odtworzenia": ("próba odtworzenia: trzy losowe pliki z kopii i eksport Notion", "–", 90),
    "sekrety": ("tokeny i hasła w menedżerze haseł, tokeny z rozmów wymienione", "menedżer haseł", None),
}
KOSZTORYS_DNI = 2  # kopia wartości arkusza – automat wieczorny; szybki ponawia starszą niż 12 h
DOKUMENTY_DNI = 7
WOLNE_MIN_GB = 15


def poz(klucz, stan, opis, gdzie="", kiedy=None, szczegol=""):
    return {"klucz": klucz, "stan": stan, "opis": opis, "gdzie": gdzie, "kiedy": kiedy, "szczegol": szczegol}


def dni_od(d: str, dzis: date) -> int:
    return (dzis - date.fromisoformat(d[:10])).days


class BladRejestru(ValueError):
    pass


def wczytaj_rejestr(hub: Path) -> dict:
    p = hub / ".dom" / REJESTR
    if not p.exists():
        return {}
    try:
        rejestr = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        raise BladRejestru(f"uszkodzony rejestr .dom/{REJESTR} ({e}) – popraw plik albo przywróć go z kopii") from e
    if not isinstance(rejestr, dict) or not all(isinstance(v, str) for v in rejestr.values()):
        raise BladRejestru(f"rejestr .dom/{REJESTR} ma zły układ – oczekiwany {{\"pozycja\": \"RRRR-MM-DD\"}}")
    return rejestr


def dokumenty(hub: Path, dzis: date) -> dict:
    """Kopia dokumentów Mac → Dysk (kopia.py) – ten sam odczyt stanu z zapasem co kopia.py i porównanie bez zapisu."""
    opis, gdzie = "dokumenty budowy → Dysk", "Dysk (Dom/_Kopie)"
    katalog = kopia.STAN_DIR if hub == kopia.HUB else hub / ".dom" / "kopia"
    try:
        stan = kopia.wczytaj_stan(katalog)
    except (ValueError, OSError, KeyError, TypeError) as e:
        return poz("dokumenty", "✗", opis, gdzie, None,
                   f"uszkodzony stan kopii .dom/kopia ({e}) – sprawdź `python3 tools/kopia.py stan`")
    kiedy = stan.get("potwierdzono")
    if not kiedy and not stan.get("potwierdzone"):
        return poz("dokumenty", "✗", opis, gdzie, None, "kopia.py nie był uruchamiany")
    potwierdzone = {k: v for k, v in (stan.get("potwierdzone") or {}).items() if kopia.dozwolony(k)}
    teraz = kopia.skanuj(hub, {**(stan.get("potwierdzone") or {}), **(stan.get("ostatni_skan") or {})})
    r = kopia.roznice(potwierdzone, teraz)
    n = sum(len(r[k]) for k in ("nowe", "zmienione", "przeniesione", "usuniete"))
    czeka = [x["data"] for x in stan.get("paczki", []) if not x.get("wgrana")]
    szczegol = f"zmian od kopii: {n}" + (f" · paczki do wgrania: {', '.join(czeka)}" if czeka else "")
    if not kiedy:
        s = "✗"
    elif (n or czeka) and dni_od(kiedy, dzis) > DOKUMENTY_DNI:
        s = "⚠"
    else:
        s = "✓"
    return poz("dokumenty", s, opis, gdzie, kiedy, szczegol)


def git(katalog: Path, *args) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "--no-optional-locks", "-C", str(katalog), *args],
                              capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, 124, "", "git nie odpowiedział w 30 s")


def repozytoria(hub: Path, dysk_zewn: str = None, dysk_stan: str = "✓") -> list:
    """Każdy katalog w <hub>/AI: git ze zdalnym, bez niewypchniętych commitów i zmian. Bez `git fetch`.
    Katalog bez zdalnej kopii: kopia na dysku zewnętrznym (dysk_zewn = jej data, dysk_stan = jej stan) aktualna → ✓,
    po terminie → ⚠, nigdy niepotwierdzona → ✗."""
    out = []
    baza = hub / "AI"
    if not baza.is_dir():
        return out
    if not shutil.which("git"):
        return [poz("repo:*", "⚠", "katalogi AI/* – nie sprawdzono", "", None,
                    "brak programu git na tym komputerze (zainstaluj: xcode-select --install)")]
    for d in sorted(x for x in baza.iterdir() if x.is_dir() and not x.name.startswith(".")):
        klucz = f"repo:{d.name}"
        zdalne = git(d, "remote").stdout.split() if (d / ".git").exists() else []
        if not zdalne:
            opis = f"AI/{d.name} – " + ("git bez zdalnego repozytorium" if (d / ".git").exists() else "bez gita")
            if not dysk_zewn:
                out.append(poz(klucz, "✗", opis, "tylko na Macu", None, "prywatne repozytorium albo dysk zewnętrzny"))
            elif dysk_stan == "✓":
                out.append(poz(klucz, "✓", opis, "dysk zewnętrzny", dysk_zewn))
            else:
                out.append(poz(klucz, "⚠", opis, "dysk zewnętrzny", dysk_zewn, "kopia na dysku zewnętrznym po terminie"))
            continue
        uwagi = []
        if git(d, "rev-parse", "--abbrev-ref", "@{u}").returncode == 0:
            przed = git(d, "rev-list", "--count", "@{u}..HEAD").stdout.strip()
            if przed and przed != "0":
                uwagi.append(f"niewypchnięte commity: {przed}")
        else:
            uwagi.append("bieżąca gałąź bez odpowiednika na GitHubie")
        zmiany = [x for x in git(d, "status", "--porcelain", "--untracked-files=normal").stdout.splitlines() if x]
        if zmiany:
            uwagi.append(f"niezacommitowane pliki: {len(zmiany)}")
        ostatni = git(d, "log", "-1", "--format=%cs").stdout.strip() or None
        out.append(poz(klucz, "⚠" if uwagi else "✓", f"AI/{d.name}", "GitHub (" + ", ".join(zdalne) + ")", ostatni,
                       " · ".join(uwagi)))
    return out


def kosztorys(hub: Path, dzis: date) -> dict:
    p = hub / "Koszty" / "Kosztorys_google.json"
    if not p.exists():
        return poz("kosztorys", "✗", "kopia wartości arkusza kosztorysu", "Mac (Koszty/)", None,
                   "brak pliku – automat wieczorny (wydatki.py pobierz) nie zapisał kopii")
    kiedy = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
    s = "⚠" if dni_od(kiedy, dzis) > KOSZTORYS_DNI else "✓"
    return poz("kosztorys", s, "kopia wartości arkusza kosztorysu", "Mac (Koszty/) → dysk zewnętrzny", kiedy)


def reczne(rejestr: dict, dzis: date) -> list:
    out = []
    for klucz, (opis, gdzie, termin) in RECZNE.items():
        kiedy = rejestr.get(klucz)
        if not kiedy:
            out.append(poz(klucz, "✗", opis, gdzie, None, "brak potwierdzenia (`kopie.py potwierdz " + klucz + "`)"))
        elif termin is not None and dni_od(kiedy, dzis) > termin:
            out.append(poz(klucz, "⚠", opis, gdzie, kiedy, f"termin co {termin} dni minął"))
        else:
            out.append(poz(klucz, "✓", opis, gdzie, kiedy))
    return out


def time_machine() -> dict:
    """Tylko informacja: na komputerze zarządzanym przez firmę Time Machine nie jest częścią planu (docs, 2)."""
    if not shutil.which("tmutil"):
        return poz("time-machine", "ℹ", "Time Machine", szczegol="niedostępne na tym systemie")
    try:
        r = subprocess.run(["tmutil", "destinationinfo"], capture_output=True, text=True, timeout=10)
        tekst = (r.stdout + r.stderr).strip()
    except (OSError, subprocess.TimeoutExpired):
        return poz("time-machine", "ℹ", "Time Machine", szczegol="nie udało się odczytać")
    jest = "Name" in tekst or "Kind" in tekst
    return poz("time-machine", "ℹ", "Time Machine", szczegol="skonfigurowane" if jest else "nieskonfigurowane")


def wolne_miejsce(hub: Path) -> dict:
    gb = shutil.disk_usage(str(hub)).free / 1024 ** 3
    return poz("miejsce", "⚠" if gb < WOLNE_MIN_GB else "ℹ", "wolne miejsce na dysku Maca",
               szczegol=f"{gb:.0f} GB" + (f" – poniżej {WOLNE_MIN_GB} GB" if gb < WOLNE_MIN_GB else ""))


def zbierz(hub: Path, dzis: date) -> list:
    try:
        rn = reczne(wczytaj_rejestr(hub), dzis)
    except BladRejestru as e:
        rn = [poz("rejestr", "✗", "rejestr kopii ręcznych", szczegol=str(e))]
    dysk = next((p for p in rn if p["klucz"] == "dysk-zewnetrzny"), {})
    return ([dokumenty(hub, dzis)] + repozytoria(hub, dysk.get("kiedy"), dysk.get("stan", "✗"))
            + [kosztorys(hub, dzis)] + rn + [time_machine(), wolne_miejsce(hub)])


def linia_cicha(pozycje: list) -> str:
    zle = {s: [p["klucz"] for p in pozycje if p["stan"] == s] for s in ("⚠", "✗")}
    if not zle["⚠"] and not zle["✗"]:
        return ""
    ok = sum(1 for p in pozycje if p["stan"] == "✓")
    return (f"[kopie] ✓ {ok} · ⚠ {len(zle['⚠'])}" + (f" ({', '.join(zle['⚠'])})" if zle["⚠"] else "")
            + f" · ✗ {len(zle['✗'])}" + (f" ({', '.join(zle['✗'])})" if zle["✗"] else ""))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("stan")
    a.add_argument("--cicho", action="store_true")
    a.add_argument("--json", action="store_true")
    a = sub.add_parser("potwierdz")
    a.add_argument("pozycja", choices=sorted(RECZNE))
    a.add_argument("data", nargs="?")
    a = ap.parse_args(argv)
    dzis = date.today()

    if a.cmd == "potwierdz":
        kiedy = a.data or dzis.isoformat()
        try:
            if date.fromisoformat(kiedy) > dzis:
                raise ValueError
        except ValueError:
            print(f"✗ data {kiedy} – podaj RRRR-MM-DD, nie z przyszłości")
            return 1
        p = HUB / ".dom" / REJESTR
        try:
            rejestr = wczytaj_rejestr(HUB)
        except BladRejestru as e:
            print(f"✗ {e}")
            return 1
        rejestr[a.pozycja] = kiedy
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rejestr, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
        print(f"[kopie] {a.pozycja}: potwierdzono {kiedy}")
        return 0

    pozycje = zbierz(HUB, dzis)
    if a.json:
        print(json.dumps(pozycje, ensure_ascii=False, indent=1))
    elif a.cicho:
        linia = linia_cicha(pozycje)
        if linia:
            print(linia)
    else:
        for p in pozycje:
            print(f"{p['stan']} {p['klucz']:<20} {p['opis']}" + (f" · {p['gdzie']}" if p["gdzie"] else "")
                  + (f" · z {p['kiedy']}" if p["kiedy"] else "") + (f" · {p['szczegol']}" if p["szczegol"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
