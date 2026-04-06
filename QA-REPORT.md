# ChevyRoots.com — QA Audit Report
**Date:** 2026-04-05
**Auditor:** QA Agent
**Scope:** All 15 HTML pages under `/Users/crystalarriaga/chevyroots/`

---

## Summary Table

| Page | Issues Found | Severity |
|------|-------------|----------|
| `index.html` | Broken links (4), Mobile nav has "News" link not in desktop spec, Desktop nav has "News" (not in brief), Logo subtitle correct, Stats OK, 8 placeholders | HIGH |
| `pages/models/index.html` | Missing Crystal's Corner in nav, No logo subtitle, Wrong MSRP data (6+ vehicles), No GM disclaimer, Many broken guide links (20+) | CRITICAL |
| `pages/events/index.html` | Missing Crystal's Corner in nav, No logo subtitle, No GM disclaimer, Broken links (2), 10 placeholders, All event detail links are `#` | HIGH |
| `pages/about/index.html` | Missing Crystal's Corner in nav, No logo subtitle, Broken links (3) | HIGH |
| `pages/builds/index.html` | Completely different nav (wrong pages), No GM disclaimer, Missing Crystal's Corner, No logo subtitle, Broken links (4+) | CRITICAL |
| `pages/guides/index.html` | Broken relative paths in nav (`../../`), Missing Crystal's Corner, Wrong copyright year (2025), Broken links (2) | HIGH |
| `pages/guides/quiz.html` | Missing Crystal's Corner in nav, No About link, Broken links (2) | MEDIUM |
| `pages/guides/known-issues.html` | Broken relative paths in nav (`../../`), Missing Crystal's Corner, Wrong copyright year (2025) | HIGH |
| `pages/guides/small-block-chevy-history.html` | Missing Crystal's Corner in nav | MEDIUM |
| `pages/guides/c8-corvette-buyers-guide.html` | Missing Crystal's Corner in nav | MEDIUM |
| `pages/guides/america-250-chevy-road-trip.html` | Missing Crystal's Corner in nav | MEDIUM |
| `pages/newsletter/index.html` | Logo subtitle says "Independent Chevrolet Resource" (not "Run by a Chevy Girl"), Missing Crystal's Corner in nav | HIGH |
| `pages/partners/index.html` | Logo subtitle says "Independent Chevrolet Resource" (not "Run by a Chevy Girl"), Missing Crystal's Corner in nav | HIGH |
| `pages/crystals-corner/index.html` | Clean — correct subtitle and nav ✓ | LOW |
| `pages/models/template.html` | Utility file, not a published page — no nav or footer | INFO |

---

## 1. Broken Links

### Pages That Do Not Exist (53 broken link targets)

The following paths are linked from one or more pages but have **no corresponding file or directory** on disk:

**Builds:**
- `/pages/builds/submit/` — linked from `about/index.html`
- `/pages/builds/1970-chevelle-ss-green-machine/` — linked from `index.html` (featured build CTA)

**Events:**
- `/pages/events/2026-chevy-show-season/` — linked from `index.html` (article card)
- `/pages/events/submit/` — linked from `about/index.html`

**Guides — Individual Model Guides (all missing):**
- `/pages/guides/silverado-1500/`
- `/pages/guides/silverado-hd/`
- `/pages/guides/colorado/`
- `/pages/guides/tahoe/`
- `/pages/guides/suburban/`
- `/pages/guides/traverse/`
- `/pages/guides/equinox/`
- `/pages/guides/blazer/`
- `/pages/guides/trailblazer/`
- `/pages/guides/trax/`
- `/pages/guides/malibu/`
- `/pages/guides/corvette-stingray/`
- `/pages/guides/corvette-z06/`
- `/pages/guides/corvette-e-ray/`
- `/pages/guides/camaro/`
- `/pages/guides/equinox-ev/`
- `/pages/guides/blazer-ev/`
- `/pages/guides/silverado-ev/`
- `/pages/guides/chevelle/`
- `/pages/guides/camaro-classic/`
- `/pages/guides/nova/`
- `/pages/guides/bel-air/`
- `/pages/guides/impala-classic/`
- `/pages/guides/caprice/`
- `/pages/guides/c10/`
- `/pages/guides/k5-blazer/`
- `/pages/guides/square-body/`
- `/pages/guides/corvette-c1/`
- `/pages/guides/corvette-c2/`
- `/pages/guides/corvette-c3/`
- `/pages/guides/c8-vs-c6-corvette/` — linked from `index.html` (article card)
- `/pages/guides/whats-your-chevy/` — linked from `index.html` (quiz CTA + footer)
- `/pages/guides/maintenance/` — linked from `index.html` footer
- `/pages/guides/compare.html` — linked from `quiz.html`
- `/pages/guides/towing.html` — linked from `quiz.html`
- `/pages/guides/small-block-chevy-history/` (with trailing slash) — linked from `models/index.html`; the `.html` version exists but the slash version does not

