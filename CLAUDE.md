@AGENTS.md

## Claude Code w tym repozytorium – start sesji i zasady pracy

To repozytorium jest źródłem harnessu – dwóch pluginów: `ja` (`plugins/ja/skills/`) i `dom-budowa`
(`plugins/dom-budowa/skills/`). Procedury czytasz z dysku (`.claude/skills/` – dowiązanie na każdy skill obu pluginów,
odtwarza je `python3 tools/build.py`), a nie z pluginów zainstalowanych na koncie (te są tu wyłączone w `.claude/settings.json`).

### Start sesji: jedna linia stanu, bez pytań

Na starcie sesji przeczytaj `<folder budowy>/.dom/automaty/stan-sesji.txt` i pokaż jego jedyną linię bez komentarza, potem od razu zadanie
z pierwszej wiadomości. Nie czytaj Notion i nie uruchamiaj skryptów na starcie; nie zadawaj pytania z listą opcji. Brak pliku albo plik starszy
niż 36 h → linia „Stan: brak świeżych danych z nocnego przebiegu”. Linię składa `przeglad.py` po każdym przebiegu (wersje harnessu w repo i na koncie,
stan ostatnich przebiegów) – bez POM i ZP. Gdy konto ma starsze pluginy niż repo, powiedz to jednym zdaniem.

Polecenia w trakcie sesji (działają tak samo jak dawne pozycje listy): „wdróż” (skrzynka zmian: `git pull`, wpisy „🤖 Zmiany asystenta” (Zasady) ze Statusem
„Do zrobienia” albo pustym – `rozwoj-harnessu`, sekcja „Wdrożenie”), „zrób POM-n” i „przeanalizuj pomysły” (tylko na prośbę), „zrób ZP-n”, „odśwież indeks”
(`python3 tools/wiedza.py sync --publikuj --cicho`), „posortuj dokumenty” (`python3 tools/dokumenty.py`, procedura `dokumenty`), „stan kopii”
(`tools/zdjecia.py stan`, `tools/kopia.py stan`, `tools/kopie.py stan`) i „rozłóż zdjęcia” (`dziennik`, `references/zdjecia-i-kopia.md`).

### Zasady pracy w repo

0. Przed pierwszym commitem w sesji (jeśli `git config core.hooksPath` nie zwraca `.githooks`): `git config core.hooksPath .githooks`
   – włącza hooki prywatności: `pre-commit` (pliki + autor), `commit-msg` (wiadomość), `pre-push` (każdy wysyłany commit).
   Autor commitów: imię inwestora albo login – dozwolone; e-mail tylko `…@users.noreply.github.com` (historia jest publiczna).
   W historii nigdy nie mogą się znaleźć dane innych osób (projektanci, wykonawcy, urzędy) – raz wypchniętych
   nie da się skutecznie usunąć, więc kontrola musi zadziałać przed pushem. Nie przepisuj opublikowanej historii
   (force push zostawia stare commity dostępne po SHA) – chyba że wyciekły dane; wtedy zatrzymaj się i zapytaj inwestora.
0a. **Równoległe sesje Claude to norma, nie przeszkoda.** Nie zatrzymuj się z ich powodu i nie wspominaj o nich
    w odpowiedzi, dopóki nic realnie nie koliduje. Z `git status` korzystaj tylko po to, żeby commitować wyłącznie własne
    pliki (`git add <pliki>`, nie `git add -A`; obce zmiany zostaw bez komentarza). Zatrzymaj się dopiero na realnej
    kolizji zauważonej w trakcie pracy: obce niezacommitowane zmiany w tym samym miejscu pliku, który sam edytujesz,
    albo ta sama strona lub baza Notion jest właśnie zmieniana w sposób wykluczający Twój zapis. Zrób wtedy wszystko, co się
    da bez kolizji, a kolizję zgłoś w bloku „🛑 Potrzebuję Twojej odpowiedzi” (format odpowiedzi – `AGENTS.md`, zasady).
    Przed commitem `git pull` – gdy inna sesja podbiła wersję pluginu, ustaw swoją wyżej.

**Repo jest publiczne** – przed każdym commitem sprawdź, że nie ma w nim danych osobowych ani danych projektu
(walidator i hook `pre-commit` pomagają, ale nie zastępują przejrzenia `git diff`).
