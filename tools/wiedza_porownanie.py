#!/usr/bin/env python3
"""Porównanie „pytanie → indeks → Notion” do ręcznego przejrzenia – `python3 tools/wiedza_jakosc.py pokaz` (ładowany
tylko przez to polecenie; hook startu i pozostałe polecenia go nie importują).

Buduje LOKALNY plik `jakosc/porownanie-RRRRMMDD-GGMM.html` (600, obok indeksu, nigdy w repo) dla próbki pytań
wymyślonych (ta sama co `sedzia --pytania N`): (A) pierwsze --top wyników `szukaj`, (B) wyniki publicznego API Notion
(klasa Notion z wiedza_jakosc: filtr `contains`, AND słów, przy zerze OR – bez rankingu i bez semantyki wyszukiwarki
MCP), posortowane po numerze WI malejąco. Pola: teza, szczegóły, tematy, etap – „Kto”, „Z kim” i tytułów źródeł kod
nie czyta. Oceny 0/1/2 z pamięci sędziego (`jakosc/sedzia.json`, klucz jak w `sedzia` – wiersz wspólny z indeksem
nie jest oceniany drugi raz). Treść jest w pliku (escapowana), który otwiera inwestor; wyjście programu (także
--json): liczby, ID pytań i ścieżka pliku.

--ocen-notion --wyslij: nieocenione wiersze Notion idą do modelu tą samą ścieżką co w `sedzia` (filtr danych
osobowych na każdym polu, na całości i na dokładnie wysyłanej paczce, kanarek, pamięć ocen, blokada sędziego). Bez
tego nic nie jest wysyłane do żadnego modelu. Notion: tylko odczyt (jeden GET schematu i POST …/query), najwyżej
--budzet żądań, token z sekrety.env nigdy nie drukowany, błędy tylko jako status HTTP.
"""
import contextlib
import html
import sys

import wiedza as W
import wiedza_sedzia as S

PREFIKS = "porownanie-"
BUDZET_MIN = 10
OCENY = {2: "2 – odpowiada", 1: "1 – częściowo", 0: "0 – nie odpowiada"}
NIE_WYSYLANY = "odfiltrowany (nie wysyłany do modelu)"
WYNIKI = {"indeks": "indeks lepszy", "notion": "Notion lepszy", "remis": "remis", "nieporownywalne": "nieporównywalne"}


def sprawdz_opcje(a):
    if a.ocen_notion != a.wyslij:
        raise S.BladSedziego("--ocen-notion i --wyslij tylko razem (ocena wierszy Notion przez model, po zgodzie "
                             "inwestora); bez nich pokaz niczego nie wysyła do modelu")
    S.sprawdz_opcje(a)
    if a.budzet < BUDZET_MIN:
        raise S.BladSedziego(f"--budzet: co najmniej {BUDZET_MIN} żądań")


# ------------------------------------------------------------------ Notion (tylko odczyt, budżet)
def opis_bledu_notion(e) -> str:
    """Tylko status – komunikat Notion potrafi powtórzyć wartości filtra (słowa pytania)."""
    return f"HTTP {e.status}" if isinstance(e, W.BladHttp) else "błąd sieci"


def zapytaj_notion(J, token: str, budzet: int, pytania: list) -> tuple:
    """({ID: {"zbior", "tryb"} albo {"blad"}}, licznik żądań)."""
    licznik = J.LicznikZadan(W.OTWIERACZ, budzet)
    wyniki = {}
    W.OTWIERACZ = licznik
    try:
        try:
            notion = J.Notion(token)
        except (W.BladHttp, W.BladSieci) as e:
            raise J.BladJakosci("Notion (schemat bazy Informacji): " + opis_bledu_notion(e)) from None
        for qid, _, q, _ in pytania:
            if licznik.budzet - licznik.zadan < J.NOTION_REZERWA:
                wyniki[qid] = {"blad": "budżet"}
                continue
            try:
                zbior, tryb = notion.szukaj(q)
                wyniki[qid] = {"zbior": zbior, "tryb": tryb}
            except J.BudzetWyczerpany:
                wyniki[qid] = {"blad": "budżet"}
            except (W.BladHttp, W.BladSieci) as e:
                wyniki[qid] = {"blad": opis_bledu_notion(e)}
    finally:
        W.OTWIERACZ = licznik.otwieracz
    return wyniki, licznik


