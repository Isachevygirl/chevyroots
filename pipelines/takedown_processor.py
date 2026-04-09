#!/usr/bin/env python3
"""
ChevyRoots — Takedown Processor
================================

Hourly cron that checks the takedowns Turso table for new removal requests
and removes matching content from the repo within 24 hours. Logs every
action for the audit trail.

Usage:
    python takedown_processor.py             # Process pending
    python takedown_processor.py --dry-run   # Show what would be removed
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.turso import TursoClient
from lib.resend import send_alert
from lib.log import log


ROOT = Path(__file__).resolve().parent.parent
CONTENT_ROOTS = [
    ROOT / "astro" / "src" / "content" / "guides",
    ROOT / "astro" / "src" / "content" / "event-reports",
    ROOT / "astro" / "src" / "content" / "crystals-corner",
]


def find_content_file(target_url: str) -> Path | None:
    """Try to resolve a target URL back to a content file in the repo."""
    if not target_url:
        return None
    slug = target_url.rstrip("/").split("/")[-1]
    for root in CONTENT_ROOTS:
        if not root.exists():
            continue
        for mdx in root.glob("**/*.mdx"):
            if mdx.stem == slug:
                return mdx
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    db = TursoClient()
    if not db.enabled:
        log("takedown_processor_no_db")
        return 0

    # Pull pending takedowns
    result = db.execute(
        "SELECT id, target_url, requester_email, reason FROM takedowns WHERE status = 'pending'",
    )

    # The Turso HTTP API response shape varies; be defensive.
    try:
        rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
    except Exception:
        rows = []

    processed = 0
    for row in rows:
        # Row format: [[{"type":"text","value":"..."},...]]
        try:
            id_, target_url, requester_email, reason = [col.get("value", "") for col in row]
        except Exception as e:
            log("takedown_row_parse_failed", error=str(e))
            continue

        log("processing_takedown", id=id_, url=target_url, reason=reason[:100])

        file = find_content_file(target_url)
        if not file:
            log("takedown_file_not_found", url=target_url)
            if not args.dry_run:
                db.execute(
                    "UPDATE takedowns SET status='handled', handled_at=datetime('now') WHERE id=?",
                    [id_],
                )
            continue

        if args.dry_run:
            log("would_delete_file", file=str(file.relative_to(ROOT)))
            continue

        try:
            file.unlink()
            db.execute(
                "UPDATE takedowns SET status='handled', handled_at=datetime('now') WHERE id=?",
                [id_],
            )
            send_alert(
                f"[ChevyRoots] Takedown processed",
                f"Removed content file: {file.relative_to(ROOT)}\n"
                f"Requester: {requester_email}\n"
                f"Reason: {reason}",
            )
            processed += 1
            log("takedown_processed", file=str(file.relative_to(ROOT)))
        except Exception as e:
            log("takedown_delete_failed", file=str(file), error=str(e))

    db.log_pipeline_run(
        "takedown_processor",
        "ok",
        items_processed=len(rows),
        items_new=processed,
    )

    log("takedown_processor_done", processed=processed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
