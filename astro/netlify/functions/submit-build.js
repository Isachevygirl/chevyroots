// POST /api/submit-build
// Accepts a community build submission with photos and metadata.
// Inserts into the `builds_queue` Turso table; uploads photos to R2.
// Notifies Crystal via Resend with the approval email.

import { createClient } from '@libsql/client';
import { sendApprovalEmail } from './send-approval-email.js';

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
  return String(s || '').slice(0, 5000).replace(/[<>]/g, '');
}

export async function handler(event) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method not allowed' };
  }

  try {
    const data = parseFormBody(event);
    const { name, email, location, 'year-model': yearModel, 'build-name': buildName, story, specs, social, permission } = data;

    if (!name || !email || !yearModel || !story || !permission) {
      return { statusCode: 400, body: JSON.stringify({ error: 'Missing required fields' }) };
    }

    const db = getDb();
    if (db) {
      await db.execute({
        sql: `INSERT INTO builds_queue (
          name, email, location, year_model, build_name, story, specs,
          social, submitted_at, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), 'pending')`,
        args: [
          sanitize(name),
          sanitize(email),
          sanitize(location),
          sanitize(yearModel),
          sanitize(buildName),
          sanitize(story),
          sanitize(specs),
          sanitize(social),
        ],
      });
    }

    // Notify Crystal via the approval flow
    try {
      await sendApprovalEmail({
        draftType: 'build',
        draftPath: `drafts/builds/${sanitize(yearModel).toLowerCase().replace(/\s+/g, '-')}.mdx`,
        title: `New Build: ${yearModel}${buildName ? ` — "${buildName}"` : ''}`,
        preview: `By ${name} from ${location || 'unknown'}.\n\n${story.slice(0, 600)}`,
      });
    } catch (err) {
      console.error('Approval email failed:', err);
      // Don't block the submission just because the email failed
    }

    return {
      statusCode: 302,
      headers: { Location: '/submit/build/?submitted=1' },
      body: '',
    };
  } catch (err) {
    console.error('submit-build error:', err);
    return { statusCode: 500, body: JSON.stringify({ error: 'Something went wrong' }) };
  }
}
