// POST /api/subscribe
// Newsletter subscription endpoint.
//
// Accepts JSON or form-encoded: { email, source? }
// - Adds the contact to Loops.so with a source tag
// - Sends a confirmation email via Resend
//
// Environment variables required:
//   LOOPS_API_KEY        - https://app.loops.so/settings?page=api
//   RESEND_API_KEY       - https://resend.com/api-keys
//   RESEND_FROM_EMAIL    - Verified sender email (e.g. hello@chevyroots.com)

const LOOPS_ENDPOINT = 'https://app.loops.so/api/v1/contacts/create';
const RESEND_ENDPOINT = 'https://api.resend.com/emails';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function parseBody(event) {
  const contentType = event.headers['content-type'] || event.headers['Content-Type'] || '';
  if (contentType.includes('application/json')) {
    return JSON.parse(event.body || '{}');
  }
  if (contentType.includes('application/x-www-form-urlencoded')) {
    const params = new URLSearchParams(event.body || '');
    return Object.fromEntries(params.entries());
  }
  return {};
}

function isValidEmail(email) {
  return typeof email === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

async function addToLoops(email, source) {
  const res = await fetch(LOOPS_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.LOOPS_API_KEY}`,
    },
    body: JSON.stringify({
      email,
      source: source || 'website',
      subscribed: true,
      userGroup: 'newsletter',
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Loops error ${res.status}: ${text}`);
  }
  return res.json();
}

async function sendWelcomeEmail(email) {
  const res = await fetch(RESEND_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
    },
    body: JSON.stringify({
      from: process.env.RESEND_FROM_EMAIL || 'ChevyRoots <hello@chevyroots.com>',
      to: email,
      subject: 'Welcome to ChevyRoots 🏁',
      html: `
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 560px; margin: 0 auto; padding: 32px 24px; color: #1a1a1a; line-height: 1.6;">
          <h1 style="font-size: 28px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.02em; margin: 0 0 16px;">Welcome to ChevyRoots</h1>
          <p style="font-size: 16px;">Hey — Crystal here.</p>
          <p style="font-size: 16px;">You're in. Every Friday I send a quick newsletter with new buyer's guides, event reports, the best community-submitted builds, and Crystal's Corner — my weekly editorial column where I write about what's on my mind in Chevy world.</p>
          <p style="font-size: 16px;">No fluff. No filler. One email a week. Unsubscribe whenever you want.</p>
          <p style="font-size: 16px;">While you wait for the first issue, here are a few places to start:</p>
          <ul style="font-size: 16px;">
            <li><a href="https://chevyroots.com/guides/" style="color: #c4a035;">Buyer's guides library</a> — 30+ honest takes on trucks, Corvettes, classics, and more</li>
            <li><a href="https://chevyroots.com/crystal/" style="color: #c4a035;">My story</a> — why I started this, and why I drive a ZR2</li>
            <li><a href="https://chevyroots.com/my-zr2/" style="color: #c4a035;">My ZR2</a> — the living page for my actual truck</li>
          </ul>
          <p style="font-size: 16px;">Talk soon,<br>Crystal<br>Founder, ChevyRoots</p>
          <hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0;" />
          <p style="font-size: 12px; color: #888;">You're receiving this because you subscribed at chevyroots.com. If you didn't, <a href="mailto:hello@chevyroots.com" style="color: #888;">let us know</a>.</p>
        </div>
      `,
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Resend error ${res.status}: ${text}`);
  }
  return res.json();
}

export async function handler(event) {
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: CORS_HEADERS, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers: CORS_HEADERS,
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    const { email, source } = parseBody(event);

    if (!isValidEmail(email)) {
      return {
        statusCode: 400,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: 'Invalid email address' }),
      };
    }

    // Run both in parallel. If Loops fails we still want Resend to fire (they
    // might already be in Loops from a previous subscribe).
    const [loopsResult, emailResult] = await Promise.allSettled([
      addToLoops(email, source),
      sendWelcomeEmail(email),
    ]);

    if (loopsResult.status === 'rejected' && emailResult.status === 'rejected') {
      console.error('Both Loops and Resend failed:', loopsResult.reason, emailResult.reason);
      return {
        statusCode: 502,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: 'Subscribe failed, please try again' }),
      };
    }

    return {
      statusCode: 200,
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      body: JSON.stringify({ ok: true, email }),
    };
  } catch (err) {
    console.error('Subscribe handler error:', err);
    return {
      statusCode: 500,
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'Internal error' }),
    };
  }
}
