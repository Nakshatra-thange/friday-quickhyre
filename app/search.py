from __future__ import annotations

import json
import logging
import re
import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.models import Job

log = logging.getLogger("friday.search")
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "jobs.json"

CITY_ALIASES = {"bengaluru": "bangalore", "gurugram": "gurgaon", "new delhi": "delhi",
                "bombay": "mumbai", "madras": "chennai"}
STOPWORDS = {"a", "an", "the", "in", "at", "for", "of", "and", "or", "me", "show", "find", "jobs",
             "job", "openings", "opening", "latest", "roles", "role", "to", "with", "on", "my",
             "internship", "internships", "intern", "interns", "fresher", "freshers", "student",
             "students", "college", "entry", "level", "remote", "hybrid", "onsite", "startup",
             "startups", "company", "companies", "any", "are", "there", "please"}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", s.lower())).strip()


def dedupe_jobs(jobs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Collapse near-duplicates: same normalized title+company+city AND skill Jaccard >= 0.5.
    Keeps the first occurrence (i.e. the best-ranked one). Returns (kept, removed_count)."""
    kept: list[dict[str, Any]] = []
    sigs: list[tuple[tuple[str, str, str], set[str]]] = []
    removed = 0
    for j in jobs:
        key = (_norm(j["title"]), _norm(j["company"]), _norm(j["city"]))
        skills = {s.lower() for s in j["skills"]}
        is_dup = False
        for k, ks in sigs:
            if k == key:
                union = skills | ks
                if not union or len(skills & ks) / len(union) >= 0.5:
                    is_dup = True
                    break
        if is_dup:
            removed += 1
        else:
            kept.append(j)
            sigs.append((key, skills))
    if removed:
        log.info(json.dumps({"event": "dedupe", "collapsed": removed}))
    return kept, removed


def _fts_query(q: str) -> str | None:
    toks = []
    for t in re.findall(r"[A-Za-z0-9+#]+", q.lower()):
        if t in STOPWORDS:
            continue
        if len(t) > 3 and t.endswith("s"):
            t = t[:-1]
        toks.append(f'"{t}"')
    return " OR ".join(toks) or None


class JobStore:
    def __init__(self, path: Path = DATA_PATH) -> None:
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE jobs(id TEXT PRIMARY KEY, title TEXT, company TEXT, city TEXT, state TEXT,
                work_mode TEXT, skills_json TEXT, skills_text TEXT, exp_min INT, exp_max INT,
                category TEXT, description TEXT, posted_at TEXT, company_type TEXT, is_internship INT);
            CREATE VIRTUAL TABLE jobs_fts USING fts5(id UNINDEXED, title, company, skills_text, category, description);
        """)
        raw = json.loads(path.read_text(encoding="utf-8"))
        for r in raw:
            j = Job(**r)  # validates schema
            st = " ".join(j.skills)
            self.db.execute("INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (j.id, j.title, j.company, j.city, j.state, j.work_mode, json.dumps(j.skills), st,
                             j.exp_min, j.exp_max, j.category, j.description, j.posted_at, j.company_type,
                             int(j.is_internship)))
            self.db.execute("INSERT INTO jobs_fts VALUES (?,?,?,?,?,?)",
                            (j.id, j.title, j.company, st, j.category, j.description))
        self.db.commit()
        log.info(json.dumps({"event": "jobs_loaded", "count": len(raw)}))

    @staticmethod
    def _row(r: sqlite3.Row) -> dict[str, Any]:
        return {"id": r["id"], "title": r["title"], "company": r["company"], "city": r["city"],
                "state": r["state"], "work_mode": r["work_mode"], "skills": json.loads(r["skills_json"]),
                "exp_min": r["exp_min"], "exp_max": r["exp_max"], "category": r["category"],
                "description": r["description"], "posted_at": r["posted_at"],
                "company_type": r["company_type"], "is_internship": bool(r["is_internship"])}

    def all(self) -> list[dict[str, Any]]:
        return [self._row(r) for r in self.db.execute("SELECT * FROM jobs ORDER BY id")]

    def get(self, job_id: str) -> dict[str, Any] | None:
        r = self.db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return self._row(r) if r else None

    def search(self, query: str | None = None, city: str | None = None, work_mode: str | None = None,
               skills: list[str] | None = None, min_exp: int | None = None, max_exp: int | None = None,
               internship_only: bool = False, company_type: str | None = None, limit: int = 5,
               resume_skills: list[str] | None = None) -> list[dict[str, Any]]:
        limit = max(1, min(limit or 5, 10))
        where: list[str] = []
        params: list[Any] = []
        if city:
            c = city.strip().lower()
            where.append("LOWER(j.city)=?"); params.append(CITY_ALIASES.get(c, c))
        if work_mode:
            where.append("LOWER(j.work_mode)=?"); params.append(work_mode.strip().lower())
        if company_type:
            where.append("LOWER(j.company_type)=?"); params.append(company_type.strip().lower())
        if internship_only:
            where.append("j.is_internship=1")
        if min_exp is not None:   # job experience range must overlap [min_exp, max_exp]
            where.append("j.exp_max>=?"); params.append(min_exp)
        if max_exp is not None:
            where.append("j.exp_min<=?"); params.append(max_exp)
        if skills:
            where.append("(" + " OR ".join("LOWER(j.skills_text) LIKE ?" for _ in skills) + ")")
            params += [f"%{s.lower()}%" for s in skills]
        extra = (" AND " + " AND ".join(where)) if where else ""

        fts = _fts_query(query) if query else None
        if fts:
            sql = ("SELECT j.*, bm25(jobs_fts) AS rank FROM jobs_fts JOIN jobs j ON j.id=jobs_fts.id "
                   f"WHERE jobs_fts MATCH ?{extra}")
            rows = self.db.execute(sql, [fts, *params]).fetchall()
        else:
            sql = "SELECT j.*, 0.0 AS rank FROM jobs j WHERE 1=1" + extra
            rows = self.db.execute(sql, params).fetchall()

        rs = {s.lower() for s in (resume_skills or [])}
        scored = []
        for r in rows:
            d = self._row(r)
            overlap = len(rs & {s.lower() for s in d["skills"]})
            scored.append((-r["rank"] + 2 * overlap, d["posted_at"], d))
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        ranked = [d for _, _, d in scored]
        deduped, _ = dedupe_jobs(ranked)
        return deduped[:limit]


@lru_cache(maxsize=1)
def get_store() -> JobStore:
    return JobStore()