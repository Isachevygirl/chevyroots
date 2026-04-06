#!/usr/bin/env python3
"""Enrich photo catalog entries with detailed tags: model, generation, era, body style, color, etc."""

import json
import re

CATALOG_FILE = "/Users/crystalarriaga/chevyroots/photos/catalog_pexels.json"
OUTPUT_FILE = "/Users/crystalarriaga/chevyroots/photos/catalog_pexels_tagged.json"

# --- Tag dictionaries ---

MODELS = {
    "corvette": "Chevrolet Corvette",
    "camaro": "Chevrolet Camaro",
    "silverado": "Chevrolet Silverado",
    "impala": "Chevrolet Impala",
    "chevelle": "Chevrolet Chevelle",
    "bel air": "Chevrolet Bel Air",
    "belair": "Chevrolet Bel Air",
    "colorado": "Chevrolet Colorado",
    "tahoe": "Chevrolet Tahoe",
    "suburban": "Chevrolet Suburban",
    "malibu": "Chevrolet Malibu",
    "blazer": "Chevrolet Blazer",
    "k5 blazer": "Chevrolet K5 Blazer",
    "s-10": "Chevrolet S-10",
    "s10": "Chevrolet S-10",
    "nova": "Chevrolet Nova",
    "monte carlo": "Chevrolet Monte Carlo",
    "equinox": "Chevrolet Equinox",
    "bolt": "Chevrolet Bolt",
    "el camino": "Chevrolet El Camino",
    "c10": "Chevrolet C10",
    "c-10": "Chevrolet C10",
    "apache": "Chevrolet Apache",
    "3100": "Chevrolet 3100",
    "nomad": "Chevrolet Nomad",
    "trailblazer": "Chevrolet Trailblazer",
    "traverse": "Chevrolet Traverse",
    "trax": "Chevrolet Trax",
    "cruze": "Chevrolet Cruze",
    "spark": "Chevrolet Spark",
    "sonic": "Chevrolet Sonic",
    "avalanche": "Chevrolet Avalanche",
    "ssr": "Chevrolet SSR",
    "lumina": "Chevrolet Lumina",
    "caprice": "Chevrolet Caprice",
    "pickup": "Chevrolet Pickup",
}

TRIMS = {
    "ss": "SS",
    "z06": "Z06",
    "zr1": "ZR1",
    "z28": "Z28",
    "zl1": "ZL1",
    "rs": "RS",
    "lt": "LT",
    "ltz": "LTZ",
    "high country": "High Country",
    "trail boss": "Trail Boss",
    "stingray": "Stingray",
    "grand sport": "Grand Sport",
    "1le": "1LE",
    "zr2": "ZR2",
    "rst": "RST",
    "premier": "Premier",
    "midnight edition": "Midnight Edition",
}

CORVETTE_GENS = {
    "c1": "C1 (1953-1962)", "c2": "C2 (1963-1967)", "c3": "C3 (1968-1982)",
    "c4": "C4 (1984-1996)", "c5": "C5 (1997-2004)", "c6": "C6 (2005-2013)",
    "c7": "C7 (2014-2019)", "c8": "C8 (2020-present)",
}

CAMARO_GENS = {
    "1st gen": "1st Gen (1967-1969)", "first gen": "1st Gen (1967-1969)",
    "2nd gen": "2nd Gen (1970-1981)", "second gen": "2nd Gen (1970-1981)",
    "3rd gen": "3rd Gen (1982-1992)", "third gen": "3rd Gen (1982-1992)",
    "4th gen": "4th Gen (1993-2002)", "fourth gen": "4th Gen (1993-2002)",
    "5th gen": "5th Gen (2010-2015)", "fifth gen": "5th Gen (2010-2015)",
    "6th gen": "6th Gen (2016-2024)", "sixth gen": "6th Gen (2016-2024)",
}

COLORS = [
    "red", "blue", "black", "white", "silver", "gray", "grey", "green",
    "yellow", "orange", "gold", "purple", "brown", "beige", "cream",
    "burgundy", "maroon", "teal", "turquoise", "copper", "bronze",
    "champagne", "ivory", "charcoal", "midnight", "metallic", "matte",
    "chrome", "pink", "lime",
]

BODY_STYLES = {
    "convertible": "Convertible",
    "coupe": "Coupe",
    "sedan": "Sedan",
    "wagon": "Wagon",
    "station wagon": "Station Wagon",
    "hatchback": "Hatchback",
    "pickup": "Pickup Truck",
    "truck": "Truck",
    "suv": "SUV",
    "crossover": "Crossover",
    "van": "Van",
    "roadster": "Roadster",
    "fastback": "Fastback",
    "hardtop": "Hardtop",
    "crew cab": "Crew Cab",
    "regular cab": "Regular Cab",
    "extended cab": "Extended Cab",
    "double cab": "Double Cab",
}

