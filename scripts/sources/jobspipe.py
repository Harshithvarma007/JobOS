"""JobsPipe client.

NOTE: this is a template against a typical REST job-search API shape
(POST a search query, get back a list of listings). JobsPipe's actual
endpoint/response schema isn't verified here — check your JobsPipe API docs
and adjust ENDPOINT / the request body / the field mapping in `_to_raw_job`
to match. The rest of JobOS (dedupe, tiering, sheet sync) doesn't care how
this function gets its data, only that it returns a list of RawJob.
"""
import requests

from config import env
from sources.base import RawJob

ENDPOINT = "https://api.jobspipe.com/v1/search"  # verify against JobsPipe's docs


def search(query: str, locations: list[str] | None = None, limit: int = 50) -> list[RawJob]:
    api_key = env("JOBSPIPE_API_KEY")
    if not api_key:
        raise RuntimeError("JOBSPIPE_API_KEY not set in .env")

    resp = requests.post(
        ENDPOINT,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"query": query, "locations": locations or [], "limit": limit},
        timeout=30,
    )
    resp.raise_for_status()
    listings = resp.json().get("results", [])
    return [_to_raw_job(item) for item in listings]


def _to_raw_job(item: dict) -> RawJob:
    return RawJob(
        company=item.get("company", ""),
        title=item.get("title", ""),
        location=item.get("location", ""),
        remote=item.get("remote", ""),
        salary=item.get("salary", ""),
        description=item.get("description", ""),
        url=item.get("url", ""),
        source="JobsPipe",
        ats=item.get("ats", ""),
        company_url=item.get("company_url", ""),
        posted_at=item.get("posted_at", ""),
    )
