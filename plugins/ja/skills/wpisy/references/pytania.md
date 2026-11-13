# Format pytań do inwestora w Notion

Inwestor odpowiada z telefonu i zagląda głównie do „📝 Wpisy”. Tabel nie używaj (na telefonie przewijanie w bok i niewygodna
edycja komórek). Trzy formaty:

| Pytanie dotyczy | Gdzie | Format |
|---|---|---|
| konkretnego wpisu (Dziennik, „Wpisy”, podstrona, widget, Skrzynka) | okienko pod wpisem w „📝 Wpisy” (`wpisy`, krok 4) | A |
| czegoś spoza wpisów: RES-n, luki w zadaniach z przeglądu dnia | Dziennik „❓ Czeka na Twoją odpowiedź”, strona RES-n („### ❓ Pytania”), strona pomysłu | B |
| problemu, którego nie wywołał żaden wpis (automat Maca, skrypt, błąd kolejki 💸), niejasnej decyzji SP-n wpisanej w pole Decyzja Rejestru | zwijany nagłówek „🔔 Komunikaty asystenta” w „📝 Wpisy” | C |

**Co w ogóle pytać.** Sprawy techniczne (harness, skrypty, automaty, scalanie, struktura Notion, warianty naprawy ZP)
rozstrzyga asystent sam i tylko odnotowuje wynik – inwestor ufa mu w tym i nie ma czasu na takie pytania. Pytaj o budowę
(termin, materiał, ekipa, pieniądze) i o rzeczy, których asystent fizycznie nie zrobi (kliknięcie na telefonie, odświeżenie
pluginów, decyzja finansowa). Krótko, kilka naraz najwyżej. **Każda sprawa, która czeka na inwestora, ma ślad w „📝 Wpisy”**
(okienko A albo blok 🔔 z C) – osobna strona, baza czy raport z pytaniami nie wystarczy, bo tam inwestor nie zagląda.

## A. Okienko pod wpisem („📝 Wpisy”)

Krótko i w jednym miejscu: inwestor ma od razu zobaczyć, czego brakuje, i dopisać odpowiedź pod spodem.

1. **Jedno okienko na wpis**: blok objaśnienia (callout) z ikoną ❓ i żółtym tłem, zagnieżdżony pod wpisem (wcięty), żeby
   wizualnie należał do wpisu i przenosił się razem z nim. Pod podstroną zagnieździć się nie da – wtedy okienko to blok
   tuż pod nią.
2. **Treść okienka:** pogrubione pytanie, do ok. 15 słów, z propozycją interpretacji w nawiasie. Dwa pytania max – w tej
   samej linii („1) … 2) …”); więcej braków → zapytaj o najważniejsze, resztę po odpowiedzi. Bez daty, nagłówka,
   checkboxów i „Szczegółów”; kontekst tylko, gdy bez niego pytanie jest niezrozumiałe – pół zdania w nawiasie.
3. **Miejsce na odpowiedź:** pod pytaniem, w okienku, jedna linia `✍️`.

Zapis w Notion (przykład zmyślony; wpis inwestora bez zmian, okienko jako dziecko bloku):

```
<p>
oddać rzecz do sklepu do tygodnia

<callout icon="❓" color="yellow_bg">
<b>Które to zadanie – zwrot z ostatniego zamówienia?</b> (propozycja: zadanie prywatne na najbliższy piątek)

✍️
</callout>
</p>
```

Wpis będący punktem listy – okienko wcięte pod punktem tak samo.

Technika: blok wpisu zastąp w całości blokiem z okienkiem jak w przykładzie (`<p>` … `</p>`; punkt listy – ten sam
punkt z wciętym okienkiem). Nie doklejaj okienka z wcięciem do samego tekstu wpisu – Notion wpisze wtedy znaczniki do
treści akapitu jako tekst (`\<callout…>`, `<br />`), a okienka nie będzie. Po zapisie sprawdź odczytem, że `<callout>`
jest dzieckiem wpisu.

### Odczyt odpowiedzi