SETTINGS = {
    "parked": "Parked",
    "driving": "Driving/Action",
    "racing": "Racing",
    "drag": "Drag Racing",
    "show": "Car Show",
    "car show": "Car Show",
    "car meet": "Car Meet",
    "garage": "Garage",
    "dealership": "Dealership",
    "museum": "Museum",
    "street": "Street",
    "highway": "Highway",
    "off-road": "Off-Road",
    "offroad": "Off-Road",
    "trail": "Trail/Off-Road",
    "desert": "Desert",
    "beach": "Beach",
    "mountain": "Mountain",
    "urban": "Urban",
    "city": "City/Urban",
    "rural": "Rural",
    "sunset": "Sunset",
    "night": "Night",
    "rain": "Rain/Wet",
    "snow": "Snow/Winter",
    "lake": "Lakeside",
    "forest": "Forest",
}

FEATURES = {
    "lowrider": "Lowrider",
    "lifted": "Lifted",
    "modified": "Modified",
    "custom": "Custom",
    "stock": "Stock",
    "restored": "Restored",
    "original": "Original",
    "engine": "Engine/Under Hood",
    "interior": "Interior",
    "cockpit": "Interior",
    "dashboard": "Dashboard",
    "wheel": "Wheels/Rims",
    "rim": "Wheels/Rims",
    "exhaust": "Exhaust",
    "hood": "Hood",
    "headlight": "Headlights",
    "taillight": "Taillights",
    "bumper": "Bumper",
    "grill": "Grille",
    "grille": "Grille",
    "badge": "Badge/Emblem",
    "emblem": "Badge/Emblem",
    "logo": "Badge/Emblem",
    "wrap": "Wrap",
    "chrome": "Chrome",
    "muscle": "Muscle Car",
    "classic": "Classic",
    "vintage": "Vintage",
    "antique": "Antique",
    "retro": "Retro",
    "modern": "Modern",
    "new": "Modern",
    "electric": "Electric/EV",
    "ev": "Electric/EV",
    "hybrid": "Hybrid",
    "diesel": "Diesel",
    "turbo": "Turbocharged",
    "supercharged": "Supercharged",
    "4x4": "4x4/4WD",
    "4wd": "4x4/4WD",
    "awd": "AWD",
    "tow": "Towing",
    "towing": "Towing",
    "police": "Police Vehicle",
    "patrol": "Police Vehicle",
    "race car": "Race Car",
    "nascar": "NASCAR",
    "drag race": "Drag Racing",
}

# Year detection
YEAR_PATTERN = re.compile(r'\b(19[2-9]\d|20[0-2]\d)\b')

def detect_era(text):
    """Detect era from year mentions."""
    years = YEAR_PATTERN.findall(text)
    eras = set()
    for y in years:
        yr = int(y)
        if yr < 1950:
            eras.add("Pre-1950s")
        elif yr < 1960:
            eras.add("1950s")
        elif yr < 1970:
            eras.add("1960s")
        elif yr < 1980:
            eras.add("1970s")
        elif yr < 1990:
            eras.add("1980s")
        elif yr < 2000:
            eras.add("1990s")
        elif yr < 2010:
            eras.add("2000s")
        elif yr < 2020:
            eras.add("2010s")
        else:
            eras.add("2020s")
    return list(eras), [int(y) for y in years]


def detect_orientation(w, h):
    if w > h * 1.2:
        return "Landscape"
    elif h > w * 1.2:
        return "Portrait"
    return "Square"


def detect_angle(text):
    angles = []
    t = text.lower()
    if "front" in t:
        angles.append("Front View")
    if "rear" in t or "back" in t:
        angles.append("Rear View")
    if "side" in t:
        angles.append("Side View")
    if "aerial" in t or "drone" in t or "above" in t or "top" in t:
        angles.append("Aerial/Top View")
    if "close" in t or "detail" in t or "macro" in t:
        angles.append("Close-Up/Detail")
    if "quarter" in t:
        angles.append("Three-Quarter View")
    return angles


