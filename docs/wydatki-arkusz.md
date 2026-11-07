# Wydatki → Arkusz Google (synchronizacja bez ręcznego wgrywania)

Wydatek wpisany w Dzienniku (albo prosto w Notion) sam trafia do arkusza Google z kosztorysem. Bez AI po stronie
arkusza, bez ręcznego eksportu i importu.

## 1. Jak to działa

```
📓 Dziennik („wydałem 5 200 zł na beton na chudziak, 16 m³, przelew”)
   │  przebieg szybki na Macu (co godzinę, claude -p + MCP Notion) – procedura koszty, sekcja B
   ▼
💸 Wydatki → arkusz  (baza Notion na DOM, Arkusz = „Do arkusza”)   ← tu możesz też dopisać wiersz ręcznie z telefonu
   │  tools/wydatki.py sync – po każdym przebiegu (automaty/przeglad.py), czysty Python, token NOTION_TOKEN
   ▼
Apps Script w arkuszu (aplikacja internetowa, sekret)  → dopisuje wiersz w arkuszu Wydatki (+ Cennik, gdy jest ilość)
   │
   ▼
Notion: Arkusz = „W arkuszu” + numer wiersza   albo   „Błąd” + powód (popraw pole, ustaw znów „Do arkusza”)
```

- Opóźnienie: do godziny (przebieg szybki 8:05–22:05 i 22:30) plus kilka sekund.
- Mac wyłączony albo uśpiony → wpisy czekają w Notion i pójdą przy następnym przebiegu. Nic nie ginie.
- Ten sam wpis wysłany dwa razy nie zdubluje się: arkusz rozpoznaje go po kolumnie Źródło (`notion:<id strony>`).
- Lista Pozycja w Notion = pozycje z arkusza Kosztorys; odświeża ją `wydatki.py pozycje` (przebieg wieczorny).
- Wydatek z ilością (np. 16 m³ betonu) dopisuje się też do arkusza Cennik: data, co, jednostka, cena za jednostkę,
  dostawca, ilość, pozycja. Ręczne wpisy w Cenniku zostają nietknięte.
- Kopia arkusza do analiz: `<hub>/Koszty/Kosztorys_google.xlsx`, odświeżana przez `wydatki.py pobierz` (przebieg wieczorny).

## 2. Kto ma dostęp do Notion (żeby się nie gubić)

| Gdzie | Jak łączy się z Notion | Co robi |
|---|---|---|
| Claude Code na Macu (ta aplikacja i `claude -p` w automatach) | lokalny serwer MCP `notion` (logowanie OAuth przez `/mcp`) | czyta i zapisuje – przebiegi Dziennika, rozmowy |
| Skrypty Pythona na Macu (`wiedza.py`, `migawka.py`, `wydatki.py`) | token integracji `NOTION_TOKEN` z `.dom/sekrety.env` (prawo odczytu i zmiany treści) | indeks wiedzy i migawka – tylko odczyt; `wydatki.py` – odczyt kolejki, zmiana pól Arkusz/Błąd/Wiersz i listy Pozycja w bazie 💸 Wydatki |
| GitHub Actions (prywatne repo kopii, `tryb-gleboki.yml`) | **żadnego** – ma tylko token Claude | odpowiada na pytania z telefonu z kopii indeksu wiedzy |
| claude.ai (czat, telefon) | konektor Notion zablokowany przez organizację | zapisy idą do „📥 Skrzynki”, Mac przenosi je do Notion |

Arkusz Google nie ma konektora AI. Dopisuje do niego wyłącznie skrypt Apps Script na Twoim koncie Google, wołany
przez `wydatki.py`. Claude nie czyta arkusza bezpośrednio – do analiz służy kopia `.xlsx` (sekcja 1).

## 3. Konfiguracja – krok po kroku (raz)

Krok 0 – porządek z Excelem. Zamknij stary plik `Kosztorys_17.10.2026_stan_zero_v2.xlsx` (Excel trzyma go otwartego).
Jeśli dopisałeś w nim wydatki po 2.09.2026, przepisz je do `Kosztorys_stan_zero_2026-11-07.xlsx` przed importem.

1. **Konto Google: prywatne**, nie służbowe. Na koncie firmowym administrator może blokować aplikacje Apps Script
   z dostępem „Każdy”, a dane budowy to sprawa prywatna.
2. **Import arkusza.** Dysk Google → Nowy → Prześlij plik → `Koszty/Kosztorys_stan_zero_2026-11-07.xlsx`. Otwórz go,
   Plik → Zapisz jako Arkusze Google. Nazwij np. „Kosztorys budowy”. Wgrany `.xlsx` usuń z Dysku, żeby nie mylić wersji.
   Sprawdź: Plik → Ustawienia → Język i region = Polska, strefa czasowa = (GMT+01:00) Warsaw; w Wydatkach działają listy
   Etap / Pozycja / Typ.
