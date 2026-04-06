#!/usr/bin/env python3
"""Retry failed Wikimedia downloads with longer delays."""

import json
import os
import re
import time
import urllib.request

PHOTOS_DIR = os.path.join(os.path.dirname(__file__), 'photos', 'vintage-ads')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
HEADERS = {
    'User-Agent': 'ChevyRootsBot/1.0 (https://chevyroots.com; educational project)'
}

def download_image(url, filepath):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(filepath, 'wb') as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f'  Error: {e}')
        return False

def safe_filename(title):
    name = title.replace('File:', '').strip()
    name = re.sub(r'[^\w\s\-.]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name[:120]

def main():
    with open(os.path.join(DATA_DIR, 'vintage-ads-images.json')) as f:
        existing = json.load(f)

    existing_paths = {item.get('local_path', '') for item in existing}

    # Re-read the full catalog to find what we already have metadata for
    # but need to re-download with proper delays
    catalog_path = os.path.join(DATA_DIR, 'vintage-ads-images.json')

    # Count what we have on disk
    downloaded_files = set(os.listdir(PHOTOS_DIR)) if os.path.exists(PHOTOS_DIR) else set()
    print(f'Already have {len(downloaded_files)} files on disk')

    # Get all file metadata from the previous run's API results
    # We need to re-fetch the ones that 429'd
    # Let's use the stored metadata and just retry downloads

    import urllib.parse
    COMMONS_API = 'https://commons.wikimedia.org/w/api.php'

    # Key ad-specific searches
    queries = [
        'Chevrolet advertisement',
        'Chevrolet ad vintage print',
        'Chevrolet brochure',
        'Corvette advertisement print',
        'Camaro advertisement',
        'Chevrolet magazine ad',
        '"Chevrolet" ad 1950',
        '"Chevrolet" ad 1960',
        '"Chevrolet" ad 1920',
        '"Chevrolet" ad 1930',
        'Chevelle ad',
        'Impala ad Chevrolet',
        'Nova Chevrolet ad',
        'Chevy truck ad',
        'Chevrolet poster',
    ]

    all_titles = set()

    for q in queries:
        params = {
            'action': 'query',
            'list': 'search',
            'srnamespace': '6',
            'srsearch': q,
            'srlimit': '50',
            'format': 'json',
        }
        url = COMMONS_API + '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            if 'query' in data:
                for item in data['query']['search']:
                    t = item['title']
                    tl = t.lower()
                    if any(kw in tl for kw in ['chevrolet', 'chevy', 'corvette', 'camaro', 'impala', 'chevelle', 'nova']):
                        all_titles.add(t)
            print(f'Search "{q}": found items, total unique: {len(all_titles)}')
        except Exception as e:
            print(f'Search error for "{q}": {e}')
        time.sleep(2)  # Much longer delay

    # Also get category files
    categories = [
        'Category:Chevrolet_advertisements',
        'Category:Chevrolet_brochures',
    ]
    for cat in categories:
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': cat,
            'cmtype': 'file',
            'cmlimit': '100',
            'format': 'json',
        }
        url = COMMONS_API + '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            if 'query' in data:
                for item in data['query']['categorymembers']:
                    all_titles.add(item['title'])
            print(f'Category "{cat}": total unique: {len(all_titles)}')
        except Exception as e:
            print(f'Category error: {e}')
        time.sleep(2)

    print(f'\nTotal titles to process: {len(all_titles)}')

    # Get file info in small batches
    all_infos = []
    titles_list = list(all_titles)
    for i in range(0, len(titles_list), 10):
        batch = titles_list[i:i+10]
        params = {
            'action': 'query',
            'titles': '|'.join(batch),
            'prop': 'imageinfo',
            'iiprop': 'url|size|mime|extmetadata',
            'iiurlwidth': '800',
            'format': 'json',
        }
        url = COMMONS_API + '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            if 'query' in data and 'pages' in data['query']:
                for pid, page in data['query']['pages'].items():
                    if 'imageinfo' not in page:
                        continue
                    info = page['imageinfo'][0]
                    mime = info.get('mime', '')
                    if not mime.startswith('image/'):
                        continue
                    ext_meta = info.get('extmetadata', {})
                    desc = ext_meta.get('ImageDescription', {}).get('value', '')
                    all_infos.append({
                        'title': page['title'],
                        'url': info.get('url', ''),
                        'thumb_url': info.get('thumburl', info.get('url', '')),
                        'width': info.get('width', 0),
                        'height': info.get('height', 0),
                        'mime': mime,
                        'description': re.sub(r'<[^>]+>', '', desc)[:500],
                    })
        except Exception as e:
            print(f'  Metadata error: {e}')
        time.sleep(2)
        if (i // 10) % 5 == 0:
            print(f'  Fetched metadata: {i+10}/{len(titles_list)}')

    print(f'\nGot metadata for {len(all_infos)} images')

    # Download with generous delays
    downloaded = list(existing)
    existing_filenames = {os.path.basename(p.get('local_path', '')) for p in existing}

    new_count = 0
    for i, img in enumerate(all_infos):
        filename = safe_filename(img['title'])
        ext = '.jpg'
        if 'png' in img['mime']:
            ext = '.png'
        elif 'gif' in img['mime']:
            ext = '.gif'
        if not filename.lower().endswith(ext) and not filename.lower().endswith('.jpeg'):
            filename += ext

        filepath = os.path.join(PHOTOS_DIR, filename)

        if os.path.exists(filepath):
            continue

        url = img.get('thumb_url') or img.get('url')
        print(f'  [{new_count+1}] Downloading: {filename[:60]}...')

        if download_image(url, filepath):
            downloaded.append({**img, 'local_path': f'photos/vintage-ads/{filename}'})
            new_count += 1

        time.sleep(3)  # 3 second delay between downloads

    # Save updated catalog
    with open(catalog_path, 'w') as f:
        json.dump(downloaded, f, indent=2)

    print(f'\n=== Done! Downloaded {new_count} new images (total: {len(downloaded)}) ===')

if __name__ == '__main__':
    main()
