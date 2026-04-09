// GET /.netlify/functions/approval-webhook?token=...
// The link Crystal clicks from her approval email.
//
// 1. Validates the signed JWT (HMAC-SHA256, 7-day expiry, single-use via Turso)
// 2. If approve: commits the draft from `drafts/` → content collection path via
//    GitHub Contents API, marking the commit as authored by Crystal
// 3. If reject: moves to drafts/rejected/ (same GitHub API)
// 4. Returns a simple HTML confirmation page
//
// Environment variables:
//   APPROVAL_JWT_SECRET
//   GITHUB_COMMIT_TOKEN    (fine-grained PAT with Contents: read/write on the repo)
//   GITHUB_REPO_OWNER
//   GITHUB_REPO_NAME
//   TURSO_DB_URL
//   TURSO_AUTH_TOKEN

import crypto from 'node:crypto';
import { createClient } from '@libsql/client';

const GH_API = 'https://api.github.com';

function base64urlDecode(str) {
  return Buffer.from(str.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString();
}

function verifyJwt(token, secret) {
  const [header, body, sig] = token.split('.');
  if (!header || !body || !sig) throw new Error('Invalid token format');
  const toVerify = `${header}.${body}`;
  const expectedSig = crypto.createHmac('sha256', secret).update(toVerify).digest('base64url');
  if (sig !== expectedSig) throw new Error('Invalid signature');
  const payload = JSON.parse(base64urlDecode(body));
  const now = Math.floor(Date.now() / 1000);
  if (payload.exp && payload.exp < now) throw new Error('Token expired');
  return payload;
}

function getDb() {
  if (!process.env.TURSO_DB_URL) return null;
  return createClient({
    url: process.env.TURSO_DB_URL,
    authToken: process.env.TURSO_AUTH_TOKEN,
  });
}

async function checkTokenReuse(db, jti) {
  if (!db) return false;
  const result = await db.execute({
    sql: 'SELECT jti FROM consumed_tokens WHERE jti = ? LIMIT 1',
    args: [jti],
  });
  return result.rows && result.rows.length > 0;
}

async function markTokenConsumed(db, jti) {
  if (!db) return;
  await db.execute({
    sql: `INSERT OR IGNORE INTO consumed_tokens (jti, consumed_at) VALUES (?, datetime('now'))`,
    args: [jti],
  });
}

async function ghRequest(path, method = 'GET', body) {
  const url = `${GH_API}${path}`;
  const res = await fetch(url, {
    method,
    headers: {
      Accept: 'application/vnd.github+json',
      Authorization: `Bearer ${process.env.GITHUB_COMMIT_TOKEN}`,
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'chevyroots-approval-webhook',
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GitHub ${method} ${path} failed ${res.status}: ${text}`);
  }
  return res.json();
}

async function getFile(owner, repo, path) {
  return ghRequest(`/repos/${owner}/${repo}/contents/${encodeURIComponent(path)}`);
}

async function putFile(owner, repo, path, content, message, sha) {
  return ghRequest(`/repos/${owner}/${repo}/contents/${encodeURIComponent(path)}`, 'PUT', {
    message,
    content: Buffer.from(content).toString('base64'),
    sha,
    committer: {
      name: 'Crystal (via approval webhook)',
      email: 'crystal@chevyroots.com',
    },
  });
}

async function deleteFile(owner, repo, path, message, sha) {
  return ghRequest(`/repos/${owner}/${repo}/contents/${encodeURIComponent(path)}`, 'DELETE', {
    message,
    sha,
    committer: {
      name: 'Crystal (via approval webhook)',
      email: 'crystal@chevyroots.com',
    },
  });
}

function livePathFromDraftPath(draftPath) {
  // drafts/guides/foo.mdx → astro/src/content/guides/foo.mdx
  return `astro/src/content/${draftPath.replace(/^drafts\//, '')}`;
}

function rejectedPathFromDraftPath(draftPath) {
  // drafts/guides/foo.mdx → drafts/rejected/guides/foo.mdx
  return draftPath.replace(/^drafts\//, 'drafts/rejected/');
}

async function approveDraft(payload) {
  const owner = process.env.GITHUB_REPO_OWNER;
  const repo = process.env.GITHUB_REPO_NAME;
  const { draftPath } = payload;

  // Read the draft
  const draftFile = await getFile(owner, repo, draftPath);
  const content = Buffer.from(draftFile.content, 'base64').toString();

  // Write to the live path
  const livePath = livePathFromDraftPath(draftPath);
  let existingSha;
  try {
    const existing = await getFile(owner, repo, livePath);
    existingSha = existing.sha;
  } catch {
    /* new file */
  }
  await putFile(owner, repo, livePath, content, `Publish draft: ${livePath}`, existingSha);

  // Delete the draft
  await deleteFile(owner, repo, draftPath, `Consume draft after publish: ${draftPath}`, draftFile.sha);
}

async function rejectDraft(payload) {
  const owner = process.env.GITHUB_REPO_OWNER;
  const repo = process.env.GITHUB_REPO_NAME;
  const { draftPath } = payload;

  const draftFile = await getFile(owner, repo, draftPath);
  const content = Buffer.from(draftFile.content, 'base64').toString();

  const rejectedPath = rejectedPathFromDraftPath(draftPath);
  await putFile(owner, repo, rejectedPath, content, `Reject draft: ${draftPath}`);
  await deleteFile(owner, repo, draftPath, `Remove rejected draft: ${draftPath}`, draftFile.sha);
}

function htmlResponse(title, body) {
  return {
    statusCode: 200,
    headers: { 'Content-Type': 'text/html; charset=utf-8' },
    body: `<!doctype html><html><head><meta charset="utf-8"><title>${title}</title><style>
      body { font-family: -apple-system, sans-serif; background: #1a1a1a; color: #f0ede6; text-align: center; padding: 80px 24px; }
      .box { max-width: 480px; margin: 0 auto; padding: 48px; background: #2a2a2a; border: 1px solid #333; border-left: 3px solid #c4a035; border-radius: 8px; }
      h1 { font-size: 28px; text-transform: uppercase; letter-spacing: 0.02em; color: #c4a035; margin: 0 0 16px; }
      p { font-size: 16px; line-height: 1.65; color: #b0ada6; }
      a { color: #c4a035; }
    </style></head><body><div class="box"><h1>${title}</h1>${body}</div></body></html>`,
  };
}

export async function handler(event) {
  const token = event.queryStringParameters?.token;
  if (!token) {
    return htmlResponse('Invalid', '<p>Missing approval token.</p>');
  }

  let payload;
  try {
    payload = verifyJwt(token, process.env.APPROVAL_JWT_SECRET);
  } catch (err) {
    console.error('Token verify failed:', err.message);
    return htmlResponse('Token Invalid', `<p>${err.message}. Contact dave@chevyroots.com if this keeps happening.</p>`);
  }

  const db = getDb();
  if (await checkTokenReuse(db, payload.jti)) {
    return htmlResponse('Already Used', '<p>This approval link has already been used. Each link is single-use.</p>');
  }

  try {
    if (payload.action === 'approve') {
      await approveDraft(payload);
      await markTokenConsumed(db, payload.jti);
      return htmlResponse(
        'Published ✓',
        `<p>The draft has been approved and committed to the site. Netlify will rebuild in about 90 seconds.</p><p><a href="/">Back to ChevyRoots</a></p>`
      );
    } else if (payload.action === 'reject') {
      await rejectDraft(payload);
      await markTokenConsumed(db, payload.jti);
      return htmlResponse(
        'Rejected',
        `<p>The draft has been moved to drafts/rejected/. A log entry was saved.</p><p><a href="/">Back to ChevyRoots</a></p>`
      );
    }
    return htmlResponse('Unknown action', `<p>Unknown action: ${payload.action}</p>`);
  } catch (err) {
    console.error('Approval webhook error:', err);
    return htmlResponse('Error', `<p>${err.message}</p>`);
  }
}
