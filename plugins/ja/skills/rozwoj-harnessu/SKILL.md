---
name: rozwoj-harnessu
description: Zgłaszanie i wdrażanie zmian w harnessie (pluginy dom-budowa i ja – procedury, zasady, szablony w repozytorium harnessu) przez skrzynkę „Zmiany do harnessu” w Notion oraz analiza pomysłów na rozwój setupu (baza „Pomysły na rozwój”). Używaj, gdy użytkownik poprawia sposób pracy asystenta („zawsze rób X”, „nie rób Y”, „źle to zapisałeś”, „zapamiętaj na przyszłość”), chce nową procedurę, zmienia strukturę Notion/Excela, mówi „wdróż zmiany”, „zaktualizuj harness”, „mam pomysł na…”, „przeanalizuj pomysły”, „zrób POM-3”, albo pyta o przeniesienie harnessu do innego AI.
---

# Rozwój harnessu

Źródło harnessu: **publiczne** repozytorium GitHub `sztalinux/notion-plugin` – marketplace z dwoma pluginami:
`dom-budowa` (budowa domu) i `ja` (Dziennik, emocje, zadania, dziecko, suplementy, przegląd dnia, ten skill). Claude na koncie
(czat, telefon, Cowork) pobiera z niego pluginy – po nowej wersji inwestor odświeża je ręcznie (albo synchronizacja, jeśli
organizacja pozwala).
Konfiguracja projektu „Dom” na claude.ai (instrukcje, wiedza): `references/claude-ai-projekt.md`. Zmiany trafiają do repo dwiema drogami:

| Gdzie jesteś | Co robisz |
|---|---|
| Czat, telefon, Cowork, inne AI (bez repo) | **Zgłoszenie** do skrzynki w Notion – sekcja A |
| Claude Code w folderze repo | **Wdrożenie** skrzynki do plików + push – sekcja B (na starcie sesji tylko po zaznaczeniu „Skrzynka zmian” na liście startowej, `CLAUDE.md`) |
| Większy pomysł na rozwój (nowa funkcja, automatyzacja, zdjęcia, Excel) | **Pomysł** do bazy „Pomysły na rozwój” → analiza → wdrożenie na polecenie – sekcja C |

Skrzynka = konkretna reguła, wchodzi od razu. Pomysł = coś do przemyślenia; nic nie wchodzi samo, decyduje inwestor.

Skrzynka: Notion → „Zmiany do harnessu”, `collection://e217448a-60ec-4af6-8584-8f368315109c`.
Pola: Zmiana (tytuł), Status (Do wdrożenia / Wdrożone / Odrzucone; **pusty = do wdrożenia** – inwestor dodaje wpisy ręcznie,
bez pól), Plugin (dom-budowa / ja), Procedura, Rodzaj (Nowa zasada, Poprawka, Nowa procedura, Zmiana struktury Notion / Excela,
Usunięcie), Treść do wdrożenia, Dlaczego, Wdrożono w wersji, Data wdrożenia, ID (HZ-n).

## Kiedy proponować zmianę (pętla uczenia)

Gdy inwestor w rozmowie:
- poprawia wynik w sposób, który powtórzy się w przyszłości (format, pole, zasada),
- dwa razy prosi o to samo dodatkowe działanie,
- zmienia strukturę danych (nowe pole w Notion, nowa kolumna w Excelu, nowy etap),
- mówi wprost „zapamiętaj to na przyszłość”,

zaproponuj na końcu odpowiedzi jedną linię: „Dopisać to do harnessu (procedura `<nazwa>`)?”.
Bez zgody nic nie zapisuj. Jednorazowe prośby to nie zmiany harnessu.

## A. Zgłoszenie (z dowolnego miejsca)

1. Sformułuj zmianę tak, żeby dało się ją wdrożyć bez tej rozmowy:
   - **Zmiana:** krótki tytuł („Oferta: zawsze pytaj o fasety”),
   - **Plugin**, **Procedura** i **Rodzaj**,
   - **Treść do wdrożenia:** gotowy tekst reguły w trybie rozkazującym, tak jak ma trafić do procedury,
   - **Dlaczego:** 1–2 zdania kontekstu z rozmowy (data).
2. Sprawdź w skrzynce, czy podobny wpis już nie czeka – jeśli tak, uzupełnij go zamiast dublować.
3. Zapisz jednym wywołaniem, Status „Do wdrożenia”. Od tej chwili zmiana obowiązuje wszędzie
   (procedura `budowa`, sekcja „Na starcie”).
4. Potwierdź jedną linią: „Zapisane jako HZ-n – obowiązuje od teraz, wejdzie do repo, gdy zaznaczysz „Skrzynka zmian” na starcie sesji Claude Code”.

## B. Wdrożenie (tylko Claude Code w folderze repo)

