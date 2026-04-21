# CLAUDE.md — Evan Gipson's Active Business Infrastructure

> **Purpose:** give any Claude Code session instant, accurate context about the
> projects, tools, and systems Evan is actively running — so we don't have to
> re-explain anything every time.
>
> **Keep this file current.** When something changes, update the relevant
> section. Longer-lived context (decisions, rationale) lives in
> `EVAN_BUSINESS_CONTEXT.md` alongside this file.

---

## Communication Style

- **Blunt, casual, direct.** No corporate tone. No over-explaining.
- **Call out bad logic directly.** If something is wrong or sketchy, say so.
- **Emojis: sparingly.** Use them when they actually add signal, not as decoration.
- **Flag issues before executing** when the user's request is premised on
  something that isn't true (stale assumption, missing info, deleted data).
  Don't silently work around it.
- **One step at a time** on big migrations. Propose → wait for approval → ship →
  verify → move on. See CRM Supabase migration (STEP 1 → STEP 5 in conversation
  history) for the pattern.
- **Show diffs before touching code** when possible.
- **Work locally only.** Don't commit or push unless the user explicitly says
  "commit" or "push." Evan handles deploys himself.

---

## About Evan

- 17 years old, runs an AI automation consulting business from Austin, TX.
- Email: `evangipson90@gmail.com` · Phone: `(737) 303-4474`
- GitHub: `EvanGipson17`
- Works directly with small local clients (real estate, property mgmt, etc.).
- Preferred tech: vanilla JS for solo stuff, React + Vite when a SPA makes
  sense, Python for one-off scripts, Supabase for any real data layer.

---

## Active projects

### 1. EG Client Manager (CRM) — `egclientmanager.com`

**What it is:** The tool Evan runs his entire consulting business from.
Single-file vanilla JS SPA with Supabase cloud sync and localStorage backup.
Features dashboard, clients, tasks, pipeline, revenue, AI Hub, settings.

**Where it lives:**

- **Local file:** `C:\Users\wwgip\evan-gipson-crm\index.html` (single file,
  ~2,300 lines, HTML + CSS + JS all inline).
- **Live site:** `https://egclientmanager.com` on Netlify.
- **NOT on GitHub.** No repo for the CRM.
- **Deploy mechanism:** manual drag-and-drop of `index.html` into Netlify
  dashboard. Not git-linked. Evan handles the upload himself.
- **Database:** Supabase project `dfdradtmbsdlgjttzbgk` (region: East US /
  `us-east-1`). URL: `https://dfdradtmbsdlgjttzbgk.supabase.co`.

**How to modify:**

- Edit `C:\Users\wwgip\evan-gipson-crm\index.html` directly.
- Test locally via the Claude Code preview server, then Evan drags the updated
  file into Netlify to deploy.
- Never commit or push — there's no repo.

**Data model (Supabase, Phase 1 of 2):**

- Tables: `profiles`, `clients`, `pipeline`, `ai_tools`, `activity`,
  `app_settings`.
- Hybrid schema: flat columns for scalars, `jsonb` for nested arrays inside
  a client (`tasks`, `logins`, `sequences`, etc.).
- Column names are snake_case; in-memory JS uses camelCase. Transforms live
  in `clientFromRow` / `clientToRow` etc. in `index.html`.
- `activity.body` is the column name (the JS key is `text`; renamed to avoid
  Postgres-type-name ambiguity).
- Single-user today. Every table has a nullable `owner_id uuid` and
  `profiles` table pre-wired so Phase 2 (real Supabase Auth + client portal +
  Stripe subscriptions + RLS) can be layered on without destructive migration.
- Phase 2 migration path is commented out at the bottom of the schema SQL.

**Credentials needed:**

- CRM unlock password (hardcoded constant, currently `#Juevon45` — change via
  Settings page or the `DEFAULT_PASSWORD` constant).
- Supabase account login (`evangipson90@gmail.com`).
- Supabase anon key — hardcoded in `index.html` (safe to expose; RLS is the
  security boundary in Phase 2).
- Supabase `service_role` key — stored in Evan's password manager, never in
  client-side code.
- Netlify login.
- Google login for Gmail/Forms (for mailto: links).

**Known state:**

- Active client: Blaga Ivancheva Trankaroff (Pacesetter Properties, Basic plan).
- 30 Austin-area leads (status='Lead') seeded `2026-04-20`.
- localStorage backup preserved at
  `eg_crm_data_v1_backup_preMigration_2026-04-18` — never read or written by
  the app.

---

### 2. Pricing Page (demo)

**URL:** `https://evangipson17.github.io/ai-business-demos/evan-gipson-ai/`

**What it is:** the public-facing pricing page for Evan Gipson AI Automation.
Static HTML/CSS, no build step.

**Repo:** `github.com/EvanGipson17/ai-business-demos` (subfolder
`evan-gipson-ai/`). Deploys via GitHub Pages.

**Local path:** TODO — confirm where this repo is cloned locally (if at all).

**How to modify:** edit the HTML/CSS in the `evan-gipson-ai/` subfolder,
push to GitHub, Pages auto-deploys.

**Credentials needed:** GitHub login (`EvanGipson17`).

---

### 3. Pacesetter Demo

**URL:** `https://evangipson17.github.io/ai-business-demos/pacesetter-properties/`

