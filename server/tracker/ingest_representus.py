"""Scrape the RepresentUs Trump Corruption Tracker.

Best-ROI source: every entry is dated and carries a link to the original
reporting (NYT, ProPublica, FT, WaPo, Reuters...), so each row lands in the DB
already citable.
"""
from __future__ import annotations
import re, sys, datetime
import httpx
from selectolax.parser import HTMLParser

from . import db

URL = "https://represent.us/trump-corruption-tracker/"
SLUG = "representus"

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

# "June. 16, 2026" / "Sept. 19, 2025" / "May 5, 2025"
DATE_RE = re.compile(r"^([A-Z][a-z]{2,8})\.?\s+(\d{1,2}),?\s+(\d{4})$")


def parse_date(text: str) -> str | None:
    m = DATE_RE.match(text.strip())
    if not m:
        return None
    mon = MONTHS.get(m.group(1)[:3].lower())
    if not mon:
        return None
    try:
        return datetime.date(int(m.group(3)), mon, int(m.group(2))).isoformat()
    except ValueError:
        return None


def fetch(url: str = URL) -> str:
    r = httpx.get(url, timeout=45, follow_redirects=True, headers={
        "User-Agent": "LeftyDevKit-CorruptionTracker/0.1 (+civic research)"})
    r.raise_for_status()
    return r.text


def extract(html: str) -> list[dict]:
    """The tracker renders one .trump-timeline__row per incident, each with a
    .trump-timeline__date and a .trump-timeline__desc whose trailing <a> is the
    original reporting. Falls back to date-line/blurb pairing if the theme changes."""
    tree = HTMLParser(html)
    rows = tree.css(".trump-timeline__row")
    items = []
    for row in rows:
        dnode = row.css_first(".trump-timeline__date")
        tnode = row.css_first(".trump-timeline__desc") or row
        raw_date = dnode.text(separator=" ", strip=True) if dnode else ""
        body = tnode.text(separator=" ", strip=True)
        body = re.sub(r"\s*\(?\s*source\s*\)?\s*$", "", body, flags=re.I).strip()
        link = None
        for a in tnode.css("a"):
            href = a.attributes.get("href", "")
            if href.startswith("http") and "represent.us" not in href:
                link = href
        if not body:
            continue
        items.append({"event_date": parse_date(raw_date),
                      "raw_date": raw_date,
                      "title": body[:180],
                      "body": body,
                      "link": link})

    seen, out = set(), []
    for it in items:
        k = (it["event_date"], it["title"][:80])
        if k in seen:
            continue
        seen.add(k)
        out.append(it)
    return out


def run(con=None) -> dict:
    own = con is None
    con = con or db.connect()
    if own:
        db.init(con)
    run_id = db.start_run(con, SLUG)
    try:
        items = extract(fetch())
        new = sum(1 for it in items
                  if db.add_raw(con, SLUG, it["title"], it["body"], it["link"],
                                it["event_date"], raw=it) is not None)
        con.commit()
        db.finish_run(con, run_id, True, len(items), new)
        return {"seen": len(items), "new": new}
    except Exception as e:
        db.finish_run(con, run_id, False, error=repr(e))
        raise


if __name__ == "__main__":
    print(run())
    sys.exit(0)
