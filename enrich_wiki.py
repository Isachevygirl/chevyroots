#!/usr/bin/env python3
"""Enrich Wikimedia catalog and merge into master catalog."""

import json
import sys
sys.path.insert(0, "/Users/crystalarriaga/chevyroots")
from enrich_tags import enrich_entry

WIKI_CATALOG = "/Users/crystalarriaga/chevyroots/photos/catalog.json"
WIKI_TAGGED = "/Users/crystalarriaga/chevyroots/photos/catalog_wiki_tagged.json"
PEXELS_TAGGED = "/Users/crystalarriaga/chevyroots/photos/catalog_pexels_tagged.json"
MASTER = "/Users/crystalarriaga/chevyroots/photos/catalog_master.json"

with open(WIKI_CATALOG) as f:
    wiki = json.load(f)

print(f"Enriching {len(wiki)} Wikimedia entries...")
wiki_enriched = [enrich_entry(e) for e in wiki]

with open(WIKI_TAGGED, "w") as f:
    json.dump(wiki_enriched, f, indent=2)

with open(PEXELS_TAGGED) as f:
    pexels = json.load(f)

master = pexels + wiki_enriched
with open(MASTER, "w") as f:
    json.dump(master, f, indent=2)

from collections import Counter
cats = Counter(e["category"] for e in master)
print(f"\nMaster catalog: {len(master)} total photos")
print("Breakdown:")
for cat, count in cats.most_common():
    print(f"  {cat}: {count}")
