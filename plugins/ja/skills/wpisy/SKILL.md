---
name: wpisy
description: Przetwarzanie luźnych wpisów inwestora ze strony „📓 Dziennik” w Notion i ze stron zakładanych widgetem w telefonie na najwyższym poziomie Private (myśli, emocje, zadania, sprawy budowy, dziecko, suplementy, książki – wpisane w biegu, z telefonu) – rozpoznanie obszaru według bazy „🧭 Obszary Dziennika”, wyjaśnienie niejasnych, przekazanie do właściwej procedury, ślad w „Przetworzone”. Używaj, gdy użytkownik mówi „przerób dziennik”, „ogarnij dziennik”, „co mam w dzienniku”, „odpowiedziałem w dzienniku”, „przerób inbox”, gdy przegląd dnia lub tygodnia pokazuje wpisy do przetworzenia, albo gdy wkleja kilka luźnych notatek naraz i prosi „wrzuć gdzie trzeba”.
---

# Dziennik → właściwe miejsca

Cel: inwestor wpisuje wszystko w jedno miejsce, bez zastanawiania się, gdzie to należy. Asystent rozpoznaje obszar według
bazy w Notion i przekazuje wpis do właściwej procedury – **dopiero gdy wpis jest jednoznaczny**. Niejasne wracają do inwestora
z pytaniem. Podział na obszary żyje w Notion, więc nowy rodzaj wpisu nie wymaga zmiany harnessu.

Miejsce: strona **📓 Dziennik** (`3f8f5982-09e7-80c8-a154-c59aeb844e8f`). Strefy (na wierzchu zawsze tylko to, czego asystent
jeszcze nie widział):

```
📓 Dziennik
	<details> Jak używać </details>
	- nowy wpis inwestora (albo podstrona)              ← NOWE: pierwszy poziom; po przebiegu pusto
	### ❓ Czeka na Twoją odpowiedź {toggle}
		- wpis niejasny
			- ❓ asystent (12.10): pytanie – propozycja interpretacji
			- odpowiedź inwestora (pod pytaniem)
	### Przetworzone {toggle}
		▸ 📅 13.10 wt · 🤖 przetworzono 3 · czeka na Ciebie 1 · jutro 2   ← zwijany blok dnia, najnowszy na górze
			🤖 13.10 wieczór: dziennik – przetworzono 3 (emocje 1, zadania 2), … (pełna linia)
			- ~~wpis~~ → Wpisy emocji: <link>
	### 🧭 Dla asystenta {toggle}  ← baza Obszary; nie ruszaj
	📝 Wpisy (podstrona) ← inwestor pisze tu wprost w treści albo zakłada wpisy jako osobne strony; bloki i podstrony = nowe wpisy
	🗃 Przetworzone podstrony, 📆 Przeglądy dzienne (podstrony) ← nie są wpisami
Private (najwyższy poziom)
	📌 DASHBOARD, 🛖 DOM, 📓 Dziennik, … 🔒 Prywatne   ← stałe strony (lista w ja/references/notion-mapa.md)
	nowa strona z widgetu w telefonie                 ← NOWY wpis; po przetworzeniu przeniesiona pod 🗃
```

**Nowy wpis** = każdy blok pierwszego poziomu (akapit, punkt), **każdy blok w treści strony „📝 Wpisy”**
(`3faf5982-09e7-80b2-9b33-c48745d67a4f`; inwestor często pisze tam wprost, bez zakładania podstrony), **każda jej
podstrona** (tytuł + treść = wpis), podstrona Dziennika założona poza „Wpisami”, z wyjątkiem
„Jak używać”, pustych linii, trzech zwijanych nagłówków i stałych podstron „📝 Wpisy”, „📆 Przeglądy dzienne”
i „🗃 Przetworzone podstrony”, **oraz każda strona na najwyższym poziomie Private spoza listy stałych stron**
(lista z ID: `ja/references/notion-mapa.md`, „Struktura najwyższego poziomu”) – tam widget „nowa strona” w telefonie
zakłada strony. Porównuj po ID, nie po tytule. 🔒 Prywatne jest na liście – nigdy jej nie otwieraj (`ja`, zasada 5).
Nieznana strona na najwyższym poziomie, która ma podstrony lub bazę albo wygląda na nowy obszar (tytuł jak nazwa działu,
bez treści wpisu), **nie jest wpisem**: nie przetwarzaj jej i nie przenoś – w „❓” punkt ze wzmianką strony: „Nowa strona
na najwyższym poziomie – wpis czy nowa stała strona? Jeśli stała, dopiszę ją do listy”.
**Podstrony (także strony z widgetu w Private) nie usuwaj i nie wycinaj znacznikiem strony z treści** (to by ją skasowało)
– po przetworzeniu przenieś ją narzędziem przenoszenia stron pod „🗃 Przetworzone podstrony” (`3faf5982-09e7-8115-908f-f764d3133d6f`), a w śladzie dnia
daj do niej wzmiankę. Jeden blok może zawierać kilka spraw – rozłóż je osobno. Nie zmieniaj treści
wpisów inwestora – tylko dopisuj pod nimi i przenoś między strefami.

