# Resumes

Put your base resume here in your real instance (`local-data/resumes/`), not
in this template folder. Any format works (`.tex`, `.pdf`, `.md`, `.docx`) as
long as the underlying content (roles, bullets, skills) also exists in
`profile/experience.example.json` → `local-data/profile/experience.json`,
since that's what the agent reads to tailor a variant per application — it
doesn't parse PDFs.

Tailored, per-application variants are not stored here: they're generated
into `local-data/applications/<company>-<role-slug>/resume.*` alongside that
application's cover letter, one folder per application.
