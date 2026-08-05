# Tools run from .venv, not through `uv run`: this package declares an entry point
# group that uv resolves against the whole environment, and a bare `uv run` can fail
# in a checkout where sibling eduTAP packages are not installed.
PYTHON := .venv/bin/python
VENV   := .venv

.DEFAULT_GOAL := help
.PHONY: help venv lint reformat test-local test-integration test-matrix

help: ## Show available targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk -F':.*?## ' '{printf "  %-18s %s\n", $$1, $$2}'

venv: ## Create .venv and install the package with the callback extra and dev group
	test -d $(VENV) || uv venv
	uv pip install -U -e ".[callback]" --group dev

lint: venv ## Run ruff checks and the type checker
	$(PYTHON) -m ruff check src tests
	$(PYTHON) -m ruff format --check src tests
	# Runs the ty pinned in the typecheck dependency group, installed into
	# .venv by the venv target above — not an unpinned `uvx ty check`, which
	# would resolve to whatever the latest release happens to be. The local
	# pre-commit hook currently pins a different, older ty
	# (.pre-commit-config.yaml: ty@0.0.17); bringing the two into agreement
	# is Task 3's job, not this target's.
	$(PYTHON) -m ty check

reformat: venv ## Autoformat and autofix
	$(PYTHON) -m ruff format src tests
	$(PYTHON) -m ruff check --fix src tests

test-local: venv ## Unit tests, no Google credentials needed
	$(PYTHON) -m pytest

test-integration: venv ## Tests against the real Google Wallet API, needs credentials
	$(PYTHON) -m pytest --run-integration

test-matrix: venv ## The full tox matrix, py310 through py314
	uvx --with "tox-uv,tox-gh" tox
