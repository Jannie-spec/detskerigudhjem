"""Bygger detskerigudhjem.dk som én statisk side (site/index.html).

Data hentes fra Klippens gæste-app (https://therns.dk/app/gudhjem.json), som hver nat samler:
Klippens egne steder og events, film i Scala, svømmehallens kalender, byens arrangementer
(kirke, museer m.m.) og åbningstider for spisesteder. Køres af GitHub Actions hver nat.
"""
import json, html, datetime, urllib.request, pathlib, re
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent
SRC = "https://therns.dk/app/gudhjem.json"
TZ = ZoneInfo("Europe/Copenhagen")
DAYS = 7
BOOK = "https://www.hotelklippen.com"
E = lambda s: html.escape(str(s or ""), quote=True)
WD = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
WD_SHORT = ["man", "tir", "ons", "tor", "fre", "lør", "søn"]
MON = ["januar", "februar", "marts", "april", "maj", "juni", "juli", "august", "september", "oktober", "november", "december"]
MUSEUMS = ["kunst", "host", "gmus", "melg"]
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
            klippen.append({"name": v["name"], "where": v["where"], "hours": span(sl), "url": v.get("url"), "end": max(tmin(b) for _, b in sl)})
    own = []
    for e in sorted(D.get("events", []), key=lambda e: e.get("time") or ""):
        if e["date"] <= iso <= (e.get("to") or e["date"]):
            own.append({"title": e["title"], "where": e.get("where", ""), "time": ("kl. " + hm(e["time"])) if e.get("time") else "", "text": e.get("text", ""), "url": e.get("url")})
    # I byen: events, film, svømmehal-events
    items = []
    for e in D.get("town", []):
        if not (e["d"] <= iso <= (e.get("to") or e["d"])):
            continue
        if e.get("wd") and ((d.weekday() + 1) % 7) not in e["wd"]:
            continue
        if e.get("t"):
            tt = hm(e["t"]) + (("–" + hm(e["t2"])) if e.get("t2") else "")
            items.append(item(tmin(e["t"]), tt, e["title"], e.get("where", ""), e.get("url"), tmin(e.get("t2") or e["t"]) + (0 if e.get("t2") else 90), kind_of(e)))
        else:
            items.append(item(-1, "Hele dagen", e["title"], e.get("where", ""), e.get("url"), None, kind_of(e)))
    for f in D.get("films", []):
        if f["d"] == iso:
            items.append(item(tmin(f["t"]), hm(f["t"]), f["title"], "Scala Gudhjem, biograf", "http://www.scalagudhjem.dk/", tmin(f["t"]) + 30, "film"))
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
                    items.append(item(tmin(x["a"]), f"{hm(x['a'])}–{hm(x['b'])}", "Familiesvømning med vipper og legeredskaber", "Gudhjem Svømmehal", pool_url, tmin(x["b"]), "svom"))
                elif x["k"] == "e":
                    items.append(item(tmin(x["a"]), f"{hm(x['a'])}–{hm(x['b'])}", x.get("title", "Arrangement"), "Gudhjem Svømmehal", pool_url, tmin(x["b"]), "svom"))
    else:
        sl = slots_on(places.get("svom"), d)
        swim = span(sl) if sl else None
    items.sort(key=lambda x: (x["s"], x["title"]))
    # Åbent: museer + svømmehal
    mus = []
    for mid in MUSEUMS:
        p = places.get(mid)
        sl = slots_on(p, d)
        if p and sl:
            mus.append({"name": MUS_SHORT[mid], "hours": span(sl), "url": p.get("url")})
    # Spisesteder og is
    food = []
    for p in places.values():
        if p.get("cat") not in ("mad", "is") or p.get("hide") or p.get("ours") or p.get("venue") or p.get("far"):
            continue
        sl = slots_on(p, d)
        if sl:
            food.append({"name": p["name"], "hours": span(sl), "cat": p["cat"], "desc": p.get("desc", ""), "url": p.get("url")})
        elif not p.get("hours") and "seasons" not in p and p.get("label"):
            food.append({"name": p["name"], "hours": "", "cat": p["cat"], "desc": p.get("label", ""), "url": p.get("url")})
    food.sort(key=lambda f: (f["cat"] != "mad", f["name"]))
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
    return f'<span class="ic ic-{kind}" title="{E(KIND_LABEL.get(kind, ""))}"><svg viewBox="0 0 24 24" aria-hidden="true">{ICON.get(kind, ICON["andet"])}</svg></span>'

def link(text, url):
    return f'<a href="{E(url)}" rel="noopener">{E(text)}</a>' if url else E(text)

