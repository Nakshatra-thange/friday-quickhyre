import asyncio

from app.search import get_store
from app.tools.registry import run_tool

JOB = get_store().all()[0]
SESSION = {"resume": {"skills": ["Python"], "years_experience": 2},
           "resume_text": "Skills: Python\nExperience\nEducation\nProjects\nWorked on a small API for a team project",
           "layout": {}}


def call(name, args, session):
    return asyncio.run(run_tool(name, args, session))


def test_tools_require_resume():
    for t in ["explain_match", "ats_check", "get_resume_profile"]:
        assert call(t, {"job_id": JOB["id"]}, {})["error"] == "no_resume"


def test_explain_match_shape():
    out = call("explain_match", {"job_id": JOB["id"]}, SESSION)
    assert 0 <= out["match_score"] <= 100
    assert {"strengths", "gaps", "how_to_close_gaps"} <= out.keys()


def test_ats_missing_keywords_are_really_missing():
    out = call("ats_check", {"job_id": JOB["id"]}, SESSION)
    for kw in out["missing_keywords"]:
        assert kw.lower() not in SESSION["resume_text"].lower()
    assert set(out["missing_keywords"]) | set(out["matched_keywords"]) == set(JOB["skills"])


def test_unknown_job():
    assert "error" in call("explain_match", {"job_id": "job_9999"}, SESSION)