# ------------------------------------------------------------------ plan: wiersze obu list
def wiersze(conn, qid, wq, lista, filtr, pred, q_czyste: bool) -> list:
    """Wiersze planu (S.wiersz_planu – ten sam klucz pamięci co sedzia) z treścią do pliku lokalnego. klucz_oceny
    służy tylko odczytowi pamięci i nie znika przy odfiltrowaniu całości (wiersz wspólny pokazuje ocenę z sedzia)."""
    wynik = []
    for poz, wi in enumerate(lista, 1):
        w, tresc = S.wiersz_planu(conn, qid, wq, poz, wi, [], filtr, pred)
        w.update(tresc=tresc, klucz_oceny=w["klucz"], pytanie_odfiltrowane=not q_czyste)
        if not q_czyste:
            w["wiersz"] = w["klucz"] = None
        wynik.append(w)
    return wynik


def zbuduj(J, conn, a, pytania: list, notion: dict, filtr) -> list:
    K = J.Korpus(conn)
    plan = []
    with J.szybka_normalizacja():
        for qid, zestaw, q, wzory in pytania:
            wq = S.normalizuj_tekst(q)
            czyste, pred = filtr.czysty(wq), K.predykat(wzory)
            nt = notion.get(qid, {"blad": "budżet"})
            p = {"id": qid, "zestaw": zestaw, "q": q, "q_wysylane": wq, "odfiltrowane": not czyste, "notion": nt,
                 "indeks": wiersze(conn, qid, wq, J.szukaj_listy(conn, q)[:a.top], filtr, pred, czyste)}
            widoczne = sorted((x for x in nt.get("zbior", ()) if K.widoczny.get(x)), reverse=True)
            nt["widocznych"], nt["pominiete"] = len(widoczne), len(nt.get("zbior", ())) - len(widoczne)
            nt["wspolne"] = {w["wi"] for w in p["indeks"]} & set(widoczne)
            p["wiersze"] = wiersze(conn, qid, wq, widoczne[:a.top], filtr, pred, czyste)   # plan wysyłki = Notion
            S.odfiltruj_calosc(p, filtr)
            plan.append(p)
    return plan


def odfiltruj_paczki(plan: list, pamiec: dict, model: str, filtr) -> int:
    """Dokładnie to, co pójdzie (nieocenione wiersze pytania), jeszcze raz przez filtr – inaczej paczka odpada."""
    n = 0
    for p, b in S.do_wyslania(plan, pamiec, model):
        if not filtr.czysty(S.tresc_zapytania(p["q_wysylane"], [w["wiersz"] for w in b])):
            for w in b:
                w["wiersz"] = w["klucz"] = None
            n += len(b)
    return n


# ------------------------------------------------------------------ oceny i liczby
def ocena(w: dict, pamiec: dict, model: str):
    if w["klucz_oceny"] is None or w["pytanie_odfiltrowane"]:
        return None
    o = pamiec["oceny"].get(S.klucz({"klucz": w["klucz_oceny"]}, model))
    return o[0] if o else None


def stan_wiersza(w: dict, pamiec: dict, model: str):
    """0/1/2, "odfiltrowany" albo "nieoceniony"."""
    o = ocena(w, pamiec, model)
    if o is not None:
        return o
    return "odfiltrowany" if w["wiersz"] is None else "nieoceniony"


