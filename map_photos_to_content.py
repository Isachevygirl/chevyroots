#!/usr/bin/env python3
"""Map photos from master catalog to site content pages based on tag matching."""

import json
import os
import re

MASTER_CATALOG = "/Users/crystalarriaga/chevyroots/photos/catalog_master.json"
OUTPUT = "/Users/crystalarriaga/chevyroots/photos/photo_assignments.json"
REPORT = "/Users/crystalarriaga/chevyroots/photos/photo_assignments_report.md"

# Define what each page needs
PAGE_PHOTO_NEEDS = {
    # === MAIN PAGES ===
    "index.html": {
        "description": "Homepage — hero image + section thumbnails",
        "needs": [
            {"role": "hero", "count": 3, "filters": {"orientation": "Landscape", "min_width": 2000}, "prefer_tags": ["Feature: Classic", "Feature: Muscle Car"], "description": "Wide hero banner shots"},
            {"role": "section-trucks", "count": 2, "filters": {}, "prefer_tags": ["Vehicle Type: Truck", "Chevrolet Silverado"], "description": "Truck section thumbnail"},
            {"role": "section-sports", "count": 2, "filters": {}, "prefer_tags": ["Vehicle Type: Sports/Performance", "Chevrolet Corvette"], "description": "Sports car section"},
            {"role": "section-classics", "count": 2, "filters": {}, "prefer_tags": ["Feature: Classic", "Feature: Vintage"], "description": "Classic car section"},
            {"role": "section-suv", "count": 2, "filters": {}, "prefer_tags": ["Vehicle Type: SUV"], "description": "SUV section"},
        ]
    },
    "pages/about/index.html": {
        "description": "About page — community and passion imagery",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Setting: Car Show", "Setting: Car Meet"], "description": "Community/car show atmosphere"},
            {"role": "lifestyle", "count": 3, "filters": {}, "prefer_tags": ["Setting: Rural", "Setting: Street", "Feature: Classic"], "description": "Lifestyle Chevy shots"},
        ]
    },

    # === GUIDE PAGES ===
    "pages/guides/chevy-history.html": {
        "description": "115-year Chevy history timeline",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Vintage", "Feature: Classic"], "description": "Iconic vintage Chevy hero"},
            {"role": "1950s", "count": 3, "filters": {}, "prefer_tags": ["Chevrolet Bel Air", "Era: 1950s", "Feature: Classic"], "description": "1950s era — Bel Air"},
            {"role": "1960s", "count": 3, "filters": {}, "prefer_tags": ["Chevrolet Impala", "Chevrolet Chevelle", "Era: 1960s"], "description": "1960s era — Impala, Chevelle"},
            {"role": "1960s-sports", "count": 2, "filters": {}, "prefer_tags": ["Chevrolet Corvette", "Chevrolet Camaro", "Feature: Classic"], "description": "1960s sports — Corvette, Camaro"},
            {"role": "1970s", "count": 2, "filters": {}, "prefer_tags": ["Era: 1970s", "Chevrolet Chevelle", "Chevrolet Nova"], "description": "1970s muscle"},
            {"role": "trucks-classic", "count": 2, "filters": {}, "prefer_tags": ["Vehicle Type: Truck", "Feature: Classic", "Chevrolet C10"], "description": "Classic trucks"},
            {"role": "modern", "count": 2, "filters": {}, "prefer_tags": ["Feature: Modern", "Feature: Electric/EV"], "description": "Modern era"},
        ]
    },
    "pages/guides/silverado-buyers-guide.html": {
        "description": "2024-2025 Silverado 1500 full buyer's guide",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Chevrolet Silverado", "Feature: Modern"], "description": "Modern Silverado hero"},
            {"role": "exterior", "count": 4, "filters": {}, "prefer_tags": ["Chevrolet Silverado", "Angle: Front View", "Angle: Side View", "Angle: Three-Quarter View"], "description": "Silverado exterior angles"},
            {"role": "detail", "count": 2, "filters": {}, "prefer_tags": ["Chevrolet Silverado", "Angle: Close-Up/Detail"], "description": "Silverado detail shots"},
            {"role": "action", "count": 2, "filters": {}, "prefer_tags": ["Chevrolet Silverado", "Setting: Highway", "Setting: Rural"], "description": "Silverado in action"},
        ]
    },
    "pages/guides/ls-swap-guide.html": {
        "description": "LS engine swap comprehensive guide",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Engine/Under Hood", "Feature: Custom"], "description": "Engine bay / LS swap hero"},
            {"role": "engines", "count": 3, "filters": {}, "prefer_tags": ["Feature: Engine/Under Hood", "Angle: Close-Up/Detail"], "description": "Engine detail shots"},
            {"role": "swap-cars", "count": 3, "filters": {}, "prefer_tags": ["Feature: Custom", "Feature: Modified", "Chevrolet C10", "Chevrolet Nova"], "description": "Popular LS swap recipient vehicles"},
        ]
    },
    "pages/guides/c8-corvette-buyers-guide.html": {
        "description": "C8 Corvette Stingray vs Z06 vs E-Ray buyer's guide",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Chevrolet Corvette", "Feature: Modern"], "description": "C8 Corvette hero shot"},
            {"role": "exterior", "count": 4, "filters": {}, "prefer_tags": ["Chevrolet Corvette", "Feature: Modern"], "description": "C8 from different angles"},
            {"role": "detail", "count": 2, "filters": {}, "prefer_tags": ["Chevrolet Corvette", "Angle: Close-Up/Detail"], "description": "C8 detail shots"},
        ]
    },
    "pages/guides/c8-corvette-best-year-to-buy.html": {
        "description": "Best year C8 Corvette to buy used",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Chevrolet Corvette"], "description": "C8 hero"},
            {"role": "gallery", "count": 4, "filters": {}, "prefer_tags": ["Chevrolet Corvette", "Feature: Modern"], "description": "Various C8 shots showing different colors/years"},
        ]
    },
    "pages/guides/small-block-chevy-history.html": {
        "description": "Small block Chevy engine history 1955-present",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Engine/Under Hood", "Feature: Classic"], "description": "Classic small block engine"},
            {"role": "classic-cars", "count": 3, "filters": {}, "prefer_tags": ["Feature: Classic", "Feature: Muscle Car", "Chevrolet Chevelle", "Chevrolet Camaro"], "description": "Cars powered by small blocks"},
            {"role": "engine-detail", "count": 2, "filters": {}, "prefer_tags": ["Feature: Engine/Under Hood", "Angle: Close-Up/Detail"], "description": "Engine close-ups"},
        ]
    },
    "pages/guides/chevy-impala-cultural-history.html": {
        "description": "Impala cultural history — lowriders, hip-hop, TV",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Chevrolet Impala", "Feature: Classic"], "description": "Iconic Impala hero"},
            {"role": "classic", "count": 4, "filters": {}, "prefer_tags": ["Chevrolet Impala", "Feature: Classic", "Feature: Vintage"], "description": "Classic Impalas"},
            {"role": "lowrider", "count": 2, "filters": {}, "prefer_tags": ["Chevrolet Impala", "Feature: Lowrider", "Feature: Custom"], "description": "Lowrider Impalas"},
            {"role": "detail", "count": 2, "filters": {}, "prefer_tags": ["Chevrolet Impala", "Angle: Close-Up/Detail", "Feature: Chrome"], "description": "Impala chrome/badge details"},
        ]
    },
    "pages/guides/america-250-chevy-road-trip.html": {
        "description": "2026 America 250 road trip itinerary with Chevy",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Setting: Highway", "Setting: Rural"], "description": "Road trip hero"},
            {"role": "scenic", "count": 4, "filters": {}, "prefer_tags": ["Setting: Desert", "Setting: Mountain", "Setting: Rural", "Setting: Highway"], "description": "Scenic driving shots"},
            {"role": "classic-cruiser", "count": 2, "filters": {}, "prefer_tags": ["Feature: Classic", "Vehicle Type: Classic Cruiser"], "description": "Classic road trip Chevy"},
        ]
    },
    "pages/guides/chevy-towing-guide.html": {
        "description": "Towing capacities for all Chevy models",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Chevrolet Silverado", "Feature: Towing"], "description": "Silverado towing hero"},
            {"role": "trucks", "count": 3, "filters": {}, "prefer_tags": ["Vehicle Type: Truck", "Chevrolet Silverado", "Chevrolet Colorado"], "description": "Truck lineup shots"},
            {"role": "suvs", "count": 2, "filters": {}, "prefer_tags": ["Vehicle Type: SUV", "Chevrolet Tahoe", "Chevrolet Suburban"], "description": "SUVs for towing"},
        ]
    },
    "pages/guides/silverado-5.3-vs-6.2.html": {
        "description": "Silverado 5.3L vs 6.2L engine comparison",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Chevrolet Silverado"], "description": "Silverado hero"},
            {"role": "engine", "count": 2, "filters": {}, "prefer_tags": ["Feature: Engine/Under Hood", "Chevrolet Silverado"], "description": "Engine bay shots"},
            {"role": "truck-action", "count": 2, "filters": {}, "prefer_tags": ["Chevrolet Silverado", "Setting: Highway", "Setting: Rural"], "description": "Silverado driving"},
        ]
    },
    "pages/guides/chevy-mlb-partnership.html": {
        "description": "Chevy and MLB 20+ year partnership",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Chevrolet Silverado", "Feature: Modern"], "description": "Modern Silverado (MLB partner vehicle)"},
            {"role": "trucks", "count": 2, "filters": {}, "prefer_tags": ["Chevrolet Silverado", "Feature: Modern"], "description": "Silverado showcase"},
        ]
    },
    "pages/guides/chevy-dream-tour.html": {
        "description": "12 historic Chevrolet sites dream tour",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Classic", "Setting: Rural"], "description": "Classic Chevy road trip"},
            {"role": "corvette", "count": 2, "filters": {}, "prefer_tags": ["Chevrolet Corvette"], "description": "Corvette (for museum stop)"},
            {"role": "classics", "count": 3, "filters": {}, "prefer_tags": ["Feature: Classic", "Feature: Vintage", "Vehicle Type: Classic Cruiser"], "description": "Various classic Chevys"},
            {"role": "trucks", "count": 2, "filters": {}, "prefer_tags": ["Vehicle Type: Truck", "Feature: Classic"], "description": "Classic trucks"},
        ]
    },
    "pages/guides/known-issues.html": {
        "description": "Searchable known issues database",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Chevrolet Silverado", "Feature: Modern"], "description": "Modern Chevy hero"},
            {"role": "models", "count": 3, "filters": {}, "prefer_tags": ["Chevrolet Silverado", "Chevrolet Colorado", "Chevrolet Tahoe"], "description": "Models with known issues"},
        ]
    },
    "pages/guides/compare.html": {
        "description": "Interactive model comparison tool",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Modern"], "description": "Modern lineup hero"},
        ]
    },
    "pages/guides/quiz.html": {
        "description": "Which Chevy is right for you quiz",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": [], "description": "Fun Chevy lineup shot"},
            {"role": "results", "count": 4, "filters": {}, "prefer_tags": ["Chevrolet Silverado", "Chevrolet Corvette", "Vehicle Type: SUV", "Feature: Electric/EV"], "description": "One per quiz result type"},
        ]
    },
    "pages/guides/best-mods-silverado.html": {
        "description": "Best Silverado modifications",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Chevrolet Silverado", "Feature: Modified", "Feature: Custom"], "description": "Modified Silverado"},
            {"role": "mods", "count": 3, "filters": {}, "prefer_tags": ["Chevrolet Silverado", "Feature: Modified", "Feature: Lifted"], "description": "Modified truck shots"},
        ]
    },
    "pages/guides/best-cold-air-intake-silverado.html": {
        "description": "Top 5 cold air intakes for Silverado",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Engine/Under Hood", "Chevrolet Silverado"], "description": "Engine bay / intake shot"},
            {"role": "engine", "count": 2, "filters": {}, "prefer_tags": ["Feature: Engine/Under Hood", "Angle: Close-Up/Detail"], "description": "Under-hood detail"},
        ]
    },
    "pages/guides/best-exhaust-silverado.html": {
        "description": "Top 5 cat-back exhausts for Silverado",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Chevrolet Silverado"], "description": "Silverado rear/exhaust view"},
            {"role": "exhaust", "count": 2, "filters": {}, "prefer_tags": ["Feature: Exhaust", "Angle: Rear View", "Chevrolet Silverado"], "description": "Exhaust/rear angle shots"},
        ]
    },
    "pages/guides/best-tonneau-covers-silverado.html": {
        "description": "Top 5 tonneau covers for Silverado",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Chevrolet Silverado", "Body: Pickup Truck"], "description": "Silverado truck bed view"},
            {"role": "bed", "count": 2, "filters": {}, "prefer_tags": ["Chevrolet Silverado", "Angle: Rear View"], "description": "Truck bed angle shots"},
        ]
    },
    "pages/guides/silverado-transmission-shudder-fix.html": {
        "description": "10-speed transmission shudder fix guide",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Chevrolet Silverado"], "description": "Silverado hero"},
            {"role": "detail", "count": 1, "filters": {}, "prefer_tags": ["Chevrolet Silverado", "Angle: Close-Up/Detail"], "description": "Mechanical detail"},
        ]
    },
    "pages/guides/chevy-maintenance-schedule.html": {
        "description": "Complete Chevy maintenance schedule",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Modern"], "description": "Modern Chevy hero"},
            {"role": "detail", "count": 2, "filters": {}, "prefer_tags": ["Angle: Close-Up/Detail", "Feature: Engine/Under Hood"], "description": "Maintenance-related detail shots"},
        ]
    },

    # === SECTION LANDING PAGES ===
    "pages/models/index.html": {
        "description": "Current Chevy model lineup showcase",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Modern"], "description": "Modern lineup hero"},
            {"role": "silverado", "count": 2, "filters": {}, "prefer_tags": ["Chevrolet Silverado", "Feature: Modern"], "description": "Silverado"},
            {"role": "corvette", "count": 2, "filters": {}, "prefer_tags": ["Chevrolet Corvette", "Feature: Modern"], "description": "Corvette"},
            {"role": "tahoe", "count": 1, "filters": {}, "prefer_tags": ["Chevrolet Tahoe"], "description": "Tahoe"},
            {"role": "equinox", "count": 1, "filters": {}, "prefer_tags": ["Chevrolet Equinox"], "description": "Equinox"},
            {"role": "colorado", "count": 1, "filters": {}, "prefer_tags": ["Chevrolet Colorado"], "description": "Colorado"},
            {"role": "blazer", "count": 1, "filters": {}, "prefer_tags": ["Chevrolet Blazer", "Feature: Modern"], "description": "Blazer"},
            {"role": "bolt", "count": 1, "filters": {}, "prefer_tags": ["Chevrolet Bolt", "Feature: Electric/EV"], "description": "Bolt EV"},
            {"role": "malibu", "count": 1, "filters": {}, "prefer_tags": ["Chevrolet Malibu"], "description": "Malibu"},
            {"role": "suburban", "count": 1, "filters": {}, "prefer_tags": ["Chevrolet Suburban"], "description": "Suburban"},
            {"role": "camaro", "count": 1, "filters": {}, "prefer_tags": ["Chevrolet Camaro", "Feature: Modern"], "description": "Camaro"},
        ]
    },
    "pages/news/index.html": {
        "description": "News hub — SEMA, auctions, events",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Setting: Car Show"], "description": "Car show/event hero"},
            {"role": "events", "count": 3, "filters": {}, "prefer_tags": ["Setting: Car Show", "Setting: Car Meet", "Feature: Custom"], "description": "Event atmosphere shots"},
        ]
    },
    "pages/community/index.html": {
        "description": "Community hub — meetups, builds, forums",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Setting: Car Show", "Setting: Car Meet"], "description": "Community gathering hero"},
            {"role": "builds", "count": 3, "filters": {}, "prefer_tags": ["Feature: Custom", "Feature: Modified", "Feature: Restored"], "description": "Custom builds"},
        ]
    },
    "pages/events/index.html": {
        "description": "Events calendar — shows, meets, races",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Setting: Car Show"], "description": "Car show hero"},
            {"role": "events", "count": 3, "filters": {}, "prefer_tags": ["Setting: Car Show", "Setting: Car Meet", "Feature: Race Car"], "description": "Event photos"},
        ]
    },
    "pages/marketplace/index.html": {
        "description": "Buy/sell vehicles and parts",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Classic", "Feature: Restored"], "description": "Clean classic Chevy hero"},
            {"role": "variety", "count": 3, "filters": {}, "prefer_tags": ["Feature: Classic", "Vehicle Type: Truck", "Vehicle Type: Sports/Performance"], "description": "Variety of buyable Chevys"},
        ]
    },
    "pages/mechanics/index.html": {
        "description": "Mechanic finder directory",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Engine/Under Hood"], "description": "Under-hood / shop hero"},
            {"role": "shop", "count": 2, "filters": {}, "prefer_tags": ["Setting: Garage", "Feature: Engine/Under Hood"], "description": "Workshop atmosphere"},
        ]
    },
    "pages/builds/index.html": {
        "description": "Build journals and project showcases",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Custom", "Feature: Modified"], "description": "Custom build hero"},
            {"role": "builds", "count": 4, "filters": {}, "prefer_tags": ["Feature: Custom", "Feature: Modified", "Feature: Restored", "Setting: Garage"], "description": "Various builds and project cars"},
        ]
    },
    "pages/ads/index.html": {
        "description": "Vintage ads archive",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Vintage", "Feature: Classic", "Feature: Retro"], "description": "Vintage/retro Chevy hero"},
            {"role": "vintage", "count": 3, "filters": {}, "prefer_tags": ["Feature: Vintage", "Feature: Classic", "Chevrolet Bel Air"], "description": "Vintage era vehicles"},
        ]
    },
    "pages/tools/index.html": {
        "description": "Tools hub — VIN decoder, comparisons, fitment",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Modern"], "description": "Clean modern Chevy"},
        ]
    },
    "pages/newsletter/index.html": {
        "description": "Weekly Wrench newsletter signup",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Classic", "Feature: Muscle Car"], "description": "Eye-catching Chevy hero"},
        ]
    },
    "pages/crystals-corner/index.html": {
        "description": "Crystal's personal column — reviews, adventures",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Setting: Street", "Setting: Rural"], "description": "Lifestyle Chevy shot"},
            {"role": "lifestyle", "count": 2, "filters": {}, "prefer_tags": ["Setting: Sunset", "Setting: Rural", "Setting: City/Urban"], "description": "Atmospheric lifestyle shots"},
        ]
    },
    "pages/partners/index.html": {
        "description": "Advertising and sponsorship page",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": ["Feature: Modern", "Setting: Car Show"], "description": "Professional Chevy shot"},
        ]
    },
    "pages/guides/index.html": {
        "description": "Guides landing page — all guide thumbnails",
        "needs": [
            {"role": "hero", "count": 1, "filters": {"orientation": "Landscape"}, "prefer_tags": [], "description": "General Chevy hero"},
            {"role": "thumbnails", "count": 6, "filters": {}, "prefer_tags": ["Chevrolet Silverado", "Chevrolet Corvette", "Chevrolet Impala", "Feature: Classic", "Vehicle Type: Truck", "Feature: Engine/Under Hood"], "description": "Guide category thumbnails"},
        ]
    },
}


