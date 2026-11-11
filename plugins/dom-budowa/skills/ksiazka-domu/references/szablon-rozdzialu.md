# Szablon rozdziału etapu – Książka domu

Podstrona „📘 Książka domu” w Notion, tytuł „<Etap> – rozdział”. Stały układ ośmiu sekcji – brak danych w sekcji
to linia „brak – <czego>”, nie pominięcie sekcji. Przykład niżej na **zmyślonych danych** (Firma A, Jan Kowalski) –
prawdziwe dane są tylko w Notion.

```
Szkic asystenta 2030-05-20 – do przeczytania
Odbiór etapu: 2030-05-18 (odebrane warunkowo – 1 usterka) · Kroki: 01 Wykop … 09 Zasypka · Folder zdjęć etapu: <link>

## 1. Jak zbudowane
- Ławy fundamentowe 60×40 cm, beton C30/37 [projekt]; wykonano zgodnie z projektem, betonowanie 2030-04-10 [wykonano]
- Ściany fundamentowe z bloczków betonowych 30 cm [wykonano]
- Izolacja pionowa: membrana bitumiczna + EPS 12 cm [wykonano – Dziennik 2030-05-02]

## 2. Odstępstwa od projektu
| Co | Projekt | Wykonano | Dlaczego | Kto zatwierdził | Źródło |
|---|---|---|---|---|---|
| Przepust wody | ściana N, oś 2 | ściana N, 0,8 m od osi 2 | kolizja z ławą | konstruktor, wpis KB | Notatnik NT-123 |

## 3. Zdjęcia przed zakryciem
| Krok | Ujęcia | Folder | Braki |
|---|---|---|---|
| 04 Kanalizacja pod posadzką | 12 zdj. z miarą | <link do przed zakryciem/> | – |
| 06 Zbrojenie ław | 8 zdj. | <link> | brak ujęcia uziomu przy narożniku SW |

## 4. Dostawy i produkty
| Produkt | Producent / typ | Partia / klasa | Ilość | Dostawca | Dokumenty |
|---|---|---|---|---|---|
| Beton | wytwórnia Firmy B, C30/37 S3 | WZ z godziną | 18 m³ | Firma B | <link Dostawy/Stan zero/> |
| Izolacja pionowa | membrana bitumiczna, producent X | partia 123 | 12 rolek | Firma C | karta produktu <link> |

## 5. Kto robił i gwarancja
| Zakres | Wykonawca | Odbiór | Gwarancja do | Rękojmia do | Zgłaszanie usterek |
|---|---|---|---|---|---|
| Stan zero (umowa) | Firma A (kontakt → 📇 Kontakty) | 2030-05-18 | 2033-05-18 | 2035-05-18 | pisemnie, wg umowy |

## 6. Protokoły i odbiory
- Odbiór dna wykopu – geotechnik, wpis do dziennika budowy 2030-03-02 <link Dziennik budowy KB/>
- Próba szczelności kanalizacji – protokół <link>
- Protokół odbioru etapu 2030-05-18 – usterka: uzupełnić izolację przy narożniku NE, termin 2030-05-30 (TASKS)

## 7. Koszt etapu
WYDANE brutto: N zł (arkusz kosztorysu, Etapy, stan na 2030-05-20) – szczegóły w arkuszu.

## 8. Uwagi na przyszłość
- Nie kopać przy ścianie północnej głębiej niż 50 cm – przyłącze wody (część B → Działka).
- Rewizja kanalizacji w pomieszczeniu gospodarczym – nie zabudowywać na stałe.
```

Zasady wypełniania:
- Sekcja 1 łączy `[projekt]` i `[wykonano]`; rozjazd → sekcja 2, nie cicha poprawka sekcji 1.
- Sekcja 2 tylko z Notatnika (decyzje) i Rejestru sprzeczności; odstępstwo bez decyzji w Notatniku → zapisz je w Notatniku
  (`notatka`) i zapytaj, kto zatwierdził.
- Sekcja 3 z pól „Zdjęcia” i „Ujęcia przed zakryciem” Dziennika budowy; braki wprost.
- Sekcja 4 z 🧱 Zakupów budowy (Dostarczone) i dokumentów w `Dostawy/<Etap>/`; produkty kupione przez ekipę – z protokołu
  i dokumentów od wykonawcy.
- Sekcja 5 bez telefonów i e-maili (`budowa`, zasada 8).
- Sekcja 7: jedna liczba z arkusza z datą stanu, netto/brutto jawnie.
- Sekcja 8 trafia też do części B (strefy „nie wiercić / nie kopać”).
