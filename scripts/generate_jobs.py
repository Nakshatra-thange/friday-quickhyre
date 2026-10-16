"""Generate ~200 SYNTHETIC jobs in QuickHyre's listing schema -> data/jobs.json.
Run: python scripts/generate_jobs.py   (deterministic, seed=42)
All companies are fictional. This is sample data, not real listings."""
import json
import random
from datetime import date, timedelta
from pathlib import Path

rng = random.Random(42)

CITIES = [("Bangalore", "Karnataka"), ("Mumbai", "Maharashtra"), ("Gurgaon", "Haryana"),
          ("Noida", "Uttar Pradesh"), ("Delhi", "Delhi"), ("Hyderabad", "Telangana"),
          ("Pune", "Maharashtra"), ("Chennai", "Tamil Nadu")]
PRE = ["Zenith", "Nimbus", "Kiraya", "Vayu", "Orbit", "Pixelkart", "Sutra", "Tarang", "Lumen",
       "Quantaloop", "Bhasha", "Nexora", "Artha", "Kavach", "Dhwani", "Prism", "Ankur", "Setu",
       "Vritti", "Mythri"]
SUF = ["Labs", "Systems", "Technologies", "AI", "Works", "Analytics", "Cloud", "Digital"]
COMPANIES = [f"{p} {s}" for p in PRE for s in SUF]
rng.shuffle(COMPANIES)
HYD_COS, OTHER_COS = COMPANIES[:16], COMPANIES[16:]

# (title, category, skills pool, base_min_exp, base_max_exp)
ROLES = [
    ("Senior Full Stack Developer", "Software Engineer", ["React", "Node.js", "MongoDB", "TypeScript"], 3, 7),
    ("Backend Engineer", "Software Engineer", ["Java", "Spring Boot", "MySQL", "Kafka"], 2, 6),
    ("Python Backend Developer", "Software Engineer", ["Python", "Django", "PostgreSQL", "Docker"], 1, 5),
    ("Frontend Developer", "Software Engineer", ["React", "JavaScript", "CSS", "Redux"], 1, 4),
    ("Data Scientist", "Data Science", ["Python", "SQL", "scikit-learn", "Pandas"], 2, 6),
    ("Machine Learning Engineer", "Data Science", ["Python", "PyTorch", "MLOps", "AWS"], 2, 6),
    ("Data Analyst", "Data Science", ["SQL", "Excel", "Power BI", "Python"], 0, 3),
    ("DevOps Engineer", "DevOps", ["AWS", "Kubernetes", "Terraform", "CI/CD"], 2, 6),
    ("Product Manager", "Product Manager", ["Roadmapping", "SQL", "User Research", "Analytics"], 3, 7),
    ("Digital Marketing Manager", "Marketing", ["SEO", "Google Ads", "Content Strategy", "Analytics"], 2, 5),
    ("Sales Development Representative", "Sales", ["Lead Generation", "CRM", "Cold Outreach", "Communication"], 0, 2),
    ("UI/UX Designer", "Design", ["Figma", "Prototyping", "User Research", "Design Systems"], 1, 5),
    ("QA Engineer", "Software Engineer", ["Selenium", "Python", "API Testing", "Jira"], 1, 4),
    ("Android Developer", "Software Engineer", ["Kotlin", "Android", "Jetpack Compose", "REST"], 2, 5),
    ("Cloud Engineer", "DevOps", ["Azure", "Docker", "Linux", "Python"], 2, 5),
    ("Business Analyst", "Product Manager", ["SQL", "Excel", "Stakeholder Management", "Tableau"], 1, 4),
]
HYD_ROLES = [
    ("Machine Learning Engineer", ["Python", "PyTorch", "MLOps", "AWS"]),
    ("GenAI Engineer", ["Python", "RAG", "Prompt Engineering", "FastAPI"]),
    ("NLP Engineer", ["Python", "Transformers", "spaCy", "PyTorch"]),
    ("Computer Vision Engineer", ["Python", "OpenCV", "PyTorch", "CUDA"]),
    ("MLOps Engineer", ["Docker", "Kubernetes", "MLflow", "AWS"]),
    ("Data Scientist", ["Python", "SQL", "scikit-learn", "Pandas"]),
]
INTERN_ROLES = [
    ("SDE Intern", "Software Engineer", ["Python", "Data Structures", "Git"]),
    ("ML Intern", "Data Science", ["Python", "NumPy", "scikit-learn"]),
    ("QA Intern", "Software Engineer", ["Manual Testing", "Selenium", "Jira"]),
    ("Data Analyst Intern", "Data Science", ["SQL", "Excel", "Python"]),
    ("Frontend Intern", "Software Engineer", ["HTML", "CSS", "JavaScript", "React"]),
    ("UI/UX Design Intern", "Design", ["Figma", "Wireframing", "User Research"]),
    ("Digital Marketing Intern", "Marketing", ["SEO", "Social Media", "Canva"]),
    ("DevOps Intern", "DevOps", ["Linux", "Docker", "Git"]),
]
FOCUS = {
    "Software Engineer": ["a high-traffic consumer platform", "internal developer tooling", "a payments product"],
    "Data Science": ["demand forecasting models", "a recommendation engine", "customer analytics dashboards"],
    "DevOps": ["cloud cost optimisation", "CI/CD pipelines", "platform reliability"],
    "Product Manager": ["a new onboarding funnel", "marketplace growth", "B2B workflow tools"],
    "Marketing": ["performance campaigns", "brand and content growth", "lifecycle marketing"],
    "Sales": ["inbound lead qualification", "enterprise outreach", "partner sales"],
    "Design": ["a redesigned mobile app", "a design system", "checkout experience"],
}


