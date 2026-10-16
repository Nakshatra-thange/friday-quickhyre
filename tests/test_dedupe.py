from app.search import dedupe_jobs

BASE = {"title": "Data Analyst", "company": "Acme Labs", "city": "Pune", "skills": ["SQL", "Excel", "Python"]}


def test_collapses_near_duplicate():
    dup = {**BASE, "title": "Data  Analyst!", "skills": ["SQL", "Excel", "Python", "Git"]}
    kept, removed = dedupe_jobs([BASE, dup])
    assert removed == 1 and kept == [BASE]


def test_keeps_different_company():
    other = {**BASE, "company": "Other Labs"}
    assert dedupe_jobs([BASE, other])[1] == 0


def test_keeps_same_title_with_different_skills():
    other = {**BASE, "skills": ["Tableau", "Power BI", "R"]}
    assert dedupe_jobs([BASE, other])[1] == 0


def test_keeps_different_city():
    assert dedupe_jobs([BASE, {**BASE, "city": "Delhi"}])[1] == 0