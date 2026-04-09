#!/usr/bin/env python3
"""
ChevyRoots — Nightly News Aggregator
=====================================

Polls RSS feeds from the configured news sources (70+ tier 1/2/3 automotive
publications), dedupes against data/news_articles.json, summarizes each new
item with Claude Haiku in 100–150 words, tags the category, and commits the
updated JSON back to the repo. Netlify auto-rebuilds.

Usage:
    python news_aggregator.py              # Full run
    python news_aggregator.py --dry-run    # Fetch + parse + summarize, no write

Environment:
    ANTHROPIC_API_KEY  (required for summarization in non-dry-run mode)
    TURSO_DB_URL       (optional; logs run metadata)
    TURSO_AUTH_TOKEN   (optional)
    RESEND_API_KEY     (optional; failure alerts)
"""

import sys
import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.http import PoliteClient
from lib.claude import summarize_news
from lib.turso import TursoClient
from lib.resend import send_alert
from lib.log import log


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "news_articles.json"
# Also update the Astro mirror if it exists
ASTRO_DATA_FILE = ROOT / "astro" / "src" / "data" / "news_articles.json"


def load_existing() -> list[dict]:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []


def parse_rss(xml_bytes: bytes, source_name: str) -> list[dict]:
    """Parse an RSS 2.0 / Atom feed into normalized dicts."""
    root = ET.fromstring(xml_bytes)
    items = []

    # RSS 2.0
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        if title and link:
            items.append({
                "title": title,
                "source": source_name,
                "url": link,
                "date": pub or datetime.now().strftime("%Y-%m-%d"),
                "raw_summary": desc,
            })

    # Atom
    atom_ns = "{http://www.w3.org/2005/Atom}"
    for entry in root.iter(f"{atom_ns}entry"):
        title = entry.findtext(f"{atom_ns}title") or ""
        link_el = entry.find(f"{atom_ns}link")
        link = link_el.get("href") if link_el is not None else ""
        content = entry.findtext(f"{atom_ns}content") or entry.findtext(f"{atom_ns}summary") or ""
        pub = entry.findtext(f"{atom_ns}published") or entry.findtext(f"{atom_ns}updated") or ""
        if title and link:
            items.append({
                "title": title.strip(),
                "source": source_name,
                "url": link,
                "date": pub[:10] if pub else datetime.now().strftime("%Y-%m-%d"),
                "raw_summary": content[:2000],
            })

    return items


def is_chevy_related(item: dict) -> bool:
    """Loose filter — keep items that mention Chevy-related terms."""
    text = (item.get("title", "") + " " + item.get("raw_summary", "")).lower()
    keywords = [
        "chevrolet", "chevy", "silverado", "corvette", "camaro", "suburban",
        "tahoe", "blazer", "equinox", "trax", "colorado", "malibu", "impala",
        "c8", "z06", "zr2", "trailboss", "stingray", "duramax", "ls swap",
        "small block", "big block", "bowtie", "gm ", " gm", "general motors",
    ]
    return any(k in text for k in keywords)


def categorize(item: dict) -> str:
    t = (item.get("title", "") + " " + item.get("raw_summary", "")).lower()
    if "recall" in t or "tsb" in t:
        return "recall"
    if "lease" in t or "incentive" in t or "deal" in t or "discount" in t:
        return "deal"
    if "ev" in t or "electric" in t or "bolt" in t or "ultium" in t:
        return "ev"
    if "race" in t or "nhra" in t or "motorsport" in t or "nascar" in t:
        return "motorsport"
    if "sema" in t or "show" in t or "restomod" in t or "classic" in t:
        return "culture"
    if "concept" in t or "reveal" in t or "announc" in t:
        return "tech"
    return "news"


def dedupe(existing: list[dict], new: list[dict]) -> list[dict]:
    seen = {item["url"] for item in existing}
    return [item for item in new if item["url"] not in seen]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-per-source", type=int, default=10)
    args = parser.parse_args()

    log("news_aggregator_start", dry_run=args.dry_run)

    db = TursoClient()
    http = PoliteClient()

    # For this scaffold, use a small built-in source list so the script works
    # even without the full config.toml parser. Expand via config.toml in
    # production.
    sources = [
        ("GM Authority", "https://gmauthority.com/blog/feed/"),
        ("Corvette Blogger", "https://www.corvetteblogger.com/feed/"),
        ("Hagerty", "https://www.hagerty.com/media/feed/"),
    ]

    existing = load_existing()
    total_found = 0
    total_new = 0
    new_items = []

    for source_name, feed_url in sources:
        try:
            log("fetching_feed", source=source_name, url=feed_url)
            xml_bytes = http.get(feed_url)
            items = parse_rss(xml_bytes, source_name)
            total_found += len(items)
            # Filter to Chevy-relevant + dedupe
            relevant = [i for i in items if is_chevy_related(i)]
            fresh = dedupe(existing, relevant)[:args.max_per_source]
            log("feed_results", source=source_name, found=len(items), relevant=len(relevant), fresh=len(fresh))
            for item in fresh:
                item["category"] = categorize(item)
                if not args.dry_run:
                    try:
                        item["summary"] = summarize_news(item["title"], item["raw_summary"])[:800]
                    except Exception as e:
                        log("summarize_failed", title=item["title"], error=str(e))
                        item["summary"] = item["raw_summary"][:300]
                else:
                    item["summary"] = item["raw_summary"][:300] + " [DRY RUN — not summarized]"
                item.pop("raw_summary", None)
                new_items.append(item)
            total_new += len(fresh)
        except Exception as e:
            log("fetch_failed", source=source_name, error=str(e))
            if not args.dry_run:
                send_alert(
                    f"[ChevyRoots] News pipeline: {source_name} failed",
                    f"Error fetching {feed_url}: {e}",
                )

    # Merge with existing
    if new_items and not args.dry_run:
        combined = new_items + existing
        # Cap at 500 most recent
        combined = combined[:500]
        DATA_FILE.write_text(json.dumps(combined, indent=2))
        if ASTRO_DATA_FILE.exists():
            ASTRO_DATA_FILE.write_text(json.dumps(combined, indent=2))
        log("wrote_file", path=str(DATA_FILE), total_items=len(combined))

    db.log_pipeline_run(
        "news_aggregator",
        "ok",
        items_processed=total_found,
        items_new=total_new,
        notes=f"dry_run={args.dry_run}",
    )

    log("news_aggregator_done", total_found=total_found, total_new=total_new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
