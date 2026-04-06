# ChevyRoots QA Report — Final
_Run: 2026-04-05_

---

## PRIORITY FIX LIST (Top 5)

| # | Issue | Severity | File(s) |
|---|-------|----------|---------|
| 1 | `best-mods-silverado.html` is a 0-byte empty file — linked from guides index, returns blank page | CRITICAL | `/pages/guides/best-mods-silverado.html` |
| 2 | 5 guide articles missing from guides hub (`/pages/guides/index.html`) | HIGH | `index.html` |
| 3 | 3 guide pages have old/stripped nav missing Crystal's Corner and News | HIGH | `best-exhaust`, `best-cold-air-intake`, `best-tonneau-covers` |
| 4 | `builds/index.html` missing News link in nav and missing newsletter CTA | HIGH | `/pages/builds/index.html` |
| 5 | `crystals-corner/index.html` and `chevy-towing-guide.html` missing GM non-affiliation disclaimer | HIGH | 2 pages |

---

## 1. BROKEN INTERNAL LINKS (404s)

Total unique internal `href` values found: **98**
Total broken (target file does not exist): **59**

### Critical broken links (user-facing)
| Link | Source page(s) |
|------|----------------|
| `/pages/models/trucks/` | `index.html` (homepage hero) |
| `/pages/models/cars/` | `index.html` |
| `/pages/models/classics/` | `index.html` |
| `/pages/models/suvs/` | `index.html` |
| `/pages/models/evs/` | `index.html` |
| `/pages/models/corvette/` | `index.html` |
| `/pages/models/silverado/` | `builds/index.html` |
| `/pages/models/c10/` | `builds/index.html` |
| `/pages/builds/submit/` | `marketplace/index.html` |
| `/pages/events/submit/` | `marketplace/index.html` |
| `/pages/advertise/` | `marketplace/index.html` |
| `/pages/contact/` | multiple guides |
| `/pages/disclaimer/` | `chevy-towing-guide.html` |
| `/pages/history/` | `c8-corvette-best-year-to-buy.html` |
| `/pages/write/` | `about/index.html` |
| `/privacy/` | `index.html`, `crystals-corner` |
| `/terms/` | `index.html`, `crystals-corner` |
| `/pages/privacy/` | `marketplace/index.html` |
| `/pages/terms/` | `marketplace/index.html` |
| `/privacy.html` | `quiz.html` |
| `/pages/guides/chevy-vs-ford-trucks.html` | `ls-swap-guide.html` |
| `/pages/guides/lift-kit-guide/` | `builds/index.html` |
| `/pages/guides/towing.html` | `quiz.html` |
| `/pages/guides/maintenance/` | `models/generate-static.html` |
| `/pages/guides/${m.guideSlug}.html` | `quiz.html` (dynamic — OK in JS context) |

### Models sub-page links (all broken — model sub-routing not implemented)
Links like `/pages/guides/silverado-1500/`, `/pages/guides/corvette-stingray/`, etc. from `models/index.html` — approximately 20 broken model sub-page links. These appear to be dynamically-expected routes that don't exist as static files.

**Severity: HIGH** — The homepage has 6 broken category filter links. The `models/index.html` has ~20 broken links to model-specific sub-pages.

---

## 2. PAGE ELEMENT AUDIT

Checked all 39 HTML pages for: "Run by a Chevy Girl", Crystal's Corner in nav, News in nav, newsletter CTA, GM non-affiliation disclaimer.

