#!/usr/bin/env python3
"""
Standardize navigation across all ChevyRoots HTML pages.
Uses the homepage (index.html) nav as the canonical format.
"""

import os
import re
import glob

ROOT = '/Users/crystalarriaga/chevyroots'

# ── Canonical nav HTML (from homepage) ──
ANNOUNCEMENT_BAR = '''  <!-- ANNOUNCEMENT BAR -->
  <div class="announcement-bar">
    <span>2026 &mdash;</span> Celebrating America&rsquo;s 250th &amp; 115 Years of Chevrolet &mdash; <span>Built in America. Still Running Strong.</span>
  </div>'''

def make_nav_html(active_page=''):
    """Generate canonical nav HTML with the correct active page."""

    # Map page paths to nav link paths
    nav_links = [
        ('/pages/models/', 'Models'),
        ('/pages/guides/', 'Guides'),
        ('/pages/builds/', 'Builds'),
        ('/pages/events/', 'Events'),
        ("/pages/crystals-corner/", "Crystal's Corner"),
        ('/pages/about/', 'About'),
    ]

    dropdown_links = [
        ('/pages/community/', 'Community'),
        ('/pages/marketplace/', 'Marketplace'),
        ('/pages/tools/', 'Tools'),
        ('/pages/mechanics/', 'Mechanics'),
        ('/pages/news/', 'News'),
        ('/pages/ads/', 'Vintage Ads'),
        ('/pages/newsletter/', 'Newsletter'),
        ('/pages/partners/', 'Partners'),
    ]

    mobile_links = nav_links + dropdown_links

    # Build primary nav links
    primary_items = ''
    for href, label in nav_links:
        is_active = active_page.startswith(href.rstrip('/'))
        cls = ' class="active" aria-current="page"' if is_active else ''
        primary_items += f'        <li><a href="{href}"{cls}>{label}</a></li>\n'

    # Build dropdown
    dropdown_items = ''
    for href, label in dropdown_links:
        is_active = active_page.startswith(href.rstrip('/'))
        cls = ' class="active"' if is_active else ''
        dropdown_items += f'            <a href="{href}"{cls}>{label}</a>\n'

    # Build mobile links
    mobile_items = ''
    for i, (href, label) in enumerate(mobile_links):
        is_active = active_page.startswith(href.rstrip('/'))
        cls = ' class="active"' if is_active else ''
        mobile_items += f'    <a href="{href}"{cls} onclick="this.closest(\'.nav-mobile\').classList.remove(\'open\')">{label}</a>\n'
        if i == len(nav_links) - 1:
            mobile_items += '    <div class="nav-mobile-divider"></div>\n'

    nav_html = f'''  <!-- NAVIGATION -->
  <nav class="nav" role="navigation" aria-label="Main navigation">
    <div class="container nav-inner">

      <a href="/" class="nav-logo" aria-label="ChevyRoots home">
        <span class="nav-logo-main">Chevy<em>Roots</em></span>
        <span class="nav-logo-sub">Run by a Chevy Girl</span>
      </a>

      <ul class="nav-links" role="list">
{primary_items}        <li class="nav-more">
          <button class="nav-more-btn" aria-expanded="false" aria-haspopup="true">More <span class="nav-more-arrow">&#9662;</span></button>
          <div class="nav-dropdown">
{dropdown_items}          </div>
        </li>
      </ul>

      <div class="nav-cta">
        <a href="/pages/builds/" class="btn btn-gold">Submit Your Build</a>
      </div>

      <button class="nav-menu-toggle" aria-label="Toggle mobile menu" onclick="document.getElementById('mobileNav').classList.toggle('open')">
        <span></span><span></span><span></span>
      </button>

    </div>
  </nav>

  <!-- Mobile Nav -->
  <div class="nav-mobile" id="mobileNav" role="navigation" aria-label="Mobile navigation">
{mobile_items}    <a href="/pages/builds/" class="btn btn-gold" style="margin-top:0.5rem;" onclick="this.closest('.nav-mobile').classList.remove('open')">Submit Your Build</a>
  </div>'''

    return nav_html


