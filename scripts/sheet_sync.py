"""Sync the local jobs.db to the single tracking Google Sheet.

Reuse rule: GOOGLE_SHEET_ID in .env is the only source of truth for which
sheet to write to. This module never creates a new sheet if that variable is
already set — it only creates one the very first time, then tells you to
save the ID back to .env.

This is the standalone path (service-account auth, for cron / scripts/run_daily.py).
When running live inside Claude Code, the agent can instead update the sheet
directly through the Google Drive MCP connection — see SKILL.md.
"""
import sys

from config import env

HEADER = [
    "id", "company", "title", "location", "remote", "salary", "tier",
    "source", "url", "status", "fit_score", "reason", "resume_version",
    "cover_letter", "outreach_sent", "applied_at", "discovered_at",
]


def _open_sheet():
    import gspread
    from google.oauth2.service_account import Credentials

    creds_path = env("GOOGLE_SERVICE_ACCOUNT_JSON")
    sheet_id = env("GOOGLE_SHEET_ID")
    if not creds_path:
        raise RuntimeError(
            "GOOGLE_SERVICE_ACCOUNT_JSON not set in .env — required for standalone sheet sync."
        )
    if not sheet_id:
        raise RuntimeError(
            "GOOGLE_SHEET_ID not set in .env. Create the sheet once (via the agent, using "
            "the Google Drive MCP connection, or manually) and save its ID here before "
            "running sync — JobOS will not create one from this script to avoid ever "
            "creating a second sheet by accident."
        )
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id).sheet1


def sync_pending(conn) -> int:
    """Push every job row not yet synced (or updated since last sync) to the
    sheet, then mark it synced. Returns the number of rows written."""
    import db as dbmod

    rows = dbmod.jobs_needing_sync(conn)
    if not rows:
        return 0

    ws = _open_sheet()
    existing_header = ws.row_values(1)
    if existing_header != HEADER:
        if not existing_header:
            ws.append_row(HEADER)
        # If a header already exists but differs, leave it alone — the sheet
        # is user-owned and may have been reordered/renamed intentionally.
        # Fall back to appending in JobOS's own column order below regardless.

    existing_ids = {row[0] for row in ws.get_all_values()[1:] if row}
    for row in rows:
        values = [str(row[col]) if row[col] is not None else "" for col in HEADER]
        if str(row["id"]) in existing_ids:
            cell = ws.find(str(row["id"]))
            ws.update(f"A{cell.row}:{chr(64 + len(HEADER))}{cell.row}", [values])
        else:
            ws.append_row(values)
        dbmod.mark_synced(conn, row["id"])
    return len(rows)


if __name__ == "__main__":
    import db as dbmod

    conn = dbmod.connect()
    n = sync_pending(conn)
    print(f"Synced {n} row(s) to the tracking sheet.", file=sys.stderr)
