#!/usr/bin/env python3
"""
Download vintage Chevrolet advertisement images from Wikimedia Commons.
Searches for actual ad scans, brochures, and promotional materials.
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

PHOTOS_DIR = os.path.join(os.path.dirname(__file__), 'photos', 'vintage-ads')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
COMMONS_API = 'https://commons.wikimedia.org/w/api.php'

# User agent required by Wikimedia
HEADERS = {
    'User-Agent': 'ChevyRootsBot/1.0 (https://chevyroots.com; educational project)'
}


def api_request(params):
    """Make a request to the Wikimedia Commons API."""
    params['format'] = 'json'
    url = COMMONS_API + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f'  API error: {e}')
        return None


def search_commons(query, limit=50):
    """Search Wikimedia Commons for files matching query."""
    results = []
    params = {
        'action': 'query',
        'list': 'search',
        'srnamespace': '6',  # File namespace
        'srsearch': query,
        'srlimit': str(limit),
    }
    data = api_request(params)
    if data and 'query' in data:
        for item in data['query']['search']:
            results.append(item['title'])
    return results


def get_category_files(category, limit=100):
    """Get files from a Wikimedia Commons category."""
    results = []
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': category,
        'cmtype': 'file',
        'cmlimit': str(limit),
    }
    data = api_request(params)
    if data and 'query' in data:
        for item in data['query']['categorymembers']:
            results.append(item['title'])
    return results


def get_file_info(titles):
    """Get image URLs and metadata for a list of file titles."""
    if not titles:
        return []

    results = []
    # Process in batches of 20
    for i in range(0, len(titles), 20):
        batch = titles[i:i+20]
        params = {
            'action': 'query',
            'titles': '|'.join(batch),
            'prop': 'imageinfo|categories',
            'iiprop': 'url|size|mime|extmetadata',
            'iiurlwidth': '800',  # Get thumbnail
        }
        data = api_request(params)
        if data and 'query' in data and 'pages' in data['query']:
            for page_id, page in data['query']['pages'].items():
                if 'imageinfo' not in page:
                    continue
                info = page['imageinfo'][0]

                # Only include images (not SVGs, PDFs without preview, etc.)
                mime = info.get('mime', '')
                if not mime.startswith('image/'):
                    continue

                ext_meta = info.get('extmetadata', {})
                desc = ext_meta.get('ImageDescription', {}).get('value', '')
                date = ext_meta.get('DateTimeOriginal', {}).get('value', '')
                artist = ext_meta.get('Artist', {}).get('value', '')
                license_short = ext_meta.get('LicenseShortName', {}).get('value', '')

                results.append({
                    'title': page['title'],
                    'url': info.get('url', ''),
                    'thumb_url': info.get('thumburl', info.get('url', '')),
                    'thumb_width': info.get('thumbwidth', info.get('width', 0)),
                    'thumb_height': info.get('thumbheight', info.get('height', 0)),
                    'width': info.get('width', 0),
                    'height': info.get('height', 0),
                    'mime': mime,
                    'description': re.sub(r'<[^>]+>', '', desc)[:500],
                    'date': date,
                    'artist': re.sub(r'<[^>]+>', '', artist)[:200],
                    'license': license_short,
                })
        time.sleep(0.5)  # Be nice to the API

    return results


def download_image(url, filepath):
    """Download an image to a local filepath."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(filepath, 'wb') as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f'  Download error: {e}')
        return False