def score_photo(photo, prefer_tags):
    """Score a photo based on how many preferred tags it matches."""
    photo_tags = set(photo.get("tags", []))
    score = 0
    for tag in prefer_tags:
        # Direct match
        if tag in photo_tags:
            score += 10
        # Partial match (tag appears as substring)
        for pt in photo_tags:
            if tag.lower() in pt.lower() and tag not in photo_tags:
                score += 3
    # Bonus for richer descriptions
    if photo.get("description"):
        score += 1
    # Bonus for higher resolution
    if photo.get("width", 0) > 3000:
        score += 2
    return score


def filter_photo(photo, filters):
    """Check if photo passes hard filters."""
    if "orientation" in filters:
        if photo.get("orientation") != filters["orientation"]:
            return False
    if "min_width" in filters:
        if photo.get("width", 0) < filters["min_width"]:
            return False
    return True


def assign_photos(catalog, page_needs):
    """Assign best-matching photos to each page's needs."""
    assignments = {}
    used_files = set()

    for page, config in page_needs.items():
        assignments[page] = {
            "description": config["description"],
            "photos": []
        }

        for need in config["needs"]:
            # Filter candidates
            candidates = [p for p in catalog if filter_photo(p, need.get("filters", {}))]

            # Score and sort
            scored = [(score_photo(p, need["prefer_tags"]), p) for p in candidates]
            scored.sort(key=lambda x: -x[0])

            # Pick top N that haven't been used yet (prefer unique photos across page)
            picked = []
            for score, photo in scored:
                if photo["file"] not in used_files and len(picked) < need["count"]:
                    picked.append({
                        "file": photo["file"],
                        "role": need["role"],
                        "role_description": need["description"],
                        "match_score": score,
                        "title": photo.get("title", ""),
                        "artist": photo.get("artist", ""),
                        "license": photo.get("license", ""),
                        "source_url": photo.get("source_url", ""),
                        "tags": photo.get("tags", [])[:15],
                        "models": photo.get("models", []),
                        "colors": photo.get("colors", []),
                        "orientation": photo.get("orientation", ""),
                        "width": photo.get("width", 0),
                        "height": photo.get("height", 0),
                    })
                    used_files.add(photo["file"])

            assignments[page]["photos"].extend(picked)

    return assignments