## Procedura

1. **Pobierz** stronę Dziennik, stronę „📝 Wpisy” (bloki w treści i podstrony) i listę stron najwyższego poziomu Private (odczyt
   listy stron prywatnych; strony spoza listy stałych otwórz, żeby mieć treść i czas ostatniej edycji – tylko je). Brak
   narzędzia do listy stron prywatnych → pomiń to źródło i dopisz w linii „🤖”: „strony z widgetu – brak odczytu”.
   Nowe wpisy oraz wpisy z „❓”, pod których ostatnim pytaniem inwestor coś dopisał, zaznaczył checkbox (albo
   poprawił wpis) – te oceń ponownie; odczyt odpowiedzi: `references/pytania.md`. Wpisy w „❓” bez odpowiedzi pomiń. Brak obu → „Dziennik pusty” (+ liczba czekających w „❓”).
2. **Pobierz Obszary** – zapisany widok „🤖 Aktywne (dla asystenta)” (`view://3faf5982-09e7-817b-a060-000c05f26c6a`, tryb view:
   Aktywny = tak, sort Kolejność; baza `collection://253b7564-00ac-45b2-a3f4-956275e3a7e0`).
3. **Dla każdego wpisu ustal** (razem z dialogiem pod nim):
   - **Obszar** – porównaj treść z „Rozpoznawanie” i „Przykład”. Jeden wpis może dotyczyć kilku obszarów (emocja + zadanie,
     budowa + emocja) – rozłóż na części. Przy remisie wygrywa niższa „Kolejność”.
   - **Czy jest jednoznaczny** – da się go zapisać jako samodzielne zdanie: co, kogo/czego dotyczy, kiedy. Pojedyncze słowa,
     skróty, zaimki bez kontekstu, „asdf” – **niejednoznaczne**.
   - **Data zdarzenia** – wzmianka daty we wpisie (`@today`) albo data tekstem; słowa względne licz od niej. Notion nie zapisuje,
     kiedy dopisano pojedynczy punkt, więc data przetwarzania to nie data wpisu. Podstrona lub strona z widgetu bez daty
     w treści → data jej ostatniej edycji (z odczytu strony), z dopiskiem w śladzie. Słowo względne bez daty przy terminie lub
     zdarzeniu z budowy → zapytaj („czy »wczoraj« to 11.10?”); przy emocji bez daty – data przetwarzania z dopiskiem
     „(data przetworzenia)”.
4. **Niejednoznaczny albo bez obszaru → nie przetwarzaj.** Przenieś do „❓” i dopisz pod nim pytania w formacie z
   `references/pytania.md` (osobny checkbox na pytanie z propozycją – „Zadanie prywatne na ten tydzień”, kontekst w „Szczegółach”). Podstrona lub strona z widgetu zostaje na miejscu –
   w „❓” idzie punkt z jej wzmianką i pytaniem; strona wymieniona w „❓” nie jest nowym wpisem, dopóki inwestor nie odpowie
   pod pytaniem albo nie zmieni strony po dacie pytania. Wpis z odpowiedzią – połącz i oceń ponownie.
   Odpowiedź opisuje rodzaj wpisu, którego nie ma w Obszarach → przetwórz go i **zaproponuj nowy wiersz Obszarów**
   („Dodać obszar »…« z rozpoznawaniem »…«, zapis do …?”); po zgodzie dodaj go (bez zmiany harnessu). Gdy nowy obszar wymaga
   własnej logiki, której nie da się opisać w polu „Jak zapisać” – zaproponuj pomysł (`rozwoj-harnessu`, C).
5. **Jednoznaczny → wykonaj obszar:**
   - Procedura = nazwa skilla (`budowa`, `emocje`, `zadania`, `dziecko`, `suple`, `rozwoj-harnessu`) → wczytaj ten skill
     i wykonaj jego kroki dla wpisu (łącznie z duplikatami i polami). Dla `budowa` – sekcja „Luźny wpis z Dziennika”.
     Pola „Gdzie” i „Jak zapisać” z wiersza to **ustawienia inwestora nadrzędne wobec skilla** (np. inna sekcja, dodatkowe
     pole, inny format) – stosuj je, jeśli są czymś więcej niż odesłaniem do skilla.
   - Procedura = `ogólna` → zapisz według „Gdzie” i „Jak zapisać” z wiersza; najpierw szukaj duplikatu (2–3 słowa).