- Tekst w okienku poza linią pytania i samym `✍️` = odpowiedź (zwykle `✍️ <odpowiedź>`). Blok dopisany pod okienkiem
  wewnątrz tego samego wpisu – też odpowiedź.
- „ok”, „tak” = zgoda na propozycję z nawiasu. „nie” bez dalszego tekstu = propozycja odrzucona → nowe pytanie bez niej.
- Samo `✍️` albo puste okienko = brak odpowiedzi – wpis czeka, nie jest nowym wpisem.
- Strona „Wpisy” edytowana mniej niż 15 minut temu, a odpowiedź pusta albo urwana w pół zdania → weź ją w następnym
  przebiegu (`przeglad-dnia`, A.3).
- Częściowa odpowiedź (dwa pytania, jedna odpowiedź): przetwórz, co się da; w okienku zostaw tylko brakujące pytanie
  i nową linię `✍️`. Odpowiedź wciąż nie wystarcza → dopisz w tym samym okienku nowe pytanie pod odpowiedzią, z linią `✍️`.

## B. Pytania spoza wpisów (checkboxy)

Inwestor ma móc zaznaczyć jedno pole, zamiast pisać.

1. **Nagłówek** jedną linią: `❓ asystent (data) · <temat> – ☑ = tak, inaczej dopisz pod punktem`.
2. **Każde pytanie to osobny to-do** (checkbox), do ok. 12 słów, z propozycją w treści, sformułowany tak, żeby zaznaczenie
   znaczyło „tak, zgadzam się” (np. `- [ ] Wariant B zamiast A`).
   - Wybór z kilku opcji = kilka to-do pod jednym punktem („zaznacz jedno”).
   - Pytanie otwarte (kwota, wymiar, data) = to-do z dopiskiem `→ wpisz pod spodem`.
3. **Max 3 pytania na punkt**; więcej → osobne punkty.
4. **Kontekst, uzasadnienie, opinie, linki i to, co asystent zrobi po odpowiedzi** – w zwiniętym toggle „Szczegóły” pod danym
   pytaniem, nigdy w linii pytania.

```
❓ asystent (12.10) · wybór wariantu – ☑ = tak, inaczej dopisz pod punktem
	- [ ] Wariant B zamiast A
		<toggle>
		Szczegóły

		dlaczego B, co zmieni, co zrobię po odpowiedzi
		</toggle>
	- [ ] Termin do piątku → wpisz pod spodem
```

Odczyt: zaznaczony to-do = zgoda na propozycję; tekst dopisany pod to-do = odpowiedź i **ma pierwszeństwo** przed
zaznaczeniem; niezaznaczony i bez dopisku = brak odpowiedzi; częściowa odpowiedź – przetwórz odpowiedziane punkty (ślad
w „Przetworzone”), reszta zostaje. Zaznaczony checkbox liczy się jako odpowiedź inwestora (`przeglad-dnia`, A.2).

## C. Komunikaty asystenta (🔔 we „📝 Wpisach”)

Problemy asynchroniczne – nikt o nie nie pytał we wpisie, a inwestor powinien o nich wiedzieć: przebieg na Macu się nie udał
albo nie uruchomił, brak logowania MCP Notion, skrypt po przebiegu zwraca błąd, kopie zapasowe po terminie
(`przeglad-tygodnia-osobisty`, klucz `kopie-zapasowe`), wpis kolejki 💸 nie trafił do arkusza
(`koszty`, E), decyzja wpisana w pole Decyzja Rejestru sprzeczności jest niejasna (`wiedza/references/sprzecznosci.md`,
„Bez inwestora”; plugin dom-budowa). Wszystkie w jednym miejscu: zwijany nagłówek „🔔 Komunikaty asystenta” na górze treści „📝 Wpisy”
(nad wpisami). Nagłówek zostaje także pusty – nie usuwaj go; brak → utwórz przy pierwszym komunikacie.