3. **Kod.** W arkuszu: Rozszerzenia → Apps Script. Skasuj zawartość `Kod.gs`, wklej kod z sekcji 7, zapisz (ikona dyskietki).
   Do schowka skopiujesz go w Terminalu: `python3 tools/wydatki.py kod | pbcopy` (w katalogu repo harnessu).
4. **Sekret.** W Apps Script: Ustawienia projektu (koło zębate) → Właściwości skryptu → Dodaj właściwość:
   nazwa `SEKRET`, wartość – długi losowy ciąg. Wygeneruj go w Terminalu:
   `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
5. **Wdrożenie.** Wdróż → Nowe wdrożenie → typ „Aplikacja internetowa”. Wykonaj jako: **Ja**. Kto ma dostęp: **Każdy**.
   Wdróż → Autoryzuj dostęp → wybierz konto → „Zaawansowane” → „Przejdź do … (niebezpieczne)” (to Twój własny,
   niezweryfikowany przez Google skrypt) → Zezwól. Skopiuj „URL aplikacji internetowej” (kończy się na `/exec`).
   „Każdy” oznacza: kto zna adres, może wysłać żądanie – bez sekretu dostaje „zły sekret”. Adresu i sekretu nie
   wklejaj nigdzie poza `sekrety.env`.
6. **Sekrety na Macu.** Dopisz dwie linie do `~/Documents/Dom/.dom/sekrety.env`:
   ```
   ARKUSZ_URL=<URL z kroku 5>
   ARKUSZ_SEKRET=<ten sam ciąg co w kroku 4>
   ```
7. **Sprawdzenie** (Terminal, w katalogu repo harnessu):
   ```
   python3 tools/wydatki.py sprawdz
   python3 tools/wydatki.py pozycje
   ```
   Pierwsze ma pokazać „arkusz: OK”, drugie – liczbę pozycji wgranych do listy Pozycja w Notion. Potem
   `python3 tools/wydatki.py pobierz` – ma zapisać `Koszty/Kosztorys_google.xlsx`.
8. **Próba.** W Notion → DOM → 💸 Wydatki → arkusz dodaj wiersz testowy (kwota 1 zł, pozycja dowolna, Arkusz
   „Do arkusza”), uruchom `python3 tools/wydatki.py sync` i sprawdź wiersz w arkuszu – zwłaszcza datę (ten sam dzień co
   w Notion) i kwotę. Potem usuń go w obu miejscach.

Od tej chwili nic nie robisz ręcznie – przebiegi na Macu wołają skrypt same.

## 4. Na co dzień

- **W Dzienniku** pisz jak zwykle: kwota, na co, ile (przy materiale), jak zapłacone. Przebieg zrobi z tego wiersz
  w 💸 Wydatki. Niejasne (nie wiadomo, która pozycja) → pytanie ❓ pod wpisem, jak przy innych wpisach.
- **Ręcznie z telefonu:** nowy wiersz w 💸 Wydatki: Wydatek, Data, Kwota, Pozycja (z listy), Typ, Ilość + Jedn.
  (materiał), Płatność, Sposób. Pole Arkusz możesz zostawić puste – pusty i „Do arkusza” idą tak samo; „Nie wysyłać”
  wstrzymuje wiersz.
- **Jedna droga na wydatek:** albo Dziennik / 💸 Wydatki, albo ręcznie w arkuszu – nie oba, bo wyjdzie podwójnie.
- **Błąd** (pole Błąd mówi co): popraw pole, ustaw Arkusz = „Do arkusza” – pójdzie przy następnym przebiegu.
- **Korekta po wysłaniu:** popraw wiersz bezpośrednio w arkuszu. Notion jest tylko kolejką; źródłem prawdy dla liczb
  jest arkusz.
- **Pomyłka (wydatek nie powinien był pójść):** `python3 tools/wydatki.py wycofaj <id strony>` – czyści wiersz w Wydatkach
  i w Cenniku, w Notion ustawia „Nie wysyłać”. Id strony to końcówka jej adresu w Notion.
- **Nowa pozycja kosztorysu:** dodaj ją w arkuszu Kosztorys (instrukcja w arkuszu), lista w Notion odświeży się wieczorem
  (albo od razu: `python3 tools/wydatki.py pozycje`).

## 5. Polecenia

| Polecenie | Co robi | Kto woła |
|---|---|---|
| `wydatki.py sync` | kolejka „Do arkusza” → arkusz, wynik do Notion | `automaty/przeglad.py` po każdym przebiegu |
| `wydatki.py sync --proba` | pokazuje, co poszłoby do arkusza; nic nie zapisuje | ręcznie |
| `wydatki.py pozycje` | pozycje z arkusza → lista Pozycja w Notion | przebieg wieczorny |
| `wydatki.py pobierz` | kopia arkusza → `Koszty/Kosztorys_google.xlsx` | przebieg wieczorny, ręcznie przed analizą |
| `wydatki.py wycofaj <id>…` | czyści wydatek w arkuszu (Wydatki i Cennik), w Notion „Nie wysyłać” | ręcznie, asystent na prośbę |
| `wydatki.py sprawdz` | sekrety, dostęp do bazy i arkusza | ręcznie |
| `wydatki.py kod` | wypisuje kod Apps Script (z `| pbcopy` – do schowka) | ręcznie przy aktualizacji kodu |

Kody wyjścia: 0 OK, 1 błąd (linie `✗`), 2 brak konfiguracji (ARKUSZ_URL / ARKUSZ_SEKRET). Wynik każdego uruchomienia
z automatu jest w logu przebiegu (`~/Documents/Dom/.dom/automaty/<tryb>-RRRR-MM-DD.log`, linia „po przebiegu wydatki.py …”).

## 6. Problemy

| Objaw | Przyczyna i naprawa |
|---|---|
| „odpowiedź nie jest JSON” | wdrożenie nie ma dostępu „Każdy” albo adres jest od edytora (`/dev`) – krok 5, adres `/exec` |
| „Cannot read properties of null (reading 'getRange')” albo inna liczba pozycji niż w pliku | zaimportowano inny plik niż `Kosztorys_stan_zero_2026-11-07.xlsx` (brak zakładki Wydatki) – w tym samym arkuszu Google: Plik → Importuj → Prześlij → właściwy plik → „Zastąp arkusz kalkulacyjny”; kod Apps Script, sekret i adres zostają |
| „zły sekret” | `ARKUSZ_SEKRET` ≠ właściwość `SEKRET` – krok 4 i 6 |
| „pozycja … nie istnieje w Kosztorysie” | pozycję usunięto albo przenumerowano w arkuszu – wybierz inną, `pozycje` odświeży listę |
| HTTP 404 z Notion | baza 💸 Wydatki niedostępna dla integracji – Notion → baza → ⋯ → Połączenia → dodaj integrację |
| HTTP 403 z Notion przy zmianie pola | integracja bez prawa „Update content” – notion.so/my-integrations → Capabilities |
| eksport `pobierz`: HTTP 401/403 | brak zgody na Dysk – w Apps Script uruchom raz dowolną funkcję (np. `ping`) z edytora i zaakceptuj nowe uprawnienia, potem nowa wersja wdrożenia |
| data w arkuszu o dzień przesunięta | arkusz ma inną strefę niż Polska – Plik → Ustawienia → Strefa czasowa (GMT+01:00) Warsaw |
| „nieznana akcja” przy `wycofaj` albo brak wierszy w Cenniku | w Apps Script jest starszy kod – wklej kod z sekcji 7 i zrób nową wersję wdrożenia (wiersz niżej) |
| zmieniłeś kod w Apps Script | Wdróż → Zarządzaj wdrożeniami → ołówek → Wersja: Nowa → Wdróż (adres zostaje ten sam) |

## 7. Kod Apps Script (wklej do `Kod.gs`)

```javascript
/**
 * Kosztorys w Arkuszach Google – punkt wejścia dla tools/wydatki.py (Mac). Instrukcja: docs/wydatki-arkusz.md
 * w repozytorium harnessu. Kod nie zawiera danych – działa na arkuszu, do którego jest przypięty.
 * Akcje (POST, JSON {"sekret", "akcja", ...}): ping · pozycje · dopisz (wiersze[]) · usun (ids[]) · xlsx.
 * Wydatek z ilością trafia też do Cennika (cena za jednostkę). Kolumn z formułami (Wydatki I i N, Cennik G) skrypt
 * nigdy nie nadpisuje; usun czyści tylko pola wpisywane, więc formuły zostają.
 */

