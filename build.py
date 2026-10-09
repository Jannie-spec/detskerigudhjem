"""Bygger detskerigudhjem.dk som én statisk side (site/index.html).

Data hentes fra Klippens gæste-app (https://therns.dk/app/gudhjem.json), som hver nat samler:
Klippens egne steder og events, film i Scala, svømmehallens kalender, byens arrangementer
(kirke, museer m.m.) og åbningstider for spisesteder. Køres af GitHub Actions hver nat.
"""
import shutil
import json, html, datetime, urllib.request, pathlib, re
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent
SRC = "https://therns.dk/app/gudhjem.json"
TZ = ZoneInfo("Europe/Copenhagen")
DAYS = 7
LATER_DAYS = 366   # "Længere frem": et år frem, grupperet pr. måned
BOOK = "https://www.hotelklippen.com"
E = lambda s: html.escape(str(s or ""), quote=True)
WD = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
WD_SHORT = ["man", "tir", "ons", "tor", "fre", "lør", "søn"]
MON = ["januar", "februar", "marts", "april", "maj", "juni", "juli", "august", "september", "oktober", "november", "december"]
MUSEUMS = ["kunst", "host", "gmus", "melg"]
LANGS = ["da", "en", "de", "sv"]
LANG = "da"
DTR = {}   # appens oversættelser (fra gudhjem.json)
DAYNAMES = {
    "da": (WD, WD_SHORT, MON),
    "en": (["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], ["January","February","March","April","May","June","July","August","September","October","November","December"]),
    "de": (["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"], ["Mo","Di","Mi","Do","Fr","Sa","So"], ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]),
    "sv": (["måndag","tisdag","onsdag","torsdag","fredag","lördag","söndag"], ["mån","tis","ons","tor","fre","lör","sön"], ["januari","februari","mars","april","maj","juni","juli","augusti","september","oktober","november","december"]),
}
# sidens egne tekster [en, de, sv]
U = {
    "Hele dagen": ["All day", "Ganztägig", "Hela dagen"],
    "Familiesvømning med vipper og legeredskaber": ["Family swim with diving boards and toys", "Familienschwimmen mit Sprungbrettern und Spielgeräten", "Familjesim med trampoliner och lekredskap"],
    "Svømmehallen": ["Swimming pool", "Schwimmhalle", "Simhallen"],
    "Lukket": ["Closed", "Geschlossen", "Stängt"],
    "Åbent denne dag": ["Open this day", "An diesem Tag geöffnet", "Öppet denna dag"],
    "Spisesteder, barer og is, der har åbent": ["Restaurants, bars and ice cream – open", "Geöffnete Restaurants, Bars und Eisdielen", "Matställen, barer och glass som har öppet"],
    "Ingen arrangementer i kalenderen endnu.": ["Nothing in the calendar yet.", "Noch nichts im Kalender.", "Inget i kalendern ännu."],
    "Hos Klippen": ["At Klippen", "Bei Klippen", "Hos Klippen"],
    "I dag": ["Today", "Heute", "I dag"], "I morgen": ["Tomorrow", "Morgen", "I morgon"],
    "Kunstmuseet": ["Art Museum", "Kunstmuseum", "Konstmuseet"],
    "Film": ["Film", "Film", "Film"], "Svømning": ["Swimming", "Schwimmen", "Simning"], "Kirke": ["Church", "Kirche", "Kyrka"],
    "Musik": ["Music", "Musik", "Musik"], "Børn og familie": ["Children and family", "Kinder und Familie", "Barn och familj"],
    "Foredrag": ["Talk", "Vortrag", "Föredrag"], "Kunst og kultur": ["Art and culture", "Kunst und Kultur", "Konst och kultur"],
    "Mad og drikke": ["Food and drink", "Essen und Trinken", "Mat och dryck"], "Arrangement": ["Event", "Veranstaltung", "Evenemang"],
    "Biograf": ["Cinema", "Kino", "Bio"],
    "Længere frem": ["Coming up", "Demnächst", "Längre fram"],
    "Det, der allerede står i kalenderen det næste år. Der kommer flere arrangementer til løbende.": [
        "What is already in the calendar for the coming year. More events are added all the time.",
        "Was für das kommende Jahr schon im Kalender steht. Laufend kommen weitere Veranstaltungen dazu.",
        "Det som redan står i kalendern det kommande året. Fler evenemang tillkommer löpande."],
    "til": ["until", "bis", "till"],
    "Intet i kalenderen længere frem endnu.": ["Nothing further ahead in the calendar yet.", "Noch nichts Weiteres im Kalender.", "Inget längre fram i kalendern ännu."],
}

def L(s):
    """Oversæt en dansk tekst til sidens sprog (sidens egne tekster, ellers appens oversættelser)."""
    if LANG == "da" or not s:
        return s
    i = LANGS.index(LANG) - 1
    if s in U: return U[s][i]
    if s in DTR: return DTR[s][i]
    return s

def kl(t):
    return ("kl. " if LANG in ("da", "sv") else "") + hm(t) + (" Uhr" if LANG == "de" else "")

MUS_SHORT = {"kunst": "Kunstmuseet", "host": "Oluf Høst Museet", "gmus": "Gudhjem Museum", "melg": "Melstedgård"}


def load():
    cache = ROOT / "data.json"
    try:
        req = urllib.request.Request(SRC, headers={"User-Agent": "detskerigudhjem-build"})
        raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
        data = json.loads(raw)
        cache.write_text(raw, encoding="utf-8")
        return data
    except Exception as e:  # brug sidste gode udgave, hvis appen ikke svarer
        print("Kunne ikke hente data:", e)
        return json.loads(cache.read_text(encoding="utf-8"))


# ---------- tider ----------
def tmin(s):
    h, m = s.replace(".", ":").split(":")
    return int(h) * 60 + int(m)

def hm(s):
    s = s.replace(".", ":")
    h, m = s.split(":")
    if LANG in ("en", "de"):
        return f"{int(h)}:{m}"
    return str(int(h)) if m == "00" else f"{int(h)}.{m}"

def span(sl):
    return ", ".join(f"{hm(a)}–{hm(b)}" for a, b in sl)

def is_summer(d):
    return (d.month == 6 and d.day >= 27) or d.month == 7 or (d.month == 8 and d.day <= 9)

def slots_on(v, d):
    """Åbningstider for et sted (venue eller place) på dato d – samme regler som i gæste-appen."""
    if not v:
        return []
    if v.get("closedMonths") and d.month in v["closedMonths"]:
        return []
    sched = v.get("sched") or v.get("hours")
    if "seasons" in v:
        md = f"{d.month:02d}-{d.day:02d}"
        se = next((s for s in v["seasons"] if s["from"] <= md <= s["to"]), None)
        if not se:
            return []
        sched = se["hours"]
    if v.get("summer") and is_summer(d):
        return v["summer"]
    if not sched:
        return []
    wd = (d.weekday() + 1) % 7  # appen bruger 0 = søndag
    return sched.get("all") or sched.get(str(wd)) or []

def merge(sl):
    out = []
    for a, b in sorted(sl):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out

def open_within_week(p, today):
    for i in range(8):
        d = today + datetime.timedelta(days=i)
        if p.get("closedMonths"):
            if d.month not in p["closedMonths"]:
                return True
            continue
        if "seasons" not in p:
            return True
        md = f"{d.month:02d}-{d.day:02d}"
        if any(s["from"] <= md <= s["to"] for s in p["seasons"]):
            return True
    return False


# ---------- én dag ----------
def item(t_sort, time_txt, title, where, url=None, end=None, kind=""):
    return {"s": t_sort, "time": time_txt, "title": title, "where": where, "url": url, "end": end, "kind": kind}

def kind_of(e):
    t = " ".join([e.get("g", ""), e.get("title", ""), e.get("where", "")]).lower()
    for k, words in (("kirke", ("gudstjeneste", "kirke", "messe")), ("musik", ("musik", "koncert", "jazz", "sang")),
                     ("born", ("børn", "famili", "halloween", "karamel", "disco")), ("foredrag", ("foredrag", "rundvisning", "salon")),
                     ("kunst", ("kunst", "museum", "udstilling", "historisk", "melstedgård")), ("mad", ("gastronomi", "smagning", "middag"))):
        if any(w in t for w in words):
            return k
    return "andet"

def build_day(D, d, places):
    iso = d.isoformat()
    V = D["venues"]
    # Hos Klippen
    klippen = []
    for key, pid in (("plateau", "plat"), ("jylkat", "jyl")):
        v = V[key]; sl = slots_on(v, d)
        if sl:
            klippen.append({"name": L(v["name"]), "where": L(v["where"]), "hours": span(sl), "url": v.get("url"), "end": max(tmin(b) for _, b in sl),
                            "desc": L((next((q for q in D["places"] if q["id"] == pid), {}) or {}).get("desc") or v["where"])})
    own = []
    for e in sorted(D.get("events", []), key=lambda e: e.get("time") or ""):
        if e["date"] <= iso <= (e.get("to") or e["date"]):
            own.append({"title": L(e["title"]), "where": L(e.get("where", "")), "time": kl(e["time"]) if e.get("time") else "", "text": L(e.get("text", "")), "url": e.get("url")})
    # I byen: events, film, svømmehal-events
    items = []
    for e in D.get("town", []):
        if e.get("long") or not (e["d"] <= iso <= (e.get("to") or e["d"])):
            continue
        if e.get("wd") and ((d.weekday() + 1) % 7) not in e["wd"]:
            continue
        if e.get("t"):
            tt = hm(e["t"]) + (("–" + hm(e["t2"])) if e.get("t2") else "")
            items.append(item(tmin(e["t"]), tt, L(e["title"]), e.get("where", ""), e.get("rurl") or e.get("url"), tmin(e.get("t2") or e["t"]) + (0 if e.get("t2") else 90), kind_of(e)))
        else:
            items.append(item(-1, L("Hele dagen"), L(e["title"]), e.get("where", ""), e.get("rurl") or e.get("url"), None, kind_of(e)))
        items[-1]["reg"] = {1: L("Kræver tilmelding"), 2: L("Tilmelding til nogle aktiviteter"), 3: L("Billet på forhånd")}.get(e.get("reg"), "")
    for f in D.get("films", []):
        if f["d"] == iso:
            items.append(item(tmin(f["t"]), hm(f["t"]), f["title"], "Scala Gudhjem, " + L("Biograf").lower(), "http://www.scalagudhjem.dk/", tmin(f["t"]) + 30, "film"))
    pool_url = (places.get("svom") or {}).get("url")
    P = D.get("pool", [])
    pd = [x for x in P if x["d"] == iso] if P and iso <= P[-1]["d"] else None
    swim, pool_closed = None, False
    if pd is not None:
        if any(x["k"] == "x" for x in pd):
            pool_closed = True
        else:
            sl = merge([[x["a"], x["b"]] for x in pd if x["k"] in ("s", "f")])
            swim = span(sl) if sl else None
            for x in pd:
                if x["k"] == "f":
                    items.append(item(tmin(x["a"]), f"{hm(x['a'])}–{hm(x['b'])}", L("Familiesvømning med vipper og legeredskaber"), "Gudhjem Svømmehal", pool_url, tmin(x["b"]), "svom"))
                elif x["k"] == "e":
                    items.append(item(tmin(x["a"]), f"{hm(x['a'])}–{hm(x['b'])}", x.get("title", "Arrangement"), "Gudhjem Svømmehal", pool_url, tmin(x["b"]), "svom"))
    else:
        sl = slots_on(places.get("svom"), d)
        swim = span(sl) if sl else None
    items.sort(key=lambda x: (x["s"], x["title"]))
    # Åbent: museer + svømmehal
    # Førder: butik og reception
    rv = V.get("reception"); sl = slots_on(rv, d) if rv else []
    if sl:
        klippen.append({"name": "Førder", "where": L("Butik med bornholmske varer, tøj og gaver · reception for Klippen Hotel") + " · Brøddegade 28",
                        "hours": span(sl), "url": "https://foerder.dk/", "end": max(tmin(b) for _, b in sl), "desc": "", "shop": True})
    mus = []
    for mid in MUSEUMS:
        p = places.get(mid)
        sl = slots_on(p, d)
        if p and sl:
            mus.append({"name": L(MUS_SHORT[mid]), "hours": span(sl), "url": p.get("url")})
    # Spisesteder og is
    food = []
    for p in places.values():
        if p.get("cat") not in ("mad", "is") or p.get("hide") or p.get("ours") or p.get("venue") or p.get("far"):
            continue
        sl = slots_on(p, d)
        if sl:
            food.append({"name": p["name"], "hours": span(sl), "cat": p["cat"], "desc": L(p.get("desc", "")), "url": p.get("url")})
        elif not p.get("hours") and "seasons" not in p and p.get("label"):
            food.append({"name": p["name"], "hours": "", "cat": p["cat"], "desc": L(p.get("label", "")), "url": p.get("url")})
    food.sort(key=lambda f: (f["cat"] != "mad", f["name"]))
    # Klippens egne spisesteder/barer står også øverst i listen
    food = [{"name": k["name"], "hours": k["hours"], "cat": "mad", "desc": k["desc"], "url": k["url"], "ours": True} for k in klippen if not k.get("shop")] + food
    return {"iso": iso, "d": d, "klippen": klippen, "own": own, "items": items, "mus": mus, "swim": swim, "pool_closed": pool_closed, "pool_url": pool_url, "food": food}


# ---------- HTML ----------
ICON = {
    "film": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 5v14M17 5v14M3 9h4M3 15h4M17 9h4M17 15h4"/>',
    "svom": '<path d="M2 15c2 0 2-1.5 4-1.5S8 15 10 15s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><path d="M2 19c2 0 2-1.5 4-1.5S8 19 10 19s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><circle cx="15" cy="6" r="2"/><path d="M6 12l4-5 4 3"/>',
    "kirke": '<path d="M12 2v5M10 4h4"/><path d="M6 21V11l6-4 6 4v10"/><path d="M10 21v-4a2 2 0 0 1 4 0v4"/>',
    "musik": '<path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>',
    "born": '<circle cx="12" cy="8" r="5"/><path d="M12 13l-1 3h2l-1-3M12 16c0 2-2 3-2 5"/>',
    "foredrag": '<path d="M4 5h16v10H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
    "kunst": '<path d="M12 3a9 9 0 1 0 0 18c1.5 0 2-1 2-2s-1-1.5-1-2.5 1-1.5 2-1.5h2a4 4 0 0 0 4-4c0-4.4-4-8-9-8z"/><circle cx="7.5" cy="11" r="1"/><circle cx="10" cy="7" r="1"/><circle cx="15" cy="7" r="1"/>',
    "mad": '<path d="M7 3v8a2 2 0 0 0 4 0V3M9 11v10"/><path d="M17 3c-2 2-2 6 0 8v10"/>',
    "andet": '<path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z"/>',
}
KIND_LABEL = {"film": "Film", "svom": "Svømning", "kirke": "Kirke", "musik": "Musik", "born": "Børn og familie", "foredrag": "Foredrag", "kunst": "Kunst og kultur", "mad": "Mad og drikke", "andet": "Arrangement"}
BIRD = '<svg class="bird" viewBox="0 0 1140 520" aria-hidden="true"><polyline points="500,175 320,15 15,102 298,95 450,180 225,215 110,355 295,262 790,122 1120,405 785,205 555,218 795,420 930,460 805,495 690,393 365,277"/></svg>'

def icon(kind):
    return f'<span class="ic ic-{kind}" title="{E(L(KIND_LABEL.get(kind, "")))}"><svg viewBox="0 0 24 24" aria-hidden="true">{ICON.get(kind, ICON["andet"])}</svg></span>'

def link(text, url):
    return f'<a href="{E(url)}" rel="noopener">{E(text)}</a>' if url else E(text)

def render_day(x, i):
    d = x["d"]
    wd_, wds_, mon_ = DAYNAMES[LANG]
    rel = L("I dag") if i == 0 else L("I morgen") if i == 1 else wd_[d.weekday()].capitalize()
    datetxt = f"{wd_[d.weekday()]}, {mon_[d.month - 1]} {d.day}" if LANG == "en" else f"{wd_[d.weekday()]}, {d.day}. {mon_[d.month - 1]}" if LANG == "de" else f"{wd_[d.weekday()]} {d.day}" + (". " if LANG == "da" else " ") + mon_[d.month - 1]
    h = [f'<section class="day" id="d-{x["iso"]}" data-date="{x["iso"]}">',
         f'<header class="dayhead"><div class="leaf" aria-hidden="true"><span class="lw">{wds_[d.weekday()]}</span><span class="ln">{d.day}</span><span class="lm">{mon_[d.month - 1][:3]}</span></div>'
         f'<h2><span class="big" data-rel="{i}" data-wd="{wd_[d.weekday()].capitalize()}">{E(rel)}</span><span class="date">{E(datetxt)}</span></h2></header>']
    if x["klippen"] or x["own"]:
        h.append(f'<div class="klippen"><p class="who">{BIRD}{L("Hos Klippen")}</p><ul>')
        for e in x["own"]:
            h.append(f'<li class="own"><span class="t">{E(e["time"])}</span><span class="what"><b>{link(e["title"], e["url"])}</b>{("<span class=where>" + E(e["where"]) + "</span>") if e["where"] else ""}{("<small>" + E(e["text"]) + "</small>") if e["text"] else ""}</span></li>')
        for k in x["klippen"]:
            h.append(f'<li data-end="{k["end"]}"><span class="t">{E(k["hours"])}</span><span class="what"><b>{link(k["name"], k["url"])}</b><span class="where">{E(k["where"])}</span></span></li>')
        h.append("</ul></div>")
    if x["items"]:
        h.append('<ol class="times">')
        for it in x["items"]:
            end = f' data-end="{it["end"]}"' if it["end"] else ""
            h.append(f'<li{end}>{icon(it["kind"] or "andet")}<span class="t">{E(it["time"])}</span><span class="what"><b>{link(it["title"], it["url"])}</b><span class="where">{E(it["where"])}</span>{('<a class="reg" href="' + E(it["url"]) + '" rel="noopener">' + E(it["reg"]) + ' ↗</a>') if it.get("reg") else ""}</span></li>')
        h.append("</ol>")
    elif not (x["klippen"] or x["own"]):
        h.append(f'<p class="quiet">{L("Ingen arrangementer i kalenderen endnu.")}</p>')
    tiles = []
    for m in x["mus"]:
        tiles.append(f'<a class="tile" href="{E(m["url"])}" rel="noopener"><span class="tn">{E(m["name"])}</span><span class="th">{E(m["hours"])}</span></a>')
    if x["swim"]:
        tiles.append(f'<a class="tile sea" href="{E(x["pool_url"])}" rel="noopener"><span class="tn">{L("Svømmehallen")}</span><span class="th">{E(x["swim"])}</span></a>')
    elif x["pool_closed"]:
        tiles.append(f'<a class="tile sea" href="{E(x["pool_url"])}" rel="noopener"><span class="tn">{L("Svømmehallen")}</span><span class="th">{L("Lukket")}</span></a>')
    if tiles:
        h.append(f'<div class="opens"><p class="olabel">{L("Åbent denne dag")}</p><div class="tiles">' + "".join(tiles) + "</div></div>")
    if x["food"]:
        h.append(f'<details class="food"><summary>{icon("mad")}<span>{L("Spisesteder, barer og is, der har åbent")} <b>{len(x["food"])}</b></span></summary><ul>')
        for f in x["food"]:
            tag = f'<span class="tag">Klippen</span>' if f.get("ours") else ""
            h.append(f'<li{" class=ours" if f.get("ours") else ""}><span class="what"><b>{tag}{link(f["name"], f["url"])}</b><small>{E(f["desc"])}</small></span><span class="t">{E(f["hours"])}</span></li>')
        h.append("</ul></details>")
    h.append("</section>")
    return "\n".join(h)

def build_later(D, today):
    """Arrangementer fra dag 8 og et år frem (byens kalender + Klippens egne), grupperet pr. måned."""
    start, end = today + datetime.timedelta(days=DAYS), today + datetime.timedelta(days=LATER_DAYS)
    rows = []
    for e in D.get("town", []):
        d1 = datetime.date.fromisoformat(e["d"]); d2 = datetime.date.fromisoformat(e.get("to") or e["d"])
        if e.get("long"):   # udstillinger o.l.: vises i den måned, de åbner – eller i første måned, hvis de allerede er i gang
            if d2 < start or d1 > end:
                continue
        elif d1 < start or d1 > end:
            continue
        tt = (hm(e["t"]) + (("–" + hm(e["t2"])) if e.get("t2") else "")) if e.get("t") else ""
        rows.append({"d": d1, "to": d2, "time": tt, "title": L(e["title"]), "where": e.get("where", ""), "url": e.get("rurl") or e.get("url"),
                     "kind": kind_of(e), "reg": {1: L("Kræver tilmelding"), 2: L("Tilmelding til nogle aktiviteter"), 3: L("Billet på forhånd")}.get(e.get("reg"), ""), "own": False,
                     "long": bool(e.get("long")), "k": max(d1, start)})
    for e in D.get("events", []):
        d1 = datetime.date.fromisoformat(e["date"]); d2 = datetime.date.fromisoformat(e.get("to") or e["date"])
        if d1 < start or d1 > end:
            continue
        rows.append({"d": d1, "to": d2, "time": kl(e["time"]) if e.get("time") else "", "title": L(e["title"]), "where": L(e.get("where", "")),
                     "url": e.get("url"), "kind": "andet", "reg": "", "own": True, "long": False, "k": d1})
    rows.sort(key=lambda r: (r["k"], not r["long"], r["time"], r["title"]))
    months = []
    for r in rows:
        k = (r["k"].year, r["k"].month)
        if not months or months[-1]["k"] != k:
            months.append({"k": k, "rows": []})
        months[-1]["rows"].append(r)
    return months

def render_later(months, today):
    wd_, wds_, mon_ = DAYNAMES[LANG]
    h = ['<section class="later" id="senere">', f'<h2 class="lhead">{L("Længere frem")}</h2>',
         f'<p class="lsub">{L("Det, der allerede står i kalenderen det næste år. Der kommer flere arrangementer til løbende.")}</p>']
    if not months:
        h.append(f'<p class="quiet">{L("Intet i kalenderen længere frem endnu.")}</p>')
    for i, m in enumerate(months):
        y, mo = m["k"]
        h.append(f'<details class="month"{" open" if i == 0 else ""}><summary><span class="mn">{E(mon_[mo - 1].capitalize())}</span>'
                 f'{("<span class=my>" + str(y) + "</span>") if y != today.year else ""}<b>{len(m["rows"])}</b></summary><ol class="lrows">')
        for r in m["rows"]:
            d, t = r["d"], r["to"]
            if r["long"]:
                dd = f"{t.day}/{t.month}"
                wtxt = L("til")
            elif t != d:
                dd = (f"{d.day}.–{t.day}." if t.month == d.month else f"{d.day}/{d.month}–{t.day}/{t.month}") if LANG != "en" else (f"{d.day}–{t.day}" if t.month == d.month else f"{d.day}/{d.month}–{t.day}/{t.month}")
                wtxt = f"{wds_[d.weekday()]}–{wds_[t.weekday()]}"
            else:
                dd = f"{d.day}." if LANG in ("da", "de") else str(d.day)
                wtxt = wds_[d.weekday()]
            reg = ('<a class="reg" href="' + E(r["url"]) + '" rel="noopener">' + E(r["reg"]) + ' ↗</a>') if r["reg"] else ""
            per = ""
            if r["long"]:
                f = lambda x: (f"{x.day}. {mon_[x.month - 1][:3]}" if LANG != "en" else f"{mon_[x.month - 1][:3]} {x.day}")
                per = f"{f(d)} – {f(t)}" + (f" {t.year}" if t.year != d.year else "")
            where = " · ".join(x for x in (r["where"], per, r["time"]) if x)
            h.append(f'<li{" class=own" if r["own"] else ""}><span class="ld"><span class="lwd">{E(wtxt)}</span><span class="ldn">{E(dd)}</span></span>'
                     f'<span class="what"><b>{BIRD if r["own"] else ""}{link(r["title"], r["url"])}</b><span class="where">{E(where)}</span>{reg}</span></li>')
        h.append('</ol></details>')
    h.append('</section>')
    return "\n".join(h)

SITENAME = {"da": "Det sker i Gudhjem", "en": "What's on in Gudhjem", "de": "Was ist los in Gudhjem", "sv": "Det händer i Gudhjem"}

def jsonld(days, later=()):
    evs = [{"@type": "WebSite", "name": SITENAME[LANG], "url": "https://detskerigudhjem.dk/" + LANG_PATH[LANG], "inLanguage": LANG,
            "publisher": {"@type": "Hotel", "name": "Klippen Hotel", "url": "https://www.hotelklippen.com/",
                          "address": {"@type": "PostalAddress", "addressLocality": "Gudhjem", "postalCode": "3760", "addressCountry": "DK"}}}]
    for x in days:
        for it in x["items"]:
            if it["s"] < 0 or it["kind"] == "film":
                continue
            m = re.match(r"(\d+)(?:\.(\d+))?", it["time"])
            start = datetime.datetime.combine(x["d"], datetime.time(int(m.group(1)), int(m.group(2) or 0)), TZ).isoformat() if m else x["iso"]
            evs.append({"@type": "Event", "name": it["title"], "startDate": start, "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                        "location": {"@type": "Place", "name": it["where"] or "Gudhjem", "address": {"@type": "PostalAddress", "addressLocality": "Gudhjem", "postalCode": "3760", "addressCountry": "DK"}},
                        **({"url": it["url"]} if it["url"] else {})})
    for m in later:
        for r in m["rows"]:
            mt = re.match(r"(\d+)(?:\.(\d+))?", r["time"] or "")
            start = datetime.datetime.combine(r["d"], datetime.time(int(mt.group(1)), int(mt.group(2) or 0)), TZ).isoformat() if mt else r["d"].isoformat()
            evs.append({"@type": "Event", "name": r["title"], "startDate": start, **({"endDate": r["to"].isoformat()} if r["to"] != r["d"] else {}),
                        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                        "location": {"@type": "Place", "name": r["where"] or "Gudhjem", "address": {"@type": "PostalAddress", "addressLocality": "Gudhjem", "postalCode": "3760", "addressCountry": "DK"}},
                        **({"url": r["url"]} if r["url"] else {})})
    return json.dumps({"@context": "https://schema.org", "@graph": evs[:151]}, ensure_ascii=False)

# skabelonens tekster: dansk → [en, de, sv]
TPL = [
    ('<html lang="da">', ['<html lang="en">', '<html lang="de">', '<html lang="sv">']),
    ('Det sker i Gudhjem – i dag og de næste dage', ["What's on in Gudhjem – today and the next few days", "Was ist los in Gudhjem – heute und in den nächsten Tagen", "Det händer i Gudhjem – i dag och de närmaste dagarna"]),
    ('Hvad sker der i Gudhjem i dag? Film i Scala, koncerter og gudstjenester, museer, svømmehal, børneaktiviteter og spisesteder med åbent – samlet og opdateret hver dag.',
     ["What's on in Gudhjem today? Films at Scala, concerts and church services, museums, the swimming pool, activities for children and restaurants that are open – in one place, updated daily.",
      "Was ist heute in Gudhjem los? Filme im Scala, Konzerte und Gottesdienste, Museen, Schwimmhalle, Kinderaktivitäten und geöffnete Restaurants – an einem Ort, täglich aktualisiert.",
      "Vad händer i Gudhjem i dag? Film på Scala, konserter och gudstjänster, museer, simhall, barnaktiviteter och matställen som har öppet – samlat och uppdaterat varje dag."]),
    ('Byens kalender: film, koncerter, museer, svømmehal og spisesteder – opdateret hver dag.',
     ["The town calendar: films, concerts, museums, swimming pool and restaurants – updated daily.", "Der Kalender der Stadt: Filme, Konzerte, Museen, Schwimmhalle und Restaurants – täglich aktualisiert.", "Stadens kalender: film, konserter, museer, simhall och matställen – uppdaterad varje dag."]),
    ('content="Det sker i Gudhjem"', ['content="What\'s on in Gudhjem"', 'content="Was ist los in Gudhjem"', 'content="Det händer i Gudhjem"']),
    ('content="da_DK"', ['content="en_GB"', 'content="de_DE"', 'content="sv_SE"']),
    ('</svg>Lavet af <a href="{{BOOK}}">Klippen Hotel</a> i Gudhjem', ['</svg>Made by <a href="{{BOOK}}">Klippen Hotel</a> in Gudhjem', '</svg>Von <a href="{{BOOK}}">Klippen Hotel</a> in Gudhjem', '</svg>Gjord av <a href="{{BOOK}}">Klippen Hotel</a> i Gudhjem']),
    ('<h1>Det sker i Gudhjem</h1>', ["<h1>What's on in Gudhjem</h1>", "<h1>Was ist los in Gudhjem</h1>", "<h1>Det händer i Gudhjem</h1>"]),
    ('Film, koncerter, gudstjenester, museer, svømmehal og børneaktiviteter – og hvor du kan spise. Samlet ét sted og opdateret hver morgen.',
     ["Films, concerts, church services, museums, the swimming pool and things for children – and where to eat. All in one place, updated every morning.",
      "Filme, Konzerte, Gottesdienste, Museen, Schwimmhalle und Kinderaktivitäten – und wo man essen kann. An einem Ort, jeden Morgen aktualisiert.",
      "Film, konserter, gudstjänster, museer, simhall och barnaktiviteter – och var du kan äta. Samlat på ett ställe och uppdaterat varje morgon."]),
    ('Tegning af Gudhjem set fra havet: Klippens hvide hotel på klipperne ved Grevens Dal med Gudhjem Mølle og kirken bagved, husene op ad bakken, Therns, Skt. Jørgens Gaard ved havnen, røgeriets gule skorstene og Christiansøbåden',
     ["Drawing of Gudhjem seen from the sea: Klippen's white hotel on the cliffs at Grevens Dal with Gudhjem Mill and the church behind, the houses up the hill, Therns, Skt. Jørgens Gaard by the harbour, the smokehouse's yellow chimneys and the Christiansø ferry",
      "Zeichnung von Gudhjem vom Meer aus: Klippens weißes Hotel auf den Klippen bei Grevens Dal mit der Mühle und der Kirche dahinter, die Häuser am Hang, Therns, Skt. Jørgens Gaard am Hafen, die gelben Schornsteine der Räucherei und die Christiansø-Fähre",
      "Teckning av Gudhjem sett från havet: Klippens vita hotell på klipporna vid Grevens Dal med Gudhjems kvarn och kyrkan bakom, husen uppför backen, Therns, Skt. Jørgens Gaard vid hamnen, rökeriets gula skorstenar och Christiansøbåten"]),
    ('aria-label="Vælg dag"', ['aria-label="Choose day"', 'aria-label="Tag wählen"', 'aria-label="Välj dag"']),
    ('<h2>Bo midt i det hele</h2>', ['<h2>Stay right in the middle of it</h2>', '<h2>Mittendrin wohnen</h2>', '<h2>Bo mitt i allt</h2>']),
    ('Klippen Hotel har tre små hoteller i Gudhjem: Grevens Dal på klipperne, Therns midt i byen og Skt. Jørgens Gaard ved havnen.',
     ["Klippen Hotel has three small hotels in Gudhjem: Grevens Dal on the cliffs, Therns in the middle of town and Skt. Jørgens Gaard by the harbour.",
      "Klippen Hotel hat drei kleine Hotels in Gudhjem: Grevens Dal auf den Klippen, Therns mitten in der Stadt und Skt. Jørgens Gaard am Hafen.",
      "Klippen Hotel har tre små hotell i Gudhjem: Grevens Dal på klipporna, Therns mitt i stan och Skt. Jørgens Gaard vid hamnen."]),
    ('Se værelser hos Klippen', ['See rooms at Klippen', 'Zimmer bei Klippen ansehen', 'Se rum hos Klippen']),
    ('<h3>Har du et arrangement i Gudhjem?</h3>', ['<h3>Have an event in Gudhjem?</h3>', '<h3>Haben Sie eine Veranstaltung in Gudhjem?</h3>', '<h3>Har du ett evenemang i Gudhjem?</h3>']),
    ('med dato, tid og sted, så kommer det med.', ['with the date, time and place, and we will add it.', 'mit Datum, Uhrzeit und Ort, dann nehmen wir es auf.', 'med datum, tid och plats, så kommer det med.']),
    ('>Skriv til <a href="mailto', ['>Write to <a href="mailto', '>Schreiben Sie an <a href="mailto', '>Skriv till <a href="mailto']),
    ('<p class="small">Opdateret {{UPDATED}}. · <a href="#" class="cookie-valg">Cookie-valg</a></p>', ['<p class="small">Updated {{UPDATED}}. · <a href="#" class="cookie-valg">Cookie settings</a></p>', '<p class="small">Aktualisiert {{UPDATED}}. · <a href="#" class="cookie-valg">Cookie-Einstellungen</a></p>', '<p class="small">Uppdaterad {{UPDATED}}. · <a href="#" class="cookie-valg">Cookieval</a></p>']),
]
LANG_PATH = {"da": "", "en": "en/", "de": "de/", "sv": "sv/"}
LANG_NAME = {"da": "DA", "en": "EN", "de": "DE", "sv": "SV"}
BOOK_URL = {"da": "https://www.hotelklippen.com", "en": "https://www.hotelklippen.com/en", "de": "https://www.hotelklippen.com/de", "sv": "https://www.hotelklippen.com/sv"}

def main():
    global LANG, DTR
    D = load()
    DTR = D.get("tr", {})
    now = datetime.datetime.now(TZ); today = now.date()
    tpl0 = (ROOT / "template.html").read_text(encoding="utf-8")
    site = ROOT / "site"; site.mkdir(exist_ok=True)
    hreflang = "\n".join(f'<link rel="alternate" hreflang="{l}" href="https://detskerigudhjem.dk/{LANG_PATH[l]}">' for l in LANGS) + '\n<link rel="alternate" hreflang="x-default" href="https://detskerigudhjem.dk/">'
    total = 0
    for LANG in LANGS:
        places = {p["id"]: p for p in D["places"]}
        for pid, p in list(places.items()):
            if p.get("cat") in ("mad", "is") and not p.get("ours") and not p.get("venue") and not open_within_week(p, today):
                del places[pid]
        days = [build_day(D, today + datetime.timedelta(days=i), places) for i in range(DAYS)]
        wd_, wds_, mon_ = DAYNAMES[LANG]
        nav = "".join(f'<a href="#d-{x["iso"]}" data-date="{x["iso"]}">{L("I dag") if i == 0 else L("I morgen") if i == 1 else wds_[x["d"].weekday()].capitalize() + " " + str(x["d"].day) + ("." if LANG in ("da", "de") else "")}</a>' for i, x in enumerate(days))
        later = build_later(D, today)
        nav += f'<a href="#senere" class="latr">{L("Længere frem")}</a>'
        body = "\n".join(render_day(x, i) for i, x in enumerate(days)) + "\n" + render_later(later, today)
        tpl = tpl0
        if LANG != "da":
            for da, tr in TPL:
                tpl = tpl.replace(da, tr[LANGS.index(LANG) - 1])
        pre = "" if LANG == "da" else "../"
        langs = "".join(f'<a href="{(pre + LANG_PATH[l]) or "./"}" hreflang="{l}" lang="{l}" aria-current="{str(l == LANG).lower()}">{LANG_NAME[l]}</a>' for l in LANGS)
        upd = f"{mon_[today.month - 1]} {today.day}, {today.year}" if LANG == "en" else f"{today.day}. {mon_[today.month - 1]} {today.year}"
        out = (tpl.replace("{{NAV}}", nav).replace("{{DAYS}}", body).replace("{{JSONLD}}", jsonld(days, later))
                  .replace("{{UPDATED}}", upd).replace("{{BOOK}}", BOOK_URL[LANG]).replace("{{PATH}}", LANG_PATH[LANG])
                  .replace("{{HREFLANG}}", hreflang).replace("{{LANGS}}", langs).replace("{{TODAY}}", L("I dag")).replace("{{TOMORROW}}", L("I morgen"))
                  .replace("{{SITENAME}}", SITENAME[LANG].replace('"', "&quot;")).replace("{{LANGCODE}}", LANG).replace("{{UP}}", pre))
        d = site / LANG_PATH[LANG]; d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(out, encoding="utf-8")
        total += sum(len(x["items"]) for x in days)
    LANG = "da"
    for f in (ROOT / "static").glob("*"):
        shutil.copy(f, site / f.name)
    (site / "CNAME").write_text("detskerigudhjem.dk\n", encoding="utf-8")
    (site / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://detskerigudhjem.dk/sitemap.xml\n", encoding="utf-8")
    urls = "".join(f'<url><loc>https://detskerigudhjem.dk/{LANG_PATH[l]}</loc><lastmod>{today.isoformat()}</lastmod><changefreq>daily</changefreq></url>' for l in LANGS)
    (site / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8")
    print("Bygget:", total, "punkter på", len(LANGS), "sprog")

if __name__ == "__main__":
    main()