### Missing "Run by a Chevy Girl"
- `/pages/guides/best-mods-silverado.html` — **EMPTY FILE** (see Issue #1)
- `/pages/guides/chevy-dream-tour.html` — nav says "Where Chevy Runs Deep" instead

### Missing Crystal's Corner in nav
- `/pages/guides/best-cold-air-intake-silverado.html` — old-style stripped nav
- `/pages/guides/best-exhaust-silverado.html` — old-style stripped nav
- `/pages/guides/best-mods-silverado.html` — empty file
- `/pages/guides/best-tonneau-covers-silverado.html` — old-style stripped nav
- `/pages/guides/c8-corvette-best-year-to-buy.html` — nav omits Crystal's Corner
- `/pages/guides/chevy-dream-tour.html` — minimal nav

### Missing News in nav
- `/pages/builds/index.html` — nav has Crystal's Corner but skips News
- `/pages/community/index.html` — nav has Crystal's Corner but skips News
- `/pages/marketplace/index.html` — nav omits News
- `/pages/guides/best-cold-air-intake-silverado.html` — old nav
- `/pages/guides/best-exhaust-silverado.html` — old nav
- `/pages/guides/best-mods-silverado.html` — empty file
- `/pages/guides/best-tonneau-covers-silverado.html` — old nav
- `/pages/guides/chevy-dream-tour.html` — minimal nav
- `/pages/guides/silverado-5.3-vs-6.2.html` — nav omits News

### Missing newsletter CTA
- `/pages/about/index.html`
- `/pages/ads/index.html`
- `/pages/builds/index.html`
- `/pages/guides/compare.html`
- `/pages/guides/index.html`
- `/pages/guides/known-issues.html`
- `/pages/guides/quiz.html`
- `/pages/marketplace/index.html`
- `/pages/models/generate-static.html` (internal tool, low priority)
- `/pages/models/index.html`
- `/pages/models/template.html` (template, low priority)
- `/pages/tools/index.html`
- `/pages/guides/chevy-history.html`

### Missing GM non-affiliation disclaimer
- `/pages/crystals-corner/index.html` — footer has no disclaimer text
- `/pages/guides/best-mods-silverado.html` — empty file
- `/pages/guides/chevy-towing-guide.html` — footer exists but no GM disclaimer

---

## 3. GUIDES HUB COVERAGE

| Category | Files on disk | Linked from index | Missing |
|----------|--------------|-------------------|---------|
| Total articles | 22 | 17 | 5 |

**5 guide articles exist on disk but are NOT linked from `/pages/guides/index.html`:**
1. `best-cold-air-intake-silverado.html` (41 KB — full article)
2. `best-exhaust-silverado.html` (40 KB — full article)
3. `best-tonneau-covers-silverado.html` (38 KB — full article)
4. `chevy-maintenance-schedule.html` (45 KB — full article)
5. `tahoe-vs-suburban.html` (37 KB — full article, also missing from find output earlier)

**Severity: HIGH** — Visitors cannot discover these articles from the guides hub.

---

## 4. PLACEHOLDER IMAGE DIVS

No `background: #333` divs with placeholder text (e.g. "PHOTO: Silverado") were found. All `#333` usage is as a CSS fallback color behind real photo URLs. **No issues found.**

---

## 5. HOMEPAGE HERO SLIDER

All 5 image paths verified to exist on disk:

| # | Path | Status |
|---|------|--------|
| 1 | `/photos/camaro/pexels_12579271_camaro.jpeg` | OK |
| 2 | `/photos/corvette/Chevrolet_Corvette_C8_IAA_2021_1X7A0156.jpg` | OK |
| 3 | `/photos/silverado/pexels_28226938_silverado.jpeg` | OK |
| 4 | `/photos/camaro/pexels_10590576_camaro.jpeg` | OK |
| 5 | `/photos/chevelle/1971_Chevrolet_Chevelle_SS_Convertible.jpg` | OK |

**No issues found.**

---

## 6. vehicles.json

- **Valid JSON:** YES
- **Structure:** `{ "vehicles": [...] }` — 20 entries
- **Schema used:** `model`, `slug`, `category`, `years[]`
- **All 20 entries have required schema fields:** YES
- **Note:** Fields are `model/slug/category/years` (not `id/make/year`) — this is the file's own schema and is consistent across all entries.

**No issues found.**

---

## 7. known-issues.json

- **Valid JSON:** YES
- **Structure:** `{ "known_issues": [...] }` — 11 entries
- **Fields:** `model`, `slug`, `issues_by_year`

**No issues found.**

---

## COMPLETE ISSUE REGISTER

| ID | Severity | Description | Fixed? |
|----|----------|-------------|--------|
| CR-01 | CRITICAL | `best-mods-silverado.html` is 0 bytes (empty file), linked from guides index | YES |
| CR-02 | HIGH | 5 guide articles not linked from guides hub index | YES |
| CR-03 | HIGH | `best-exhaust`, `best-cold-air-intake`, `best-tonneau-covers` have old stripped nav (missing Crystal's Corner + News) | YES |
| CR-04 | HIGH | `builds/index.html` missing News in nav and newsletter CTA | YES |
| CR-05 | HIGH | `crystals-corner/index.html` missing GM non-affiliation disclaimer | YES |
| CR-06 | HIGH | `chevy-towing-guide.html` missing GM non-affiliation disclaimer | YES (fixed alongside CR-05) |
| CR-07 | HIGH | Homepage has 6 broken model category filter links (`/pages/models/trucks/`, etc.) | NO — needs model routing |
| CR-08 | HIGH | `models/index.html` has ~20 broken model-specific sub-page links | NO — needs static model pages |
| CR-09 | MEDIUM | `chevy-dream-tour.html` nav says "Where Chevy Runs Deep" instead of "Run by a Chevy Girl", missing Crystal's Corner + News | NO |
| CR-10 | MEDIUM | `c8-corvette-best-year-to-buy.html` missing Crystal's Corner + News in nav | NO |
| CR-11 | MEDIUM | `silverado-5.3-vs-6.2.html` missing News in nav | NO |
| CR-12 | MEDIUM | Newsletter CTA missing on: about, ads, builds, compare, guides-index, known-issues, quiz, marketplace, models-index, tools, chevy-history | Partial (builds fixed) |
| CR-13 | MEDIUM | `community/index.html` and `marketplace/index.html` missing News in nav | NO |
| CR-14 | LOW | ~35 additional broken links (advertise, contact, disclaimer, privacy, terms, write, lift-kit-guide, etc.) — pages not built yet | NO |
| CR-15 | LOW | `ls-swap-guide.html` links to non-existent `/pages/guides/chevy-vs-ford-trucks.html` | NO |
| CR-16 | LOW | `quiz.html` has broken `/privacy.html` and `/pages/guides/towing.html` links | NO |
| CR-17 | INFO | `vehicles.json` uses `model/slug/category` schema (no top-level `id` or `make` fields) — consistent, but differs from a possible expected schema | N/A |

---

## FIXES APPLIED

### Fix 1 — CR-01: Rebuilt empty best-mods-silverado.html (CRITICAL)
`/pages/guides/best-mods-silverado.html` was 0 bytes. Rebuilt as a complete 32KB article with:
- Full standard nav (Crystal's Corner, News, all links)
- Hero header, article content (8 mods ranked with specs and affiliate links)
- Newsletter CTA section
- Footer with GM non-affiliation disclaimer

### Fix 2 — CR-02: Added 7 missing guide cards to guides/index.html (HIGH)
The guides hub was missing 7 articles that existed on disk. Added cards to their appropriate sections:
- **Buyer's Guides section:** `chevy-dealer-negotiation.html`, `used-chevy-truck-guide.html`, `tahoe-vs-suburban.html`
- **How-To & Mods section:** `best-cold-air-intake-silverado.html`, `best-exhaust-silverado.html`, `best-tonneau-covers-silverado.html`, `chevy-maintenance-schedule.html`
- All 24 guide article files now have matching cards in the index.

### Fix 3 — CR-03: Updated nav on 3 guide pages (HIGH)
`best-exhaust-silverado.html`, `best-cold-air-intake-silverado.html`, and `best-tonneau-covers-silverado.html` had an old stripped nav (linking to `/index.html` instead of `/`, missing Crystal's Corner and News). Updated to full standard nav on all three.

### Fix 4 — CR-04: Added News link and newsletter CTA to builds/index.html (HIGH)
- Added `<li><a href="/pages/news/">News</a></li>` to nav
- Added a complete newsletter signup section before the footer

### Fix 5 — CR-05/06: Added GM non-affiliation disclaimer to 2 pages (HIGH)
- `crystals-corner/index.html`: Added disclaimer paragraph to footer bottom
- `chevy-towing-guide.html`: Added disclaimer paragraph to footer-bottom section
- Also updated footer disclaimer text on `best-exhaust`, `best-cold-air-intake`, and `best-tonneau-covers` to explicitly state non-affiliation with GM (previously said "independent" without the explicit non-affiliation language)