**Models Sub-Category Pages (all missing):**
- `/pages/models/trucks/`
- `/pages/models/corvette/`
- `/pages/models/classics/`
- `/pages/models/cars/`
- `/pages/models/suvs/`
- `/pages/models/evs/`

**Other Missing Pages:**
- `/pages/community/` — directory exists but is empty (no `index.html`)
- `/pages/news/` — directory exists but is empty (no `index.html`); linked from `index.html` desktop AND mobile nav
- `/pages/parts/` — linked from `builds/index.html` nav
- `/pages/registry/` — linked from `builds/index.html` nav
- `/pages/privacy/` and `/privacy/` — footer links across multiple pages; neither exists
- `/pages/terms/` and `/terms/` — footer links across multiple pages; neither exists
- `/pages/write/` — linked from `about/index.html` footer
- `/pages/advertise/` — linked from `about/index.html` footer

### Relative Path Errors (Guides sub-pages)

`pages/guides/index.html` and `pages/guides/known-issues.html` use relative paths (`../../pages/models/`, `../../about/`) in the nav. Since these files sit at depth `/pages/guides/`, going `../../` reaches the root correctly for `../../pages/models/`, but `../../about/` resolves to `/about/` — not `/pages/about/`. This is a broken nav link. These pages should use absolute paths (`/pages/models/`, `/pages/about/`) like every other page does.

---

## 2. Nav Consistency

### Required Nav Links (per brief): Models, Guides, Builds, Events, Crystal's Corner, About

| Page | Models | Guides | Builds | Events | Crystal's Corner | About | Extra / Wrong Links |
|------|--------|--------|--------|--------|-----------------|-------|---------------------|
| `index.html` (desktop) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **"News" added — not in spec** |
| `index.html` (mobile) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **"News" added — not in spec** |
| `models/index.html` | ✓ | ✓ (as "Buying Guides") | ✓ | ✓ | **MISSING** | ✓ | "Home", "Find Your Chevy" CTA |
| `events/index.html` | ✓ | ✓ | ✓ | ✓ | **MISSING** | ✓ | — |
| `about/index.html` | ✓ | **MISSING** | ✓ | ✓ | **MISSING** | ✓ | — |
| `builds/index.html` | ✓ | **MISSING** | ✓ | **MISSING** | **MISSING** | **MISSING** | "VIN Registry", "Community", "Parts" (all broken) |
| `guides/index.html` | ✓ | ✓ | ✓ | ✓ | **MISSING** | ✓ | Relative paths (see §1) |
| `guides/quiz.html` | ✓ | ✓ | ✓ | ✓ | **MISSING** | **MISSING** | — |
| `guides/known-issues.html` | ✓ | ✓ | ✓ | ✓ | **MISSING** | ✓ | Relative paths (see §1) |
| `guides/small-block-chevy-history.html` | ✓ | ✓ | ✓ | ✓ | **MISSING** | ✓ | — |
| `guides/c8-corvette-buyers-guide.html` | ✓ | ✓ | ✓ | ✓ | **MISSING** | ✓ | — |
| `guides/america-250-chevy-road-trip.html` | ✓ | ✓ | ✓ | ✓ | **MISSING** | ✓ | — |
| `newsletter/index.html` | ✓ | ✓ | ✓ | ✓ | **MISSING** | ✓ | "Newsletter" self-link |
| `partners/index.html` | ✓ | ✓ | ✓ | ✓ | **MISSING** | ✓ | — |
| `crystals-corner/index.html` | ✓ | ✓ | ✓ | ✓ | ✓ (active) | ✓ | — |

