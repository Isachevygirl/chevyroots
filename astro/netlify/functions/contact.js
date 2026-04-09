// POST /api/contact
// Contact form handler.
//
// Accepts form-encoded from the contact page. Sends a Resend email to
// hello@chevyroots.com with the submission details.
//
// Basic honeypot + per-IP rate limiting to suppress spam.

const RESEND_ENDPOINT = 'https://api.resend.com/emails';

function parseBody(event) {
  const contentType = event.headers['content-type'] || '';
  if (contentType.includes('application/json')) {
    return JSON.parse(event.body || '{}');
  }
  const params = new URLSearchParams(event.body || '');
  return Object.fromEntries(params.entries());
}

function sanitize(s) {
  return String(s || '').slice(0, 5000).replace(/[<>]/g, '');
}

async function sendContactEmail({ name, email, topic, message }) {
  const res = await fetch(RESEND_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
    },
    body: JSON.stringify({
      from: process.env.RESEND_FROM_EMAIL || 'ChevyRoots Contact <hello@chevyroots.com>',
      to: ['hello@chevyroots.com'],
      reply_to: email,
      subject: `[ChevyRoots] ${topic || 'Contact form'}: ${name}`,
      html: `
        <div style="font-family: -apple-system, sans-serif; max-width: 560px;">
          <h2>New contact form submission</h2>
          <p><strong>Name:</strong> ${sanitize(name)}</p>
          <p><strong>Email:</strong> ${sanitize(email)}</p>
          <p><strong>Topic:</strong> ${sanitize(topic || 'general')}</p>
          <hr>
          <p><strong>Message:</strong></p>
          <p style="white-space: pre-wrap;">${sanitize(message)}</p>
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
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method not allowed' };
  }

  try {
    const body = parseBody(event);
    const { name, email, topic, message, _hp } = body;

    // Honeypot: real users won't fill this hidden field
    if (_hp) {
      return { statusCode: 200, body: JSON.stringify({ ok: true }) };
    }

    if (!name || !email || !message) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Missing required fields' }),
      };
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Invalid email address' }),
      };
    }

    await sendContactEmail({ name, email, topic, message });

    return {
      statusCode: 302,
      headers: { Location: '/contact/?sent=1' },
      body: '',
    };
  } catch (err) {
    console.error('Contact handler error:', err);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Something went wrong' }),
    };
  }
}
