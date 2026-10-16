from __future__ import annotations

import re
from typing import Any

ALIASES = {
    "js": "javascript", "node": "node.js", "nodejs": "node.js", "react.js": "react", "reactjs": "react",
    "postgres": "postgresql", "sklearn": "scikit-learn", "scikit learn": "scikit-learn",
    "k8s": "kubernetes", "powerbi": "power bi", "ci cd": "ci/cd", "cicd": "ci/cd",
    "ml ops": "mlops", "mongo": "mongodb", "ms excel": "excel",
}


def canon(s: str) -> str:
    s = re.sub(r"\s+", " ", s.strip().lower())
    return ALIASES.get(s, s)


def _forms(skill: str) -> set[str]:
    c = canon(skill)
    return {c} | {a for a, v in ALIASES.items() if v == c}


def skill_in_text(skill: str, text: str) -> bool:
    """Whole-token match, so 'Java' does not match 'JavaScript' and 'SQL' does not match 'MySQL'."""
    low = text.lower()
    for f in _forms(skill):
        if re.search(r"(?<![a-z0-9+#.])" + re.escape(f) + r"(?![a-z0-9+#])", low):
            return True
    return False


def evidence_line(skill: str, text: str) -> str | None:
    for line in text.splitlines():
        if skill_in_text(skill, line):
            return line.strip()[:140]
    return None


def exp_fit(years: float, lo: int, hi: int) -> float:
    if lo <= years <= hi:
        return 1.0
    if years < lo:
        return max(0.0, 1 - 0.3 * (lo - years))
    return max(0.6, 1 - 0.1 * (years - hi))


def compare(job: dict[str, Any], profile: dict[str, Any], text: str = "") -> dict[str, Any]:
    """score = 70% skill coverage + 30% experience fit. Fully deterministic."""
    have = {canon(s) for s in profile.get("skills", [])}
    matched: list[str] = []
    missing: list[str] = []
    for s in job["skills"]:
        ok = canon(s) in have or (bool(text) and skill_in_text(s, text))
        (matched if ok else missing).append(s)
    coverage = len(matched) / (len(job["skills"]) or 1)
    years = float(profile.get("years_experience") or 0)
    fit = exp_fit(years, job["exp_min"], job["exp_max"])
    score = round(100 * (0.7 * coverage + 0.3 * fit))
    return {"score": max(0, min(100, score)), "matched": matched, "missing": missing,
            "skill_coverage": round(coverage, 2), "experience_fit": round(fit, 2), "years": years}