def statystyki(lista: list, pamiec: dict, model: str) -> dict:
    stany = [stan_wiersza(w, pamiec, model) for w in lista]
    oc = [s for s in stany if isinstance(s, int)]
    return {"wierszy": len(stany), "ocenionych": len(oc), "nieocenionych": stany.count("nieoceniony"),
            "odfiltrowanych": stany.count("odfiltrowany"), "dwojek": oc.count(2), "lagodnych": sum(s >= 1 for s in oc)}


def dwojki(s: dict):
    """Do werdyktu pytania: liczba ocen 2 wśród pokazanych (klasyczne P@top – ten sam mianownik dla obu list, krótka
    lista Notion nie wygrywa samą długością). Tylko lista w całości oceniona; pusta = 0; same odfiltrowane = None."""
    if s["nieocenionych"] or (s["wierszy"] and not s["ocenionych"]):
        return None
    return s["dwojek"]


def wynik_pytania(si: dict, sn: dict, notion_ok: bool) -> str:
    pi, pn = dwojki(si), dwojki(sn) if notion_ok else None
    if pi is None or pn is None:
        return "nieporownywalne"
    return "indeks" if pi > pn else "notion" if pn > pi else "remis"


def proc(licznik: int, mianownik: int):
    return round(100 * licznik / mianownik, 1) if mianownik else None


def liczby(plan: list, pamiec: dict, model: str) -> tuple:
    """(podsumowanie, [liczby na pytanie]) – tylko liczby i ID pytań."""
    na_pytanie, suma = [], {"indeks": [], "notion": []}
    for p in plan:
        nt = p["notion"]
        si, sn = statystyki(p["indeks"], pamiec, model), statystyki(p["wiersze"], pamiec, model)
        suma["indeks"].append(si)
        suma["notion"].append(sn)
        r = {"id": p["id"], "odfiltrowane": p["odfiltrowane"], "notion_tryb": nt.get("tryb"),
             "notion_blad": nt.get("blad"), "notion_trafien": len(nt.get("zbior", ())),
             "notion_widocznych": nt["widocznych"], "notion_pominiete": nt["pominiete"], "wspolne": len(nt["wspolne"]),
             "notion_w_indeksie": "blad" not in nt and nt["widocznych"] == len(nt["wspolne"]),
             "wynik": wynik_pytania(si, sn, "blad" not in nt)}
        for nazwa, s in (("indeks", si), ("notion", sn)):
            r.update({f"{nazwa}_{k}": s[k] for k in ("wierszy", "ocenionych", "nieocenionych", "odfiltrowanych")})
            r[f"{nazwa}_p_scisle"], r[f"{nazwa}_p_lagodne"] = (proc(s["dwojek"], s["ocenionych"]),
                                                               proc(s["lagodnych"], s["ocenionych"]))
        na_pytanie.append(r)
    pod = {"pytan": len(plan), "pytan_odfiltrowanych": sum(p["odfiltrowane"] for p in plan),
           "notion_trafien": sum(r["notion_trafien"] for r in na_pytanie),
           "notion_pominiete": sum(r["notion_pominiete"] for r in na_pytanie),
           "notion_zero": sum(1 for r in na_pytanie if not r["notion_blad"] and r["notion_trafien"] == 0),
           "notion_nieukonczone": sum(1 for r in na_pytanie if r["notion_blad"]),
           "notion_or": sum(1 for r in na_pytanie if r["notion_tryb"] == "OR"),
           "wspolne": sum(r["wspolne"] for r in na_pytanie),
           "notion_w_indeksie": sum(r["notion_w_indeksie"] for r in na_pytanie)}
    for nazwa, lista in suma.items():
        razem = {k: sum(s[k] for s in lista) for k in ("ocenionych", "nieocenionych", "odfiltrowanych", "dwojek",
                                                        "lagodnych")}
        pod.update({f"{nazwa}_{k}": razem[k] for k in ("ocenionych", "nieocenionych", "odfiltrowanych")})
        pod[f"{nazwa}_p_scisle"] = proc(razem["dwojek"], razem["ocenionych"])
        pod[f"{nazwa}_p_lagodne"] = proc(razem["lagodnych"], razem["ocenionych"])
    for k in ("indeks", "notion", "remis", "nieporownywalne"):
        pod[k + ("_lepszy" if k in ("indeks", "notion") else "")] = sum(r["wynik"] == k for r in na_pytanie)
    return pod, na_pytanie


