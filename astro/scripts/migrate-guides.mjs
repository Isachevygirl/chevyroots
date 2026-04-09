#!/usr/bin/env node
// HTML → MDX converter for ChevyRoots guides.
//
// Reads every .html file in ../../pages/guides/, extracts the <article class="article-body">
// body, converts inline component patterns (tip-box / warning-box / crystal-take /
// affiliate-box / inline-img) into the Astro components already defined, and writes
// the result to ../src/content/guides/{slug}.mdx with a full frontmatter block.
//
// Usage: node scripts/migrate-guides.mjs

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SRC_DIR = path.resolve(__dirname, '../../pages/guides');
const OUT_DIR = path.resolve(__dirname, '../src/content/guides');

// ── CLUSTER MAP ────────────────────────────────────────────────────────────────
// Maps each slug to the cluster the content-pipeline-SUMMARY decided it belongs to.
// Any slug not listed defaults to "Other".
const CLUSTERS = {
  'chevy-extended-warranty': 'Silverado Buyer Funnel',
  'chevy-dealer-negotiation': 'Silverado Buyer Funnel',
  'silverado-buyers-guide': 'Silverado Buyer Funnel',
  'used-chevy-truck-guide': 'Silverado Buyer Funnel',
  'silverado-vs-ram': 'Comparison',
  'silverado-5.3-vs-6.2': 'Silverado Buyer Funnel',
  'buying-truck-as-woman': 'Silverado Buyer Funnel',
  'best-mods-silverado': 'Affiliate Density',
  'best-cold-air-intake-silverado': 'Affiliate Density',
  'best-exhaust-silverado': 'Affiliate Density',
  'best-tonneau-covers-silverado': 'Affiliate Density',
  'chevy-towing-guide': 'Affiliate Density',
  'silverado-oil-change-guide': 'Maintenance',
  'chevy-maintenance-schedule': 'Maintenance',
  'silverado-transmission-shudder-fix': 'Maintenance',
  'c8-corvette-buyers-guide': 'Performance & Classic',
  'c8-corvette-best-year-to-buy': 'Performance & Classic',
  'small-block-chevy-history': 'Performance & Classic',
  'ls-swap-guide': 'Performance & Classic',
  'classic-chevy-insurance': 'Insurance & Ownership',
  'chevy-history': 'History',
  'chevy-impala-cultural-history': 'History',
  'chevy-vintage-ads': 'History',
  'chevy-rpo-codes': 'History',
  'gm-military-discount': 'Insurance & Ownership',
  'section-179-chevy': 'Insurance & Ownership',
  'chevy-dream-tour': 'Lifestyle & Culture',
  'america-250-chevy-road-trip': 'Lifestyle & Culture',
  'chevy-mlb-partnership': 'Lifestyle & Culture',
  'tahoe-vs-suburban': 'Comparison',
};

// ── REVENUE PRIORITY ───────────────────────────────────────────────────────────
// Top 5 revenue articles from content-pipeline-SUMMARY.md
const REVENUE_PRIORITY = {
  'chevy-extended-warranty': 100,
  'chevy-dealer-negotiation': 95,
  'silverado-lease-deals-2026': 90,
  'gm-employee-discount-explained': 85,
  'how-to-find-best-chevy-dealer-near-me': 80,
  'silverado-buyers-guide': 75,
  'classic-chevy-insurance': 70,
  'used-chevy-truck-guide': 65,
};

// ── UTILITIES ──────────────────────────────────────────────────────────────────

function slugFromFilename(filename) {
  return filename.replace(/\.html$/i, '');
}

function stripHtmlTags(html) {
  return html.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
}

