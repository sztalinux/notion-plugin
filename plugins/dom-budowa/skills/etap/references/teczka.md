# Teczka etapu – składniki, braki, wymagania banku

Teczka = folder `Teczki/<Etap>/RRRR-MM-DD/` w folderze budowy ze spisem `SPIS.md`: dokumenty etapu w działach 1–5 i lista
braków. Służy do (a) wniosku o wypłatę transzy kredytu i kontroli banku, (b) rozliczenia transzy z wykonawcą po odbiorze.
Składa ją `tools/teczka.py` (Claude Code z folderem budowy; czat bez folderu tylko przygotuje listę braków słowami).

## Wymagania banku – nie zgaduj

**Nie wiemy, czego wymaga bank ani czy kredyt będzie w transzach** – wiedza jest w umowie kredytowej (folder budowy, `dokumenty`)
i w regulaminie wypłat banku. Poniższa lista to **typowy zestaw `[opinia]`, do potwierdzenia z umową kredytową** – gdy umowa jest
w folderze, porównaj ją z listą i wynik wpisz do Notatnika jako Decyzję („Bank wymaga: …”). Do tego czasu teczka jest
uniwersalna: zbiera wszystko, co zwykle potrzebne, i nie obiecuje kompletu.

## Typowe składniki (stan: do potwierdzenia z umową kredytową)

| Dział teczki | Składnik | Skąd | Uwaga |
|---|---|---|---|
| 1 Protokoły | protokół odbioru etapu / robót (z podpisami), protokoły prób i pomiarów | `Umowy/Protokoły/` | bez protokołu nie ma podstawy do płatności dla ekipy (`koszty` D.1) |
| 2 Faktury | faktury i rachunki za etap (materiał, ekipa), potwierdzenia płatności | `Faktury/RRRR/` | nazwa pliku zaczyna się od daty wystawienia; skrypt wybiera po dacie |
| 3 Wpisy kierownika | wpisy kierownika budowy w dzienniku budowy – stan zaawansowania, odbiory przed zakryciem | `Dziennik budowy KB/` | banki często opierają transzę na wpisie o stopniu zaawansowania |
| 4 Dostawy | WZ betonu, atesty stali, deklaracje i karty produktów | `Dostawy/<Etap>/` | folder o nazwie etapu z Harmonogramu |
| 5 Dodatkowe | to, co bank wskaże poza standardem (np. oświadczenie, wniosek, kosztorys etapu) | `--dodaj <ścieżka>` | wniosek o transzę zwykle wypełnia inwestor na druku banku |
| spis → Zdjęcia | zdjęcia kroków i „przed zakryciem” | linki folderów na Dysku (pole „Zdjęcia” kroku w Harmonogramie) | pliki nie są kopiowane |

Poza teczką, a zwykle wymagane przez bank (sprawdź w umowie): wizja lokalna / kontrola banku (termin ustala się z bankiem,
nie z teczki), ubezpieczenie budowy, dokumenty własności i pozwolenie na budowę (są w folderze budowy od początku),
harmonogram rzeczowo-finansowy (Harmonogram w Notion, `harmonogram`), stan kosztorysu (arkusz, Podsumowanie – `koszty`).

## Forma: folder czy jeden PDF

Domyślnie **folder** ze spisem (można go wgrać na Dysk i wysłać link albo spakować). Jeden PDF – tylko gdy bank wprost nie
przyjmie folderu ani linku; wtedy scal działy 1–4 w kolejności spisu drukiem do PDF w Finderze
(skrypt PDF nie składa – założenie z 11.11.2026, bo wymóg banku jest nieznany).

## Gdzie teczka leży

`Teczki/` jest pochodna (kopia plików z innych folderów) – nie wchodzi do kopii na Dysk (`tools/kopia.py` nie ma jej na liście
dozwolonych) ani do indeksu `dokumenty.py`. Potrzebna na Dysku, np. do wysłania linku → wgraj folder ręcznie do `Dom/Teczki` (Dysk w przeglądarce).
