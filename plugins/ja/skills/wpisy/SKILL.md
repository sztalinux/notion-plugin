---
name: wpisy
description: Przetwarzanie luźnych wpisów inwestora ze strony „📓 Dziennik” w Notion i ze stron zakładanych widgetem w telefonie na najwyższym poziomie Private (myśli, emocje, zadania, sprawy budowy, dziecko, suplementy, książki – wpisane w biegu, z telefonu) – rozpoznanie obszaru według bazy „🧭 Obszary Dziennika”, wyjaśnienie niejasnych, przekazanie do właściwej procedury, ślad w „Przetworzone”. Używaj, gdy użytkownik mówi „przerób dziennik”, „ogarnij dziennik”, „co mam w dzienniku”, „odpowiedziałem w dzienniku”, „przerób inbox”, gdy przegląd dnia lub tygodnia pokazuje wpisy do przetworzenia, albo gdy wkleja kilka luźnych notatek naraz i prosi „wrzuć gdzie trzeba”.
---

# Dziennik → właściwe miejsca

Cel: inwestor wpisuje wszystko w jedno miejsce, bez zastanawiania się, gdzie to należy. Asystent rozpoznaje obszar według
bazy w Notion i przekazuje wpis do właściwej procedury – **dopiero gdy wpis jest jednoznaczny**. Niejasne wracają do inwestora
z pytaniem w okienku pod wpisem w „📝 Wpisy” – tam inwestor zagląda najczęściej. Podział na obszary żyje w Notion, więc nowy rodzaj wpisu nie wymaga zmiany harnessu.

Miejsce: strona **📓 Dziennik** (`3f8f5982-09e7-80c8-a154-c59aeb844e8f`). Strefy (na wierzchu zawsze tylko to, czego asystent
jeszcze nie widział):

```
📓 Dziennik
	▸ Jak używać (zwijany blok)
	- nowy wpis inwestora (albo podstrona)              ← NOWE: pierwszy poziom; po przebiegu pusto
	▸ ### ❓ Czeka na Twoją odpowiedź (zwijany nagłówek)  ← tylko pytania spoza wpisów (RES-n, luki w zadaniach); wpisów tu nie trzymaj
	▸ ### Przetworzone (zwijany nagłówek)
		▸ 📅 13.10 wt · 🤖 przetworzono 3 · czeka na Ciebie 1 · jutro 2   ← zwijany blok dnia, najnowszy na górze
			🤖 13.10 wieczór: dziennik – przetworzono 3 (emocje 1, zadania 2), … (pełna linia)
			- ~~wpis~~ → Wpisy emocji: <link>
	▸ ### 🧭 Dla asystenta (zwijany nagłówek)  ← baza Obszary; nie ruszaj
	📝 Wpisy (podstrona) ← inwestor pisze tu wprost w treści albo zakłada wpisy jako osobne strony; bloki i podstrony = nowe wpisy
		▸ ### 🔔 Komunikaty asystenta (zwijany nagłówek)  ← na górze; problemy bez wpisu (automaty, 💸) – references/pytania.md, C; nie są wpisami
		wpis niejasny                                     ← czeka tu, aż inwestor odpowie
			❓ {okienko} **Co miałeś na myśli – X czy Y?** (propozycja: …)
				✍️ odpowiedź inwestora
	🗃 Przetworzone podstrony, 🗃 Przetworzone – archiwum, 📆 Przeglądy dzienne / 📅 tygodniowe (podstrony) ← nie są wpisami
Private (najwyższy poziom)
	📌 DASHBOARD, 🛖 DOM, 📓 Dziennik, … 🔒 Prywatne   ← stałe strony (lista w ja/references/notion-mapa.md)
	nowa strona z widgetu w telefonie                 ← NOWY wpis; po przetworzeniu przeniesiona pod 🗃
```

