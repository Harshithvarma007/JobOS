---
name: jobos
description: Run an end-to-end job search — search multiple job sources, score and tier every listing, track everything in one Google Sheet, and draft tailored resumes/cover letters/outreach for the tiers configured for it. Use when the user wants to find jobs, check for new listings, log/update an application, or work on their job search.
---

# JobOS

You are running the user's job search. Read this file fully before acting —
it is the single routing document: it tells you where every piece of data
lives and exactly what to do with it. Data itself lives in
`knowledge-base/` (shareable templates) and `local-data/` (this user's real
instance, git-ignored) — see `knowledge-base/README.md` for the index of
those files.

## 0. Check whether onboarding has run

Look for `local-data/config/tiers.json`. If it (or any of the other
`local-data/config/*.json` / `local-data/profile/*.json` files) doesn't
exist, this is a first run — go to **§1 Onboarding**. Otherwise skip to
**§2 Workflow**.

## 1. Onboarding (first run only)

Do this conversationally, one topic at a time — don't dump every question
at once. For each file below: copy the matching `knowledge-base/*.example.json`
template to `local-data/...json`, then ask the user and fill it in for real
(swap Ask User Question style prompts for whatever your interface offers).

1. **Profile** (`local-data/profile/`) — ask for what's needed to fill
   `personal.json`, `experience.json`, `education.json`, `skills.json`,
   `preferences.json`. If the user already has a resume file, offer to read
   it and pre-fill from that instead of asking everything from scratch, then
   confirm the extracted details with them.
2. **Tier scheme** (`local-data/config/tiers.json`) — ask how they want
   applications categorized: by fit score, by company tier list, by
   compensation band, or something custom. `tiers.example.json` shows all
   three shapes under `alternate_schemes`.
3. **Apply strategy per tier** (`local-data/config/apply_strategy.json`) —
   for each tier, ask: generate a tailored resume? a cover letter? draft
   outreach to someone at the company (email / LinkedIn connection note)?
   Should submission ever be fully automatic, or always paused for review?
   Default to **paused for review** unless they explicitly ask for
   auto-submit on a given tier.
4. **Monitoring** (`local-data/config/monitoring.json`) — ask how often to
   re-check sources: same cadence for everything (uniform), higher cadence
   for the top tier only (tiered), or only when they explicitly ask
   (on-demand). Also ask for any custom instructions (e.g. "only alert me
   for Series A-C startups", "skip anything under 20 employees").
5. **Sources** (`local-data/config/sources.json`) — ask which sources they
   have access to. For anything with `method: "api"`, ask for the API key
   and save it to `.env` (never in this JSON file). For `browser_agent`
   sources (Wellfound, Instahyre, LinkedIn), confirm the Claude in Chrome
   extension is installed and they're logged into those sites. For a source
   not already listed, use the `custom-api-source` template entry.
6. **Tracking sheet** — check `.env` for `GOOGLE_SHEET_ID`.
   - If it's already set: reuse that sheet. Never create another one.
   - If it's empty: create one Google Sheet (via the Google Drive MCP
     connection, or ask the user for an existing sheet to reuse), title it
     something like "JobOS Tracker", write the header row (see §3 schema
     below), then save its ID to `GOOGLE_SHEET_ID` and its URL to
     `GOOGLE_SHEET_URL` in `.env`. From this point on, every session reuses
     it — check `.env` first, always.
7. Confirm the whole config back to the user in a short summary before
   running the first real search.

## 2. Workflow (every run)

1. **Load config.** Read `local-data/config/{tiers,apply_strategy,monitoring,sources}.json`
   and `local-data/profile/*.json`.
2. **Search each enabled source:**
   - `method: "api"` — use `scripts/sources/<name>.py` (or `generic_api.py`
     against the source's config entry), or call `scripts/run_daily.py` to
     do this mechanically for all API sources at once.
   - `method: "mcp_tool"` (e.g. Indeed) — call the corresponding built-in
     MCP tool directly.
   - `method: "browser_agent"` (Wellfound, Instahyre, LinkedIn Jobs, company
     career pages) — use the Claude in Chrome tools to navigate and read
     listings live. Don't use LinkedIn browsing as a primary discovery
     strategy; prefer it for filling gaps and for outreach.
3. **Dedupe.** For every listing found, compute/check its hash (company +
   title + location) against `local-data/db/jobs.db` (`scripts/db.py`).
   Skip anything already present.
4. **Score & tier.** For each new listing, judge fit against
   `local-data/profile/*.json` (0-100, with a one-line reason), then call
   `scripts/tiering.assign_tier(...)` to map that score (or comp/company,
   depending on scheme) to a tier per `local-data/config/tiers.json`. Insert
   into `jobs.db` with `tier`, `fit_score`, and `reason` filled in.
5. **Act per tier**, per `apply_strategy.json`:
   - If the tier calls for a resume: read `profile/experience.json` +
     `profile/skills.json` + the job description, write a tailored resume
     variant into `local-data/applications/<company>-<role>/` (use
     `scripts/apply_pipeline.application_folder(...)` for the path).
   - If it calls for a cover letter: same folder, same judgment call.
   - If it calls for outreach: find a relevant person at the company
     (via LinkedIn/company site), draft an email (Gmail MCP `create_draft`)
     or a LinkedIn connection note. Draft only — do not send/connect
     without the user's go-ahead, unless that tier has `auto_submit: true`.
   - Record what you did with `scripts/apply_pipeline.record_application(...)`.
6. **Sync to the sheet.** Push every new/changed row to the single tracking
   sheet (`GOOGLE_SHEET_ID` from `.env`) — either via `scripts/sheet_sync.py`
   or directly through the Google Drive MCP connection. Never create a
   second sheet.
7. **Report back**: what's new, by tier, and what (if anything) is waiting
   on the user's review before it gets sent/submitted.

## 3. Tracking sheet schema

One row per job, matching `db/schema.sql` / `scripts/sheet_sync.HEADER`:

```
id | company | title | location | remote | salary | tier | source | url |
status | fit_score | reason | resume_version | cover_letter |
outreach_sent | applied_at | discovered_at
```

`status` moves through: `new → applied → outreach_sent → interviewing →
rejected / offer`. Update it in place as things change — don't append a new
row for a status change on an existing job.

## 4. Rules

- **One sheet, always.** Check `.env` for `GOOGLE_SHEET_ID` before ever
  creating a sheet. If it's set, that's the sheet — full stop.
- **Never auto-submit or auto-send by default.** Resumes, cover letters,
  and outreach are drafts until the user says go, unless they explicitly
  configured `auto_submit: true` for that tier during onboarding.
- **Don't re-litigate config every run.** Onboarding answers are durable —
  only ask again if the user brings it up, or a config file is missing.
- **Keep `local-data/` out of git.** It's already in `.gitignore`; don't
  add real personal data anywhere under `knowledge-base/`.

## 5. Requirements this skill assumes

- Google Drive connected (MCP) — tracking sheet + resume/cover-letter storage.
- Gmail connected (MCP) — only if outreach is configured to draft emails.
- Claude in Chrome extension, logged into any `browser_agent` sources in use.
- API keys in `.env` for any `method: "api"` source that's enabled.
- Python 3.10+ + `pip install -r requirements.txt` only if you want
  `scripts/run_daily.py` runnable outside a Claude session (e.g. cron).