def do_oceny(plan: list, pamiec: dict, model: str) -> dict:
    wyslac = S.do_wyslania(plan, pamiec, model)
    return {"do_oceny_wierszy": sum(len(b) for _, b in wyslac), "do_oceny_wywolan": len(wyslac),
            "do_oceny_znakow": sum(len(S.SYSTEM) + len(S.tresc_zapytania(p["q_wysylane"], [w["wiersz"] for w in b]))
                                   for p, b in wyslac)}


# ------------------------------------------------------------------ HTML (lokalny, treść escapowana)
CSS = """
:root{--tlo:#fbfbfa;--karta:#fff;--tekst:#1d1d1f;--slaby:#5f6368;--ramka:#dcdcdc;--wsp:#e6f0ff;--wsp-r:#3a6fd8;
--o2:#1e7d32;--o1:#9a6700;--o0:#b3261e;--nie:#6b6b6b;--filtr:#7b3fa0}
@media (prefers-color-scheme:dark){:root{--tlo:#141416;--karta:#1d1d20;--tekst:#e8e8ea;--slaby:#a0a0a8;
--ramka:#3a3a40;--wsp:#1c2a44;--wsp-r:#7aa2f7;--o2:#6fcf7a;--o1:#e3b341;--o0:#f28b82;--nie:#9a9aa2;--filtr:#c69bf0}}
*{box-sizing:border-box}
body{margin:0;background:var(--tlo);color:var(--tekst);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",
Roboto,sans-serif;overflow-wrap:anywhere}
.strona{max-width:960px;margin:0 auto;padding:16px}
h1{font-size:1.4em;margin:.2em 0}h2{font-size:1.15em;margin:1.2em 0 .4em}h3{font-size:1em;margin:.8em 0 .3em}
.slaby,.stat{color:var(--slaby);font-size:.9em}
table{border-collapse:collapse;width:100%;font-size:.9em}td,th{border-bottom:1px solid var(--ramka);padding:4px 6px;
text-align:left}
details{background:var(--karta);border:1px solid var(--ramka);border-radius:8px;margin:10px 0;padding:6px 10px}
summary{cursor:pointer;font-weight:600}summary .liczby{display:block;font-weight:400;color:var(--slaby);font-size:.85em}
ol{list-style:none;padding:0;margin:0}
li{border:1px solid var(--ramka);border-radius:6px;padding:6px 8px;margin:6px 0}
li.wspolny{background:var(--wsp);border-left:4px solid var(--wsp-r)}
.meta{font-size:.85em;color:var(--slaby)}.meta span{margin-right:8px}
.o2{color:var(--o2);font-weight:600}.o1{color:var(--o1);font-weight:600}.o0{color:var(--o0);font-weight:600}
.nie{color:var(--nie)}.filtr{color:var(--filtr);font-weight:600}.etykieta{color:var(--wsp-r);font-weight:600}
.teza{margin:.2em 0;font-weight:600}.szcz{margin:.2em 0;white-space:pre-wrap}.dod{margin:.2em 0;font-size:.85em;
color:var(--slaby)}
"""


def e(x) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def pr(x) -> str:
    return "–" if x is None else f"{x:.1f}%"


