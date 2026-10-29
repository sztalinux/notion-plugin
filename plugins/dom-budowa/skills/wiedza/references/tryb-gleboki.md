# Tryb głęboki – pytanie złożone, na które Mac czyta całą bazę (czat na telefonie)

Cel: odpowiedź na pytanie, którego nie pokrywa żadna karta, oparta na CAŁEJ bazie. Czat zostawia pytanie w prywatnym repo kopii indeksu;
Mac czyta całą bazę modelem w małych porcjach (dwa przebiegi, Sonnet), pisze pełną odpowiedź (Opus) z tezami, otwartymi sprzecznościami
i Notatnikiem z migawki i odkłada ją do repo; czat pobiera ją i przekazuje. Powód: karta to wybór tez zrobiony z góry dla rodziny pytań,
a pytanie złożone lub nietypowe może potrzebować tez, których karta nie ma. Koszt: 3–6 minut, ok. 1–2 USD na pytanie; Mac musi nie spać.

## Kiedy

Zostaw pytanie Macowi, gdy zachodzi którykolwiek z warunków:
1. `karty --do` nie wskazuje karty pytań pasującej rodziną do pytania (`pytanie-do-bazy.md`, pkt 2.3), a pytanie jest złożone – łączy
   etapy albo zagadnienia;
2. inwestor prosi wprost: „tryb głęboki”, „przeczytaj całą bazę”, „dokładnie wszystko”;
3. `karty --do` pokazuje dużo trafień poza kartami: `trafienia poza wszystkimi kartami: m`, m > 15 (ten sam próg co w `pytanie-do-bazy.md`,
   pkt 2.3; linia kończy się wtedy „… (+k)”).

Nie dla faktów wąskich (wystarczy `szukaj`) ani dla pytań, które karta pokrywa – to 3–6 minut i 1–2 USD za odpowiedź, którą karta daje od razu.

## Protokół (czat na telefonie)

Pola bierz z pliku dostępu „🔑 Dostęp asystenta” w wiedzy projektu „Dom” (`indeks.md`, sekcja czatu), z sekcji „Tryb głęboki”: `<GITHUB_REPO>`
i `<TOKEN ZAPISU>` (odczyt – zwykły `<TOKEN>`). Nigdy nie wypisuj tokenów: w odpowiedzi, notatce, pliku ani w wyniku polecenia (nie używaj
`curl -v` – drukuje nagłówek z tokenem). Brak sekcji albo tokena → napisz „tryb głęboki niedostępny” i wróć do zwykłej drogi (`pytanie-do-bazy.md`, pkt 2; przy m > 15 z poziomem „normalnie”).

1. **Zapisz pytanie jako pierwsze** – po `karty --do` (z jego wyniku wynikają warunki 1 i 3; przy prośbie inwestora od razu), przed pierwszym
   `karta … --czesc`: Mac pracuje w czasie, gdy czat czyta kartę. ID zapamiętaj i podaj inwestorowi (kolejne wywołania nie widzą zmiennych
   powłoki). JSON i base64 zbuduj w `python3`, nie ręcznie: cudzysłowy, „” i nowe linie w pytaniu zepsułyby ręczny JSON (w literale
   `r"""…"""` zostają bez zmian):
```
ID=$(date -u +%Y%m%d-%H%M%S)-$RANDOM
python3 - "$ID" <<'EOF' > /tmp/p.json
import base64, datetime, json, sys
pytanie = r"""<pytanie dosłownie>"""
sytuacja = r"""<etap, założenia, kontekst z rozmowy – albo puste>"""
teraz = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
d = {"id": sys.argv[1], "pytanie": pytanie, "sytuacja": sytuacja or None, "kanal": "telefon", "utworzono": teraz}
tresc = base64.b64encode(json.dumps(d, ensure_ascii=False).encode()).decode()
print(json.dumps({"message": "pytanie " + sys.argv[1], "content": tresc}))
EOF
curl -s -o /dev/null -w "%{http_code}" -X PUT -H "Authorization: Bearer <TOKEN ZAPISU>" -H "X-GitHub-Api-Version: 2022-11-28" --data @/tmp/p.json https://api.github.com/repos/<GITHUB_REPO>/contents/pytania/$ID.json
```
   Kod 201 = przyjęte. Inny kod → napisz „tryb głęboki niedostępny (kod n)”, wróć do zwykłej drogi (przy m > 15 z „normalnie”) i nie ponawiaj.
