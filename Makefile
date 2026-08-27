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
	# Whole repository, matching `prek run -a` and the CI lint job (both run
	# every hook over every tracked file) — commit 59620c2 is proof this and
	# CI already diverged once on examples/, which `src tests` does not cover.
	$(PYTHON) -m ruff check .
	# Deliberately still scoped to src tests, NOT widened to match the check
	# above. `ruff format .` also formats Python code blocks embedded in
	# Markdown (CLAUDE.md, README.md, docs/tutorials.md all have some) as of
	# ruff 0.16, but the ruff-format pre-commit hook only ever receives
	# python/pyi/jupyter files (its `types_or`), so CI never format-checks
	# those three files and would not fail if they drifted. Widening this to
	# `.` would make `make lint` stricter than CI, not equal to it, and would
	# need those three docs reformatted as a one-off side effect unrelated to
	# any code change. Revisit deliberately, in its own commit, if wanted.
	$(PYTHON) -m ruff format --check src tests
	# Runs the ty pinned in the typecheck dependency group, installed into
	# .venv by the venv target above — not an unpinned `uvx ty check`, which
	# would resolve to whatever the latest release happens to be. Keep the
	# pin in sync with rev: on the ty hook in .pre-commit-config.yaml, so
	# this target and CI report the same thing.
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