var ARKUSZ_WYDATKI = 'Wydatki';
var ARKUSZ_KOSZTORYS = 'Kosztorys';
var ARKUSZ_CENNIK = 'Cennik';
var PIERWSZY_WIERSZ = 5;
var STATUSY = ['Zrealizowane', 'Do zapłaty'];
var TYPY = ['Materiał', 'Robocizna', 'Sprzęt', 'Usługa', 'Formalności'];

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
      case 'dopisz': return odpowiedz(dopisz(zadanie.wiersze || []));
      case 'usun': return odpowiedz(usun(zadanie.ids || []));
      case 'xlsx': return odpowiedz(eksportXlsx());
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

function ping() {
  var ss = SpreadsheetApp.getActive();
  var dane = ss.getSheetByName(ARKUSZ_WYDATKI).getRange('C' + PIERWSZY_WIERSZ + ':C').getValues();
  var n = dane.filter(function (w) { return w[0] !== ''; }).length;
  return {ok: true, arkusz: ss.getName(), wydatki: n};
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
  var lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    var arkusz = SpreadsheetApp.getActive().getSheetByName(ARKUSZ_WYDATKI);
    var strefa = SpreadsheetApp.getActive().getSpreadsheetTimeZone();  // data = ten dzień w strefie arkusza
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
      var cennik = Number(w.ilosc) > 0 ? doCennika(w, p, strefa, zrodlo) : null;
      wyniki.push({id: w.id, ok: true, wiersz: wolny, juz: false, cennik: cennik});
      wolny = nastepnyWolny(arkusz, wolny + 1);
    });
    SpreadsheetApp.flush();
    return {ok: true, wyniki: wyniki};
  } finally {
    lock.releaseLock();
  }
}