**Nowy wpis** = każdy blok pierwszego poziomu (akapit, punkt), **każdy blok w treści strony „📝 Wpisy”**
(`3faf5982-09e7-80b2-9b33-c48745d67a4f`; inwestor często pisze tam wprost, bez zakładania podstrony), **każda jej
podstrona** (tytuł + treść = wpis), podstrona Dziennika założona poza „Wpisami”, z wyjątkiem
„Jak używać”, pustych linii, trzech zwijanych nagłówków Dziennika, nagłówka „🔔 Komunikaty asystenta” we „Wpisach” z blokami pod nim
(komunikat staje się pracą dopiero po odpowiedzi – `references/pytania.md`, C) i stałych podstron „📝 Wpisy”, „📆 Przeglądy dzienne”,
„📅 Przeglądy tygodniowe”, „🗃 Przetworzone podstrony” i „🗃 Przetworzone – archiwum”, **oraz każda strona na najwyższym poziomie Private spoza listy stałych stron**
(lista z ID: `ja/references/notion-mapa.md`, „Struktura najwyższego poziomu”) – tam widget „nowa strona” w telefonie
zakłada strony. Porównuj po ID, nie po tytule. 🔒 Prywatne jest na liście – nigdy jej nie otwieraj (`ja`, zasada 5).
Nieznana strona na najwyższym poziomie, która ma podstrony lub bazę albo wygląda na nowy obszar (tytuł jak nazwa działu,
bez treści wpisu), **nie jest wpisem**: nie przetwarzaj jej i nie przenoś – we „Wpisach” akapit z jej wzmianką i okienkiem
„Wpis czy nowa stała strona? (jeśli stała, dopiszę ją do listy)” (krok 4).
**Podstrony (także strony z widgetu w Private) nie usuwaj i nie wycinaj znacznikiem strony z treści** (to by ją skasowało)
– po przetworzeniu przenieś ją narzędziem przenoszenia stron pod „🗃 Przetworzone podstrony” (`3faf5982-09e7-8115-908f-f764d3133d6f`), a w śladzie dnia
daj do niej wzmiankę. Jeden blok może zawierać kilka spraw – rozłóż je osobno. Nie zmieniaj treści
wpisów inwestora – tylko dopisuj pod nimi i przenoś między strefami.

## Procedura

1. **Pobierz** stronę Dziennik, stronę „📝 Wpisy” (bloki w treści i podstrony) i listę stron najwyższego poziomu Private (odczyt
   listy stron prywatnych; strony spoza listy stałych otwórz, żeby mieć treść i czas ostatniej edycji – tylko je). Brak
   narzędzia do listy stron prywatnych → pomiń to źródło i dopisz w linii „🤖”: „strony z widgetu – brak odczytu”.
   Nowe wpisy oraz wpisy z okienkiem ❓ we „Wpisach”, w którym inwestor coś dopisał – te oceń ponownie; odczyt odpowiedzi:
   `references/pytania.md`, A. Komunikaty 🔔 z odpowiedzią albo zmianą stanu – obsłuż wg `references/pytania.md`, C. Wpis z okienkiem bez odpowiedzi nie jest nowy – pomiń go. Brak obu → „Dziennik pusty”
   (+ liczba czekających we „Wpisach”).
2. **Pobierz Obszary** – zapisany widok „🤖 Aktywne (dla asystenta)” (`view://3faf5982-09e7-817b-a060-000c05f26c6a`, tryb view:
   Aktywny = tak, sort Kolejność; baza `collection://253b7564-00ac-45b2-a3f4-956275e3a7e0`).
