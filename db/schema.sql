CREATE TABLE IF NOT EXISTS jobs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    company             TEXT NOT NULL,
    title               TEXT NOT NULL,
    location            TEXT,
    remote              TEXT,
    salary              TEXT,
    tier                TEXT,                 -- derived from fit_score / comp / company list per config/tiers.json
    description         TEXT,
    url                 TEXT,
    source              TEXT,                 -- JobsPipe / Openings / Indeed / Wellfound / Instahyre / LinkedIn / etc.
    ats                 TEXT,                 -- Greenhouse / Lever / Ashby / Workday / etc.
    company_url         TEXT,
    posted_at           TEXT,
    discovered_at       TEXT DEFAULT (datetime('now')),
    hash                TEXT UNIQUE,          -- dedup key: company+title+location
    fit_score           INTEGER,              -- 0-100
    reason              TEXT,                 -- why it fits / was tiered this way
    status              TEXT DEFAULT 'new',   -- new / applied / outreach_sent / interviewing / rejected / offer
    resume_version      TEXT,                 -- path/filename of the tailored resume used, if any
    cover_letter        TEXT,                 -- path/filename of the cover letter used, if any
    outreach_sent       INTEGER DEFAULT 0,    -- 0/1
    outreach_notes      TEXT,
    applied_at          TEXT,
    sheet_synced_at     TEXT                  -- last time this row was pushed to the tracking sheet
);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_tier ON jobs(tier);
CREATE INDEX IF NOT EXISTS idx_jobs_hash ON jobs(hash);
