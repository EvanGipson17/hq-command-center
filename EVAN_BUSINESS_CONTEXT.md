# Evan Gipson — Business Context

> **Purpose:** long-lived context any AI assistant can read to understand
> Evan's business, the decisions he's made, and why. Complements `CLAUDE.md`
> (which is the current-state reference).
>
> **The Decisions Log below is appended to automatically.** Use the `context`
> command from any terminal:
>
> ```powershell
> context "Decided to switch CRM database from Firebase to Supabase"
> ```
>
> That runs `update_context.py` in this repo, which appends a dated entry
> to the bottom of the Decisions Log (chronological order, newest last)
> and commits + pushes to GitHub.

---

## Who

**Evan Gipson** — 17, Austin TX, runs a one-person AI automation consulting
business. Works directly with small local clients (real estate, property
management, etc.). Builds his own tools when off-the-shelf doesn't fit.

Contact: `evangipson90@gmail.com` · `(737) 303-4474`
GitHub: `EvanGipson17`

---

## Operating principles

- **Ship personal tools fast, clients' tools carefully.** Internal tooling
  can be scrappy; client-facing work has to feel solid.
- **Vanilla-first for solo projects.** React + Vite when a SPA genuinely
  helps. Python for one-off scripts. Supabase for any real data layer.
- **Offline-first with cloud sync.** LocalStorage is the backup, cloud is
  the source of truth. Never destroy the local backup in a migration.
- **Additive migrations only.** If a future phase would force a destructive
  schema change, redesign now.
- **One step at a time on anything risky.** Propose, wait, ship, verify,
  move on.

---

## Stack preferences

- **Frontend SPA:** Vite + React + React Router. Single `data.js` file as
  source of truth for static content. No state-management libraries unless
  actually needed.
- **Single-file apps:** vanilla HTML/CSS/JS in one `index.html` (see CRM).
- **Backend data:** Supabase. Hybrid schema (flat columns + jsonb) for
  anything with nested lists.
- **Auth (future):** Supabase Auth with RLS. Roles `admin` and `client`.
- **Payments (future):** Stripe, with subscription lifecycle tracked via
  webhooks.
- **Email (current):** Gmail SMTP + App Passwords for headless sends.
- **Automation (current):** Python scripts, scheduled via cron on Manus.
- **Hosting:** Netlify (drag-drop), GitHub Pages (static sites), Vercel
  (Vite apps), Manus (cron jobs).

---

## Business model

- **Basic plan:** $150/month — light-touch AI automation.
- **Standard plan:** $300/month.
- **Professional plan:** $500/month.
- **Max plan:** $700/month.
- **One-Time:** $1,500 flat for scoped project work.
- **Custom:** priced per client.

Sales funnel stages: Lead → Contacted → Meeting Booked → Proposal Sent →
Negotiating → Closed Won / Closed Lost.

---

## Decisions Log

<!-- APPEND NEW ENTRIES BELOW. Format: `- **YYYY-MM-DD** — note` -->
<!-- The `context` command and update_context.py will append here automatically. -->

- **2026-04-17** — Built EG Client Manager v1 as single-file vanilla JS with localStorage persistence. Password-locked (`EvanCRM2026`, later rotated to `#Juevon45`). White/navy/gold design, HubSpot-style.
- **2026-04-17** — Started the CRM migration from localStorage to Supabase. Single-user Phase 1 first, full client portal + Auth + Stripe in Phase 2. Region: `us-east-1` (closest mature Supabase region to Austin).
- **2026-04-18** — Designed Supabase schema to be Phase-1 functional but Phase-2 ready: nullable `owner_id` + `auth_user_id` on every table, `profiles` table pre-created, Stripe columns pre-added as nullable. Phase 2 migration is purely additive — no destructive changes.
- **2026-04-18** — Wiped the incomplete Blaga + TEST User Alpha rows from Supabase. Keeping ai_tools defaults. Decided Blaga will re-enter via the Phase 2 client portal, but re-seeded her full data on 2026-04-20 for active-client continuity.
- **2026-04-18** — Shipped Supabase migration §1 (load path) and §2 (writes via diff-based sync with 300ms debounce + fetch keepalive for tab-close safety). Writes now round-trip Supabase with localStorage as simultaneous backup.
- **2026-04-20** — Added `website` and `industry` columns to `clients` table in Supabase. Added `Lead` as a 4th status enum. Seeded 30 Austin-area leads.
- **2026-04-20** — Bootstrapped the auto-context system: `update_context.py` + PowerShell `context` function. Future decisions get logged here automatically.
- **2026-04-20** — Verified the auto-context system end-to-end: append + commit + push.
- **2026-04-20** — Killed Deal Flipper project. Removing from HQ Command Center to keep dashboard focused on active business.
- **2026-04-21** — Built client portal on egclientmanager.com — April 21 2026
