# Wydatki → Arkusz Google – jak to działa (dla agentów i inwestora)

Kosztorys budowy żyje w arkuszu Google „Kosztorys budowy” (prywatne konto inwestora). Arkusz jest **jedynym źródłem
prawdy dla liczb**; Notion jest tylko kolejką, którą automat na Macu przenosi do arkusza. Wydatek, wycena albo plan kwoty
napisane we wpisie w Dzienniku lub w wiadomości do asystenta trafiają do arkusza bez ręcznego eksportu i importu. Błąd
wraca do inwestora jako komunikat 🔔 we „📝 Wpisach”. Konektor Google Sheets przyspiesza odczyt i zmiany układu, ale nic od
niego nie zależy – bez niego działa droga zapasowa (sekcje 4 i 8).

Gdzie co jest opisane:
- procedura dla agenta (co zapisać, kiedy pytać): `plugins/dom-budowa/skills/koszty/SKILL.md`, sekcje B (wydatek),
  B2 (wycena), B3 (plan pozycji), C (zmiana układu), D (transze), E (błąd → komunikat 🔔 we Wpisach);
- układ zakładek i kolumn: `plugins/dom-budowa/skills/koszty/references/arkusze.md`;
- pola bazy 💸 Wydatki → arkusz: `plugins/dom-budowa/skills/notatka/references/notion-schematy.md`;
- narzędzie: `tools/wydatki.py` (sam Python, biblioteka standardowa); kod Apps Script: sekcja 9 tego pliku.

## 1. Przepływ danych

```
wpis w 📓 Dzienniku  ·  wiadomość do asystenta  ·  zdjęcie faktury  ·  wiersz dodany ręcznie w Notion
   │  agent wg koszty B/B2/B3 zapisuje stronę z Arkusz = „Do arkusza”
   ▼
💸 Wydatki → arkusz   (baza Notion na DOM, collection://72cff09c-609b-405d-a32c-263271b3b59c)
   │  tools/wydatki.py sync  – NOTION_TOKEN, bez AI
   ▼
Apps Script przypięty do arkusza (aplikacja internetowa + sekret, @OnlyCurrentDoc)
   │  Rodzaj Wydatek i Zwrot → zakładka Wydatki  ·  Wycena → Cennik  ·  Plan → Kosztorys, kolumna „Plan ręczny”
   │  pole „Nowa pozycja” → najpierw nowy wiersz pozycji w etapie Kosztorysu (kod ≥ 5, po pierwszym sprawdzeniu w sesji), potem jak wyżej
   ▼
Notion: Arkusz = „W arkuszu” + Wiersz arkusza   albo   „Błąd” + powód w polu Błąd
   │  przebieg szybki: widok „⚠ Błędy do zgłoszenia” → komunikat 🔔 z okienkiem ❓ we „📝 Wpisach”, Zgłoszono = dziś
   ▼
odpowiedź inwestora → agent poprawia pola, „Do arkusza” → następny `sync`
```

Kanały i kiedy wiersz trafia do arkusza:

| Kanał | Kto zapisuje do kolejki | Kiedy w arkuszu |
|---|---|---|
| Claude Code z inwestorem (Mac) | agent przez MCP Notion | od razu – agent uruchamia `python3 tools/wydatki.py sync` i podaje numer wiersza |
| Przebieg Dziennika bez inwestora (`claude -p`, launchd) | agent w przebiegu (`wpisy` → `budowa` → `koszty`) | zaraz po przebiegu: `AI/automaty/przeglad.py` woła `sync` (hook PO_PRZEBIEGU) |
| claude.ai / telefon bez Notion | agent pisze do „📥 Skrzynki” słowami, ze wszystkimi polami | Mac przenosi Skrzynkę do Notion w przebiegu, potem jak wyżej |
| Inwestor ręcznie w Notion | inwestor (pole Arkusz puste albo „Do arkusza”) | najbliższy przebieg (co godzinę 8:05–22:05 i 22:30) |
| Inwestor ręcznie w arkuszu | – (z pominięciem kolejki) | od razu; tej płatności nie wolno już zapisywać w Notion |

Harmonogram automatu: przebieg szybki → `sync` i `pobierz --gdy-starsza 12` (ponawia kopię, gdy nocna się nie
udała); nocny → `sync`, `pozycje`, `pobierz`; tygodniowy → `sync`. Mac
wyłączony → strony czekają w Notion, nic nie ginie. GitHub Actions nie mają dostępu do Notion – całość działa na Macu.

## 2. Obsługa płatności przez agenta (skrót – pełne reguły w `koszty` B/B2/B3/D)

| Sytuacja | Co zapisać w 💸 Wydatki | Uwagi |
|---|---|---|
| „zapłaciłem / wydałem / kupiłem za …” | Rodzaj Wydatek, Płatność „Zrealizowane” | kilka płatności w jednej wiadomości = kilka stron |
| faktura albo transza czeka na zapłatę | Płatność „Do zapłaty” | liczy się do zobowiązań, nie do WYDANE |
| „zapłaciłem tę fakturę” (strona już w arkuszu) | ta sama strona: Płatność „Zrealizowane”, Data = dzień zapłaty, Arkusz „Do arkusza” | `sync` poprawia jej wiersz (A:H, J:M, P), nie dodaje nowego |
| zła kwota / pozycja w wysłanym wydatku | popraw pola tej samej strony, Arkusz „Do arkusza” | jak wyżej; nadpisze ręczną zmianę inwestora w tym wierszu |
| zwrot pieniędzy (różnica VAT od wykonawcy, zwrot towaru) | nowa strona: Rodzaj Zwrot, Kwota dodatnia, ta sama Pozycja i Typ co wydatek, bez Ilości; „Do zapłaty” = oczekiwany | arkusz: osobny wiersz z minusem (kod Apps Script ≥ 4); wydatek zostaje bez zmian, WYDANE = suma |
| wydatek wysłany przez pomyłkę | – | `python3 tools/wydatki.py wycofaj <id strony>` (czyści wiersz, w Notion „Nie wysyłać”) |
| oferta / cena dostawcy („X ma beton po … zł/m³ brutto”) | Rodzaj Wycena, Kwota = cena za jednostkę, Jedn., Cena podana Netto/Brutto, VAT % | idzie do Cennika, nie do Wydatków; wybór = Status wyceny „Wybrana” i ponowne wysłanie |
| „planuję wydać ok. N”, „szacowałem N, wyszło M” | Rodzaj Plan, Kwota = plan całej pozycji brutto (+ osobno wydatek M) | `sync` wpisuje „Plan ręczny” pozycji; inny plan już jest → Błąd i pytanie (nie dla planu tej pozycji wpisanego wcześniej przez tę samą stronę – `<hub>/.dom/wydatki/plany.json`), „Nadpisz plan” zastępuje |
| „kupić X na budowę” (jeszcze nie kupione) | nic – to zakup, procedura `zakupy` | koszt powstaje dopiero przy zapłacie |
| wydatek bez pasującej pozycji | ❓ z propozycją „Nowa pozycja: 47 \| Pozycja X \| Materiał \| kpl – tak?”; po „tak” strona z pustą Pozycją i polem Nowa pozycja | `sync` dodaje pozycję (kod ≥ 5, po pierwszym sprawdzeniu w sesji) i wysyła wydatek w tym samym przebiegu; nowy etap – pierwsza sesja Claude Code (`koszty/references/nowa-pozycja.md`); pole tylko przy Wydatku i Wycenie, wybrana Pozycja wygrywa |

Pola obowiązkowe wydatku: Data, Kwota (to, co zapłacono – zwykle brutto), Pozycja z listy (= pozycja Kosztorysu, z niej
arkusz bierze etap), Typ (Materiał / Robocizna / Sprzęt / Usługa / Formalności – zawsze). Materiał w etapach 02–08 – także
Ilość i Jedn. Brak daty → dzień wpisu albo wiadomości i w Notatkach „data = dzień zgłoszenia”. Niepewny opis lub typ nie
blokuje – zapisz z „do potwierdzenia: …” w Notatkach. Pytaj (❓ pod wpisem albo w rozmowie) tylko o brakującą kwotę albo
niepewną pozycję. Nie zgaduj netto/brutto ani stawki VAT (zasada 7 `budowa`): VAT 8% usługa z materiałem, 23% sam materiał.