1. `git pull`. Pobierz wpisy ze Statusem „Do wdrożenia” **albo pustym** (najstarsze pierwsze). Wpis dodany ręcznie z samym
   tytułem → najpierw uzupełnij pola jednym zapisem: Status „Do wdrożenia”, Plugin, Procedura, Rodzaj, Treść do wdrożenia
   (reguła w trybie rozkazującym, wyprowadzona z tytułu) i Dlaczego („wpis ręczny inwestora, <data>”). Nie da się ustalić,
   o co chodzi → zapytaj inwestora, nie wdrażaj.
2. Dla każdego wpisu: znajdź właściwe miejsce (`plugins/<plugin>/skills/<procedura>/SKILL.md` lub `references/`),
   wprowadź zmianę zgodnie z `references/pisanie-procedur.md`. Nie kopiuj treści mechanicznie – wpasuj w strukturę
   procedury, usuń sprzeczne stare zapisy. Wpis niejasny lub sprzeczny z inną procedurą → zapytaj inwestora przed wdrożeniem.
3. Podbij wersję zmienionego pluginu w `plugins/<plugin>/.claude-plugin/plugin.json` (dla `dom-budowa` także
   `gemini-extension.json` – muszą być równe): PATCH = poprawka treści, MINOR = nowa procedura/pole, MAJOR = zmiana
   struktury danych. **Bez podbicia wersji telefon i Cowork nie dostaną aktualizacji.**
4. Dopisz wpis w `CHANGELOG.md` pod nagłówkiem `## <plugin> [wersja] – data` (lista HZ-n z jednym zdaniem każdy);
   zmiana obu pluginów = dwa nagłówki.
5. `python3 tools/build.py` – musi przejść walidację, w tym kontrolę prywatności (wzorce + lista słów zakazanych
   `.dom/zakazane-w-repo.txt` w folderze budowy). Hooki w `.githooks/` powtarzają ją przy commicie (pliki, autor,
   wiadomość) i przed pushem (każdy wysyłany commit). Zablokowany hook = popraw dane, nigdy `--no-verify`.
   Przejrzyj `git diff`: zero nazwisk, firm, adresów, działek, telefonów, e-maili, kwot i treści notatek.
   Jeśli wpis ze skrzynki zawiera takie dane – wdroż regułę w wersji ogólnej („Firma A”), a konkret zostaw w Notion.
6. `git add <zmienione pliki> && git commit -m "Harness <plugin> <wersja>: HZ-… <skrót>" && git push` – tylko pliki z tej
   sesji; obcych zmian nie komentuj (kolizję zgłaszasz tylko, gdy realnie utrudnia Twoją zmianę – `CLAUDE.md`, 0a). `tools/build.py` odtwarza dowiązania `.claude/skills/` – nowy skill dodaj do commita z nimi.
7. W Notion oznacz wdrożone wpisy jednym przebiegiem: Status „Wdrożone”, Wdrożono w wersji, Data wdrożenia.
   Zaktualizuj linię „Wersja” (obu pluginów) na stronie „🤖 Asystent AI” (najwyższy poziom Private, ID w `ja/references/notion-mapa.md`;
   strona to ramka nad skrzynką i pomysłami – opis procedur jest w README repo); nowa procedura = nowa opcja w polu „Procedura” skrzynki.
   Zmiana struktury Notion (baza, widok, pole) → zaktualizuj mapę: budowa – `dom-budowa/skills/budowa/references/notion-mapa.md`,
   sprawy osobiste – `ja/skills/ja/references/notion-mapa.md`. Obie trafiają do przewodnika w Notion przy następnym
   `tools/dokumenty.py` – zsynchronizuj go (`dokumenty`, sekcja C). Pełna lista miejsc w repo i w Notion, które trzeba
   zaktualizować przy zmianie miejsca lub struktury: `ja`, zasada 8 – przejdź ją całą. Nowy rodzaj wpisu w Dzienniku, który da się opisać
   polami „Gdzie” i „Jak zapisać”, to wiersz w bazie Obszary, nie zmiana harnessu.
8. Podsumuj w blokach z `ja` („Domknięcie rozmowy”), w 2–4 liniach: ✅ wersje i co weszło, ⏳ co odrzucone lub odłożone i dlaczego
   oraz czynności po stronie inwestora (to nie pytania – nie wpisuj ich do 🛑): „odśwież plugin(y) na claude.ai
   (`references/claude-ai-projekt.md`, sekcja „Aktualizacja pluginów”)”; jeśli zmienił się tekst instrukcji
   w `references/claude-ai-projekt.md` – także „wklej na nowo `dist/claude-ai-projekt/instrukcje.md` w projekt »Dom«”.

Zmiany, o które inwestor prosi bezpośrednio w Claude Code, wdrażasz od razu tymi samymi krokami 2–8 (bez skrzynki).

## C. Pomysły na rozwój

