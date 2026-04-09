// Typed data loaders for the JSON files in src/data/. Keeps page components
// clean and gives us a single place to add validation/caching later.

import vehiclesJson from '../data/vehicles.json';
import knownIssuesJson from '../data/known-issues.json';
import mechanicsJson from '../data/mechanics.json';
import newsJson from '../data/news_articles.json';
import vintageAdsJson from '../data/vintage-ads.json';
import vintageAdsImagesJson from '../data/vintage-ads-images.json';
import southwestEventsJson from '../data/southwest-events-2026-2027.json';
import northeastEventsJson from '../data/northeast-chevy-events-2026-2027.json';
import midwestEventsJson from '../data/midwest_chevy_events_2026_2027.json';

// ── VEHICLES ──────────────────────────────────────────────────────────────────
export interface Trim {
  name: string;
  msrp: number;
  engine?: string;
  hp?: number;
  torque?: number;
  transmission?: string;
  drivetrain?: string;
  towing_capacity?: number;
  mpg_city?: number;
  mpg_highway?: number;
  key_features?: string[];
}

export interface VehicleYear {
  year: number;
  starting_msrp: number;
  trims: Trim[];
}

export interface Vehicle {
  model: string;
  slug: string;
  category: string;
  years: VehicleYear[];
  hero_image?: string;
  description?: string;
  generations?: Array<{ years: string; name?: string; notes?: string }>;
}

export const vehicles: Vehicle[] = (vehiclesJson as any).vehicles || [];

export const vehicleBySlug = (slug: string): Vehicle | undefined =>
  vehicles.find((v) => v.slug === slug);

export const vehiclesByCategory = (category: string): Vehicle[] =>
  vehicles.filter((v) => v.category === category);

// ── KNOWN ISSUES ──────────────────────────────────────────────────────────────
export interface KnownIssue {
  title: string;
  description: string;
  severity: 'minor' | 'moderate' | 'major';
  affected_trims?: string[];
  fix_description?: string;
  estimated_cost?: string;
  tsb?: string;
}

export interface ModelIssues {
  model: string;
  slug: string;
  issues_by_year: Array<{
    year_range: string;
    issues: KnownIssue[];
  }>;
}

export const knownIssues: ModelIssues[] =
  (knownIssuesJson as any).known_issues || [];

export const knownIssuesForModel = (slug: string): ModelIssues | undefined =>
  knownIssues.find((m) => m.slug === slug);

// ── MECHANICS ─────────────────────────────────────────────────────────────────
export interface Mechanic {
  id?: string;
  name: string;
  city: string;
  state: string;
  specialties?: string[];
  phone?: string;
  website?: string;
  rating?: number;
  description?: string;
  address?: string;
}

export const mechanics: Mechanic[] =
  (mechanicsJson as any).mechanics ||
  (Array.isArray(mechanicsJson) ? (mechanicsJson as Mechanic[]) : []);

export const mechanicsByState = (state: string): Mechanic[] =>
  mechanics.filter((m) => m.state?.toUpperCase() === state.toUpperCase());

// ── NEWS ──────────────────────────────────────────────────────────────────────
export interface NewsItem {
  title: string;
  source: string;
  url: string;
  date: string;
  category: string;
  summary: string;
  image?: string;
}

export const news: NewsItem[] = Array.isArray(newsJson) ? (newsJson as NewsItem[]) : [];

export const newsByCategory = (category: string): NewsItem[] =>
  news.filter((n) => n.category === category);

export const recentNews = (limit = 10): NewsItem[] =>
  [...news]
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, limit);

// ── VINTAGE ADS ───────────────────────────────────────────────────────────────
export interface VintageAd {
  id?: string;
  title?: string;
  year?: number | string;
  decade?: string;
  model?: string;
  description?: string;
  image?: string;
  source?: string;
}

export const vintageAds: VintageAd[] = Array.isArray(vintageAdsJson)
  ? (vintageAdsJson as VintageAd[])
  : ((vintageAdsJson as any).ads || []);

export const vintageAdsByDecade = (decade: string): VintageAd[] =>
  vintageAds.filter((ad) => String(ad.decade) === decade || String(ad.year).startsWith(decade.slice(0, 3)));

// ── EVENTS ────────────────────────────────────────────────────────────────────
export interface ChevyEvent {
  id: number | string;
  name: string;
  dates: string;
  location: {
    city: string;
    state: string;
    venue?: string;
  };
  type: string;
  chevy_specific?: boolean;
  description?: string;
  url?: string;
  region?: string;
}

const tagRegion = (events: any[], region: string): ChevyEvent[] =>
  events.map((e) => ({ ...e, region }));

export const events: ChevyEvent[] = [
  ...tagRegion((southwestEventsJson as any).events || [], 'southwest'),
  ...tagRegion((northeastEventsJson as any).events || [], 'northeast'),
  ...tagRegion((midwestEventsJson as any).events || [], 'midwest'),
];

export const eventsByState = (state: string): ChevyEvent[] =>
  events.filter((e) => e.location.state?.toUpperCase() === state.toUpperCase());

export const eventsByRegion = (region: string): ChevyEvent[] =>
  events.filter((e) => e.region === region);

// ── VEHICLE CATEGORIES ────────────────────────────────────────────────────────
export const CATEGORIES: Record<
  string,
  { slug: string; label: string; description: string }
> = {
  truck: {
    slug: 'trucks',
    label: 'Trucks',
    description: 'Silverado, Colorado, and every hauler that wears the bowtie.',
  },
  car: {
    slug: 'cars',
    label: 'Cars',
    description: 'Corvette, Camaro, Malibu — the cars that made Chevy.',
  },
  suv: {
    slug: 'suvs',
    label: 'SUVs',
    description: 'Tahoe, Suburban, Traverse, Equinox, Blazer.',
  },
  ev: {
    slug: 'evs',
    label: 'Electric Vehicles',
    description: 'The Ultium era — Blazer EV, Equinox EV, Silverado EV.',
  },
  classic: {
    slug: 'classics',
    label: 'Classics',
    description: 'C10s, Impalas, Bel Airs, muscle cars — the originals.',
  },
};

export const categoryBySlug = (slug: string) =>
  Object.entries(CATEGORIES).find(([, cat]) => cat.slug === slug);
