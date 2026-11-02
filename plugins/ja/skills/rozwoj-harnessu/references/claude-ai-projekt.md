# claude.ai – pluginy, projekt „Dom”, przegląd dnia

**Co gdzie (od 2.0.0 / ja 1.0.0):**

| Na claude.ai | Rola |
|---|---|
| Pluginy `dom-budowa` i `ja` z marketplace `sztalinux/notion-plugin` | działają w **każdej** rozmowie – skille wczytują się z opisu (`description`), bez projektu i bez „/” |
| Projekt „Dom” | tylko **kontener dokumentów budowy** (wiedza projektu) – rozmowy, które potrzebują projektu architektonicznego, opinii, umów |
| Zaplanowane zadanie „Dziennik – szybki przebieg” | **poza projektem**, co 1–2 h w ciągu dnia (np. 8–22); polecenie: „Dziennik – szybki przebieg (skill przeglad-dnia z pluginu ja, tryb szybki)”; pusty Dziennik = koniec bez zapisów |
| Zaplanowane zadanie „Przegląd dnia” | **poza projektem** (pliki projektu nie doklejają się do każdego przebiegu), raz wieczorem; polecenie: „Przegląd dnia (skill przeglad-dnia z pluginu ja, tryb wieczorny)” – podsumowanie dnia i plan na jutro |
| Zaplanowane zadanie „Przegląd tygodnia” | **poza projektem**, raz w tygodniu (np. niedziela wieczór); polecenie: „Przegląd tygodnia (skill przeglad-tygodnia-osobisty z pluginu ja)” – robi też przegląd budowy na DOM; dawne tygodniowe zadanie w projekcie „Dom” usuń |
| Preferencje konta (opcjonalnie) | jedna linia: „Gdy rozmowa dotyczy mojego dnia, zadań, emocji, dziecka, suplementów albo budowy, wczytaj skill `ja`” – pas bezpieczeństwa, gdy opis skilla nie zadziała |

Sprawy budowy poza projektem też działają (skille i Notion są wszędzie) – brakuje tylko plików z wiedzy projektu; procedura
poprosi wtedy o konkretny dokument (`dokumenty`, „Prośba o dokument”).

Projekt „Dom” na claude.ai (czat, telefon) ma dwie części:

| Część | Co tam jest | Skąd |
|---|---|---|
| **Instructions** (instrukcje projektu) | krótki tekst z sekcji niżej – każe przy każdej wiadomości użyć harnessu | ten plik (wersjonowany w repo); gotowa kopia z numerem wersji: `dist/claude-ai-projekt/instrukcje.md` z `tools/build.py` |
| **Wiedza projektu** (pliki) | może być pusta; opcjonalnie kopia awaryjna `00_SPIS.md` + `01_Sciaga-projektu.md` | paczka `_Do claude.ai/` (procedura `dokumenty`) |

Przewodnik po dokumentach i mapę Notion asystent czyta ze strony Notion „📑 Przewodnik po dokumentach i Notion” –
Claude Code aktualizuje ją sam (procedura `dokumenty`, sekcja C), więc po zmianach w dokumentach lub w strukturze Notion
nic nie trzeba wgrywać. Claude Code nie może zapisywać plików w wiedzy projektu na claude.ai (brak takiej możliwości),
ale może zapisywać w Notion, które claude.ai czyta na żywo.

Instrukcje są celowo tylko odnośnikiem: zasady i zachowanie (np. prośba o dokument) są w skillach i przychodzą
z pluginem, więc instrukcji nie trzeba wklejać na nowo przy każdej wersji – tylko gdy zmieni się tekst niżej
(CHANGELOG to zaznacza). Dawny plik `START.md` w wiedzy projektu – usuń.

## Aktualizacja pluginów na claude.ai

Wersję widać na stronie pluginu (Customize → Plugins → „Dom budowa” / „Ja”: „from notion-plugin · X.Y.Z”). Po pushu z podbitą
wersją:

1. Jeśli jest opcja odświeżenia marketplace'u (wg dokumentacji „Check for updates” przy marketplace „notion-plugin”, nie przy
   samym pluginie; może jej nie być, gdy organizacja ogranicza pluginy) – użyj jej.
2. Jeśli nie ma: usuń oba pluginy i marketplace „notion-plugin”, potem Add marketplace → `sztalinux/notion-plugin` →
   zainstaluj `dom-budowa` i `ja`. Pobiera się bieżąca wersja z GitHuba.
3. Gdy organizacja blokuje marketplace'y: `python3 tools/build.py`, Add → Upload plugin → `dist/dom-budowa.plugin`
   i `dist/ja.plugin`.

**Przejście z repo `sztalinux/dom` (jednorazowo, 2.0.0):** usuń plugin „Dom budowa” i marketplace „dom”, dodaj marketplace
`sztalinux/notion-plugin`, zainstaluj oba pluginy; zaplanowane zadanie „Przegląd dnia” usuń z projektu „Dom” i utwórz dwa
nowe poza projektem (tabela wyżej); w projekcie „Dom” wklej na nowo instrukcje z `dist/claude-ai-projekt/instrukcje.md`.

## Wiedza projektu a kontekst

Dopóki pliki mieszczą się w kontekście, claude.ai dołącza je w całości do każdej rozmowy w projekcie (szybciej zużywa
limit konta); powyżej progu sam przełącza się na wyszukiwanie fragmentów (RAG). Zajętość widać we wskaźniku pojemności
wiedzy projektu. Co trafia do paczki, decyduje procedura `dokumenty` (sekcja A).

## Tekst instrukcji

<!-- instrukcje-start -->
Jesteś asystentem budowy domu inwestora. Pracujesz według harnessu – pluginów „dom-budowa” i „ja” (skille).

1. Przy każdej wiadomości wczytaj skill `budowa` i według jego mapy procedur wczytaj właściwe skille
   (jedna wiadomość może wymagać kilku – po kolei). Nie czekaj, aż użytkownik wpisze „/”.
2. Raz na rozmowę (przy pierwszej wiadomości) sprawdź w Notion skrzynkę „Zmiany do harnessu” – opis w skillu `ja`.
   Sprawy pozabudowlane (Dziennik, zadania prywatne, emocje, dziecko) – skill `ja` i jego mapa.
3. Dane naszej budowy są w Notion: strona DOM (ściąga „📐 Dane projektu”, „🔴 Do zamknięcia”) i strona
   „📑 Przewodnik po dokumentach i Notion” (3f6f5982-09e7-81f5-bade-ec877d8d936a) – pobierz ją przy pierwszej
   wiadomości. Pełnych dokumentów tu nie ma – gdy są potrzebne, poproś o konkretny plik (skill `dokumenty`).
   Szukaj najpierw w moich materiałach, potem w sprawach otwartych, na końcu w internecie – zawsze ze źródłem
   (skill `budowa`, zasada 10). Nie zgaduj.
4. Brak narzędzi Notion w rozmowie (konektor wyłączony, telefon) to nie powód do odmowy: wiedzę czytaj z indeksu,
   Notatnik i zadania z migawki, a każdy zapis kieruj do dokumentu Claude „📥 Skrzynka” – Mac przeniesie go do Notion
   w ciągu godziny (skill `budowa`, zasada 13). Pomiń odczyty Notion z punktów 2–3 i napisz krótko, czego bez nich
   nie sprawdziłeś.
5. Jeśli skille dom-budowa są niedostępne, napisz to w pierwszym zdaniu i nie zgaduj procedur.
<!-- instrukcje-koniec -->
