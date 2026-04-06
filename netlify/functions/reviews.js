/* ============================================================
   reviews.js — Netlify Function
   Aggregates external reviews from Yelp Fusion + Google Places
   GET /.netlify/functions/reviews?mechanic_id=<slug>
============================================================ */

const YELP_API_KEY = process.env.YELP_API_KEY;
const GOOGLE_API_KEY = process.env.GOOGLE_PLACES_API_KEY;
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours

// Simple in-memory cache (persists across warm invocations)
const cache = new Map();

exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers, body: '' };
  }

  if (event.httpMethod !== 'GET') {
    return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  const mechanicId = event.queryStringParameters?.mechanic_id;
  if (!mechanicId) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'mechanic_id is required' }) };
  }

  // Check cache
  const cached = cache.get(mechanicId);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return { statusCode: 200, headers, body: JSON.stringify({ ...cached.data, cached: true }) };
  }

  // Load mechanic data to get external IDs
  let mechanic;
  try {
    const fs = require('fs');
    const path = require('path');
    const dataPath = path.resolve(__dirname, '../../data/mechanics.json');
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    mechanic = data.mechanics.find(m => m.id === mechanicId || m.slug === mechanicId);
  } catch (e) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: 'Failed to load mechanic data' }) };
  }

  if (!mechanic) {
    return { statusCode: 404, headers, body: JSON.stringify({ error: 'Mechanic not found' }) };
  }

  const result = { yelp: null, google: null };

  // Fetch Yelp reviews
  if (YELP_API_KEY && mechanic.external_ids.yelp) {
    try {
      const yelpRes = await fetch(
        `https://api.yelp.com/v3/businesses/${mechanic.external_ids.yelp}/reviews?limit=5&sort_by=newest`,
        { headers: { Authorization: `Bearer ${YELP_API_KEY}` } }
      );
      if (yelpRes.ok) {
        const yelpData = await yelpRes.json();
        result.yelp = {
          reviews: (yelpData.reviews || []).map(r => ({
            author: r.user?.name || 'Anonymous',
            rating: r.rating,
            text: r.text,
            date: r.time_created,
            url: r.url
          })),
          total: yelpData.total || 0
        };
      }
    } catch (e) {
      console.error('Yelp API error:', e.message);
    }
  }

  // Fetch Google Places reviews
  if (GOOGLE_API_KEY && mechanic.external_ids.google_place_id) {
    try {
      const googleRes = await fetch(
        `https://maps.googleapis.com/maps/api/place/details/json?place_id=${mechanic.external_ids.google_place_id}&fields=reviews,rating,user_ratings_total&key=${GOOGLE_API_KEY}`
      );
      if (googleRes.ok) {
        const googleData = await googleRes.json();
        const place = googleData.result || {};
        result.google = {
          reviews: (place.reviews || []).slice(0, 5).map(r => ({
            author: r.author_name || 'Anonymous',
            rating: r.rating,
            text: r.text,
            date: new Date(r.time * 1000).toISOString(),
            relative_time: r.relative_time_description
          })),
          rating: place.rating || null,
          total: place.user_ratings_total || 0
        };
      }
    } catch (e) {
      console.error('Google Places API error:', e.message);
    }
  }

  // Update cache
  cache.set(mechanicId, { data: result, timestamp: Date.now() });

  return {
    statusCode: 200,
    headers,
    body: JSON.stringify({ ...result, cached: false })
  };
};
