# Adaptery dostawców – jak ten sam harness działa w różnych narzędziach

Jedno źródło: `plugins/dom-budowa/skills/` i `plugins/ja/skills/` + `AGENTS.md` w publicznym repo GitHub `sztalinux/notion-plugin`
(bez danych osobowych i danych budowy).
Poprawki zgłoszone z dowolnego miejsca czekają w Notion („Zmiany do harnessu”) i obowiązują od razu.

| Narzędzie | Skąd bierze harness | Uwagi |
|---|---|---|
| Claude Code (komputer) | folder repo: `CLAUDE.md` → `AGENTS.md`, skille z `.claude/skills` (dowiązanie) | jedyne miejsce, które zapisuje zmiany do repo (commit + push) |
| claude.ai – czat, telefon, Cowork | plugin z marketplace = repo GitHub; projekt „Dom”: Instructions + wiedza projektu (paczka `_Do claude.ai/`, procedura `dokumenty`) – `claude-ai-projekt.md` | nowa wersja: push z podbitym numerem, potem ręczne odświeżenie pluginu (`claude-ai-projekt.md`) albo „Sync automatically”, jeśli organizacja pozwala; hooki pluginu nie działają w czacie, działają w Cowork |
| Gemini CLI | `GEMINI.md` → `AGENTS.md`, `gemini-extension.json`, skille z `.agents/skills` | praca w katalogu repo; Notion jako serwer MCP w settings.json |
| Gemini w przeglądarce (Gem) | `dist/gemini-gem/` z `tools/build.py` | ręczne wgranie plików; brak automatycznego doboru procedur |
| Codex / inne zgodne z AGENTS.md | `AGENTS.md`, `.agents/skills` | praca w katalogu repo |

Uwagi:
- W Claude Code w folderze repo plugin z konta jest wyłączony (`.claude/settings.json`, `enabledPlugins`),
  żeby nie dublować skilli – obowiązują pliki z dysku.
- `.agents/skills/` i `.claude/skills/` to katalogi z dowiązaniem na każdy skill obu pluginów (odtwarza je `tools/build.py`).
  Na Windows bez obsługi symlinków: `python3 tools/build.py --kopiuj-dowiazania` (albo `git config core.symlinks true`
  i tryb dewelopera Windows).
- Gem dostaje na razie tylko `dom-budowa` (`dist/gemini-gem/`; instrukcje Gema mówią to wprost). Gemini CLI w katalogu
  repo czyta `AGENTS.md` (mapa obu pluginów) i `.agents/skills`, więc ma też `ja`; `gemini-extension.json` nosi nazwę
  i wersję `dom-budowa`.
- Dane (Notion, arkusz kosztorysu, dokumenty) nie są częścią pluginu. Pliki leżą w folderze budowy na komputerze (poza repo).
- W Claude Code w repo synchronizacja pluginów z claude.ai jest wyłączona lokalnie (`.claude/settings.local.json`,
  `syncClaudeAiPlugins: false`) – inaczej wersja z konta dublowałaby procedury z dysku.
