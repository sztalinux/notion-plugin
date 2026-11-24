---
name: wpisy
description: Przetwarzanie luźnych wpisów ze strony „📝 Wpisy” (pod „📓 Dziennikiem”) i z „📥 Skrzynki” – obszar wg bazy „🧭 Obszary Dziennika”, pytanie pod niejasnym wpisem, przekazanie do procedury, ślad w „Przetworzone”. Używaj, gdy użytkownik mówi „przerób dziennik”, „co mam w dzienniku”, „odpowiedziałem w dzienniku”, „przerób skrzynkę”, albo wkleja kilka luźnych notatek naraz („wrzuć gdzie trzeba”).
---

# Dziennik → właściwe miejsca

Cel: inwestor wpisuje wszystko w jedno miejsce, bez zastanawiania się, gdzie to należy. Asystent rozpoznaje obszar według
bazy w Notion i przekazuje wpis do właściwej procedury – **dopiero gdy wpis jest jednoznaczny**. Niejasne wracają do inwestora
z pytaniem w okienku pod wpisem w „📝 Wpisy” – tam inwestor zagląda najczęściej. Podział na obszary żyje w Notion, więc nowy rodzaj wpisu nie wymaga zmiany harnessu.

Miejsce: strona **📓 Dziennik** (`3f8f5982-09e7-80c8-a154-c59aeb844e8f`). Strefy (na wierzchu zawsze tylko to, czego asystent
jeszcze nie widział):

```
📓 Dziennik
	<toggle> Jak używać </toggle>  ← w nim zdanie „Piszesz we 📝 Wpisach…” (bloki 1. poziomu Dziennika nie są źródłem wpisów od ja 1.19.0)
	📝 Wpisy (podstrona) ← inwestor pisze tu wprost w treści albo zakłada wpisy jako osobne strony; bloki i podstrony = nowe wpisy
		▸ ### 🔔 Komunikaty asystenta (zwijany nagłówek)  ← na górze; problemy bez wpisu (automaty, 💸) – references/pytania.md, C; nie są wpisami
		wpis niejasny                                     ← czeka tu, aż inwestor odpowie
			❓ {okienko} **Co miałeś na myśli – X czy Y?** (propozycja: …)
				✍️ odpowiedź inwestora
	▸ ### ❓ Czeka na Twoją odpowiedź (zwijany nagłówek)  ← tylko zdanie „Pytania są teraz we 📝 Wpisach (🔔)” (znacznik przejścia 1.2); zostaje
	▸ ### Przetworzone (zwijany nagłówek)
		▸ 📅 13.10 wt · 🤖 przetworzono 3 · czeka na Ciebie 1 · jutro 2   ← zwijany blok dnia, najnowszy na górze
			🤖 13.10 noc: dziennik – przetworzono 3 (emocje 1, zadania 2), … (pełna linia)
			- ~~wpis~~ → Wpisy emocji: <link>
	▸ ### 🧭 Dla asystenta (zwijany nagłówek)  ← baza Obszary; nie ruszaj
	🗃 Przetworzone podstrony, 🗃 Przetworzone – archiwum, 🧠 Rozkminki, 📆 Przeglądy dzienne / 📅 tygodniowe (podstrony) ← nie są wpisami
Private (najwyższy poziom)
	📌 DASHBOARD, 🛖 DOM, 📓 Dziennik, … 🔒 Prywatne   ← stałe strony (lista w ja/references/notion-mapa.md; chroni 🔒 Prywatne)
```