3. **Dla każdego wpisu ustal** (razem z dialogiem pod nim):
   - **Obszar** – porównaj treść z „Rozpoznawanie” i „Przykład”. Jeden wpis może dotyczyć kilku obszarów (emocja + zadanie,
     budowa + emocja) – rozłóż na części. Przy remisie wygrywa niższa „Kolejność”.
   - **Czy jest jednoznaczny** – da się go zapisać jako samodzielne zdanie: co, kogo/czego dotyczy, kiedy. Pojedyncze słowa,
     skróty, zaimki bez kontekstu, „asdf” – **niejednoznaczne**.
   - **Data zdarzenia** – wzmianka daty we wpisie (`@today`) albo data tekstem; słowa względne licz od niej. Bez daty we wpisie
     słowa względne („dziś”, „jutro”, „w piątek”, „za tydzień”) licz **od daty przetwarzania** – przebiegi idą co godzinę, więc wpis
     jest z tego samego dnia; **nie pytaj** o to i nie odkładaj wpisu z pytaniem z tego powodu. Zapisz termin, a w śladzie dopisz
     „(termin od daty przetworzenia)”. Wyjątek: pierwszy przebieg dnia (do 9:00) po wpisach, które mogły powstać poprzedniego
     wieczoru – gdy blok dnia w Dzienniku albo data ostatniej edycji strony wskazuje wczoraj, licz od wczoraj i dopisz to w śladzie.
     Podstrona lub strona z widgetu bez daty w treści → data jej ostatniej edycji (z odczytu strony), z dopiskiem w śladzie.
     Przy emocji bez daty – data przetwarzania z dopiskiem „(data przetworzenia)”.
4. **Niejednoznaczny albo bez obszaru → nie przetwarzaj, zapytaj pod wpisem w „📝 Wpisy”** – okienko ❓ w formacie
   `references/pytania.md`, A (jedno krótkie pytanie z propozycją i linia `✍️` na odpowiedź). Gdzie trafia okienko:
   - blok z treści „Wpisów” – zostaje na miejscu, okienko zagnieżdżone pod nim;
   - blok z pierwszego poziomu Dziennika – przenieś go na koniec treści „Wpisów” (przed pustą linią), z okienkiem pod nim;
   - podstrona „Wpisów” – okienko jako blok tuż pod nią;
   - strona z widgetu, pozycja Skrzynki – we „Wpisach” akapit ze wzmianką strony (Skrzynka: treść dosłownie) i okienkiem
     pod nim; strona zostaje na miejscu i nie jest nowym wpisem, dopóki inwestor nie odpowie w okienku albo nie zmieni
     strony po dacie pytania.
   Wpis z odpowiedzią – połącz z nią i oceń ponownie. **Wpis jasny tylko w części** (np. zadanie zapisane, kwota albo
   miejsce niejasne) → zapisz jasną część, jej ślad daj do „Przetworzone” z dopiskiem „(reszta – pytanie we Wpisach)”,
   a wpis zostaw we „Wpisach” z okienkiem o brakującą część; zamknij go (krok 6) dopiero po odpowiedzi.
   Odpowiedź opisuje rodzaj wpisu, którego nie ma w Obszarach → przetwórz go i **zaproponuj nowy wiersz Obszarów**
   w okienku pod tym wpisem („Dodać obszar »…« z rozpoznawaniem »…«, zapis do …?”; jak wpis jasny w części – wyżej); po zgodzie dodaj go (bez zmiany harnessu). Gdy nowy obszar wymaga
   własnej logiki, której nie da się opisać w polu „Jak zapisać” – zaproponuj pomysł (`rozwoj-harnessu`, C).
5. **Jednoznaczny → wykonaj obszar:**
   - Procedura = nazwa skilla (`budowa`, `emocje`, `zadania`, `dziecko`, `suple`, `rozwoj-harnessu`) → wczytaj ten skill
     i wykonaj jego kroki dla wpisu (łącznie z duplikatami i polami). Dla `budowa` – sekcja „Luźny wpis z Dziennika”.
     Pola „Gdzie” i „Jak zapisać” z wiersza to **ustawienia inwestora nadrzędne wobec skilla** (np. inna sekcja, dodatkowe
     pole, inny format) – stosuj je, jeśli są czymś więcej niż odesłaniem do skilla.
   - Procedura = `ogólna` → zapisz według „Gdzie” i „Jak zapisać” z wiersza; najpierw szukaj duplikatu (2–3 słowa).
   - **Prośba o rozkminkę** – wpis wprost prosi o pracę myślową dla inwestora („przygotuj mi…”, „napisz mi…”, „jakie pytania
     zadać…”, „przemyśl / rozkmiń…”, „porównaj…”), nie o zapis. W rozmowie – wykonaj od razu właściwą procedurę. W przebiegu
     bez inwestora nie wykonuj jej: jasne części wpisu (zadanie, termin) zapisz normalnie, a ślad daj jako
     `~~wpis~~ → 🧠 rozkminka wieczorem` (z obszarem: „budowa” albo nazwa obszaru) – robi ją przegląd dnia (`przeglad-dnia`, B.2a).
     W tym śladzie zostaw pełną treść prośby, bez skrótu z kroku 6 – wieczór czyta ją stąd.
