"""Import the 76 hardcoded entries from src/lib/instances.ts.

They come in as status='unverified' with amounts parked in `deal_value`
(NOT flow_to_trump), so they cannot inflate the headline counter until a human
has attached a citation and reclassified the money. This is the whole point:
the counter should start honest and grow as evidence lands.
"""
from __future__ import annotations
import re, pathlib, sys
from . import db

TS = pathlib.Path(__file__).resolve().parent.parent / "src" / "lib" / "instances.ts"
ROW = re.compile(
    r"\{\s*id:\s*(\d+),\s*title:\s*\"(.*?)\",\s*amount:\s*([0-9_]+),"
    r"\s*isEstimated:\s*(true|false)\s*\}")


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:70]


def parse(path: pathlib.Path = TS) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    return [{"legacy_id": int(m[0]), "title": m[1].strip(),
             "amount": int(m[2].replace("_", "")), "is_estimated": m[3] == "true"}
            for m in ROW.findall(text)]


def run(con=None) -> dict:
    own = con is None
    con = con or db.connect()
    if own:
        db.init(con)
    rows = parse()
    added = 0
    for r in rows:
        if con.execute("SELECT 1 FROM incidents WHERE legacy_id=?",
                       (r["legacy_id"],)).fetchone():
            continue
        db.upsert_incident(
            con,
            slug=slugify(r["title"]),
            title=r["title"],
            summary=None,
            event_date=None,
            date_precision="ongoing",
            category="unclassified",
            deal_value=r["amount"],          # quarantined until sourced
            amount_basis="legacy hardcoded figure, unsourced, needs reclassification",
            is_estimated=1 if r["is_estimated"] else 0,
            status="unverified",
            confidence=0,
            legacy_id=r["legacy_id"],
            notes="imported from instances.ts",
        )
        added += 1
    con.commit()
    return {"parsed": len(rows), "imported": added}


if __name__ == "__main__":
    print(run())
    sys.exit(0)
