# Wydatki → Arkusz Google (synchronizacja bez ręcznego wgrywania)

Wydatek albo wycena dostawcy wpisane w Dzienniku (albo prosto w Notion) same trafiają do arkusza Google z kosztorysem. Bez AI po stronie
arkusza, bez ręcznego eksportu i importu.

## 1. Jak to działa

```
📓 Dziennik („wydałem 5 200 zł na beton na chudziak, 16 m³, przelew”)
   │  przebieg szybki na Macu (co godzinę, claude -p + MCP Notion) – procedura koszty, sekcja B
   ▼
💸 Wydatki → arkusz  (baza Notion na DOM, Arkusz = „Do arkusza”)   ← tu możesz też dopisać wiersz ręcznie z telefonu
   │  tools/wydatki.py sync – po każdym przebiegu (automaty/przeglad.py), czysty Python, token NOTION_TOKEN
   ▼
Apps Script w arkuszu (aplikacja internetowa, sekret)  → wydatek: arkusz Wydatki · wycena: arkusz Cennik
   │
   ▼
Notion: Arkusz = „W arkuszu” + numer wiersza   albo   „Błąd” + powód (popraw pole, ustaw znów „Do arkusza”)
```

- Opóźnienie: do godziny (przebieg szybki 8:05–22:05 i 22:30) plus kilka sekund.
- Mac wyłączony albo uśpiony → wpisy czekają w Notion i pójdą przy następnym przebiegu. Nic nie ginie.
- Ten sam wpis wysłany dwa razy nie zdubluje się: arkusz rozpoznaje go po kolumnie Źródło (`notion:<id strony>`).
- Lista Pozycja w Notion = pozycje z arkusza Kosztorys; odświeża ją `wydatki.py pozycje` (przebieg wieczorny).
- **Wycena** (Rodzaj = Wycena; „beton C12/15 371 zł/m³ brutto w firmie X”) idzie do arkusza Cennik jako jedna oferta:
  cena za jednostkę, netto albo brutto (brutto liczy arkusz), dostawca, pozycja, status Oferta. Decyzja = Status wyceny
  „Wybrana” (pozostałe „Odrzucona”) i ponowne wysłanie – arkusz aktualizuje ten sam wiersz, a Kosztorys pokazuje cenę
  wybraną (kol. N–P). Wydatki do Cennika nie trafiają – cenę zapłaconą liczy kolumna Cena jedn. w Wydatkach.
- Wyceny wymagają kodu Apps Script w wersji 2 i Cennika w nowym układzie; inaczej `sync` je wstrzymuje (linia „wyceny
  czekają” w logu).
- **Arkusza nie wgrywa się ponownie.** Zmiany układu i wyglądu (kolumny, formuły, kolory, listy) robi asystent na żywym
  arkuszu – sekcja 8.
- Kopia wartości arkusza do analiz: `<hub>/Koszty/Kosztorys_google.json` (wszystkie zakładki, bez formuł), odświeżana przez
  `wydatki.py pobierz` (przebieg wieczorny).

## 2. Kto ma dostęp do Notion (żeby się nie gubić)

| Gdzie | Jak łączy się z Notion | Co robi |
|---|---|---|
| Claude Code na Macu (ta aplikacja i `claude -p` w automatach) | lokalny serwer MCP `notion` (logowanie OAuth przez `/mcp`) | czyta i zapisuje – przebiegi Dziennika, rozmowy |
| Skrypty Pythona na Macu (`wiedza.py`, `migawka.py`, `wydatki.py`) | token integracji `NOTION_TOKEN` z `.dom/sekrety.env` (prawo odczytu i zmiany treści) | indeks wiedzy i migawka – tylko odczyt; `wydatki.py` – odczyt kolejki, zmiana pól Arkusz/Błąd/Wiersz i listy Pozycja w bazie 💸 Wydatki |
| GitHub Actions (prywatne repo kopii, `tryb-gleboki.yml`) | **żadnego** – ma tylko token Claude | odpowiada na pytania z telefonu z kopii indeksu wiedzy |
| claude.ai (czat, telefon) | konektor Notion zablokowany przez organizację | zapisy idą do „📥 Skrzynki”, Mac przenosi je do Notion |

Arkusz Google nie ma konektora AI. Dopisuje do niego wyłącznie skrypt Apps Script na Twoim koncie Google, wołany
przez `wydatki.py`. Claude nie czyta arkusza bezpośrednio – do analiz służy kopia JSON (sekcja 1). Skrypt ma dostęp tylko
do tego jednego arkusza (`@OnlyCurrentDoc`) – nie widzi Dysku ani innych plików.

## 3. Konfiguracja – krok po kroku (raz)

Krok 0 – porządek z Excelem. Zamknij stary plik `Kosztorys_17.10.2026_stan_zero_v2.xlsx` (Excel trzyma go otwartego).
Jeśli dopisałeś w nim wydatki po 2.09.2026, przepisz je do `Kosztorys_stan_zero_2026-11-07.xlsx` przed importem.

