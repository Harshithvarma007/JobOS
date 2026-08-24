"""SQLite helpers for the local job dedupe/tracking database."""
import hashlib
import sqlite3
from datetime import datetime, timezone

from config import DB_PATH, REPO_ROOT


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    schema = (REPO_ROOT / "db" / "schema.sql").read_text()
    with connect() as conn:
        conn.executescript(schema)


def job_hash(company: str, title: str, location: str) -> str:
    key = f"{company.strip().lower()}|{title.strip().lower()}|{(location or '').strip().lower()}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def job_exists(conn: sqlite3.Connection, hash_: str) -> bool:
    row = conn.execute("SELECT 1 FROM jobs WHERE hash = ?", (hash_,)).fetchone()
    return row is not None


def insert_job(conn: sqlite3.Connection, job: dict) -> int:
    """job must contain at least company, title. hash is computed if absent."""
    job = dict(job)
    job.setdefault(
        "hash", job_hash(job["company"], job["title"], job.get("location", ""))
    )
    if job_exists(conn, job["hash"]):
        return -1
    cols = ", ".join(job.keys())
    placeholders = ", ".join("?" for _ in job)
    cur = conn.execute(
        f"INSERT INTO jobs ({cols}) VALUES ({placeholders})", tuple(job.values())
    )
    conn.commit()
    return cur.lastrowid


def update_job(conn: sqlite3.Connection, job_id: int, **fields) -> None:
    if not fields:
        return
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    conn.execute(
        f"UPDATE jobs SET {set_clause} WHERE id = ?", (*fields.values(), job_id)
    )
    conn.commit()


def jobs_needing_sync(conn: sqlite3.Connection):
    return conn.execute(
        "SELECT * FROM jobs WHERE sheet_synced_at IS NULL "
        "OR sheet_synced_at < discovered_at"
    ).fetchall()


def mark_synced(conn: sqlite3.Connection, job_id: int) -> None:
    update_job(conn, job_id, sheet_synced_at=datetime.now(timezone.utc).isoformat())
