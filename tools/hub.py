"""Folder budowy (hub) dla narzędzi z tools/ – także uruchomionych z kopii roboczej git (`.claude/worktrees/<nazwa>`).

Kolejność: zmienna DOM_HUB (ustawiona i niepusta), inaczej dwa poziomy nad GŁÓWNĄ kopią repo (…/Dom/AI/dom → …/Dom).
Kopia robocza ma zamiast katalogu `.git` plik „gitdir: <repo>/.git/worktrees/<nazwa>” – bez tego narzędzie z kopii
roboczej trafiałoby w `AI/dom/.claude` i zakładało tam śmieciowe `.dom/` (logika jak `glowna_kopia` w build.py).

Zapis z kopii roboczej: polecenie zapisujące woła `zapis_zablokowany(REPO, <cele zapisu>)` – odmowa, gdy narzędzie działa
z kopii roboczej, DOM_HUB nie jest ustawione jawnie, a cel zapisu leży w prawdziwym folderze budowy (cel w katalogu
tymczasowym z BUDZET_DANE, ZDJECIA_DANE, KOPIA_DANE albo z testu – wolno). Tylko biblioteka standardowa, bez efektów
ubocznych przy imporcie.
"""
import os
from pathlib import Path

ODMOWA = "✗ kopia robocza: ustaw DOM_HUB albo uruchom z głównej kopii"


def glowna_kopia(root: Path) -> Path:
    """Główna kopia repo dla `root`; dla zwykłej kopii – `root` bez zmian (ta sama logika co build.glowna_kopia)."""
    root = Path(root)
    g = root / ".git"
    if g.is_file():
        t = g.read_text(encoding="utf-8").strip()
        if t.startswith("gitdir:"):
            return (g.parent / t[7:].strip()).resolve().parent.parent.parent  # ścieżka bywa względna
    return root


def domyslny_hub(repo: Path) -> Path:
    """Prawdziwy folder budowy – dwa poziomy nad główną kopią, bez względu na DOM_HUB (dla zabezpieczeń)."""
    return glowna_kopia(repo).parent.parent.expanduser().resolve()


def folder_budowy(repo: Path) -> Path:
    """Folder budowy dla narzędzia z repo `repo`: DOM_HUB (niepuste) albo `domyslny_hub`."""
    env = os.environ.get("DOM_HUB")
    return Path(env).expanduser().resolve() if env else domyslny_hub(repo)


def kopia_robocza(repo: Path) -> bool:
    """Narzędzie działa z kopii roboczej git (nie z głównej kopii)."""
    return glowna_kopia(repo).resolve() != Path(repo).resolve()


def tylko_odczyt(repo: Path, *cele) -> bool:
    """Kopia robocza bez jawnego DOM_HUB, a któryś cel zapisu leży w prawdziwym folderze budowy – zapisu nie robimy."""
    if os.environ.get("DOM_HUB") or not kopia_robocza(repo):
        return False
    prawdziwy = domyslny_hub(repo)
    for c in cele:
        s = Path(c).expanduser().resolve()
        if s == prawdziwy or prawdziwy in s.parents:
            return True
    return False


def zapis_zablokowany(repo: Path, *cele) -> bool:
    """Jak `tylko_odczyt`, a przy blokadzie wypisuje jedną linię odmowy – wywołujący kończy z kodem 1."""
    if tylko_odczyt(repo, *cele):
        print(ODMOWA)
        return True
    return False
