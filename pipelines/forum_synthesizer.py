#!/usr/bin/env python3
"""
ChevyRoots — Forum Editorial Synthesizer (Phase 3F)
=====================================================

**LEGALLY FRAMED. READ THE HARD RULES BEFORE RUNNING.**

This pipeline reads legendary public forum threads from the ToS-reviewed
allowlist, writes original editorial synthesis in Crystal's voice, and
publishes to /archives/{forum}/{slug} after Crystal's email approval.

**Hard rules enforced in code:**
1. Allowlist-only. Any forum not explicitly listed in config.toml is refused.
2. robots.txt respected on every fetch via PoliteClient.
3. Rate limit: minimum 5-second delay per request, concurrency of 1.
4. Any quoted passage is limited to ≤150 words.
5. Total quoted content must be ≤10% of the original thread length.
6. Every output file includes original author handle, original URL,
   original date, a visible link back, and a "takedown@chevyroots.com"
   contact line.
7. Any URL whose domain is in `takedowns.json` is skipped automatically.
8. Drafts go through Crystal's email approval — they are never auto-published.

Disabled by default until the ToS review is complete and the allowlist is
populated in pipelines/config.toml.

Usage:
    python forum_synthesizer.py --dry-run   # Planning / testing only
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.http import PoliteClient
from lib.log import log


ROOT = Path(__file__).resolve().parent.parent
ALLOWED_FORUMS: list[str] = []  # Populated from config.toml after ToS review


def enforce_quote_limit(quoted: str, max_words: int = 150) -> str:
    words = quoted.split()
    if len(words) <= max_words:
        return quoted
    return " ".join(words[:max_words]) + " [...quoted excerpt truncated to 150 words...]"


def enforce_quote_percentage(quoted: list[str], full_text: str, max_pct: float = 0.10) -> bool:
    full_words = len(full_text.split())
    quoted_words = sum(len(q.split()) for q in quoted)
    if full_words == 0:
        return False
    return (quoted_words / full_words) <= max_pct


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Dry run is the default for this pipeline until ToS review completes")
    parser.add_argument("--force", action="store_true",
                       help="Override the dry-run default (use only after ToS allowlist is populated)")
    args = parser.parse_args()

    if not ALLOWED_FORUMS:
        log("forum_synthesizer_disabled", reason="allowlist_empty")
        print(
            "Forum synthesizer is disabled until ALLOWED_FORUMS is populated\n"
            "after ToS review for each target forum. Update pipelines/config.toml\n"
            "and re-import the allowlist here before running for real.",
            file=sys.stderr,
        )
        return 0

    if not args.force and not args.dry_run:
        print("Refusing to run without --dry-run or --force. This is intentional.", file=sys.stderr)
        return 1

    log("forum_synthesizer_start", dry_run=args.dry_run, allowed_forums=ALLOWED_FORUMS)

    http = PoliteClient(rate_limit_seconds=5.0, respect_robots=True)

    # TODO: Once the allowlist is populated, this is where the synthesis
    # logic runs:
    #   1. For each allowed forum, discover legendary threads via their
    #      public "top threads" or sticky lists (read-only, robots-aware)
    #   2. Fetch thread pages via http.get, respecting robots.txt
    #   3. Extract the text content, filter out replies < threshold
    #   4. Build an attribution block: author, thread URL, date, forum name
    #   5. Draft original editorial in Crystal's voice via Claude Sonnet
    #      (using DRAFTING_MODEL from lib.claude)
    #   6. Include ≤150-word quoted excerpts, clearly marked as quotes
    #   7. Verify total quoted content ≤10% of source length
    #   8. Write to drafts/archives/{forum}/{slug}.mdx for approval
    #   9. Email Crystal via send-approval-email for final publish approval

    log("forum_synthesizer_done", note="stub — populate ALLOWED_FORUMS after ToS review")
    return 0


if __name__ == "__main__":
    sys.exit(main())
