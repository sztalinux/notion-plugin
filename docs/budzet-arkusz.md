# Budżet domowy → Arkusz Google – wydatki z wpisów od razu w arkuszu (dla agentów i inwestora)

Budżet domowy żyje w arkuszu Google „Budżet domowy” (zakładka Transakcje, prywatne konto inwestora). Wydatek z wpisu
(`wpis.py dodaj`, procedura `budzet`, sekcja A) trafia najpierw do pliku miesiąca `<hub>/.dom/budzet/listy/RRRR-MM-wpisy.jsonl`,
a stamtąd – w ciągu godziny – do arkusza przez mały skrypt Apps Script przypięty do arkusza. Zamknięcie miesiąca (sekcje B–C)
nie dubluje tych wierszy: płatność z wyciągu przypina się do wiersza z wpisu. Kosztorys budowy ma osobny skrypt i osobny
arkusz (`docs/wydatki-arkusz.md`) – te dwa skrypty nie mają wspólnych sekretów.

Gdzie co jest opisane:
- procedura dla agenta: `plugins/ja/skills/budzet/SKILL.md` (A – wpis, B–C – zamknięcie), układ arkusza: `references/arkusz.md`;
- narzędzie: `tools/budzet/arkusz_budzetu.py` (sam Python, biblioteka standardowa); kod Apps Script: sekcja 8 tego pliku.

## 1. Przepływ danych

```
wpis we „📝 Wpisach” · wiadomość w Claude Code · Skrzynka („Zrobić: wydatek …”) · zdjęcie paragonu we „📝 Wpisach”
   │  agent: wpis.py dodaj albo paragon.py rozpisz (części <id>-1…n, bez sieci) → listy/RRRR-MM-wpisy.jsonl
   ▼
arkusz_budzetu.py sync  – automat po każdym przebiegu na Macu; w Claude Code agent zaraz po zapisie
   │  tylko zapisy z datą od 1.12.2026 (ARKUSZ_OD w tools/budzet/wspolne.py), nowe i zmienione
   ▼
Apps Script arkusza „Budżet domowy” (aplikacja internetowa + sekret, @OnlyCurrentDoc)
   │  dopisz: nowy wiersz w Transakcjach (ID wpisu w kolumnie O, Notatki „z wpisu”) · popraw · usuń
   ▼
znacznik wysyłki w zapisie (pole „arkusz”: wiersz, skrót treści, czas)
   │  zamknięcie miesiąca: importuj.py → przypięcia (ID wyciągu do O, kwota z wyciągu do D) → arkusz_budzetu.py przypnij
   ▼
nocny przebieg: arkusz_budzetu.py kontrola – wpis bez wiersza w arkuszu → komunikat 🔔 we „📝 Wpisach”
```

Wpisy sprzed 1.12.2026 (listopad) zostają w pliku i wchodzą przy zamknięciu miesiąca, jak dotąd. Gotówka jest tylko we
wpisach – osobnej listy gotówki na koniec miesiąca nie ma.

## 2. Polecenia (`python3 tools/budzet/arkusz_budzetu.py …`, katalog repo)