**Źródła wpisów (jedyne):** (1) każdy blok w treści strony „📝 Wpisy” (`3faf5982-09e7-80b2-9b33-c48745d67a4f`) i **każda jej
podstrona** (tytuł + treść = wpis), (2) pozycje sekcji „Nowe” dokumentu „📥 Skrzynka” (`references/skrzynka.md`), (3) odpowiedzi
inwestora w okienkach ❓ i pod blokami 🔔. Wyjątki (nie wpisy): „Jak używać”, puste linie, nagłówek „🔔 Komunikaty asystenta”
z blokami pod nim (komunikat staje się pracą dopiero po odpowiedzi – `references/pytania.md`, C) i stałe podstrony „📆 Przeglądy dzienne”,
„📅 Przeglądy tygodniowe”, „🗃 Przetworzone podstrony”, „🗃 Przetworzone – archiwum”, „🧠 Rozkminki”.
**Nie są już źródłem** (od ja 1.19.0): bloki 1. poziomu strony „📓 Dziennik” i strony na najwyższym poziomie Private spoza listy
stałych stron (widget „nowa strona”). Nie przetwarzaj ich; wyjątek – **przejście 1.1** (tylko nocny przebieg, dopóki w „Jak używać” Dziennika brak zdania „Piszesz we 📝 Wpisach”; `przeglad-dnia/references/przejscia.md`): przenieś jeszcze te stare źródła do „📝 Wpisów” jako zwykłe wpisy (blok → na koniec treści Wpisów; strona z widgetu
→ jej treść jako blok we Wpisach, strona pod „🗃 Przetworzone podstrony”), od następnego przebiegu ich nie czytaj.
Porównuj po ID, nie po tytule. 🔒 Prywatne – nigdy jej nie otwieraj (`ja`, zasada 5). Ogólny zakaz: nie przetwarzaj stron spoza Wpisów.
**Podstron „Wpisów” nie usuwaj i nie wycinaj znacznikiem strony z treści** (to by ją skasowało)
– po przetworzeniu przenieś ją narzędziem przenoszenia stron pod „🗃 Przetworzone podstrony” (`3faf5982-09e7-8115-908f-f764d3133d6f`), a w śladzie dnia
daj do niej wzmiankę. Jeden blok może zawierać kilka spraw – rozłóż je osobno. Nie zmieniaj treści
wpisów inwestora – tylko dopisuj pod nimi i przenoś między strefami.

## Procedura

1. **Pobierz** stronę „📝 Wpisy” (bloki w treści i podstrony) i sekcję „Nowe” Skrzynki (`references/skrzynka.md`). Stronę Dziennik
   pobierz tylko do zapisu „Przetworzone” (krok 6–7). Przy przejściu 1.1 (patrz „Źródła wpisów”) pobierz też bloki 1. poziomu
   Dziennika i listę stron najwyższego poziomu Private.
   Nowe wpisy oraz wpisy z okienkiem ❓ we „Wpisach”, w którym inwestor coś dopisał – te oceń ponownie; odczyt odpowiedzi:
   `references/pytania.md`, A. Komunikaty 🔔 z odpowiedzią albo zmianą stanu – obsłuż wg `references/pytania.md`, C. Wpis z okienkiem bez odpowiedzi nie jest nowy – pomiń go. Brak obu → „Wpisy puste”
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
     Podstrona bez daty w treści → data jej ostatniej edycji (z odczytu strony), z dopiskiem w śladzie.
     Przy emocji bez daty – data przetwarzania z dopiskiem „(data przetworzenia)”.
4. **Niejednoznaczny albo bez obszaru → nie przetwarzaj, zapytaj pod wpisem w „📝 Wpisy”** – okienko ❓ w formacie
   `references/pytania.md`, A (jedno krótkie pytanie z propozycją i linia `✍️` na odpowiedź). Gdzie trafia okienko:
   - blok z treści „Wpisów” – zostaje na miejscu, okienko zagnieżdżone pod nim;
   - podstrona „Wpisów” – okienko jako blok tuż pod nią;
   - pozycja Skrzynki – we „Wpisach” akapit ze wzmianką (Skrzynka: treść dosłownie) i okienkiem pod nim; pozycja zostaje
     w „Nowe” i nie jest nowym wpisem, dopóki inwestor nie odpowie w okienku.
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
     `~~wpis~~ → 🧠 rozkminka wieczorem` (z obszarem: „budowa” albo nazwa obszaru) – robi ją przegląd dnia (`przeglad-dnia`, B.2a);
     polecenie z akapitem „Rozkminki w ciągu dnia” → ślad `→ 🧠 rozkminka w toku <token>` i linia `ROZKMINKI:` (`przeglad-dnia/references/rozkminka.md`).
     W tym śladzie zostaw pełną treść prośby, bez skrótu z kroku 6 – wieczór czyta ją stąd.
