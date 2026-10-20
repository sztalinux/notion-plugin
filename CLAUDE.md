@AGENTS.md

## Claude Code w tym repozytorium – obowiązkowo na starcie każdej sesji

To repozytorium jest źródłem harnessu – dwóch pluginów: `ja` (`plugins/ja/skills/`) i `dom-budowa`
(`plugins/dom-budowa/skills/`). Procedury czytasz z dysku (`.claude/skills/` – dowiązanie na każdy skill obu pluginów,
odtwarza je `python3 tools/build.py`), a nie z pluginów zainstalowanych na koncie (te są tu wyłączone w `.claude/settings.json`).

Zanim zajmiesz się czymkolwiek innym:

0. Jednorazowo (jeśli `git config core.hooksPath` nie zwraca `.githooks`): `git config core.hooksPath .githooks`
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
1. `git pull` – żeby pracować na aktualnej wersji.
2. Sprawdź skrzynkę **„Zmiany do harnessu”** w Notion (`collection://e217448a-60ec-4af6-8584-8f368315109c`),
   wpisy ze Statusem „Do wdrożenia” **albo pustym** (inwestor dodaje je ręcznie bez pól – uzupełnij je, HZ-3).
3. Jeśli są – wdroż je od razu wg `plugins/ja/skills/rozwoj-harnessu/SKILL.md`, sekcja „Wdrożenie”
   (zmiana plików → wersja → CHANGELOG → `python3 tools/build.py` → commit → push → oznaczenie wpisów jako „Wdrożone”).
   Jeśli wpis jest niejasny albo sprzeczny z inną procedurą – zapytaj inwestora, zanim go wdrożysz.
4. Jeśli skrzynka jest pusta – napisz jedną linię „Harness aktualny (dom-budowa X.Y.Z, ja X.Y.Z)”.
4a. Baza **„Pomysły na rozwój”** (`collection://fdee4f05-8f43-4be4-a0d5-2b88642fa6d3`): dopisz jedną linię „Pomysły: n nowych do analizy,
    m »Do zrobienia«” (pomiń przy zerach). Niczego z niej nie wdrażaj bez polecenia „zrób POM-n”
    (`rozwoj-harnessu`, sekcja C).
5. Raport „[dokumenty]” z hooka startowego (`tools/dokumenty.py`): „Przewodnik zmieniony” → od razu przepisz stronę
   przewodnika w Notion (`dokumenty`, sekcja C), bez pytania. Jeśli są nowe pliki do sklasyfikowania –
   zaproponuj ich obsługę wg `plugins/dom-budowa/skills/dokumenty/SKILL.md` (jedna linia); jeśli jest lista
   „Kopia awaryjna” – nie przypominaj (wgrywanie opcjonalne). Potem przejdź do zadania.

**Repo jest publiczne** – przed każdym commitem sprawdź, że nie ma w nim danych osobowych ani danych projektu
(walidator i hook `pre-commit` pomagają, ale nie zastępują przejrzenia `git diff`).

Nie pomijaj tego kroku, nawet gdy pierwsza wiadomość dotyczy czegoś innego – wykonaj go najpierw, krótko.
