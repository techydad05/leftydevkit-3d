"""Promote raw_items into canonical incidents with citations.

A raw item from a tier-1/2 tracker that carries a dated entry AND a link to
original reporting is auto-promoted to status='verified' — that is the bar:
a watchdog org staked its name on it and pointed at a named outlet. Anything
missing a date or a link stays 'unverified' for human review.

Money is NOT auto-extracted into flow_to_trump. Dollar figures are parsed into
`deal_value` with the sentence that produced them recorded in amount_basis, so
a human decides which ledger it belongs in. The headline counter counts
INCIDENTS, which we can defend; dollar totals stay opt-in.
"""
from __future__ import annotations
import re, json, sys
from urllib.parse import urlparse
from . import db

TIER = {"representus": 1, "crew": 1, "clc": 1, "propublica": 1,
        "kleptocracy": 2, "brennan": 2, "legacy": 3}

MULT = {"thousand": 1e3, "k": 1e3, "million": 1e6, "m": 1e6,
        "billion": 1e9, "b": 1e9, "trillion": 1e12, "t": 1e12}
MONEY = re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s?(trillion|billion|million|thousand|[KMBT])?\b",
                   re.I)

CATEGORY_RULES = [
    ("pardons",      r"pardon|clemency|commut"),
    ("contracts",    r"no-bid|contract|procure|bidding|loan|grant"),
    ("crypto",       r"crypto|memecoin|meme coin|bitcoin|token|world liberty|wlf"),
    ("emoluments",   r"emolument|foreign government|qatar|saudi|uae|jet|gift"),
    ("appointments", r"cabinet|nominee|appoint|divest|stock|holdings|recus"),
    ("oversight",    r"inspector general|watchdog|probe|investigation|oversight|bypass(ed)? congress"),
    ("selfdeal",     r"resort|golf|ballroom|property|library|trump organization|family"),
    ("propaganda",   r"renamed|portrait|signature|statue"),
]


def parse_money(text: str) -> tuple[float, str | None]:
    """Largest dollar figure in the text, plus the phrase it came from."""
    best, phrase = 0.0, None
    for m in MONEY.finditer(text or ""):
        try:
            val = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        unit = (m.group(2) or "").lower()
        val *= MULT.get(unit, 1)
        if val > best:
            best, phrase = val, m.group(0)
    return best, phrase


def categorize(text: str) -> str:
    low = (text or "").lower()
    for cat, pat in CATEGORY_RULES:
        if re.search(pat, low):
            return cat
    return "other"


def make_title(body: str) -> str:
    first = re.split(r"(?<=[.;])\s", body.strip())[0]
    return (first[:150] + "…") if len(first) > 150 else first


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:70]


def run(con=None) -> dict:
    own = con is None
    con = con or db.connect()
    if own:
        db.init(con)

    rows = con.execute(
        "SELECT * FROM raw_items WHERE processed=0 AND source_slug!='legacy'").fetchall()
    made = skipped = 0
    for r in rows:
        body = r["body"] or r["title"] or ""
        title = make_title(body)
        slug = slugify(title)
        # dedupe against existing incidents by slug or same-date near-title
        existing = con.execute(
            "SELECT id FROM incidents WHERE slug=? OR (event_date IS NOT NULL "
            "AND event_date=? AND substr(title,1,60)=?)",
            (slug, r["event_date"], title[:60])).fetchone()
        tier = TIER.get(r["source_slug"], 3)
        if existing:
            inc_id = existing["id"]
            skipped += 1
        else:
            amount, phrase = parse_money(body)
            verified = bool(r["event_date"]) and bool(r["link"]) and tier <= 2
            inc_id = db.upsert_incident(
                con,
                slug=slug,
                title=title,
                summary=body[:1200],
                event_date=r["event_date"],
                date_precision="day",
                category=categorize(body),
                deal_value=amount,
                amount_basis=(f"figure '{phrase}' auto-extracted from source blurb; "
                              "ledger assignment pending human review") if phrase else None,
                is_estimated=1,
                status="verified" if verified else "unverified",
                confidence=80 if verified else 30,
                notes=f"auto-normalized from {r['source_slug']}",
            )
            made += 1
        if r["link"]:
            db.add_citation(con, inc_id, r["link"],
                            source_slug=r["source_slug"],
                            publisher=urlparse(r["link"]).netloc.replace("www.", ""),
                            published_at=r["event_date"],
                            tier=tier,
                            title=title[:180],
                            quote=body[:500])
        con.execute("UPDATE raw_items SET processed=1, incident_id=? WHERE id=?",
                    (inc_id, r["id"]))
    con.commit()
    return {"raw_processed": len(rows), "incidents_created": made, "deduped": skipped}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
    sys.exit(0)
