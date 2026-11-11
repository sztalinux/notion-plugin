# Gotówka w czasie – ile pieniędzy wyjdzie w którym miesiącu

Odpowiedź na „ile gotówki potrzebuję w grudniu”, „ile mam mieć na koncie do końca stanu zero”, „co do wypłaty z banku”
(`koszty`, sekcja D.4). Widok **miesięczny**. Liczby z arkusza kosztorysu (kopia albo konektor), czas z Harmonogramu w Notion.
Zasady oznaczone [do potwierdzenia] przyjęto nocą 2026-11-11 bez inwestora (POM-5) – zmienia je inwestor.

## Skąd liczby (od najszybszego; błąd → następna droga, bez ponawiania)

1. **Claude Code (Mac):** `python3 tools/wydatki.py gotowka` – tylko odczyt: kopia `Koszty/Kosztorys_google.json` (świeża:
   najpierw `wydatki.py pobierz`) i Harmonogram przez API Notion. Wypisuje tabelę z kwotami **na ekran rozmowy** – nie
   kieruj jej do logu ani do pliku w repo. Harmonogram niedostępny (linia `✗`, wszystko „bez daty”) → odczytaj kroki
   z Notion (baza Harmonogram: Nr etapu, Termin), zapisz je w `<hub>/.dom/wydatki/kroki.json` jako
   `[{"nr": "03", "od": "RRRR-MM-DD", "do": "RRRR-MM-DD"}]` i uruchom znów z `--harmonogram <ten plik>`.
2. **claude.ai / telefon z konektorem Google Sheets:** te same reguły ręcznie (niżej) na żywym arkuszu: Etapy (po nagłówkach),
   Wydatki „Do zapłaty”, Podsumowanie (rezerwa) + Harmonogram z Notion.
3. **Bez konektora:** poproś o eksport arkusza (Plik → Pobierz → Microsoft Excel) i licz ręcznie; bez Notion poproś
   o daty kroków albo pokaż wszystko jako „bez daty”.

## Reguły liczenia (te same w skrypcie i ręcznie)

- **Do zapłaty:** wiersze Wydatków ze Statusem „Do zapłaty” – miesiąc z kolumny Data.
- **Transze ekipy:** Etapy „Do zapłaty ekipie (umowa – wydane ekipa)”; etap bez umowy – plan ekipy − wydane ekipy.
  Odejmij „Do zapłaty” typu Robocizna tego etapu (już policzone wyżej). Miesiąc = **koniec ostatniego kroku** etapu
  w Harmonogramie (Nr etapu = numer etapu w arkuszu) – płatność po odbiorze [do potwierdzenia].
- **Materiał i inne:** (plan − wydane) materiału + (plan − wydane) „Inne” etapu, minus „Do zapłaty” innych typów tego etapu.
  Miesiąc = **start pierwszego kroku** etapu – materiał kupuje się przed robotą [do potwierdzenia]. Dokładniejsze terminy
  zamówień są w 🧱 Zakupach budowy („Zamówić do”) – użyj ich w komentarzu, nie w liczbach.
- **Po terminie:** termin minął, a pieniądze nie wyszły → bieżący miesiąc z dopiskiem „po terminie”, nie miesiąc z przeszłości.
- **Bez daty:** etap bez kroków z Terminem (np. 01, 02, 07, 08, koszty ogólne, przyłącza) → osobny wiersz „bez daty”
  z listą etapów; nie rozkładaj go po miesiącach na domysł.
- **Ujemne** (przekroczenie planu) = 0 – przekroczenia pokazuje sekcja A, nie plan gotówki.
- **Rezerwa:** stawka z Podsumowania („Rezerwa na stan zero”) – kolumna „z rezerwą” = razem × (1 + rezerwa) dla każdego
  miesiąca [do potwierdzenia: rezerwa na całość, nie tylko na plan]. Etap 08 (rezerwa i roboty dodatkowe) to osobna
  pula w planie – stoi w „bez daty”; nie dodawaj jej drugi raz do „z rezerwą”.
- **Gotówka a przelew:** znana tylko z kolumny Sposób wierszy „Do zapłaty” (dopisek „w tym gotówką”). Sposobu płatności
  transz arkusz nie trzyma – sprawdź go w umowie z wykonawcą (`oferta/references/umowa.md`); umowa mówi „gotówką po
  etapach” → transze dolicz do gotówki i napisz to wprost.
- **Nie modelujemy:** obiecanych zwrotów (wiersz „Do zapłaty” z minusem – nie są wpływem), zatrzymania (kaucji) z umowy, terminów płatności faktur dłuższych niż Data, kredytu w transzach
  (D.3), etapów umowy wykonawcy innych niż etapy arkusza – wspomnij o nich, gdy dotyczą miesiąca.

## Format odpowiedzi

```
Gotówka (brutto, wg kopii arkusza z <data>, Harmonogram z <data/Notion>):
| Miesiąc | Do zapłaty | Transze ekipy | Materiał i inne | Razem | z rezerwą |
<wiersze miesięcy> · bez daty: <kwota> (<etapy>)
W <miesiąc pytania>: <kwota> (w tym gotówką N, po terminie M). Uwagi: <terminy szacunkowe – Pewność terminu „Szacunek”>,
<transze wg umowy>, <co nie wliczone>.
```
Kwoty oznaczaj: transze i do zapłaty = **umówione / fakt z arkusza**, materiał i inne = **plan (szacunek)**.

## Zakładka w arkuszu (opcjonalnie, na prośbę inwestora)

Arkusz nie ma dziś zestawienia po miesiącach – działa bez niego (skrypt i reguły wyżej). Proponowany układ zakładki
„Płatności” i formuły: `references/arkusze.md`, sekcja „Proponowane”. Dodaje ją inwestor albo agent na wyraźną prośbę
(sekcja C); do tego czasu nie zapisuj planu płatności nigdzie poza odpowiedzią.
