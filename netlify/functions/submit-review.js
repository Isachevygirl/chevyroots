/* ============================================================
   submit-review.js — Netlify Function
   Handles community review submissions
   POST /.netlify/functions/submit-review
============================================================ */

exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  let body;
  try {
    body = JSON.parse(event.body);
  } catch {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Invalid JSON' }) };
  }

  // Validate required fields
  const required = ['mechanic_id', 'author', 'rating', 'title', 'body'];
  const missing = required.filter(f => !body[f]);
  if (missing.length) {
    return {
      statusCode: 400,
      headers,
      body: JSON.stringify({ error: `Missing required fields: ${missing.join(', ')}` })
    };
  }

  // Validate rating range
  const rating = parseInt(body.rating);
  if (isNaN(rating) || rating < 1 || rating > 5) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Rating must be 1-5' }) };
  }

  // Sanitize text fields (basic XSS prevention)
  const sanitize = (str) => String(str).replace(/[<>]/g, '').trim().slice(0, 2000);

  const review = {
    id: `r_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    mechanic_id: sanitize(body.mechanic_id),
    author: sanitize(body.author).slice(0, 100),
    rating,
    date: new Date().toISOString().split('T')[0],
    vehicle: body.vehicle ? sanitize(body.vehicle).slice(0, 100) : '',
    service_type: body.service_type ? sanitize(body.service_type) : '',
    title: sanitize(body.title).slice(0, 200),
    body: sanitize(body.body),
    helpful_count: 0,
    status: 'pending' // All submissions require moderation
  };

  // For now, log the review. In production, write to Netlify Blobs or a database.
  // Reviews in "pending" status won't appear on the site until manually approved
  // and added to mechanic-reviews.json.
  console.log('New review submission:', JSON.stringify(review));

  return {
    statusCode: 200,
    headers,
    body: JSON.stringify({
      success: true,
      message: 'Thank you! Your review has been submitted for moderation.',
      review_id: review.id
    })
  };
};
