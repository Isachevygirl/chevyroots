// GET /go/{retailer}/{slug}
// Affiliate outbound redirect.
//
// 1. Logs the click to Turso (retailer, slug, timestamp, referrer, country)
// 2. Looks up the destination URL in the affiliate_links table
// 3. 302 redirects to the destination with tracking UTM params
// 4. Falls back to a known-good URL per retailer if the slug isn't found
//
// Deploy with the Netlify redirect rule in netlify.toml:
//   [[redirects]]
//     from = "/go/*"
//     to = "/.netlify/functions/go/:splat"
//     status = 200
//
// Environment variables:
//   TURSO_DB_URL
//   TURSO_AUTH_TOKEN

import { createClient } from '@libsql/client';

// Per-retailer fallback destinations. If a specific slug isn't in the DB
// we still redirect cleanly instead of 404ing.
const FALLBACK_URLS = {
  amazon: 'https://www.amazon.com/?tag=chevyroots-20',
  summit: 'https://www.summitracing.com/?aff=chevyroots',
  jegs: 'https://www.jegs.com/?aff=chevyroots',
  'classic-industries': 'https://www.classicindustries.com/?aff=chevyroots',
  'lmc-truck': 'https://www.lmctruck.com/?aff=chevyroots',
  weathertech: 'https://www.weathertech.com/?aff=chevyroots',
  realtruck: 'https://www.realtruck.com/?aff=chevyroots',
  americantrucks: 'https://www.americantrucks.com/?aff=chevyroots',
  hagerty: 'https://www.hagerty.com/?aff=chevyroots',
  endurance: 'https://www.enduranceadvantage.com/?aff=chevyroots',
  carchex: 'https://www.carchex.com/?aff=chevyroots',
  'discount-tire': 'https://www.discounttire.com/?aff=chevyroots',
  'tire-rack': 'https://www.tirerack.com/?aff=chevyroots',
  etrailer: 'https://www.etrailer.com/?aff=chevyroots',
  partner: 'https://chevyroots.com/partners/',
};

function getClient() {
  if (!process.env.TURSO_DB_URL) return null;
  return createClient({
    url: process.env.TURSO_DB_URL,
    authToken: process.env.TURSO_AUTH_TOKEN,
  });
}

async function logClick(db, { retailer, slug, referrer, country, ua }) {
  if (!db) return;
  try {
    await db.execute({
      sql: `INSERT INTO affiliate_clicks (retailer, slug, ts, referrer, country, ua_class)
            VALUES (?, ?, datetime('now'), ?, ?, ?)`,
      args: [retailer, slug, referrer || '', country || '', ua || ''],
    });
  } catch (err) {
    console.error('Click log failed:', err);
  }
}

async function resolveUrl(db, retailer, slug) {
  if (db) {
    try {
      const result = await db.execute({
        sql: 'SELECT url FROM affiliate_links WHERE retailer = ? AND slug = ? LIMIT 1',
        args: [retailer, slug],
      });
      if (result.rows && result.rows.length > 0) {
        return result.rows[0].url;
      }
    } catch (err) {
      console.error('URL lookup failed:', err);
    }
  }
  return FALLBACK_URLS[retailer] || null;
}

function classifyUA(ua) {
  if (!ua) return 'unknown';
  if (/bot|crawler|spider|scraper/i.test(ua)) return 'bot';
  if (/mobile|android|iphone|ipad/i.test(ua)) return 'mobile';
  return 'desktop';
}

export async function handler(event) {
  // Path comes in as /go/{retailer}/{slug}
  // When called via the Netlify function directly it'll be /.netlify/functions/go/{retailer}/{slug}
  const path = event.path.replace(/^\/\.netlify\/functions\/go\//, '').replace(/^\/go\//, '');
  const parts = path.split('/').filter(Boolean);

  if (parts.length < 2) {
    return {
      statusCode: 400,
      body: 'Expected /go/{retailer}/{slug}',
    };
  }

  const [retailer, ...slugParts] = parts;
  const slug = slugParts.join('/');

  const db = getClient();
  const ua = event.headers['user-agent'] || '';
  const referrer = event.headers.referer || event.headers.referrer || '';
  const country = event.headers['x-country'] || event.headers['cf-ipcountry'] || '';

  // Fire-and-forget click log
  const logPromise = logClick(db, {
    retailer,
    slug,
    referrer,
    country,
    ua: classifyUA(ua),
  });

  const destination = await resolveUrl(db, retailer, slug);

  // Always complete the log before redirecting
  await logPromise;

  if (!destination) {
    return {
      statusCode: 404,
      body: `No affiliate link found for ${retailer}/${slug}`,
    };
  }

  // Append tracking UTM so we can cross-reference with the retailer's reporting
  const dest = new URL(destination);
  if (!dest.searchParams.has('utm_source')) dest.searchParams.set('utm_source', 'chevyroots');
  if (!dest.searchParams.has('utm_medium')) dest.searchParams.set('utm_medium', 'affiliate');
  if (!dest.searchParams.has('utm_campaign')) dest.searchParams.set('utm_campaign', slug);

  return {
    statusCode: 302,
    headers: {
      Location: dest.toString(),
      'Cache-Control': 'no-store',
    },
    body: '',
  };
}