# Canonical nav CSS
NAV_CSS = '''    /* ============================================================
       ANNOUNCEMENT BAR
    ============================================================ */
    .announcement-bar {
      background: var(--red);
      text-align: center;
      padding: 0.5rem 1rem;
      font-family: var(--font-mono);
      font-size: 0.68rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #fff;
    }
    .announcement-bar span { color: rgba(255,255,255,0.75); }

    /* ============================================================
       NAVIGATION
    ============================================================ */
    .nav {
      position: sticky;
      top: 0;
      z-index: 100;
      height: var(--nav-height);
      background: rgba(26,26,26,0.97);
      border-bottom: 1px solid rgba(196,160,53,0.2);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
    }
    .nav-inner {
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 2rem;
    }
    .nav-logo {
      display: flex;
      flex-direction: column;
      line-height: 1;
    }
    .nav-logo-main {
      font-family: var(--font-heading);
      font-size: 1.6rem;
      font-weight: 900;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--off-white);
    }
    .nav-logo-main em {
      font-style: normal;
      color: var(--gold);
    }
    .nav-logo-sub {
      font-family: var(--font-mono);
      font-size: 0.55rem;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: var(--light-gray);
      margin-top: 1px;
    }
    .nav-links {
      display: flex;
      align-items: center;
      gap: 0.25rem;
    }
    .nav-links a {
      font-family: var(--font-heading);
      font-size: 0.9rem;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--light-gray);
      padding: 0.4rem 0.75rem;
      border-radius: var(--radius);
      transition: color var(--transition), background var(--transition);
    }
    .nav-links a:hover,
    .nav-links a.active {
      color: var(--gold);
      background: rgba(196,160,53,0.08);
    }
    .nav-more {
      position: relative;
    }
    .nav-more-btn {
      font-family: var(--font-heading);
      font-size: 0.9rem;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--light-gray);
      padding: 0.4rem 0.75rem;
      border-radius: var(--radius);
      background: none;
      border: none;
      cursor: pointer;
      transition: color var(--transition), background var(--transition);
      display: flex;
      align-items: center;
      gap: 0.3rem;
    }
    .nav-more-btn:hover {
      color: var(--gold);
      background: rgba(196,160,53,0.08);
    }
    .nav-more-arrow {
      font-size: 0.6rem;
      transition: transform 0.2s;
    }
    .nav-dropdown {
      position: absolute;
      top: 100%;
      right: 0;
      min-width: 200px;
      background: #2A2A2A;
      border: 1px solid #3A3A3A;
      border-top: 2px solid var(--gold);
      border-radius: 0 0 var(--radius-lg) var(--radius-lg);
      padding: 0.5rem 0;
      opacity: 0;
      visibility: hidden;
      transform: translateY(-4px);
      transition: opacity 0.2s, transform 0.2s, visibility 0.2s;
      z-index: 200;
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }
    .nav-more:hover .nav-dropdown,
    .nav-more.open .nav-dropdown {
      opacity: 1;
      visibility: visible;
      transform: translateY(0);
    }
    .nav-more:hover .nav-more-arrow {
      transform: rotate(180deg);
    }
    .nav-dropdown a {
      display: block;
      font-family: var(--font-heading);
      font-size: 0.85rem;
      font-weight: 600;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--light-gray);
      padding: 0.5rem 1.25rem;
      transition: color var(--transition), background var(--transition);
    }
    .nav-dropdown a:hover,
    .nav-dropdown a.active {
      color: var(--gold);
      background: rgba(196,160,53,0.08);
    }
    .nav-cta {
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    .nav-menu-toggle {
      display: none;
      flex-direction: column;
      gap: 5px;
      cursor: pointer;
      padding: 0.5rem;
      background: none;
      border: none;
    }
    .nav-menu-toggle span {
      display: block;
      width: 22px;
      height: 2px;
      background: var(--off-white);
      transition: var(--transition);
    }
    .nav-mobile {
      display: none;
      position: fixed;
      top: var(--nav-height);
      left: 0;
      right: 0;
      background: var(--warm-gray);
      border-bottom: 2px solid var(--gold);
      padding: 1.5rem;
      z-index: 99;
      flex-direction: column;
      gap: 0.25rem;
    }
    .nav-mobile.open { display: flex; }
    .nav-mobile a {
      font-family: var(--font-heading);
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--off-white);
      padding: 0.75rem 1rem;
      border-radius: var(--radius);
      transition: color var(--transition), background var(--transition);
    }
    .nav-mobile a:hover,
    .nav-mobile a.active {
      color: var(--gold);
      background: rgba(196,160,53,0.08);
    }
    .nav-mobile-divider {
      height: 1px;
      background: rgba(196,160,53,0.2);
      margin: 0.5rem 0;
    }'''

