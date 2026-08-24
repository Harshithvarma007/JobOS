"""Common shape every API-based source client returns, so run_daily.py and
db.insert_job can treat them uniformly."""
from dataclasses import dataclass, field


@dataclass
class RawJob:
    company: str
    title: str
    location: str = ""
    remote: str = ""
    salary: str = ""
    description: str = ""
    url: str = ""
    source: str = ""
    ats: str = ""
    company_url: str = ""
    posted_at: str = ""

    def as_row(self) -> dict:
        return {
            "company": self.company,
            "title": self.title,
            "location": self.location,
            "remote": self.remote,
            "salary": self.salary,
            "description": self.description,
            "url": self.url,
            "source": self.source,
            "ats": self.ats,
            "company_url": self.company_url,
            "posted_at": self.posted_at,
            "status": "new",
        }
