#!/usr/bin/env python3
"""Download and categorize free Chevy photos from Pexels API."""

import json
import os
import time
import urllib.request
import urllib.parse
import ssl

API_KEY = "wCGh74JHac23EGDqZPPjgiPhdd8ZAAK6QjWNpXL9tiYjLeI13H3TFA2N"
BASE_DIR = "/Users/crystalarriaga/chevyroots/photos"
CATALOG_FILE = "/Users/crystalarriaga/chevyroots/photos/catalog_pexels.json"

SEARCHES = {
    "corvette": ["chevrolet corvette", "corvette stingray", "corvette car"],
    "camaro": ["chevrolet camaro", "camaro ss", "camaro car"],
    "silverado": ["chevrolet silverado", "silverado truck"],
    "impala": ["chevrolet impala", "impala car classic"],
    "chevelle": ["chevrolet chevelle", "chevelle ss"],
    "belair": ["chevrolet bel air", "1957 chevy"],
    "colorado": ["chevrolet colorado truck"],
    "tahoe": ["chevrolet tahoe"],
    "suburban": ["chevrolet suburban"],
    "malibu": ["chevrolet malibu car"],
    "blazer": ["chevrolet blazer", "chevy blazer"],
    "s10": ["chevrolet s10"],
    "nova": ["chevrolet nova"],
    "monte-carlo": ["chevrolet monte carlo"],
    "equinox": ["chevrolet equinox"],
    "bolt": ["chevrolet bolt ev"],
    "trucks-classic": ["classic chevy truck", "vintage chevrolet pickup", "chevy c10"],
    "trucks-modern": ["chevy truck", "chevrolet pickup truck"],
    "classic-misc": ["classic chevrolet", "vintage chevy car", "chevy el camino"],
    "modern-misc": ["chevrolet suv", "chevy trailblazer", "chevrolet traverse"],
}

ctx = ssl.create_default_context()


def pexels_search(query, per_page=40, page=1):
    """Search Pexels API for photos."""
    params = urllib.parse.urlencode({
        "query": query,
        "per_page": str(per_page),
        "page": str(page),
    })
    url = f"https://api.pexels.com/v1/search?{params}"
    req = urllib.request.Request(url, headers={
        "Authorization": API_KEY,
        "User-Agent": "ChevyRoots/1.0"
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("photos", [])
    except Exception as e:
        print(f"  Search error for '{query}': {e}")
        return []


def download_image(url, filepath):
    """Download an image."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  Download error: {e}")
        return False


def main():
    catalog = []
    seen_ids = set()
    total = 0

    for category, queries in SEARCHES.items():
        cat_dir = os.path.join(BASE_DIR, category)
        os.makedirs(cat_dir, exist_ok=True)
        print(f"\n{'='*60}")
        print(f"Category: {category}")
        print(f"{'='*60}")

        for query in queries:
            # Fetch 2 pages per query (up to 80 photos)
            for page in range(1, 3):
                print(f"\n  Searching: '{query}' (page {page})")
                photos = pexels_search(query, per_page=40, page=page)
                print(f"  Found {len(photos)} results")

                if not photos:
                    break

                for photo in photos:
                    pid = photo["id"]
                    if pid in seen_ids:
                        continue
                    seen_ids.add(pid)

                    # Use "large" size (940px wide) for good quality without huge files
                    img_url = photo.get("src", {}).get("large", "")
                    if not img_url:
                        continue

                    photographer = photo.get("photographer", "Unknown")
                    alt = photo.get("alt", "")
                    w = photo.get("width", 0)
                    h = photo.get("height", 0)
                    pexels_url = photo.get("url", "")

                    filename = f"pexels_{pid}_{category}.jpeg"
                    filepath = os.path.join(cat_dir, filename)

                    if os.path.exists(filepath):
                        continue

                    print(f"    Downloading: {filename} by {photographer}")
                    if download_image(img_url, filepath):
                        entry = {
                            "file": f"{category}/{filename}",
                            "category": category,
                            "search_query": query,
                            "title": alt or f"Pexels photo {pid}",
                            "license": "Pexels License (free commercial use, no attribution required)",
                            "artist": photographer,
                            "description": alt[:200] if alt else "",
                            "source_url": pexels_url,
                            "pexels_id": pid,
                            "width": w,
                            "height": h,
                            "tags": [category, query],
                        }
                        catalog.append(entry)
                        total += 1

                    time.sleep(0.5)

                # Respect rate limits
                time.sleep(1)

    # Write catalog
    with open(CATALOG_FILE, "w") as f:
        json.dump(catalog, f, indent=2)

    print(f"\n{'='*60}")
    print(f"DONE! Downloaded {total} photos across {len(SEARCHES)} categories")
    print(f"Catalog saved to {CATALOG_FILE}")

    from collections import Counter
    cats = Counter(e["category"] for e in catalog)
    print(f"\nBreakdown:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count} photos")


if __name__ == "__main__":
    main()
