# Indeks wiedzy – jak używać

Cel: znaleźć w Bazie wiedzy informacje, tematy i sprzeczności szybko, bez przeszukiwania Notion (jest wolne i limitowane).
Indeks to lokalna kopia czterech baz (SQLite FTS5), tylko do odczytu. Notion zostaje jedynym źródłem prawdy i jedynym
miejscem zapisu – nigdy nie zapisuj wiedzy do indeksu. Trzy kanały dostępu mają różne polecenia; wybierz swój.

## Claude Code – sesja interaktywna w repo

Indeks odświeża się na żądanie – pozycją „Indeks wiedzy” z listy startowej Claude Code albo poleceniem `sync` poniżej; bez tego bywa
nieaktualny. Polecenia uruchamiaj z katalogu repo:
- `python3 tools/wiedza.py szukaj "przerwa robocza płyta" [--etap "Stan zero"] [--limit 12]` – wpisz 2–4 słowa
  treściowe, bez zdania i spójników („czy”, „jak”, „na” program i tak odrzuci). Końcówki fleksyjne program przycina sam,
  więc „drenażu” znajdzie też „drenaż” (wyżej stoją informacje z dokładnie wpisaną formą). `drena*` (prefiks)
  i „fraza w cudzysłowie” zostają dokładnie takie, jak wpisano. Gdy do wszystkich słów pasuje mniej niż 12 widocznych
  informacji, program dopisuje pod nimi pasujące do części słów (nie przy zapytaniu z samych słów wypełniających) –
  przy pytaniach z 3+ słowami to zwykły przypadek. Nagłówek mówi wtedy „(dopasowanie częściowe od pozycji k)”,
  a `--json` – `"czesciowe": true` i `"pelnych": n` (k = n + 1; n = ile informacji ma wszystkie słowa, 0 = żadna).
  Dopisane linie idą od pasujących do największej liczby słów; traktuj je jak wskazówkę i nie opieraj na nich
  odpowiedzi bez przeczytania tezy. Mało pełnych trafień (`pelnych` 0–2) → zapytaj krócej, o jedno pojęcie naraz
  (np. „przemarzanie”, potem „posadowienie”). Domyślnie pomija Nieaktualne i Ciekawostki (z licznikiem);
  `--ciekawostki` pokaże też je. Zero linii wyniku po filtrach to nie brak wiedzy – zobacz liczniki `pominięto`
  i rozluźnij filtr.
- `python3 tools/wiedza.py temat "NAZWA"` – stan wiedzy tematu, Kluczowe i otwarte SP; `duplikaty [--od RRRR-MM-DD]` –
  pary o bardzo podobnej tezie; `stan` – liczniki i daty.

Linia wyniku: `WI-n · Istotność · Etap · Status · teza · T: tematy · ZRD-n „tytuł” (Kto: …; typ autora; wiarygodność) · SP-n · link`.
- Segment `Kto` jest obowiązkowy: bez niego nie zastosujesz reguły „ten sam autor to nie potwierdzenie” (`wiedza`, A.5).
- Marker `ustalenie w Notatniku` w miejscu źródła: informacja nie ma źródła w bazie Źródeł, opiera się na ustaleniu
  zapisanym w Notatniku budowy. Otwórz je z linku w wierszu, zanim oprzesz na niej decyzję – indeks nie niesie więcej.
- `💬 komentarz inwestora:` na końcu linii to pole „Mój komentarz” – czytaj je i reaguj wg `wiedza`, sekcja H.
- Sekcja „Otwarte sprzeczności w trafieniach” zbiera SP ze wszystkich trafień. SP z dopiskiem „(tylko w dalszych
  trafieniach)” nie niesie żadna pokazana linia – otwórz je z linku albo zwiększ `--limit`.

Czytaj Notion (stronę z linku) mimo wyniku z indeksu, gdy:
- potrzebujesz szczegółów (Szczegóły, Fragment), podejmujesz decyzję albo zaraz zapisujesz wiedzę;
- indeks jest niedostępny (brak pliku, stara wersja schematu – wtedy `python3 tools/wiedza.py sync`) – wróć do dotychczasowej drogi;
- data stanu (nagłówek wyniku `# indeks: stan …` i `stan`) jest starsza niż 24 h – podaj ją w odpowiedzi.

Po zapisie wiedzy do Notion w sesji interaktywnej uruchom `python3 tools/wiedza.py sync --publikuj` (indeks i kopia dla czatu).

## Czat/telefon i zaplanowane zadania na claude.ai

Tu nie ma `tools/` ani repo. Przeczytaj raz na rozmowę stronę Notion „🔑 Asystent – dostęp” (`3fcf5982-09e7-810e-aaca-f2b582438924`)
i wstaw jej pola w miejsce `<GITHUB_REPO>` i `<TOKEN>`. Nigdy nie zapisuj tokena w odpowiedzi, notatce ani pliku.

```
curl -sf -H "Authorization: Bearer <TOKEN>" -H "Accept: application/vnd.github.raw" -o /tmp/wiedza.sqlite https://api.github.com/repos/<GITHUB_REPO>/contents/wiedza.sqlite
curl -sf -H "Authorization: Bearer <TOKEN>" -H "Accept: application/vnd.github.raw" -o /tmp/wiedza.py https://api.github.com/repos/<GITHUB_REPO>/contents/wiedza.py
python3 /tmp/wiedza.py szukaj "przerwa robocza" --db /tmp/wiedza.sqlite
```

- Pozostałe polecenia (`temat`, `duplikaty`, `stan`) mają ten sam kształt co w Claude Code, z `--db /tmp/wiedza.sqlite`.
- Katalog `/tmp` bywa pusty w kolejnej wiadomości – pobierz oba pliki ponownie (stronę dostępu masz już przeczytaną).
- Brak strony, tokena, sieci albo błąd pobrania → napisz „indeks niedostępny” i czytaj Notion bezpośrednio.
- Nie uruchamiaj `sync` ani `publikuj`. Po zapisie wiedzy napisz wprost: „indeks dogoni przy najbliższym sync na Macu”.
- Daty w kopii podawaj informacyjnie: bez nowych danych nie ma nowej publikacji, więc starsza data nie jest alarmem.

## Przebieg nocny (skrypty `claude -p`)

Katalog roboczy jest neutralny, hooków repo nie ma. Uruchamiaj wyłącznie `szukaj`, `temat`, `duplikaty` i `stan`,
przez bezwzględną ścieżkę `tools/wiedza.py` podaną w prompcie skryptu. Nigdy `sync` ani `publikuj` – sync po każdym filmie
robi skrypt. Notion przeszukuj tylko wtedy, gdy indeks nie odpowiada na pytanie.

## Ograniczenia kopii

- Wiersze usunięte w Notion znikają z indeksu przy pełnym sync (automatycznie co 7 dni albo `sync --pelny`) – do tego czasu
  sprawdź w Notion informację, na której opierasz decyzję.
- `stan`: `zbudowano` starsze niż 7 dni albo `ostatni pełny sync` starszy niż 14 dni → uruchom `sync --pelny` ręcznie;
  `kopia aktualna: nie` → `python3 tools/wiedza.py publikuj --teraz` (samo `publikuj` bywa odłożone przez odstęp 60 min).
- Awarie, odnowienie tokenów, odtworzone repo kopii i komunikaty `[wiedza]` → `references/indeks-awarie.md`; jakość
  wyszukiwania, log zapytań, alarmy `[jakosc]` (tylko Claude Code) → `references/indeks-jakosc.md`.
