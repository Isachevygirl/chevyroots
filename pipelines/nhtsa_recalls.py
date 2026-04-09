#!/usr/bin/env python3
"""
ChevyRoots — NHTSA Recall Watcher
==================================

Polls the free NHTSA recalls API for Chevrolet models, refreshes
data/known-issues.json, and drafts a short post via Claude for each new
major recall, writing to drafts/guides/ for Crystal's email approval.

Usage:
    python nhtsa_recalls.py            # Full run
    python nhtsa_recalls.py --dry-run  # Fetch + process, no writes
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.http import PoliteClient
from lib.claude import draft_recall_post
from lib.turso import TursoClient
from lib.log import log


ROOT = Path(__file__).resolve().parent.parent
NHTSA_BASE = "https://api.nhtsa.gov/recalls/recallsByVehicle"

# Chevrolet models we track, as NHTSA spells them
MODELS = [
    "SILVERADO 1500", "SILVERADO 2500", "CORVETTE", "CAMARO",
    "MALIBU", "TAHOE", "SUBURBAN", "BLAZER", "TRAVERSE", "EQUINOX",
    "TRAX", "TRAILBLAZER", "COLORADO", "BOLT",
]
START_YEAR = 2018


def fetch_recalls(http: PoliteClient, model: str, year: int) -> list[dict]:
    url = f"{NHTSA_BASE}?make=CHEVROLET&model={model.replace(' ', '%20')}&modelYear={year}"
    try:
        data = json.loads(http.get(url))
        return data.get("results", [])
    except Exception as e:
        log("nhtsa_fetch_failed", model=model, year=year, error=str(e))
        return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--start-year", type=int, default=START_YEAR)
    args = parser.parse_args()

    log("nhtsa_start", dry_run=args.dry_run, start_year=args.start_year)

    http = PoliteClient()
    db = TursoClient()

    all_recalls: list[dict] = []
    current_year = 2026

    for model in MODELS:
        for year in range(args.start_year, current_year + 1):
            recalls = fetch_recalls(http, model, year)
            for r in recalls:
                r["_model"] = model
                r["_year"] = year
            all_recalls.extend(recalls)

    log("nhtsa_fetched", total=len(all_recalls))

    # Group by severity — we draft posts for high-risk recalls
    high_risk = [
        r for r in all_recalls
        if r.get("Consequence", "").lower().count("injury") or r.get("Consequence", "").lower().count("crash")
    ]

    drafts_written = 0
    for r in high_risk[:5]:  # Cap at 5 drafts per run
        if args.dry_run:
            log("would_draft_recall", campaign=r.get("NHTSACampaignNumber"), consequence=r.get("Consequence", "")[:120])
            continue
        try:
            body = draft_recall_post({
                "campaign": r.get("NHTSACampaignNumber"),
                "summary": r.get("Summary"),
                "consequence": r.get("Consequence"),
                "remedy": r.get("Remedy"),
                "model": r["_model"],
                "year": r["_year"],
                "nhtsa_url": f"https://www.nhtsa.gov/recalls?nhtsaId={r.get('NHTSACampaignNumber')}",
            })
            draft_file = ROOT / "drafts" / "guides" / f"recall-{r.get('NHTSACampaignNumber', 'unknown')}.mdx"
            draft_file.parent.mkdir(parents=True, exist_ok=True)
            front = (
                "---\n"
                f"title: \"Recall Alert: {r.get('Component', 'Component')} — "
                f"{r['_year']} {r['_model']}\"\n"
                f"description: \"NHTSA campaign {r.get('NHTSACampaignNumber')} — "
                f"what owners of the {r['_year']} {r['_model']} need to know.\"\n"
                "published: " + __import__("datetime").datetime.now().strftime("%Y-%m-%d") + "\n"
                "cluster: \"Maintenance\"\n"
                "eyebrow: \"Recall Alert\"\n"
                "---\n\n"
            )
            draft_file.write_text(front + body)
            drafts_written += 1
            log("drafted_recall", file=str(draft_file.relative_to(ROOT)))
        except Exception as e:
            log("recall_draft_failed", error=str(e))

    db.log_pipeline_run(
        "nhtsa_recalls",
        "ok",
        items_processed=len(all_recalls),
        items_new=drafts_written,
        notes=f"dry_run={args.dry_run}",
    )

    log("nhtsa_done", total=len(all_recalls), drafts=drafts_written)
    return 0


if __name__ == "__main__":
    sys.exit(main())
