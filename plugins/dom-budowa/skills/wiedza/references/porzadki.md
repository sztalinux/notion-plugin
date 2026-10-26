# Porządki w bazie wiedzy – scalanie duplikatów, zły temat, sprzeczności

Kiedy: inwestor zatwierdził arkusz grup z przeglądu bazy (DUPLIKAT, BLISKIE „scalić”, ZŁY TEMAT, SPRZECZNOŚĆ,
DO AKTUALIZACJI, Notatnik dublujący wiedzę) albo mówi „scal WI-x z WI-y”. Scalenie w Notion jest w praktyce
nieodwracalne (relacje, rollupy), dlatego każda zmiana ma ślad do cofnięcia, a każdą grupę sprawdzasz na bieżącym stanie.

## Zasady ogólne

1. **Nigdy nie usuwaj ani nie archiwizuj stron.** Wycofanie = zmiana Statusu z dopiskiem; odnośniki („powtarza WI-y”,
   relacje SP, Notatnik) dalej prowadzą do wiersza, który mówi, dokąd go scalono.
2. **Bieżący stan przed każdą grupą:** pobierz strony grupy z Notion (nie z indeksu ani z arkusza – mogą być stare).
   Stan inny niż w arkuszu tak, że reguła nie pasuje (wiersz już „Nieaktualne”, zmieniona teza, nowy wpis w Rejestrze,
   inna para tematów) → pomiń grupę z powodem. Tezy obu wierszy przeczytaj sam – streszczenie w arkuszu bywa skrótem.
3. **Log poza repo** (katalog porządków obok indeksu, pliki 600): przed zapisem stan PRZED – pełne wartości zmienianych
   pól, **pełne listy relacji** (odczyt relacji z podziałem na strony – odczyt strony obcina długie listy) i zmieniany
   fragment treści; po zapisie stan PO i czas. Relację zapisujesz zawsze całą listą (zapis zastępuje listę), więc listę
   zbuduj z bieżącego odczytu, nie z indeksu. Strona zmieniona przez kogoś między odczytem a zapisem → nie zapisuj.
4. **Kolejność:** sprzeczności → scalenia → ZŁY TEMAT → DO AKTUALIZACJI → Notatnik. Zapisy wsadowe (`budowa`, zasada 6).
5. Daty w dopiskach w formacie RRRR-MM-DD.

## Scalenie (DUPLIKAT, BLISKIE „scalić”)

1. **Łańcuchy:** grupy, które mają wspólny wiersz, połącz – jeden wiersz główny na cały łańcuch; „Scalone do WI-x”
   wskazuje ostateczny wiersz główny, nigdy pośredni.
2. **Wiersz główny – najpełniejszy wiersz, nie najdłuższa teza:** kolejno ocena inwestora (Status „Przejrzane”, Istotność
   po przejrzeniu, Mój komentarz), liczba źródeł, relacja Notatnik, wyższa Istotność, dopiero potem długość tezy (przy remisie
   niższy WI). Wiersz z oceną inwestora zostaje głównym albo grupę pomiń – jego ocena nie może zniknąć w wycofanym. Wybór inny
   niż w arkuszu odnotuj w logu i w raporcie.
3. **Nie wycofuj wiersza „Sporne” ani powiązanego z wpisem Rejestru „Czeka na decyzję” / „Do sprawdzenia u projektanta”** –
   wycofanie rozstrzygnęłoby spór po cichu. Taki wiersz może być głównym. Ta sama para w grupie SPRZECZNOŚĆ i scalenia →
   tylko wpis w Rejestrze, scalenie pomiń.
4. **Wiersz wycofany:** Status „Nieaktualne”; Szczegóły zaczynają się od „Scalone do WI-x (RRRR-MM-DD). ” – reszta bez zmian.
5. **Wiersz główny:**
   - tezy nie przepisuj; brakujące szczegóły z wycofanego (liczby, warunki, wyjątki, produkty) dopisz na końcu Szczegółów
     jako „Z WI-y: …” – warunki z obu tez muszą zostać (np. „po uruchomieniu…”, „przy gruncie spoistym…”);
   - Tematy, Sprzeczności, Notatnik – suma obu list;
   - Źródła – dodaj tylko źródła **niezależne** od już podpiętych (inny autor i inny krąg: kurs, kanał, blog, podcast;
     `SKILL.md`, A.5; `ocena-zrodla.md`). Źródło z tego samego kręgu zostaje tylko przy wycofanym wierszu. Rollup
     Potwierdzenia zmieni się – zapisz w logu jego wartość przed i po;
   - Dotyczy nas i Dla naszej budowy – przenieś, gdy u głównego puste albo „Do oceny”; Istotność – gdy główny ma Status
     „Nowe”, ustaw wyższą z obu;
   - **Mój komentarz** inwestora na głównym nie zmieniaj. Komentarz z wycofanego: u głównego puste → wpisz go tam
     z przedrostkiem „[z WI-y, scalone RRRR-MM-DD] ”; u głównego jest już komentarz → dopisz go do Szczegółów głównego
     z tą samą adnotacją.

## Sprzeczność

Wpis w Rejestrze wg `sprzecznosci.md` (wszystkie pola zgłoszenia, Status „Czeka na decyzję”, relacje Informacje, Źródła,
Tematy); nic nie rozstrzygaj, Statusu wierszy wiedzy nie zmieniaj. Przed zapisem sprawdź Rejestr: jest już wpis z obiema
tezami (w dowolnym Statusie) → pomiń. Ten sam dylemat co otwarty wpis Rejestru → dopnij wiersz do jego relacji Informacje,
nie zakładaj nowego SP. Różne zalecenia dla różnych warunków to nie sprzeczność (`sprzecznosci.md`) → pomiń.

## ZŁY TEMAT, DO AKTUALIZACJI

- ZŁY TEMAT: zmień tylko relację Tematy (usuń temat albo przenieś do proponowanego); wiersz nie może zostać bez tematu.
- DO AKTUALIZACJI: dopisz na końcu Szczegółów „do weryfikacji (RRRR-MM-DD)”, Statusu nie zmieniaj.

## Notatnik i widoki

- Wpis Notatnika dublujący wiedzę albo inny wpis: `notatka/references/scalanie.md`.
- Wycofane wiersze nie mają zaśmiecać widoków: w widokach bazy Informacje bez filtra na Status dodaj „Status ≠ Nieaktualne”
  (istniejących filtrów nie zmieniaj, odczytaj je i połącz przez „i”). Zmienione widoki zapisz w logu (filtr przed i po).
- Po każdej paczce sprawdź, że widoki otwartych spraw na DOM („🔴 Do zamknięcia…”, „Krytyczne i otwarte”) mają te same wpisy.

## Po porządkach

`python3 tools/wiedza.py sync --pelny --publikuj`, potem `python3 tools/wiedza_jakosc.py zloty`. Alarm przy wierszach
zbioru kontrolnego, które stały się „Nieaktualne”, jest spodziewany – wtedy `zloty --odnowa` i odnotuj to w raporcie.
