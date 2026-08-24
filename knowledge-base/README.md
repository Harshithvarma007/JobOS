# Knowledge base index

This is the data index for JobOS. It exists so the agent (and you) can find any
piece of information in one lookup instead of scanning the whole repo. Every
file here is a **template** (`*.example.json`) — safe to commit, contains no
real data. Your real instance of each file lives at the mirrored path under
`../local-data/`, e.g.:

```
knowledge-base/profile/personal.example.json  →  local-data/profile/personal.json
knowledge-base/config/tiers.example.json      →  local-data/config/tiers.json
```

**Rule for the agent:** always read from `local-data/...`. Only fall back to
the `knowledge-base/...example.json` template when the matching `local-data`
file doesn't exist yet (which means onboarding hasn't been run for that
piece) — in that case, copy the template into `local-data/` and fill it in
by asking the user, per the onboarding flow in `../SKILL.md`.

## Profile (`profile/`)

Who the user is. Split by topic, not dumped into one file, so a partial
update (e.g. "add a new job") only touches one small file.

| File | Contains |
|---|---|
| `personal.example.json` | Name, contact info, links, work authorization, location |
| `experience.example.json` | Work history: company, title, dates, bullets, tech used |
| `education.example.json` | Degrees, institutions, dates |
| `skills.example.json` | Languages, frameworks, tools, domain areas |
| `preferences.example.json` | Target roles, locations, remote/relocation, comp expectations, exclusions |

## Config (`config/`)

How the user wants JobOS to behave. Set once during onboarding, editable any
time — just edit the JSON directly or ask the agent to change it.

| File | Contains |
|---|---|
| `tiers.example.json` | The tier scheme: how many tiers, and the exact rule that sorts a job into one |
| `apply_strategy.example.json` | Per tier: generate resume? cover letter? outreach? auto-submit? |
| `monitoring.example.json` | How often each source/tier gets re-checked |
| `sources.example.json` | Which job sources are enabled, their method (api / browser_agent), and which `.env` key holds their credential |

## Resumes & applications (`resumes/`, and `../local-data/applications/`)

`resumes/README.md` explains the expected base-resume format. Generated,
tailored per-application material (resume variant + cover letter) is written
to `local-data/applications/<company>-<role-slug>/`, one folder per
application — mirroring what gets logged as a row in the tracking sheet.

## The tracking sheet

Not a file in this repo — it's a live Google Sheet, the single source of
truth for every application's status. Its ID lives in `../.env` as
`GOOGLE_SHEET_ID` and is always reused. See `../SKILL.md` §"Tracking sheet"
for the schema and the reuse rule.
