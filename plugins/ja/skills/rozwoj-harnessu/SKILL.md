---
name: rozwoj-harnessu
description: Zgłaszanie i wdrażanie zmian w harnessie (pluginy dom-budowa i ja – procedury, zasady, szablony w repozytorium harnessu) przez bazę „🤖 Zmiany asystenta” w Notion (zasady, pomysły, usterki) oraz analiza pomysłów na rozwój setupu (Rodzaj Pomysł w bazie „🤖 Zmiany asystenta”). Używaj, gdy użytkownik poprawia sposób pracy asystenta („zawsze rób X”, „nie rób Y”, „źle to zapisałeś”, „zapamiętaj na przyszłość”), chce nową procedurę, zmienia strukturę Notion/arkusza, mówi „wdróż zmiany”, „zaktualizuj harness”, „mam pomysł na…”, „przeanalizuj pomysły”, „zrób POM-3”, „zrób ZP-2”, „znane problemy”, albo pyta o przeniesienie harnessu do innego AI.
---

# Rozwój harnessu

Źródło harnessu: **publiczne** repozytorium GitHub `sztalinux/notion-plugin` – marketplace z dwoma pluginami:
`dom-budowa` (budowa domu) i `ja` (Dziennik, emocje, zadania, dziecko, suplementy, przegląd dnia, ten skill). Claude na koncie
(czat, telefon, Cowork) pobiera z niego pluginy – po nowej wersji inwestor odświeża je ręcznie (albo synchronizacja, jeśli
organizacja pozwala).
Konfiguracja projektu „Dom” na claude.ai (instrukcje, wiedza): `references/claude-ai-projekt.md`. Zmiany trafiają do repo dwiema drogami:

| Gdzie jesteś | Co robisz |
|---|---|
| Czat, telefon, Cowork, inne AI (bez repo) | **Zgłoszenie** do bazy „🤖 Zmiany asystenta” (Rodzaj Zasada) – sekcja A |
| Claude Code w folderze repo | **Wdrożenie** skrzynki do plików + push – sekcja B (na polecenie „wdróż”) |
| Większy pomysł na rozwój (nowa funkcja, automatyzacja, zdjęcia, arkusz kosztorysu) | **Pomysł** (Rodzaj Pomysł w „🤖 Zmiany asystenta”) → analiza → wdrożenie na polecenie – sekcja C |
| Coś działa źle w tle, a przebieg tego nie naprawi (automat, skrypt, konektor) | **Usterka** (Rodzaj Usterka w „🤖 Zmiany asystenta”) → naprawa w Claude Code – sekcja D |

Skrzynka = konkretna reguła, wchodzi od razu. Pomysł = coś do przemyślenia; nic nie wchodzi samo, decyduje inwestor.

Jedna baza dla zasad, pomysłów i usterek: „🤖 Zmiany asystenta” – pola, statusy, ID (`HZ-n` / `POM-n` / `ZP-n`, pole tekstowe)
i widoki: `references/zmiany-asystenta.md`. Skrzynka = wiersze Rodzaj Zasada ze Statusem pustym albo „Do zrobienia”
(**pusty = do wdrożenia** – inwestor dodaje wpisy ręcznie, bez pól); widok „📥 Zasady do wdrożenia".

## Kiedy proponować zmianę (pętla uczenia)

Gdy inwestor w rozmowie:
- poprawia wynik w sposób, który powtórzy się w przyszłości (format, pole, zasada),
- dwa razy prosi o to samo dodatkowe działanie,
- zmienia strukturę danych (nowe pole w Notion, nowa kolumna w arkuszu kosztorysu, nowy etap),
- mówi wprost „zapamiętaj to na przyszłość”,

zaproponuj na końcu odpowiedzi jedną linię: „Dopisać to do harnessu (procedura `<nazwa>`)?”.
Bez zgody nic nie zapisuj. Jednorazowe prośby to nie zmiany harnessu.

## A. Zgłoszenie (z dowolnego miejsca)

