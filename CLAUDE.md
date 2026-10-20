@AGENTS.md

## Claude Code w tym repozytorium – start sesji i zasady pracy

To repozytorium jest źródłem harnessu – dwóch pluginów: `ja` (`plugins/ja/skills/`) i `dom-budowa`
(`plugins/dom-budowa/skills/`). Procedury czytasz z dysku (`.claude/skills/` – dowiązanie na każdy skill obu pluginów,
odtwarza je `python3 tools/build.py`), a nie z pluginów zainstalowanych na koncie (te są tu wyłączone w `.claude/settings.json`).

### Start sesji: lista wyboru, domyślnie nic

Na starcie nic nie uruchamia się samo (hooków startowych nie ma w `.claude/settings.json`) – inwestor nie zawsze chce, żeby
sesja coś robiła. Pierwszą czynnością sesji, przed czymkolwiek innym i także gdy pierwsza wiadomość jest zadaniem, jest jedno
pytanie z listą wielokrotnego wyboru (narzędzie AskUserQuestion, `multiSelect`), **bez żadnej zaznaczonej pozycji**:

- Pytanie „Harness i repo”:
  - **Skrzynka zmian** – `git pull`; wpisy „Zmiany do harnessu” (`collection://e217448a-60ec-4af6-8584-8f368315109c`) ze Statusem
    „Do wdrożenia” **albo pustym** (inwestor dodaje je ręcznie bez pól – uzupełnij je, HZ-3) wdroż wg
    `plugins/ja/skills/rozwoj-harnessu/SKILL.md`, sekcja „Wdrożenie” (zmiana plików → wersja → CHANGELOG →
    `python3 tools/build.py` → commit → push → oznaczenie wpisów jako „Wdrożone”). Wpis niejasny albo sprzeczny z inną
    procedurą – zapytaj inwestora przed wdrożeniem. Skrzynka pusta – jedna linia „Harness aktualny (dom-budowa X.Y.Z, ja X.Y.Z)”.
  - **Pomysły** – jedna linia „Pomysły: n nowych do analizy, m »Do zrobienia«” z bazy „Pomysły na rozwój”
    (`collection://fdee4f05-8f43-4be4-a0d5-2b88642fa6d3`; pomiń przy zerach). Niczego z niej nie analizuj ani nie wdrażaj bez
    polecenia „zrób POM-n” (`rozwoj-harnessu`, sekcja C).
  - **git pull** – zaktualizuj repo.
- Pytanie „Dane i dokumenty”:
  - **Dokumenty budowy** – `python3 tools/dokumenty.py`; „Przewodnik zmieniony” → od razu przepisz stronę przewodnika w Notion
    (`dokumenty`, sekcja C), bez pytania. Nowe pliki do sklasyfikowania – zaproponuj ich obsługę wg
    `plugins/dom-budowa/skills/dokumenty/SKILL.md` (jedna linia); listy „Kopia awaryjna” nie przypominaj.
  - **Indeks wiedzy** – `python3 tools/wiedza.py sync --publikuj --cicho`, potem `python3 tools/wiedza_jakosc.py przypomnij --cicho`;
    wynik w jednej linii.

Wykonaj tylko to, co inwestor zaznaczył. Brak zaznaczenia, odrzucenie pytania albo „nic” = nic z listy, od razu zadanie
z pierwszej wiadomości. Przed wyborem nie czytaj Notion i nie uruchamiaj skryptów (opisy opcji bez liczb). Gdy pytanie jest
niemożliwe (tryb nieinteraktywny) – pomiń listę i nic nie uruchamiaj. Prośba w trakcie sesji („wdróż skrzynkę”, „odśwież
indeks”) działa tak samo jak zaznaczenie.

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
