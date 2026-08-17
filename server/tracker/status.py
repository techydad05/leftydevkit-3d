"""Where is the project? Run: python -m tracker.status"""
from __future__ import annotations
from . import db


def main() -> None:
    con = db.connect()
    db.init(con)
    q = lambda s, *a: con.execute(s, a).fetchall()

    print("== incidents by status ==")
    for r in q("SELECT status, COUNT(*) n FROM incidents GROUP BY status ORDER BY n DESC"):
        print(f"  {r['status']:<12} {r['n']}")

    print("== raw items by source ==")
    for r in q("""SELECT source_slug, COUNT(*) n, SUM(processed) done,
                  MIN(event_date) lo, MAX(event_date) hi
                  FROM raw_items GROUP BY source_slug"""):
        print(f"  {r['source_slug']:<14} {r['n']:>4} raw, {r['done'] or 0} processed"
              f"  [{r['lo']} .. {r['hi']}]")

    print("== citations ==")
    r = q("SELECT COUNT(*) n, COUNT(DISTINCT incident_id) inc FROM citations")[0]
    print(f"  {r['n']} citations across {r['inc']} incidents")

    print("== headline counter (verified only) ==")
    v = q("SELECT * FROM v_counter")[0]
    print(f"  incidents      : {v['verified_incidents']}")
    print(f"  flow to Trump  : ${v['total_flow_to_trump']:,.0f}")
    print(f"  cost to public : ${v['total_cost_to_public']:,.0f}")
    print(f"  window         : {v['first_date']} .. {v['last_date']}")

    print("== last ingest runs ==")
    for r in q("""SELECT source_slug,started_at,ok,items_seen,items_new,error
                  FROM ingest_runs ORDER BY id DESC LIMIT 5"""):
        print(f"  {r['started_at']} {r['source_slug']:<14} ok={r['ok']} "
              f"seen={r['items_seen']} new={r['items_new']} {r['error'] or ''}")


if __name__ == "__main__":
    main()
