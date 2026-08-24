"""Maps a job's signal (fit_score, comp, or company) to a tier, per
local-data/config/tiers.json. The signal itself (fit_score, in particular)
is produced by the agent's judgment when running the skill, not by this
module — this only implements the deterministic mapping once that judgment
exists.
"""
from config import load_tiers


def assign_tier(*, fit_score: int = None, comp: float = None, company: str = None) -> str:
    config = load_tiers()
    scheme = config["scheme_type"]

    if scheme == "fit_score":
        if fit_score is None:
            raise ValueError("fit_score scheme requires a fit_score")
        for t in config["tiers"]:
            if t["min_score"] <= fit_score <= t["max_score"]:
                return t["tier"]
        raise ValueError(f"fit_score {fit_score} did not match any tier")

    if scheme == "compensation":
        if comp is None:
            raise ValueError("compensation scheme requires comp")
        tiers = sorted(config["tiers"], key=lambda t: -t["min"])
        for t in tiers:
            if comp >= t["min"]:
                return str(t["tier"])
        return str(tiers[-1]["tier"])

    if scheme == "company_stage":
        if company is None:
            raise ValueError("company_stage scheme requires company")
        for t in config["tiers"]:
            names = [c.lower() for c in t["companies"]]
            if "*" in t["companies"] or company.lower() in names:
                return t["tier"]
        return config["tiers"][-1]["tier"]

    raise ValueError(f"Unknown tier scheme_type: {scheme}")
