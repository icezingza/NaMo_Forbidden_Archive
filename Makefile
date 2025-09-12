.PHONY: setup lint format test audit run precommit

VENVDIR := .venv
PY := $(VENVDIR)/bin/python
PIP := $(VENVDIR)/bin/pip

$(VENVDIR)/bin/activate:
	python -m venv $(VENVDIR)
	. $(VENVDIR)/bin/activate;     	pip install --upgrade pip;     	pip install -r requirements.txt || true;     	pip install -r requirements-dev.txt

setup: $(VENVDIR)/bin/activate
	$(VENVDIR)/bin/pre-commit install

lint:
	$(VENVDIR)/bin/ruff check .

format:
	$(VENVDIR)/bin/ruff check --fix .
	$(VENVDIR)/bin/black .

test:
	$(VENVDIR)/bin/pytest -q

audit:
	$(VENVDIR)/bin/pip-audit -r requirements.txt || true
	$(VENVDIR)/bin/bandit -r . || true

run:
	APP_ENV=dev APP_PORT=8000 $(VENVDIR)/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --reload

precommit:
	$(VENVDIR)/bin/pre-commit run --all-files