**Summary:** Crystal's Corner is missing from 12 of 15 pages. The `builds/index.html` nav is the most broken — it appears to have been built with an entirely different site architecture in mind (VIN Registry, Community, Parts).

---

## 3. Logo Subtitle

The correct subtitle is **"Run by a Chevy Girl"**.

| Page | Subtitle Present | Subtitle Text | Correct? |
|------|-----------------|---------------|----------|
| `index.html` | Yes | "Run by a Chevy Girl" | ✓ |
| `models/index.html` | **No** | None — logo is plain text only | ✗ |
| `events/index.html` | **No** | Logo renders as `Chevy<span>Roots</span>` with no subtitle | ✗ |
| `about/index.html` | **No** | Logo renders as `Chevy<span>Roots</span>` with no subtitle | ✗ |
| `builds/index.html` | **No** | Logo is `CHEVY<span>ROOTS</span>` all-caps, no subtitle | ✗ |
| `guides/index.html` | **No** | Logo is `<em>Chevy</em>Roots`, no subtitle | ✗ |
| `guides/quiz.html` | **No** | No subtitle | ✗ |
| `guides/known-issues.html` | **No** | No subtitle | ✗ |
| `guides/small-block-chevy-history.html` | **No** | No subtitle | ✗ |
| `guides/c8-corvette-buyers-guide.html` | **No** | No subtitle | ✗ |
| `guides/america-250-chevy-road-trip.html` | **No** | No subtitle | ✗ |
| `newsletter/index.html` | Yes | **"Independent Chevrolet Resource"** | ✗ — wrong text |
| `partners/index.html` | Yes | **"Independent Chevrolet Resource"** | ✗ — wrong text |
| `crystals-corner/index.html` | Yes (in hero tagline, footer) | "Run by a Chevy Girl" | ✓ (partial — logo element doesn't show subtitle, but brand tagline is correct) |

**Summary:** Only `index.html` has the correct logo subtitle. 11 pages have no subtitle. 2 pages (`newsletter`, `partners`) have the wrong subtitle text.

---

## 4. Mobile Nav

| Page | Hamburger Present | Mobile Nav Has Crystal's Corner | Notes |
|------|------------------|--------------------------------|-------|
| `index.html` | ✓ (`nav-menu-toggle`) | ✓ | Also has "News" (broken link) |
| `models/index.html` | ✓ | **MISSING** | — |
| `events/index.html` | ✓ (`nav-hamburger`) | **MISSING** | No mobile nav drawer visible in markup |
| `about/index.html` | ✓ (`nav__hamburger`) | **MISSING** | JS-toggled list, no Crystal's Corner |
| `builds/index.html` | — | **MISSING** | Uses different nav — no mobile drawer found in markup |
| `guides/index.html` | ✓ (`nav-menu-toggle`) | **MISSING** | Mobile nav uses broken relative paths |
| `guides/quiz.html` | ✓ (`nav-hamburger`) | **MISSING** | — |
| `guides/known-issues.html` | ✓ (`nav-menu-toggle`) | **MISSING** | Mobile nav uses broken relative paths |
| `guides/small-block-chevy-history.html` | ✓ (`nav-hamburger`) | **MISSING** | — |
| `guides/c8-corvette-buyers-guide.html` | ✓ (`nav-hamburger`) | **MISSING** | — |
| `guides/america-250-chevy-road-trip.html` | ✓ (`nav-hamburger`) | **MISSING** | — |
| `newsletter/index.html` | ✓ (`nav-menu-toggle`) | **MISSING** | Mobile nav otherwise complete |
| `partners/index.html` | ✓ (`nav-menu-toggle`) | **MISSING** | Mobile nav otherwise complete |
| `crystals-corner/index.html` | ✓ (`nav__hamburger`, JS toggle) | ✓ | — |

**Note:** Three different hamburger class names are in use site-wide (`nav-menu-toggle`, `nav-hamburger`, `nav__hamburger`). This is inconsistent and indicates the nav was never templated — each page was built independently.

---

## 5. Footer Consistency

| Page | GM Non-Affiliation Disclaimer | Copyright Year | Notes |
|------|------------------------------|---------------|-------|
| `index.html` | ✓ (in footer-disclaimer) | 2026 | Correct |
| `models/index.html` | ✗ — **pricing disclaimer only**, no GM affiliation statement | 2026 | Missing GM disclaimer |
| `events/index.html` | ✗ — **No GM disclaimer** | 2026 | Footer says "Independent. Unaffiliated. Built for Chevy people." — passable but inconsistent |
| `about/index.html` | ✓ "Not affiliated with General Motors. Just in love with what they build." | Not shown in extracted text | Wording differs from standard disclaimer |
| `builds/index.html` | ✗ — **No GM disclaimer** | 2026 | Footer copy: "Built for the community by the community" — no affiliation notice |
| `guides/index.html` | ✓ "Not affiliated with General Motors" | **2025** ← wrong year | Copyright year is stale |
| `guides/quiz.html` | Not checked in footer | — | No footer disclaimer found in audit |
| `guides/known-issues.html` | ✓ "Not affiliated with General Motors" | **2025** ← wrong year | Copyright year is stale |
| `guides/small-block-chevy-history.html` | ✓ "Not affiliated with General Motors" | 2026 | Correct |
| `guides/c8-corvette-buyers-guide.html` | ✓ "Not affiliated with General Motors" | 2026 | Correct |
| `guides/america-250-chevy-road-trip.html` | ✓ "Not affiliated with General Motors" | 2026 | Correct |
| `newsletter/index.html` | ✓ | 2026 | Correct |
| `partners/index.html` | ✓ | 2026 | Correct |
| `crystals-corner/index.html` | — | 2026 | Has brand tagline but no explicit non-affiliation statement found |

**Issues:**
- `guides/index.html` and `guides/known-issues.html` show copyright © 2025 — stale.
- `builds/index.html` and `models/index.html` are missing the GM non-affiliation disclaimer entirely — a legal risk.
- Disclaimer wording varies across 5+ different formulations. Should be standardized to one canonical statement.

---

## 6. Placeholder Images

| Page | Placeholder Count | Notes |
|------|------------------|-------|
| `index.html` | 8 | Hero bg, 6 category cards, 1 quiz section |
| `models/index.html` | 0 | Uses `/photos/` local images and CSS text for classics — OK |
| `events/index.html` | 10 | Every event card has a text-label placeholder |
| `about/index.html` | 3 | — |
| `builds/index.html` | 0 (by class name) | Uses `[ build photo placeholder ]` text inside `build-card-img` divs — effectively placeholders |
| `guides/index.html` | 0 | — |
| `guides/quiz.html` | 4 | Result cards use `result-img-placeholder` |
| All other guide pages | 0 | — |
| `newsletter/index.html` | 0 | — |
| `partners/index.html` | 0 | — |
| `crystals-corner/index.html` | 0 | — |

**No Unsplash or external image URLs were found.** All images either use local `/photos/` paths or CSS placeholder divs. This is correct behavior.

**However:** The `models/index.html` references several local photos that should be verified for existence (e.g., `/photos/silverado/pexels_12624306_silverado.jpeg`, `/photos/tahoe/pexels_35004984_tahoe.jpeg`). These were not confirmed present in the audit.

---

## 7. Fake / Inflated Stats

No obviously fake community membership stats ("12K members", "3,400 builds") were found. The stats present are:

- **`index.html` hero:** "115 Years of Chevy" and "2026 America 250" — factual/contextual, acceptable.
- **`builds/index.html` hero:** "6 Builds Live", "$141K Total Documented", "5+ Decades Covered", "0 Other Sites Like This" — low and honest for a new site. Acceptable.
- **`builds/index.html` build cards:** Explicitly labeled `[ build photo placeholder ]` and cost estimates with `*Placeholder estimates` disclaimer. Good.
- **`events/index.html`:** Event descriptions cite "3,000 vehicles", "6,000 cars" etc. for real-world events — these are third-party event stats, not site community stats. Acceptable if accurate, but should be sourced.

**No fake community stats found.** This check passes.

---

## 8. Data Accuracy — Vehicle Specs vs. `vehicles.json`

`vehicles.json` contains authoritative data for 10 models. Comparing against `pages/models/index.html` and `pages/guides/quiz.html`:

| Vehicle | Page Claims | vehicles.json Says | Discrepancy? |
|---------|------------|-------------------|-------------|
| Silverado 1500 MSRP | From $38,200 | From $37,200 (2025) / $36,400 (2024) | **YES — overstated** |
| Silverado 1500 max tow | "Tows up to 13,300 lbs" | 13,300 lbs | ✓ Matches |
| Colorado MSRP | From $30,100 | From $31,995 (2025) / $30,995 (2024) | **YES — understated** |
| Tahoe MSRP | From $56,200 | From $58,500 (2025) / $57,800 (2024) | **YES — understated by ~$2K** |
| Tahoe tow | 8,400 lbs | 8,400 lbs | ✓ Matches |
| Suburban MSRP | From $60,100 | From $62,500 (2025) / $61,700 (2024) | **YES — understated by ~$2.4K** |
| Traverse MSRP | From $35,400 | From $38,995 (2025) / $37,995 (2024) | **YES — understated by ~$3.6K** |
| Equinox MSRP | From $30,100 | From $33,000 (2025) / $31,900 (2024) | **YES — understated by ~$2.9K** |
| Trax MSRP | From $21,500 | From $21,000 (2025) / $20,400 (2024) | **YES — overstated slightly** |
| Corvette Stingray MSRP | From $66,300 | From $71,995 (2025) / $69,995 (2024) | **YES — understated by ~$5.7K** |
| Camaro MSRP | From $27,400 | From $29,995 (2024) | **YES — understated by ~$2.6K** |
| Tahoe (quiz.html) | "355 HP V8 (base)" | Not checked in vehicles.json | 355 HP matches the 5.3L V8's rated output — plausible |
| Suburban (quiz.html) | "355 HP V8" | Not checked | Plausible — same engine family |

**Summary:** Every MSRP on the Models page is wrong. They appear to be early estimates or outdated figures. With vehicles.json as the source of truth, all 10 model MSRPs shown on `models/index.html` are inaccurate. The page needs to either pull from `vehicles.json` dynamically or be updated manually. The towing numbers checked are correct.

---

## 9. JavaScript Files

| JS File | Exists on Disk? | Referenced By | Status |
|---------|----------------|--------------|--------|
| `/js/newsletter.js` | ✓ Yes | `pages/newsletter/index.html` | OK |
| `/js/affiliate.js` | ✓ Yes | **Not referenced by any HTML page** | Orphaned — never loaded |

**`affiliate.js` is an orphan.** It exists in `/js/` but no HTML page includes it via a `<script src>` tag. If this script is meant to track affiliate links across the site, it is currently doing nothing.

**No broken JS references.** `newsletter.js` is the only JS file referenced in HTML, and it exists.

---

## 10. CSS / External Resource Dependencies

All pages load fonts from **Google Fonts**:
```
https://fonts.googleapis.com/css2?family=Barlow+Condensed...&family=Inter...&family=JetBrains+Mono...
```

This is an external dependency. If Google Fonts is unavailable (offline dev, network issues, Google outage), the site will fall back to system fonts and lose its designed appearance. All CSS is otherwise inline per-page — there are no external CSS file references that could break.

**Minor inconsistency:** `models/index.html` and several other pages load `Barlow+Condensed` without the italic variant (`ital,wght@...`), while `index.html` loads it with italic weights. This means the italic logo styling (`<em>Roots</em>`) on `index.html` may not render correctly on pages that don't load the italic font variant.

---

## Prioritized Fix List

### P0 — Legal / Credibility Risk (Fix before any public launch)

1. **Add GM non-affiliation disclaimer** to `builds/index.html` and `models/index.html` footers. These are the two highest-traffic pages and both are missing it entirely. This is a legal exposure issue.
2. **Fix all MSRP data** on `models/index.html`. Every single price is wrong versus `vehicles.json`. Understating prices by thousands is misleading to users.

### P1 — Critical UX / Broken Navigation (Fix immediately)

3. **Add Crystal's Corner to the nav on all 12 pages** that are missing it. This is the site owner's signature section and it's invisible from most of the site.
4. **Fix `builds/index.html` nav** — it has a completely different architecture (VIN Registry, Community, Parts) that doesn't match the rest of the site and links entirely to non-existent pages. Replace with the standard nav.
5. **Fix `/pages/news/`** — it has an empty directory and is linked in `index.html` desktop and mobile nav. Either create an `index.html` or remove "News" from the nav everywhere.
6. **Fix relative paths in `guides/index.html` and `guides/known-issues.html`** — the `../../about/` path resolves to `/about/` which doesn't exist. Replace all relative hrefs with absolute paths.

### P2 — High Priority UX (Fix before soft launch)

7. **Add logo subtitle "Run by a Chevy Girl"** to all pages. Currently only `index.html` has it. `newsletter/index.html` and `partners/index.html` have the wrong subtitle text.
8. **Fix `pages/privacy/` and `pages/terms/`** — these are linked in footers across almost every page and don't exist. Create stub pages or at minimum redirect them.
9. **Create `/pages/guides/whats-your-chevy/`** — this quiz entry point is linked from `index.html` twice (hero CTA + footer). The quiz itself exists at `/pages/guides/quiz.html` but the linked path does not. Either create a redirect or fix the href.
10. **Remove or hide all broken "View Guide →" links** on `models/index.html` until those pages are built. Currently 20+ guide links go to 404s.

### P3 — Medium Priority (Fix within first week of launch)

11. **Standardize the GM disclaimer wording** across all pages to one canonical statement.
12. **Fix copyright year** in `guides/index.html` and `guides/known-issues.html` — both say © 2025, should be © 2026.
13. **Wire up `affiliate.js`** — include it via `<script src="/js/affiliate.js">` on pages where affiliate link tracking is needed, or delete the file if it's not being used.
14. **Add About link to `guides/quiz.html`** nav — it's the only page missing it.
15. **Standardize hamburger button class names** — three different class names (`nav-menu-toggle`, `nav-hamburger`, `nav__hamburger`) are in use across the site. Pick one and normalize.
16. **Add Guides link to `about/index.html`** nav — currently missing.

### P4 — Low Priority / Polish

17. **Replace placeholder divs on `index.html`** (8 instances) and `events/index.html` (10 instances) with real photos.
18. **Add subtitle italic font variant** consistently — ensure all pages load `Barlow+Condensed` with the italic weight if they use italic styling in the logo.
19. **Verify local photo file existence** for `models/index.html` background-image references (e.g., `/photos/silverado/pexels_12624306_silverado.jpeg`).
20. **All event "Details →" links** on `events/index.html` point to `#` — replace with real event URLs or remove the links until available.
21. **Index.html "News" nav link** — if "News" is not an intended nav section per the site brief, remove it from both the desktop and mobile navs on `index.html`.

---

## Files Audited

```
index.html
pages/models/index.html
pages/models/template.html
pages/models/generate-static.html
pages/events/index.html
pages/about/index.html
pages/builds/index.html
pages/guides/index.html
pages/guides/quiz.html
pages/guides/known-issues.html
pages/guides/small-block-chevy-history.html
pages/guides/c8-corvette-buyers-guide.html
pages/guides/america-250-chevy-road-trip.html
pages/newsletter/index.html
pages/partners/index.html
pages/crystals-corner/index.html
```

## Supporting Data Files Checked

```
data/vehicles.json  (10 vehicles, 2024–2025 data)
js/newsletter.js    (exists)
js/affiliate.js     (exists, orphaned)
```
