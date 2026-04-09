#!/usr/bin/env python3
"""
ChevyRoots — Reddit Content-Idea Listener
==========================================

Uses the sanctioned Reddit API (via PRAW) to watch the Chevy subreddits for
high-upvote question threads. Flags them as content ideas in the Turso
`content_ideas` table for Dave to review and Claude to draft.

Does NOT auto-post to Reddit. Read-only, ToS-compliant.

Usage:
    python reddit_listener.py                # Full run
    python reddit_listener.py --dry-run      # Fetch + process, no writes

Environment variables:
    REDDIT_CLIENT_ID
    REDDIT_CLIENT_SECRET
    REDDIT_USER_AGENT
"""

import sys
import os
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.turso import TursoClient
from lib.log import log


SUBREDDITS = [
    "Chevy", "Chevrolet", "Corvette", "Silverado",
    "camaro", "chevytrucks", "Cartalk",
]
MIN_UPVOTES = 50
MAX_IDEAS_PER_RUN = 30


def classify_post(post) -> tuple[str, str]:
    """Return (category, angle_suggestion) for a Reddit post."""
    title = post.title.lower()
    if "?" in title:
        return "question", f"Answer the top community question on {post.title[:100]}"
    if any(w in title for w in ["best", "top", "should i", "worth it"]):
        return "buying-decision", f"Definitive guide addressing '{post.title[:100]}'"
    if any(w in title for w in ["problem", "issue", "won't start", "noise", "broke"]):
        return "troubleshooting", f"Diagnostic walkthrough for '{post.title[:100]}'"
    if any(w in title for w in ["mod", "swap", "upgrade", "install"]):
        return "modification", f"How-to guide for '{post.title[:100]}'"
    return "general", f"Editorial take on '{post.title[:100]}'"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=25, help="Posts per subreddit")
    args = parser.parse_args()

    log("reddit_listener_start", dry_run=args.dry_run)

    try:
        import praw
    except ImportError:
        log("praw_not_installed", note="pip install praw")
        print("ERROR: praw not installed. Run: pip install praw", file=sys.stderr)
        return 1

    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "chevyroots-listener/1.0")

    if not client_id or not client_secret:
        log("reddit_credentials_missing")
        return 1

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )
    reddit.read_only = True

    db = TursoClient()
    ideas_new = 0
    total_seen = 0

    for sub_name in SUBREDDITS:
        log("scanning_subreddit", subreddit=sub_name)
        sub = reddit.subreddit(sub_name)
        for post in sub.top(time_filter="week", limit=args.limit):
            total_seen += 1
            if post.score < MIN_UPVOTES:
                continue
            if post.stickied or post.over_18:
                continue

            category, angle = classify_post(post)
            url = f"https://reddit.com{post.permalink}"
            summary = (post.selftext or post.title)[:1500]

            if args.dry_run:
                log("would_add_idea", subreddit=sub_name, title=post.title[:80], upvotes=post.score)
                continue

            try:
                db.execute(
                    """INSERT INTO content_ideas
                       (source, url, topic, raw_summary, suggested_angle, priority, first_seen, status)
                       VALUES (?, ?, ?, ?, ?, ?, datetime('now'), 'new')""",
                    ["reddit", url, post.title, summary, angle, post.score],
                )
                ideas_new += 1
            except Exception as e:
                log("insert_idea_failed", error=str(e))

            if ideas_new >= MAX_IDEAS_PER_RUN:
                break
        if ideas_new >= MAX_IDEAS_PER_RUN:
            break

    db.log_pipeline_run(
        "reddit_listener",
        "ok",
        items_processed=total_seen,
        items_new=ideas_new,
        notes=f"dry_run={args.dry_run}",
    )

    log("reddit_listener_done", total_seen=total_seen, ideas_new=ideas_new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