| Polecenie | Co robi | Kto woła |
|---|---|---|
| `sync` | zapisy bez znacznika → `dopisz` (ID już w O → od razu `popraw` bieżącą treścią, potem znacznik); zmieniona treść → `popraw`; usunięte → `usun`; zapis bez kategorii czeka na zamknięcie; przy blokadzie zamknięcia nic nie wysyła (kod 0) | automat po przebiegu; agent w Claude Code po `wpis.py dodaj` / `usun` |
| `sync --proba` | co by poszło, z odczytem kolumny O (gdy skrypt jest wdrożony): nowy wiersz, już w arkuszu, popraw, usuń; nic nie zapisuje | pierwsza synchronizacja; ręcznie |
| `kontrola` | tylko odczyt: zapis wysłany, a wiersza z jego ID nie ma; zapis niewysłany od ponad doby; wiersz z ID wpisu bez zapisu w pliku; usunięcie czekające ponad dobę – kod 1, gdy coś jest; chwilowy brak połączenia – kod 0, trwały błąd (sekret, wersja kodu, nagłówki) – kod 1 | automat po nocnym przebiegu |
| `ponow <id>…` | czyści znacznik – następny `sync` dopisze wiersz od nowa, a gdy ID jest już w O – poprawi go bieżącą treścią; zapisu usuniętego (`usuniety`) nie rusza – `sync` ponowi usunięcie | agent po odpowiedzi „dopisz ponownie” |
| `zamknij-wpisy --miesiac RRRR-MM` / `zamknij-wpisy <id>…` | znacznik zamknięcia wpisom z listy `wpisy_rozstrzygniete` w `miesiace/RRRR-MM-zapis.json` (rozstrzygnięte bez ID w O: ręczny wiersz, Pomiń, Już w arkuszu) albo podanym ID (odświeża znacznik po ręcznej poprawce wiersza); zwykłego znacznika nie rusza; powtórzone nic nie zmienia. `sync` sam robi to samo dla wszystkich zamkniętych miesięcy (bezpiecznik) | agent przy zamknięciu (C.3 f, pod blokadą) |
| `blokada zaloz` / `blokada zdejmij` | blokada zamknięcia miesiąca (plik `miesiace/.zamkniecie` w folderze danych, ważna 60 min – porzuconą `sync` potem ignoruje): w tym czasie `sync` nic nie wysyła, więc numery wierszy się nie przesuwają, a wiersz zapasowy nie pójdzie drugi raz. `sync` trzyma przez cały przebieg `flock` na `miesiace/.zamkniecie.lock`; `zaloz` czeka na jego koniec do 120 s (potem kod 1) i ponownie wywołane odnawia czas | agent przy zamknięciu (C.3) |
| `przypnij --miesiac RRRR-MM [--proba]` | przypięcia z `miesiace/RRRR-MM-zapis.json` (ID wyciągu do O wszystkich wierszy grupy, kwota z wyciągu do D) | agent przy zamknięciu (C.3) |
| `sprawdz` | sekrety i ping (nazwa arkusza, wersja kodu, nagłówki Transakcji, strefa) | ręcznie, przy problemach |
| `kod` | kod Apps Script z sekcji 8 (`\| LANG=en_US.UTF-8 pbcopy` – do schowka) | przy wklejaniu i aktualizacji kodu |

Kody wyjścia: 0 OK **i także brak konfiguracji** w `sync` i `kontrola` (wtedy jedna linia „nieskonfigurowane – N wpisów czeka
w pliku”; automat nie zgłasza tego jako błędu), 1 błąd (linie `✗`), 2 brak konfiguracji w `przypnij` i `sprawdz`. Komunikaty
niosą tylko liczby, daty i ID – bez kwot i opisów.

## 3. Znacznik wysyłki i zasady

- Zapis w pliku dostaje pole `arkusz` = `{"wiersz": N, "skrot": "<12 znaków>", "czas": "RRRR-MM-DD GG:MM", "kwota": D}`. Skrót liczy się
  z treści zapisu bez pól `dodano`, `arkusz`, `usuniety` (`wspolne.skrot`). `sync` wysyła zapis tylko bez znacznika albo ze
  zmienionym skrótem – ręczna poprawka wiersza w arkuszu zostaje, dopóki nie zmieni się wpis.
- Wiersz szuka się zawsze po ID w kolumnie O (tokeny po przecinku, dokładne dopasowanie), nigdy po numerze – numer
  w znaczniku jest informacyjny (usunięcie wiersza wyżej przesuwa numery).
- Znacznik zamknięcia `{"zamkniecie": "RRRR-MM", "skrot", "czas"}` – wpis jest w ręcznym wierszu bez swojego ID: `sync` go
  nie wysyła (także po zmianie treści – wtedy `kontrola` zgłasza „zmieniony po zamknięciu”), `ponow` go nie zdejmuje. Zapis
  bez znacznika z miesiąca zamkniętego starszą wersją (plik zapisu bez `wpisy_rozstrzygniete`) `sync` odrzuca (✗) – dopisze go
  dopiero `sync --mimo-zamkniecia`.
