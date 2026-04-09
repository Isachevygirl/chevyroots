// POST /api/submit-event
// Accepts a community-submitted car show/cruise event.
// Inserts into `events_queue` in Turso for moderator review.

import { createClient } from '@libsql/client';

function getDb() {
  if (!process.env.TURSO_DB_URL) return null;
  return createClient({
    url: process.env.TURSO_DB_URL,
    authToken: process.env.TURSO_AUTH_TOKEN,
  });
}

function parseFormBody(event) {
  const params = new URLSearchParams(event.body || '');
  return Object.fromEntries(params.entries());
}

function sanitize(s) {
  return String(s || '').slice(0, 2000).replace(/[<>]/g, '');
}

export async function handler(event) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method not allowed' };
  }

  try {
    const data = parseFormBody(event);
    const {
      'event-name': eventName,
      'event-dates': eventDates,
      venue,
      city,
      state,
      'event-type': eventType,
      'chevy-focus': chevyFocus,
      description,
      url,
      'submitter-email': submitterEmail,
    } = data;

    if (!eventName || !eventDates || !city || !state || !submitterEmail) {
      return { statusCode: 400, body: JSON.stringify({ error: 'Missing required fields' }) };
    }

    const db = getDb();
    if (db) {
      await db.execute({
        sql: `INSERT INTO events_queue (
          event_name, event_dates, venue, city, state, event_type,
          chevy_focus, description, url, submitter_email,
          submitted_at, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), 'pending')`,
        args: [
          sanitize(eventName),
          sanitize(eventDates),
          sanitize(venue),
          sanitize(city),
          sanitize(state).toUpperCase().slice(0, 2),
          sanitize(eventType),
          sanitize(chevyFocus),
          sanitize(description),
          sanitize(url),
          sanitize(submitterEmail),
        ],
      });
    }

    return {
      statusCode: 302,
      headers: { Location: '/submit/event/?submitted=1' },
      body: '',
    };
  } catch (err) {
    console.error('submit-event error:', err);
    return { statusCode: 500, body: JSON.stringify({ error: 'Something went wrong' }) };
  }
}
