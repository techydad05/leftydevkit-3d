"""Corruption Counter API + explorer server.

    python -m tracker.server          # http://127.0.0.1:8910

Endpoints
  GET /api/hero      tiny, cache-friendly payload for the LDK website hero
  GET /api/stats     full counter + category/ledger breakdowns
  GET /api/incidents ?q= &category= &status= &ledger= &sort= &limit= &offset=
  GET /api/incident/<slug>
  GET /api/timeline  incidents grouped by month, for charting
  GET /api/history   counter value over time (for "it went up again" deltas)
  GET /api/overlay   OBS browser-source payload (headline + latest incident)
  GET /healthz
"""
from __future__ import annotations
import json, datetime, pathlib
from flask import Flask, jsonify, request, Response, send_from_directory
from . import db

app = Flask(__name__, static_folder=None)
WEB = pathlib.Path(__file__).resolve().parent.parent / "web"


def _cors(resp: Response) -> Response:
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Cache-Control"] = "public, max-age=300"
    return resp


app.after_request(_cors)


def con():
    c = db.connect()
    db.init(c)
    return c


def _counter(c) -> dict:
    v = c.execute("SELECT * FROM v_counter").fetchone()
    pend = c.execute("SELECT COUNT(*) n FROM incidents WHERE status='unverified' "
                     "AND merged_into IS NULL").fetchone()["n"]
    cits = c.execute("SELECT COUNT(*) n FROM citations").fetchone()["n"]
    deals = c.execute("SELECT COALESCE(SUM(deal_value),0) s FROM incidents "
                      "WHERE status='verified'").fetchone()["s"]
    flow, public = v["total_flow_to_trump"], v["total_cost_to_public"]
    return {
        "verified_incidents": v["verified_incidents"],
        "unverified_pending": pend,
        "citation_count": cits,
        "flow_to_trump": flow,
        "cost_to_public": public,
        "combined": flow + public,
        "documented_deal_value": deals,
        "first_date": v["first_date"],
        "last_date": v["last_date"],
    }


@app.get("/api/hero")
def hero():
    c = con()
    k = _counter(c)
    return jsonify({
        "combined": k["combined"],
        "flow_to_trump": k["flow_to_trump"],
        "cost_to_public": k["cost_to_public"],
        "incidents": k["verified_incidents"],
        "citations": k["citation_count"],
        "since": k["first_date"],
        "updated": k["last_date"],
        "url": "/tool",
    })


@app.get("/api/stats")
def stats():
    c = con()
    k = _counter(c)
    k["by_category"] = {r["category"]: r["n"] for r in c.execute(
        "SELECT category, COUNT(*) n FROM incidents WHERE status='verified' "
        "GROUP BY category ORDER BY n DESC")}
    k["by_category_money"] = {r["category"]: r["s"] for r in c.execute(
        "SELECT category, SUM(flow_to_trump+cost_to_public) s FROM incidents "
        "WHERE status='verified' GROUP BY category ORDER BY s DESC")}
    k["top_incidents"] = [dict(r) for r in c.execute(
        "SELECT slug,title,event_date,flow_to_trump,cost_to_public FROM incidents "
        "WHERE status='verified' ORDER BY (flow_to_trump+cost_to_public) DESC LIMIT 10")]
    k["sources"] = [dict(r) for r in c.execute(
        "SELECT s.slug,s.name,s.tier,COUNT(ci.id) citations FROM sources s "
        "LEFT JOIN citations ci ON ci.source_slug=s.slug GROUP BY s.slug ORDER BY s.tier")]
    k["last_run"] = dict(c.execute(
        "SELECT source_slug,started_at,ok,items_seen,items_new FROM ingest_runs "
        "ORDER BY id DESC LIMIT 1").fetchone() or {})
    return jsonify(k)


@app.get("/api/incidents")
def incidents():
    c = con()
    q = (request.args.get("q") or "").strip()
    cat = request.args.get("category")
    status = request.args.get("status", "verified")
    ledger = request.args.get("ledger")
    sort = request.args.get("sort", "date")
    limit = min(int(request.args.get("limit", 100)), 500)
    offset = int(request.args.get("offset", 0))

    where, params = ["merged_into IS NULL"], []
    if status and status != "all":
        where.append("status=?"); params.append(status)
    if cat and cat != "all":
        where.append("category=?"); params.append(cat)
    if q:
        where.append("(title LIKE ? OR summary LIKE ? OR actors LIKE ?)")
        params += [f"%{q}%"] * 3
    if ledger == "flow":
        where.append("flow_to_trump>0")
    elif ledger == "public":
        where.append("cost_to_public>0")
    elif ledger == "money":
        where.append("(flow_to_trump>0 OR cost_to_public>0)")

    order = {"date": "event_date DESC NULLS LAST",
             "date_asc": "event_date ASC NULLS LAST",
             "amount": "(flow_to_trump+cost_to_public) DESC",
             "confidence": "confidence DESC"}.get(sort, "event_date DESC NULLS LAST")

    sql = f"SELECT * FROM incidents WHERE {' AND '.join(where)} ORDER BY {order} LIMIT ? OFFSET ?"
    rows = c.execute(sql, (*params, limit, offset)).fetchall()
    total = c.execute(f"SELECT COUNT(*) n FROM incidents WHERE {' AND '.join(where)}",
                      params).fetchone()["n"]
    out = []
    for r in rows:
        d = dict(r)
        d["actors"] = json.loads(r["actors"]) if r["actors"] else []
        d["citations"] = [dict(x) for x in c.execute(
            "SELECT url,publisher,title,tier FROM citations WHERE incident_id=? ORDER BY tier",
            (r["id"],))]
        out.append(d)
    return jsonify({"total": total, "limit": limit, "offset": offset, "incidents": out})


