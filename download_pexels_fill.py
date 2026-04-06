#!/usr/bin/env python3
"""Download additional Chevy photos for underrepresented categories."""

import json
import os
import time
import urllib.request
import urllib.parse
import ssl

API_KEY = "wCGh74JHac23EGDqZPPjgiPhdd8ZAAK6QjWNpXL9tiYjLeI13H3TFA2N"
BASE_DIR = "/Users/crystalarriaga/chevyroots/photos"

# Targeted searches with desired NEW photo counts
SEARCHES = {
    "silverado": {
        "queries": ["chevrolet silverado 2024", "silverado pickup", "chevy silverado off road"],
        "need": 10,
    },
    "tahoe": {
        "queries": ["chevrolet tahoe suv", "chevy tahoe 2024"],
        "need": 5,
    },
    "camaro": {
        "queries": ["chevrolet camaro zl1", "camaro muscle car", "chevy camaro red"],
        "need": 8,
    },
    "suburban": {
        "queries": ["chevrolet suburban", "chevy suburban black"],
        "need": 3,
    },
    "colorado": {
        "queries": ["chevrolet colorado zr2", "chevy colorado truck"],
        "need": 3,
    },
    "trucks-classic": {
        "queries": ["chevy c10 pickup", "classic chevy truck restored", "1960s chevrolet truck"],
        "need": 5,
    },
    "blazer": {
        "queries": ["chevrolet blazer ev", "chevy blazer 2024", "chevy k5 blazer"],
        "need": 3,
    },
    "trucks-modern": {
        "queries": ["chevy truck", "chevrolet pickup truck modern", "chevy work truck"],
        "need": 5,
    },
}

ctx = ssl.create_default_context()


def pexels_search(query, per_page=40, page=1):
    params = urllib.parse.urlencode({
        "query": query, "per_page": str(per_page), "page": str(page),
    })
    url = f"https://api.pexels.com/v1/search?{params}"
    req = urllib.request.Request(url, headers={
        "Authorization": API_KEY, "User-Agent": "ChevyRoots/1.0",
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return json.loads(resp.read()).get("photos", [])
    except Exception as e:
        print(f"  Search error for '{query}': {e}")
        return []


def download_image(url, filepath):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        })
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  Download error: {e}")
        return False


def get_existing_ids(cat_dir):
    ids = set()
    if os.path.exists(cat_dir):
        for fname in os.listdir(cat_dir):
            if fname.startswith("pexels_"):
                parts = fname.split("_")
                if len(parts) >= 2:
                    try:
                        ids.add(int(parts[1]))
                    except ValueError:
                        pass
    return ids


def main():
    total = 0
    for category, info in SEARCHES.items():
        cat_dir = os.path.join(BASE_DIR, category)
        os.makedirs(cat_dir, exist_ok=True)
        existing_ids = get_existing_ids(cat_dir)
        needed = info["need"]
        downloaded = 0

        print(f"\n{'='*50}")
        print(f"{category}: need {needed} new photos (have {len(existing_ids)} existing)")
        print(f"{'='*50}")

        for query in info["queries"]:
            if downloaded >= needed:
                break
            for page in range(1, 3):
                if downloaded >= needed:
                    break
                print(f"  Searching: '{query}' page {page}")
                photos = pexels_search(query, per_page=15, page=page)
                print(f"  Got {len(photos)} results")

                for photo in photos:
                    if downloaded >= needed:
                        break
                    pid = photo["id"]
                    if pid in existing_ids:
                        continue
                    existing_ids.add(pid)

                    img_url = photo.get("src", {}).get("large", "")
                    if not img_url:
                        continue

                    filename = f"pexels_{pid}_{category}.jpeg"
                    filepath = os.path.join(cat_dir, filename)
                    photographer = photo.get("photographer", "Unknown")

                    print(f"    [{downloaded+1}/{needed}] {filename} by {photographer}")
                    if download_image(img_url, filepath):
                        downloaded += 1
                        total += 1
                    time.sleep(0.5)

                time.sleep(1)

        print(f"  => Downloaded {downloaded}/{needed} for {category}")

    print(f"\nDone! Downloaded {total} new photos total.")


if __name__ == "__main__":
    main()
