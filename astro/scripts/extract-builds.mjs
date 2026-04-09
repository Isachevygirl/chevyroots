#!/usr/bin/env node
// Extract the 12 community builds + Build of the Month from the old
// pages/builds/index.html into a structured JSON file that the new
// Astro builds page can render from. Preserves every data point from
// the original.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SRC = path.resolve(__dirname, '../../pages/builds/index.html');
const OUT = path.resolve(__dirname, '../src/data/builds.json');

const html = fs.readFileSync(SRC, 'utf8');

function decodeEntities(s) {
  return s
    .replace(/&amp;/g, '&')
    .replace(/&mdash;/g, '—')
    .replace(/&ndash;/g, '–')
    .replace(/&rsquo;/g, '\u2019')
    .replace(/&lsquo;/g, '\u2018')
    .replace(/&rdquo;/g, '\u201d')
    .replace(/&ldquo;/g, '\u201c')
    .replace(/&rarr;/g, '→')
    .replace(/&nbsp;/g, ' ')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function strip(s) {
  return decodeEntities((s || '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim());
}

function extractFirst(re, text) {
  const m = re.exec(text);
  return m ? m[1] : '';
}

// ── Extract the Build of the Month ────────────────────────────────────────────
function extractBotm(html) {
  const sectionMatch = /<section class="botm-section"[\s\S]*?<\/section>/.exec(html);
  if (!sectionMatch) return null;
  const s = sectionMatch[0];

  return {
    month: strip(extractFirst(/<span class="section-label mono"[^>]*>([^<]*)<\/span>/, s)),
    image: extractFirst(/<img src="([^"]+)"/, s),
    eyebrow: strip(extractFirst(/<div class="botm-eyebrow">([^<]*)<\/div>/, s)),
    title: strip(extractFirst(/<h2 class="botm-title[^"]*"[^>]*>([^<]*)<\/h2>/, s)),
    subtitle: strip(extractFirst(/<p class="botm-subtitle">([^<]*)<\/p>/, s)),
    owner: strip(extractFirst(/<div class="botm-avatar">([^<]*)<\/div>/, s)),
    handle: strip(extractFirst(/<div class="botm-owner-name">([^<]*)<\/div>/, s)),
    location: strip(extractFirst(/<div class="botm-owner-loc">([^<]*)<\/div>/, s)),
    stats: Array.from(s.matchAll(/<div class="botm-stat">\s*<span class="botm-stat-val">([^<]*)<\/span>\s*<span class="botm-stat-lbl">([^<]*)<\/span>/g))
      .map((m) => ({ value: strip(m[1]), label: strip(m[2]) })),
    keyMods: Array.from(s.matchAll(/<div class="botm-mod">([^<]*)<\/div>/g))
      .map((m) => strip(m[1])),
  };
}

// ── Extract the 12 build cards ────────────────────────────────────────────────
function extractBuildCards(html) {
  const builds = [];
  // Each build is wrapped in <article class="build-card" ...> ... </article>
  const cardRe = /<article class="build-card"[\s\S]*?<\/article>/g;
  const cards = html.match(cardRe) || [];

  for (const card of cards) {
    const build = {
      model: strip(extractFirst(/data-model="([^"]*)"/, card)),
      year: strip(extractFirst(/data-year="([^"]*)"/, card)),
      yearRange: strip(extractFirst(/data-year-range="([^"]*)"/, card)),
      type: strip(extractFirst(/data-type="([^"]*)"/, card)),
      budget: strip(extractFirst(/data-budget="([^"]*)"/, card)),
      search: strip(extractFirst(/data-search="([^"]*)"/, card)),
      image: extractFirst(/background-image: url\('([^']+)'\)/, card),
      stageText: strip(extractFirst(/<div class="build-card-stage-badge">([^<]*)<\/div>/, card)),
      vehicle: strip(extractFirst(/<h3 class="build-card-vehicle[^"]*"[^>]*>([^<]*)<\/h3>/, card)),
      subtitle: strip(extractFirst(/<p class="build-card-subtitle">([^<]*)<\/p>/, card)),
      avatar: strip(extractFirst(/<div class="build-card-avatar">([^<]*)<\/div>/, card)),
      handle: strip(extractFirst(/<div class="build-card-handle">([^<]*)<\/div>/, card)),
      location: strip(extractFirst(/<div class="build-card-location">([^<]*)<\/div>/, card)),
      stats: Array.from(card.matchAll(/<div class="build-stat">\s*<span class="build-stat-value">([^<]*)<\/span>\s*<span class="build-stat-label">([^<]*)<\/span>/g))
        .map((m) => ({ value: strip(m[1]), label: strip(m[2]) })),
      tags: Array.from(card.matchAll(/<span class="tag tag-(\w+)">([^<]*)<\/span>/g))
        .map((m) => ({ color: m[1], label: strip(m[2]) })),
      progressPct: strip(extractFirst(/<span class="build-progress-pct mono">(\d+)%<\/span>/, card)),
      modsCount: strip(extractFirst(/<span class="build-card-cta-mods mono">(\d+)\s*mods documented<\/span>/, card)),
    };
    if (build.vehicle) builds.push(build);
  }
  return builds;
}

// ── Popular mods list ─────────────────────────────────────────────────────────
function extractPopularMods(html) {
  const sectionMatch = /<section class="popular-mods-section"[\s\S]*?<\/section>/.exec(html);
  if (!sectionMatch) return [];
  const s = sectionMatch[0];
  const items = [];
  const rowRe = /<div class="popular-mod-row">([\s\S]*?)<\/div>\s*<\/div>/g;
  let m;
  while ((m = rowRe.exec(s)) !== null) {
    const row = m[1];
    const title = strip(extractFirst(/<div class="popular-mod-title[^"]*"[^>]*>([^<]*)<\/div>/, row));
    if (title) items.push({ title });
  }
  return items;
}

// ── Run ───────────────────────────────────────────────────────────────────────
const output = {
  botm: extractBotm(html),
  builds: extractBuildCards(html),
  popularMods: extractPopularMods(html),
};

fs.writeFileSync(OUT, JSON.stringify(output, null, 2));
console.log(`Extracted: ${output.builds.length} builds, BOTM: ${output.botm?.title || 'not found'}`);
console.log(`Popular mods: ${output.popularMods.length}`);
console.log(`Output: ${OUT}`);
