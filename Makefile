PYTHON ?= python

.PHONY: setup test lint typecheck security run docker-up

setup:
	$(PYTHON) -m venv .venv
	.venv/bin/python -m pip install --requirement requirements-dev.txt

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

typecheck:
	$(PYTHON) -m mypy backend

security:
	$(PYTHON) -m bandit -q -r backend src
	$(PYTHON) -m pip_audit -r requirements.txt

docker-up:
	docker compose up --build