@app.get("/api/incident/<slug>")
def incident(slug):
    c = con()
    r = c.execute("SELECT * FROM incidents WHERE slug=?", (slug,)).fetchone()
    if not r:
        return jsonify({"error": "not found"}), 404
    d = dict(r)
    d["actors"] = json.loads(r["actors"]) if r["actors"] else []
    d["citations"] = [dict(x) for x in c.execute(
        "SELECT * FROM citations WHERE incident_id=? ORDER BY tier", (r["id"],))]
    return jsonify(d)


@app.get("/api/timeline")
def timeline():
    c = con()
    rows = c.execute(
        """SELECT substr(event_date,1,7) m, COUNT(*) n,
                  SUM(flow_to_trump) flow, SUM(cost_to_public) public
           FROM incidents WHERE status='verified' AND event_date IS NOT NULL
           GROUP BY m ORDER BY m""").fetchall()
    run_n = run_m = 0
    out = []
    for r in rows:
        run_n += r["n"]; run_m += (r["flow"] or 0) + (r["public"] or 0)
        out.append({"month": r["m"], "incidents": r["n"],
                    "flow": r["flow"] or 0, "public": r["public"] or 0,
                    "cumulative_incidents": run_n, "cumulative_money": run_m})
    return jsonify({"months": out})


@app.get("/api/history")
def history():
    """Counter value at each ingest run — proves it's live, not a static number."""
    c = con()
    rows = c.execute("""SELECT started_at, source_slug, items_new FROM ingest_runs
                        WHERE ok=1 ORDER BY id DESC LIMIT 60""").fetchall()
    return jsonify({"runs": [dict(r) for r in rows], "current": _counter(c)})


INTEREST_START = "2025-01-20"  # second inauguration


@app.get("/api/interest")
def interest():
    """Documented corruption principal accruing interest, live.

    Shows how much the money already documented would have grown if sitting in a
    money-market account since the second inauguration. Rate is an explicit,
    conservative ESTIMATE (default ~3.5% APY, override with ?rate=0.05 etc.).
    """
    c = con()
    k = _counter(c)
    principal = k["flow_to_trump"] + k["cost_to_public"]  # money already "in the bank"
    annual = float(request.args.get("rate", 0.035))
    daily = annual / 365.0
    start_s = request.args.get("start", INTEREST_START)
    try:
        d0 = datetime.date.fromisoformat(start_s)
    except ValueError:
        d0 = datetime.date.fromisoformat(INTEREST_START)
    today = datetime.date.today()
    days = (today - d0).days
    accrued = principal * ((1 + daily) ** max(days, 0) - 1)
    return jsonify({
        "principal": principal,
        "annual_rate": annual,
        "daily_rate": daily,
        "start_date": d0.isoformat(),
        "days": max(days, 0),
        "accrued_interest": accrued,
        "total_with_interest": principal + accrued,
        "per_day": principal * daily,
        "as_of": today.isoformat(),
        "note": ("Estimate: documented principal compounding at "
                 f"{annual*100:.1f}% APY since {d0.isoformat()}. Assumption is labeled, not a fact."),
    })


@app.get("/api/overlay")
def overlay():
    c = con()
    k = _counter(c)
    latest = c.execute("""SELECT slug,title,event_date,flow_to_trump,cost_to_public
                          FROM incidents WHERE status='verified'
                          ORDER BY event_date DESC LIMIT 1""").fetchone()
    return jsonify({"counter": k, "latest": dict(latest) if latest else None})


@app.get("/healthz")
def healthz():
    try:
        n = con().execute("SELECT COUNT(*) n FROM incidents").fetchone()["n"]
        return jsonify({"ok": True, "incidents": n})
    except Exception as e:
        return jsonify({"ok": False, "error": repr(e)}), 500


@app.get("/tool")
@app.get("/")
def tool():
    return send_from_directory(WEB, "index.html")


@app.get("/<path:p>")
def assets(p):
    return send_from_directory(WEB, p)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8910, debug=False)
