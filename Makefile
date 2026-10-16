.RECIPEPREFIX = >
.PHONY: install data run test eval

install:
> pip install -r requirements.txt

data:
> python scripts/generate_jobs.py

run:
> uvicorn app.main:app --reload --port 8000

test:
> pytest -q

eval:
> python eval/run_evals.py