6. **Zamknij wpis:** przenieś go do „Przetworzone” (z okienkiem: pytanie i odpowiedź w jednej linii `(❓ … → ✍️ …)`), do **zwijanego bloku dzisiejszego dnia** (`<toggle>` – zapis jak w `przeglad-dnia/references/uklad-wpisu.md`, A; nigdy `<details>`,
   tytuł „📅 <dd.mm> <dzień> · <skrót linii 🤖>”; brak – utwórz na górze), jako `~~wpis~~ → <gdzie>: <link>`;
   **wpis rozłożony na więcej niż dwa miejsca** – punkt z przekreślonym skrótem wpisu (do ok. 80 znaków) i pod nim po
   jednym podpunkcie na miejsce, z ikoną i liczbą: `📓 Dziennik budowy: <link>` · `💸 Wydatki (3): <link>, …` ·
   `✅ TASKS (2): <link>, …` · `🧱 Zakupy: ZAM-6, ZAM-8 – …` · `📅 Harmonogram: HR-1 Zrobione, …` (bez jednej długiej linii)
   (blok z treści „Wpisów”: `~~wpis~~ (Wpisy) → <gdzie>: <link>`;
   podstrona: `~~tytuł~~ (podstrona → <wzmianka>) → <gdzie>: <link>`, strona z widgetu: `(widget → <wzmianka>)`, po
   przeniesieniu jej pod „🗃 Przetworzone podstrony”). Zdublowane / nieprzydatne / testowe / pusta strona z widgetu (bez
   tytułu i treści) → `~~wpis~~ → pominięte: <jedno zdanie>`. Nie usuwaj.
7. **Zapisy wsadowo** (`ja`, zasada 2): odczyty, potem jedno wywołanie na bazę docelową, na końcu **jedna** edycja strony
   Dziennik (przeniesienia do „Przetworzone”, zdjęcie bloków przeniesionych do „Wpisów”, linia „🤖”) – podstrony i strony
   z widgetu przenosisz jednym osobnym wywołaniem przed nią; po nim na najwyższym poziomie Private zostają tylko stałe strony
   (i te z okienkiem we „Wpisach”). Bloki z treści „📝 Wpisy” idą w tej edycji Dziennika do „Przetworzone”; **jedna** edycja
   „Wpisów” (punktowa, podstron nie ruszaj) zdejmuje przetworzone bloki z ich okienkami, dodaje okienka pod niejasnymi
   i przenosi tu niejasne z Dziennika – po niej treść „Wpisów” to tylko nagłówek 🔔 z komunikatami, wpisy z okienkami ❓, podstrony i 1 pusta linia
   (zmiany w 🔔 idą w tej samej edycji).
   Po edycji Dziennika **pierwszy poziom jest pusty** – poza „Jak używać”, trzema nagłówkami, pięcioma stałymi podstronami (lista wyżej) i 1–2 pustymi
   liniami do pisania. Linia „🤖” idzie na górę bloku dnia:
   ```
   🤖 15.10 wieczór: dziennik – przetworzono 5 (budowa 2, emocje 1, zadania 2), czeka na Ciebie 1 · pomysły – 1 · jutro: 3
   ```
   Kolejny przebieg tego dnia (np. ręczny) – druga linia „🤖 … (ręczne)” w tym samym bloku. W rozmowie z inwestorem
   przy > 3 wpisach pokaż plan (tabela: wpis | obszar | gdzie trafi | pytanie?) i poproś o „ok”, chyba że powiedział
   „bez pytania”; w przeglądzie dnia – bez pytań.