**What it is:** live demo site showcasing AI automation work for Pacesetter
Properties (Blaga's real-estate business). Same repo as the pricing page,
different subfolder.

**Repo:** `github.com/EvanGipson17/ai-business-demos` (subfolder
`pacesetter-properties/`). GitHub Pages.

**Local path:** TODO — confirm where this repo is cloned locally (same repo
as pricing page).

**How to modify:** edit, push, auto-deploys.

**Credentials needed:** GitHub login (`EvanGipson17`).

---

### 4. Form Router (`eg-form-router`)

**What it is:** headless Python script that auto-responds to new Google
Forms intake submissions with personalized onboarding emails. See
`C:\Users\wwgip\eg-form-router\README.md` for full details.

**Repo:** `github.com/EvanGipson17/eg-form-router` (private).

**Local path:** `C:\Users\wwgip\eg-form-router\`.

**Deployment:** Manus — scheduled cron, every 3 days. Located at
`/home/ubuntu/eg-form-router/` on the Manus server. No public URL (it's a
cron, not a web service).

**Stack:** Python 3.9+, single dep `python-dotenv`, uses the `gws` CLI
from Google Workspace for form reads and Gmail SMTP with an App Password
for sends.

**Three Google Forms it connects:**

- **Intake form** — short yes/no questionnaire clients fill out first.
  Form ID `1EZfb7yFMudKzYy6OtX7SBMTAQlx63WU7yBBld8F3-xY`.
  Public `/viewform` URL: TODO — confirm.
- **Full Setup Portal** — detailed form sent to clients after the intake
  router fires.
  URL: `https://docs.google.com/forms/d/e/1FAIpQLSdEohGvs6ruK-zK7V_uZuwK3FFYk27MzguGZ-I-O2FDPXALLA/viewform`.
- **Basic Plan form** — entry point for the $150/mo Basic plan sign-up.
  URL: TODO — confirm.

**How to modify:** edit `form_router.py` locally, commit, push to GitHub,
then pull on Manus and re-run. Or push and trigger a manual run.

**Credentials needed:**

- Gmail App Password for `evangipson90@gmail.com` (set as env var
  `GMAIL_APP_PASSWORD` — 16 chars, no spaces required at runtime).
- `gws` CLI pre-authenticated via Google OAuth.
- Manus account login.

---

### 5. OpenClaw — 24/7 personal AI assistant

**What it is:** Evan's always-on AI assistant running on his desktop.
Responds to commands via Telegram bot. Powers all on-the-go agent tasks.

**Where it lives:** `C:\Users\wwgip\.openclaw\` (hidden folder in home
directory).

**Telegram bot:** `@EvanGipsonAI_bot`.

**Model:** `anthropic/claude-sonnet-4-6`. API keys managed at
`platform.claude.com`.

**How to start:** started manually when Evan boots his computer. No auto-run
at login today.

**Credentials needed:**

- Anthropic API key (from `platform.claude.com`).
- Telegram bot token (for `@EvanGipsonAI_bot`).

---

### 6. HQ Command Center (this repo)

**What it is:** local dashboard for managing everything else. Shows a grid
of tools (CRM, Form Router, Deal Flipper, etc.) that link out to the actual
projects. This is the landing page for "what am I working on."

**Where it lives:** `C:\Users\wwgip\hq-command-center\`.

**Repo:** `github.com/EvanGipson17/hq-command-center`.

**Stack:** Vite + React + React Router + Vercel.

**Live URL:** TODO — confirm the Vercel URL.

**How to modify:**

- Add/edit cards in `src/data/tools.js` (single source of truth).
- Add new categories in `src/data/categories.js`.
- Add new dedicated tool pages in `src/pages/`, register the route in
  `src/App.jsx`, and set the tool's `href` to the new route.
- `npm run dev` for local, `npm run build` for production.

**Current tools on the dashboard:**

- **Deal Flipper** (active, `/deal-flipper`) — marketplace arbitrage
  scanner with a local Flask API.
- **Form Router** (active, `/form-router`) — hub page linking to the
  eg-form-router infrastructure.
- **Investment Scout, Market Pulse, Deal Alerts, Research Assistant,
  Prompt Library** — coming-soon placeholders.

**Credentials needed:** GitHub + Vercel logins.

---

## Auto-context system

When Evan makes a meaningful decision or learns something worth remembering
long-term, he can log it from any terminal:

```powershell
context "Decided to migrate CRM to Supabase instead of Firebase"
```

This runs `update_context.py` in this repo, which appends a dated entry to
the `## Decisions Log` section of `EVAN_BUSINESS_CONTEXT.md`, then commits
and pushes to GitHub.

The `context` function lives in Evan's PowerShell profile. Setup details
are in `update_context.py` and `README.md` of this repo.

---

## Quick index

| Project | Local path | Live URL | Repo |
|---|---|---|---|
| CRM | `C:\Users\wwgip\evan-gipson-crm\` | `egclientmanager.com` | *(none — Netlify drag-drop)* |
| Pricing Page | TODO | `evangipson17.github.io/ai-business-demos/evan-gipson-ai/` | `EvanGipson17/ai-business-demos` |
| Pacesetter Demo | TODO | `evangipson17.github.io/ai-business-demos/pacesetter-properties/` | `EvanGipson17/ai-business-demos` |
| Form Router | `C:\Users\wwgip\eg-form-router\` | *(no public URL — Manus cron)* | `EvanGipson17/eg-form-router` |
| OpenClaw | `C:\Users\wwgip\.openclaw\` | *(Telegram: @EvanGipsonAI_bot)* | *(n/a — local only)* |
| HQ Command Center | `C:\Users\wwgip\hq-command-center\` | TODO (Vercel) | `EvanGipson17/hq-command-center` |

---

*Last updated: 2026-04-20.*