6. **Zamknij wpis:** przenieś go do „Przetworzone” (z okienkiem: pytanie i odpowiedź w jednej linii `(❓ … → ✍️ …)`), do **zwijanego bloku dzisiejszego dnia** (`<toggle>` – zapis jak w `przeglad-dnia/references/uklad-wpisu.md`, A; nigdy `<details>`,
   tytuł „📅 <dd.mm> <dzień> · <skrót linii 🤖>”; brak – utwórz na górze), jako `~~wpis~~ → <gdzie>: <link>`;
   **wpis rozłożony na więcej niż dwa miejsca** – punkt z przekreślonym skrótem wpisu (do ok. 80 znaków) i pod nim po
   jednym podpunkcie na miejsce, z ikoną i liczbą: `📓 Dziennik budowy: <link>` · `💸 Wydatki (3): <link>, …` ·
   `✅ TASKS (2): <link>, …` · `🧱 Zakupy: ZAM-6, ZAM-8 – …` · `📅 Harmonogram: HR-1 Zrobione, …` (bez jednej długiej linii)
   (blok z treści „Wpisów”: `~~wpis~~ (Wpisy) → <gdzie>: <link>`;
   podstrona: `~~tytuł~~ (podstrona → <wzmianka>) → <gdzie>: <link>`, po
   przeniesieniu jej pod „🗃 Przetworzone podstrony”). Zdublowane / nieprzydatne / testowe / pusta podstrona (bez
   tytułu i treści) → `~~wpis~~ → pominięte: <jedno zdanie>`. Nie usuwaj.
7. **Zapisy wsadowo** (`ja`, zasada 2): odczyty, potem jedno wywołanie na bazę docelową, na końcu **jedna** edycja strony
   Dziennik (przeniesienia do „Przetworzone”, linia „🤖”) – podstrony „Wpisów” przenosisz jednym osobnym wywołaniem przed nią.
   Bloki z treści „📝 Wpisy” idą w tej edycji Dziennika do „Przetworzone”; **jedna** edycja
   „Wpisów” (punktowa, podstron nie ruszaj) zdejmuje przetworzone bloki z ich okienkami, dodaje okienka pod niejasnymi
   (przy przejściu 1.1 także dopisuje tu stare wpisy z Dziennika i widgetu) – po niej treść „Wpisów” to tylko nagłówek 🔔 z komunikatami, wpisy z okienkami ❓, podstrony i 1 pusta linia
   (zmiany w 🔔 idą w tej samej edycji).
   Po edycji Dziennika (po przejściu) na 1. poziomie zostaje tylko to, co stałe – „Jak używać” (ze zdaniem „Piszesz we 📝 Wpisach”), trzema nagłówkami („❓” z samym zdaniem-znacznikiem), sześcioma stałymi podstronami („📝 Wpisy” i lista wyżej) i 1–2 pustymi
   liniami do pisania. Każda zamiana (`old_str`) obejmuje tylko blok, który przenosisz, albo jedną linię-kotwicę – nigdy
   całej sekcji. Po edycji odczyt kontrolny: trzy nagłówki z treścią sprzed edycji i sześć podstron są na
   miejscu; brak czegoś → przywróć z odczytu sprzed edycji i odnotuj w linii „🤖”. Linia „🤖” idzie na górę bloku dnia:
   ```
   🤖 15.10 noc: dziennik – przetworzono 5 (budowa 2, emocje 1, zadania 2), czeka na Ciebie 1 · jutro: 3
   ```
   Kolejny przebieg tego dnia (np. ręczny) – druga linia „🤖 … (ręczne)” w tym samym bloku. W rozmowie z inwestorem
   przy > 3 wpisach pokaż plan (tabela: wpis | obszar | gdzie trafi | pytanie?) i poproś o „ok”, chyba że powiedział
   „bez pytania”; w przeglądzie dnia – bez pytań.
8. **Podsumuj** w blokach z `ja` („Domknięcie rozmowy”): 🛑 wpisy do wyjaśnienia (wpis: pytanie – czeka we „Wpisach”) · ✅ przetworzone (wpis → gdzie) ·
   ⏳ pominięte i dlaczego.
   Bloki dni starsze niż 14 dni przegląd tygodnia przenosi do „🗃 Przetworzone – archiwum” (`przeglad-tygodnia-osobisty`, D).

## Bez inwestora

