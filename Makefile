.PHONY: install data run test eval

install:
	python -m pip install -r requirements.txt

data:
	python scripts/generate_jobs.py

run:
	python -m uvicorn app.main:app --reload --port 8000

test:
	python -m pytest -q

eval:
	python eval/run_evals.py