def html_wiersza(w: dict, stan, etykieta: str) -> str:
    if isinstance(stan, int):
        oc = f'<span class="o{stan}">ocena {e(OCENY[stan])}</span>'
    elif stan == "odfiltrowany":
        oc = '<span class="filtr">' + e(NIE_WYSYLANY + (" – pytanie" if w["pytanie_odfiltrowane"] else "")) + "</span>"
    else:
        oc = '<span class="nie">nie oceniono</span>'
    t = w["tresc"]
    dod = " · ".join(x for x in (f"Tematy: {e(t['tematy'])}" if t.get("tematy") else "",
                                 f"Etap: {e(t['etap'])}" if t.get("etap") else "") if x)
    return (f'<li class="{"wspolny" if etykieta else "zwykly"}"><div class="meta"><span>#{w["ranga"]}</span>'
            f'<span>WI-{w["wi"]}</span>{oc}<span>predykat słów {"✓" if w["pred"] else "✗"}</span>'
            + (f'<span class="etykieta">{e(etykieta)}</span>' if etykieta else "") + "</div>"
            f'<p class="teza">{e(t.get("teza"))}</p>' + (f'<p class="szcz">{e(t["szczegoly"])}</p>'
                                                          if t.get("szczegoly") else "")
            + (f'<p class="dod">{dod}</p>' if dod else "") + "</li>")


def html_pytania(p: dict, r: dict, pamiec: dict, model: str, top: int) -> str:
    nt = p["notion"]
    rangi = {w["wi"]: w["ranga"] for w in p["indeks"]}
    if "blad" in nt:
        opis_nt = f"Notion: nie zapytano ({e(nt['blad'])})"
    else:
        opis_nt = (f"Notion: {r['notion_trafien']} trafień ({e(nt['tryb'])}), widocznych {r['notion_widocznych']}, "
                   f"pominiętych {r['notion_pominiete']}")
    liczby_q = (f"{opis_nt} · wspólne {r['wspolne']} · P@{top} ścisłe: indeks {pr(r['indeks_p_scisle'])}, Notion "
                f"{pr(r['notion_p_scisle'])} · nieocenione: indeks {r['indeks_nieocenionych']}, Notion "
                f"{r['notion_nieocenionych']} · wynik: {e(WYNIKI[r['wynik']])}")
    czesci = [f'<details><summary>{e(p["id"])} · {e(p["q"])}<span class="liczby">{liczby_q}</span></summary>']
    if p["odfiltrowane"]:
        czesci.append('<p class="filtr">Pytanie albo całość wierszy Notion odfiltrowane – nic z tego pytania nie idzie '
                      'do modelu.</p>')
    for tytul, lista, nazwa, etyk in (
            (f"A. Indeks – pierwsze {top} wyników szukaj", p["indeks"], "indeks",
             lambda w: "wspólny – też w Notion" if w["wi"] in nt["wspolne"] else ""),
            ("B. Notion (API, przybliżenie) – WI malejąco, bez rankingu", p["wiersze"], "notion",
             lambda w: f"wspólny – w indeksie #{rangi[w['wi']]}" if w["wi"] in nt["wspolne"] else "")):
        czesci.append(f"<section><h3>{e(tytul)}</h3><p class=\"stat\">wierszy {r[nazwa + '_wierszy']}, ocenionych "
                      f"{r[nazwa + '_ocenionych']}, nieocenionych {r[nazwa + '_nieocenionych']}, odfiltrowanych "
                      f"{r[nazwa + '_odfiltrowanych']} · P@{top} ścisłe {pr(r[nazwa + '_p_scisle'])}, łagodne "
                      f"{pr(r[nazwa + '_p_lagodne'])}"
                      + (f" · tryb {e(nt.get('tryb'))}, trafień {r['notion_trafien']}, pominiętych "
                         f"{r['notion_pominiete']}" if nazwa == "notion" and "blad" not in nt else "") + "</p>")
        if lista:
            czesci.append("<ol>" + "".join(html_wiersza(w, stan_wiersza(w, pamiec, model), etyk(w))
                                           for w in lista) + "</ol>")
        else:
            czesci.append('<p class="slaby">brak wierszy</p>')
        czesci.append("</section>")
    czesci.append("</details>")
    return "".join(czesci)


