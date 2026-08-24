"""Template client for any other REST job-search API (Openings MCP, JobSpy,
a RapidAPI job board, YC Jobs API, etc.). Duplicate + adjust per source, or
point this generic version directly at a source config entry from
local-data/config/sources.json.
"""
import requests

from config import env
from sources.base import RawJob


def search(source_config: dict, query: str, locations: list[str] | None = None, limit: int = 50) -> list[RawJob]:
    """source_config is one entry from config/sources.json, e.g.:
    {"name": "...", "method": "api", "env_key": "...", "endpoint": "..."}
    """
    api_key = env(source_config["env_key"]) if source_config.get("env_key") else None
    if source_config.get("env_key") and not api_key:
        raise RuntimeError(f"{source_config['env_key']} not set in .env")

    resp = requests.get(
        source_config["endpoint"],
        headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
        params={"q": query, "locations": ",".join(locations or []), "limit": limit},
        timeout=30,
    )
    resp.raise_for_status()
    listings = resp.json().get("results", resp.json() if isinstance(resp.json(), list) else [])
    return [_to_raw_job(item, source_config["name"]) for item in listings]


def _to_raw_job(item: dict, source_name: str) -> RawJob:
    return RawJob(
        company=item.get("company", ""),
        title=item.get("title", ""),
        location=item.get("location", ""),
        remote=item.get("remote", ""),
        salary=item.get("salary", ""),
        description=item.get("description", ""),
        url=item.get("url", ""),
        source=source_name,
        ats=item.get("ats", ""),
        company_url=item.get("company_url", ""),
        posted_at=item.get("posted_at", ""),
    )
