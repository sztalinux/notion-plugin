# Wiedza w Notion – identyfikatory, pola, plan zapisu (stan: 2026-10-09)

Strona główna: **📚 Baza wiedzy** `3f4f5982-09e7-8193-a68e-fd35c9265012` (DOM → toggle „Baza wiedzy”).
Na niej: „⏳ Czeka na decyzję”, informacje z zakładkami „🆕 Do przejrzenia” (Nowe, wg Istotności), „⭐ Kluczowe i ważne”,
„💬 Z moim komentarzem”, „🎯 Na teraz – <etap>” (bieżący etap + Cała budowa, pod koniec etapu także następny); blok
„🗂 Wiedza wg etapu” (zakładka na każdy etap, stałe filtry); bazy Tematy i Rozmowy i źródła,
podstrona „Bazy: Informacje i Rejestr sprzeczności”. Jeśli zapis zwróci błąd pola – pobierz schemat bazy i zaktualizuj ten plik.

Cztery warstwy: **Tematy** (co wiemy teraz) ← **Informacje** (pojedyncze fakty) ← **Rozmowy i źródła** (kto, kiedy, skąd)
+ **Rejestr sprzeczności** (spory i decyzje inwestora). Działania dla naszej budowy → Notatnik budowy.

## Rozmowy i źródła – `collection://35453d82-e38d-4797-840c-d19677c71b54` (ID: ZRD-n)

Jeden wpis = jedno źródło: film, artykuł, telefon, spotkanie, mail, wizyta na budowie.

| Pole | Typ | Wartości / uwagi |
|---|---|---|
| Rozmowa | tytuł | film: tytuł filmu; rozmowa: „Telefon – konstruktor – przerwa robocza” |
| Data | data | data rozmowy / **data publikacji** filmu |
| Forma | select | Telefon, Spotkanie, Na budowie, Mail / SMS, Artykuł / film, Notatki własne |
| Kto | tekst | imię / firma / kanał |
| Z kim | select | Konstruktor, Architekt, Geotechnik, Kierownik budowy, Wykonawca, Instalator, Urząd / gestor, Internet / kurs, Rodzina / znajomi, Inne |
| Najważniejsze | tekst | 3–5 punktów: główne tezy, dosłownie liczby i nazwy |
| Link | URL | film / artykuł |
| Typ autora | select | Niezależny wykonawca, Projektant / konstruktor, Kierownik / inspektor, Producent, Sprzedawca / dystrybutor, Inwestor (własna budowa), Twórca / popularyzator, Nasz projektant / wykonawca, Inny |
| Konflikt interesów | select | Brak, Możliwy, Materiał sponsorowany, ? |
| Wiarygodność | select | 5 – bardzo wysoka, 4 – wysoka, 3 – średnia, 2 – niska, 1 – wątpliwa |
| Tematy | relacja → Tematy | |
| Informacje | relacja → Informacje | |
| Sprzeczności | relacja → Rejestr | |
| Przeniesione do tematu | checkbox | zaznacz, gdy przetworzone |
| Dodano | czas utworzenia | auto |

## Tematy – `collection://718422ca-ed6f-4269-a38f-4e508eff286c`

Jeden wiersz = jeden temat (np. Hydroizolacja piwnicy, Drenaż, Przemarzanie). Treść strony tematu = aktualny stan wiedzy.

| Pole | Typ | Wartości |
|---|---|---|
| Temat | tytuł | |
| W skrócie | tekst | aktualny stan wiedzy w 1–2 zdaniach – co obowiązuje dziś |
| Stan wiedzy | select | Ustalone, W trakcie, Do sprawdzenia |
| Branża | multi-select | jak niżej |
| Etap | select | jak niżej |
| Kluczowe dla | multi-select | Konstruktor, Architekt, Geotechnik, Kierownik budowy, Ekipa, Instalator |
| Rozmowy / Informacje / Sprzeczności / Notatnik | relacje | |
| Aktualizacja | ostatnia edycja | auto |

Przed utworzeniem nowego tematu sprawdź, czy nie ma bliskiego istniejącego (np. „Hydroizolacja piwnicy” zamiast nowego „Izolacja ścian”).
Temat ma być na tyle szeroki, by zebrać kilka-kilkanaście informacji.

## Informacje – `collection://f78bb02d-6da5-46fb-bea9-c25e15f93117` (ID: WI-n)

