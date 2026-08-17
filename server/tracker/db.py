"""SQLite layer for the corruption tracker."""
from __future__ import annotations
import sqlite3, hashlib, json, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = pathlib.Path(__import__("os").environ.get(
    "CORRUPTION_DB", ROOT / "data" / "corruption.db"))
SCHEMA = pathlib.Path(__file__).with_name("schema.sql")

SOURCES = [
    ("representus", "RepresentUs Trump Corruption Tracker",
     "https://represent.us/trump-corruption-tracker/", 1, "tracker"),
    ("crew", "Citizens for Responsibility and Ethics in Washington",
     "https://www.citizensforethics.org/", 1, "database"),
    ("clc", "Campaign Legal Center conflicts tracker",
     "https://campaignlegal.org/trump-administration-conflicts-of-interest", 1, "tracker"),
    ("propublica", "ProPublica conflicts-of-interest database",
     "https://www.propublica.org/", 1, "database"),
    ("kleptocracy", "SNF Agora Kleptocracy Tracker Timeline (JHU)",
     "https://snfagora.jhu.edu/our-work/research-projects/kleptocracy-tracker-timeline/", 2, "tracker"),
    ("brennan", "Brennan Center, Corruption in America",
     "https://www.brennancenter.org/series/corruption-america", 2, "tracker"),
    ("legacy", "Pre-existing hardcoded instances.ts list", None, 3, "press"),
]


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def connect(path: pathlib.Path | str = DB_PATH) -> sqlite3.Connection:
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con


def init(con: sqlite3.Connection) -> None:
    con.executescript(SCHEMA.read_text(encoding="utf-8"))
    for slug, name, url, tier, kind in SOURCES:
        con.execute(
            "INSERT OR IGNORE INTO sources(slug,name,url,tier,kind) VALUES(?,?,?,?,?)",
            (slug, name, url, tier, kind))
    con.commit()


def content_hash(*parts) -> str:
    return hashlib.sha256("|".join(str(p or "") for p in parts).encode()).hexdigest()


def add_raw(con, source_slug, title, body=None, link=None, event_date=None,
            external_id=None, raw=None) -> int | None:
    """Insert a scraped item. Returns rowid, or None if already seen."""
    h = content_hash(source_slug, event_date, title, link)
    try:
        cur = con.execute(
            """INSERT INTO raw_items(source_slug,external_id,fetched_at,event_date,
               title,body,link,raw_json,content_hash) VALUES(?,?,?,?,?,?,?,?,?)""",
            (source_slug, external_id, now(), event_date, title, body, link,
             json.dumps(raw or {}), h))
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def start_run(con, slug) -> int:
    cur = con.execute("INSERT INTO ingest_runs(source_slug,started_at) VALUES(?,?)",
                      (slug, now()))
    con.commit()
    return cur.lastrowid


def finish_run(con, run_id, ok=True, seen=0, new=0, error=None) -> None:
    con.execute("""UPDATE ingest_runs SET finished_at=?,ok=?,items_seen=?,
                   items_new=?,error=? WHERE id=?""",
                (now(), 1 if ok else 0, seen, new, error, run_id))
    con.commit()


def upsert_incident(con, **f) -> int:
    f.setdefault("created_at", now())
    f["updated_at"] = now()
    if isinstance(f.get("actors"), list):
        f["actors"] = json.dumps(f["actors"])
    cols = ",".join(f)
    ph = ",".join("?" * len(f))
    cur = con.execute(f"INSERT INTO incidents({cols}) VALUES({ph})", tuple(f.values()))
    return cur.lastrowid


def add_citation(con, incident_id, url, **f) -> None:
    f.setdefault("added_at", now())
    f["incident_id"] = incident_id
    f["url"] = url
    cols = ",".join(f)
    ph = ",".join("?" * len(f))
    try:
        con.execute(f"INSERT INTO citations({cols}) VALUES({ph})", tuple(f.values()))
    except sqlite3.IntegrityError:
        pass
