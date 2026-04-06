#!/usr/bin/env python3
"""
Map downloaded images and YouTube videos to vintage ads JSON.
Priority: 1) Real ad scans  2) Dealer ads  3) Existing site photos by model
"""

import json
import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
PHOTOS_DIR = os.path.join(os.path.dirname(__file__), 'photos')

# YouTube video IDs for iconic Chevy commercials
YOUTUBE_VIDEOS = {
    40: "sLnxjiMbpGo",   # See the USA in Your Chevrolet - Dinah Shore
    46: "LkF5ZmGnPBQ",   # 1955 Chevy The Hot One
    51: "NM4w2Yvjvok",   # 1957 Sweet Smooth Sassy
    54: "Iq_e6wR7PXQ",   # 1958 Impala intro
    62: "GFSFvJ01mY4",   # 1963 Corvette Sting Ray
    70: "5Mwi7oBrv0w",   # 1967 Camaro Hugger
    87: "GQMJEiHcrWM",   # Baseball Hot Dogs Apple Pie
    100: "4iYiL1HGfBo",  # Heartbeat of America
    106: "IocCC1-jeTY",  # Like a Rock
    108: "73rSWL5Dxf0",  # 1993 Camaro launch
    113: "2zBcRR2uxuM",  # C5 Corvette
    123: "h8F60sA6xs8",  # American Revolution
    131: "clz3MK-rWH0",  # 2009 Camaro relaunch
    137: "8u3W6sDe3nE",  # Find New Roads
    138: "p_ISHf_qLP0",  # C7 Corvette Stingray
    142: "xTfS0nAgfuE",  # Real People Not Actors
    149: "qGkkAjwVJpM",  # C8 Corvette reveal
    154: "RrC-gCvGesU",  # Silverado EV Sopranos
    155: "JOyuaXcwnco",  # Corvette Z06 sound
    158: "oU3bvwMI61c",  # Equinox EV Super Bowl
    200: "XxFUBbMRLuw",  # Silverado Mayan Apocalypse
}