1. **Konto Google: prywatne**, nie służbowe. Na koncie firmowym administrator może blokować aplikacje Apps Script
   z dostępem „Każdy”, a dane budowy to sprawa prywatna.
2. **Import arkusza.** Dysk Google → Nowy → Prześlij plik → `Koszty/Kosztorys_stan_zero_2026-11-07.xlsx`. Otwórz go,
   Plik → Zapisz jako Arkusze Google. Nazwij np. „Kosztorys budowy”. Wgrany `.xlsx` usuń z Dysku, żeby nie mylić wersji.
   Sprawdź: Plik → Ustawienia → Język i region = Polska, strefa czasowa = (GMT+01:00) Warsaw; w Wydatkach działają listy
   Etap / Pozycja / Typ.
3. **Kod.** W arkuszu: Rozszerzenia → Apps Script. Skasuj zawartość `Kod.gs`, wklej kod z sekcji 9, zapisz (ikona dyskietki).
   Do schowka skopiujesz go w Terminalu: `python3 tools/wydatki.py kod | pbcopy` (w katalogu repo harnessu).
4. **Sekret.** W Apps Script: Ustawienia projektu (koło zębate) → Właściwości skryptu → Dodaj właściwość:
   nazwa `SEKRET`, wartość – długi losowy ciąg. Wygeneruj go w Terminalu:
   `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
5. **Wdrożenie.** Wdróż → Nowe wdrożenie → typ „Aplikacja internetowa”. Wykonaj jako: **Ja**. Kto ma dostęp: **Każdy**.
   Wdróż → Autoryzuj dostęp → wybierz konto → „Zaawansowane” → „Przejdź do … (niebezpieczne)” (to Twój własny,
   niezweryfikowany przez Google skrypt) → Zezwól. Skopiuj „URL aplikacji internetowej” (kończy się na `/exec`).
   „Każdy” oznacza: kto zna adres, może wysłać żądanie – bez sekretu dostaje „zły sekret”. Adresu i sekretu nie
   wklejaj nigdzie poza `sekrety.env`. Z sekretem skrypt umie: dopisać i wycofać wydatek albo wycenę, oddać kopię
   arkusza (wartości) i zmienić układ zakładek (wartości, formuły, kolory, listy) – bez usuwania zakładek, bez formuł
   IMPORT…/IMAGE/HYPERLINK, czyścić wolno tylko pusty Cennik i archiwum szacunku AI. Dostęp: wyłącznie ten arkusz. Wyciek adresu i sekretu → nowy
   sekret (krok 4 i 6).
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
   `python3 tools/wydatki.py pobierz` – ma zapisać `Koszty/Kosztorys_google.json`.
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
- **Wyceny we wpisach:** „X ma beton C25/30 W8 po 420 zł brutto”, „biorę stal z Y” – asystent założy albo zaktualizuje
  wycenę. Ręcznie: wiersz w arkuszu Cennik (status z listy).
- **Jedna droga na wydatek:** albo Dziennik / 💸 Wydatki, albo ręcznie w arkuszu – nie oba, bo wyjdzie podwójnie.
- **Błąd** (pole Błąd mówi co): popraw pole, ustaw Arkusz = „Do arkusza” – pójdzie przy następnym przebiegu.
- **Korekta po wysłaniu:** popraw wiersz bezpośrednio w arkuszu. Notion jest tylko kolejką; źródłem prawdy dla liczb
  jest arkusz.
- **Pomyłka (wydatek nie powinien był pójść):** `python3 tools/wydatki.py wycofaj <id strony>` – czyści wiersz w Wydatkach
  albo wycenę w Cenniku, w Notion ustawia „Nie wysyłać”. Id strony to końcówka jej adresu w Notion.
- **Nowa pozycja kosztorysu:** dodaj ją w arkuszu Kosztorys (instrukcja w arkuszu), lista w Notion odświeży się wieczorem
  (albo od razu: `python3 tools/wydatki.py pozycje`).

## 5. Polecenia

| Polecenie | Co robi | Kto woła |
|---|---|---|
| `wydatki.py sync` | kolejka „Do arkusza” → arkusz, wynik do Notion | `automaty/przeglad.py` po każdym przebiegu |
| `wydatki.py sync --proba` | pokazuje, co poszłoby do arkusza; nic nie zapisuje | ręcznie |
| `wydatki.py pozycje` | pozycje z arkusza → lista Pozycja w Notion | przebieg wieczorny |
| `wydatki.py pobierz` | wartości arkusza → `Koszty/Kosztorys_google.json` | przebieg wieczorny, ręcznie przed analizą |
| `wydatki.py wycofaj <id>…` | czyści wydatek (Wydatki) albo wycenę (Cennik), w Notion „Nie wysyłać” | ręcznie, asystent na prośbę |
| `wydatki.py sprawdz` | sekrety, dostęp do bazy i arkusza | ręcznie |
| `wydatki.py kod` | wypisuje kod Apps Script (z `| pbcopy` – do schowka) | ręcznie przy aktualizacji kodu |
| `wydatki.py migruj <zmiany.json>` | zmiana układu na arkuszu (cofanie: Plik → Historia wersji) | asystent w Claude Code |

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
| data w arkuszu o dzień przesunięta | arkusz ma inną strefę niż Polska – Plik → Ustawienia → Strefa czasowa (GMT+01:00) Warsaw |
| „nieznana akcja” przy `wycofaj` albo „arkusz ma kod w wersji 1 – wyceny czekają” | w Apps Script jest starszy kod – sekcja 7 |
| „Cennik w starym układzie – najpierw zmiana układu” | kod v2 jest, ale zmiana układu jeszcze nie przeszła – sekcja 8 |
| zmieniłeś kod w Apps Script | Wdróż → Zarządzaj wdrożeniami → ołówek → Wersja: Nowa → Wdróż (adres zostaje ten sam) |

## 7. Aktualizacja kodu Apps Script (rzadko – gdy asystent poprosi)

1. Terminal, katalog repo harnessu: `python3 tools/wydatki.py kod | pbcopy` – cały kod trafia do schowka.
2. W arkuszu: Rozszerzenia → Apps Script → plik `Kod.gs` → Cmd+A (zaznacz wszystko) → Cmd+V (wklej, zastępuje stary kod)
   → zapisz.
3. Wdróż → Zarządzaj wdrożeniami → ołówek przy wdrożeniu → Wersja: **Nowa wersja** → Wdróż. Adres `/exec` zostaje ten sam,
   `sekrety.env` się nie zmienia. Gdy kod potrzebuje innych uprawnień, w edytorze wybierz funkcję `doGet` → Uruchom →
   zezwól (dostęp tylko do tego arkusza).
4. `python3 tools/wydatki.py sprawdz` pokazuje wersję kodu.

## 8. Zmiany układu arkusza bez ponownego importu (asystent w Claude Code)

1. Docelowy układ zbuduj lokalnie jako `.xlsx` (openpyxl) i porównaj z kopią żywego arkusza (`wydatki.py pobierz`, JSON):
   te same wiersze danych, kolumny z danymi inwestora poza zmienianymi zakresami.
2. Plik zmian: `python3 ~/Documents/Dom/AI/automaty/arkusz_zmiany.py --cel cel.xlsx --wyjscie zmiany.json --zakres …`
   (narzędzie lokalne poza repo – wymaga openpyxl; opis opcji: `--help`). Zapisz go w `.dom/wydatki/` z datą.
3. Przetestuj docelowy `.xlsx` lokalnie (LibreOffice: zero #NAME?/#REF!, sumy jak przed zmianą, podgląd zakładek) i plik
   zmian na makiecie, jeśli zmienia kod albo nowe rodzaje operacji.
4. `python3 tools/wydatki.py migruj zmiany.json`, potem `pobierz` i kontrola: zero błędów formuł w JSON, sumy Podsumowania
   jak przed zmianą. Coś nie tak → inwestor cofa w arkuszu: Plik → Historia wersji → wersja sprzed zmiany.

## 9. Kod Apps Script (`Kod.gs`)

```javascript
/** @OnlyCurrentDoc */
/**
 * Kosztorys w Arkuszach Google – punkt wejścia dla tools/wydatki.py (Mac). Instrukcja: docs/wydatki-arkusz.md
 * w repozytorium harnessu. Kod nie zawiera danych – działa na arkuszu, do którego jest przypięty.
 * Akcje (POST, JSON {"sekret", "akcja", ...}):
 *   ping · pozycje · dane · dopisz (wiersze[]) · usun (ids[]) · zmien (operacje[]) – zmiany układu bez ponownego importu.
 * @OnlyCurrentDoc: skrypt ma dostęp wyłącznie do tego arkusza (bez Dysku, bez innych plików). Cofanie zmian – Plik →
 * Historia wersji.
 * dopisz: rodzaj „Wycena” → arkusz Cennik (ponowne wysłanie aktualizuje ten sam wiersz), reszta → arkusz Wydatki.
 * Kolumn z formułami (Wydatki I i N, Cennik G i K, Kosztorys N–P) dopisz/usun nigdy nie nadpisują.
 * zmien: tylko znane zakładki, bez usuwania zakładek, bez formuł IMPORT…/IMAGE/HYPERLINK; czyścić wolno tylko pusty Cennik
 * i archiwum szacunku AI.
 */

var WERSJA = 3;
var ARKUSZ_WYDATKI = 'Wydatki';
var ARKUSZ_KOSZTORYS = 'Kosztorys';
var ARKUSZ_CENNIK = 'Cennik';
var PIERWSZY_WIERSZ = 5;
var STATUSY = ['Zrealizowane', 'Do zapłaty'];
var TYPY = ['Materiał', 'Robocizna', 'Sprzęt', 'Usługa', 'Formalności'];
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
  if (!(Number(w.kwota) > 0)) return 'brak kwoty';
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
 *  zamroz, siatka, ramka. Dane wpisane przez inwestora zmienia tylko „zakres” – generator wysyła tam wyłącznie
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
      default:
        throw new Error('operacja ' + nr + ': nieznana ' + o.op);
    }
    wykonane++;
  });
  SpreadsheetApp.flush();
  return {ok: true, wykonane: wykonane};
}
```
