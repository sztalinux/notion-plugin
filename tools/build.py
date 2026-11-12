#!/usr/bin/env python3
"""Walidacja i budowanie paczek harnessu dom-budowa.

    python3 tools/build.py                       # walidacja + dowiązania skilli + dist/
    python3 tools/build.py --tylko-walidacja     # tylko walidacja
    python3 tools/build.py --kopiuj-dowiazania   # .agents/skills i .claude/skills jako kopie (Windows)

Pluginy = katalogi plugins/<nazwa>/ z .claude-plugin/plugin.json (dziś: dom-budowa, ja).
.claude/skills/ i .agents/skills/ to katalogi z dowiązaniem na każdy skill wszystkich pluginów
(odtwarzane przy każdym uruchomieniu).

Wynik w dist/:
    <plugin>.plugin           – plugin dla Claude (Cowork / claude.ai), po jednym na plugin
    gemini-gem/instrukcje.md  – instrukcje do wklejenia w Gem (dom-budowa)
    gemini-gem/wiedza/*.md    – po jednym pliku na procedurę (pliki wiedzy Gema)
    claude-ai-projekt/instrukcje.md – instrukcje projektu „Dom” na claude.ai
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
try:
    import fcntl  # blokada builda (macOS/Linux); na Windows bez blokady
except ImportError:
    fcntl = None
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
PLUGIN = PLUGINS / "dom-budowa"          # Gemini i instrukcje projektu „Dom” – tylko ten plugin
SKILLS = PLUGIN / "skills"
KONTEKST = {"dom-budowa": "budowa", "ja": "ja"}  # skill kontekstowy pluginu = mapa jego procedur
DIST = ROOT / "dist"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def glowna_kopia(root: Path) -> Path:
    """Kopia robocza git (np. .claude/worktrees/<nazwa>) ma plik .git „gitdir: <repo>/.git/worktrees/<nazwa>” –
    folder budowy liczymy od głównej kopii, inaczej lista zakazanych słów byłaby szukana w złym miejscu."""
    g = root / ".git"
    if g.is_file():
        t = g.read_text(encoding="utf-8").strip()
        if t.startswith("gitdir:"):
            return (g.parent / t[7:].strip()).resolve().parent.parent.parent  # ścieżka bywa względna
    return root


HUB = Path(os.environ.get("DOM_HUB", glowna_kopia(ROOT).parent.parent)).expanduser()
ZAKAZANE = HUB / ".dom" / "zakazane-w-repo.txt"  # poza repo: sama lista byłaby wyciekiem


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def pluginy() -> list:
    return sorted(d for d in PLUGINS.iterdir() if (d / ".claude-plugin/plugin.json").exists())


def skille(plugin: Path) -> list:
    return sorted(d for d in (plugin / "skills").iterdir() if d.is_dir())


def waliduj() -> list:
    bledy = []
    # manifesty i wersje
    try:
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        gem = json.loads((ROOT / "gemini-extension.json").read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return [f"Manifest JSON nieczytelny: {e}"]
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8") if (ROOT / "CHANGELOG.md").exists() else ""
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    nazwy_skilli = {}
    for pl in pluginy():
        try:
            plugin = json.loads((pl / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            bledy.append(f"{pl.name}: plugin.json nieczytelny: {e}")
            continue
        nazwa, wersja = plugin.get("name", ""), plugin.get("version", "")
        if nazwa != pl.name:
            bledy.append(f"{pl.name}: name w plugin.json ({nazwa}) ≠ nazwa katalogu")
        wpisy = [p for p in market.get("plugins", []) if p.get("name") == nazwa]
        if not wpisy:
            bledy.append(f"marketplace.json: brak wpisu dla pluginu {nazwa}")
        elif not (ROOT / wpisy[0].get("source", "")).joinpath(".claude-plugin/plugin.json").exists():
            bledy.append(f"marketplace.json: source pluginu {nazwa} nie wskazuje katalogu pluginu")
        if not NAME_RE.match(nazwa):
            bledy.append(f"{pl.name}: name nie jest kebab-case")
        if not re.match(r"^\d+\.\d+\.\d+$", wersja):
            bledy.append(f"{pl.name}: version nie jest semver X.Y.Z")
        if nazwa == "dom-budowa" and wersja != gem.get("version"):
            bledy.append(f"Różne wersje: dom-budowa {wersja} vs gemini-extension.json {gem.get('version')}")
        if not re.search(rf"^## {re.escape(nazwa)} \[{re.escape(wersja)}\]", changelog, re.M):
            bledy.append(f"CHANGELOG.md: brak nagłówka „## {nazwa} [{wersja}] – data”")
        kontekst = KONTEKST.get(nazwa)
        if not kontekst or not (pl / "skills" / kontekst / "SKILL.md").exists():
            bledy.append(f"{pl.name}: brak skilla kontekstowego (słownik KONTEKST w tools/build.py)")
            continue
        router = (pl / "skills" / kontekst / "SKILL.md").read_text(encoding="utf-8")
        for d in skille(pl):
            if d.name in nazwy_skilli:
                bledy.append(f"{d.name}: ta sama nazwa skilla w {nazwy_skilli[d.name]} i {pl.name} – nazwy muszą być unikalne")
            nazwy_skilli[d.name] = pl.name
            sk = d / "SKILL.md"
            if not sk.exists():
                bledy.append(f"{pl.name}/{d.name}: brak SKILL.md")
                continue
            fm = frontmatter(sk)
            if fm.get("name") != d.name:
                bledy.append(f"{d.name}: name we frontmatter ({fm.get('name')}) ≠ nazwa katalogu")
            if not NAME_RE.match(d.name):
                bledy.append(f"{d.name}: nazwa katalogu nie jest kebab-case")
            desc = fm.get("description", "")
            if not desc:
                bledy.append(f"{d.name}: brak description")
            elif len(desc) > 1024:
                bledy.append(f"{d.name}: description ma {len(desc)} znaków (max 1024)")
            if desc and desc[0] not in "\"'" and (": " in desc or " #" in desc):
                bledy.append(f"{d.name}: description z „: ” albo „ #” bez cudzysłowu to niepoprawny YAML – ujmij w \"…\"")
            if d.name != kontekst:
                if f"plugins/{pl.name}/skills/{d.name}/SKILL.md" not in agents:
                    bledy.append(f"{d.name}: brak w tabeli procedur w AGENTS.md (plugins/{pl.name}/skills/{d.name}/SKILL.md)")
                if f"`{d.name}`" not in router:
                    bledy.append(f"{d.name}: brak w mapie procedur w skills/{kontekst}/SKILL.md")
            linie = len(sk.read_text(encoding="utf-8").splitlines())
            if linie > 200:
                bledy.append(f"{d.name}: SKILL.md ma {linie} linii – przenieś szczegóły do references/")
            # odwołania do references/ muszą istnieć
            for ref in re.findall(r"`(references/[\w\-./]+)`", sk.read_text(encoding="utf-8")):
                if not (d / ref).exists():
                    bledy.append(f"{d.name}: odwołanie do nieistniejącego {ref}")
    bledy += kontrola_odeslan()
    bledy += kontrola_prywatnosci()
    return bledy


def kontrola_odeslan() -> list:
    """Odesłania `references/x.md` i `<skill>/references/x.md` we wszystkich plikach .md pluginów (nie tylko w SKILL.md):
    gołe – względem własnego skilla, z nazwą – względem skilla o tej nazwie w dowolnym pluginie."""
    skille_wszystkie = {d.name: d for pl in pluginy() for d in skille(pl)}
    bledy = []
    for d in skille_wszystkie.values():
        for f in sorted(d.rglob("*.md")):
            for m in re.finditer(r"`(?:([a-z0-9-]+)/)?(references/[\w\-./]+\.md)`", f.read_text(encoding="utf-8")):
                nazwa, ref = m.groups()
                if nazwa and nazwa not in skille_wszystkie:
                    continue  # inny zapis ścieżki (np. dom-budowa/skills/…)
                if not ((skille_wszystkie[nazwa] if nazwa else d) / ref).exists():
                    bledy.append(f"{f.relative_to(ROOT)}: odwołanie do nieistniejącego {m.group(0)}")
    return bledy


# --- kontrola prywatności (repo jest publiczne) -------------------------------------------
POMIJANE_KATALOGI = {".git", "dist", "dane", "__pycache__", "node_modules", ".agents", ".idea", ".maister"}
WZORCE = [
    (re.compile(r"(?<![\w-])(\+48[\s-]?)?\d{3}[\s-]?\d{3}[\s-]?\d{3}(?![\w-])"), "numer telefonu"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", re.I), "adres e-mail"),
    (re.compile(r"\b(dz\.?|działk\w*|nr ew\w*)\s*(nr\s*)?\d+/\d+", re.I), "numer działki"),
    (re.compile(r"\b\d{2}-\d{3}\b"), "kod pocztowy"),
    (re.compile(r"\b(ul\.|ulica)\s+[A-ZĄĆĘŁŃÓŚŹŻ]", re.U), "adres"),
    (re.compile(r"PESEL\D{0,5}\d{11}", re.I), "PESEL"),
    (re.compile(r"(?<![\w.-])\d{11}(?![\w.-])"), "PESEL (11 cyfr)"),
    (re.compile(r"(?<!\w)(?:PL ?)?\d{2}(?:[ ]?\d{4}){6}(?!\w)"), "numer konta"),
    (re.compile(r"\bNIP\D{0,5}\d{3}-?\d{2,3}-?\d{2}-?\d{2,3}\b|(?<![\w-])\d{3}-\d{3}-\d{2}-\d{2}(?![\w-])"), "NIP"),
    (re.compile(r"\b[A-Z]{2}\d[A-Z]/\d{8}/\d\b"), "numer księgi wieczystej"),
    (re.compile(r"\b(secre[t]_|n[t]n_|gh[pousr]_|github_pa[t]_|sk-ant-|xox[bp]-)[A-Za-z0-9_-]{16,}"
                r"|\bAIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----"),
     "token / klucz API"),
    # kwoty z „zł” albo „PLN” (z odstępami tysięcy i groszami); przykłady w procedurach pisz „N zł”
    (re.compile(r"(?<![\w.,])\d(?:[\d \u00a0.,]*\d)?\s?(?:zł|PLN)(?!\w)|\bPLN\s?\d"), "kwota"),
]
DOZWOLONE = [re.compile(r"noreply@anthropic\.com"),            # stopka Co-Authored-By
             re.compile(r"[\w.+-]+@users\.noreply\.github\.com")]  # anonimowy adres GitHuba
BINARNE = {".xlsx", ".xls", ".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".heic", ".zip",
           ".csv", ".tsv", ".ods", ".odt", ".rtf", ".pages", ".numbers", ".eml", ".msg",
           ".webp", ".gif", ".tif", ".tiff", ".mp4", ".mov", ".m4a", ".mp3", ".wav",
           ".sqlite", ".sqlite3", ".db", ".sqlite-wal", ".sqlite-shm", ".sqlite-journal",
           ".sqlite3-wal", ".sqlite3-shm", ".sqlite3-journal", ".db-wal", ".db-shm", ".db-journal"}
# dane obserwatora jakości wyszukiwania (tools/wiedza_jakosc.py): słowa wierszy indeksu i zapytania inwestora
DANE_OBSERWATORA = re.compile(r"(^|/)jakosc/|(^|/)(szukaj\.log.*\.jsonl|ki\.json|wlasne\.json|reczna-.*\.jsonl"
                              r"|porownanie-.*\.html|historia\.sqlite)$", re.I)


def zakazane_slowa() -> list:
    """Lista słów zakazanych trzymana POZA repo (`.dom/zakazane-w-repo.txt` w folderze budowy;
    sama lista w repo byłaby wyciekiem)."""
    out = []
    for lista in (ZAKAZANE, ROOT / "dane" / "prywatne.txt"):
        if lista.exists():
            out += [unicodedata.normalize("NFC", w.strip()).lower() for w in lista.read_text(encoding="utf-8").splitlines()
                    if w.strip() and not w.strip().startswith("#")]
    # wariant bez ogonków („zolw” dla „żółw”) – w wiadomościach i nazwach plików polskie znaki często znikają
    out += [w for w in {bez_ogonkow(x) for x in out} if w not in out]
    if not out:
        print(f"UWAGA: brak listy {ZAKAZANE} – sprawdzam tylko wzorce (telefon, e-mail, działka, kod, adres, PESEL, konto, NIP, KW, token, kwota)")
    return out


def bez_ogonkow(s: str) -> str:
    return unicodedata.normalize("NFKD", s.replace("ł", "l").replace("Ł", "L")).encode("ascii", "ignore").decode()


def jako_tekst(dane: bytes):
    """Treść pliku do sprawdzenia bez względu na rozszerzenie (.csv, .html, .sh, .bak-* też); binarny → None.
    Także „Tekst Unicode” z Excela/Notatnika (UTF-16 z BOM) i polski Windows (cp1250)."""
    if dane[:2] in (b"\xff\xfe", b"\xfe\xff"):
        try:
            return dane.decode("utf-16")
        except UnicodeDecodeError:
            return None
    if b"\0" in dane:
        return None
    try:
        return dane.decode("utf-8")
    except UnicodeDecodeError:
        return dane.decode("cp1250", errors="replace")


def sprawdz_tekst(etykieta: str, tekst: str, zakazane: list) -> list:
    bledy = []
    tekst = unicodedata.normalize("NFC", tekst)  # nazwy skopiowane z Findera bywają w NFD – lista jest w NFC
    for rx in DOZWOLONE:
        tekst = rx.sub("", tekst)
    for nr, linia in enumerate(tekst.splitlines(), 1):
        for rx, opis in WZORCE:
            if rx.search(linia):
                bledy.append(f"{etykieta}:{nr}: wygląda na {opis} – repo jest publiczne")
        niskie = re.sub(r"\s+", " ", linia.lower())  # „Imię  Nazwisko” z podwójną spacją albo tabulatorem
        if any(w in niskie for w in zakazane):
            bledy.append(f"{etykieta}:{nr}: słowo z listy zakazanych – repo jest publiczne, usuń lub uogólnij")
    return bledy


def kontrola_prywatnosci() -> list:
    """Dane osobowe/projektowe w plikach roboczych repo."""
    bledy, zakazane = [], zakazane_slowa()
    for f in sorted(ROOT.rglob("*")):
        rel = f.relative_to(ROOT)
        if (not f.is_file() or set(rel.parts) & POMIJANE_KATALOGI
                or rel.as_posix().startswith((".claude/skills", ".claude/worktrees"))):
            continue
        if f.suffix.lower() in BINARNE or DANE_OBSERWATORA.search(rel.as_posix()):
            bledy.append(f"{rel}: plik z danymi w repo – dokumenty trzymaj w folderze budowy")
            continue
        tekst = jako_tekst(f.read_bytes())
        if tekst is not None:
            bledy += sprawdz_tekst(str(rel), tekst, zakazane)
    return bledy


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def sprawdz_osobe(etykieta: str, imie: str, email: str, zakazane: list) -> list:
    bledy = []
    if not any(rx.fullmatch(email) for rx in DOZWOLONE):
        bledy.append(f"{etykieta}: e-mail „{email}” trafi do publicznej historii – ustaw "
                     "`git config user.email <id>+<login>@users.noreply.github.com`")
    if any(w in unicodedata.normalize("NFC", imie).lower() for w in zakazane):
        bledy.append(f"{etykieta}: imię/nazwisko „{imie}” jest na liście zakazanych – ustaw `git config user.name <login>`")
    return bledy


def kontrola_tozsamosci() -> list:
    """Autor i commiter, którzy trafią do nowego commita (pre-commit)."""
    zakazane, bledy = zakazane_slowa(), []
    for rola, zmienna in (("autor", "GIT_AUTHOR_IDENT"), ("commiter", "GIT_COMMITTER_IDENT")):
        m = re.match(r"(.*) <(.*)> \d+ [+-]\d+$", git("var", zmienna).strip())
        if m:
            bledy += sprawdz_osobe(rola, m.group(1), m.group(2), zakazane)
    return bledy


def kontrola_wiadomosci(plik: str) -> list:
    """Treść wiadomości commita (commit-msg). Linie z „#” też: przy `-m` i `-F` git je zostawia w wiadomości;
    pomijany jest tylko podgląd zmian `commit -v` (pod linią nożyczek)."""
    tekst = Path(plik).read_text(encoding="utf-8").split("# ------------------------ >8 ------------------------")[0]
    return sprawdz_tekst("wiadomość commita", tekst, zakazane_slowa())


def kontrola_commitow(zakres: list) -> list:
    """Wszystko, co wychodzi na GitHub (pre-push): metadane, wiadomości i treść zmienionych plików
    w każdym wysyłanym commicie – także tych zrobionych z pominięciem hooków (--no-verify)."""
    zakazane, bledy = zakazane_slowa(), []
    for sha in git("rev-list", *zakres).split():
        k = sha[:7]
        an, ae, cn, ce = git("show", "-s", "--format=%an%n%ae%n%cn%n%ce", sha).splitlines()[:4]
        bledy += sprawdz_osobe(f"{k} autor", an, ae, zakazane) + sprawdz_osobe(f"{k} commiter", cn, ce, zakazane)
        bledy += sprawdz_tekst(f"{k} wiadomość", git("show", "-s", "--format=%B", sha), zakazane)
        # -z: ścieżki z polskimi znakami bez cudzysłowów i ósemkowych kodów (inaczej plik byłby pominięty);
        # -c: w scaleniu pliki różne od wszystkich rodziców – treść wniesiona przy rozwiązaniu konfliktu
        for sciezka in filter(None, git("diff-tree", "-z", "-c", "--no-commit-id", "-r", "--root", "--name-only",
                                        "--diff-filter=AMR", sha).split("\0")):
            if (Path(sciezka).suffix.lower() in BINARNE or DANE_OBSERWATORA.search(sciezka)
                    or sciezka.startswith("dane/")):
                bledy.append(f"{k} {sciezka}: plik z danymi w commicie")
                continue
            r = subprocess.run(["git", "show", f"{sha}:{sciezka}"], cwd=ROOT, capture_output=True)
            tresc = jako_tekst(r.stdout) if r.returncode == 0 else None
            if tresc is not None:
                bledy += sprawdz_tekst(f"{k} {sciezka}", tresc, zakazane)
    return bledy


def zbuduj_plugin(pl: Path) -> Path:
    out = DIST / f"{pl.name}.plugin"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(pl.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts and f.name != ".DS_Store":  # Finder: spis plików folderu
                z.write(f, f.relative_to(pl).as_posix())
    return out


def zbuduj_gem(wersja: str) -> Path:
    gem = DIST / "gemini-gem"
    if gem.exists():
        shutil.rmtree(gem)
    (gem / "wiedza").mkdir(parents=True)
    instr = [f"<!-- dom-budowa {wersja} – wygenerowane przez tools/build.py, nie edytuj ręcznie -->",
             (ROOT / "AGENTS.md").read_text(encoding="utf-8"),
             "\n## Jak korzystać z plików wiedzy\n",
             "Każda procedura jest w osobnym pliku wiedzy `procedura-<nazwa>.md`. Gdy zadanie pasuje do procedury, "
             "przeczytaj ten plik w całości i wykonaj kroki. Ścieżki `skills/<nazwa>/...` w tekście oznaczają "
             "odpowiedni plik wiedzy. Narzędzia Notion mogą być niedostępne – wtedy przygotuj wpisy do wklejenia.",
             "\nTen Gem ma tylko procedury budowy (`dom-budowa`). Procedur pluginu `ja` (`plugins/ja/skills/...`: "
             "Dziennik, zadania prywatne, emocje, dziecko, suplementy, przegląd dnia, rozwój harnessu) tu nie ma – "
             "w takich sprawach napisz to w pierwszym zdaniu i nie zgaduj procedury; w sprawach budowy pomiń krok "
             "z wczytaniem `plugins/ja/skills/ja/SKILL.md` i zacznij od `procedura-budowa.md`."]
    (gem / "instrukcje.md").write_text("\n".join(instr), encoding="utf-8")
    for d in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        czesci = [f"<!-- dom-budowa {wersja} / skills/{d.name} -->", (d / "SKILL.md").read_text(encoding="utf-8")]
        for ref in sorted((d / "references").glob("*.md")) if (d / "references").exists() else []:
            czesci.append(f"\n\n---\n# Plik: skills/{d.name}/references/{ref.name}\n")
            czesci.append(ref.read_text(encoding="utf-8"))
        (gem / "wiedza" / f"procedura-{d.name}.md").write_text("\n".join(czesci), encoding="utf-8")
    return gem


def zbuduj_claude_projekt(wersja: str) -> Path:
    zrodlo = (PLUGINS / "ja/skills/rozwoj-harnessu/references/claude-ai-projekt.md").read_text(encoding="utf-8")
    m = re.search(r"<!-- instrukcje-start -->\n(.*?)<!-- instrukcje-koniec -->", zrodlo, re.S)
    if not m:
        raise SystemExit("claude-ai-projekt.md: brak znaczników instrukcje-start / instrukcje-koniec")
    out = DIST / "claude-ai-projekt" / "instrukcje.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"(Instrukcje projektu „Dom”, harness dom-budowa {wersja})\n\n{m.group(1)}", encoding="utf-8")
    return out


def odswiez_dowiazania(kopiuj: bool = False):
    """.claude/skills i .agents/skills: katalog z dowiązaniem (albo kopią – Windows) na każdy skill każdego pluginu."""
    for kat in (ROOT / ".agents/skills", ROOT / ".claude/skills"):
        if kat.is_symlink() or kat.is_file():
            kat.unlink()  # stary układ: jedno dowiązanie do plugins/dom-budowa/skills
        kat.mkdir(parents=True, exist_ok=True)
        oczekiwane = {d.name: d for pl in pluginy() for d in skille(pl)}
        for wpis in list(kat.iterdir()):
            if wpis.name not in oczekiwane or kopiuj != (not wpis.is_symlink()):
                wpis.unlink() if wpis.is_symlink() or wpis.is_file() else shutil.rmtree(wpis)
        for nazwa, d in oczekiwane.items():
            cel = kat / nazwa
            if cel.exists() or cel.is_symlink():
                if kopiuj:
                    shutil.rmtree(cel)
                    shutil.copytree(d, cel)
                continue
            if kopiuj:
                shutil.copytree(d, cel)
            else:
                cel.symlink_to(os.path.relpath(d, kat))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tylko-walidacja", action="store_true")
    ap.add_argument("--kopiuj-dowiazania", action="store_true")
    ap.add_argument("--tozsamosc", action="store_true", help="pre-commit: autor i commiter")
    ap.add_argument("--wiadomosc", metavar="PLIK", help="commit-msg: treść wiadomości")
    ap.add_argument("--commity", metavar="ZAKRES", help="pre-push: zakres dla git rev-list, np. 'a..b' lub 'sha --not --remotes'")
    a = ap.parse_args()
    for flaga, kontrola in ((a.tozsamosc, kontrola_tozsamosci), (a.wiadomosc, lambda: kontrola_wiadomosci(a.wiadomosc)),
                            (a.commity, lambda: kontrola_commitow(a.commity.split()))):
        if flaga:
            bledy = kontrola()
            for b in bledy:
                print("  ✗", b)
            return 1 if bledy else 0
    bledy = waliduj()
    if bledy:
        print("WALIDACJA – BŁĘDY:")
        for b in bledy:
            print("  ✗", b)
        return 1
    print("Walidacja OK (" + ", ".join(f"{pl.name}: {len(skille(pl))}" for pl in pluginy()) + " procedur).")
    if a.tylko_walidacja:
        return 0
    DIST.mkdir(exist_ok=True)
    blokada = open(DIST / ".build.lock", "w")  # równoległe sesje: drugi build czeka, zamiast psuć dist/ i dowiązania
    if fcntl:
        fcntl.flock(blokada, fcntl.LOCK_EX)
    odswiez_dowiazania(kopiuj=a.kopiuj_dowiazania)
    wersja = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    for pl in pluginy():
        print("Zbudowano:", zbuduj_plugin(pl).relative_to(ROOT))
    print("Zbudowano:", zbuduj_gem(wersja).relative_to(ROOT), "(instrukcje.md + wiedza/)")
    print("Zbudowano:", zbuduj_claude_projekt(wersja).relative_to(ROOT), "(wklej w projekt „Dom” → Instructions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
