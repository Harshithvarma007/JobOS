# JobOS

~NO~ AI was harmed will building this

A Claude Code skill that runs your job search end-to-end: search multiple job sources, score and tier every listing against your profile, track everything in one Google Sheet, and (for the tiers you choose) draft tailored resumes, cover letters, and outreach.

JobOS is a **template**. Nothing in this repo contains anyone's personal data — your real profile, resume, API keys, and Google Sheet link live in `local-data/` and `.env`, both git-ignored. Clone it, run the onboarding flow once, and it becomes your own private job-search system.

## What it does

1. **Search** — pulls new listings from every source you enable: API-based aggregators (JobsPipe, Openings, JobSpy, or any REST job-search API you have a key for) and browser-based sources with no public API (Wellfound, Instahyre, LinkedIn Jobs) via the Claude in Chrome extension.
2. **Dedupe** — every listing is hashed (company + title + location) against `local-data/db/jobs.db` so re-runs only surface what's new.
3. **Score & tier** — each new listing is scored against your profile and sorted into the tiers you defined during onboarding (e.g. S/A/B by fit, or by comp band, or by company list — your choice).
4. **Track** — every job, its tier, and its status lives in **one** Google Sheet, the single source of truth. JobOS reads `GOOGLE_SHEET_ID` from `.env` and always reuses that sheet — it creates one only the first time that variable is empty, and never again.
5. **Apply** — for the tiers you configured for action: generates a tailored resume and (if configured) a cover letter, drafts outreach to relevant people at the company (email draft or a LinkedIn connection note) for the tiers you enabled outreach on, and always pauses for your review before anything is actually sent or submitted, unless you explicitly turned auto-submit on.

## Requirements

- **Claude Code**, with this repo installed as a skill (see Install below).
- **Google Drive** connected in Claude Code (MCP) — used to create/read/update the tracking Google Sheet and to store generated resumes/cover letters.
- **Gmail** connected in Claude Code (MCP) — optional, only needed if you want outreach drafted as Gmail drafts.
- **Claude in Chrome** extension, connected and logged into the sites you want scraped/applied to (Wellfound, Instahyre, LinkedIn, individual company career pages) — required for any source without a public API, and for applying on sites without one.
- **Python 3.10+** for the mechanical scripts (`pip install -r requirements.txt`) — only needed if you want the API-based collection step (`scripts/run_daily.py`) to be runnable outside a Claude session (e.g. via cron). Everything else works purely through Claude Code.
- API keys for whichever job-search APIs you use (JobsPipe, Openings MCP, JobSpy, RapidAPI job boards, etc.) — go in `.env`, never in the repo.

## Install

```bash
git clone <this-repo> ~/.claude/skills/jobos
```

Or, inside an existing project, clone it to `.claude/skills/jobos` in that project. Claude Code will pick up `SKILL.md` automatically.

## First run

Tell Claude: *"set up JobOS"* or just start using it — `SKILL.md` checks whether `local-data/` is populated and, if not, walks you through onboarding: your profile, your tier scheme, how hard to work each tier, how much to monitor, which sources you have access to, and where the tracking sheet should live. See `SKILL.md` for the exact flow.

## Layout

```
JobOS/
├── SKILL.md                 # the skill: routing + full workflow the agent follows
├── knowledge-base/          # TEMPLATE knowledge base (safe to share) — *.example.json + docs
├── local-data/               # YOUR real instance: profile, config, db, resumes (git-ignored)
├── scripts/                  # Python: db, tiering, sheet sync, source clients, apply pipeline
├── db/schema.sql             # SQLite schema for the local job dedupe/tracking database
├── .env.example               # every env var JobOS reads, with placeholders
└── .gitignore
```

## Design notes

- **One sheet, always.** JobOS never creates a second tracking sheet for an existing instance. `GOOGLE_SHEET_ID` in `.env` is the only source of truth for which sheet to use.
- **Submission is never fully autonomous by default.** Drafts (resumes, cover letters, outreach messages, application form fills) are prepared and shown to you; JobOS waits for explicit go-ahead before sending or submitting, unless you deliberately enable auto-submit for a tier during onboarding.
- **Mechanical vs. agentic split.** Fetching from a REST API, deduping, and writing to SQLite/Sheets are deterministic — those live in `scripts/` and can run unattended (cron). Scoring fit, browsing sites with no API, tailoring resumes, and writing outreach require judgment — those happen live, inside a Claude Code session running this skill.