def legenda(top: int, model: str) -> list:
    return [
        "Porównanie jest przybliżeniem: lista B to publiczne API Notion – filtr „contains” na tezie, szczegółach "
        "i „dla naszej budowy” (AND słów pytania, przy zerze OR), bez rankingu i bez semantyki wyszukiwarki Notion MCP.",
        f"API nie zwraca rankingu: lista Notion jest posortowana po numerze WI malejąco (najnowsze pierwsze) "
        f"i obcięta do {top}; „#” na liście B to pozycja na tej liście, nie ranga.",
        "Wiersze Notion spoza widocznych w indeksie (Nieaktualne, Ciekawostka, brak w indeksie) są pominięte – liczy je "
        "„pominiętych”.",
        f"Ocena sędziego z pamięci ocen (model {model}): 2 – odpowiada, 1 – częściowo, 0 – nie; „nie oceniono” – brak "
        "oceny w pamięci; „" + NIE_WYSYLANY + "” – trafienie filtra danych osobowych (pokazany, bo plik jest lokalny).",
        f"„wspólny” (tło i etykieta) – wiersz jest w pierwszych {top} indeksu i w wynikach Notion (wszystkich "
        "widocznych, nie tylko pokazanych).",
        "„predykat słów” – automatyczna trafność z wzorców pytania (jak w zloty): przybliżenie, ślepe na sens.",
        f"P@{top} ścisłe = oceny 2 / ocenione wiersze; łagodne = oceny ≥ 1 / ocenione; odfiltrowane poza "
        f"mianownikiem. Werdykt pytania (lepszy / remis): liczba ocen 2 wśród pokazanych, czyli klasyczne P@{top} "
        "z tym samym mianownikiem – krótka lista Notion nie wygrywa samą długością; tylko gdy obie listy są "
        "w całości ocenione (udane zapytanie Notion bez trafień = 0), inaczej „nieporównywalne”.",
        "„Notion ⊂ indeks” – pytania, w których wszystkie widoczne wyniki Notion są też w wynikach indeksu.",
        "Plik zawiera treść bazy: tylko do przejrzenia na tym komputerze – nie wysyłaj go i nie wklejaj do czatu z AI."]


def zbuduj_html(plan: list, pod: dict, na_pytanie: list, pamiec: dict, a, data: str, zadan: int) -> str:
    wiersze_pod = [
        ("Pytań", f"{pod['pytan']} (odfiltrowanych {pod['pytan_odfiltrowanych']})"),
        ("Żądań do Notion", f"{zadan}/{a.budzet} (pytań nieukończonych {pod['notion_nieukonczone']})"),
        ("Trafień Notion", f"{pod['notion_trafien']} (pominiętych {pod['notion_pominiete']}; pytań z 0 trafień "
                           f"{pod['notion_zero']}; tryb OR {pod['notion_or']})"),
        ("Wspólne wiersze", f"{pod['wspolne']} (pytań Notion ⊂ indeks {pod['notion_w_indeksie']})")]
    for nazwa, etyk in (("indeks", "Indeks"), ("notion", "Notion")):
        wiersze_pod.append((f"{etyk}: P@{a.top} ścisłe / łagodne",
                            f"{pr(pod[nazwa + '_p_scisle'])} / {pr(pod[nazwa + '_p_lagodne'])} (ocenionych "
                            f"{pod[nazwa + '_ocenionych']}, nieocenionych {pod[nazwa + '_nieocenionych']}, "
                            f"odfiltrowanych {pod[nazwa + '_odfiltrowanych']})"))
    wiersze_pod.append((f"Werdykt (oceny 2 w {a.top})", f"indeks lepszy {pod['indeks_lepszy']} · Notion lepszy "
                                         f"{pod['notion_lepszy']} · remis {pod['remis']} · nieporównywalne "
                                         f"{pod['nieporownywalne']}"))
    tabela = "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in wiersze_pod)
    return ("<!doctype html><html lang=\"pl\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'unsafe-inline'\">"
            "<meta name=\"referrer\" content=\"no-referrer\"><meta name=\"robots\" content=\"noindex\">"
            f"<title>Porównanie indeks–Notion {e(data)}</title><style>{CSS}</style></head><body>"
            "<div class=\"strona\"><header><h1>Porównanie: indeks wiedzy vs Notion</h1>"
            f"<p class=\"slaby\">{e(data)} · model sędziego {e(a.model)} · pytań {pod['pytan']} · pierwszych "
            f"{a.top} wyników</p><table>{tabela}</table><h2>Legenda</h2><ul>"
            + "".join(f"<li class=\"zwykly\">{e(x)}</li>" for x in legenda(a.top, a.model))
            + "</ul></header><main><h2>Pytania</h2>"
            + "".join(html_pytania(p, r, pamiec, a.model, a.top) for p, r in zip(plan, na_pytanie))
            + "</main></div></body></html>\n")