def enrich_entry(entry):
    """Add rich tags to a catalog entry."""
    text = " ".join([
        entry.get("title", ""),
        entry.get("description", ""),
        entry.get("search_query", ""),
        entry.get("file", ""),
        entry.get("category", ""),
    ]).lower()

    tags = set(entry.get("tags", []))

    # Model
    models_found = []
    for key, val in MODELS.items():
        if key in text:
            models_found.append(val)
            tags.add(val)

    # Trim/variant
    trims_found = []
    for key, val in TRIMS.items():
        if re.search(r'\b' + re.escape(key) + r'\b', text):
            trims_found.append(val)
            tags.add(f"Trim: {val}")

    # Corvette generation
    for key, val in CORVETTE_GENS.items():
        if key in text:
            tags.add(f"Generation: {val}")

    # Camaro generation
    for key, val in CAMARO_GENS.items():
        if key in text:
            tags.add(f"Generation: {val}")

    # Colors
    colors_found = []
    for c in COLORS:
        if re.search(r'\b' + c + r'\b', text):
            colors_found.append(c.title())
            tags.add(f"Color: {c.title()}")

    # Body style
    body_found = []
    for key, val in BODY_STYLES.items():
        if key in text:
            body_found.append(val)
            tags.add(f"Body: {val}")

    # Setting/scene
    settings_found = []
    for key, val in SETTINGS.items():
        if key in text:
            settings_found.append(val)
            tags.add(f"Setting: {val}")

    # Features
    features_found = []
    for key, val in FEATURES.items():
        if re.search(r'\b' + re.escape(key) + r'\b', text):
            features_found.append(val)
            tags.add(f"Feature: {val}")

    # Era and years
    eras, years = detect_era(text)
    for era in eras:
        tags.add(f"Era: {era}")

    # Orientation
    w = entry.get("width", 0)
    h = entry.get("height", 0)
    orientation = detect_orientation(w, h)
    tags.add(f"Orientation: {orientation}")

    # Angle
    angles = detect_angle(text)
    for a in angles:
        tags.add(f"Angle: {a}")

    # Brand tag
    tags.add("Chevrolet")
    tags.add("Chevy")
    tags.add("GM")
    tags.add("General Motors")

    # Category-based era inference
    cat = entry.get("category", "")
    if cat in ("belair", "nova", "chevelle", "classic-misc", "trucks-classic"):
        tags.add("Feature: Classic")
    if cat in ("bolt",):
        tags.add("Feature: Electric/EV")
    if cat in ("trucks-classic", "trucks-modern", "silverado", "colorado", "s10"):
        tags.add("Vehicle Type: Truck")
    if cat in ("tahoe", "suburban", "blazer", "equinox", "trailblazer"):
        tags.add("Vehicle Type: SUV")
    if cat in ("corvette", "camaro", "chevelle", "nova", "monte-carlo"):
        tags.add("Vehicle Type: Sports/Performance")
    if cat in ("impala", "malibu"):
        tags.add("Vehicle Type: Sedan")
    if cat in ("belair",):
        tags.add("Vehicle Type: Classic Cruiser")

    # Build structured metadata
    entry["tags"] = sorted(list(tags))
    entry["models"] = list(set(models_found))
    entry["trims"] = list(set(trims_found))
    entry["colors"] = list(set(colors_found))
    entry["body_styles"] = list(set(body_found))
    entry["settings"] = list(set(settings_found))
    entry["features"] = list(set(features_found))
    entry["eras"] = eras
    entry["years"] = sorted(list(set(years)))
    entry["orientation"] = orientation
    entry["angles"] = angles
    entry["vehicle_type"] = []
    for t in entry["tags"]:
        if t.startswith("Vehicle Type:"):
            entry["vehicle_type"].append(t.replace("Vehicle Type: ", ""))

    return entry


def main():
    with open(CATALOG_FILE) as f:
        catalog = json.load(f)

    print(f"Enriching {len(catalog)} entries...")

    enriched = [enrich_entry(e) for e in catalog]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(enriched, f, indent=2)

    # Stats
    from collections import Counter
    all_tags = []
    for e in enriched:
        all_tags.extend(e["tags"])

    tag_counts = Counter(all_tags)

    print(f"\nDone! Saved to {OUTPUT_FILE}")
    print(f"Total entries: {len(enriched)}")
    print(f"Unique tags: {len(tag_counts)}")

    print("\n--- Top 50 Tags ---")
    for tag, count in tag_counts.most_common(50):
        print(f"  {tag}: {count}")

    # Check tagging quality
    no_model = sum(1 for e in enriched if not e["models"])
    no_color = sum(1 for e in enriched if not e["colors"])
    no_body = sum(1 for e in enriched if not e["body_styles"])
    no_features = sum(1 for e in enriched if not e["features"])

    print(f"\n--- Coverage ---")
    print(f"  With model identified: {len(enriched) - no_model}/{len(enriched)}")
    print(f"  With color identified: {len(enriched) - no_color}/{len(enriched)}")
    print(f"  With body style: {len(enriched) - no_body}/{len(enriched)}")
    print(f"  With features: {len(enriched) - no_features}/{len(enriched)}")

    # Sample enriched entry
    print("\n--- Sample Entry ---")
    sample = next((e for e in enriched if len(e["tags"]) > 10), enriched[0])
    print(json.dumps(sample, indent=2))


if __name__ == "__main__":
    main()