def generate_report(assignments):
    """Generate a human-readable markdown report."""
    lines = ["# ChevyRoots Photo Assignments Report\n"]
    lines.append(f"Generated from master catalog of {total_photos} photos\n")

    total_assigned = 0
    for page, data in assignments.items():
        count = len(data["photos"])
        total_assigned += count
        lines.append(f"\n---\n\n## 📄 `{page}`")
        lines.append(f"**{data['description']}** — {count} photos assigned\n")

        if not data["photos"]:
            lines.append("*No matching photos found*\n")
            continue

        for photo in data["photos"]:
            lines.append(f"### [{photo['role']}] {photo['role_description']}")
            lines.append(f"- **File**: `{photo['file']}`")
            lines.append(f"- **Title**: {photo['title'][:80]}")
            lines.append(f"- **Artist**: {photo['artist']}")
            lines.append(f"- **Score**: {photo['match_score']}")
            lines.append(f"- **Size**: {photo['width']}x{photo['height']} ({photo['orientation']})")
            lines.append(f"- **Models**: {', '.join(photo['models']) if photo['models'] else 'General'}")
            lines.append(f"- **Colors**: {', '.join(photo['colors']) if photo['colors'] else 'N/A'}")
            lines.append(f"- **License**: {photo['license'][:60]}")
            top_tags = [t for t in photo['tags'] if not t.startswith(('Chevrolet', 'Chevy', 'GM', 'General'))][:8]
            lines.append(f"- **Key Tags**: {', '.join(top_tags)}")
            lines.append("")

    lines.append(f"\n---\n\n## Summary")
    lines.append(f"- **Total pages**: {len(assignments)}")
    lines.append(f"- **Total photos assigned**: {total_assigned}")
    lines.append(f"- **Unique photos used**: {total_assigned} (no duplicates)")

    return "\n".join(lines)


if __name__ == "__main__":
    with open(MASTER_CATALOG) as f:
        catalog = json.load(f)

    total_photos = len(catalog)
    print(f"Loaded {total_photos} photos from master catalog")
    print(f"Mapping to {len(PAGE_PHOTO_NEEDS)} pages...")

    assignments = assign_photos(catalog, PAGE_PHOTO_NEEDS)

    with open(OUTPUT, "w") as f:
        json.dump(assignments, f, indent=2)

    report = generate_report(assignments)
    with open(REPORT, "w") as f:
        f.write(report)

    total_assigned = sum(len(d["photos"]) for d in assignments.values())
    print(f"\nDone! Assigned {total_assigned} photos across {len(assignments)} pages")
    print(f"JSON: {OUTPUT}")
    print(f"Report: {REPORT}")

    # Quick summary
    print("\nPer-page summary:")
    for page, data in assignments.items():
        print(f"  {page}: {len(data['photos'])} photos")
