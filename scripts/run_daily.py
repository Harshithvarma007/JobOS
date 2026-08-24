"""Mechanical, unattended collection step — safe to run from cron.

Handles only the deterministic part of the pipeline: query every enabled
*api*-method source (config/sources.json), dedupe against jobs.db, insert
new listings as tier=unscored, and sync to the tracking sheet.

It deliberately does NOT: score fit (needs judgment), touch browser_agent
sources (Wellfound/Instahyre/LinkedIn — need the Claude in Chrome extension,
which only exists inside a live Claude Code session), or generate/apply
anything. Run the JobOS skill inside Claude Code for those steps — see
SKILL.md.
"""
import sys

import db as dbmod
import sheet_sync
from config import load_preferences, load_sources


def main() -> int:
    dbmod.init_db()
    conn = dbmod.connect()
    prefs = load_preferences()
    query = " OR ".join(prefs.get("target_roles", []))
    locations = prefs.get("locations", [])

    inserted = 0
    for source in load_sources():
        if not source.get("enabled") or source.get("method") != "api":
            continue
        try:
            if source["name"] == "JobsPipe":
                import sources.jobspipe as jobspipe

                results = jobspipe.search(query, locations)
            else:
                import sources.generic_api as generic_api

                results = generic_api.search(source, query, locations)
        except Exception as e:  # noqa: BLE001 — log and keep going with other sources
            print(f"[{source['name']}] search failed: {e}", file=sys.stderr)
            continue

        for raw in results:
            row_id = dbmod.insert_job(conn, raw.as_row())
            if row_id != -1:
                inserted += 1

    print(f"Inserted {inserted} new job(s).", file=sys.stderr)

    try:
        synced = sheet_sync.sync_pending(conn)
        print(f"Synced {synced} row(s) to the tracking sheet.", file=sys.stderr)
    except RuntimeError as e:
        print(f"Sheet sync skipped: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