1. Sformułuj zmianę tak, żeby dało się ją wdrożyć bez tej rozmowy:
   - **Zmiana:** krótki tytuł („Oferta: zawsze pytaj o fasety”),
   - **Plugin**, **Procedura** i **Typ zmiany** (Rodzaj = Zasada),
   - **Treść do wdrożenia:** gotowy tekst reguły w trybie rozkazującym, tak jak ma trafić do procedury,
   - **Dlaczego:** 1–2 zdania kontekstu z rozmowy (data).
2. Sprawdź w skrzynce, czy podobny wpis już nie czeka – jeśli tak, uzupełnij go zamiast dublować.
3. Zapisz jednym wywołaniem, Rodzaj Zasada, Status „Do zrobienia”, ID według `references/zmiany-asystenta.md`. Od tej chwili zmiana obowiązuje w rozmowach (procedura `budowa`,
   sekcja „Na starcie”); automaty Maca (przebiegi launchd) skrzynki nie czytają – stosują ją dopiero po wdrożeniu (sekcja B).
4. Potwierdź jedną linią: „Zapisane jako HZ-n – w rozmowach obowiązuje od teraz, w automatach Maca po wdrożeniu; wejdzie do repo, gdy napiszesz „wdróż” w Claude Code”.

## B. Wdrożenie (tylko Claude Code w folderze repo)

1. `git pull`. Pobierz wiersze Rodzaj Zasada ze Statusem „Do zrobienia” **albo pustym** (widok „📥 Zasady do wdrożenia”) (najstarsze pierwsze). Wpis dodany ręcznie z samym
   tytułem → najpierw uzupełnij pola jednym zapisem: Status „Do zrobienia”, ID, Plugin, Procedura, Typ zmiany, Treść do wdrożenia
   (reguła w trybie rozkazującym, wyprowadzona z tytułu) i Dlaczego („wpis ręczny inwestora, <data>”). Nie da się ustalić,
   o co chodzi → zapytaj inwestora, nie wdrażaj.
2. Dla każdego wpisu: znajdź właściwe miejsce (`plugins/<plugin>/skills/<procedura>/SKILL.md` lub `references/`),
   wprowadź zmianę zgodnie z `references/pisanie-procedur.md`. Nie kopiuj treści mechanicznie – wpasuj w strukturę
   procedury, usuń sprzeczne stare zapisy. Wpis niejasny lub sprzeczny z inną procedurą → zapytaj inwestora przed wdrożeniem;
   „nie wdrażaj” → Status „Odrzucone”, powód jednym zdaniem w polu Dlaczego (inaczej wpis wraca na każdym starcie).
3. Podbij wersję zmienionego pluginu w `plugins/<plugin>/.claude-plugin/plugin.json` (dla `dom-budowa` także
   `gemini-extension.json` – muszą być równe): PATCH = poprawka treści, MINOR = nowa procedura/pole, MAJOR = zmiana
   struktury danych. **Bez podbicia wersji telefon i Cowork nie dostaną aktualizacji.**
4. Dopisz wpis w `CHANGELOG.md` pod nagłówkiem `## <plugin> [wersja] – data` (lista HZ-n z jednym zdaniem każdy);
   zmiana obu pluginów = dwa nagłówki. Wdrożenie pomysłu lub znanego problemu: numer w nagłówku – `## ja [1.2.3] – data (POM-n)` –
   bo z niego przegląd dnia bierze wersję do pola „Zrobiono w wersji” (`przeglad-dnia/references/kontrola-spojnosci-pomysly.md`;
   `python3 tools/pomysly_wersje.py n` pokazuje, co wyjdzie – czyta gałąź main, więc po scaleniu).
