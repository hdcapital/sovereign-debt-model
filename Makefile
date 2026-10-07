# Sovereign Debt Spiral Monitor
# Every target is a thin wrapper around `python -m sdm.cli <command>`.
PY ?= .venv/bin/python
UV ?= uv

.PHONY: setup update indicators backtest dashboard report email monthly quarterly test lint

setup:            ## create venv and install everything (incl. dev + report extras)
	$(UV) venv .venv --python 3.11 || $(UV) venv .venv
	$(UV) pip install --python $(PY) -e ".[dev,report]"
	@test -f .env || cp .env.example .env
	@echo "Fill in .env, then: make update"

update:           ## refresh all data sources incrementally; log what changed
	$(PY) -m sdm.cli update

indicators:       ## compute the quarterly indicator table for every country
	$(PY) -m sdm.cli indicators

backtest:         ## run the backtest against data/events.csv -> reports/backtest/
	$(PY) -m sdm.cli backtest

dashboard:        ## build reports/dashboard/latest.html (+ dated copy)
	$(PY) -m sdm.cli dashboard

report:           ## generate the narrative quarterly report via Claude
	$(PY) -m sdm.cli report

email:            ## send the latest report (use DRY=1 for --dry-run -> reports/outbox/)
	$(PY) -m sdm.cli email $(if $(DRY),--dry-run,)

monthly:          ## update + indicators; email only if a transition / 1.5σ move fired
	$(PY) -m sdm.cli monthly

quarterly:        ## update + indicators + backtest + dashboard + report + email
	$(PY) -m sdm.cli quarterly

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check src tests
	$(PY) -m ruff format --check src tests
