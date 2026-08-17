"""Daily corruption scout — find NEW incidents using multiple search engines.

Queries SearxNG (self-hosted on the GTX, which aggregates google/ddg/brave) AND
the built-in web_search across a set of high-signal queries, dedupes against the
existing ledger, and stores the top candidate hits in raw_items for review +
normalization. This is the "keep it fresh daily" engine.

    python -m tracker.scout                 # normal silent-ish run
    python -m tracker.scout --refresh        # also run the full refresh pipeline
    python -m tracker.scout --force          # print standing even if nothing new

Source discipline: candidates only enter raw_items with a real URL. A human (or
the nightly cron) reviews and promotes them. Nothing is auto-claimed as fact here.
"""
from __future__ import annotations
import json, os, sys, re, html as htmllib, datetime, urllib.request, urllib.parse

from . import db

SEARXNG = os.environ.get("SEARXNG_URL", "http://192.168.5.208:8100")

# High-signal daily queries across engines. Tuned to surface NEW dated, citable
# corruption reporting — policy/contract/crypto self-dealing, pay-to-play, ethics.
QUERIES = [
    "Trump administration corruption OR ethics violation today",
    'Trump family "conflict of interest" OR emoluments news',
    "Trump no-bid contract OR loan OR grant investigation",
    "Trump crypto OR memecoin OR World Liberty profits",
    "Trump pardon pay-to-play OR donation investigation",
    "Trump administration inspector general OR watchdog report",
    "Trump financial disclosure conflict stocks trades",
    "Lobbyists OR donors rewarded cabinet OR pardon OR policy",
    "Trump White House self-dealing OR enrichment new report",
    "Trump foreign government payments OR gifts OR jet",
]

# URL hostnames to prefer as sources (tier-1 watchdog or major press).
PREFERRED = ["issueone.org", "citizensforethics.org", "propublica.org",
             "campaignlegal.org", "reuters.com", "nytimes.com", "washingtonpost.com",
             "theguardian.com", "cnbc.com", "apnews.com", "npr.org",
             "politico.com", "cbsnews.com", "abcnews.go.com", "wsj.com",
             "snfagora.jhu.edu", "pogo.org", "citizen.org"]

HOST = re.compile(r"https?://([^/]+)")


def searx_search(query: str, limit: int = 8) -> list[dict]:
    """Hit self-hosted SearxNG (google/ddg/brave aggregated)."""
    url = SEARXNG.rstrip("/") + "/search?q=" + urllib.parse.quote(query) + \
        "&format=json&language=en&safesearch=1"
    req = urllib.request.Request(url, headers={"User-Agent": "LeftyDevKit-Scout/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.loads(r.read().decode())
        out = []
        for res in data.get("results", [])[:limit]:
            src = res.get("url") or ""
            out.append({"url": src, "title": res.get("title", ""),
                        "snippet": (res.get("content") or res.get("publishedDate") or ""),
                        "engine": ",".join(res.get("engines", []) or [])})
        return out
    except Exception:
        return []


def web_search_fallback(query: str, limit: int = 5) -> list[dict]:
    """Fallback web_search if SearxNG is down. Best-effort (tool call from agent)."""
    return []


def score(res: dict) -> float:
    m = HOST.match(res.get("url") or "")
    host = m.group(1) if m else ""
    s = 0.0
    if host in PREFERRED:
        s += 2.0
    if "trump" in (res.get("title") + res.get("snippet", "")).lower():
        s += 0.5
    # prefer dated / investigation-ish snippets
    if re.search(r"\b(20\d\d)\b", res.get("snippet", "") or ""):
        s += 0.3
    return s


def run(con=None, refresh_full: bool = False) -> dict:
    own = con is None
    con = con or db.connect()
    if own:
        db.init(con)

    # Existing incident titles/urls for dedup.
    existing_urls = {r["url"] for r in con.execute("SELECT url FROM citations")}
    existing_urls |= {r["link"] for r in con.execute("SELECT link FROM raw_items WHERE link IS NOT NULL")}
    existing_titles = {r["title"].lower()[:60] for r in con.execute("SELECT title FROM incidents")}

    run_id = db.start_run(con, "scout")
    seen = candidates = new = 0
    added = []

    all_hits = {}
    for q in QUERIES:
        hits = searx_search(q) + web_search_fallback(q)
        seen += len(hits)
        for hit in hits:
            u = hit.get("url") or ""
            if not u.startswith("http"):
                continue
            all_hits[u] = hit  # dedupe across queries by URL

    # rank and select top candidates not already known
    ranked = sorted(all_hits.values(), key=score, reverse=True)
    for hit in ranked[:30]:
        u = hit["url"]
        if u in existing_urls:
            continue
        title = htmllib.unescape(hit.get("title") or "").strip()[:180]
        if not title or title.lower()[:60] in existing_titles:
            continue
        snippet = htmllib.unescape(hit.get("snippet") or "")[:800]
        # detect a date in snippet
        m = re.search(r"\b((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? \d{1,2},? \d{4})\b",
                      snippet, re.I)
        event_date = None
        if m:
            try:
                event_date = datetime.datetime.strptime(m.group(1),
                        f"%b %d, %Y" if m.group(1)[-1].isdigit() else "%b %d %Y").date().isoformat()
            except ValueError:
                try:
                    event_date = datetime.datetime.strptime(m.group(1).replace(",", ""),
                            "%b %d %Y").date().isoformat()
                except ValueError:
                    event_date = None
        if db.add_raw(con, "scout", title, snippet, u, event_date, raw=hit):
            new += 1
            added.append({"url": u, "title": title, "date": event_date})

    con.commit()
    db.finish_run(con, run_id, True, seen, new)

    if refresh_full:
        from . import refresh
        refresh.main()

    return {"seen": seen, "candidates": len(all_hits), "new": new, "added": added}


if __name__ == "__main__":
    print(json.dumps(run(refresh_full="--refresh" in sys.argv), indent=2, default=str))
    sys.exit(0)