5. `python3 tools/build.py` – musi przejść walidację, w tym kontrolę prywatności (wzorce + lista słów zakazanych
   `.dom/zakazane-w-repo.txt` w folderze budowy). Hooki w `.githooks/` powtarzają ją przy commicie (pliki, autor,
   wiadomość) i przed pushem (każdy wysyłany commit). Zablokowany hook = popraw dane, nigdy `--no-verify`.
   Przejrzyj `git diff`: zero nazwisk, firm, adresów, działek, telefonów, e-maili, kwot i treści notatek.
   Jeśli wpis ze skrzynki zawiera takie dane – wdroż regułę w wersji ogólnej („Firma A”), a konkret zostaw w Notion.
6. `git add <zmienione pliki> && git commit -m "Harness <plugin> <wersja>: HZ-… <skrót>" && git push` – tylko pliki z tej
   sesji; obcych zmian nie komentuj (kolizję zgłaszasz tylko, gdy realnie utrudnia Twoją zmianę – `CLAUDE.md`, 0a). `tools/build.py` odtwarza dowiązania `.claude/skills/` i `.agents/skills/` – nowy skill dodaj do commita z obydwoma.
7. W Notion oznacz wdrożone wpisy jednym przebiegiem: Status „Zrobione”, Zrobiono w wersji, Data wdrożenia.
   Zaktualizuj linię „Wersja” (obu pluginów) na stronie „🤖 Asystent AI” (najwyższy poziom Private, ID w `ja/references/notion-mapa.md`;
   strona to ramka nad skrzynką i pomysłami – opis procedur jest w README repo); nowa procedura = nowa opcja w polu „Procedura” skrzynki.
   **Dokumentacja dla człowieka – przy każdym wdrożeniu, nie tylko przy zmianie struktury:** przejdź listę z `ja`,
   zasada 8 (repo i Notion), wyszukaj stare określenia, których zmiana dotyczy, i popraw nieaktualne zdania w tym samym
   wydaniu – także „📘 Instrukcja obsługi” (pod DASHBOARD), ale **tylko sekcje, których dotyczy zmiana**, z nową linią „Stan:”
   (zmiana niewidoczna dla inwestora → instrukcji nie ruszaj); kopii offline `AI/Instrukcja obsługi.md` przy wdrożeniu nie
   odświeżaj – robi to raz w miesiącu `przeglad-tygodnia-osobisty` (krok 3); w podsumowaniu linia „Dokumentacja: <co zaktualizowane> / bez zmian – <dlaczego>”.
   Zmiana struktury Notion (baza, widok, pole) → zaktualizuj mapę: budowa – `dom-budowa/skills/budowa/references/notion-mapa.md`,
   sprawy osobiste – `ja/skills/ja/references/notion-mapa.md`. Obie trafiają do przewodnika w Notion przy następnym
   `tools/dokumenty.py` – zsynchronizuj go (`dokumenty`, sekcja C). Pełna lista miejsc w repo i w Notion, które trzeba
   zaktualizować przy zmianie miejsca lub struktury: `ja`, zasada 8 – przejdź ją całą. Nowy rodzaj wpisu w Dzienniku, który da się opisać
   polami „Gdzie” i „Jak zapisać”, to wiersz w bazie Obszary, nie zmiana harnessu.
8. Podsumuj w blokach z `ja` („Domknięcie rozmowy”), w 2–4 liniach: ✅ wersje i co weszło, ⏳ co odrzucone lub odłożone i dlaczego
   oraz czynności po stronie inwestora (to nie pytania – nie wpisuj ich do 🛑): „odśwież plugin(y) na claude.ai
   (`references/claude-ai-projekt.md`, sekcja „Aktualizacja pluginów”)”; jeśli zmienił się tekst instrukcji
   w `references/claude-ai-projekt.md` – także „wklej na nowo `dist/claude-ai-projekt/instrukcje.md` w projekt »Dom«”;
   jeśli zmienił się kod Apps Script (`docs/wydatki-arkusz.md`, sekcja 9) – „zaktualizuj kod arkusza do wersji N (sekcja 7,
   »Aktualizacja kodu«); do tego czasu `wydatki.py sync` odkłada to, co wymaga nowej wersji” (to samo w CHANGELOG).

