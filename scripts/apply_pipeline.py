"""Bookkeeping for the apply step. The creative work — tailoring a resume to
a job description, writing a cover letter, drafting outreach — is judgment
the agent does live (reading profile/*.json and the job description) inside
a Claude Code session. This module just records the result: it creates the
per-application folder and updates jobs.db so sheet_sync picks up the change.

Typical flow (driven by the agent, per SKILL.md):
  1. agent decides tier's apply_strategy calls for a resume/cover letter
  2. agent writes the tailored files itself
  3. agent calls record_application(...) with the paths it wrote
"""
from pathlib import Path
import re

from config import LOCAL_DATA
import db as dbmod


def application_folder(company: str, title: str) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "-", f"{company}-{title}".lower()).strip("-")
    folder = LOCAL_DATA / "applications" / slug
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def record_application(
    conn,
    job_id: int,
    *,
    resume_version: str | None = None,
    cover_letter: str | None = None,
    outreach_sent: bool = False,
    outreach_notes: str = "",
    status: str = "applied",
    applied_at: str | None = None,
) -> None:
    from datetime import datetime, timezone

    fields = {"status": status}
    if resume_version:
        fields["resume_version"] = resume_version
    if cover_letter:
        fields["cover_letter"] = cover_letter
    if outreach_sent:
        fields["outreach_sent"] = 1
    if outreach_notes:
        fields["outreach_notes"] = outreach_notes
    if status == "applied":
        fields["applied_at"] = applied_at or datetime.now(timezone.utc).isoformat()
    dbmod.update_job(conn, job_id, **fields)