Duplikaty: przed zapisem szukaj w bazie strony z tą samą datą i kwotą – duplikat to ta z tego samego źródła (wpis, wiadomość, nr FV);
dwie płatności tego dnia na tę samą kwotę to dwa wiersze (`koszty` B.3); w Claude Code sprawdź też kopię arkusza
(`Koszty/Kosztorys_google.json`, zakładka Wydatki) – starsze wydatki są tylko tam. Ta sama strona wysłana dwa razy nie
zdubluje wiersza: arkusz rozpoznaje ją po kolumnie Źródło `notion:<id strony>`.

## 3. Co liczy arkusz sam (powiązania formuł)

Agent nie przelicza ręcznie niczego, co liczy arkusz – zmienia dane wejściowe, a formuły robią resztę.

- **Etap pozycji:** Kosztorys kol. A to formuła z zakładki Etapy (wiersz etapu `=Etapy!A<n>`, pozycje `=$A$<wiersz etapu>`);
  stan budowy (Stan zero, SSO…) też pochodzi z Etapów. Wydatek dostaje etap z pozycji (akcja `pozycje`).
- **PLAN pozycji (Kosztorys G):** wybrana oferta z Cennika × Ilość plan (kol. P); bez wybranej oferty – Plan ręczny (kol. U,
  wpisuje inwestor). Zmiana ilości, ceny albo wyboru oferty przelicza PLAN, sumy etapów i Podsumowanie.
- **Grupy materiałów (Kosztorys V, Cennik P):** jedna oferta (np. stal) zasila kilka pozycji tej samej grupy.
- **Jednostki:** Cennik Q przelicza cenę na jednostkę bazową (t → kg), żeby oferta za tonę pasowała do pozycji w kg.
- **VAT w Cenniku:** G = cena brutto, O = cena netto; VAT % wpisany jako 8 albo 0,08 działa tak samo (`sync` zamienia ułamek na procenty).
- **WYDANE:** sumy Wydatków „Zrealizowane” po pozycji i typie → Kosztorys I, Etapy H–L, Podsumowanie. Zwroty (kwoty
  ujemne) odejmują się same; „Do zapłaty” z minusem obniża zobowiązania.
- **VAT w Wydatkach:** P = VAT % (z pola VAT % strony; `sync` wpisuje, korekta nadpisuje, `wycofaj` czyści), Q = netto
  (formuła `C/(1+P)`, pusta bez stawki).
- **Szacunek AI:** zakładka „Szacunek AI 10.2026” (pełna wycena AI, wartości); kol. J–K przypisują wiersz do etapu i pozycji
  Kosztorysu, stąd Kosztorys Q–S, Etapy P–R i tabela „wg stanów” w Podsumowaniu (materiał / robocizna / razem).
- **Kontrole:** Kosztorys T (⚠ etap spoza Etapów, brak typu), Wydatki N (⚠ przy wierszu), Podsumowanie „Kontrola
  powiązań” (PLAN i WYDANE: Kosztorys − Etapy, Wydatki − Etapy; liczba ⚠) – wszystko ma dawać 0 / ✓.

## 4. Dostęp i bezpieczeństwo

| Kto | Jak sięga do danych | Co może |
|---|---|---|
| Claude Code na Macu (rozmowa i `claude -p`) | MCP Notion | czyta i zapisuje kolejkę 💸 Wydatki |
| `tools/wydatki.py` | `NOTION_TOKEN` + `ARKUSZ_URL` i `ARKUSZ_SEKRET` z `.dom/sekrety.env` | kolejka → arkusz, pola Arkusz/Błąd/Wiersz, lista Pozycja |
| Apps Script | przypięty do jednego arkusza (`@OnlyCurrentDoc`) | dopisz / usuń / zmień układ – bez Dysku i innych plików; sam z siebie (bez pliku zmian) tylko nowy wiersz pozycji w istniejącym etapie, z kontrolą przed i po |
| Konektor Google Drive / Sheets (gdy jest w sesji Claude: Claude Code, claude.ai, telefon) | konto Google inwestora (właściciel arkusza) | odczyt żywego arkusza z formułami – pierwsze źródło liczb; zmiany układu w Claude Code (sekcja 8); nigdy wydatki, wyceny ani plany (omija kolejkę i deduplikację); przebiegi `claude -p` na nim nie polegają |
| GitHub Actions | brak dostępu do Notion i arkusza | – |

**Kolejność źródeł liczb** (brak narzędzia albo błąd → następne, bez ponawiania): konektor (żywy arkusz) → kopia
`Koszty/Kosztorys_google.json` w Claude Code (`pobierz` po świeżą) → eksport od inwestora na claude.ai. ID arkusza i e-mail
właściciela nie trafiają do repo – plik znajdź po tytule wyszukiwarką Dysku.

Sekretów (adres `/exec`, sekret, tokeny) nigdy nie wypisuj ani nie wklejaj poza `sekrety.env`. Wyciek → nowy sekret
(sekcja 7, kroki 3 i 5). Komunikaty `wydatki.py` niosą tylko liczby, numery pozycji i statusy – bez kwot i opisów.
Zmian w arkuszu nie cofa skrypt – służy do tego Plik → Historia wersji.

## 5. Polecenia (`python3 tools/wydatki.py …`, katalog repo)

| Polecenie | Co robi | Kto woła |
|---|---|---|
| `sync` | kolejka „Do arkusza” (i puste Arkusz) → arkusz; strona już w arkuszu = korekta jej wiersza; Plan → „Plan ręczny” w Kosztorysie (kolumna i wiersz po nagłówkach); czyści Zgłoszono | automat po przebiegu; agent w Claude Code po zapisie |
| `sync --proba` | pokazuje, co by poszło; nic nie zapisuje. Sprawdza tylko pola strony (data, kwota, pozycja z listy, ilość, wycena) – pozycję wobec Kosztorysu, konflikt planu i wersję kodu Apps Script sprawdza dopiero `sync` | ręcznie |
| `pozycje` | pozycje Kosztorysu → opcje pola Pozycja w Notion | przebieg nocny; po dodaniu pozycji w arkuszu |
| `pobierz [--gdy-starsza H]` | wartości wszystkich zakładek → `<hub>/Koszty/Kosztorys_google.json` (limit odczytu 300 s); z `--gdy-starsza` tylko, gdy kopia jest starsza niż H godzin | przebieg nocny, szybki (ponowienie); przed analizą liczb |
| `wycofaj <id>…` | czyści wiersze strony w Wydatkach / Cenniku i jej „Plan ręczny” (gdy stoi tam kwota z tej strony), w Notion „Nie wysyłać” | agent na prośbę |
| `sprawdz` | sekrety, dostęp do bazy i arkusza, wersja kodu | ręcznie, przy problemach |
| `kod` | kod Apps Script z sekcji 9 (z `\| LANG=en_US.UTF-8 pbcopy` – do schowka; bez LANG polskie znaki się psują) | przy aktualizacji kodu |
| `migruj <zmiany.json>` | zmiana układu na żywym arkuszu (sekcja 8) | agent w Claude Code |
| `nowa-pozycja "47 \| Nazwa \| Typ \| Jedn." [--proba]` | pozycja w istniejącym etapie (akcja „dodaj_pozycje”, kod ≥ 5) i opcja w Notion – działa bez znacznika; z `--proba` – plan na sucho (wiersz, Lp, suma etapu, wzór), nic nie zmienia | agent w Claude Code; pierwsze sprawdzenie (`koszty` C.8) |
| `nowa-pozycja --potwierdz` | znacznik `<hub>/.dom/wydatki/nowa-pozycja-sprawdzona` – od niego `sync` sam wstawia pozycje (bez niego woła akcję na sucho: istniejąca pozycja przechodzi, nowa czeka) | sesja po zgodnym pierwszym sprawdzeniu |
| `sesja [--zablokuj \| --odblokuj]` | co czeka na sesję: nowe etapy i pierwsze sprawdzenie (`<hub>/.dom/wydatki/kosztorys-do-sesji.json`, pisze `sync`; z niego linia stanu sesji); blokada – jedna sesja naraz (2 h), przy świeżej blokadzie `sync` nie wstawia pozycji w żadnym etapie (strony z „Nową pozycją” czekają) | sesja Claude Code (`koszty` C.7–C.8) |
| `gotowka [--harmonogram PLIK]` | tylko odczyt: ile pieniędzy wyjdzie w którym miesiącu – kopia arkusza + Harmonogram z Notion (`NOTION_TOKEN`); tabela z kwotami na ekran, nie do logu; reguły: `koszty/references/gotowka.md` | agent na „ile gotówki potrzebuję w …”, przegląd tygodnia |