# ------------------------------------------------------------------ wyjście (tylko liczby i ścieżka)
def opis(pod: dict, na_pytanie: list, plik, top: int, zadan: int, budzet: int) -> list:
    linie = [f"[jakosc] porównanie indeks vs Notion – przybliżenie (API Notion: filtr „contains” bez rankingu i bez "
             f"semantyki wyszukiwarki MCP); plik lokalny: {plik}",
             f"  pytań {pod['pytan']} (odfiltrowanych {pod['pytan_odfiltrowanych']}) · żądań do Notion {zadan}/"
             f"{budzet} (pytań nieukończonych {pod['notion_nieukonczone']}) · trafień Notion {pod['notion_trafien']} "
             f"(pominiętych {pod['notion_pominiete']}, pytań z 0 trafień {pod['notion_zero']}, tryb OR "
             f"{pod['notion_or']}) · wspólne {pod['wspolne']} (pytań Notion ⊂ indeks {pod['notion_w_indeksie']})"]
    for nazwa, etyk in (("indeks", "indeks"), ("notion", "Notion")):
        linie.append(f"  {etyk}: P@{top} ścisłe {pr(pod[nazwa + '_p_scisle'])} · łagodne "
                     f"{pr(pod[nazwa + '_p_lagodne'])} (ocenionych {pod[nazwa + '_ocenionych']}, nieocenionych "
                     f"{pod[nazwa + '_nieocenionych']}, odfiltrowanych {pod[nazwa + '_odfiltrowanych']})")
    linie.append(f"  werdykt wg ocen 2 w pierwszych {top} (klasyczne P@{top}): indeks lepszy {pod['indeks_lepszy']}"
                 f" · Notion lepszy {pod['notion_lepszy']} · remis {pod['remis']} · nieporównywalne "
                 f"{pod['nieporownywalne']}")
    linie.append(f"  do oceny przez model (wiersze Notion bez oceny): wierszy {pod['do_oceny_wierszy']}, znaków "
                 f"{pod['do_oceny_znakow']}, wywołań {pod['do_oceny_wywolan']}")
    for r in na_pytanie:
        nt = r["notion_blad"] or f"{r['notion_trafien']} ({r['notion_tryb']})"
        linie.append(f"    {r['id']}: Notion {nt}, wspólne {r['wspolne']} · P ścisłe/łagodne indeks "
                     f"{pr(r['indeks_p_scisle'])}/{pr(r['indeks_p_lagodne'])}, Notion {pr(r['notion_p_scisle'])}/"
                     f"{pr(r['notion_p_lagodne'])} · nieocenione {r['indeks_nieocenionych']}/"
                     f"{r['notion_nieocenionych']} → {WYNIKI[r['wynik']]}")
    return linie


# ------------------------------------------------------------------ polecenie
def cmd_pokaz(a, J) -> int:
    try:
        return przebieg(a, J)
    except (S.BladSedziego, J.BladJakosci) as e:
        if a.json:   # komunikaty to stałe teksty bez treści wierszy
            W.wypisz_json({"blad": "odmowa", "komunikat": str(e)})
            return 1
        raise J.BladJakosci(str(e)) from None
    except KeyboardInterrupt:
        if a.json:
            W.wypisz_json({"blad": "przerwane"})
        else:
            print("[jakosc] pokaz: przerwano – zapisane oceny zostają w pamięci, pliku nie zapisano")
        return 130


