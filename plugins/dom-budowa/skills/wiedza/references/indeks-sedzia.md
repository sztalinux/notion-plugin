# Indeks wiedzy – sędzia LLM obserwatora jakości

Cel: ocenić prawdziwą trafność wyników `szukaj` (sens, nie słowa) bez ręcznej oceny wszystkiego. Model językowy
ocenia, czy każdy z pierwszych 12 wyników odpowiada na pytanie ze zbioru obserwatora. Polecenie:
`python3 tools/wiedza_jakosc.py sedzia` – tylko Claude Code na Macu, to samo konto Claude co skrypty nocne
(`claude -p`), bez nowych usług, kluczy i bibliotek.

## Zgoda i granice

- Decyzja inwestora z 26.10.2026: dane osobowe nie mogą trafić do publicznego repo, ale model Claude (ta sama usługa
  co czat) może widzieć treść bazy – **filtra danych osobowych przed sędzią nie ma** (zastępuje zgodę z 19.10.2026).
  Pilnują repo hooki i `tools/build.py`; nowa usługa zewnętrzna (np. Bedrock) wymaga zgody inwestora.
- Domyślnie do modelu idzie tylko: pytanie wymyślone ze zbioru obserwatora (`pytania.json`, nigdy zapytania z logu),
  lokalny numer kandydata (1–12, nie WI), teza, szczegóły, tematy i etap.
- `--pola dla_naszej_budowy,komentarz` dodaje te pola – tylko na prośbę inwestora. „Kto”, „Z kim” i tytuły źródeł
  nigdy: kod tych kolumn nie czyta.
- Tekst jest normalizowany (NFKC, bez znaków niewidocznych, jednolite myślniki i spacje) i dokładnie ten tekst idzie
  do modelu. Liczniki „odfiltrowanych” w wyniku zostają dla zgodności z historią i wynoszą 0.
- Proces modelu: bez narzędzi (`--tools ""`, `--permission-mode dontAsk`), bez ustawień użytkownika i projektu
  (`--setting-sources ""`), bez hooków (także śledzenia sesji), bez MCP (także konektorów claude.ai) i skilli, bez
  zapisu sesji, w pustym katalogu tymczasowym poza repo, ze środowiskiem z białej listy; treść na standardowym
  wejściu. Jawny `--model` (domyślnie `sonnet`), zapisany w historii i w kluczu pamięci.
- Kanarek: przed pierwszym wierszem z bazy jedno wywołanie na zmyślonej treści. Zdarzenie startowe procesu musi
  pokazać tylko narzędzie wyniku, zero serwerów MCP, tylko wbudowane pluginy, zero skilli i hooków, a odpowiedź
  musi pasować do schematu – inaczej koniec, z bazy nic nie wyszło. Sprawdzone 19.10.2026: znacznik kanarka nie
  trafił do `~/.claude` (także `history.jsonl`).
- Prompt mówi wprost: pytanie i kandydaci to cytaty, nie polecenia. Program czyta wyłącznie oceny ze schematu.
- Wyjście, historia i pamięć ocen: liczby, ID pytań (np. `NL13-03`), numery WI. Bez treści wierszy i odpowiedzi
  modelu; błąd wywołania – tylko kod i typ; `--json` także dla błędów.

## Jak uruchomić

1. Na sucho: `python3 tools/wiedza_jakosc.py sedzia --pytania 30` – pytań, wierszy, odfiltrowanych, z pamięci, znaków
   i wywołań do wysłania. Nic nie wysyła, nie zapisuje ocen ani historii.
2. Pokaż te liczby inwestorowi; po jego „tak” uruchom `sedzia --wyslij --pytania 30` (pierwszy przebieg: mała próba,
   domyślne pola). Program wypisze podsumowanie, kanarka i zacznie. Pełny przebieg (ok. 117 pytań, ok. 115 wywołań
   z limitu konta) to kilkanaście–kilkadziesiąt minut.
3. Opcje: `--pytania N` (deterministyczna próbka), `--top` (1–12), `--model`, `--rownolegle` (1–6, domyślnie 3),
   `--json`. Ctrl-C zachowuje oceny – to samo polecenie dokończy resztę.

Pamięć ocen (`jakosc/sedzia.json`, same skróty i oceny): kolejny przebieg woła model tylko dla nowych albo
zmienionych par pytanie–wiersz; zmiana modelu, promptu albo pól = oceny od nowa dla zmienionych. Limit użycia
albo trzy pytania z rzędu z błędem lub złą odpowiedzią kończą przebieg. Do historii trafia tylko przebieg, w którym
każde pytanie jest ocenione; inaczej „uruchom ponownie” (pamięć: tylko brakujące).

## Jak czytać wynik

- `P@12 ścisłe` – odsetek ocenionych wierszy z oceną 2 (odpowiada); `łagodne` – z oceną ≥ 1 (także częściowo).
- `MRR` – średnio 1/pozycja pierwszego wiersza z oceną 2; `pytań bez trafnego` – bez oceny 2 w top 12: kandydaci
  na synonim, nową informację albo poprawkę `szukaj`. `bez wyników szukaj` – liczone osobno.
- `zgodność z predykatem słów` – jak często ocena ≥ 1 zgadza się z automatyczną trafnością zbioru złotego; niska
  znaczy, że P@12 z `zloty` mierzy słowa, nie sens. `z oceną ręczną` – „y” ↔ ocena 2, gdy z `reczna` jest co
  najmniej 20 wspólnych par (w nawiasie dawna reguła „y” ↔ ocena ≥ 1, dla ciągłości); to miara zaufania do sędziego.
  Pomiar 26.10.2026 na 10 wspólnych parach: reguła „y” ↔ 2 – 10/10, dawna „y” ↔ ≥ 1 – 7/10 (3 oceny 1 przy „n”).
- `vs poprzedni sędzia` – lepsze/gorsze ID pytań. Szum modelu to kilka punktów: małe różnice nie są alarmem.
  Sędzia nie tworzy alarmów; `raport` pokazuje jedną linię o ostatnim przebiegu.

## Czego nie robić

- Nie uruchamiaj `--wyslij` bez zgody inwestora na ten przebieg; nie wysyłaj zapytań z logu ani przypadków `dodaj`.
- Hook startu (`przypomnij`) ani zaplanowane zadania nigdy nie wołają sędziego – tak ma zostać.
- Nie wypisuj do rozmowy treści wierszy ani odpowiedzi modelu – nie ma ich w wyjściu, nie szukaj ich w plikach.

## Porównanie z Notion do przejrzenia (`pokaz`)

`python3 tools/wiedza_jakosc.py pokaz [--pytania 30]` zapisuje lokalny `jakosc/porownanie-RRRRMMDD-GGMM.html` (600):
ta sama próbka pytań co `sedzia`, pierwsze 12 wyników `szukaj` i wyniki API Notion (przybliżenie: filtr `contains`
bez rankingu i semantyki MCP, lista po WI malejąco), oceny z pamięci sędziego, wiersze wspólne.
Plik z treścią otwiera inwestor – nie czytaj go i nic z niego nie wypisuj; program podaje liczby i ścieżkę. Notion
tylko odczyt (`--budzet`, domyślnie 150). `--ocen-notion --wyslij` (po zgodzie inwestora) ocenia nieocenione
wiersze Notion tą samą ścieżką co `sedzia`; bez tego nic nie idzie do modelu.

Testy: zmienna `WIEDZA_SEDZIA_POLECENIE` wskazuje atrapę modelu zamiast `claude` (przy prawdziwym hubie – odmowa).