- `wpis.py dodaj` z tym samym `--id` przenosi znacznik (także gdy zmienił się miesiąc daty) – `sync` poprawi wiersz.
- `wpis.py usun` dla zapisu ze znacznikiem zostawia znak `usuniety`; `sync` usuwa wiersz w arkuszu, potem zapis z pliku.
  Wiersz z ID wyciągu w O (płatność przypięta przy zamknięciu) zostaje – skrypt zdejmuje tylko ID wpisu i dopisek „z wpisu”.
- `popraw` nie rusza kwoty (D), gdy w O jest już ID wyciągu (kwota z wyciągu wygrywa), i zostawia pozostałe ID w O.
  Wiersz, w którym są ID kilku wpisów (np. wiersze listopadowe scalone ręcznie), nie jest poprawiany ani usuwany – błąd
  „wiersz ma też inne wpisy”.
- Jeden ID = jeden wiersz: wiersze z wpisów nie są scalane ani przez `sync`, ani przy zamknięciu.
- Paragon (`tools/budzet/paragon.py`, procedura `budzet`, `references/paragony.md`) – części jednej płatności: ID
  `w<id>-1…n`, to samo pole `grupa` (`w<id>`), pole `paragon` (sklep, suma, liczba części, plik zdjęcia). Każda część to
  osobny wiersz (jedna wysyłka `dopisz` dla całej grupy); `przypnij` dostaje listę ich ID, różnicę wobec wyciągu bierze
  największa część. Ponowne `rozpisz` z tym samym ID zastępuje grupę (część, której nie ma, dostaje `usuniety`);
  `wpis.py usun` z ID wpisu albo części usuwa całą grupę (i zwykły wpis z tym ID); `wpis.py dodaj` odmawia ID grupy i ID części, a `rozpisz` – ID części zajętego przez zwykły wydatek.
  Paragon przypięty do płatności z wyciągu albo z zamkniętego miesiąca (`miesiace/RRRR-MM-zapis.json`) `rozpisz` odmawia
  zastąpić. Bezpiecznik w `sync`: część grupy, której `popraw` wrócił z `kwota_z_wyciagu` przy innej kwocie niż w znaczniku,
  albo której `usun` wrócił z `zostal` – błąd (linia ✗ z ID, kod 1 → 🔔), bo arkusz nie przyjął nowej kwoty.
- Zapisy w pliku pod blokadą (`listy/.wpisy.lock`): `wpis.py` i `sync` nie nadpisują sobie zmian.

## 4. Dostęp i bezpieczeństwo

| Kto | Jak sięga do danych | Co może |
|---|---|---|
| `tools/budzet/wpis.py` | plik miesiąca | zapis wydatku – bez sieci |
| `tools/budzet/arkusz_budzetu.py` | `BUDZET_ARKUSZ_URL` i `BUDZET_ARKUSZ_SEKRET` z `.dom/sekrety.env` | dopisz / popraw / usuń wiersze z ID wpisu, przypnij ID wyciągu, odczyt kolumny O |
| Apps Script | przypięty do jednego arkusza (`@OnlyCurrentDoc`) | tylko zakładka Transakcje, tylko wiersze z ID wpisu (prefiks `w`) |
| Konektor Google Sheets (sesja Claude) | konto Google inwestora | odczyt Transakcji przy zamknięciu; zapis wierszy z zamknięcia (C.3) i zapas przypięć |

Zmienne `BUDZET_ARKUSZ_URL` i `BUDZET_ARKUSZ_SEKRET` w środowisku nadpisują plik (testy). Sekretów nie wypisuj ani nie
wklejaj poza `sekrety.env`; wyciek → nowy sekret (sekcja 6, kroki 3 i 5). Zmian w arkuszu nie cofa skrypt – służy do tego
Plik → Historia wersji.

**Zapas (skrypt nie wdrożony albo nie odpowiada):** wpisy czekają w pliku; zamknięcie miesiąca dopisuje brakujące wiersze
po ID (`importuj.py` – zapis bez ID w kolumnie O = nowy wiersz), a przypięcia wpisuje agent konektorem (C.3).