def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def normalize(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


# Model name -> photo directory mapping
MODEL_DIR_MAP = {
    'bel air': 'belair', 'belair': 'belair',
    'blazer': 'blazer', 'k5 blazer': 'blazer', 's-10 blazer': 'blazer',
    'bolt': 'bolt', 'bolt ev': 'bolt', 'bolt euv': 'bolt',
    'camaro': 'camaro', 'camaro ss': 'camaro', 'camaro z28': 'camaro', 'camaro zl1': 'camaro', 'iroc-z': 'camaro', '1le': 'camaro',
    'chevelle': 'chevelle', 'chevelle ss': 'chevelle', 'chevelle malibu': 'chevelle', 'malibu ss': 'chevelle',
    'colorado': 'colorado', 'colorado zr2': 'colorado',
    'corvette': 'corvette', 'corvette sting ray': 'corvette', 'corvette stingray': 'corvette', 'corvette z06': 'corvette', 'corvette zr1': 'corvette', 'corvette zr-1': 'corvette', 'corvette e-ray': 'corvette', 'corvette c8': 'corvette',
    'equinox': 'equinox', 'equinox ev': 'equinox',
    'impala': 'impala', 'impala ss': 'impala',
    'malibu': 'malibu',
    'monte carlo': 'monte-carlo',
    'nova': 'nova', 'nova ss': 'nova', 'chevy ii': 'nova',
    's-10': 's10', 's10': 's10',
    'silverado': 'silverado', 'silverado ev': 'silverado', 'silverado hd': 'silverado',
    'suburban': 'suburban', 'suburban carryall': 'suburban',
    'tahoe': 'tahoe',
}


def get_model_dir(model_name):
    """Map a model name to the photo directory."""
    mn = model_name.lower().strip()
    # Exact match
    if mn in MODEL_DIR_MAP:
        return MODEL_DIR_MAP[mn]
    # Partial match
    for key, dir_name in MODEL_DIR_MAP.items():
        if key in mn or mn in key:
            return dir_name
    return None


def classify_wiki_image(img):
    """Classify a Wikimedia image as ad_scan, dealer_ad, or car_photo."""
    title = img.get('title', '').lower()
    desc = img.get('description', '').lower()
    combined = title + ' ' + desc

    ad_keywords = ['_ad', 'ad_', 'advertisement', 'advert.', 'brochure', 'promotional', 'poster', 'print ad', 'magazine ad']
    dealer_keywords = ['dankel', 'dealer', 'matchcover', 'town auto', 'don allen']

    if any(kw in combined for kw in ad_keywords):
        return 'ad_scan'
    if any(kw in combined for kw in dealer_keywords):
        return 'dealer_ad'
    return 'car_photo'


def extract_year_from_title(title):
    """Extract a year from a filename/title."""
    match = re.search(r'(19\d{2}|20[012]\d)', title)
    return int(match.group(1)) if match else None


def main():
    ads = load_json(os.path.join(DATA_DIR, 'vintage-ads.json'))

    # Load Wikimedia images
    wiki_images = []
    wiki_path = os.path.join(DATA_DIR, 'vintage-ads-images.json')
    if os.path.exists(wiki_path):
        wiki_images = load_json(wiki_path)

    # Classify wiki images
    ad_scans = []
    dealer_ads = []
    for img in wiki_images:
        if not img.get('local_path'):
            continue
        # Verify file exists
        full_path = os.path.join(os.path.dirname(__file__), img['local_path'])
        if not os.path.exists(full_path):
            continue
        cat = classify_wiki_image(img)
        img['_year'] = extract_year_from_title(img.get('title', ''))
        if cat == 'ad_scan':
            ad_scans.append(img)
        elif cat == 'dealer_ad':
            dealer_ads.append(img)

    print(f'Real ad scans: {len(ad_scans)}')
    print(f'Dealer ads: {len(dealer_ads)}')

    # Scan site photo directories
    site_photos = {}
    for subdir in os.listdir(PHOTOS_DIR):
        subpath = os.path.join(PHOTOS_DIR, subdir)
        if os.path.isdir(subpath) and subdir != 'vintage-ads':
            files = sorted([f for f in os.listdir(subpath)
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
            if files:
                site_photos[subdir] = files
    print(f'Site photo dirs: {len(site_photos)}')

    # Map each ad
    stats = {'ad_scan': 0, 'dealer_ad': 0, 'site_photo': 0, 'none': 0, 'video': 0}

    for ad in ads:
        # Remove any previous mapping
        ad.pop('image', None)
        ad.pop('youtube_id', None)

        # 1) YouTube video
        if ad['id'] in YOUTUBE_VIDEOS:
            ad['youtube_id'] = YOUTUBE_VIDEOS[ad['id']]
            stats['video'] += 1

        # 2) Try to find a real ad scan that matches by year
        best_scan = None
        for scan in ad_scans:
            if scan['_year'] and abs(scan['_year'] - ad['year']) <= 1:
                # Check model match
                title_norm = normalize(scan.get('title', ''))
                model_norm = normalize(ad['model'])
                if any(kw in title_norm for kw in model_norm.split() if len(kw) > 3):
                    best_scan = scan
                    break
            elif scan['_year'] and scan['_year'] == ad['year']:
                best_scan = scan

        if best_scan:
            ad['image'] = best_scan['local_path']
            stats['ad_scan'] += 1
            continue

        # 3) Try dealer ads from similar era
        for da in dealer_ads:
            if da['_year'] and abs(da['_year'] - ad['year']) <= 3:
                ad['image'] = da['local_path']
                stats['dealer_ad'] += 1
                break
        if ad.get('image'):
            continue

        # 4) Site photos by model
        model_dir = get_model_dir(ad['model'])
        if model_dir and model_dir in site_photos:
            photos = site_photos[model_dir]
            # Use year-based index for variety
            idx = (ad['year'] * 7 + ad['id']) % len(photos)
            ad['image'] = f'photos/{model_dir}/{photos[idx]}'
            stats['site_photo'] += 1
            continue

        # 5) Fallback to era-appropriate misc photos
        if ad['year'] < 1975 and 'classic-misc' in site_photos:
            photos = site_photos['classic-misc']
            idx = (ad['year'] * 7 + ad['id']) % len(photos)
            ad['image'] = f'photos/classic-misc/{photos[idx]}'
            stats['site_photo'] += 1
        elif 'trucks-classic' in site_photos and any(kw in ad['model'].lower() for kw in ['truck', 'pickup', 'c10', 'c/k', 'one-ton']):
            photos = site_photos['trucks-classic']
            idx = (ad['year'] * 7 + ad['id']) % len(photos)
            ad['image'] = f'photos/trucks-classic/{photos[idx]}'
            stats['site_photo'] += 1
        elif 'modern-misc' in site_photos:
            photos = site_photos['modern-misc']
            idx = (ad['year'] * 7 + ad['id']) % len(photos)
            ad['image'] = f'photos/modern-misc/{photos[idx]}'
            stats['site_photo'] += 1
        else:
            stats['none'] += 1

    print(f'\n--- Results ---')
    print(f'Real ad scans matched: {stats["ad_scan"]}')
    print(f'Dealer ads matched: {stats["dealer_ad"]}')
    print(f'Site car photos: {stats["site_photo"]}')
    print(f'YouTube videos: {stats["video"]}')
    print(f'No image: {stats["none"]}')
    print(f'Total with image: {stats["ad_scan"] + stats["dealer_ad"] + stats["site_photo"]}')

    save_json(os.path.join(DATA_DIR, 'vintage-ads.json'), ads)
    print('Saved!')


if __name__ == '__main__':
    main()