Kody wyjścia: 0 OK, 1 błąd polecenia (linie `✗` pod podsumowaniem, np. timeout arkusza, Notion), 2 brak konfiguracji.
Błąd pojedynczej strony nie zmienia kodu: `sync` zapisuje go w Notion (Arkusz = „Błąd”), a `sync --proba` tylko go wypisuje
(linia `✗` nad podsumowaniem, licznik `bledy`). Wynik z automatu: log przebiegu
`<hub>/.dom/automaty/<tryb>-RRRR-MM-DD.log`, linia „po przebiegu wydatki.py …”.

Zabezpieczenia w `sync`: walidacja przed wysyłką (data, kwota, pozycja, ilość i jednostka materiału 02–08; wycena – jednostka, nazwa,
VAT przy netto) → strona dostaje „Błąd” z powodem; wyceny czekają, gdy kod Apps Script < 2 albo Cennik w starym układzie
(`cennik_ok`), zwroty – gdy kod < 4, strony z polem „Nowa pozycja” – gdy kod < 5; kolumny z formułami (Wydatki I, N i Q, Cennik G, K i O–Q, Kosztorys N–P) nigdy nie są
nadpisywane; zapis pod
blokadą (LockService) – dwa przebiegi naraz nie wejdą sobie w drogę.

## 6. Problemy

| Objaw | Przyczyna i naprawa |
|---|---|
| `arkusz: timeout` | Google bywa chwilowo wolny (zdarzało się, że przez kilka godzin także ping) – strony zostają „Do arkusza” i pójdą przy następnym przebiegu; ponów później `sprawdz`. Nie wysyłaj ich drugą drogą |
| „odpowiedź nie jest JSON” | wdrożenie bez dostępu „Każdy” albo adres `/dev` zamiast `/exec` – sekcja 7, krok 4 |
| „zły sekret” | `ARKUSZ_SEKRET` ≠ właściwość `SEKRET` – sekcja 7, kroki 3 i 5 |
| „pozycja … nie istnieje w Kosztorysie” | pozycję usunięto lub przenumerowano – wybierz inną; `pozycje` odświeży listę |
| „materiał stanu zero bez ilości albo jednostki” | dopisz Ilość i Jedn., ustaw „Do arkusza” |
| „pozycja … ma już inny plan ręczny” | inwestor decyduje: zaznacz „Nadpisz plan” i „Do arkusza” albo zostaw stary plan („Nie wysyłać”) |
| „plany: timeout – strony zostają w kolejce” | odczyt Kosztorysu przekroczył czas – plany pójdą przy następnym `sync` |
| „cena netto bez stawki” | wpisz VAT % (nie zgaduj – zapytaj inwestora) |
| HTTP 404 / 403 z Notion | integracja bez dostępu do bazy (⋯ → Połączenia) albo bez prawa „Update content” |
| data przesunięta o dzień | strefa arkusza ≠ Warsaw – Plik → Ustawienia |
| „N wycen czeka: arkusz ma kod w wersji …” / „N wycen czeka: Cennik w starym układzie …” / „N zwrotów czeka: arkusz ma kod w wersji …” | starszy kod (sekcja 7, aktualizacja kodu; `sprawdz` pokaże wersję) albo brak zmiany układu (sekcja 8); strony czekają „Do arkusza”, `sync` kończy się kodem 1 |
| „N stron z nową pozycją czeka: arkusz ma kod w wersji …” | kod < 5 – sekcja 7, aktualizacja kodu; strony czekają „Do arkusza” |
| Błąd „nowa pozycja NN.n: … – wstawiony wiersz usunięty” | kontrola po wstawieniu się nie zgodziła (sumy, „Kontrola powiązań”); arkusz bez zmian. Sprawdź układ etapu (sumy w nagłówku, zakresy `$5:$<n>`) – `nowa-pozycja … --proba` pokaże plan |
| Błąd pola „czeka na etap NN …” (Arkusz „Do arkusza”) | etapu nie ma w Kosztorysie (albo nagłówek bez pozycji) – doda go najbliższa sesja Claude Code (`koszty` C.7); `sesja` pokazuje listę |
| Błąd pola „czeka na pierwsze sprawdzenie …” | brak znacznika – pierwszą nową pozycję wstawia sesja z kontrolą (`koszty` C.8) |
| „czeka na sesję Claude Code ponad 3 dni: …” (kod 1, 🔔 z przebiegu) | otwórz sesję Claude Code w repo – zrobi C.7–C.8 sama |
| Błąd „wiersz N w etapie NN bez Lp” / „pozycja NN.n już jest, ale …” | w arkuszu wiersz bez Lp albo uszkodzona pozycja o tej nazwie – popraw w arkuszu, potem „Do arkusza” |
| #ERROR! / dziwne liczby po zmianie układu | formuła z „,” zamiast „;” (arkusz ma polskie ustawienia) – sekcja 8, pułapki |

## 7. Konfiguracja od zera (już zrobiona – tylko przy odtwarzaniu)

1. Arkusz Google na **prywatnym** koncie; Plik → Ustawienia: Polska, strefa (GMT+01:00) Warsaw. Arkusza nie importuje się
   ponownie – zastąpienie pliku kasuje wydatki dopisane od tamtej pory.
2. Rozszerzenia → Apps Script → `Kod.gs` = kod z sekcji 9 (`python3 tools/wydatki.py kod | LANG=en_US.UTF-8 pbcopy`), zapisz.
3. Ustawienia projektu → Właściwości skryptu → `SEKRET` = `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`.
4. Wdróż → Nowe wdrożenie → Aplikacja internetowa, Wykonaj jako **Ja**, dostęp **Każdy** (bez sekretu odpowiedź „zły
   sekret”). Autoryzuj (skrypt prosi tylko o ten arkusz). Skopiuj adres `/exec`.
5. `<hub>/.dom/sekrety.env`: `ARKUSZ_URL=<adres>`, `ARKUSZ_SEKRET=<sekret>`.
6. `wydatki.py sprawdz`, `pozycje`, `pobierz`; próba: strona testowa N zł → `sync` → sprawdź datę i kwotę w arkuszu →
   `wycofaj <id>` i strona do kosza.

Aktualizacja kodu: wklej nowy kod jak w kroku 2, potem Wdróż → Zarządzaj wdrożeniami → ołówek → Wersja: **Nowa** → Wdróż
(adres i sekret bez zmian). `sprawdz` pokaże wersję. Kod zmieniasz tylko w tym pliku (sekcja 9) – `kod` czyta go stąd.

## 8. Zmiany układu na żywym arkuszu (agent w Claude Code)

Inwestor zmienia arkusz ręcznie równolegle (przenosi kolumny, poprawia PLAN) – zawsze pracuj na aktualnym stanie.

0. **Droga szybka – konektor Google Sheets** (gdy jest w sesji): migawka zmienianego zakresu z formułami
   (`get_spreadsheet` z `userEnteredValue`) zapisana w `<hub>/.dom/wydatki/` → zapis (`update_formulas`, `update_values`,
   `update_spreadsheet`) → odczyt kontrolny. Te same zasady co skrypt: formuły ze „;” i przecinkiem dziesiętnym
   (sprawdzone 10.11.2026 – „,” daje liczbę dziesiętną), bez nadpisywania kolumn wpisywanych (Wydatki A–H, J–M, O, P;
   Kosztorys B–F, K, L, U, V; Cennik A–F, H–J, L–N), bez IMPORT…/IMAGE/HYPERLINK, nie w trakcie `sync`. Reguły formatowania
   warunkowego przez `update_spreadsheet` przetestuj najpierw na jednej regule. Konektora brak albo błąd → kroki 1–5 (wolniej,
   ten sam wynik). Potem i tak krok 5 (kontrola).
1. `wydatki.py pobierz` albo odczyt konektorem – aktualne wartości i nagłówki. Odwołania do innych zakładek buduj po
   **nagłówkach żywego arkusza**, nie po literach z `arkusze.md` (kolumny bywają przesunięte).
2. Plik zmian JSON `{"opis": …, "operacje": [ … ]}` (operacje akcji `zmien`: `zakres`, `wyczysc`, `walidacja`, `warunkowe`, `szerokosci`, `wysokosci`,
   `zamroz`, `siatka`, `ramka`, `wstaw` – 1–5 pustych wierszy w Kosztorysie, tylko wewnątrz pozycji: `{"op": "wstaw", "arkusz": "Kosztorys", "przed": N, "ile": 2}`) – ręcznie albo narzędziem `python3 ~/Documents/Dom/AI/automaty/arkusz_zmiany.py` (poza
   repo, openpyxl; z docelowego `.xlsx`). Zapisz go w `<hub>/.dom/wydatki/` z datą, obok migawkę „przed”.