## 5. Problemy

| Objaw | Przyczyna i naprawa |
|---|---|
| `nieskonfigurowane` | skrypt nie wdrożony albo brak zmiennych w `sekrety.env` – sekcja 6; wpisy czekają, nic nie ginie |
| `arkusz: timeout` | Google bywa wolny – zapisy zostają bez znacznika i pójdą przy następnym przebiegu |
| „odpowiedź nie jest JSON” | wdrożenie bez dostępu „Każdy” albo adres `/dev` zamiast `/exec` – sekcja 6, krok 4 |
| „zły sekret” | `BUDZET_ARKUSZ_SEKRET` ≠ właściwość `SEKRET` w Apps Script |
| „arkusz ma kod w wersji N” | starszy kod – wklej nowy (sekcja 6, aktualizacja); zapisy czekają |
| „nagłówki Transakcji inne niż oczekiwane” | ktoś zmienił kolumny A–O – popraw arkusz albo kod (`NAGLOWEK` w sekcji 8 i `references/arkusz.md`) |
| „wiersz ma też inne wpisy” | wiersz scalony ręcznie z kilku wpisów – popraw go ręcznie albo rozdziel (jeden ID = jeden wiersz) |
| `kontrola`: zmieniony po zamknięciu | wpis z ręcznym wierszem (bez ID) zmieniony po zamknięciu miesiąca – popraw wiersz ręcznie, potem `zamknij-wpisy <id>` |
| `sync`: miesiąc zamknięty starszą wersją | wpis jest już w arkuszu (ręczny wiersz) → `zamknij-wpisy <id>`; nie ma go → `sync --mimo-zamkniecia` |
| `kontrola`: brak wiersza | wiersz z ID wpisu skasowany w arkuszu – inwestor decyduje: `ponow <id>` (dopisz ponownie) albo `wpis.py usun` |
| `✗ RRRR-MM-wpisy.jsonl: linia N to nie JSON` | uszkodzona linia w pliku wpisów (ręczna edycja) – popraw albo usuń tę linię; do tego czasu `wpis.py`, `sync`, `kontrola` i import stoją (kod 1) |
| data przesunięta o dzień | daty idą w strefie arkusza (Plik → Ustawienia); nie zmieniaj strefy bez sprawdzenia wierszy |

## 6. Wdrożenie skryptu (raz, inwestor)

1. Otwórz arkusz „Budżet domowy” → Rozszerzenia → Apps Script. W nowym projekcie zastąp całą treść `Kod.gs` kodem z sekcji 8
   (`python3 tools/budzet/arkusz_budzetu.py kod | LANG=en_US.UTF-8 pbcopy` – kod w schowku), zapisz (ikona dyskietki).
2. Nazwij projekt, np. „Budżet – wpisy”. To osobny projekt – kodu kosztorysu w nim nie ma.
3. Ustawienia projektu (koło zębate) → Właściwości skryptu → Dodaj: `SEKRET` = wynik
   `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`. Zapisz.
4. Wdróż → Nowe wdrożenie → typ: Aplikacja internetowa; Wykonaj jako: **Ja**; Kto ma dostęp: **Każdy** (bez sekretu odpowiedź
   „zły sekret”). Autoryzuj (skrypt prosi tylko o ten arkusz). Skopiuj adres kończący się na `/exec`.
5. `<hub>/.dom/sekrety.env` (chmod 600) – dopisz dwie linie: `BUDZET_ARKUSZ_URL=<adres /exec>`, `BUDZET_ARKUSZ_SEKRET=<sekret z kroku 3>`.
6. Sprawdzenie: `python3 tools/budzet/arkusz_budzetu.py sprawdz` (wersja kodu, nagłówki OK), potem
   `python3 tools/budzet/arkusz_budzetu.py sync --proba` – lista „dopisz / już w arkuszu”; porównaj z arkuszem. Dopiero potem
   pierwszy `sync` (albo zostaw automatowi).