6. **Zamknij wpis:** przenieś go (z dialogiem) do „Przetworzone”, do **zwijanego bloku dzisiejszego dnia** (`<details>`,
   tytuł „📅 <dd.mm> <dzień> · <skrót linii 🤖>”; brak – utwórz na górze), jako `~~wpis~~ → <gdzie>: <link>`
   (blok z treści „Wpisów”: `~~wpis~~ (Wpisy) → <gdzie>: <link>`;
   podstrona: `~~tytuł~~ (podstrona → <wzmianka>) → <gdzie>: <link>`, strona z widgetu: `(widget → <wzmianka>)`, po
   przeniesieniu jej pod „🗃 Przetworzone podstrony”). Zdublowane / nieprzydatne / testowe / pusta strona z widgetu (bez
   tytułu i treści) → `~~wpis~~ → pominięte: <jedno zdanie>`. Nie usuwaj.
7. **Zapisy wsadowo** (`ja`, zasada 2): odczyty, potem jedno wywołanie na bazę docelową, na końcu **jedna** edycja strony
   Dziennik (przeniesienia do „❓”, do „Przetworzone”, linia „🤖”) – podstrony i strony z widgetu przenosisz
   jednym osobnym wywołaniem przed nią; po nim na najwyższym poziomie Private zostają tylko stałe strony (i te czekające w „❓”).
   Bloki z treści „📝 Wpisy” idą w tej edycji Dziennika do „Przetworzone” albo „❓”, a z „Wpisów” zdejmij je osobną edycją
   tej strony (podstron nie ruszaj) – po niej treść „Wpisów” to tylko podstrony i 1 pusta linia.
   Po niej **pierwszy poziom jest pusty** – poza „Jak używać”, trzema nagłówkami, dwiema stałymi podstronami i 1–2 pustymi
   liniami do pisania. Linia „🤖” idzie na górę bloku dnia:
   ```
   🤖 15.10 wieczór: dziennik – przetworzono 5 (budowa 2, emocje 1, zadania 2), czeka na Ciebie 1 · pomysły – 1 · jutro: 3
   ```
   Kolejny przebieg tego dnia (np. ręczny) – druga linia „🤖 … (ręczne)” w tym samym bloku. W rozmowie z inwestorem
   przy > 3 wpisach pokaż plan (tabela: wpis | obszar | gdzie trafi | pytanie?) i poproś o „ok”, chyba że powiedział
   „bez pytania”; w przeglądzie dnia – bez pytań.
8. **Podsumuj** w blokach z `ja` („Domknięcie rozmowy”): 🛑 wpisy do wyjaśnienia (wpis: pytanie) · ✅ przetworzone (wpis → gdzie) ·
   ⏳ pominięte i dlaczego.
   „Przetworzone” czyści przegląd tygodnia (bloki dni starsze niż 14 dni, po zgodzie).

## Bez inwestora

W ciągu dnia Dziennik przerabia zaplanowany **szybki przebieg** (co 1–2 h), a wieczorem **przegląd dnia** – oba w skillu
`przeglad-dnia` (tryby A i B), bez pytań w rozmowie, z wyjątkami opisanymi tam. Kilka przebiegów dziennie dopisuje się
do jednego bloku dnia w „Przetworzone”.

## Zasady

- Nigdy nie zgaduj znaczenia skrótowego wpisu i nie zapisuj go „na wszelki wypadek” – lepiej jedno pytanie niż zagadka
  w bazie. Wyjątek: w docelowej bazie jest już wpis, który go wyjaśnia – wtedy dopisz uzupełnienie tam.
- Źródło (kto powiedział, skąd) przepisuj dosłownie, gdy procedura docelowa ma na nie pole.
- **Research (RES-n):** odpowiedź „RES-n: …” (w Dzienniku albo pod pytaniami na stronie researchu) → dopisz ją pod pytaniami
  na stronie RES-n z datą i ustaw Status „Do zrobienia” (wieczór dokończy); „RES-n niepotrzebny” albo zakup już Kupione →
  Status „Zamknięty”.
- **Sprzątanie „❓”:** pytanie (RES-n, SP-n, zadanie, wpis), które inwestor rozstrzygnął w rozmowie, zamknij w tej samej pracy:
  dopisz wynik i odpowiedzi tam, gdzie żyje sprawa (strona RES-n z nowym Statusem itd.), a jego linię przenieś z „❓” do bloku
  dnia w „Przetworzone” jako `~~RES-n: …~~ → rozwiązane w rozmowie (data): <wzmianka>`. Nie usuwaj.
- Zdjęcia we wpisie: budowa → `dziennik` (plugin dom-budowa); inne – zostaw w treści docelowej strony.
- Dziennik to skrzynka wejściowa, nie archiwum: wpis żyje w docelowym miejscu, „Przetworzone” to ślad na kilka dni.
- Inwestor woli pisać niż wypełniać pola – nie proponuj zamiany Dziennika na bazę.
