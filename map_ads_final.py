#!/usr/bin/env python3
"""Final mapping: real ad scans + YouTube videos -> vintage-ads.json"""
import json, os, re

BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, 'data')

def load(p):
    with open(os.path.join(DATA, p)) as f: return json.load(f)
def save(p, d):
    with open(os.path.join(DATA, p), 'w') as f: json.dump(d, f, indent=2)

VIDEOS = {
    40: "sLnxjiMbpGo", 46: "LkF5ZmGnPBQ", 51: "NM4w2Yvjvok",
    62: "GFSFvJ01mY4", 70: "5Mwi7oBrv0w", 87: "GQMJEiHcrWM",
    100: "4iYiL1HGfBo", 106: "IocCC1-jeTY", 113: "2zBcRR2uxuM",
    123: "h8F60sA6xs8", 131: "clz3MK-rWH0", 137: "8u3W6sDe3nE",
    138: "p_ISHf_qLP0", 142: "xTfS0nAgfuE", 149: "qGkkAjwVJpM",
    154: "RrC-gCvGesU", 155: "JOyuaXcwnco", 158: "oU3bvwMI61c",
    200: "XxFUBbMRLuw",
}

MODEL_DIRS = {
    'bel air': 'belair', 'blazer': 'blazer', 'bolt': 'bolt', 'camaro': 'camaro',
    'chevelle': 'chevelle', 'colorado': 'colorado', 'corvette': 'corvette',
    'equinox': 'equinox', 'impala': 'impala', 'malibu': 'malibu',
    'monte carlo': 'monte-carlo', 'nova': 'nova', 'chevy ii': 'nova',
    's-10': 's10', 'silverado': 'silverado', 'suburban': 'suburban', 'tahoe': 'tahoe',
}

def get_model_dir(model):
    ml = model.lower()
    for k, d in MODEL_DIRS.items():
        if k in ml: return d
    return None

def main():
    ads = load('vintage-ads.json')
    real_mapping = load('real-ads-mapping.json')

    # Scan real ads dir
    real_dir = os.path.join(BASE, 'photos', 'vintage-ads-real')
    real_files = {}
    if os.path.exists(real_dir):
        for f in sorted(os.listdir(real_dir)):
            m = re.match(r'(\d{4})_Chevrolet_Ad-(\d+)\.jpg', f)
            if m:
                yr = int(m.group(1))
                if yr not in real_files:
                    real_files[yr] = []
                real_files[yr].append(f)

    # Scan site photos
    photos_dir = os.path.join(BASE, 'photos')
    site_photos = {}
    for sub in os.listdir(photos_dir):
        sp = os.path.join(photos_dir, sub)
        if os.path.isdir(sp) and sub not in ('vintage-ads', 'vintage-ads-real'):
            files = sorted([f for f in os.listdir(sp) if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))])
            if files: site_photos[sub] = files

    stats = {'real_ad': 0, 'nearby_ad': 0, 'site_photo': 0, 'fallback': 0, 'video': 0}
    used_real = {}  # Track which real ads are used per year to avoid duplication

    for ad in ads:
        ad.pop('image', None)
        ad.pop('youtube_id', None)

        if ad['id'] in VIDEOS:
            ad['youtube_id'] = VIDEOS[ad['id']]
            stats['video'] += 1

        yr = ad['year']

        # 1) Exact year real ad scan
        if yr in real_files:
            files = real_files[yr]
            # Pick next unused one for this year
            used = used_real.get(yr, 0)
            idx = used % len(files)
            ad['image'] = f'photos/vintage-ads-real/{files[idx]}'
            used_real[yr] = used + 1
            stats['real_ad'] += 1
            continue

        # 2) Nearby year real ad (within 2 years)
        found = False
        for offset in [1, -1, 2, -2]:
            ny = yr + offset
            if ny in real_files:
                files = real_files[ny]
                used = used_real.get(ny, 0)
                idx = used % len(files)
                ad['image'] = f'photos/vintage-ads-real/{files[idx]}'
                used_real[ny] = used + 1
                stats['nearby_ad'] += 1
                found = True
                break
        if found: continue

        # 3) Site model-specific photos (for 1988+ era where we don't have real scans)
        mdir = get_model_dir(ad['model'])
        if mdir and mdir in site_photos:
            photos = site_photos[mdir]
            idx = (yr * 7 + ad['id']) % len(photos)
            ad['image'] = f'photos/{mdir}/{photos[idx]}'
            stats['site_photo'] += 1
            continue

        # 4) Era fallback
        truck_kw = ['truck','pickup','c10','c/k','one-ton','task force','advance design']
        if any(kw in ad['model'].lower() for kw in truck_kw):
            d = 'trucks-classic' if yr < 1980 else 'trucks-modern'
        elif yr < 1975:
            d = 'classic-misc'
        else:
            d = 'modern-misc'
        if d in site_photos:
            photos = site_photos[d]
            ad['image'] = f'photos/{d}/{photos[(yr*7+ad["id"]) % len(photos)]}'
            stats['fallback'] += 1

    total_img = stats['real_ad'] + stats['nearby_ad'] + stats['site_photo'] + stats['fallback']
    print(f'Real ad scans (exact year):  {stats["real_ad"]}')
    print(f'Real ad scans (nearby year): {stats["nearby_ad"]}')
    print(f'Site model photos:           {stats["site_photo"]}')
    print(f'Era fallback:                {stats["fallback"]}')
    print(f'YouTube videos:              {stats["video"]}')
    print(f'Total with image:            {total_img}/258')

    save('vintage-ads.json', ads)
    print('Saved!')

if __name__ == '__main__':
    main()
