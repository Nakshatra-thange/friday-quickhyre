from __future__ import annotations

import re
from typing import Any

from app.matching import skill_in_text
from app.search import get_store
from app.tools.explain_match import NO_RESUME

BULLET_RE = re.compile(r"^\s*[•\-\*▪●◦–]\s+")
WEAK_START = re.compile(r"^(responsible for|worked on|helped|involved in|assisted|participated|duties included|handled)\b", re.I)
SECTIONS = {"experience": ("experience", "employment", "internship"), "education": ("education", "academic"),
            "skills": ("skills", "technologies", "tech stack"), "projects": ("project",)}


def _bullets(text: str) -> list[str]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    b = [BULLET_RE.sub("", l) for l in lines if BULLET_RE.match(l)]
    return b if len(b) >= 3 else [l for l in lines if len(l.split()) >= 7]


def _sections_found(text: str) -> set[str]:
    found: set[str] = set()
    for line in text.splitlines():
        low = line.strip().lower()
        if 0 < len(low) <= 40:
            found |= {k for k, words in SECTIONS.items() if any(w in low for w in words)}
    return found


def ats_check(args: dict[str, Any], session: dict) -> dict[str, Any]:
    text = session.get("resume_text")
    if not text:
        return NO_RESUME
    job = get_store().get(str(args.get("job_id", "")))
    if not job:
        return {"error": "job_id not found in dataset"}

    matched = [k for k in job["skills"] if skill_in_text(k, text)]
    missing = [k for k in job["skills"] if k not in matched]
    coverage = round(100 * len(matched) / len(job["skills"])) if job["skills"] else 100

    layout, words, flags = session.get("layout") or {}, len(text.split()), []
    found = _sections_found(text)
    if len(found) < 3:
        flags.append("No clear section headings (missing: " + ", ".join(s for s in SECTIONS if s not in found)
                     + "). Use standard headings like Experience, Education, Skills, Projects.")
    if words > 700 or layout.get("pages", 1) > 2:
        flags.append(f"Long resume (~{words} words). Aim for 1 page under 5 years of experience, 2 pages max.")
    if layout.get("tables", 0) > 0 or layout.get("columnar_ratio", 0) > 0.25:
        flags.append("Tables or multi-column layout detected; many ATS parsers read these out of order. "
                     "Prefer a single-column layout.")
    bullets = _bullets(text)
    if sum(1 for b in bullets if re.search(r"\d", b)) < 2:
        flags.append("Few quantified results (numbers, %, scale). Add measurable impact where it is true.")

    weak = [b for b in bullets if not re.search(r"\d", b) and len(b.split()) >= 5]
    weak.sort(key=lambda b: 0 if WEAK_START.match(b) else 1)
    return {"job_id": job["id"], "title": job["title"], "keyword_coverage_pct": coverage,
            "matched_keywords": matched, "missing_keywords": missing, "formatting_flags": flags,
            "weak_bullets": [w[:220] for w in weak[:3]],
            "rewrite_guidance": (
                "Write exactly 3 rewrites, one per weak bullet. Use ONLY facts already in that bullet. For any "
                "number or outcome not given, insert a placeholder like [X%] or [N users] for the candidate to "
                "fill in truthfully. NEVER add a missing keyword as experience. Missing keywords are gaps: "
                "suggest learning them, or mention one only if the resume genuinely evidences it.")}