def posted() -> str:
    return (date(2026, 10, 14) - timedelta(days=rng.randint(0, 45))).isoformat()


def make(title, cat, skills, lo, hi, company, city, mode, ctype, intern=False, ai=False):
    focus = "LLM and ML products" if ai else rng.choice(FOCUS.get(cat, ["core product features"]))
    intro = f"{company} is an AI startup hiring" if ai else f"{company} is hiring"
    tail = ("Freshers and final-year students are welcome to apply."
            if intern else f"Ideal for candidates with {lo}-{hi} years of experience.")
    desc = (f"{intro} a {title} in {city[0]}. You will work on {focus} using "
            f"{', '.join(skills[:3])}. {tail}")
    return {"id": "", "title": title, "company": company, "city": city[0], "state": city[1],
            "work_mode": mode, "skills": skills, "exp_min": lo, "exp_max": hi, "category": cat,
            "description": desc, "posted_at": posted(), "company_type": ctype, "is_internship": intern}


def mode() -> str:
    return rng.choices(["Remote", "Hybrid", "On-site"], [2, 4, 4])[0]


jobs, general = [], []
for i in range(152):                                   # general listings
    t, cat, pool, lo, hi = rng.choice(ROLES)
    lo += rng.randint(0, 1)
    j = make(t, cat, rng.sample(pool, rng.choice([3, 4])), lo, lo + rng.randint(1, 3),
             rng.choice(OTHER_COS), rng.choice(CITIES), mode(),
             rng.choices(["startup", "mnc", "unicorn", "services"], [4, 3, 1, 2])[0])
    general.append(j)
jobs += general

for i in range(22):                                    # internships / freshers
    t, cat, sk = INTERN_ROLES[i % len(INTERN_ROLES)]
    jobs.append(make(t, cat, sk, 0, 1, rng.choice(OTHER_COS), CITIES[i % len(CITIES)], mode(),
                     rng.choice(["startup", "mnc", "services"]), intern=True))

for i in range(16):                                    # Hyderabad AI startups
    t, sk = HYD_ROLES[i % len(HYD_ROLES)]
    lo = rng.randint(0, 3)
    jobs.append(make(t, "Data Science", sk, lo, lo + rng.randint(2, 3), HYD_COS[i],
                     ("Hyderabad", "Telangana"), mode(), "startup", ai=True))

for src in rng.sample(general, 10):                    # seeded near-duplicates
    d = dict(src)
    extra = next(s for s in ["Git", "Agile", "Communication"] if s not in src["skills"])
    d["skills"] = src["skills"] + [extra]
    d["description"] = src["description"].replace("is hiring", "is now hiring")
    d["posted_at"] = (date.fromisoformat(src["posted_at"]) + timedelta(days=rng.randint(1, 3))).isoformat()
    jobs.append(d)

rng.shuffle(jobs)
for n, j in enumerate(jobs, 1):
    j["id"] = f"job_{n:04d}"

out = Path(__file__).resolve().parent.parent / "data" / "jobs.json"
out.write_text(json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {len(jobs)} jobs | internships={sum(j['is_internship'] for j in jobs)} | "
      f"hyd AI startups={sum(j['city']=='Hyderabad' and j['company_type']=='startup' and j['category']=='Data Science' for j in jobs)}")