# Responsive CSS to inject into @media (max-width: 768px) if not present
NAV_RESPONSIVE = '''      .nav-links,
      .nav-cta { display: none; }
      .nav-menu-toggle { display: flex; }'''


def get_active_page(filepath):
    """Determine the active page path from the file location."""
    rel = os.path.relpath(filepath, ROOT)
    # index.html at root = home page
    if rel == 'index.html':
        return '/'
    # pages/news/index.html -> /pages/news
    parts = rel.replace('index.html', '').rstrip('/')
    return '/' + parts


def process_file(filepath):
    """Process a single HTML file to standardize its navigation."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    active_page = get_active_page(filepath)

    # Skip if not a real page (e.g., template files)
    if '<html' not in content:
        return False

    # ── Step 1: Replace nav HTML ──

    # Pattern to match any existing announcement bar
    ann_patterns = [
        r'<!--\s*=+\s*\n\s*ANNOUNCEMENT BAR\s*\n\s*=+\s*-->\s*\n\s*<div class="announcement-bar">.*?</div>',
        r'<!--\s*ANNOUNCEMENT BAR\s*-->\s*\n\s*<div class="announcement-bar">.*?</div>',
        r'<div class="announcement-bar">.*?</div>',
    ]

    # Pattern to match any existing nav (all three formats)
    nav_patterns = [
        # Format A: with comments
        r'<!--\s*=+\s*\n\s*NAVIGATION\s*\n\s*=+\s*-->\s*\n\s*<nav[^>]*class="nav"[^>]*>.*?</nav>\s*\n\s*<!--\s*Mobile Nav\s*-->\s*\n\s*<div[^>]*class="nav-mobile"[^>]*id="mobileNav"[^>]*>.*?</div>',
        # Format A without mobile nav
        r'<!--\s*=+\s*\n\s*NAVIGATION\s*\n\s*=+\s*-->\s*\n\s*<nav[^>]*class="nav"[^>]*>.*?</nav>',
        # Format B: BEM style
        r'<nav[^>]*class="nav"[^>]*>.*?</nav>\s*(?:<div[^>]*class="nav-mobile"[^>]*>.*?</div>)?',
        # Generic nav
        r'<nav[^>]*role="navigation"[^>]*>.*?</nav>',
    ]

    # Try to find and replace the announcement bar + nav block
    # First, try to find the full block (announcement + nav + mobile)
    full_block_pattern = re.compile(
        r'(<!--[^>]*ANNOUNCEMENT[^>]*-->[\s\S]*?<div class="announcement-bar">[\s\S]*?</div>\s*)?'
        r'(<div class="announcement-bar">[\s\S]*?</div>\s*)?'
        r'(<!--[^>]*NAVIGATION[^>]*-->\s*)?'
        r'<nav\b[^>]*>[\s\S]*?</nav>\s*'
        r'(<!--\s*Mobile Nav\s*-->\s*)?'
        r'(<div[^>]*(?:class="nav-mobile"|id="mobileNav")[^>]*>[\s\S]*?</div>\s*)?',
        re.IGNORECASE
    )

    canonical = ANNOUNCEMENT_BAR + '\n\n' + make_nav_html(active_page) + '\n'

    match = full_block_pattern.search(content)
    if match:
        content = content[:match.start()] + canonical + '\n' + content[match.end():]
    else:
        # Insert after <body> tag
        body_match = re.search(r'<body[^>]*>', content)
        if body_match:
            insert_pos = body_match.end()
            content = content[:insert_pos] + '\n\n' + canonical + '\n' + content[insert_pos:]

    # ─�� Step 2: Ensure nav CSS exists ──
    # Check if nav CSS is present (look for .nav-more-btn which is unique to canonical format)
    if '.nav-more-btn' not in content and '<style>' in content:
        # Find the first section comment after variables/reset/base
        # Insert nav CSS before the first page-specific CSS section
        # Look for a good insertion point after base styles
        style_sections = [
            '/* ============================================================\n       HERO',
            '/* ============================================================\n       PAGE HERO',
            '/* ============================================================\n       HEADER',
            '/* ============================================================\n       FEATURED',
            '/* ============================================================\n       CONTENT',
            '/* ============================================================\n       SECTION',
        ]

        inserted = False
        for section_marker in style_sections:
            idx = content.find(section_marker)
            if idx != -1:
                content = content[:idx] + NAV_CSS + '\n\n    ' + content[idx:]
                inserted = True
                break

        if not inserted:
            # Insert before </style>
            style_end = content.find('</style>')
            if style_end != -1:
                content = content[:style_end] + '\n' + NAV_CSS + '\n  ' + content[style_end:]

    # ── Step 3: Ensure responsive nav rules exist ──
    if '.nav-menu-toggle { display: flex; }' not in content:
        # Find @media (max-width: 768px) block and add nav responsive rules
        media_match = re.search(r'@media\s*\(max-width:\s*768px\)\s*\{', content)
        if media_match:
            insert_pos = media_match.end()
            content = content[:insert_pos] + '\n' + NAV_RESPONSIVE + '\n' + content[insert_pos:]

    # ── Step 4: Clean up duplicate announcement bars ──
    # Count announcement bars
    ann_count = content.count('class="announcement-bar"')
    if ann_count > 1:
        # Keep only the first one
        first_idx = content.find('class="announcement-bar"')
        remaining = content[first_idx + len('class="announcement-bar"'):]
        while 'class="announcement-bar"' in remaining:
            dup_start = remaining.find('<div class="announcement-bar">')
            dup_end = remaining.find('</div>', dup_start) + len('</div>')
            remaining = remaining[:dup_start] + remaining[dup_end:]
        content = content[:first_idx + len('class="announcement-bar"')] + remaining

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    # Find all HTML files
    html_files = []
    for pattern in ['*.html', 'pages/**/*.html']:
        html_files.extend(glob.glob(os.path.join(ROOT, pattern), recursive=True))

    html_files = sorted(set(html_files))

    updated = 0
    skipped = 0
    errors = []

    for filepath in html_files:
        rel = os.path.relpath(filepath, ROOT)
        try:
            if process_file(filepath):
                print(f'  UPDATED: {rel}')
                updated += 1
            else:
                print(f'  (no change): {rel}')
                skipped += 1
        except Exception as e:
            print(f'  ERROR: {rel} — {e}')
            errors.append((rel, str(e)))

    print(f'\nDone. Updated: {updated}, Unchanged: {skipped}, Errors: {len(errors)}')
    if errors:
        for path, err in errors:
            print(f'  {path}: {err}')


if __name__ == '__main__':
    main()
