"""One command to refresh everything:  python -m tracker.refresh"""
from __future__ import annotations
import json, traceback
from . import db, import_legacy, normalize, export, seed_verified, dedupe, seed_research
from . import ingest_representus

INGESTORS = [ingest_representus]


def main() -> None:
    con = db.connect()
    db.init(con)
    report = {"ingest": {}, }
    import_legacy.run(con)
    for mod in INGESTORS:
        name = mod.SLUG
        try:
            report["ingest"][name] = mod.run(con)
        except Exception as e:
            report["ingest"][name] = {"error": repr(e)}
            traceback.print_exc()
    report["normalize"] = normalize.run(con)
    report["seed"] = seed_verified.run(con)
    report["seed_research"] = seed_research.run(con)
    report["dedupe"] = dedupe.run(con)
    report["export"] = export.run(con)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
