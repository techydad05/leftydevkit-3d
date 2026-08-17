"""Merge duplicate incidents so the counter never double-counts.

The curated seed records and the scraped tracker rows describe some of the same
events (Qatar jet, Vulcan Elements, the ballroom). The curated record is the
canonical one — it has the ledger assignment and the amount_basis. The scraped
duplicate gets status='merged' + merged_into=<canonical id>, and its citations
are moved onto the canonical record so we keep the extra sourcing.

Merged rows stay in the DB (audit trail) but are excluded from v_counter and
from the API, because every query filters `merged_into IS NULL`.
"""
from __future__ import annotations
import json, sys, re
from . import db

# canonical slug -> regexes matching the scraped duplicate's title
DUPES = {
    "qatar-400m-jet": [r"\$400 million jet from the Qatari"],
    "vulcan-elements-620m-pentagon-loan": [r"Vulcan Elements"],
    "white-house-ballroom-taxpayer-half": [
        r"taxpayer dollars will fund half the costs of the White House ballroom"],
    "oge-2025-disclosure-memecoin-royalties": [
        r"Trump family made millions from a crypto meme coin"],
}


def run(con=None) -> dict:
    own = con is None
    con = con or db.connect()
    if own:
        db.init(con)
    merged = moved = 0
    for canon_slug, pats in DUPES.items():
        canon = con.execute("SELECT id FROM incidents WHERE slug=?", (canon_slug,)).fetchone()
        if not canon:
            continue
        cid = canon["id"]
        for r in con.execute(
                "SELECT id,title FROM incidents WHERE id!=? AND merged_into IS NULL",
                (cid,)).fetchall():
            if not any(re.search(p, r["title"], re.I) for p in pats):
                continue
            # carry citations over to the canonical record
            for c in con.execute("SELECT * FROM citations WHERE incident_id=?", (r["id"],)):
                db.add_citation(con, cid, c["url"], source_slug=c["source_slug"],
                                publisher=c["publisher"], title=c["title"],
                                tier=c["tier"], published_at=c["published_at"])
                moved += 1
            con.execute("""UPDATE incidents SET status='merged', merged_into=?,
                           updated_at=? WHERE id=?""", (cid, db.now(), r["id"]))
            merged += 1
    con.commit()
    return {"merged": merged, "citations_moved": moved}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
    sys.exit(0)
