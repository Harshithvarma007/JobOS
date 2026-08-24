"""Shared paths and config loading for JobOS scripts."""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_DATA = REPO_ROOT / "local-data"
KNOWLEDGE_BASE = REPO_ROOT / "knowledge-base"
DB_PATH = LOCAL_DATA / "db" / "jobs.db"

load_dotenv(REPO_ROOT / ".env")


def local_or_template(relative_path: str) -> Path:
    """Return the local-data path if it exists, else the matching
    knowledge-base/*.example.json template (read-only fallback)."""
    local = LOCAL_DATA / relative_path
    if local.exists():
        return local
    template_name = relative_path.replace(".json", ".example.json")
    template = KNOWLEDGE_BASE / template_name
    if template.exists():
        return template
    raise FileNotFoundError(
        f"Neither local-data/{relative_path} nor its knowledge-base template exists. "
        "Run onboarding first (see SKILL.md)."
    )


def load_json(relative_path: str):
    with open(local_or_template(relative_path)) as f:
        return json.load(f)


def load_tiers():
    return load_json("config/tiers.json")


def load_apply_strategy():
    return load_json("config/apply_strategy.json")


def load_monitoring():
    return load_json("config/monitoring.json")


def load_sources():
    return load_json("config/sources.json")


def load_preferences():
    return load_json("profile/preferences.json")


def env(key: str, default=None):
    return os.environ.get(key, default)