W ciągu dnia Dziennik przerabia zaplanowany **szybki przebieg** (co godzinę, launchd na Macu), a wieczorem **przegląd dnia** – oba w skillu
`przeglad-dnia` (tryby A i B), bez pytań w rozmowie, z wyjątkami opisanymi tam. Kilka przebiegów dziennie dopisuje się
do jednego bloku dnia w „Przetworzone”. Czwarte źródło wpisów: **Skrzynka** – dokument Claude „📥 Skrzynka” z zapisami
z czatu bez Notion (`references/skrzynka.md`): te same kroki 3–7, ślad w Skrzynce i w linii „🤖”.

## Zasady

- Nigdy nie zgaduj znaczenia skrótowego wpisu i nie zapisuj go „na wszelki wypadek” – lepiej jedno pytanie niż zagadka
  w bazie. Wyjątek: w docelowej bazie jest już wpis, który go wyjaśnia – wtedy dopisz uzupełnienie tam.
- Źródło (kto powiedział, skąd) przepisuj dosłownie, gdy procedura docelowa ma na nie pole.
- **Research (RES-n):** odpowiedź „RES-n: …” (w bloku 🔔 z kluczem `RES-n` we „Wpisach” albo pod pytaniami na stronie researchu; w bloku obsługuje je nocny przebieg) → dopisz ją pod pytaniami
  na stronie RES-n z datą i ustaw Status „Do zrobienia” (wieczór dokończy); „RES-n niepotrzebny” albo zakup już Kupione →
  Status „Zamknięty”.
- **Sprzeczności (SP-n):** odpowiedź „SP-n: …” (we „Wpisach”, w bloku 🔔 albo w okienku ❓) → `wiedza`, sekcja C (plugin
  dom-budowa) – także w przeglądzie dnia bez inwestora; jasna (także własny wariant albo część dylematu) = domknięcie ze
  skutkami, niejasna („?”, „nie wiem”, otwarte „A albo B”) = okienko ❓ pod wpisem (granica: `wiedza/references/sprzecznosci.md`).
- **Sprzątanie pytań:** pytanie (okienko pod wpisem, RES-n, SP-n, blok 🔔), które inwestor rozstrzygnął w rozmowie,
  zamknij w tej samej pracy: dopisz wynik tam, gdzie żyje sprawa (strona RES-n z nowym Statusem itd.), a wpis z okienkiem
  albo blok 🔔 przenieś do bloku dnia w „Przetworzone” jako `~~…~~ → rozwiązane w rozmowie (data): <wzmianka>`. Nie usuwaj.
- **Pozycja w starej sekcji „❓ Czeka na Twoją odpowiedź” w Dzienniku** (jednorazowe przejście, tylko nocny przebieg) → przenieś
  do „🔔 Komunikaty asystenta” jako blok 🔔 (checkboxy i dopiski zachowaj, klucz `KS-…`/`RES-n` w kodzie); sekcję zostaw z jednym
  zdaniem „Pytania są teraz we 📝 Wpisach (🔔)”.
- **Pytanie czy komunikat:** pytanie o to, co inwestor sam wpisał → okienko pod wpisem (A); problem, którego nie wywołał
  żaden wpis (automat, skrypt, błąd kolejki) → blok pod „🔔 Komunikaty asystenta” (C). Pytania z tła, także RES-n i luki w zadaniach, to też 🔔
  (C.7, z checkboxami).
- **Komunikat 💸** (błąd kolejki wydatków, zakłada go przebieg pod 🔔): odpowiedź i zamknięcie – `koszty`, sekcja E (plugin
  dom-budowa); bez odpowiedzi sprawdź stan strony – nie jest już „Błąd” → zamknij jako naprawione.
- Zdjęcia we wpisie: paragon albo rachunek (obraz z dopiskiem, kto płacił i czym) → `budzet/references/paragony.md`
  (obraz paragonu bez „kto i czym” → okienko ❓, nic się nie zapisuje); budowa → `dziennik` (plugin dom-budowa); inne –
  zostaw w treści docelowej strony.
- Dziennik to skrzynka wejściowa, nie archiwum: wpis żyje w docelowym miejscu, „Przetworzone” to ślad na kilka dni.
- Inwestor woli pisać niż wypełniać pola – nie proponuj zamiany Dziennika na bazę.
