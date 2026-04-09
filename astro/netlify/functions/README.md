# ChevyRoots Netlify Functions

These Node.js functions power the dynamic pieces of ChevyRoots: newsletter
subscriptions, affiliate redirect tracking, contact form, build/event
submissions, and the email-based approval workflow for Crystal.

## Deploy prerequisites

1. **Netlify site** created and connected to the repo.
2. **Environment variables** set in the Netlify dashboard (see `.env.example`
   at the repo root). Minimum required for this first batch of functions:

   | Variable | Purpose |
   |---|---|
   | `LOOPS_API_KEY` | Newsletter contacts |
   | `RESEND_API_KEY` | Transactional email |
   | `RESEND_FROM_EMAIL` | Verified sender (e.g. `hello@chevyroots.com`) |
   | `TURSO_DB_URL` | Sqlite-at-edge database URL |
   | `TURSO_AUTH_TOKEN` | Turso auth token |
   | `APPROVAL_JWT_SECRET` | HMAC secret for signing approval email tokens |
   | `GITHUB_COMMIT_TOKEN` | Fine-grained PAT, Contents: read/write on the repo |
   | `GITHUB_REPO_OWNER` | e.g. `Isachevygirl` |
   | `GITHUB_REPO_NAME` | e.g. `chevyroots` |

3. **NPM dependency** — the `@libsql/client` package must be installed for the
   Turso functions. Add it with:

   ```sh
   cd astro
   npm install @libsql/client
   ```

4. **Turso schema** — run `schema.sql` once against your Turso database:

   ```sh
   turso db shell chevyroots < netlify/functions/schema.sql
   ```

5. **DNS / domain** — point `chevyroots.com` at the Netlify site.

## Function inventory

| Path | Method | Purpose |
|---|---|---|
| `/api/subscribe` | POST | Newsletter signup — Loops + Resend welcome |
| `/api/contact` | POST | Contact form → email to hello@chevyroots.com |
| `/go/{retailer}/{slug}` | GET | Affiliate redirect with click logging |
| `/api/submit-build` | POST | Community build submission → moderation queue |
| `/api/submit-event` | POST | Event submission → moderation queue |
| `/.netlify/functions/approval-webhook` | GET | Handle approve/reject clicks from Crystal's email |
| `/.netlify/functions/send-approval-email` | POST (internal) | Helper used by submission pipelines |

## Redirect rules

The `netlify.toml` at `astro/netlify.toml` maps pretty URLs to the functions:

```toml
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[[redirects]]
  from = "/go/*"
  to = "/.netlify/functions/go/:splat"
  status = 200
```

## Local testing

```sh
cd astro
netlify dev
```

Then hit `http://localhost:8888/api/subscribe` etc. Each function uses the
same env vars locally via `.env` (which you should copy from `.env.example`).

## Security notes

- All user input is length-capped and angle-bracket-stripped before being
  passed to database or email APIs.
- Approval tokens are HMAC-SHA256 signed, 7-day expiry, single-use (JTI
  tracked in `consumed_tokens` table).
- Affiliate redirects log the click but never store full user-agent strings
  or PII.
- The contact form has a honeypot field (`_hp`) that real users don't see.
