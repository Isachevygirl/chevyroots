-- Turso (libSQL) schema for ChevyRoots dynamic functions.
-- Run once against the production Turso database:
--   turso db shell chevyroots < schema.sql

-- ── Affiliate tracking ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS affiliate_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  retailer TEXT NOT NULL,
  slug TEXT NOT NULL,
  url TEXT NOT NULL,
  utm_campaign TEXT,
  commission_rate REAL,
  added_at TEXT DEFAULT (datetime('now')),
  UNIQUE(retailer, slug)
);

CREATE TABLE IF NOT EXISTS affiliate_clicks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  retailer TEXT NOT NULL,
  slug TEXT NOT NULL,
  ts TEXT DEFAULT (datetime('now')),
  referrer TEXT,
  country TEXT,
  ua_class TEXT
);

CREATE INDEX IF NOT EXISTS idx_clicks_retailer_slug ON affiliate_clicks(retailer, slug);
CREATE INDEX IF NOT EXISTS idx_clicks_ts ON affiliate_clicks(ts);

-- ── User submissions (moderation queue) ────────────────────────────────
CREATE TABLE IF NOT EXISTS builds_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  location TEXT,
  year_model TEXT NOT NULL,
  build_name TEXT,
  story TEXT NOT NULL,
  specs TEXT,
  social TEXT,
  photos_r2_keys TEXT,  -- JSON array of R2 object keys
  submitted_at TEXT DEFAULT (datetime('now')),
  status TEXT DEFAULT 'pending',  -- pending | approved | rejected
  reviewed_at TEXT,
  reviewer_notes TEXT
);

CREATE TABLE IF NOT EXISTS events_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_name TEXT NOT NULL,
  event_dates TEXT NOT NULL,
  venue TEXT,
  city TEXT NOT NULL,
  state TEXT NOT NULL,
  event_type TEXT,
  chevy_focus TEXT,
  description TEXT,
  url TEXT,
  submitter_email TEXT NOT NULL,
  submitted_at TEXT DEFAULT (datetime('now')),
  status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS mechanic_reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mechanic_id TEXT NOT NULL,
  author_name TEXT,
  author_email TEXT,
  rating INTEGER,
  body TEXT,
  submitted_at TEXT DEFAULT (datetime('now')),
  status TEXT DEFAULT 'pending'
);

-- ── Comments ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  article_slug TEXT NOT NULL,
  author_email TEXT NOT NULL,
  author_name TEXT,
  body TEXT NOT NULL,
  submitted_at TEXT DEFAULT (datetime('now')),
  approved INTEGER DEFAULT 0,
  parent_id INTEGER REFERENCES comments(id)
);

CREATE INDEX IF NOT EXISTS idx_comments_article ON comments(article_slug, approved);

-- ── Approval workflow ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS consumed_tokens (
  jti TEXT PRIMARY KEY,
  consumed_at TEXT DEFAULT (datetime('now'))
);

-- ── Magic-link auth (Phase 5) ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  display_name TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  last_seen_at TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
  token TEXT PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  created_at TEXT DEFAULT (datetime('now')),
  expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS roles (
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  role TEXT,  -- user | moderator | admin
  PRIMARY KEY (user_id, role)
);

-- ── Content-idea queue (Phase 3 pipelines write here) ─────────────────
CREATE TABLE IF NOT EXISTS content_ideas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,  -- reddit | forum | nhtsa | auction | news | user
  url TEXT,
  topic TEXT,
  raw_summary TEXT,
  suggested_angle TEXT,
  priority INTEGER DEFAULT 0,
  first_seen TEXT DEFAULT (datetime('now')),
  status TEXT DEFAULT 'new'  -- new | queued | drafting | published | rejected
);

CREATE INDEX IF NOT EXISTS idx_ideas_status ON content_ideas(status);
CREATE INDEX IF NOT EXISTS idx_ideas_priority ON content_ideas(priority DESC);

-- ── Pipeline runs observability ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS pipeline_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pipeline TEXT NOT NULL,
  started_at TEXT DEFAULT (datetime('now')),
  completed_at TEXT,
  status TEXT,  -- running | ok | failed
  items_processed INTEGER DEFAULT 0,
  items_new INTEGER DEFAULT 0,
  error TEXT,
  notes TEXT
);

-- ── Video stats (Phase 4) ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS video_stats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_slug TEXT NOT NULL,
  platform TEXT NOT NULL,  -- youtube | instagram | tiktok
  views INTEGER,
  likes INTEGER,
  shares INTEGER,
  comments INTEGER,
  recorded_at TEXT DEFAULT (datetime('now'))
);

-- ── Takedowns (Phase 3 forum archive) ─────────────────────────────────
CREATE TABLE IF NOT EXISTS takedowns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  target_url TEXT NOT NULL,
  requester_email TEXT,
  reason TEXT,
  received_at TEXT DEFAULT (datetime('now')),
  handled_at TEXT,
  status TEXT DEFAULT 'pending'  -- pending | handled | rejected
);