Zmiany, o które inwestor prosi bezpośrednio w Claude Code, wdrażasz od razu tymi samymi krokami 2–8 (bez skrzynki).

## C. Pomysły (Rodzaj Pomysł)

Wiersze Rodzaj Pomysł w „🤖 Zmiany asystenta” (widok „💡 Tablica pomysłów”; pola i statusy: `references/zmiany-asystenta.md`;
**pusty Status = Nowy**; dawne „Pytania do mnie” = „Czeka na mnie”).
Treść strony: pomysł inwestora (nie zmieniaj), pod nim sekcja „Analiza” pisana przez asystenta.

**Zapis pomysłu** („mam pomysł…”, wpis w Dzienniku „pomysł: …” o asystencie, Notion, arkuszu kosztorysu, plikach, automatyzacji):
sprawdź, czy podobny już jest (uzupełnij zamiast dublować); nowy wiersz – tytuł, Obszar, w treści „## Pomysł (kto, data)”
i słowa inwestora. Rodzaj Pomysł, ID tekst wg `references/zmiany-asystenta.md` („ID nowego wiersza”), Status pusty/Nowy. Poprawka sposobu pracy (jedna reguła) to nie pomysł – sekcja A.

**Analiza** – tylko na prośbę inwestora („przeanalizuj pomysły”, „przeanalizuj POM-n”); przegląd dnia ich nie analizuje (wpisy Nowy lub pusty):
1. Przeczytaj pomysł i przejrzyj, co już jest: procedury (mapy w `ja` i `budowa`, odpowiednie `SKILL.md`), mapy Notion
   (`ja/references/notion-mapa.md`, `budowa/references/notion-mapa.md`), inne pomysły (zależności, duplikaty). Wiersz dodany
   ręcznie z pustymi polami → uzupełnij je przy analizie (Obszar, Status, Nakład, Wymaga ode mnie).
2. Niejasne, co inwestor chce → dopisz „### ❓ Pytania (data)” z 1–3 pytaniami i propozycją interpretacji, Status
   „Czeka na mnie”. Odpowiedź inwestora pod pytaniami → analizuj dalej przy kolejnej prośbie inwestora.
3. Jasne → dopisz pod pomysłem sekcję (nie nadpisuj wcześniejszych):
   ```
   ## Analiza (asystent, data)
   **Co rozumiem:** 1–2 zdania.
   **Co już jest:** procedury / bazy / pola, które to częściowo robią; czego brakuje.
   **Co trzeba zrobić:** Harness (pliki procedur) · Notion (bazy, pola, widoki) · arkusz kosztorysu · narzędzia w repo · Ty (decyzje,
     aplikacje, konta) – lista numerowana, kolejność wdrożenia dla Claude Code.
   **Ograniczenia:** czego się nie da / co wymaga zgody (np. connector do nowej usługi → najpierw zgłoszenie IT
     w organizacji inwestora; nie proponuj obejść), koszty usług, prywatność (repo publiczne).
   **Bez konektora:** droga zapasowa, gdy inwestor straci dostęp (`AGENTS.md`), albo wprost „brak zapasu – …”.
   **Nakład:** S (jedna sesja) / M (kilka) / L (projekt). **Zależności:** POM-n.
   **Do decyzji przed startem:** … **Rekomendacja:** zrobić teraz / przed <etapem> / odłożyć – dlaczego.
   ```
   Ustaw: Status „Przeanalizowany”, Nakład, Obszar, „Wymaga ode mnie” (krótko), Przeanalizowano = data.
4. Analiza to plan, nie wdrożenie: nie zmieniaj procedur, baz ani plików. Bez dostępu do repo (claude.ai) opieraj się
   na skillach z pluginu – Claude Code i tak sprawdzi pliki przed wdrożeniem.

