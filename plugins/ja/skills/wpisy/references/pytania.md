# Format pytań do inwestora w Notion

Inwestor odpowiada z telefonu i zagląda głównie do „📝 Wpisy”. Tabel nie używaj (na telefonie przewijanie w bok i niewygodna
edycja komórek). Dwa formaty:

| Pytanie dotyczy | Gdzie | Format |
|---|---|---|
| konkretnego wpisu (Dziennik, „Wpisy”, podstrona, widget, Skrzynka) | okienko pod wpisem w „📝 Wpisy” (`wpisy`, krok 4) | A |
| czegoś spoza wpisów: RES-n, luki w zadaniach z przeglądu dnia | Dziennik „❓ Czeka na Twoją odpowiedź”, strona RES-n („### ❓ Pytania”), strona pomysłu | B |

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
		<details><summary>Szczegóły</summary> dlaczego B, co zmieni, co zrobię po odpowiedzi </details>
	- [ ] Termin do piątku → wpisz pod spodem
```

Odczyt: zaznaczony to-do = zgoda na propozycję; tekst dopisany pod to-do = odpowiedź i **ma pierwszeństwo** przed
zaznaczeniem; niezaznaczony i bez dopisku = brak odpowiedzi; częściowa odpowiedź – przetwórz odpowiedziane punkty (ślad
w „Przetworzone”), reszta zostaje. Zaznaczony checkbox liczy się jako odpowiedź inwestora (`przeglad-dnia`, A.2).