def safe_filename(title):
    """Convert a Wikimedia title to a safe filename."""
    name = title.replace('File:', '').strip()
    name = re.sub(r'[^\w\s\-.]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name[:120]


def main():
    os.makedirs(PHOTOS_DIR, exist_ok=True)

    all_files = set()

    # Search queries for actual advertisements
    search_queries = [
        'Chevrolet advertisement vintage',
        'Chevrolet print ad',
        'Chevrolet brochure',
        'Chevrolet commercial poster',
        'Chevrolet dealer advertisement',
        'Corvette advertisement',
        'Camaro advertisement',
        'Chevrolet magazine ad',
        'Chevrolet newspaper ad',
        '"Chevrolet" "advertisement"',
        'Chevrolet promotional',
        'Impala advertisement',
        'Bel Air advertisement Chevrolet',
        'Chevelle advertisement',
        'Silverado advertisement',
        'Chevrolet truck advertisement',
        '"See the USA" Chevrolet',
        '"Heartbeat of America" Chevrolet',
        '"Like a Rock" Chevrolet',
        'Chevrolet ad 1950s',
        'Chevrolet ad 1960s',
        'Chevrolet ad 1930s',
        'Chevrolet ad 1920s',
    ]

    # Categories to search
    categories = [
        'Category:Chevrolet_advertisements',
        'Category:Chevrolet_brochures',
        'Category:Advertisements_for_automobiles',
        'Category:Chevrolet_vehicles_in_art',
        'Category:Corvette_in_popular_culture',
    ]

    print('=== Searching Wikimedia Commons for Chevrolet ads ===\n')

    # Search by query
    for query in search_queries:
        print(f'Searching: {query}')
        files = search_commons(query, limit=50)
        # Filter for likely ad images
        for f in files:
            fl = f.lower()
            if any(kw in fl for kw in ['chevrolet', 'chevy', 'corvette', 'camaro', 'impala',
                                         'bel air', 'chevelle', 'silverado', 'nova', 'malibu',
                                         'monte carlo', 'blazer', 'tahoe', 'suburban']):
                all_files.add(f)
        time.sleep(0.3)

    # Search by category
    for cat in categories:
        print(f'Category: {cat}')
        files = get_category_files(cat, limit=100)
        all_files.update(files)
        time.sleep(0.3)

    print(f'\nFound {len(all_files)} potential files\n')

    # Get metadata for all files
    all_titles = list(all_files)
    print('Fetching file metadata...')
    file_infos = get_file_info(all_titles)

    # Filter to likely advertisements (not just any car photo)
    ad_images = []
    ad_keywords = ['ad', 'advertisement', 'advert', 'brochure', 'poster', 'promo',
                   'catalog', 'catalogue', 'dealer', 'flyer', 'leaflet', 'commercial',
                   'marketing', 'promotional', 'print ad', 'magazine ad', 'newspaper']

    for info in file_infos:
        combined = (info['title'] + ' ' + info['description']).lower()
        # Include if it looks like an ad, or if it's from a Chevy ad category
        is_ad = any(kw in combined for kw in ad_keywords)
        is_chevy = any(kw in combined for kw in ['chevrolet', 'chevy', 'corvette', 'camaro'])
        is_vintage = any(kw in combined for kw in ['vintage', 'classic', 'antique', 'historic', 'retro', '19'])

        if is_chevy and (is_ad or is_vintage):
            ad_images.append(info)

    print(f'Filtered to {len(ad_images)} likely advertisement images\n')

    # Download images
    downloaded = []
    for i, img in enumerate(ad_images):
        filename = safe_filename(img['title'])
        # Determine extension
        ext = '.jpg'
        if 'png' in img['mime']:
            ext = '.png'
        elif 'gif' in img['mime']:
            ext = '.gif'
        elif 'webp' in img['mime']:
            ext = '.webp'

        if not filename.lower().endswith(ext):
            filename += ext

        filepath = os.path.join(PHOTOS_DIR, filename)

        if os.path.exists(filepath):
            print(f'  [{i+1}/{len(ad_images)}] Already exists: {filename}')
            downloaded.append({**img, 'local_path': f'photos/vintage-ads/{filename}'})
            continue

        # Use thumbnail (800px wide) for reasonable file sizes
        url = img.get('thumb_url') or img.get('url')
        print(f'  [{i+1}/{len(ad_images)}] Downloading: {filename}')

        if download_image(url, filepath):
            downloaded.append({**img, 'local_path': f'photos/vintage-ads/{filename}'})

        time.sleep(0.5)  # Rate limit

    # Save catalog
    catalog_path = os.path.join(DATA_DIR, 'vintage-ads-images.json')
    with open(catalog_path, 'w') as f:
        json.dump(downloaded, f, indent=2)

    print(f'\n=== Done! Downloaded {len(downloaded)} images ===')
    print(f'Catalog saved to: {catalog_path}')

    return downloaded


if __name__ == '__main__':
    main()