**Wdrożenie** – tylko gdy inwestor powie w Claude Code „zrób POM-n” (albo ustawi „Do zrobienia” i poprosi o to):
przeczytaj stronę pomysłu z analizą, potwierdź decyzje z „Do decyzji przed startem”, potem kroki B.2–B.8. Na końcu Status
„Zrobione”, „Zrobiono w wersji”, w treści linia „Wdrożone w <wersja> (data): co weszło, co pominięto”. Wdrożenie tylko część
pomysłu → Status zostaje, a w „Zrobiono w wersji” dopisz „(częściowo)” (kontrola spójności tego nie flaguje).

## D. Usterki (Rodzaj Usterka, dawne „Znane problemy”)

Wiersze Rodzaj Usterka w „🤖 Zmiany asystenta” (widok „🧯 Otwarte usterki”: Status inny niż Zrobione / Odrzucone; pola: Obszar,
Skąd – klucz komunikatu albo procedura, Pierwszy raz, Ostatnio, Co zrobić – jedno zdanie: następny krok i kto, Zrobiono w wersji;
`references/zmiany-asystenta.md`). Dawne „Rozwiązany” = „Zrobione”, „Zostaje” = „Odrzucone”.
Treść strony: objaśnienie, wystąpienia z datą, ustalenia z odpowiedzi inwestora.

- **Kto wpisuje:** przebieg, gdy odpowiedź pod komunikatem 🔔 wymaga pracy poza przebiegiem (`wpisy/references/pytania.md`,
  C.5); Claude Code, gdy w pracy trafi na powtarzalną usterkę spoza bieżącego zadania; inwestor ręcznie (pusty Status =
  Nowy). Przed dodaniem szukaj tego samego problemu (Skąd, 2–3 słowa) – jest → zaktualizuj Ostatnio i treść; nowy wiersz – Rodzaj Usterka, ID tekst wg `references/zmiany-asystenta.md` („ID nowego wiersza”).
- **Problem a pomysł:** coś, co miało działać, a nie działa → tu; nowa funkcja albo zmiana sposobu pracy → sekcja C lub A.
- **Naprawa** – w Claude Code na „zrób ZP-n” (albo gdy inwestor wskaże ZP):
  przeczytaj stronę, ustal przyczynę (log, `stan.json`, skrypt), napraw; zmiana harnessu → kroki B.2–B.8. Na końcu Status
  „Zrobione”, Zrobiono w wersji (albo „skrypt poza repo, data”), w treści linia „Naprawione (data): przyczyna, co
  zmieniono”. Wybór wariantu technicznego rozstrzygnij sam (domyślny z „Co zrobić”) – nie pytaj. Naprawa naprawdę wymaga
  inwestora (dostęp, kliknięcie, decyzja budowlana) → Status „Czeka na mnie” i od razu blok 🔔 w „📝 Wpisy” z pytaniem
  (`wpisy/references/pytania.md`, C.5) – sam status w bazie nie wystarczy; nie warto → „Odrzucone”.
- Komunikat 🔔 z linią `→ ZP-n` znika z „Wpisów”, gdy wiersz jest „Zrobione” albo „Odrzucone” (sprawdza przebieg nocny).

## Nowa procedura – minimum

- Katalog `plugins/<plugin>/skills/<nazwa-kebab-case>/SKILL.md` (budowa → `dom-budowa`, reszta → `ja`) z frontmatter
  `name` (= nazwa katalogu, **unikalna w obu pluginach**) i `description` (co robi + kiedy używać + typowe frazy, < 1024 znaki).
- Wpis w tabeli procedur w `AGENTS.md` i w mapie procedur skilla kontekstowego pluginu (`ja/SKILL.md` albo
  `budowa/SKILL.md`); nowa opcja w polu „Procedura” skrzynki w Notion; gdy procedura obsługuje wpisy z Dziennika –
  wiersz w bazie Obszary z tą nazwą w polu Procedura (i nowa opcja tego pola).
- Szczegóły, schematy, szablony → `references/`.

## Przeniesienie do innego dostawcy

Opis adapterów (Claude, Gemini CLI, Gemini w przeglądarce, Codex): `references/dostawcy.md`.
