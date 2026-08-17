-- Corruption Counter schema. Idempotent.
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  url TEXT,
  tier INTEGER NOT NULL DEFAULT 3,   -- 0 primary gov, 1 curated watchdog, 2 institute, 3 press
  kind TEXT                          -- tracker | database | press | primary
);

-- Anything a scraper pulled, verbatim. Never edited by hand.
CREATE TABLE IF NOT EXISTS raw_items (
  id INTEGER PRIMARY KEY,
  source_slug TEXT NOT NULL,
  external_id TEXT,                  -- source's own id/anchor if any
  fetched_at TEXT NOT NULL,
  event_date TEXT,                   -- ISO yyyy-mm-dd if parseable
  title TEXT,
  body TEXT,
  link TEXT,                         -- source's cited article
  raw_json TEXT,
  content_hash TEXT UNIQUE,          -- dedupe identical re-scrapes
  processed INTEGER NOT NULL DEFAULT 0,
  incident_id INTEGER                -- set once normalized
);

-- The canonical, defensible record. This is what the counter counts.
CREATE TABLE IF NOT EXISTS incidents (
  id INTEGER PRIMARY KEY,
  slug TEXT UNIQUE,
  title TEXT NOT NULL,
  summary TEXT,
  event_date TEXT,                   -- ISO; NULL only if genuinely undated
  date_precision TEXT DEFAULT 'day', -- day | month | year | ongoing
  category TEXT,                     -- pardons|contracts|crypto|emoluments|selfdeal|
                                     -- oversight|appointments|propaganda|other
  actors TEXT,                       -- JSON array of names
  -- three separate ledgers, never blindly summed
  flow_to_trump REAL DEFAULT 0,
  cost_to_public REAL DEFAULT 0,
  deal_value REAL DEFAULT 0,
  amount_basis TEXT,                 -- how the number was derived, in words
  is_estimated INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'unverified', -- unverified|verified|disputed|rejected|merged
  confidence INTEGER DEFAULT 0,      -- 0-100
  legacy_id INTEGER,                 -- old instances.ts id
  merged_into INTEGER,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS citations (
  id INTEGER PRIMARY KEY,
  incident_id INTEGER NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
  source_slug TEXT,
  url TEXT NOT NULL,
  title TEXT,
  publisher TEXT,
  published_at TEXT,
  tier INTEGER DEFAULT 3,
  quote TEXT,
  added_at TEXT NOT NULL,
  UNIQUE(incident_id, url)
);

CREATE TABLE IF NOT EXISTS ingest_runs (
  id INTEGER PRIMARY KEY,
  source_slug TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  ok INTEGER,
  items_seen INTEGER DEFAULT 0,
  items_new INTEGER DEFAULT 0,
  error TEXT
);

CREATE INDEX IF NOT EXISTS idx_inc_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_inc_date ON incidents(event_date);
CREATE INDEX IF NOT EXISTS idx_raw_unproc ON raw_items(processed);
CREATE INDEX IF NOT EXISTS idx_cit_inc ON citations(incident_id);

-- Headline view: only what we can defend.
CREATE VIEW IF NOT EXISTS v_counter AS
SELECT
  COUNT(*)                    AS verified_incidents,
  COALESCE(SUM(flow_to_trump),0)  AS total_flow_to_trump,
  COALESCE(SUM(cost_to_public),0) AS total_cost_to_public,
  MIN(event_date)             AS first_date,
  MAX(event_date)             AS last_date
FROM incidents
WHERE status='verified' AND merged_into IS NULL;
