from app.matching import canon, compare, exp_fit, skill_in_text

ML = {"skills": ["Python", "PyTorch", "MLOps", "AWS"], "exp_min": 2, "exp_max": 6}
JAVA = {"skills": ["Java", "Spring Boot", "MySQL", "Kafka"], "exp_min": 2, "exp_max": 6}
DS = {"skills": ["Python", "PyTorch", "scikit-learn", "AWS", "MLOps"], "years_experience": 3}


def test_aliases():
    assert canon("sklearn") == "scikit-learn"
    assert skill_in_text("scikit-learn", "Trained models with sklearn")


def test_token_boundaries():
    assert not skill_in_text("Java", "Built apps in JavaScript")
    assert not skill_in_text("SQL", "Used MySQL daily")
    assert skill_in_text("SQL", "Wrote SQL, Python")


def test_exp_fit():
    assert exp_fit(3, 2, 6) == 1.0
    assert exp_fit(0, 3, 6) < exp_fit(2, 3, 6) < 1.0
    assert exp_fit(12, 2, 6) >= 0.6


def test_ordering_ml_over_java():
    assert compare(ML, DS)["score"] > compare(JAVA, DS)["score"] + 30


def test_score_bounds_and_determinism():
    a, b = compare(ML, DS), compare(ML, DS)
    assert a == b and 0 <= a["score"] <= 100
    assert compare(ML, {"skills": [], "years_experience": 0})["score"] < 30