| Pole | Typ | Wartości / uwagi |
|---|---|---|
| Informacja | tytuł | samodzielne zdanie z liczbami i warunkiem |
| Szczegóły | tekst | warunki, wyjątki, produkty, uzasadnienie; „uzupełnia WI-x” |
| Rodzaj | select | Zasada wykonania, Parametr / liczba, Błąd do uniknięcia, Kolejność prac, Materiał / produkt, Koszt / cena, Przepis / norma, Kontrola / odbiór, Inne |
| Branża | multi-select | Konstrukcja, Grunt i woda, Hydroizolacja, Drenaż, Elektryka, Wod-kan, Ogrzewanie, Wentylacja, Dach, Okna i drzwi, Elewacja, Ściany, Wnętrza, Smart home, Ogród, Formalności, Energooszczędność, Organizacja |
| Etap | select | Projekt i formalności, Stan zero, SSO, Deweloperski, Wykończenie, Teren i ogród, Cała budowa – **kiedy wiedza będzie potrzebna** (SKILL.md, A.4) |
| Tematy | relacja → Tematy | **ustawiaj zawsze** – tak informacja trafia „w dobre miejsce” |
| Źródła | relacja → Rozmowy i źródła | **źródło obowiązkowe**: Źródła albo Notatnik (SKILL.md) |
| Notatnik | relacja → Notatnik budowy (tam: „Wiedza”) | ustalenie/decyzja naszej budowy, z której wynika informacja (sekcja F) |
| Sprzeczności | relacja → Rejestr | |
| Potwierdzenia | rollup (liczba źródeł) | **tylko odczyt** |
| Data informacji | rollup (najnowsza data źródła) | **tylko odczyt** |
| Fragment | tekst | `mm:ss – „cytat”` |
| Dotyczy nas | select | Tak, Częściowo, Nie, Do oceny |
| Dla naszej budowy | tekst | 1–2 zdania |
| Status | select | Nowe, Przejrzane, Sporne, Nieaktualne |
| Istotność | select | Kluczowe, Ważne, Ciekawostka – przy „Nowe” propozycja asystenta, po przejrzeniu ocena inwestora (SKILL.md) |
| Mój komentarz | tekst | **pole inwestora** – nie nadpisuj; sprzeciw/wątpliwość → SKILL.md, sekcja H |
| Pokazano | data | kiedy ostatnio w przeglądzie tygodnia w „Wiedza na teraz” – ustawia przegląd, żeby się nie powtarzała |
| Wrażliwe na czas | checkbox | ceny, przepisy, dotacje, dostępność produktów |
| Dodano / Zmieniono | czas | auto |

## Rejestr sprzeczności – `collection://7589d5f5-2d22-4b85-9138-72cd34d4a1f8` (ID: SP-n)

Pola: Dylemat (tytuł), Status (Czeka na decyzję, Do sprawdzenia u projektanta, Rozstrzygnięte, Zastąpione,
Nieaktualne), Rodzaj (Źródło vs źródło, Źródło vs projekt, Źródło vs nasza decyzja, Źródło vs oferta wykonawcy,
Dylemat bez sprzeczności), Branża (multi-select), Etap (select), Priorytet (Krytyczne, Ważne, Zwykłe), Stanowisko A,
Stanowisko B, Kontekst naszej budowy, Opcje, Rekomendacja asystenta, Pytanie do inwestora, Decyzja, Uzasadnienie,
Konsekwencje, Data decyzji (data), Informacje (relacja), Źródła (relacja → Rozmowy i źródła), Tematy (relacja), Karta (Notatnik) (relacja → Notatnik budowy; po stronie
Notatnika „Sprzeczność (Rejestr)”), Zgłoszono (auto).
Długie pola tekstowe (Stanowisko A/B, Kontekst naszej budowy, Opcje, Rekomendacja asystenta, Uzasadnienie, Konsekwencje,
Decyzja) to rich_text. Numer (WI-n, ZRD-n, SP-n) niesie właściwość `ID` (unique_id); Tematy jej nie mają.
W Notion właściwość opisana tu jako „Pytanie do inwestora” ma w rzeczywistej nazwie imię inwestora – przed zapisem
pobierz schemat bazy i dopasuj ją po prefiksie „Pytanie do”.

## Plan zapisu jednego źródła (minimum zatwierdzeń, pełna jakość)

Najpierw wszystkie odczyty (tematy, podobne informacje, sprzeczności, decyzje), potem zapisy w tej kolejności:

1. **Tematy – jedno wywołanie** tworzące wszystkie potrzebne nowe tematy (tylko jeśli brak pasujących).
2. **Informacje – jedno wywołanie** tworzące wszystkie nowe wiersze (NOWE, UZUPEŁNIENIA, SPORNE) z relacją Tematy.
3. **Rejestr – jedno wywołanie** tworzące wszystkie wpisy SP z relacjami Informacje (nowe sporne + istniejące) i Tematy.
4. **Rozmowy i źródła – jedno wywołanie** tworzące wpis źródła z relacjami Informacje = (nowe + istniejące potwierdzone),
   Tematy, Sprzeczności. Relacje dwustronne same uzupełnią drugą stronę, a rollupy przeliczą Potwierdzenia i Datę
   informacji – **nie aktualizuj potwierdzonych wierszy pojedynczo**.
5. **Notatnik budowy – jedno wywołanie** ze wszystkimi wpisami do działania (jeśli są).
6. **Tematy – aktualizacja „W skrócie”/treści** tylko dla tematów spełniających próg z SKILL.md (krok 8), po jednym na temat.
7. **Indeks wiedzy** (po zapisach 1–6, szczegóły: `references/indeks.md`): w sesji interaktywnej Claude Code w repo uruchom
   `python3 tools/wiedza.py sync --publikuj`; w przebiegu nocnym pomiń (sync robi skrypt); w czacie pomiń i napisz wprost,
   że indeks dogoni przy najbliższym sync na Macu.

Rozstrzygnięcie sprzeczności (po decyzji): wpis SP (1) + wiersze Informacji, którym zmienia się status (po 1 na wiersz)
+ ewentualnie Notatnik (1) + temat (1).

## Szablon treści strony tematu

```
<callout icon="🧭" color="gray_bg">
	Aktualizacja: <data> · źródeł: <n> · otwarte sprzeczności: <n>
</callout>
## Stan wiedzy
- <zwięzły punkt z liczbami> (WI-x, WI-y)
## Dla naszej budowy
- <co z tego wynika u nas, co ustalone, czego pilnować>
## Sprzeczności i rozstrzygnięcia
- SP-n <dylemat> – <czeka / decyzja: …>
```
Wszystkie informacje tematu są widoczne w relacji „Informacje” na stronie tematu – nie kopiuj ich do treści.
