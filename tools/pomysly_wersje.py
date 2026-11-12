#!/usr/bin/env python3
"""Wersje pluginów z CHANGELOG.md dla pomysłów POM-n – podstawa kontroli spójności „status POM ↔ stan wdrożenia”.

Reguła (rozwoj-harnessu, sekcja B.4): wpis wdrożenia ma nagłówek `## <plugin> [wersja] – data (POM-n)`.
Narzędzie czyta CHANGELOG.md z gałęzi main (`git show main:CHANGELOG.md` – to, co wdrożone, a nie stan bieżącej gałęzi
roboczej; brak gałęzi main albo gita → ostrzeżenie i plik z dysku; stdlib, bez sieci) i dla każdego POM-n podaje:
  - „nagłówki” – wersje z nagłówków z numerem POM (jednoznaczne: z nich wolno uzupełnić pole „Zrobiono w wersji”),
  - „tylko w treści” – wersje, w których treści POM-n jest wspomniany, a nagłówek go nie ma (niejednoznaczne –
    wzmianka bywa tylko odwołaniem; tego nie wpisuj do pola, najwyżej zapytaj inwestora).

    python3 tools/pomysly_wersje.py            # wszystkie POM-n z CHANGELOG
    python3 tools/pomysly_wersje.py 8 POM-14   # wybrane
    python3 tools/pomysly_wersje.py --json
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAGLOWEK = re.compile(r"^##\s+(?:(?P<plugin>ja|dom-budowa)\s+)?\[(?P<wersja>[^\]]+)\]\s*[–-]\s*(?P<data>\S+)(?P<reszta>.*)$")
POM = re.compile(r"POM-(\d+)")


def sekcje(tekst: str) -> list:
    """Lista sekcji `## …` jako (plugin, wersja, data, nagłówek, treść). Wpisy bez nazwy pluginu to dom-budowa."""
    wynik, biezaca = [], None
    for linia in tekst.splitlines():
        if linia.startswith("## "):
            m = NAGLOWEK.match(linia)
            if m:
                biezaca = {"plugin": m.group("plugin") or "dom-budowa", "wersja": m.group("wersja"),
                           "data": m.group("data"), "naglowek": linia, "tresc": []}
                wynik.append(biezaca)
            else:
                biezaca = None  # np. „## [Unreleased]” bez daty albo inny nagłówek – nie liczymy
        elif biezaca is not None:
            biezaca["tresc"].append(linia)
    return wynik


def mapa_pomyslow(tekst: str) -> dict:
    """{numer: {"naglowki": ["ja 1.12.7", …], "tylko_w_tresci": […]}} – wersje w kolejności z pliku (najnowsze pierwsze)."""
    wynik = {}
    for s in sekcje(tekst):
        etykieta = f"{s['plugin']} {s['wersja']}"
        w_naglowku = {int(n) for n in POM.findall(s["naglowek"])}
        w_tresci = {int(n) for n in POM.findall("\n".join(s["tresc"]))} - w_naglowku
        for n in w_naglowku:
            wpis = wynik.setdefault(n, {"naglowki": [], "tylko_w_tresci": []})
            if etykieta not in wpis["naglowki"]:
                wpis["naglowki"].append(etykieta)
        for n in w_tresci:
            wpis = wynik.setdefault(n, {"naglowki": [], "tylko_w_tresci": []})
            if etykieta not in wpis["tylko_w_tresci"]:
                wpis["tylko_w_tresci"].append(etykieta)
    return wynik


def czytaj_changelog() -> tuple:
    """(tekst, ostrzeżenie): CHANGELOG z gałęzi main; bez niej – plik z dysku z ostrzeżeniem; brak obu → (None, błąd)."""
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "show", "main:CHANGELOG.md"], capture_output=True, timeout=30)
        if r.returncode == 0:
            return r.stdout.decode("utf-8"), ""
        powod = r.stderr.decode("utf-8", "replace").strip().splitlines()[-1:] or ["nieznany błąd"]
    except (OSError, subprocess.SubprocessError) as e:
        powod = [str(e)]
    plik = ROOT / "CHANGELOG.md"
    ostrzezenie = f"⚠ nie da się odczytać CHANGELOG.md z gałęzi main ({powod[0]}) – czytam plik z dysku"
    if not plik.exists():
        return None, ostrzezenie.replace("czytam plik z dysku", "brak też CHANGELOG.md na dysku")
    return plik.read_text(encoding="utf-8"), ostrzezenie


def numer(arg: str) -> int:
    m = re.fullmatch(r"(?:POM-)?(\d+)", arg.strip(), re.IGNORECASE)
    if not m:
        raise ValueError(f"nie rozumiem „{arg}” – podaj np. 14 albo POM-14")
    return int(m.group(1))


def main(argv: list) -> int:
    json_out = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    tekst, ostrzezenie = czytaj_changelog()
    if ostrzezenie:
        print(ostrzezenie, file=sys.stderr)
    if tekst is None:
        return 1
    mapa = mapa_pomyslow(tekst)
    try:
        chciane = sorted({numer(a) for a in argv}) if argv else sorted(mapa)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    wynik = {n: mapa.get(n, {"naglowki": [], "tylko_w_tresci": []}) for n in chciane}
    if json_out:
        print(json.dumps({f"POM-{n}": w for n, w in wynik.items()}, ensure_ascii=False, indent=2))
        return 0
    for n, w in wynik.items():
        print(f"POM-{n}\tnagłówki: {', '.join(w['naglowki']) or '–'}\ttylko w treści: {', '.join(w['tylko_w_tresci']) or '–'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
