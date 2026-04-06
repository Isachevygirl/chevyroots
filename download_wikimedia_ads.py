#!/usr/bin/env python3
"""Download confirmed ad images from wikimedia-ads.json catalog."""
import json, os, re, time, urllib.request

PHOTOS_DIR = os.path.join(os.path.dirname(__file__), 'photos', 'vintage-ads')
HEADERS = {'User-Agent': 'ChevyRootsBot/1.0 (https://chevyroots.com; educational)'}
os.makedirs(PHOTOS_DIR, exist_ok=True)

with open(os.path.join(os.path.dirname(__file__), 'data', 'wikimedia-ads.json')) as f:
    ads = json.load(f)

downloaded = 0
for i, ad in enumerate(ads):
    # Clean filename
    name = re.sub(r'[^\w\s\-.]', '', ad['title'])
    name = re.sub(r'\s+', '_', name).strip('_')[:120]
    if not name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        name += '.jpg'

    filepath = os.path.join(PHOTOS_DIR, name)
    ad['local_path'] = f'photos/vintage-ads/{name}'

    if os.path.exists(filepath):
        print(f'  [{i+1}] Exists: {name[:60]}')
        downloaded += 1
        continue

    url = ad.get('thumb_url') or ad.get('url')
    print(f'  [{i+1}] Downloading: {name[:60]}')
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(filepath, 'wb') as f:
                f.write(resp.read())
        downloaded += 1
    except Exception as e:
        print(f'    Error: {e}')
        ad['local_path'] = None
    time.sleep(3)

# Save updated catalog with local paths
with open(os.path.join(os.path.dirname(__file__), 'data', 'wikimedia-ads.json'), 'w') as f:
    json.dump(ads, f, indent=2)

print(f'\nDone: {downloaded}/{len(ads)} images available')