2. **Wstępna odpowiedź** – od razu, w tej samej odpowiedzi, napisz ją z karty zwykłą drogą (`pytanie-do-bazy.md`, pkt 2), oznaczoną „wstępna –
   tryb głęboki w toku (ID)”; „normalnie” z pkt 2.3 pomiń – zastępuje je głęboka. Powód: inwestor ma użyteczny wynik, nawet gdy Mac nie odpowie.
3. **Odbiór** – do 3 wywołań (ok. 6 minut), do pliku (odpowiedź bywa dłuższa niż limit wyniku narzędzia). Zmienne powłoki znikają między
   wywołaniami, więc zacznij od `ID=<ID>` – z kroku 1, a po „sprawdź odpowiedź <ID>” od inwestora:
```
ID=<ID>
for i in 1 2 3 4 5 6; do sleep 20; curl -sf -H "Authorization: Bearer <TOKEN>" -H "Accept: application/vnd.github.raw" -o /tmp/odp-$ID.md https://api.github.com/repos/<GITHUB_REPO>/contents/odpowiedzi/$ID.md && break; done
wc -c < /tmp/odp-$ID.md; curl -s -o /dev/null -w "w-toku: %{http_code}\n" -H "Authorization: Bearer <TOKEN>" https://api.github.com/repos/<GITHUB_REPO>/contents/odpowiedzi/$ID.w-toku
```
   - plik jest → krok 4; brak pliku i `w-toku: 200` (znacznik `odpowiedzi/<ID>.w-toku`; jego pole `krok` mówi: „w kolejce”, „wybór tez”,
     „odpowiedź” albo „czeka na limit” – przekaż inwestorowi) → Mac pracuje: powtórz wywołanie, a po trzecim
     napisz, że jeszcze pracuje, i podaj „sprawdź odpowiedź <ID>”;
   - brak pliku i `w-toku: 404` po ok. 2 minutach → Mac uśpiony albo offline: napisz to, zostaw wstępną odpowiedź i powiedz, że „sprawdź
     odpowiedź <ID>” pobierze ją później (pytanie czeka w repo; to jedno pobranie `odpowiedzi/<ID>.md`). Powód: nie czekaj na Maca, który się nie obudzi.
4. **Przekaż w całości** – odpowiedź ma własny nagłówek i linię Zasięg („przeczytano całą bazę: N tez…”); czytaj plik porcjami po 20 000 bajtów
   (`pytanie-do-bazy.md`, pkt 3, „Długie wyniki”) i nie skracaj: za pełną lekturę bazy zapłacono, a skrót gubi tezy, dla których to robiono.
   Dopisz, czym różni się od wstępnej: tezy, których karta nie miała (numery WI).
5. **Nic nie usuwaj** – pliki w `pytania/` i `odpowiedzi/` zostają w repo jako historia; pytanie, które poszło tym trybem, to kandydat na nową
   kartę pytań (`karty.md`).

## Claude Code na Macu

Bez prywatnego repo i tokena zapisu: uruchom lokalnie skrypt `pytania.py` z katalogu automatów na Macu (ścieżka i opcje – README automatów):
`python3 <katalog automatów>/pytania.py --pytanie "…" [--sytuacja "…"]`. Odpowiedź ląduje w `.dom/automaty/`; przekaż ją w całości jak w kroku 4.
