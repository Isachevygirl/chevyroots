# ChevyRoots Content Pipelines

Python scripts that keep the ChevyRoots content engine running automatically.
All pipelines are scheduled via GitHub Actions and run against the repo itself
(free unlimited minutes for public repos).

Every pipeline follows the same pattern:
1. Fetch new items from a source (RSS, API, HTML scrape with rate limiting)
2. Dedupe against what's already in Turso or the JSON data files
3. Run through Claude for summarization, editorial framing, or tag extraction
4. Write the result (either a commit to the repo that Netlify picks up, or
   a row in Turso that the live site reads)
5. Log the run to the `pipeline_runs` table in Turso and alert via Resend
   on failure

## Pipelines

| File | Schedule | What it does |
|---|---|---|
| `news_aggregator.py` | Nightly | RSS poll of 70+ automotive sources → dedupe → summarize → append to news_articles.json |
| `nhtsa_recalls.py` | Weekly | NHTSA public API → refresh known-issues.json for Chevy models → draft recall alerts |
| `reddit_listener.py` | Daily | PRAW (sanctioned API) watches r/Chevy, r/Silverado, r/Corvette etc → flags top questions as content ideas |
| `bat_auction.py` | Weekly | Bring a Trailer + Hemmings RSS filtered for Chevy → weekly "This Week in Chevy Auctions" draft |
| `event_scraper.py` | Weekly | Goodguys, NHRA, SEMA, Hagerty, regional calendars → updates regional event JSON files |
| `forum_synthesizer.py` | Weekly | Editorial synthesis of public forum threads (CorvetteForum, ChevyTalk, GM-Trucks) → original articles with ≤150 word quoted excerpts + full attribution + takedown link |
| `takedown_processor.py` | Hourly | Checks takedowns table, removes matching content within 24h |
| `photo_enricher.py` | On-commit | Runs enrich_tags.py against any new photos in /photos/new/ |

## Common library

`pipelines/lib/` contains shared helpers:
- `http.py` — polite HTTP client with robots.txt check, rate limiting,
  identified User-Agent
- `claude.py` — Claude API wrapper for summarization/drafting
- `turso.py` — Turso DB helper using the libsql-client for Python
- `resend.py` — Resend wrapper for alert emails
- `log.py` — structured JSON logging + Turso run logging
- `attribution.py` — builds attribution blocks for forum-derived content

## Environment

Required environment variables are the same as the rest of the stack — see
`.env.example` at the repo root. GitHub Actions reads them from encrypted
secrets (`gh secret set`).

## Local testing

Every pipeline supports `--dry-run`:

```sh
cd pipelines
python news_aggregator.py --dry-run
```

Dry run mode fetches everything, processes everything, but doesn't commit
or write to the database. Useful for validating changes before pushing.

## Legal guardrails

- Every scraper reads robots.txt first and respects it
- Rate limiting: minimum 5-second delay per request, concurrency of 1 per
  domain, identified User-Agent with contact email
- Forum synthesis: max 150 words per quoted passage, total quoted content
  kept under 10% of original thread length, full attribution required
- Takedown requests honored within 24 hours via `takedown_processor.py`
- Per-source allowlist in `pipelines/config.toml` — only sources that pass
  ToS review are enabled