8. **Podsumuj** w blokach z `ja` („Domknięcie rozmowy”): 🛑 wpisy do wyjaśnienia (wpis: pytanie – czeka we „Wpisach”) · ✅ przetworzone (wpis → gdzie) ·
   ⏳ pominięte i dlaczego.
   Bloki dni starsze niż 14 dni przegląd tygodnia przenosi do „🗃 Przetworzone – archiwum” (`przeglad-tygodnia-osobisty`, D).

## Bez inwestora

W ciągu dnia Dziennik przerabia zaplanowany **szybki przebieg** (co 1–2 h), a wieczorem **przegląd dnia** – oba w skillu
`przeglad-dnia` (tryby A i B), bez pytań w rozmowie, z wyjątkami opisanymi tam. Kilka przebiegów dziennie dopisuje się
do jednego bloku dnia w „Przetworzone”. Czwarte źródło wpisów: **Skrzynka** – dokument Claude „📥 Skrzynka” z zapisami
z czatu bez Notion (`references/skrzynka.md`): te same kroki 3–7, ślad w Skrzynce i w linii „🤖”.

## Zasady

- Nigdy nie zgaduj znaczenia skrótowego wpisu i nie zapisuj go „na wszelki wypadek” – lepiej jedno pytanie niż zagadka
  w bazie. Wyjątek: w docelowej bazie jest już wpis, który go wyjaśnia – wtedy dopisz uzupełnienie tam.
- Źródło (kto powiedział, skąd) przepisuj dosłownie, gdy procedura docelowa ma na nie pole.
- **Research (RES-n):** odpowiedź „RES-n: …” (w Dzienniku albo pod pytaniami na stronie researchu) → dopisz ją pod pytaniami
  na stronie RES-n z datą i ustaw Status „Do zrobienia” (wieczór dokończy); „RES-n niepotrzebny” albo zakup już Kupione →
  Status „Zamknięty”.
- **Sprzeczności (SP-n):** odpowiedź „SP-n: …” (w Dzienniku, we „Wpisach” albo w okienku ❓) → `wiedza`, sekcja C (plugin
  dom-budowa) – także w przeglądzie dnia bez inwestora; jasna = domknięcie ze skutkami, niejasna = okienko ❓ pod wpisem.
- **Sprzątanie pytań:** pytanie (okienko pod wpisem, RES-n, SP-n, zadanie w „❓”), które inwestor rozstrzygnął w rozmowie,
  zamknij w tej samej pracy: dopisz wynik tam, gdzie żyje sprawa (strona RES-n z nowym Statusem itd.), a wpis z okienkiem
  albo linię „❓” przenieś do bloku dnia w „Przetworzone” jako `~~…~~ → rozwiązane w rozmowie (data): <wzmianka>`. Nie usuwaj.
- **Wpis w „❓” Dziennika** (stary format albo pomyłka) → przy najbliższej edycji przenieś go do „Wpisów” z jednym okienkiem
  (scal pytania, dopisane odpowiedzi uwzględnij) – pytania o wpisy mają być tam, gdzie inwestor pisze.
- **Pytanie czy komunikat:** pytanie o to, co inwestor sam wpisał → okienko pod wpisem (A); problem, którego nie wywołał
  żaden wpis (automat, skrypt, błąd kolejki) → blok pod „🔔 Komunikaty asystenta” (C). Pytania spoza wpisów (RES-n, luki
  w zadaniach) zostają w „❓” Dziennika (B).
- **Komunikat 💸** (błąd kolejki wydatków, zakłada go przebieg pod 🔔): odpowiedź i zamknięcie – `koszty`, sekcja E (plugin
  dom-budowa); bez odpowiedzi sprawdź stan strony – nie jest już „Błąd” → zamknij jako naprawione.
- Zdjęcia we wpisie: budowa → `dziennik` (plugin dom-budowa); inne – zostaw w treści docelowej strony.
- Dziennik to skrzynka wejściowa, nie archiwum: wpis żyje w docelowym miejscu, „Przetworzone” to ślad na kilka dni.
- Inwestor woli pisać niż wypełniać pola – nie proponuj zamiany Dziennika na bazę.