/** Cennik: A Data · B Materiał / usługa · C Jedn. · D Cena jedn. · E Dostawca · F Ilość · G Wartość (formuła) ·
 *  H Pozycja · I Uwagi (tu znacznik notion:<id>). Zwraca numer wiersza albo null, gdy wpis już jest. */
function doCennika(w, p, strefa, zrodlo) {
  var c = SpreadsheetApp.getActive().getSheetByName(ARKUSZ_CENNIK);
  var n = Math.max(c.getLastRow(), PIERWSZY_WIERSZ) - PIERWSZY_WIERSZ + 1;
  var dane = c.getRange(PIERWSZY_WIERSZ, 1, n, 9).getValues();
  var wolny = PIERWSZY_WIERSZ + n;
  for (var i = dane.length - 1; i >= 0; i--) {
    if (String(dane[i][8]).indexOf(zrodlo) >= 0) return null;
  }
  for (var j = 0; j < dane.length; j++) {
    if (dane[j][0] === '' && dane[j][1] === '') { wolny = PIERWSZY_WIERSZ + j; break; }
  }
  var cena = Math.round(Number(w.kwota) / Number(w.ilosc) * 100) / 100;
  c.getRange(wolny, 1, 1, 6).setValues([[Utilities.parseDate(w.data, strefa, 'yyyy-MM-dd'), w.opis || p.klucz,
    w.jedn || '', cena, w.dostawca || '', Number(w.ilosc)]]);
  c.getRange(wolny, 8, 1, 2).setValues([[p.klucz, 'z wydatku · ' + zrodlo]]);
  return wolny;
}

/** Wycofanie wydatków: czyści pola wpisywane w Wydatkach (A:H, J:M, O) i w Cenniku (A:F, H:I) dla podanych stron
 *  Notion. Wiersz zostaje pusty, formuły zostają; następny dopisz zajmie tę lukę. */
function usun(ids) {
  var lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
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
      c.getRange(PIERWSZY_WIERSZ, 9, nc, 1).getValues().forEach(function (w, i) {
        if (String(w[0]).indexOf(zrodlo) >= 0) {
          var r = PIERWSZY_WIERSZ + i;
          c.getRange(r, 1, 1, 6).clearContent(); c.getRange(r, 8, 1, 2).clearContent();
          wynik.cennik.push(r);
        }
      });
      wyniki.push(wynik);
    });
    SpreadsheetApp.flush();
    return {ok: true, wyniki: wyniki};
  } finally {
    lock.releaseLock();
  }
}

function nastepnyWolny(arkusz, od) {
  var wiersz = od;
  while (arkusz.getRange(wiersz, 1).getValue() !== '' || arkusz.getRange(wiersz, 15).getValue() !== '') wiersz++;
  return wiersz;
}

function sprawdz(w, mapa) {
  if (!w.id) return 'brak id strony';
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(w.data || ''))) return 'brak daty';
  if (!(Number(w.kwota) > 0)) return 'brak kwoty';
  if (STATUSY.indexOf(w.status) < 0) return 'Płatność: ' + STATUSY.join(' / ');
  if (!w.lp) return 'brak pozycji (numer z Kosztorysu, np. 03.5)';
  if (!mapa[w.lp]) return 'pozycja ' + w.lp + ' nie istnieje w Kosztorysie';
  if (w.typ && TYPY.indexOf(w.typ) < 0) return 'nieznany typ ' + w.typ;
  return '';
}

function eksportXlsx() {
  var ss = SpreadsheetApp.getActive();
  DriveApp.getFileById(ss.getId());  // wymusza zakres Dysku – bez niego eksport zwraca 401/403
  var url = 'https://docs.google.com/spreadsheets/d/' + ss.getId() + '/export?format=xlsx';
  var plik = UrlFetchApp.fetch(url, {headers: {Authorization: 'Bearer ' + ScriptApp.getOAuthToken()}});
  return {ok: true, nazwa: ss.getName(), xlsx: Utilities.base64Encode(plik.getBlob().getBytes())};
}
```
