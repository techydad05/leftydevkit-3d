"""Daily watch job. Prints a report ONLY when something changed.

Silent when nothing new — designed for `cronjob no_agent=True`, where empty
stdout means no message is sent. Non-empty stdout gets delivered verbatim.

    python -m tracker.watch          # normal, quiet unless new
    python -m tracker.watch --force  # always print current standing
"""
from __future__ import annotations
import sys, json, pathlib, datetime
from . import db, refresh as refresh_mod, export

STATE = pathlib.Path(__file__).resolve().parent.parent / "data" / "watch_state.json"


def snapshot(con) -> dict:
    v = con.execute("SELECT * FROM v_counter").fetchone()
    return {
        "incidents": v["verified_incidents"],
        "flow": v["total_flow_to_trump"],
        "public": v["total_cost_to_public"],
        "citations": con.execute("SELECT COUNT(*) n FROM citations").fetchone()["n"],
    }


def money(n: float) -> str:
    if n >= 1e9:
        return f"${n/1e9:.2f}B"
    if n >= 1e6:
        return f"${n/1e6:.1f}M"
    return f"${n:,.0f}"


def main() -> int:
    force = "--force" in sys.argv
    con = db.connect()
    db.init(con)
    before = snapshot(con)

    # run the full pipeline quietly
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            refresh_mod.main()
        except Exception as e:
            print(f"⚠ Corruption Ledger ingest FAILED: {e!r}")
            return 1

    after = snapshot(con)
    d_inc = after["incidents"] - before["incidents"]
    d_money = (after["flow"] + after["public"]) - (before["flow"] + before["public"])

    if not force and d_inc == 0 and d_money == 0:
        return 0  # silent: nothing new today

    lines = []
    if d_inc or d_money:
        lines.append(f"🚨 Corruption Ledger updated: +{d_inc} incident(s), "
                     f"+{money(d_money)}")
        for r in con.execute(
                """SELECT title,event_date,flow_to_trump,cost_to_public FROM incidents
                   WHERE status='verified' ORDER BY id DESC LIMIT ?""", (max(d_inc, 1),)):
            amt = (r["flow_to_trump"] or 0) + (r["cost_to_public"] or 0)
            lines.append(f"  • [{r['event_date']}] {r['title'][:110]}"
                         + (f" — {money(amt)}" if amt else ""))
    else:
        lines.append("Corruption Ledger — no change since last check.")

    total = after["flow"] + after["public"]
    lines.append(f"Standing total: {money(total)} across {after['incidents']} "
                 f"verified incidents, {after['citations']} citations.")
    lines.append(f"  to Trump: {money(after['flow'])} | public money: {money(after['public'])}")
    lines.append("Tool: http://127.0.0.1:8910/tool")
    print("\n".join(lines))

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(
        {"checked_at": datetime.datetime.now().isoformat(timespec="seconds"), **after},
        indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