function decodeEntities(s) {
  return s
    .replace(/&mdash;/g, '—')
    .replace(/&ndash;/g, '–')
    .replace(/&rsquo;/g, '\u2019')
    .replace(/&lsquo;/g, '\u2018')
    .replace(/&rdquo;/g, '\u201d')
    .replace(/&ldquo;/g, '\u201c')
    .replace(/&hellip;/g, '…')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ')
    .replace(/&#8217;/g, '\u2019')
    .replace(/&#8216;/g, '\u2018')
    .replace(/&#x27;/g, "'");
}

function extract(re, s) {
  const m = re.exec(s);
  return m ? m[1].trim() : null;
}

function yamlEscape(value) {
  if (value == null) return '';
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  const str = String(value);
  if (/[:#@\[\]{}&*!|>'"%`,?-]/.test(str) || str.length > 100) {
    return `"${str.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`;
  }
  return str;
}

// Rough word-count reading time (200 wpm)
function readingTime(html) {
  const words = stripHtmlTags(html).split(/\s+/).filter(Boolean).length;
  return Math.max(2, Math.round(words / 200));
}

// ── COMPONENT REPLACEMENTS ─────────────────────────────────────────────────────

// These regex operate on the raw article body HTML. Order matters — compound
// components (with nested labels) must run before simpler text-level replacements.

function convertTipBox(body) {
  return body.replace(
    /<div class="tip-box">\s*<div class="tip-label">([^<]*)<\/div>\s*([\s\S]*?)<\/div>/g,
    (_m, label, inner) => {
      const cleanLabel = decodeEntities(label).trim();
      const labelAttr = cleanLabel && cleanLabel !== 'Pro Tip' ? ` label="${cleanLabel}"` : '';
      return `\n\n<TipBox${labelAttr}>\n${inner.trim()}\n</TipBox>\n\n`;
    }
  );
}

function convertWarningBox(body) {
  return body.replace(
    /<div class="warning-box">\s*<div class="warning-label">([^<]*)<\/div>\s*([\s\S]*?)<\/div>/g,
    (_m, label, inner) => {
      const cleanLabel = decodeEntities(label).trim();
      const labelAttr = cleanLabel && cleanLabel !== 'Watch Out' ? ` label="${cleanLabel}"` : '';
      return `\n\n<WarningBox${labelAttr}>\n${inner.trim()}\n</WarningBox>\n\n`;
    }
  );
}

function convertCrystalTake(body) {
  return body.replace(
    /<div class="crystal-take">\s*<div class="crystal-take-header">[^<]*<\/div>\s*([\s\S]*?)<\/div>/g,
    (_m, inner) => {
      return `\n\n<CrystalTake>\n${inner.trim()}\n</CrystalTake>\n\n`;
    }
  );
}

function convertAffiliateBox(body) {
  return body.replace(
    /<div class="affiliate-box">\s*<div class="affiliate-box-icon">([^<]*)<\/div>\s*<div class="affiliate-box-text">\s*<strong>([^<]*)<\/strong>\s*([\s\S]*?)<\/div>\s*<a[^>]*href="([^"]*)"[^>]*>([^<]*)<\/a>\s*<\/div>/g,
    (_m, icon, product, description, url, cta) => {
      // Derive a retailer/slug from url or title
      const cleanProduct = decodeEntities(product).trim();
      const cleanDesc = decodeEntities(stripHtmlTags(description));
      const cleanCta = decodeEntities(cta).trim();
      const cleanIcon = decodeEntities(icon).trim();
      const slugGuess = cleanProduct.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
      return `\n\n<AffiliateBox\n  retailer="partner"\n  slug="${slugGuess}"\n  product={"${cleanProduct.replace(/"/g, '\\"')}"}\n  description={"${cleanDesc.replace(/"/g, '\\"')}"}\n  cta={"${cleanCta.replace(/"/g, '\\"')}"}\n  icon={"${cleanIcon}"}\n/>\n\n`;
    }
  );
}

function convertInlineImg(body) {
  return body.replace(
    /<div class="inline-img" style="background:[^"]*url\('([^']+)'\)[^"]*"[^>]*><\/div>/g,
    (_m, src) => {
      return `\n\n<figure class="inline-fig">\n  <img src="${src}" alt="" loading="lazy" />\n</figure>\n\n`;
    }
  );
}

function convertPullquote(body) {
  return body.replace(
    /<blockquote[^>]*class="pullquote"[^>]*>([\s\S]*?)<\/blockquote>/g,
    (_m, inner) => {
      const text = stripHtmlTags(inner).trim();
      return `\n\n<Pullquote>${text}</Pullquote>\n\n`;
    }
  );
}