Aktualizacja kodu: wklej nowy kod jak w kroku 1, potem Wdróż → Zarządzaj wdrożeniami → ołówek → Wersja: **Nowa** → Wdróż
(adres i sekret bez zmian). `sprawdz` pokaże wersję. Kod zmieniasz tylko w tym pliku (sekcja 8) – `kod` czyta go stąd.

## 7. Interfejs skryptu (POST JSON `{"sekret", "akcja", …}`; odpowiedź `{"ok": true, …}` albo `{"ok": false, "blad"}`)

| Akcja | Wejście | Wynik |
|---|---|---|
| `ping` | – | `wersja`, `arkusz`, `wierszy`, `naglowek_ok`, `strefa` |
| `odczyt` | – | `wiersze`: `[{wiersz, o, data, kwota}]` – każdy wiersz z niepustą kolumną O (data `RRRR-MM-DD`) |
| `dopisz` | `wiersze`: `[W]` | `wyniki`: `[{id, ok, wiersz, juz}]` – `juz` = ID było w O, wiersz bez zmian (klient od razu wysyła `popraw` z bieżącą treścią) |
| `popraw` | `wiersze`: `[W]` | `wyniki`: `[{id, ok, wiersz, kwota_z_wyciagu}]`; brak wiersza → `ok: false` |
| `usun` | `ids`: `[id]` | `wyniki`: `[{id, ok, wiersz, zostal}]` – `wiersz: null`, gdy go nie było; `zostal: true` – wiersz ma ID wyciągu w O, więc zostaje bez ID wpisu (płatność jest prawdziwa) |
| `przypnij` | `przypiecia`: `[{id_wyciagu, ids: [id…], kwoty: {id: liczba}}]` | `wyniki`: `[{id_wyciagu, ok, wiersze}]` |

`W` = `{id, data, status, typ, kwota, kat, pod, konto, osoba, opis, tag, notatki}` – `id` z prefiksem `w`, `data`
`RRRR-MM-DD`, `kwota` liczba albo formuła sumy (`=12.50+3`, tylko cyfry, kropka, plus i minus; arkusz ma ustawienia en_US).
Buduje go `wspolne.wiersz_wpisu` – ten sam wiersz co przy zamknięciu miesiąca. Kilka wierszy w jednym wywołaniu (części
paragonu) – jedna blokada.

## 8. Kod Apps Script (`Kod.gs`)