def przebieg(a, J) -> int:
    sprawdz_opcje(a)
    m = J.Miejsca(a)
    m.przygotuj()
    filtr = S.Filtr(S.plik_listy(m))
    polecenie = S.wymagania_wysylki(m, filtr) if a.wyslij else None
    ostrzezenia = []
    with contextlib.ExitStack() as stos:
        if a.wyslij:   # blokada przed wczytaniem pamięci: równoległy sedzia nie straci ocen
            if not stos.enter_context(J.blokada_przebiegu(m, S.BLOKADA)):
                raise S.BladSedziego("trwa inny przebieg sędziego – spróbuj za chwilę")
        with contextlib.redirect_stdout(sys.stderr if a.json else sys.stdout):
            token = W.wczytaj_sekrety(W.SEKRETY).get("NOTION_TOKEN")
        if not token:
            raise J.BladJakosci("brak NOTION_TOKEN w sekrety.env – porównanie z Notion niemożliwe")
        with contextlib.closing(W.otworz_db(m.baza, zapis=False)) as conn:
            pytania = S.pytania_proby(J, m, a.pytania, ostrzezenia)
            notion, licznik = zapytaj_notion(J, token, a.budzet, pytania)
            plan = zbuduj(J, conn, a, pytania, notion, filtr)
        pamiec = S.wczytaj_pamiec(J, m, ostrzezenia)
        odfiltruj_paczki(plan, pamiec, a.model, filtr)
        if not a.json:
            for o in ostrzezenia:
                W.ostrzez(o)
        stan, stat = "na_sucho", None
        if a.wyslij:
            d = do_oceny(plan, pamiec, a.model)
            if not a.json:
                print(f"[jakosc] pokaz: do wysłania wierszy Notion {d['do_oceny_wierszy']}, znaków "
                      f"{d['do_oceny_znakow']}, wywołań {d['do_oceny_wywolan']} (+ kanarek) · model {a.model}",
                      flush=True)
            stan, stat = S.wyslij_plan(J, m, a, plan, pamiec, polecenie)
        pod, na_pytanie = liczby(plan, pamiec, a.model)
        pod.update(do_oceny(plan, pamiec, a.model), notion_zadan=licznik.zadan, notion_budzet=a.budzet,
                   model=a.model, top=a.top)
        data = J.teraz().astimezone()
        plik = m.dane / f"{PREFIKS}{data:%Y%m%d-%H%M}.html"
        J.zapisz_plik(plik, zbuduj_html(plan, pod, na_pytanie, pamiec, a, f"{data:%Y-%m-%d %H:%M}", licznik.zadan))
        J.zaostrz(m.dane)
    if a.json:
        W.wypisz_json({"plik": str(plik), "na_sucho": not a.wyslij, "stan": stan, "podsumowanie": pod,
                       "pytania": na_pytanie, "wywolan": stat["wywolan"] if stat else 0,
                       "bledy_wywolan": stat["bledy"] if stat else {}, "ostrzezenia": ostrzezenia})
    else:
        print("\n".join(opis(pod, na_pytanie, plik, a.top, licznik.zadan, a.budzet)))
        if stat:
            print(f"  wysłano: wywołań {stat['wywolan']} (+ kanarek)" + (
                "" if stan == "ok" else f" – {S.POWODY[stan]}; oceny zapisane zostają w pamięci, uruchom ponownie"))
            S.wypisz_bledy(stat)
        else:
            print("  na sucho – nic nie wysłano do modelu; ocena wierszy Notion: pokaz --ocen-notion --wyslij (po "
                  "zgodzie inwestora); wiersze indeksu: sedzia --wyslij (te same --pytania)")
    return 0 if stan in ("ok", "na_sucho") else 130 if stan == "przerwane" else 1