3. **Pułapki polskich ustawień:** formuły w operacji `zakres` muszą mieć „;” jako separator i przecinek dziesiętny
   (`arkusz_zmiany.py` robi to funkcją `pl()`); reguły formatowania warunkowego pisz bez przecinków i ułamków – iloczyn
   zamiast AND, suma zamiast OR, porównania `>=`/`<` zamiast LEFT (`cf_bez_przecinkow()`). VAT czytaj jako
   `IF(F>1;F/100;F)`.
4. Sprawdź lokalnie (LibreOffice: zero #NAME?/#REF!, sumy jak przed), przy nowym rodzaju operacji – na makiecie Node.
5. `wydatki.py migruj zmiany.json`, potem `pobierz` i kontrola: zero błędów formuł, sumy Podsumowania jak przed (różnica
   = ręczna zmiana inwestora, nie Twoja – sprawdź, zanim „naprawisz”), „Kontrola powiązań” = 0. Coś nie tak → inwestor
   cofa: Plik → Historia wersji.
6. Zmieniony układ opisz w `koszty/references/arkusze.md`; zmiana kolumn czytanych przez skrypt (⚙) wymaga też zmiany
   kodu (sekcja 9) i `tools/wydatki.py`.

## 9. Kod Apps Script (`Kod.gs`)

```javascript
/** @OnlyCurrentDoc */
/**
 * Kosztorys w Arkuszach Google – punkt wejścia dla tools/wydatki.py (Mac). Instrukcja: docs/wydatki-arkusz.md
 * w repozytorium harnessu. Kod nie zawiera danych – działa na arkuszu, do którego jest przypięty.
 * Akcje (POST, JSON {"sekret", "akcja", ...}):
 *   ping · pozycje · dane · dopisz (wiersze[]) · usun (ids[]) · zmien (operacje[]) – zmiany układu bez ponownego importu
 *   · dodaj_pozycje (pozycja {etap, nazwa, typ, jedn}, na_sucho) – nowy wiersz pozycji w istniejącym etapie Kosztorysu.
 * @OnlyCurrentDoc: skrypt ma dostęp wyłącznie do tego arkusza (bez Dysku, bez innych plików). Cofanie zmian – Plik →
 * Historia wersji.
 * dodaj_pozycje: jedyna zmiana układu, którą skrypt robi sam. Wstawia wiersz wewnątrz etapu (przed ostatnią pozycją etapu,
 * a przy etapie z jedną pozycją – za nią), kopiuje formuły i formaty z pozycji z kompletem formuł, od razu wpisuje Lp
 * (najwyższy numer etapu w Kosztorysie i Wydatkach + 1) i nazwę, poprawia sumy w nagłówku etapu. Kontrola przed i po:
 * „Kontrola powiązań”, RAZEM KOSZTORYS i sumy nagłówka etapu bez zmian, nowy wiersz w sumach i z kompletem formuł – inaczej
 * (także po wyjątku) usuwa wstawiony wiersz i zwraca błąd. Nagłówki i etykiety sprawdza przed zmianą. Ta sama nazwa
 * w etapie = istniejący Lp, jeśli jego wiersz jest kompletny. Wiersz etapu bez Lp = odmowa. Etapu nie dodaje (brak_etapu).
 * dopisz: rodzaj „Wycena” → arkusz Cennik (ponowne wysłanie aktualizuje ten sam wiersz), reszta → arkusz Wydatki
 * („Zwrot” z kwotą ujemną). Wydatki P (VAT %) wpisuje i czyści tools/wydatki.py akcją zmien, nie dopisz/usun.
 * Kolumn z formułami (Wydatki I, N i Q, Cennik G, K i O–Q, Kosztorys N–P) dopisz/usun nigdy nie nadpisują.
 * zmien: tylko znane zakładki, bez usuwania zakładek, bez formuł IMPORT…/IMAGE/HYPERLINK; czyścić wolno tylko pusty Cennik
 * i archiwum szacunku AI.
 */

var WERSJA = 5;
var ARKUSZ_WYDATKI = 'Wydatki';
var ARKUSZ_KOSZTORYS = 'Kosztorys';
var ARKUSZ_CENNIK = 'Cennik';
var ARKUSZ_PODSUMOWANIE = 'Podsumowanie';
var PIERWSZY_WIERSZ = 5;
var STATUSY = ['Zrealizowane', 'Do zapłaty'];
var TYPY = ['Materiał', 'Robocizna', 'Sprzęt', 'Usługa', 'Formalności'];
var JEDNOSTKI = ['kpl', 'm³', 'm²', 'mb', 'kg', 't', 'szt', 'h', 'dzień', 'mies.', 'l'];
var KONTROLA = 'Kontrola powiązań';
var RAZEM_KOSZTORYS = 'RAZEM KOSZTORYS';
var SUMA_ETAPU = /^=SUM\(([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?\)$/;
var STATUSY_WYCENY = ['Oferta', 'Wybrana', 'Odrzucona'];
var ARKUSZ_SZACUNEK = 'Szacunek AI 10.2026';
var ZAKLADKI = ['Instrukcja', 'Podsumowanie', 'Wydatki', 'Cennik', 'Etapy', 'Kosztorys', ARKUSZ_SZACUNEK];
var ZAKAZANE = /IMPORTXML|IMPORTDATA|IMPORTHTML|IMPORTFEED|IMPORTRANGE|IMAGE\s*\(|HYPERLINK\s*\(/i;
// Cennik: A Data · B Materiał / usługa · C Jedn. · D Cena (z oferty) · E Netto / Brutto · F VAT % · G Cena brutto (formuła)
// · H Dostawca · I Pozycja · J Status · K Najtańsza (formuła) · L Ważna do · M Uwagi · N Źródło (notion:<id>)
var CENNIK_NAGLOWEK = ['Data', 'Materiał / usługa', 'Jedn.', 'Cena (z oferty)', 'Netto / Brutto', 'VAT %', 'Cena brutto',
  'Dostawca', 'Pozycja kosztorysu', 'Status', 'Najtańsza', 'Ważna do', 'Uwagi (transport, min. ilość, rabat)', 'Źródło'];

function doPost(e) {
  var zadanie;
  try {
    zadanie = JSON.parse(e.postData.contents);
  } catch (err) {
    return odpowiedz({ok: false, blad: 'niepoprawny JSON'});
  }
  var sekret = PropertiesService.getScriptProperties().getProperty('SEKRET');
  if (!sekret || zadanie.sekret !== sekret) {
    return odpowiedz({ok: false, blad: 'zły sekret'});
  }
  try {
    switch (zadanie.akcja) {
      case 'ping': return odpowiedz(ping());
      case 'pozycje': return odpowiedz({ok: true, pozycje: pozycje()});
      case 'dopisz': return odpowiedz(podBlokada(function () { return dopisz(zadanie.wiersze || []); }));
      case 'usun': return odpowiedz(podBlokada(function () { return usun(zadanie.ids || []); }));
      case 'dane': return odpowiedz(dane());
      case 'zmien': return odpowiedz(podBlokada(function () { return zmien(zadanie.operacje || []); }));
      case 'dodaj_pozycje':
        return odpowiedz(podBlokada(function () { return {ok: true, wynik: dodajPozycje(zadanie.pozycja || {}, !!zadanie.na_sucho)}; }));
      default: return odpowiedz({ok: false, blad: 'nieznana akcja'});
    }
  } catch (err) {
    return odpowiedz({ok: false, blad: String(err).slice(0, 300)});
  }
}

function doGet() {
  return odpowiedz({ok: false, blad: 'użyj POST'});
}

function odpowiedz(obiekt) {
  return ContentService.createTextOutput(JSON.stringify(obiekt)).setMimeType(ContentService.MimeType.JSON);
}

function podBlokada(f) {
  var lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    return f();
  } finally {
    lock.releaseLock();
  }
}

function ping() {
  var ss = SpreadsheetApp.getActive();
  var dane = ss.getSheetByName(ARKUSZ_WYDATKI).getRange('C' + PIERWSZY_WIERSZ + ':C').getValues();
  var n = dane.filter(function (w) { return w[0] !== ''; }).length;
  var naglowek = ss.getSheetByName(ARKUSZ_CENNIK).getRange(4, 1, 1, CENNIK_NAGLOWEK.length).getValues()[0];
  var cennikOk = naglowek.join('|') === CENNIK_NAGLOWEK.join('|');
  return {ok: true, arkusz: ss.getName(), wydatki: n, wersja: WERSJA, cennik_ok: cennikOk};
}

/** Lp → {etap, klucz} z arkusza Kosztorys (kol. A Etap, B Lp, M Klucz). */
function pozycje() {
  var k = SpreadsheetApp.getActive().getSheetByName(ARKUSZ_KOSZTORYS);
  var dane = k.getRange(PIERWSZY_WIERSZ, 1, k.getLastRow() - PIERWSZY_WIERSZ + 1, 13).getValues();
  var wynik = [];
  dane.forEach(function (w) {
    var lp = String(w[1]).trim();
    if (lp && w[0]) wynik.push({lp: lp, etap: String(w[0]), klucz: String(w[12] || (lp + ' ' + w[2]))});
  });
  return wynik;
}

function dopisz(wiersze) {
  var ss = SpreadsheetApp.getActive();
  var arkusz = ss.getSheetByName(ARKUSZ_WYDATKI);
  var strefa = ss.getSpreadsheetTimeZone();  // data = ten dzień w strefie arkusza
  var mapa = {};
  pozycje().forEach(function (p) { mapa[p.lp] = p; });
  var ostatni = Math.max(arkusz.getLastRow(), PIERWSZY_WIERSZ);
  var kolA = arkusz.getRange(PIERWSZY_WIERSZ, 1, ostatni - PIERWSZY_WIERSZ + 1, 1).getValues();
  var kolO = arkusz.getRange(PIERWSZY_WIERSZ, 15, ostatni - PIERWSZY_WIERSZ + 1, 1).getValues();
  var zajete = {};
  kolO.forEach(function (w, i) {
    var z = String(w[0]);
    if (z.indexOf('notion:') === 0) zajete[z] = PIERWSZY_WIERSZ + i;
  });
  var wolny = PIERWSZY_WIERSZ + kolA.length;
  for (var i = 0; i < kolA.length; i++) {
    if (kolA[i][0] === '' && String(kolO[i][0]) === '') { wolny = PIERWSZY_WIERSZ + i; break; }
  }
  var wyniki = [];
  wiersze.forEach(function (w) {
    if (w.rodzaj === 'Wycena') {
      wyniki.push(wycena(w, mapa, strefa));
      return;
    }
    var zrodlo = 'notion:' + w.id;
    if (zajete[zrodlo]) {
      wyniki.push({id: w.id, ok: true, wiersz: zajete[zrodlo], juz: true});
      return;
    }
    var blad = sprawdz(w, mapa);
    if (blad) {
      wyniki.push({id: w.id, ok: false, blad: blad});
      return;
    }
    var p = mapa[w.lp];
    arkusz.getRange(wolny, 1, 1, 8).setValues([[
      Utilities.parseDate(w.data, strefa, 'yyyy-MM-dd'), w.status, Number(w.kwota), p.etap, p.klucz,
      w.typ || '', w.ilosc === null || w.ilosc === undefined ? '' : Number(w.ilosc), w.jedn || '']]);
    arkusz.getRange(wolny, 10, 1, 4).setValues([[w.sposob || '', w.opis || '', w.dostawca || '', w.notatki || '']]);
    arkusz.getRange(wolny, 15).setValue(zrodlo);
    zajete[zrodlo] = wolny;
    wyniki.push({id: w.id, ok: true, wiersz: wolny, juz: false});
    wolny = nastepnyWolny(arkusz, wolny + 1);
  });
  SpreadsheetApp.flush();
  return {ok: true, wyniki: wyniki};
}

function nastepnyWolny(arkusz, od) {
  var wiersz = od;
  while (arkusz.getRange(wiersz, 1).getValue() !== '' || arkusz.getRange(wiersz, 15).getValue() !== '') wiersz++;
  return wiersz;
}

function sprawdz(w, mapa) {
  if (!w.id) return 'brak id strony';
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(w.data || ''))) return 'brak daty';
  // Zwrot (pieniądze oddane, np. różnica VAT) przychodzi z kwotą ujemną – wtedy plus byłby błędem
  if (w.rodzaj === 'Zwrot' ? !(Number(w.kwota) < 0) : !(Number(w.kwota) > 0)) return 'brak kwoty';
  if (STATUSY.indexOf(w.status) < 0) return 'Płatność: ' + STATUSY.join(' / ');
  if (!w.lp) return 'brak pozycji (numer z Kosztorysu, np. 03.5)';
  if (!mapa[w.lp]) return 'pozycja ' + w.lp + ' nie istnieje w Kosztorysie';
  if (w.typ && TYPY.indexOf(w.typ) < 0) return 'nieznany typ ' + w.typ;
  return '';
}

/** Wycena → Cennik (układ: CENNIK_NAGLOWEK). Strona już w Cenniku → aktualizacja tego wiersza, inaczej pierwszy wolny. */
function wycena(w, mapa, strefa) {
  var blad = sprawdzWycene(w, mapa);
  if (blad) return {id: w.id, ok: false, blad: blad};
  var c = SpreadsheetApp.getActive().getSheetByName(ARKUSZ_CENNIK);
  var zrodlo = 'notion:' + w.id;
  var n = Math.max(c.getLastRow(), PIERWSZY_WIERSZ) - PIERWSZY_WIERSZ + 1;
  var dane = c.getRange(PIERWSZY_WIERSZ, 1, n, 14).getValues();
  var wiersz = 0, juz = false;
  for (var i = 0; i < dane.length; i++) {
    if (String(dane[i][13]) === zrodlo) { wiersz = PIERWSZY_WIERSZ + i; juz = true; break; }
  }
  if (!wiersz) {
    wiersz = PIERWSZY_WIERSZ + n;
    for (var j = 0; j < dane.length; j++) {
      if (dane[j][0] === '' && dane[j][1] === '' && dane[j][13] === '') { wiersz = PIERWSZY_WIERSZ + j; break; }
    }
  }
  var klucz = w.lp ? mapa[w.lp].klucz : '';
  var vat = w.vat === null || w.vat === undefined || w.vat === '' ? '' : Number(w.vat) / 100;
  c.getRange(wiersz, 1, 1, 6).setValues([[Utilities.parseDate(w.data, strefa, 'yyyy-MM-dd'), w.opis, w.jedn,
    Number(w.kwota), w.cena_podana || 'Brutto', vat]]);
  c.getRange(wiersz, 8, 1, 3).setValues([[w.dostawca || '', klucz, w.status_wyceny || 'Oferta']]);
  c.getRange(wiersz, 12, 1, 3).setValues([[w.wazna_do ? Utilities.parseDate(w.wazna_do, strefa, 'yyyy-MM-dd') : '',
    w.notatki || '', zrodlo]]);
  return {id: w.id, ok: true, wiersz: wiersz, juz: juz, arkusz: ARKUSZ_CENNIK};
}

function sprawdzWycene(w, mapa) {
  if (!w.id) return 'brak id strony';
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(w.data || ''))) return 'brak daty';
  if (!(Number(w.kwota) > 0)) return 'brak ceny za jednostkę (pole Kwota)';
  if (!w.jedn) return 'brak jednostki (Jedn.)';
  if (!w.opis) return 'brak nazwy (Wydatek)';
  if (w.lp && !mapa[w.lp]) return 'pozycja ' + w.lp + ' nie istnieje w Kosztorysie';
  if (w.status_wyceny && STATUSY_WYCENY.indexOf(w.status_wyceny) < 0) return 'Status wyceny: ' + STATUSY_WYCENY.join(' / ');
  if (w.cena_podana && ['Netto', 'Brutto'].indexOf(w.cena_podana) < 0) return 'Cena podana: Netto / Brutto';
  if (w.cena_podana === 'Netto' && (w.vat === null || w.vat === undefined || w.vat === '')) return 'cena netto bez stawki VAT %';
  return '';
}

/** Wycofanie: czyści pola wpisywane w Wydatkach (A:H, J:M, O) i w Cenniku (A:F, H:J, L:N). Formuły zostają. */
function usun(ids) {
  var ss = SpreadsheetApp.getActive();
  var wyniki = [];
  ids.forEach(function (id) {
    var zrodlo = 'notion:' + id;
    var wynik = {id: id, wydatki: [], cennik: []};
    var a = ss.getSheetByName(ARKUSZ_WYDATKI);
    var na = Math.max(a.getLastRow(), PIERWSZY_WIERSZ) - PIERWSZY_WIERSZ + 1;
    a.getRange(PIERWSZY_WIERSZ, 15, na, 1).getValues().forEach(function (w, i) {
      if (String(w[0]) === zrodlo) {
        var r = PIERWSZY_WIERSZ + i;
        a.getRange(r, 1, 1, 8).clearContent(); a.getRange(r, 10, 1, 4).clearContent(); a.getRange(r, 15).clearContent();
        wynik.wydatki.push(r);
      }
    });
    var c = ss.getSheetByName(ARKUSZ_CENNIK);
    var nc = Math.max(c.getLastRow(), PIERWSZY_WIERSZ) - PIERWSZY_WIERSZ + 1;
    c.getRange(PIERWSZY_WIERSZ, 14, nc, 1).getValues().forEach(function (w, i) {
      if (String(w[0]) === zrodlo) {
        var r = PIERWSZY_WIERSZ + i;
        c.getRange(r, 1, 1, 6).clearContent(); c.getRange(r, 8, 1, 3).clearContent(); c.getRange(r, 12, 1, 3).clearContent();
        wynik.cennik.push(r);
      }
    });
    wyniki.push(wynik);
  });
  SpreadsheetApp.flush();
  return {ok: true, wyniki: wyniki};
}

/** Wartości wszystkich zakładek (bez formuł) – kopia do analiz po stronie Maca. Daty jako RRRR-MM-DD. */
function dane() {
  var ss = SpreadsheetApp.getActive();
  var strefa = ss.getSpreadsheetTimeZone();
  var wynik = {};
  ss.getSheets().forEach(function (a) {
    var n = a.getLastRow(), k = a.getLastColumn();
    if (!n || !k) { wynik[a.getName()] = []; return; }
    var w = a.getRange(1, 1, n, k).getValues().map(function (r) {
      return r.map(function (x) { return x instanceof Date ? Utilities.formatDate(x, strefa, 'yyyy-MM-dd') : x; });
    });
    while (w.length && w[w.length - 1].every(function (x) { return x === ''; })) w.pop();
    wynik[a.getName()] = w;
  });
  return {ok: true, nazwa: ss.getName(), arkusze: wynik};
}

/** Zmiany układu i wyglądu na miejscu. Operacje: zakres, wyczysc, walidacja, warunkowe, szerokosci, wysokosci,
 *  zamroz, siatka, ramka, wstaw. Dane wpisane przez inwestora zmienia tylko „zakres” – generator wysyła tam wyłącznie
 *  nagłówki, formuły i formaty, nigdy kolumn z danymi. */
function zmien(operacje) {
  var ss = SpreadsheetApp.getActive();
  var wykonane = 0;
  operacje.forEach(function (o, nr) {
    if (ZAKLADKI.indexOf(o.arkusz) < 0) throw new Error('operacja ' + nr + ': nieznana zakładka ' + o.arkusz);
    var a = ss.getSheetByName(o.arkusz);
    switch (o.op) {
      case 'zakres':
        var r = a.getRange(o.a1);
        if (o.wartosci) {
          o.wartosci.forEach(function (w) { w.forEach(function (x) {
            if (typeof x === 'string' && x.charAt(0) === '=' && ZAKAZANE.test(x)) throw new Error('operacja ' + nr + ': zakazana formuła');
          }); });
          r.setValues(o.wartosci);
        }
        if (o.formaty) r.setNumberFormats(o.formaty);
        if (o.tla) r.setBackgrounds(o.tla);
        if (o.kolory) r.setFontColors(o.kolory);
        if (o.grubosci) r.setFontWeights(o.grubosci);
        if (o.style) r.setFontStyles(o.style);
        if (o.rozmiary) r.setFontSizes(o.rozmiary);
        if (o.wyrownania) r.setHorizontalAlignments(o.wyrownania);
        if (o.zawijanie !== undefined) r.setWrap(o.zawijanie);
        if (o.pionowo) r.setVerticalAlignment(o.pionowo);
        break;
      case 'wyczysc':
        if (o.arkusz !== ARKUSZ_CENNIK && o.arkusz !== ARKUSZ_SZACUNEK) throw new Error('operacja ' + nr + ': czyścić wolno tylko Cennik i szacunek AI');
        if (o.arkusz === ARKUSZ_CENNIK) {
          var wpisy = a.getRange(PIERWSZY_WIERSZ, 1, Math.max(a.getLastRow() - PIERWSZY_WIERSZ + 1, 1), 2).getValues();
          if (wpisy.some(function (w) { return w[0] !== '' || w[1] !== ''; })) throw new Error('Cennik ma dane – nie czyszczę');
        }
        a.getRange(o.a1).clear().clearDataValidations();
        break;
      case 'walidacja':
        var b = SpreadsheetApp.newDataValidation().setAllowInvalid(true);
        b = o.lista ? b.requireValueInList(o.lista, true) : b.requireValueInRange(ss.getRange(o.zakres), true);
        a.getRange(o.a1).setDataValidation(b.build());
        break;
      case 'warunkowe':
        a.setConditionalFormatRules(o.reguly.map(function (g) {
          var rb = SpreadsheetApp.newConditionalFormatRule().whenFormulaSatisfied(g.formula)
            .setRanges(g.zakresy.map(function (z) { return a.getRange(z); }));
          if (g.tlo) rb = rb.setBackground(g.tlo);
          if (g.kolor) rb = rb.setFontColor(g.kolor);
          if (g.pogrubienie) rb = rb.setBold(true);
          if (g.kursywa) rb = rb.setItalic(true);
          return rb.build();
        }));
        break;
      case 'szerokosci':
        Object.keys(o.kolumny).forEach(function (k) { a.setColumnWidth(a.getRange(k + '1').getColumn(), o.kolumny[k]); });
        break;
      case 'wysokosci':
        a.setRowHeights(o.od, o.do - o.od + 1, o.px);
        break;
      case 'zamroz':
        a.setFrozenRows(o.wiersze); a.setFrozenColumns(o.kolumny);
        break;
      case 'siatka':
        a.setHiddenGridlines(!!o.ukryj);
        break;
      case 'ramka':
        a.getRange(o.a1).setBorder(true, true, true, true, true, true, o.kolor || '#E3E6EA', SpreadsheetApp.BorderStyle.SOLID);
        break;
      case 'wstaw':
        // puste wiersze w Kosztorysie (nowy etap bez konektora) – tylko wewnątrz pozycji, żeby zakresy sum ($5:$<ostatnia>) objęły je same
        var ost = ostatniaPozycja(a);
        if (o.arkusz !== ARKUSZ_KOSZTORYS || !(o.przed > PIERWSZY_WIERSZ && o.przed <= ost) || !(o.ile >= 1 && o.ile <= 5)) {
          throw new Error('operacja ' + nr + ': wstawiać wolno 1–5 wierszy w Kosztorysie, przed wierszem ' + (PIERWSZY_WIERSZ + 1) + '–' + ost);
        }
        a.insertRowsBefore(o.przed, o.ile);
        break;
      default:
        throw new Error('operacja ' + nr + ': nieznana ' + o.op);
    }
    wykonane++;
  });
  SpreadsheetApp.flush();
  return {ok: true, wykonane: wykonane};
}

/** Etap „47 Wyposażenie…” / „3 …” / „P1 Działka” → „47” / „03” / „P1”; reszta → ''. */
function numerEtapu(tekst) {
  var m = /^(P\d|\d{1,2})(\s|$)/.exec(String(tekst).trim());
  if (!m) return '';
  return m[1].charAt(0) === 'P' ? m[1] : ('0' + m[1]).slice(-2);
}

function zwykla(t) {
  return String(t).replace(/\s+/g, ' ').trim().toLowerCase();
}

/** Numer kolumny (od 1) po początku nagłówka w wierszu 4; brak → wyjątek (wołane przed jakąkolwiek zmianą). */
function kolumnaNaglowka(arkusz, poczatek) {
  var nag = arkusz.getRange(PIERWSZY_WIERSZ - 1, 1, 1, arkusz.getLastColumn()).getValues()[0];
  for (var i = 0; i < nag.length; i++) if (String(nag[i]).indexOf(poczatek) === 0) return i + 1;
  throw new Error(arkusz.getName() + ': brak kolumny „' + poczatek + '” w wierszu ' + (PIERWSZY_WIERSZ - 1));
}

function ostatniaPozycja(k) {
  var b = k.getRange(PIERWSZY_WIERSZ, 2, Math.max(k.getLastRow() - PIERWSZY_WIERSZ + 1, 1), 1).getValues();
  for (var i = b.length - 1; i >= 0; i--) if (String(b[i][0]).trim()) return PIERWSZY_WIERSZ + i;
  return PIERWSZY_WIERSZ;
}

/** Kosztorys A:C od wiersza 5 → blok etapu. Nagłówek: pierwszy wiersz z A = etap i pustym B. Blok kończy się na wierszu
 *  z innym niepustym A (inny etap) albo na RAZEM KOSZTORYS – nie na pustym B. Wiersz bloku z A = etap i pustym B to
 *  sierota (ręcznie dodany wiersz bez Lp) – przy niej akcja odmawia, bo sumy etapu byłyby niepewne. */
function blokEtapu(dane, etap) {
  var b = {naglowek: 0, etap: '', pozycje: [], sieroty: [], ostatnia: 0, razem: 0};
  var koniec = false;
  dane.forEach(function (w, i) {
    var r = PIERWSZY_WIERSZ + i, a = String(w[0]).trim(), lp = String(w[1]).trim(), c = String(w[2]).trim();
    if (c === RAZEM_KOSZTORYS) { b.razem = r; koniec = koniec || !!b.naglowek; return; }
    if (lp) b.ostatnia = r;
    if (!b.naglowek) {
      if (a && !lp && numerEtapu(a) === etap) { b.naglowek = r; b.etap = a; }
      return;
    }
    if (koniec) return;
    if (a && a !== b.etap) { koniec = true; return; }
    if (lp) b.pozycje.push({wiersz: r, lp: lp, nazwa: c});
    else if (a) b.sieroty.push(r);
  });
  return b;
}

function kolumnyZFormula(f) {
  var s = [];
  f.forEach(function (x, i) { if (x) s.push(i); });
  return s;
}

/** Komplet formuł pozycji = najczęstszy zestaw kolumn z formułą wśród pozycji arkusza (indeksy od 0); musi obejmować
 *  kolumny PLAN, Wydane, Klucz i Kontrola. Pozycja z liczbą wpisaną ręcznie w kolumnę z formułą kompletu nie ma. */
function kompletFormul(dane, formuly, wymagane) {
  var licz = {}, naj = '', ile = 0;
  dane.forEach(function (w, i) {
    if (!String(w[1]).trim()) return;
    var z = kolumnyZFormula(formuly[i]).join(',');
    licz[z] = (licz[z] || 0) + 1;
    if (licz[z] > ile) { ile = licz[z]; naj = z; }
  });
  var komplet = naj ? naj.split(',').map(Number) : [];
  wymagane.forEach(function (k) {
    if (komplet.indexOf(k) < 0) throw new Error('Kosztorys: pozycje bez formuły w kolumnie ' + (k + 1));
  });
  return komplet;
}

function maKomplet(f, komplet) {
  return komplet.every(function (i) { return !!f[i]; });
}

/** Wzór nowego wiersza: pozycja etapu z kompletem formuł najbliżej ostatniej pozycji etapu, a gdy żadnej – najbliższa
 *  taka pozycja arkusza. → numer wiersza (przed wstawieniem) albo 0. */
function wybierzWzor(b, dane, formuly, komplet) {
  var ostatnia = b.pozycje[b.pozycje.length - 1].wiersz;
  for (var i = b.pozycje.length - 1; i >= 0; i--) {
    if (maKomplet(formuly[b.pozycje[i].wiersz - PIERWSZY_WIERSZ], komplet)) return b.pozycje[i].wiersz;
  }
  var naj = 0;
  dane.forEach(function (w, i) {
    var r = PIERWSZY_WIERSZ + i;
    if (String(w[1]).trim() && maKomplet(formuly[i], komplet) && (!naj || Math.abs(r - ostatnia) < Math.abs(naj - ostatnia))) naj = r;
  });
  return naj;
}

/** Najwyższy numer pozycji etapu – z Kosztorysu i z Wydatków (kol. „Pozycja”), żeby nie nadać ponownie numeru usuniętej
 *  pozycji, do której odwołują się stare wydatki. */
function maksNumer(ss, etap, lpEtapu) {
  var maks = 0;
  function dolicz(x) {
    var t = String(x).trim().split(/\s+/)[0];
    if (t.indexOf(etap + '.') !== 0) return;
    var n = Number(t.slice(etap.length + 1));
    if (n % 1 === 0 && n > maks) maks = n;
  }
  lpEtapu.forEach(dolicz);
  var w = ss.getSheetByName(ARKUSZ_WYDATKI);
  var kp = kolumnaNaglowka(w, 'Pozycja');
  var n = w.getLastRow() - PIERWSZY_WIERSZ + 1;
  if (n > 0) w.getRange(PIERWSZY_WIERSZ, kp, n, 1).getValues().forEach(function (x) { dolicz(x[0]); });
  return maks;
}

/** Liczby, które wstawienie pustej pozycji nie może zmienić: tabela „Kontrola powiązań” (Podsumowanie), RAZEM
 *  KOSZTORYS (PLAN, Wydane) i sumy w nagłówku etapu. Szuka po etykietach, nie po adresach. */
function kontrola(ss, k, naglowek) {
  var p = ss.getSheetByName(ARKUSZ_PODSUMOWANIE).getDataRange().getValues();
  var wynik = {};
  for (var r = 0; r < p.length; r++) {
    for (var c = 0; c + 1 < p[r].length; c++) {
      if (String(p[r][c]).trim() !== KONTROLA) continue;
      for (var i = 1; i <= 3 && r + i < p.length; i++) wynik[String(p[r + i][c])] = p[r + i][c + 1];
    }
  }
  if (!Object.keys(wynik).length) throw new Error('Podsumowanie: brak tabeli „' + KONTROLA + '”');
  var razem = blokEtapu(k.getRange(PIERWSZY_WIERSZ, 1, k.getLastRow() - PIERWSZY_WIERSZ + 1, 3).getValues(), '-').razem;
  if (!razem) throw new Error('Kosztorys: brak wiersza ' + RAZEM_KOSZTORYS);
  wynik['RAZEM PLAN'] = k.getRange(razem, kolumnaNaglowka(k, 'PLAN')).getValue();
  wynik['RAZEM Wydane'] = k.getRange(razem, kolumnaNaglowka(k, 'Wydane')).getValue();
  if (naglowek) {
    var f = k.getRange(naglowek, 1, 1, k.getLastColumn()).getFormulas()[0];
    var v = k.getRange(naglowek, 1, 1, k.getLastColumn()).getValues()[0];
    f.forEach(function (x, i) { if (SUMA_ETAPU.test(x)) wynik['suma etapu, kolumna ' + (i + 1)] = v[i]; });
  }
  return wynik;
}

/** Nazwy wartości, które się różnią (bez samych liczb – komunikat trafia do Notion i do logu). */
function rozne(przed, po) {
  return Object.keys(przed).concat(Object.keys(po)).filter(function (n, i, wszystkie) {
    if (wszystkie.indexOf(n) !== i) return false;
    var a = przed[n], b = po[n];
    if (typeof a === 'number' && typeof b === 'number') return Math.abs(a - b) >= 0.005;
    return String(a) !== String(b);
  });
}

/** Wiersz pozycji: komplet formuł, klucz „Lp Nazwa”, pusta Kontrola. → opis problemu albo ''. */
function sprawdzWiersz(k, r, klucz, komplet, kol) {
  var kolumn = k.getLastColumn();
  if (!maKomplet(k.getRange(r, 1, 1, kolumn).getFormulas()[0], komplet)) return 'wiersz ' + r + ' bez kompletu formuł';
  var w = k.getRange(r, 1, 1, kolumn).getValues()[0];
  if (String(w[kol.klucz]) !== klucz) return 'klucz w wierszu ' + r + ' się nie zgadza';
  if (String(w[kol.kontrola])) return 'kontrola w wierszu ' + r + ': ' + String(w[kol.kontrola]);
  return '';
}

/** Nowa pozycja w istniejącym etapie Kosztorysu. p = {etap: '47', nazwa, typ, jedn}. Zwraca {ok, lp, klucz, wiersz, juz},
 *  {ok: true, brak_etapu: true[, bez_pozycji: true]} albo {ok: false, blad}. naSucho – tylko plan, bez zmian w arkuszu. */
function dodajPozycje(p, naSucho) {
  var etap = String(p.etap || '').trim();
  var nazwa = String(p.nazwa || '').replace(/\s+/g, ' ').trim();
  var typ = String(p.typ || ''), jedn = String(p.jedn || 'kpl');
  if (!/^(P\d|\d{2})$/.test(etap)) return {ok: false, blad: 'etap nowej pozycji: numer, np. 47 albo P2'};
  if (!nazwa || nazwa.length > 120) return {ok: false, blad: 'nazwa nowej pozycji: 1–120 znaków'};
  if (/^[=+\-@']/.test(nazwa) || ZAKAZANE.test(nazwa)) return {ok: false, blad: 'nazwa nowej pozycji: bez = + - @ \' na początku i bez formuł'};
  if (TYPY.indexOf(typ) < 0) return {ok: false, blad: 'typ nowej pozycji: ' + TYPY.join(' / ')};
  if (JEDNOSTKI.indexOf(jedn) < 0) return {ok: false, blad: 'jednostka nowej pozycji: ' + JEDNOSTKI.join(' / ')};
  var ss = SpreadsheetApp.getActive();
  var k = ss.getSheetByName(ARKUSZ_KOSZTORYS);
  var kolumn = k.getLastColumn();
  var plan;
  try {
    // wszystko, co akcja czyta po nagłówkach i etykietach, sprawdzone przed jakąkolwiek zmianą
    var kol = {plan: kolumnaNaglowka(k, 'PLAN') - 1, wydane: kolumnaNaglowka(k, 'Wydane') - 1,
               klucz: kolumnaNaglowka(k, 'Klucz') - 1, kontrola: kolumnaNaglowka(k, 'Kontrola') - 1};
    var n = k.getLastRow() - PIERWSZY_WIERSZ + 1;
    var dane = k.getRange(PIERWSZY_WIERSZ, 1, n, 3).getValues();
    var formuly = k.getRange(PIERWSZY_WIERSZ, 1, n, kolumn).getFormulas();
    var komplet = kompletFormul(dane, formuly, [kol.plan, kol.wydane, kol.klucz, kol.kontrola]);
    var b = blokEtapu(dane, etap);
    if (!b.naglowek) return {ok: true, brak_etapu: true, etap: etap};
    if (b.sieroty.length) return {ok: false, blad: 'wiersz ' + b.sieroty[0] + ' w etapie ' + etap + ' bez Lp – uzupełnij Lp albo usuń wiersz'};
    for (var i = 0; i < b.pozycje.length; i++) {
      var x = b.pozycje[i];
      if (zwykla(x.nazwa) !== zwykla(nazwa)) continue;
      var zly = sprawdzWiersz(k, x.wiersz, x.lp + ' ' + x.nazwa, komplet, kol);
      if (zly) return {ok: false, blad: 'pozycja ' + x.lp + ' już jest, ale ' + zly + ' – popraw ją w arkuszu'};
      return {ok: true, juz: true, lp: x.lp, klucz: x.lp + ' ' + x.nazwa, wiersz: x.wiersz};
    }
    if (!b.pozycje.length) return {ok: true, brak_etapu: true, bez_pozycji: true, etap: etap};
    if (!b.razem || b.razem < b.ostatnia) return {ok: false, blad: 'Kosztorys: brak wiersza ' + RAZEM_KOSZTORYS + ' pod pozycjami'};
    var lp = etap + '.' + (maksNumer(ss, etap, b.pozycje.map(function (x) { return x.lp; })) + 1);
    var ostatnia = b.pozycje[b.pozycje.length - 1].wiersz;
    // przed ostatnią pozycją etapu = zawsze wewnątrz zakresów $5:$<ostatnia pozycja arkusza> (RAZEM, Etapy, Podsumowanie);
    // etap z jedną pozycją – za nią (kolejność), chyba że to ostatnia pozycja arkusza (wtedy wiersz wypadłby z zakresów)
    var przed = b.pozycje.length > 1 || ostatnia === b.ostatnia;
    var nowy = przed ? ostatnia : ostatnia + 1;
    var wzorPrzed = wybierzWzor(b, dane, formuly, komplet);
    if (!wzorPrzed) return {ok: false, blad: 'Kosztorys: żadna pozycja nie ma kompletu formuł – brak wzoru dla nowego wiersza'};
    plan = {lp: lp, klucz: lp + ' ' + nazwa, wiersz: nowy, przed: przed, koniecBloku: ostatnia + 1,
            wzor: wzorPrzed >= nowy ? wzorPrzed + 1 : wzorPrzed, b: b, kol: kol, komplet: komplet};
    var przedZmiana = kontrola(ss, k, b.naglowek);
    var formulyNaglowka = k.getRange(b.naglowek, 1, 1, kolumn).getFormulas()[0];
  } catch (err) {
    return {ok: false, blad: String(err.message || err).slice(0, 200) + ' – arkusz bez zmian'};
  }
  if (naSucho) {
    return {ok: true, na_sucho: true, lp: plan.lp, klucz: plan.klucz, wiersz: plan.wiersz, przed_ostatnia: plan.przed,
            suma_etapu: (b.naglowek + 1) + ':' + plan.koniecBloku, wzor: wzorPrzed, kontrola: Object.keys(przedZmiana)};
  }
  if (przed) k.insertRowBefore(ostatnia); else k.insertRowAfter(ostatnia);
  var blad;
  try {
    k.getRange(plan.wzor, 1, 1, kolumn).copyTo(k.getRange(nowy, 1, 1, kolumn));   // formaty, listy, formuły (adresy względne)
    // od razu Lp i nazwa (jako tekst – „04.9” bez formatu stałoby się datą): przerwany skrypt nie zostawi wiersza bez Lp
    k.getRange(nowy, 2, 1, 2).setNumberFormat('@');
    k.getRange(nowy, 2, 1, 4).setValues([[lp, nazwa, typ, jedn]]);
    var f = k.getRange(nowy, 1, 1, kolumn).getFormulas()[0];
    for (var c = 6; c <= kolumn; c++) if (!f[c - 1]) k.getRange(nowy, c).clearContent();   // dane wzoru (ilość, plan ręczny…) – nie
    k.getRange(nowy, 1).setFormula('=$A$' + b.naglowek);
    formulyNaglowka.forEach(function (fn, i) {
      var m = SUMA_ETAPU.exec(fn);
      if (m) k.getRange(b.naglowek, i + 1).setFormula('=SUM(' + m[1] + (b.naglowek + 1) + ':' + m[1] + plan.koniecBloku + ')');
    });
    SpreadsheetApp.flush();
    blad = sprawdzWstawienie(ss, k, plan, przedZmiana);
  } catch (err) {
    blad = 'błąd skryptu po wstawieniu (' + String(err.message || err).slice(0, 150) + ')';
  }
  if (!blad) return {ok: true, juz: false, lp: lp, klucz: plan.klucz, wiersz: nowy};
  try {
    cofnijWstawienie(k, nowy, b.naglowek, formulyNaglowka);
  } catch (err) {
    return {ok: false, blad: 'nowa pozycja ' + lp + ': ' + blad + '; wycofanie nieudane – sprawdź wiersz ' + nowy + ' (Plik → Historia wersji)'};
  }
  return {ok: false, blad: 'nowa pozycja ' + lp + ': ' + blad + ' – wstawiony wiersz usunięty, arkusz bez zmian'};
}

function sprawdzWstawienie(ss, k, plan, przedZmiana) {
  var b = plan.b, nowy = plan.wiersz;
  var kPlan = plan.kol.plan + 1;
  var razem = k.getRange(b.razem + 1, kPlan).getFormula();   // RAZEM przesunął się o wstawiony wiersz
  var m = /[A-Z]+\$?\d+:\$?[A-Z]+\$?(\d+)/.exec(razem);       // =SUMIFS(G$5:G$92;…) → 92
  if (!m || Number(m[1]) < plan.koniecBloku) return 'nowy wiersz poza sumą ' + RAZEM_KOSZTORYS;
  var s = SUMA_ETAPU.exec(k.getRange(b.naglowek, kPlan).getFormula());
  if (!s || Number(s[2]) > nowy || Number(s[4] || s[2]) < nowy) return 'nowy wiersz poza sumą etapu';
  if (String(k.getRange(nowy, 1).getValue()).trim() !== b.etap) return 'etap nowego wiersza się nie zgadza';
  var zly = sprawdzWiersz(k, nowy, plan.klucz, plan.komplet, plan.kol);
  if (zly) return zly;
  var r = rozne(przedZmiana, kontrola(ss, k, b.naglowek));
  if (r.length) return 'zmieniło się: ' + r.join(', ');
  return '';
}

function cofnijWstawienie(k, nowy, naglowek, formulyNaglowka) {
  k.deleteRow(nowy);
  formulyNaglowka.forEach(function (fn, i) {
    if (SUMA_ETAPU.test(fn)) k.getRange(naglowek, i + 1).setFormula(fn);
  });
  SpreadsheetApp.flush();
}
```