def render_day(x, i):
    d = x["d"]
    rel = "I dag" if i == 0 else "I morgen" if i == 1 else WD[d.weekday()].capitalize()
    h = [f'<section class="day" id="d-{x["iso"]}" data-date="{x["iso"]}">',
         f'<header class="dayhead"><div class="leaf" aria-hidden="true"><span class="lw">{WD_SHORT[d.weekday()]}</span><span class="ln">{d.day}</span><span class="lm">{MON[d.month - 1][:3]}</span></div>'
         f'<h2><span class="big" data-rel="{i}" data-wd="{WD[d.weekday()].capitalize()}">{E(rel)}</span><span class="date">{WD[d.weekday()]} {d.day}. {MON[d.month - 1]}</span></h2></header>']
    if x["klippen"] or x["own"]:
        h.append(f'<div class="klippen"><p class="who">{BIRD}Hos Klippen</p><ul>')
        for e in x["own"]:
            h.append(f'<li class="own"><span class="t">{E(e["time"])}</span><span class="what"><b>{link(e["title"], e["url"])}</b>{("<span class=where>" + E(e["where"]) + "</span>") if e["where"] else ""}{("<small>" + E(e["text"]) + "</small>") if e["text"] else ""}</span></li>')
        for k in x["klippen"]:
            h.append(f'<li data-end="{k["end"]}"><span class="t">{E(k["hours"])}</span><span class="what"><b>{link(k["name"], k["url"])}</b><span class="where">{E(k["where"])}</span></span></li>')
        h.append("</ul></div>")
    if x["items"]:
        h.append('<ol class="times">')
        for it in x["items"]:
            end = f' data-end="{it["end"]}"' if it["end"] else ""
            h.append(f'<li{end}>{icon(it["kind"] or "andet")}<span class="t">{E(it["time"])}</span><span class="what"><b>{link(it["title"], it["url"])}</b><span class="where">{E(it["where"])}</span></span></li>')
        h.append("</ol>")
    elif not (x["klippen"] or x["own"]):
        h.append('<p class="quiet">Ingen arrangementer i kalenderen endnu.</p>')
    tiles = []
    for m in x["mus"]:
        tiles.append(f'<a class="tile" href="{E(m["url"])}" rel="noopener"><span class="tn">{E(m["name"])}</span><span class="th">{E(m["hours"])}</span></a>')
    if x["swim"]:
        tiles.append(f'<a class="tile sea" href="{E(x["pool_url"])}" rel="noopener"><span class="tn">Svømmehallen</span><span class="th">{E(x["swim"])}</span></a>')
    elif x["pool_closed"]:
        tiles.append(f'<a class="tile sea" href="{E(x["pool_url"])}" rel="noopener"><span class="tn">Svømmehallen</span><span class="th">Lukket</span></a>')
    if tiles:
        h.append('<div class="opens"><p class="olabel">Åbent denne dag</p><div class="tiles">' + "".join(tiles) + "</div></div>")
    if x["food"]:
        h.append(f'<details class="food"><summary>{icon("mad")}<span>Spisesteder og is med åbent <b>{len(x["food"])}</b></span></summary><ul>')
        for f in x["food"]:
            h.append(f'<li><span class="what"><b>{link(f["name"], f["url"])}</b><small>{E(f["desc"])}</small></span><span class="t">{E(f["hours"])}</span></li>')
        h.append("</ul></details>")
    h.append("</section>")
    return "\n".join(h)

def jsonld(days):
    evs = []
    for x in days:
        for it in x["items"]:
            if it["s"] < 0 or it["kind"] == "film":
                continue
            m = re.match(r"(\d+)(?:\.(\d+))?", it["time"])
            start = datetime.datetime.combine(x["d"], datetime.time(int(m.group(1)), int(m.group(2) or 0)), TZ).isoformat() if m else x["iso"]
            evs.append({"@type": "Event", "name": it["title"], "startDate": start, "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                        "location": {"@type": "Place", "name": it["where"] or "Gudhjem", "address": {"@type": "PostalAddress", "addressLocality": "Gudhjem", "postalCode": "3760", "addressCountry": "DK"}},
                        **({"url": it["url"]} if it["url"] else {})})
    return json.dumps({"@context": "https://schema.org", "@graph": evs[:60]}, ensure_ascii=False)

def main():
    D = load()
    places = {p["id"]: p for p in D["places"]}
    now = datetime.datetime.now(TZ); today = now.date()
    for pid, p in list(places.items()):
        if p.get("cat") in ("mad", "is") and not p.get("ours") and not p.get("venue") and not open_within_week(p, today):
            del places[pid]
    days = [build_day(D, today + datetime.timedelta(days=i), places) for i in range(DAYS)]
    nav = "".join(f'<a href="#d-{x["iso"]}" data-date="{x["iso"]}">{"I dag" if i == 0 else "I morgen" if i == 1 else WD_SHORT[x["d"].weekday()].capitalize() + " " + str(x["d"].day) + "."}</a>' for i, x in enumerate(days))
    body = "\n".join(render_day(x, i) for i, x in enumerate(days))
    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    out = (tpl.replace("{{NAV}}", nav).replace("{{DAYS}}", body).replace("{{JSONLD}}", jsonld(days))
              .replace("{{UPDATED}}", f"{today.day}. {MON[today.month - 1]} {today.year}").replace("{{BOOK}}", BOOK))
    site = ROOT / "site"; site.mkdir(exist_ok=True)
    (site / "index.html").write_text(out, encoding="utf-8")
    (site / "CNAME").write_text("detskerigudhjem.dk\n", encoding="utf-8")
    (site / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://detskerigudhjem.dk/sitemap.xml\n", encoding="utf-8")
    (site / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://detskerigudhjem.dk/</loc><lastmod>{today.isoformat()}</lastmod><changefreq>daily</changefreq></url></urlset>\n', encoding="utf-8")
    print("Bygget:", sum(len(x["items"]) for x in days), "punkter over", DAYS, "dage")

if __name__ == "__main__":
    main()
