// Astro content collections — single source of truth for every piece of content
// that needs a stable schema. Adding a new field? Edit here; TypeScript catches
// every page that uses it.

import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// ── GUIDES ─────────────────────────────────────────────────────────────────────
const guides = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/guides' }),
  schema: z.object({
    title: z.string().max(120),
    description: z.string().min(40).max(260),
    author: z.string().default('Crystal'),
    published: z.coerce.date(),
    updated: z.coerce.date().optional(),
    eyebrow: z.string().default("Buyer's Guide"),
    cluster: z.enum([
      'Silverado Buyer Funnel',
      'Affiliate Density',
      'EV Cluster',
      'Performance & Classic',
      'Insurance & Ownership',
      'Lifestyle & Culture',
      'History',
      'Maintenance',
      'My ZR2',
      'Comparison',
      'Other',
    ]).default('Other'),
    heroImage: z.string().optional(),
    heroAlt: z.string().optional(),
    readingTime: z.number().int().positive().optional(),
    hasAffiliates: z.boolean().default(true),
    affiliateRetailers: z.array(z.string()).default([]),
    related: z.array(z.string()).default([]),
    tags: z.array(z.string()).default([]),
    featured: z.boolean().default(false),
    revenuePriority: z.number().int().min(0).max(100).default(0),
    noindex: z.boolean().default(false),
  }),
});

// ── CRYSTAL'S CORNER ───────────────────────────────────────────────────────────
const crystalsCorner = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/crystals-corner' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    published: z.coerce.date(),
    excerpt: z.string().optional(),
    heroImage: z.string().optional(),
    tags: z.array(z.string()).default([]),
  }),
});

// ── EVENT REPORTS ──────────────────────────────────────────────────────────────
const eventReports = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/event-reports' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    eventDate: z.coerce.date(),
    published: z.coerce.date(),
    location: z.object({
      city: z.string(),
      state: z.string(),
      venue: z.string().optional(),
    }),
    heroImage: z.string().optional(),
    gallery: z.array(z.string()).default([]),
    videoEmbed: z.string().optional(),
    relatedBuilds: z.array(z.string()).default([]),
  }),
});

export const collections = {
  guides,
  'crystals-corner': crystalsCorner,
  'event-reports': eventReports,
};
