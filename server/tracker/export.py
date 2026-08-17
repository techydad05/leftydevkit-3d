"""Export the DB to static JSON the Svelte counter / OBS overlay consume.

    python -m tracker.export   ->  public/data/incidents.json
"""
from __future__ import annotations
import json, pathlib, datetime
from . import db

OUT = pathlib.Path(__file__).resolve().parent.parent / "public" / "data" / "incidents.json"


def build(con) -> dict:
    incs = []
    for r in con.execute(
            """SELECT * FROM incidents WHERE status IN ('verified','unverified')
               AND merged_into IS NULL ORDER BY event_date DESC NULLS LAST, id"""):
        cits = [dict(c) for c in con.execute(
            "SELECT url,publisher,title,published_at,tier FROM citations "
            "WHERE incident_id=? ORDER BY tier", (r["id"],))]
        incs.append({
            "id": r["id"], "slug": r["slug"], "title": r["title"],
            "summary": r["summary"], "date": r["event_date"],
            "category": r["category"], "status": r["status"],
            "confidence": r["confidence"],
            "flow_to_trump": r["flow_to_trump"],
            "cost_to_public": r["cost_to_public"],
            "deal_value": r["deal_value"],
            "amount_basis": r["amount_basis"],
            "is_estimated": bool(r["is_estimated"]),
            "citations": cits,
        })
    v = con.execute("SELECT * FROM v_counter").fetchone()
    verified = [i for i in incs if i["status"] == "verified"]
    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "counter": {
            "verified_incidents": v["verified_incidents"],
            "unverified_pending": len(incs) - len(verified),
            "total_flow_to_trump": v["total_flow_to_trump"],
            "total_cost_to_public": v["total_cost_to_public"],
            "documented_deal_value": sum(i["deal_value"] or 0 for i in verified),
            "first_date": v["first_date"], "last_date": v["last_date"],
            "citation_count": con.execute("SELECT COUNT(*) c FROM citations").fetchone()["c"],
        },
        "by_category": {k: sum(1 for i in verified if i["category"] == k)
                        for k in sorted({i["category"] for i in verified})},
        "incidents": incs,
    }


def run(con=None, out: pathlib.Path = OUT) -> dict:
    own = con is None
    con = con or db.connect()
    if own:
        db.init(con)
    data = build(con)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"path": str(out), **data["counter"]}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