Baza: Notion → 🤖 Asystent AI → „💡 Pomysły na rozwój”, `collection://fdee4f05-8f43-4be4-a0d5-2b88642fa6d3` (widok „💡 Tablica”).
Pola: Pomysł (tytuł), Status (Nowy / Pytania do mnie / Przeanalizowany / Do zrobienia / Zrobione / Odłożone / Odrzucone;
**pusty = Nowy**), Obszar, Nakład (S/M/L), Wymaga ode mnie, Przeanalizowano, Zrobiono w wersji, ID (POM-n).
Treść strony: pomysł inwestora (nie zmieniaj), pod nim sekcja „Analiza” pisana przez asystenta.

**Zapis pomysłu** („mam pomysł…”, wpis w Dzienniku „pomysł: …” o asystencie, Notion, Excelu, plikach, automatyzacji):
sprawdź, czy podobny już jest (uzupełnij zamiast dublować); nowy wiersz – tytuł, Obszar, w treści „## Pomysł (kto, data)”
i słowa inwestora. Status pusty/Nowy. Poprawka sposobu pracy (jedna reguła) to nie pomysł – sekcja A.

**Analiza** (wpisy Nowy lub pusty; w przeglądzie dnia `przeglad-dnia` automatycznie, inaczej na prośbę):
1. Przeczytaj pomysł i przejrzyj, co już jest: procedury (mapy w `ja` i `budowa`, odpowiednie `SKILL.md`), mapy Notion
   (`ja/references/notion-mapa.md`, `budowa/references/notion-mapa.md`), inne pomysły (zależności, duplikaty). Wiersz dodany
   ręcznie z pustymi polami → uzupełnij je przy analizie (Obszar, Status, Nakład, Wymaga ode mnie).
2. Niejasne, co inwestor chce → dopisz „### ❓ Pytania (data)” z 1–3 pytaniami i propozycją interpretacji, Status
   „Pytania do mnie”. Odpowiedź inwestora pod pytaniami → przy następnym przebiegu analizuj dalej.
3. Jasne → dopisz pod pomysłem sekcję (nie nadpisuj wcześniejszych):
   ```
   ## Analiza (asystent, data)
   **Co rozumiem:** 1–2 zdania.
   **Co już jest:** procedury / bazy / pola, które to częściowo robią; czego brakuje.
   **Co trzeba zrobić:** Harness (pliki procedur) · Notion (bazy, pola, widoki) · Excel · narzędzia w repo · Ty (decyzje,
     aplikacje, konta) – lista numerowana, kolejność wdrożenia dla Claude Code.
   **Ograniczenia:** czego się nie da / co wymaga zgody (np. connector do nowej usługi → najpierw zgłoszenie IT
     w organizacji inwestora; nie proponuj obejść), koszty usług, prywatność (repo publiczne).
   **Nakład:** S (jedna sesja) / M (kilka) / L (projekt). **Zależności:** POM-n.
   **Do decyzji przed startem:** … **Rekomendacja:** zrobić teraz / przed <etapem> / odłożyć – dlaczego.
   ```
   Ustaw: Status „Przeanalizowany”, Nakład, Obszar, „Wymaga ode mnie” (krótko), Przeanalizowano = data.
4. Analiza to plan, nie wdrożenie: nie zmieniaj procedur, baz ani plików. Bez dostępu do repo (claude.ai) opieraj się
   na skillach z pluginu – Claude Code i tak sprawdzi pliki przed wdrożeniem.

**Wdrożenie** – tylko gdy inwestor powie w Claude Code „zrób POM-n” (albo ustawi „Do zrobienia” i poprosi o to):
przeczytaj stronę pomysłu z analizą, potwierdź decyzje z „Do decyzji przed startem”, potem kroki B.2–B.8. Na końcu Status
„Zrobione”, „Zrobiono w wersji”, w treści linia „Wdrożone w <wersja> (data): co weszło, co pominięto”.

## Nowa procedura – minimum

- Katalog `plugins/<plugin>/skills/<nazwa-kebab-case>/SKILL.md` (budowa → `dom-budowa`, reszta → `ja`) z frontmatter
  `name` (= nazwa katalogu, **unikalna w obu pluginach**) i `description` (co robi + kiedy używać + typowe frazy, < 1024 znaki).
- Wpis w tabeli procedur w `AGENTS.md` i w mapie procedur skilla kontekstowego pluginu (`ja/SKILL.md` albo
  `budowa/SKILL.md`); nowa opcja w polu „Procedura” skrzynki w Notion; gdy procedura obsługuje wpisy z Dziennika –
  wiersz w bazie Obszary z tą nazwą w polu Procedura (i nowa opcja tego pola).
- Szczegóły, schematy, szablony → `references/`.

## Przeniesienie do innego dostawcy

Opis adapterów (Claude, Gemini CLI, Gemini w przeglądarce, Codex): `references/dostawcy.md`.
