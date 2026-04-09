// Internal helper — NOT a public endpoint.
// Called by other functions (e.g. a cron-triggered draft dispatcher, or the
// content pipeline) to send Crystal an email with an approve/reject link for
// a specific draft.
//
// Usage from another function:
//   import { sendApprovalEmail } from './send-approval-email.js';
//   await sendApprovalEmail({
//     draftType: 'guide',            // 'guide' | 'crystals-corner' | 'event-report' | 'video'
//     draftPath: 'drafts/guides/my-new-guide.mdx',
//     title: 'New Guide Draft — Silverado Lease Deals April 2026',
//     preview: 'The first 300 words of the draft body...',
//     heroImage: 'https://chevyroots.com/photos/...',
//   });
//
// The email contains:
//   - Preview of the draft
//   - "APPROVE" button (signed JWT)
//   - "REJECT" button (signed JWT)
//   - "Edit on GitHub" link
//
// The JWT is validated and consumed by approval-webhook.js below.

import crypto from 'node:crypto';

const RESEND_ENDPOINT = 'https://api.resend.com/emails';
const APPROVAL_BASE_URL = process.env.URL || 'https://chevyroots.com';

function base64url(buf) {
  return Buffer.from(buf).toString('base64url');
}

function signJwt(payload, secret, expiresInSeconds = 7 * 24 * 60 * 60) {
  const header = { alg: 'HS256', typ: 'JWT' };
  const now = Math.floor(Date.now() / 1000);
  const body = {
    ...payload,
    iat: now,
    exp: now + expiresInSeconds,
    jti: crypto.randomBytes(8).toString('hex'),
  };
  const encodedHeader = base64url(JSON.stringify(header));
  const encodedBody = base64url(JSON.stringify(body));
  const toSign = `${encodedHeader}.${encodedBody}`;
  const sig = crypto.createHmac('sha256', secret).update(toSign).digest();
  return `${toSign}.${base64url(sig)}`;
}

export async function sendApprovalEmail({ draftType, draftPath, title, preview, heroImage }) {
  if (!process.env.APPROVAL_JWT_SECRET) {
    throw new Error('APPROVAL_JWT_SECRET not set');
  }
  if (!process.env.RESEND_API_KEY) {
    throw new Error('RESEND_API_KEY not set');
  }

  const approveToken = signJwt(
    { action: 'approve', draftType, draftPath },
    process.env.APPROVAL_JWT_SECRET
  );
  const rejectToken = signJwt(
    { action: 'reject', draftType, draftPath },
    process.env.APPROVAL_JWT_SECRET
  );

  const approveUrl = `${APPROVAL_BASE_URL}/.netlify/functions/approval-webhook?token=${approveToken}`;
  const rejectUrl = `${APPROVAL_BASE_URL}/.netlify/functions/approval-webhook?token=${rejectToken}`;
  const githubUrl = `https://github.com/${process.env.GITHUB_REPO_OWNER}/${process.env.GITHUB_REPO_NAME}/edit/main/astro/src/content/${draftPath.replace('drafts/', '')}`;

  const safeTitle = String(title).replace(/[<>]/g, '');
  const safePreview = String(preview || '').slice(0, 1500).replace(/[<>]/g, '');
  const heroHtml = heroImage
    ? `<img src="${heroImage}" alt="" style="width:100%;border-radius:8px;margin-bottom:16px;" />`
    : '';

  const html = `
    <div style="font-family: -apple-system, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; color: #1a1a1a;">
      <div style="font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: #c4a035; margin-bottom: 12px;">
        ChevyRoots · Draft Awaiting Your Approval
      </div>
      <h1 style="font-size: 26px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.02em; line-height: 1.1; margin: 0 0 20px;">
        ${safeTitle}
      </h1>
      ${heroHtml}
      <div style="font-size: 15px; line-height: 1.6; color: #333; margin-bottom: 24px;">
        ${safePreview.replace(/\n\n/g, '</p><p>').replace(/^/, '<p>').replace(/$/, '</p>')}
      </div>
      <div style="margin: 32px 0; text-align: center;">
        <a href="${approveUrl}" style="display: inline-block; background: #c4a035; color: #1a1a1a; padding: 14px 32px; border-radius: 6px; text-decoration: none; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; margin: 0 6px 12px;">✓ Approve</a>
        <a href="${rejectUrl}" style="display: inline-block; background: #c0392b; color: #fff; padding: 14px 32px; border-radius: 6px; text-decoration: none; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; margin: 0 6px 12px;">✗ Reject</a>
      </div>
      <div style="text-align: center; margin-bottom: 24px;">
        <a href="${githubUrl}" style="color: #666; font-size: 13px;">Edit on GitHub →</a>
      </div>
      <hr style="border: none; border-top: 1px solid #ddd; margin: 32px 0 16px;" />
      <p style="font-size: 11px; color: #888; text-align: center;">
        This approval link is single-use and expires in 7 days. Signed with HMAC-SHA256.
      </p>
    </div>
  `;

  const res = await fetch(RESEND_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
    },
    body: JSON.stringify({
      from: process.env.RESEND_FROM_EMAIL || 'ChevyRoots Editor <hello@chevyroots.com>',
      to: ['crystal@chevyroots.com'],
      subject: `Draft awaiting approval — ${safeTitle}`,
      html,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Resend error ${res.status}: ${text}`);
  }
  return res.json();
}

// Allow this module to be called as a Netlify function directly for testing
export async function handler(event) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method not allowed' };
  }
  try {
    const payload = JSON.parse(event.body || '{}');
    const result = await sendApprovalEmail(payload);
    return { statusCode: 200, body: JSON.stringify(result) };
  } catch (err) {
    console.error('send-approval-email error:', err);
    return { statusCode: 500, body: JSON.stringify({ error: err.message }) };
  }
}
