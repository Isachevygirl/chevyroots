#!/usr/bin/env python3
"""Download and categorize free-to-use Chevy photos from Wikimedia Commons."""

import json
import os
import re
import time
import urllib.request
import urllib.parse
import ssl

BASE_DIR = "/Users/crystalarriaga/chevyroots/photos"
CATALOG_FILE = "/Users/crystalarriaga/chevyroots/photos/catalog.json"

# Search terms mapped to folder categories
SEARCHES = {
    "corvette": [
        "Chevrolet Corvette", "Corvette C1", "Corvette C2", "Corvette C3",
        "Corvette C4", "Corvette C5", "Corvette C6", "Corvette C7", "Corvette C8",
        "Corvette Stingray", "Corvette ZR1", "Corvette Z06"
    ],
    "camaro": [
        "Chevrolet Camaro", "Camaro SS", "Camaro Z28", "Camaro ZL1",
        "Camaro RS", "Camaro convertible"
    ],
    "silverado": [
        "Chevrolet Silverado", "Silverado 1500", "Silverado 2500",
        "Silverado HD", "Silverado EV"
    ],
    "impala": [
        "Chevrolet Impala", "Impala SS", "Chevrolet Impala 1967",
        "Chevrolet Impala 1964", "Chevrolet Impala lowrider"
    ],
    "chevelle": [
        "Chevrolet Chevelle", "Chevelle SS", "Chevelle Malibu"
    ],
    "belair": [
        "Chevrolet Bel Air", "1957 Chevrolet", "Chevy Bel Air"
    ],
    "colorado": [
        "Chevrolet Colorado", "Chevy Colorado"
    ],
    "tahoe": [
        "Chevrolet Tahoe"
    ],
    "suburban": [
        "Chevrolet Suburban"
    ],
    "malibu": [
        "Chevrolet Malibu car"
    ],
    "blazer": [
        "Chevrolet Blazer", "Chevy Blazer", "K5 Blazer"
    ],
    "s10": [
        "Chevrolet S-10", "Chevy S10"
    ],
    "nova": [
        "Chevrolet Nova", "Chevy Nova", "Chevy II Nova"
    ],
    "monte-carlo": [
        "Chevrolet Monte Carlo"
    ],
    "equinox": [
        "Chevrolet Equinox"
    ],
    "bolt": [
        "Chevrolet Bolt", "Bolt EV", "Bolt EUV"
    ],
    "trucks-classic": [
        "Chevrolet pickup truck vintage", "Chevrolet C10",
        "Chevrolet Apache", "Chevrolet 3100"
    ],
    "trucks-modern": [
        "Chevrolet truck", "Chevy pickup"
    ],
    "classic-misc": [
        "Chevrolet classic car", "vintage Chevrolet",
        "Chevrolet El Camino", "Chevrolet Nomad"
    ],
    "modern-misc": [
        "Chevrolet Trax", "Chevrolet Traverse", "Chevrolet Trailblazer SUV"
    ],
}

ctx = ssl.create_default_context()

def wiki_search(query, limit=20):
    """Search Wikimedia Commons for files matching query."""
    params = urllib.parse.urlencode({
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": "6",
        "srlimit": str(limit),
        "format": "json"
    })
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ChevyRootsBot/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = json.loads(resp.read())
            return [item["title"] for item in data.get("query", {}).get("search", [])]
    except Exception as e:
        print(f"  Search error for '{query}': {e}")
        return []


def get_image_url(title):
    """Get the actual image URL for a Wikimedia Commons file."""
    params = urllib.parse.urlencode({
        "action": "query",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1280",
        "format": "json"
    })
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ChevyRootsBot/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = json.loads(resp.read())
            pages = data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                # Use thumbnail URL (1280px wide) for reasonable file sizes
                thumb_url = ii.get("thumburl", ii.get("url"))
                full_url = ii.get("url", "")
                extmeta = ii.get("extmetadata", {})
                license_short = extmeta.get("LicenseShortName", {}).get("value", "Unknown")
                artist = extmeta.get("Artist", {}).get("value", "Unknown")
                desc = extmeta.get("ImageDescription", {}).get("value", "")
                # Strip HTML from artist/desc
                artist = re.sub(r'<[^>]+>', '', artist).strip()
                desc = re.sub(r'<[^>]+>', '', desc).strip()
                return {
                    "thumb_url": thumb_url,
                    "full_url": full_url,
                    "license": license_short,
                    "artist": artist,
                    "description": desc,
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": ii.get("mime", ""),
                }
    except Exception as e:
        print(f"  Info error for '{title}': {e}")
    return None


def download_image(url, filepath, retries=3):
    """Download an image to a local filepath with retry on 429."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                with open(filepath, "wb") as f:
                    f.write(resp.read())
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                wait = (attempt + 1) * 10
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  Download error: {e}")
                return False
        except Exception as e:
            print(f"  Download error: {e}")
            return False
    return False


def sanitize_filename(title):
    """Convert wiki title to safe filename."""
    name = title.replace("File:", "").strip()
    name = re.sub(r'[^\w\s\-\.]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name[:120]  # cap length


def main():
    catalog = []
    seen_urls = set()
    total = 0

    for category, queries in SEARCHES.items():
        cat_dir = os.path.join(BASE_DIR, category)
        os.makedirs(cat_dir, exist_ok=True)
        print(f"\n{'='*60}")
        print(f"Category: {category}")
        print(f"{'='*60}")

        for query in queries:
            print(f"\n  Searching: {query}")
            titles = wiki_search(query, limit=15)
            print(f"  Found {len(titles)} results")

            for title in titles:
                # Only process image files
                lower = title.lower()
                if not any(lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    continue

                info = get_image_url(title)
                if not info or not info["thumb_url"]:
                    continue

                # Skip duplicates
                if info["full_url"] in seen_urls:
                    continue
                seen_urls.add(info["full_url"])

                # Skip tiny images
                if info["width"] < 400 or info["height"] < 300:
                    continue

                filename = sanitize_filename(title)
                filepath = os.path.join(cat_dir, filename)

                print(f"    Downloading: {filename[:60]}...")
                if download_image(info["thumb_url"], filepath):
                    entry = {
                        "file": f"{category}/{filename}",
                        "category": category,
                        "search_query": query,
                        "title": title.replace("File:", ""),
                        "license": info["license"],
                        "artist": info["artist"],
                        "description": info["description"][:200],
                        "source_url": info["full_url"],
                        "width": info["width"],
                        "height": info["height"],
                    }
                    catalog.append(entry)
                    total += 1

                # Be polite to the API
                time.sleep(2)

            time.sleep(3)

    # Write catalog
    with open(CATALOG_FILE, "w") as f:
        json.dump(catalog, f, indent=2)

    print(f"\n{'='*60}")
    print(f"DONE! Downloaded {total} photos across {len(SEARCHES)} categories")
    print(f"Catalog saved to {CATALOG_FILE}")

    # Print summary by category
    from collections import Counter
    cats = Counter(e["category"] for e in catalog)
    print(f"\nBreakdown:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count} photos")


if __name__ == "__main__":
    main()