1. **Jeden problem = jeden blok** pod nagłówkiem: akapit `🔔 <dd.mm gg:mm> · <skąd> – <co się stało, jedno zdanie>`
   (od drugiego razu dopisek `(od <dd.mm>, n razy)`), na końcu klucz problemu w kodzie (`` `przebieg-wieczorny` ``; z listy
   automatu – dosłownie, 💸 – wzmianka strony kolejki zamiast klucza). Pod akapitem okienko jak w A: ❓, żółte tło,
   pogrubione „Co możesz zrobić” z propozycją (do ok. 20 słów, np. „Nic – ponowię sam; napisz »log«, a zajrzę do logu”),
   linia `✍️`. 💸: format z `koszty`, E – tylko miejsce się zmienia. SP-n: akapit `🔔 <dd.mm> · SP-n – wpisałeś „<Decyzja>”`
   z wzmianką wiersza Rejestru i kluczem `` `SP-n` ``, w okienku pogrubione pytanie z propozycją opcji („czy to znaczy B?”),
   linia `✍️`; odpowiedź (pkt 4) = domknięcie wg `wiedza`, sekcja C (plugin dom-budowa), blok do „Przetworzone”.
2. **Ten sam problem po raz kolejny** (ten sam klucz albo ta sama strona 💸) → zaktualizuj istniejący blok (data, „od”,
   licznik), nie dodawaj drugiego.
3. **Ustąpiło samo** (automat podał „ustąpiło”, strona 💸 nie jest już „Błąd”) → blok do „Przetworzone” jako
   `~~🔔 <skrót>~~ → ustąpiło <dd.mm>`, bez pytania. Automat podał „bloku nie było” (problem minął, zanim dało się go
   zgłosić – np. brak logowania MCP) → sam ślad w bloku dnia „Przetworzone” w tym formacie, bez bloku 🔔.
4. **Odpowiedź inwestora** (odczyt jak w A) = praca dla najbliższego przebiegu (szybkiego albo wieczornego): wykonaj, co się
   da w przebiegu, i przenieś blok do „Przetworzone” (`~~🔔 <skrót>~~ (❓ … → ✍️ …) → <co zrobiono>`).
5. **Za duże na przebieg** (wymaga Claude Code, zmiany skryptu, decyzji technicznej) → wiersz w bazie „🧯 Znane problemy”
   (`rozwoj-harnessu`, D; ten sam problem już jest → zaktualizuj Ostatnio i treść), w okienku zamiast `✍️` linia
   `→ ZP-n (<status>)`. Blok zostaje, dopóki wiersz nie ma Statusu „Rozwiązany” albo „Zostaje” – wtedy do „Przetworzone”
   (`→ ZP-n rozwiązany` / `zostaje`); statusy ZP sprawdza tylko przebieg wieczorny.
   Wiersz ZP ze Statusem „Czeka na mnie” bez bloku 🔔 (założony albo zmieniony w Claude Code, nocą, ręcznie) → dodaj blok
   `🔔 <dd.mm> · ZP-n – <Problem>` z okienkiem: pogrubione pytanie z „Co zrobić” (z propozycją domyślną) i linia `✍️`;
   odpowiedź przepisz do treści strony ZP („ustalenia z odpowiedzi inwestora”) i ustaw Status „Nowy” – naprawi Claude Code.
6. **Blok bez odpowiedzi nie jest nowym wpisem** – tryb szybki go pomija (`przeglad-dnia`, A.2); zmienia go tylko nowa lista
   od automatu, odpowiedź albo zmiana stanu (pkt 2–5).

Zapis w Notion (przykład zmyślony; nagłówek to zwijany nagłówek h3, komunikat jego dzieckiem):

```
<toggle heading="h3">
🔔 Komunikaty asystenta

<p>
🔔 10.11 21:30 · przegląd wieczorny – przerwany limitem czasu (od 09.11, 2 razy) `przebieg-wieczorny`

<callout icon="❓" color="yellow_bg">
<b>Co możesz zrobić:</b> nic – ponowię jutro (propozycja: napisz „log”, sprawdzę przyczynę)

✍️
</callout>
</p>
</toggle>
```