// Convert <a href="/pages/guides/foo.html"> to <a href="/guides/foo/">
function rewriteInternalLinks(body) {
  return body
    .replace(/href="\/pages\/guides\/([a-z0-9-]+)\.html"/g, 'href="/guides/$1/"')
    .replace(/href="\/pages\/guides\/"/g, 'href="/guides/"')
    .replace(/href="\/pages\/models\/([a-z0-9-]+)\.html"/g, 'href="/models/$1/"')
    .replace(/href="\/pages\/models\/"/g, 'href="/models/"')
    .replace(/href="\/pages\/events\/"/g, 'href="/events/"')
    .replace(/href="\/pages\/mechanics\/"/g, 'href="/mechanics/"')
    .replace(/href="\/pages\/news\/"/g, 'href="/news/"')
    .replace(/href="\/pages\/about\/"/g, 'href="/about/"')
    .replace(/href="\/pages\/crystals-corner\/"/g, 'href="/crystals-corner/"')
    .replace(/href="\/pages\/([a-z0-9-]+)\/"/g, 'href="/$1/"');
}

// Replace class attributes that are now handled by the layout
function stripInlineClasses(body) {
  return body
    .replace(/ class="coverage-table"/g, '')
    .replace(/ class="article-body"/g, '');
}

// MDX does not allow bare braces in text; escape any curly braces we find.
function escapeCurlyBraces(body) {
  return body.replace(/\{/g, '\u007b'); // literal { — safe in MDX if we don't intend JSX
}

// Collapse leading + trailing whitespace on each line while keeping blank lines between blocks
function cleanBodyWhitespace(body) {
  return body
    .split('\n')
    .map((line) => line.replace(/[\t ]+$/g, ''))
    .join('\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

// ── HEADER EXTRACTION ──────────────────────────────────────────────────────────

function extractMetadata(html, slug) {
  // Title: <h1 class="article-title">...</h1>  — may include <span>
  const titleRaw = extract(/<h1 class="article-title">([\s\S]*?)<\/h1>/i, html);
  const title = titleRaw ? decodeEntities(stripHtmlTags(titleRaw)) : slugToTitle(slug);

  // Eyebrow: <div class="article-eyebrow">...</div>
  const eyebrowRaw = extract(/<div class="article-eyebrow">([\s\S]*?)<\/div>/i, html);
  const eyebrow = eyebrowRaw
    ? decodeEntities(stripHtmlTags(eyebrowRaw)).replace(/\s*\/\s*/g, ' · ')
    : "Buyer's Guide";

  // Description: <meta name="description" content="...">
  const description =
    extract(/<meta name="description" content="([^"]*)"/, html) ||
    `${title}. Independent review and buyer's guide from Crystal and the ChevyRoots team.`;

  // Hero image: background image inside .article-hero-img
  const heroMatch = /class="article-hero-img"[^>]*background:[^"]*url\('([^']+)'\)/.exec(html);
  const heroImage = heroMatch ? heroMatch[1] : undefined;

  // Updated date: <div class="article-meta-item"><span class="dot"></span>Updated April 2026</div>
  const updatedMatch = /Updated\s+([A-Z][a-z]+\s+\d{4})/.exec(html);
  const updated = updatedMatch ? parseHumanDate(updatedMatch[1]) : null;

  // Read time: "7 min read"
  const rtMatch = /(\d+)\s*min read/i.exec(html);
  const rt = rtMatch ? parseInt(rtMatch[1], 10) : null;

  return { title, eyebrow, description, heroImage, updated, rt };
}

function slugToTitle(slug) {
  return slug
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

function parseHumanDate(str) {
  const d = new Date(`${str} 01`);
  if (isNaN(d.getTime())) return null;
  return d.toISOString().slice(0, 10);
}

// ── MAIN CONVERSION ────────────────────────────────────────────────────────────

function extractArticleBody(html) {
  // Pattern 1: <article class="article-body"...>...</article>
  let m = /<article[^>]*class="[^"]*article-body[^"]*"[^>]*>([\s\S]*?)<\/article>/.exec(html);
  if (m) return m[1];

  // Pattern 2: <main class="article-body"...>...</main>
  m = /<main[^>]*class="[^"]*article-body[^"]*"[^>]*>([\s\S]*?)<\/main>/.exec(html);
  if (m) return m[1];

  // Pattern 3: <section class="article-body"...>...</section>
  m = /<section[^>]*class="[^"]*article-body[^"]*"[^>]*>([\s\S]*?)<\/section>/.exec(html);
  if (m) return m[1];

  // Pattern 4: <div class="article-body"...>...</div> up to aside or closing layout
  m = /<div[^>]*class="[^"]*article-body[^"]*"[^>]*>([\s\S]*?)<\/div>\s*(?=<aside)/.exec(html);
  if (m) return m[1];

  // Pattern 5: Generic <main>...</main> with sidebar stripped
  m = /<main[^>]*>([\s\S]*?)<\/main>/.exec(html);
  if (m) {
    return m[1]
      .replace(/<header[\s\S]*?<\/header>/g, '')
      .replace(/<aside[\s\S]*?<\/aside>/g, '')
      .replace(/<nav[\s\S]*?<\/nav>/g, '');
  }

  return null;
}

function stripHtmlComments(body) {
  return body.replace(/<!--[\s\S]*?-->/g, '');
}

function selfCloseVoidTags(body) {
  // MDX requires void elements to self-close. Convert <br> → <br />, <hr> → <hr />, <img ...> → <img ... />
  return body
    .replace(/<br\s*>/gi, '<br />')
    .replace(/<hr\s*>/gi, '<hr />')
    // img with no closing: match <img ...> not already self-closed
    .replace(/<img\b([^>]*?)(?<!\/)>/gi, '<img$1 />')
    // input and other void elements
    .replace(/<input\b([^>]*?)(?<!\/)>/gi, '<input$1 />')
    .replace(/<meta\b([^>]*?)(?<!\/)>/gi, '<meta$1 />')
    .replace(/<link\b([^>]*?)(?<!\/)>/gi, '<link$1 />');
}

function stripScriptsAndStyles(body) {
  return body
    .replace(/<script[\s\S]*?<\/script>/g, '')
    .replace(/<style[\s\S]*?<\/style>/g, '')
    .replace(/<noscript[\s\S]*?<\/noscript>/g, '');
}

function stripDataAndOnAttrs(body) {
  // Remove onclick= and onmouseover= etc. since they break MDX parsing
  return body.replace(/ on[a-z]+="[^"]*"/gi, '');
}

function escapeMarkdownChars(body) {
  // Inside HTML text content, MDX/remark still interprets markdown-hot characters.
  // `~` is the nastiest because `~text~` is strikethrough. Replace with entity.
  // We escape the tilde everywhere — it's very rare in English and will never matter.
  return body.replace(/~/g, '&#126;');
}

function escapeMdxBraces(body) {
  // Braces inside HTML text content break MDX parsing. Escape bare { that aren't already
  // inside a JSX component attribute.
  // Simple heuristic: replace { with &lbrace; when it's not followed by a JSX-like attribute.
  return body.replace(/([^={])\{([^}]*)\}/g, (match, before, inner) => {
    // Leave untouched if inside a JSX attribute or self-closing tag
    if (before === '=' || before === '{') return match;
    return `${before}&#123;${inner}&#125;`;
  });
}

function removeLegacyIds(body) {
  // <h2 id="foo"> → <h2>  (kept as anchor targets via remark-slug later if needed)
  // Actually keep ids for TOC anchors — they're valid HTML
  return body;
}

function convertBody(raw) {
  let body = raw;
  // Strip HTML comments BEFORE other conversions — they break MDX
  body = stripHtmlComments(body);
  body = stripScriptsAndStyles(body);
  body = stripDataAndOnAttrs(body);
  body = escapeMarkdownChars(body);
  body = selfCloseVoidTags(body);
  // Component conversions (order-sensitive)
  body = convertTipBox(body);
  body = convertWarningBox(body);
  body = convertCrystalTake(body);
  body = convertAffiliateBox(body);
  body = convertPullquote(body);
  body = convertInlineImg(body);
  body = stripInlineClasses(body);
  body = rewriteInternalLinks(body);
  // NOTE: don't escape braces — our guides don't use raw {} in content, and
  // doing it eagerly would mangle component props
  body = cleanBodyWhitespace(body);
  return body;
}

function buildFrontmatter({ slug, title, description, eyebrow, cluster, published, updated, heroImage, rt, revenuePriority }) {
  const lines = ['---'];
  lines.push(`title: ${yamlEscape(title)}`);
  lines.push(`description: ${yamlEscape(description)}`);
  lines.push(`published: ${published}`);
  if (updated) lines.push(`updated: ${updated}`);
  if (eyebrow) lines.push(`eyebrow: ${yamlEscape(eyebrow)}`);
  lines.push(`cluster: ${yamlEscape(cluster)}`);
  if (heroImage) lines.push(`heroImage: ${yamlEscape(heroImage)}`);
  if (rt) lines.push(`readingTime: ${rt}`);
  if (revenuePriority) lines.push(`revenuePriority: ${revenuePriority}`);
  if (revenuePriority && revenuePriority >= 75) lines.push(`featured: true`);
  lines.push('hasAffiliates: true');
  lines.push('---');
  return lines.join('\n');
}

function buildMdx({ frontmatter, imports, body }) {
  return `${frontmatter}\n\n${imports}\n\n${body}\n`;
}

// ── IMPORTS for MDX ────────────────────────────────────────────────────────────

const COMPONENT_IMPORTS = `import TipBox from '@components/TipBox.astro';
import WarningBox from '@components/WarningBox.astro';
import CrystalTake from '@components/CrystalTake.astro';
import AffiliateBox from '@components/AffiliateBox.astro';
import AffiliateLink from '@components/AffiliateLink.astro';
import Pullquote from '@components/Pullquote.astro';`;

// ── RUN ────────────────────────────────────────────────────────────────────────

function main() {
  if (!fs.existsSync(SRC_DIR)) {
    console.error(`Source dir not found: ${SRC_DIR}`);
    process.exit(1);
  }
  if (!fs.existsSync(OUT_DIR)) {
    fs.mkdirSync(OUT_DIR, { recursive: true });
  }

  const files = fs
    .readdirSync(SRC_DIR)
    .filter((f) => f.endsWith('.html'))
    // Skip tool/hub pages that aren't articles
    .filter((f) => !['index.html', 'quiz.html', 'known-issues.html', 'compare.html'].includes(f));

  console.log(`Found ${files.length} guide HTML files to migrate`);
  let success = 0;
  let failed = 0;

  for (const file of files) {
    const slug = slugFromFilename(file);
    try {
      const html = fs.readFileSync(path.join(SRC_DIR, file), 'utf8');
      const bodyRaw = extractArticleBody(html);
      if (!bodyRaw) {
        console.warn(`⚠  ${slug}: no <article class="article-body"> found — skipping`);
        failed++;
        continue;
      }
      const meta = extractMetadata(html, slug);
      const body = convertBody(bodyRaw);
      const cluster = CLUSTERS[slug] || 'Other';
      const revenuePriority = REVENUE_PRIORITY[slug] || 0;
      const frontmatter = buildFrontmatter({
        slug,
        title: meta.title,
        description: meta.description,
        eyebrow: meta.eyebrow,
        cluster,
        published: meta.updated || '2026-04-01',
        updated: meta.updated,
        heroImage: meta.heroImage,
        rt: meta.rt || readingTime(bodyRaw),
        revenuePriority,
      });
      const mdx = buildMdx({ frontmatter, imports: COMPONENT_IMPORTS, body });
      fs.writeFileSync(path.join(OUT_DIR, `${slug}.mdx`), mdx, 'utf8');
      console.log(`✓ ${slug}`);
      success++;
    } catch (err) {
      console.error(`✗ ${slug}: ${err.message}`);
      failed++;
    }
  }

  console.log(`\nDone. ${success} migrated, ${failed} failed.`);
}

main();
