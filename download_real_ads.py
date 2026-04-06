#!/usr/bin/env python3
"""
Download real vintage Chevrolet ad scans from oldcaradvertising.com.
URL pattern: https://www.oldcaradvertising.com/Chevrolet/{YEAR}/{YEAR} Chevrolet Ad-{NN}.jpg
"""

import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse

BASE = os.path.dirname(__file__)
ADS_DIR = os.path.join(BASE, 'photos', 'vintage-ads-real')
DATA_DIR = os.path.join(BASE, 'data')
os.makedirs(ADS_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'image/*,*/*;q=0.8',
    'Referer': 'https://www.oldcaradvertising.com/',
}

BASE_URL = 'https://www.oldcaradvertising.com/Chevrolet'

with open(os.path.join(DATA_DIR, 'vintage-ads.json')) as f:
    ads = json.load(f)

needed_years = sorted(set(a['year'] for a in ads if 1913 <= a['year'] <= 1987))
print(f'Need images for {len(needed_years)} unique years')

downloaded = {}
total = 0

for year in needed_years:
    year_str = str(year)
    # Special wartime combined year
    if year in [1942, 1943, 1944, 1945]:
        year_str = '1942-45'

    for ad_num in range(1, 4):  # Get up to 3 per year
        filename = f'{year}_Chevrolet_Ad-{ad_num:02d}.jpg'
        filepath = os.path.join(ADS_DIR, filename)

        if os.path.exists(filepath) and os.path.getsize(filepath) > 5000:
            if year not in downloaded:
                downloaded[year] = []
            downloaded[year].append(filename)
            continue

        # URL encode the space in the filename
        encoded_name = urllib.parse.quote(f'{year_str} Chevrolet Ad-{ad_num:02d}.jpg')
        url = f'{BASE_URL}/{urllib.parse.quote(year_str)}/{encoded_name}'

        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if len(data) > 2000:
                    with open(filepath, 'wb') as f:
                        f.write(data)
                    if year not in downloaded:
                        downloaded[year] = []
                    downloaded[year].append(filename)
                    total += 1
                    print(f'  [{total}] {filename} ({len(data)//1024}KB)')
                else:
                    break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                if ad_num == 1:
                    print(f'  {year}: not found')
                break
            else:
                print(f'  {year}/{ad_num:02d}: HTTP {e.code}')
                break
        except Exception as e:
            print(f'  {year}/{ad_num:02d}: {e}')
            break

        time.sleep(1)

# Save mapping
mapping = {}
for year, files in downloaded.items():
    mapping[str(year)] = [f'photos/vintage-ads-real/{f}' for f in files]

with open(os.path.join(DATA_DIR, 'real-ads-mapping.json'), 'w') as f:
    json.dump(mapping, f, indent=2)

print(f'\n=== Downloaded {total} real ad scans for {len(downloaded)} years ===')