```javascript
/** @OnlyCurrentDoc */
/**
 * Budżet domowy w Arkuszach Google – punkt wejścia dla tools/budzet/arkusz_budzetu.py (Mac). Instrukcja:
 * docs/budzet-arkusz.md w repozytorium harnessu. Kod nie zawiera danych – działa na arkuszu, do którego jest przypięty.
 * Akcje (POST, JSON {"sekret", "akcja", ...}): ping · odczyt · dopisz (wiersze[]) · popraw (wiersze[]) · usun (ids[]) ·
 * przypnij (przypiecia[]). Zmienia wyłącznie zakładkę Transakcje i wyłącznie wiersze z ID wpisu (prefiks w) w kolumnie O.
 * Cofanie zmian – Plik → Historia wersji.
 */

var WERSJA = 1;
var ARKUSZ = 'Transakcje';
var NAGLOWEK = ['Typ', 'Kwota (PLN)', 'Kategoria', 'Podkategoria', 'Konto', 'Osoba (płaci/dostaje)', 'Opis', 'Projekt', 'Tag',
  'Notatki', 'Miesiąc (1. dzień)', 'Rok', 'ID importu'];  // C1:O1
var TYPY = ['Przychód', 'Wydatek', 'Koszt', 'Inwestycja', 'Przelew'];
var KOL_O = 15;
var FORMAT_DATY = 'd"-"mmm"-"yyyy';
var FORMAT_KWOTY = '#,##0.00" zł"';
var FORMAT_MIESIACA = 'yyyy-mm';

function doPost(e) {
  var z;
  try {
    z = JSON.parse(e.postData.contents);
  } catch (err) {
    return odpowiedz({ok: false, blad: 'niepoprawny JSON'});
  }
  var sekret = PropertiesService.getScriptProperties().getProperty('SEKRET');
  if (!sekret || z.sekret !== sekret) return odpowiedz({ok: false, blad: 'zły sekret'});
  try {
    switch (z.akcja) {
      case 'ping': return odpowiedz(ping());
      case 'odczyt': return odpowiedz({ok: true, wiersze: odczyt()});
      case 'dopisz': return odpowiedz(podBlokada(function () { return dopisz(z.wiersze || []); }));
      case 'popraw': return odpowiedz(podBlokada(function () { return popraw(z.wiersze || []); }));
      case 'usun': return odpowiedz(podBlokada(function () { return usun(z.ids || []); }));
      case 'przypnij': return odpowiedz(podBlokada(function () { return przypnij(z.przypiecia || []); }));
      default: return odpowiedz({ok: false, blad: 'nieznana akcja'});
    }
  } catch (err) {
    return odpowiedz({ok: false, blad: String(err).slice(0, 300)});
  }
}

function doGet() {
  return odpowiedz({ok: false, blad: 'użyj POST'});
}

function odpowiedz(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

function podBlokada(f) {
  var lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    var wynik = f();
    SpreadsheetApp.flush();
    return wynik;
  } finally {
    lock.releaseLock();
  }
}

function arkusz() {
  var a = SpreadsheetApp.getActive().getSheetByName(ARKUSZ);
  if (!a) throw new Error('brak zakładki ' + ARKUSZ);
  return a;
}

function ping() {
  var ss = SpreadsheetApp.getActive();
  var a = arkusz();
  var nag = a.getRange(1, 3, 1, NAGLOWEK.length).getValues()[0].map(String);
  return {ok: true, wersja: WERSJA, arkusz: ss.getName(), wierszy: a.getLastRow(),
    naglowek_ok: nag.join('|') === NAGLOWEK.join('|'), strefa: ss.getSpreadsheetTimeZone()};
}

/** Tokeny kolumny O w wierszach 2..ostatni: [{wiersz, tokeny}]. */
function kolumnaO(a) {
  var n = a.getLastRow() - 1;
  if (n < 1) return [];
  return a.getRange(2, KOL_O, n, 1).getValues().map(function (w, i) {
    return {wiersz: i + 2, tokeny: String(w[0]).split(',').map(function (t) { return t.trim(); }).filter(String)};
  });
}

function wierszeId(kol, id) {
  return kol.filter(function (k) { return k.tokeny.indexOf(id) >= 0; });
}

function odczyt() {
  var a = arkusz();
  var strefa = SpreadsheetApp.getActive().getSpreadsheetTimeZone();
  var n = a.getLastRow() - 1;
  if (n < 1) return [];
  var dane = a.getRange(2, 1, n, KOL_O).getValues();
  var wynik = [];
  dane.forEach(function (w, i) {
    if (String(w[KOL_O - 1]) === '') return;
    wynik.push({wiersz: i + 2, o: String(w[KOL_O - 1]),
      data: w[0] instanceof Date ? Utilities.formatDate(w[0], strefa, 'yyyy-MM-dd') : String(w[0]),
      kwota: typeof w[3] === 'number' ? w[3] : ''});
  });
  return wynik;
}

function tekst(v) {
  var s = v === null || v === undefined ? '' : String(v);
  return /^[=+\-@]/.test(s) ? "'" + s : s;  // tekst zaczynający się od = byłby formułą
}

function sprawdz(w) {
  if (!/^w[^,\s]+$/.test(String(w.id || ''))) return 'id wpisu musi zaczynać się od w (bez przecinków)';
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(w.data || ''))) return 'brak daty';
  if (TYPY.indexOf(w.typ) < 0) return 'nieznany typ ' + w.typ;
  if (!w.kat) return 'brak kategorii';
  if (typeof w.kwota === 'string') {
    if (!/^=[0-9.+\-]+$/.test(w.kwota)) return 'formuła kwoty tylko z cyfr, kropki, + i -';
  } else if (typeof w.kwota !== 'number' || !isFinite(w.kwota)) {
    return 'brak kwoty';
  }
  return '';
}

function ustawKwote(a, r, kwota) {
  var c = a.getRange(r, 4);
  if (typeof kwota === 'string') c.setFormula(kwota); else c.setValue(kwota);
}

/** Pola wpisywane A:L (bez D, gdy zachowajKwote) – wspólne dla dopisz i popraw. Opis, tag i Notatki jako tekst (@),
 *  żeby „3/4” czy „2-3” nie stały się datą. */
function zapiszPola(a, r, w, strefa, zachowajKwote) {
  a.getRange(r, 9).setNumberFormat('@');
  a.getRange(r, 11, 1, 2).setNumberFormat('@');
  a.getRange(r, 1, 1, 3).setValues([[Utilities.parseDate(w.data, strefa, 'yyyy-MM-dd'), tekst(w.status || 'Zrealizowane'),
    w.typ]]);
  if (!zachowajKwote) ustawKwote(a, r, w.kwota);
  a.getRange(r, 5, 1, 8).setValues([[tekst(w.kat), tekst(w.pod), tekst(w.konto), tekst(w.osoba), tekst(w.opis), '',
    tekst(w.tag), tekst(w.notatki)]]);
}

/** Formuły M:N i formaty daty, kwoty i miesiąca – nowy wiersz albo wiersz po przerwanym dopisz. */
function formulyIFormaty(a, r) {
  a.getRange(r, 13, 1, 2).setFormulas([['=IF($A' + r + '="","",DATE(YEAR($A' + r + '),MONTH($A' + r + '),1))',
    '=IF($A' + r + '="","",YEAR($A' + r + '))']]);
  a.getRange(r, 1).setNumberFormat(FORMAT_DATY);
  a.getRange(r, 4).setNumberFormat(FORMAT_KWOTY);
  a.getRange(r, 13).setNumberFormat(FORMAT_MIESIACA);
}

function dopisz(wiersze) {
  var a = arkusz();
  var strefa = SpreadsheetApp.getActive().getSpreadsheetTimeZone();
  var kol = kolumnaO(a);
  var nowy = a.getLastRow() + 1;
  var brak = nowy + wiersze.length - 1 - a.getMaxRows();
  if (brak > 0) a.insertRowsAfter(a.getMaxRows(), brak);  // arkusz bez wolnych wierszy na końcu
  var wyniki = [];
  wiersze.forEach(function (w) {
    var blad = sprawdz(w);
    if (blad) { wyniki.push({id: w.id, ok: false, blad: blad}); return; }
    var juz = wierszeId(kol, w.id);
    if (juz.length) { wyniki.push({id: w.id, ok: true, wiersz: juz[0].wiersz, juz: true}); return; }
    var r = nowy++;
    if (r > 2) a.getRange(r - 1, 1, 1, KOL_O).copyTo(a.getRange(r, 1, 1, KOL_O), SpreadsheetApp.CopyPasteType.PASTE_FORMAT, false);
    a.getRange(r, KOL_O).setValue(w.id);  // ID najpierw: błąd w połowie zostawia wiersz z ID – następny sync go poprawi
    zapiszPola(a, r, w, strefa, false);
    formulyIFormaty(a, r);
    kol.push({wiersz: r, tokeny: [w.id]});
    wyniki.push({id: w.id, ok: true, wiersz: r, juz: false});
  });
  return {ok: true, wyniki: wyniki};
}

/** Jedyny wiersz z tym ID, w którym nie ma ID innych wpisów; inaczej opis błędu. */
function wierszWpisu(kol, id) {
  var k = wierszeId(kol, id);
  if (!k.length) return {blad: 'brak wiersza z tym ID'};
  if (k.length > 1) return {blad: 'kilka wierszy z tym ID: ' + k.map(function (x) { return x.wiersz; }).join(', ')};
  var inne = k[0].tokeny.filter(function (t) { return t.charAt(0) === 'w' && t !== id; });
  if (inne.length) return {blad: 'wiersz ' + k[0].wiersz + ' ma też inne wpisy – popraw ręcznie'};
  return k[0];
}

function popraw(wiersze) {
  var a = arkusz();
  var strefa = SpreadsheetApp.getActive().getSpreadsheetTimeZone();
  var kol = kolumnaO(a);
  return {ok: true, wyniki: wiersze.map(function (w) {
    var blad = sprawdz(w);
    if (blad) return {id: w.id, ok: false, blad: blad};
    var k = wierszWpisu(kol, w.id);
    if (k.blad) return {id: w.id, ok: false, blad: k.blad};
    var zWyciagu = k.tokeny.some(function (t) { return t.charAt(0) !== 'w'; });  // kwota z wyciągu wygrywa
    zapiszPola(a, k.wiersz, w, strefa, zWyciagu);
    if (a.getRange(k.wiersz, 13, 1, 2).getFormulas()[0].join('') === '') formulyIFormaty(a, k.wiersz);  // ślad przerwanego dopisz
    return {id: w.id, ok: true, wiersz: k.wiersz, kwota_z_wyciagu: zWyciagu};
  })};
}

function usun(ids) {
  var a = arkusz();
  return {ok: true, wyniki: ids.map(function (id) {
    if (!/^w[^,\s]+$/.test(String(id || ''))) return {id: id, ok: false, blad: 'id wpisu musi zaczynać się od w'};
    var kol = kolumnaO(a);  // po każdym usunięciu numery wierszy się przesuwają
    if (!wierszeId(kol, id).length) return {id: id, ok: true, wiersz: null};
    var k = wierszWpisu(kol, id);
    if (k.blad) return {id: id, ok: false, blad: k.blad};
    var obce = k.tokeny.filter(function (t) { return t.charAt(0) !== 'w'; });
    if (obce.length) {  // wiersz ma płatność z wyciągu – zostaje; znika tylko ID wpisu i dopisek „z wpisu”
      a.getRange(k.wiersz, KOL_O).setValue(obce.join(','));
      var notatki = a.getRange(k.wiersz, 12);
      if (/^z (wpisu|paragonu)/.test(String(notatki.getValue()))) notatki.setValue('');
      return {id: id, ok: true, wiersz: k.wiersz, zostal: true};
    }
    a.deleteRow(k.wiersz);
    return {id: id, ok: true, wiersz: k.wiersz};
  })};
}

/** ID wyciągu do kolumny O każdego wiersza grupy; kwoty[id] (gdy podana) do D. */
function przypnij(lista) {
  var a = arkusz();
  var kol = kolumnaO(a);
  return {ok: true, wyniki: lista.map(function (p) {
    var idw = String(p.id_wyciagu || '');
    if (!/^[a-z][0-9a-z]+$/.test(idw)) return {id_wyciagu: idw, ok: false, blad: 'złe id wyciągu'};
    var ids = p.ids || [];
    var kwoty = p.kwoty || {};
    var znalezione = [];
    for (var i = 0; i < ids.length; i++) {
      var k = wierszWpisu(kol, ids[i]);
      if (k.blad) return {id_wyciagu: idw, ok: false, blad: ids[i] + ': ' + k.blad};
      var kw = kwoty[ids[i]];
      if (kw !== undefined && kw !== null && (typeof kw !== 'number' || !isFinite(kw))) {
        return {id_wyciagu: idw, ok: false, blad: ids[i] + ': zła kwota'};
      }
      znalezione.push({id: ids[i], k: k, kwota: kw});
    }
    znalezione.forEach(function (z) {
      if (z.k.tokeny.indexOf(idw) < 0) {
        z.k.tokeny.push(idw);
        a.getRange(z.k.wiersz, KOL_O).setValue(z.k.tokeny.join(','));
      }
      if (z.kwota !== undefined && z.kwota !== null) a.getRange(z.k.wiersz, 4).setValue(z.kwota);
    });
    return {id_wyciagu: idw, ok: true, wiersze: znalezione.map(function (z) { return z.k.wiersz; })};
  })};
}
```
