# Package Modernisation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring `edutap.wallet_google` up to the project's tooling standard — a `Makefile` as the uniform entry point, PEP 639 and PEP 735 packaging metadata, an `sdist` that stops shipping internal documents, a `ty` pin that can actually be updated, and the full ruff rule selection.

**Architecture:** Five independent changes on one branch, in an order that matters: the packaging metadata defines the `dev` dependency group that the `Makefile` then installs, and the linter rules go last so their large diffs do not sit underneath everything else during review.

**Tech Stack:** hatchling, uv, prek, ruff, ty, tox, pytest.

**Spec:** `superpowers/specs/2026-08-04-package-modernisation-design.md` — read it before starting. It carries the measurements behind every number in this plan.

## Global Constraints

- Branch: `chore/package-modernisation`, already created from `main`. Never commit to `main`. Never `git push` — the user pushes.
- Conventional Commits. Commit messages, code, comments and identifiers in English.
- **Do not drop Python 3.10 support in this branch.** Its end of life is 2026-10-31, which has not happened. Narrowing `requires-python` in a published library is a breaking change and belongs in its own release.
- **Do not write the 144 missing docstrings.** The `D1xx` rules stay in `ignore`; see Task 5.
- `tests/` stays in the sdist. A distribution packager wants to run the suite.
- After Task 1 the install command everywhere is `uv pip install -U -e ".[callback]" --group dev`. `[test]`, `[typecheck]` and `[develop]` no longer exist as extras.
- Each task ends with a green `pytest` before its commit. The suite is fast; run it.

## Environment setup

```bash
cd worktrees/modernisation
uv venv
uv pip install -e ".[test,develop]"   # the *old* extras; Task 1 replaces them
```

`pytest` below means `.venv/bin/python -m pytest`. Use `-v --no-cov -p no:cacheprovider` for fast single-file runs; the project's `addopts` otherwise force a coverage run.

## File Structure

| File | Responsibility | Task |
| --- | --- | --- |
| `pyproject.toml` | license expression, dependency groups, sdist contents, ruff rules, dated 3.10 marker | 1, 3, 4, 5 |
| `MANIFEST.in` | deleted — hatchling never read it | 1 |
| `Makefile` | uniform entry point to the common workflows (create) | 2 |
| `.pre-commit-config.yaml` | `ty` moves to the official hook repository | 3 |
| `RELEASING.md` | the Python 3.10 removal checklist | 3 |
| `src/edutap/wallet_google/handlers/fastapi.py`, `handlers/validate.py`, `registry.py`, `credentials.py` | `B904`, `B007`, `B019` fixes | 4 |
| `src/edutap/wallet_google/clientpool.py`, `models/datatypes/enums.py` | three `# noqa: S105` | 4 |
| `tests/test_check_models.py`, `test_handler_validate.py`, `test_settings.py` | `B007`, `B017`, `B018` fixes | 4 |
| every module with a docstring | `D` autofix and the 58 manual fixes | 5 |

---

### Task 1: Packaging metadata

**Files:**
- Modify: `pyproject.toml:13-33` (license, classifiers), `:51-71` (extras → groups), `[tool.tox.env_run_base]`
- Delete: `MANIFEST.in`

**Interfaces:**
- Consumes: nothing.
- Produces: the extra `callback` and the dependency groups `test`, `typecheck`, `dev`. Every later task and the `Makefile` install with `-e ".[callback]" --group dev`.

- [ ] **Step 1: Record what the sdist contains today**

```bash
uvx --from build pyproject-build --sdist --outdir dist-before .
python3 -c "
import tarfile, glob
t = tarfile.open(glob.glob('dist-before/*.tar.gz')[0])
names = sorted(n.split('/', 1)[1] for n in t.getnames() if '/' in n)
open('sdist-before.txt', 'w').write('\n'.join(names))
print(len(names), 'files')
"
```

Expected: 108 files. This list is the baseline the last step of this task diffs against; without it, "the sdist still contains what it should" is an opinion.

- [ ] **Step 2: Adopt the PEP 639 license expression**

In `pyproject.toml`, replace lines 14-20 (the `license` field and the whole TODO comment block) with:

```toml
license = "EUPL-1.2"
license-files = ["LICENSE"]
```

and delete this line from `classifiers`:

```toml
    "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
```

PEP 639 forbids carrying both a license expression and a license classifier; leaving the classifier in makes the build fail rather than warn.

- [ ] **Step 3: Move the development extras to dependency groups**

Replace the whole `[project.optional-dependencies]` block (lines 51-71) with:

```toml
[project.optional-dependencies]
# The only extra a consumer of this library installs. Everything else that used
# to live here is a dependency group below: groups are not published in the
# wheel metadata, which is the right place for tooling nobody downstream needs.
callback = [
    "fastapi",
]

[dependency-groups]
test = [
    "freezegun",
    "pytest-asyncio",
    "pytest-cov",
    "pytest-explicit",
    "pytest",
    "respx",
    "tox",
]
typecheck = [
    "ty",
]
dev = [
    {include-group = "test"},
    {include-group = "typecheck"},
    "pdbp>=1.7.1", # the maintained successor to pdbpp
    # "ipython",  not recommended with pdpb, better use ipdb then
]
```

Note what is **not** there: the old `test` extra began with `"edutap.wallet-google[callback]"`. Inside an extra that is a recursive self-reference; inside a dependency group it is an ordinary requirement and would be resolved against PyPI, pulling the published package over the local checkout. `callback` therefore moves to the install command instead.

- [ ] **Step 4: Point tox at the group**

In `[tool.tox.env_run_base]`, replace:

```toml
extras = ["test", "develop"]
```

with:

```toml
extras = ["callback"]
dependency_groups = ["dev"]
```

tox 4.58 supports both keys together. `dev` pulls `test` and `typecheck` in through `include-group`.

- [ ] **Step 5: Verify the install resolves**

```bash
uv pip install -e ".[callback]" --group dev
```

Expected: resolves and installs, including `fastapi`, `pytest`, `ty` and `pdbp`.

Read the output rather than only the exit code. `edutap-wallet-google` must appear as the local editable path, not as a *downloaded* package — if it is downloaded, a self-reference survived Step 3 and the checkout is being shadowed by the published release.

- [ ] **Step 6: Constrain the sdist and delete `MANIFEST.in`**

Add to `pyproject.toml`, next to the existing `[tool.hatch.build.targets.wheel]`:

```toml
[tool.hatch.build.targets.sdist]
# hatchling does not read MANIFEST.in — that is a setuptools file, and an sdist
# built with it in place still contained docs/ and .claude/, both of which it
# claimed to exclude. These are the contents on purpose:
#   tests/ stays, so a distribution packager can run the suite.
#   superpowers/, .claude/, CLAUDE.md are internal working documents.
#   .github/, docs/ and examples/ are not needed to build or test the package.
include = [
    "/src",
    "/tests",
    "/README.md",
    "/CONTRIBUTING.md",
    "/LICENSE",
    "/pyproject.toml",
]
```

Then:

```bash
git rm MANIFEST.in
```

- [ ] **Step 7: Diff the sdist against the baseline**

```bash
uvx --from build pyproject-build --sdist --outdir dist-after .
python3 -c "
import tarfile, glob
t = tarfile.open(glob.glob('dist-after/*.tar.gz')[0])
names = sorted(n.split('/', 1)[1] for n in t.getnames() if '/' in n)
open('sdist-after.txt', 'w').write('\n'.join(names))
print(len(names), 'files')
"
diff sdist-before.txt sdist-after.txt
```

Expected in the diff, as removals only: `.claude/*`, `.dockerignore`, `.editorconfig`, `.github/*`, `.gitignore`, `.pre-commit-config.yaml`, `CLAUDE.md`, `MANIFEST.in`, `RELEASING.md`, `docs/*`, `examples/*`, `superpowers/*`. `PKG-INFO` stays (hatchling generates it).

**Every `src/` and `tests/` path must be unchanged.** A removal under either is a mistake in the `include` list, not an improvement.

- [ ] **Step 8: Confirm the license metadata in the built artefact**

```bash
python3 -c "
import tarfile, glob
t = tarfile.open(glob.glob('dist-after/*.tar.gz')[0])
name = [n for n in t.getnames() if n.endswith('PKG-INFO')][0]
print(t.extractfile(name).read().decode()[:600])
"
```

Expected: `Metadata-Version: 2.4`, `License-Expression: EUPL-1.2`, `License-File: LICENSE`, and **no** `Classifier: License :: OSI Approved …`.

- [ ] **Step 9: Clean up and run the suite**

```bash
rm -rf dist-before dist-after sdist-before.txt sdist-after.txt
pytest
```

Expected: PASS.

- [ ] **Step 10: Commit**

`MANIFEST.in` was already staged for deletion by the `git rm` in Step 6.

```bash
git add pyproject.toml
git commit -m "build: adopt PEP 639 and PEP 735, and stop shipping internal docs

The PEP 639 TODO in pyproject.toml is redeemable: hatchling emits
Metadata-Version 2.4 with License-Expression, so the license text field and
the license classifier both go.

test, typecheck and develop were extras, which published them in the wheel
metadata although no consumer installs them; they become dependency groups,
with develop renamed dev. The self-reference to [callback] cannot come along —
in a group it would resolve against PyPI rather than the checkout — so it
moves to the install command.

MANIFEST.in never did anything: hatchling does not read it, and the sdist it
claimed to trim still contained docs/ and .claude/. An explicit sdist target
replaces it and drops 40 files of CI configuration and internal notes."
```

---

### Task 2: Makefile and prek

**Files:**
- Create: `Makefile`
- Modify: `pyproject.toml` (`[tool.tox.env.format]`, `[tool.tox.env.lint]`)

**Interfaces:**
- Consumes: the `callback` extra and the `dev` group from Task 1.
- Produces: `make venv | lint | reformat | test-local | test-integration | test-matrix`. Later tasks use `make lint` and `make test-local`.

- [ ] **Step 1: Write the Makefile**

Create `Makefile`. It follows `edutap.data_provider`'s, including the reason tools are invoked through the venv interpreter rather than `uv run`:

```makefile
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
	uvx ty check

reformat: venv ## Autoformat and autofix
	$(PYTHON) -m ruff format src tests
	$(PYTHON) -m ruff check --fix src tests

test-local: venv ## Unit tests, no Google credentials needed
	$(PYTHON) -m pytest

test-integration: venv ## Tests against the real Google Wallet API, needs credentials
	$(PYTHON) -m pytest --run-integration

test-matrix: venv ## The full tox matrix, py310 through py314
	uvx --with "tox-uv,tox-gh" tox
```

`ty` is invoked with `uvx` rather than `$(PYTHON) -m ty` to match how `.pre-commit-config.yaml` runs it, so `make lint` and the hook cannot disagree about the version.

- [ ] **Step 2: Verify every target**

```bash
make help
make venv
make lint
make test-local
```

Expected: `help` lists six targets; `venv` installs; `lint` and `test-local` pass. Do not run `test-integration` — it needs Google credentials and creates permanent objects in the Wallet account.

- [ ] **Step 3: Switch the tox hook environments to prek**

In `pyproject.toml`, `[tool.tox.env.format]` and `[tool.tox.env.lint]` both list `deps = ["pre-commit"]` and call `pre-commit`. Replace with `prek`, which is a drop-in for the same `.pre-commit-config.yaml`:

```toml
[tool.tox.env.format]
description = "automatically reformats code"
skip_install = true
deps = ["prek"]
commands = [
    ["prek", "run", "-a", "ruff"],
    ["prek", "run", "-a", "ruff-format"],
]

[tool.tox.env.lint]
description = "run linters that will help improve the code style"
skip_install = true
deps = ["prek"]
commands = [["prek", "run", "-a"]]
```

Leave the `ci:` block in `.pre-commit-config.yaml` alone. pre-commit.ci runs server-side on real `pre-commit`; prek is the local runner, and the two share the config file by design.

- [ ] **Step 4: Verify the lint environment still works**

Run: `uvx --with tox-uv tox -e lint`

Expected: PASS, the same hooks as before. If a hook behaves differently under prek, that is a prek incompatibility worth reporting — do not paper over it by reverting only that hook.

- [ ] **Step 5: Document the Makefile**

In `CONTRIBUTING.md`, add near the top of whatever section covers getting started:

```markdown
## Common tasks

    make help              # list every target
    make venv              # create .venv and install the package for development
    make lint              # ruff check, ruff format --check, ty check
    make reformat          # ruff format and ruff check --fix
    make test-local        # the unit suite
    make test-matrix       # the full tox matrix, py310 through py314

`make test-integration` runs against the real Google Wallet API. It needs
credentials and it creates objects that cannot be deleted; read
`tests/integration/` before running it.
```

- [ ] **Step 6: Commit**

```bash
git add Makefile pyproject.toml CONTRIBUTING.md
git commit -m "build: add a Makefile and switch the local hook runner to prek

Every repository is supposed to expose its common workflows through the same
make targets; this one had none. Follows edutap.data_provider's Makefile,
including its reason for calling .venv/bin/python rather than uv run.

prek reads the same .pre-commit-config.yaml, so only the two tox environments
change. pre-commit.ci keeps running server-side on pre-commit."
```

---

### Task 3: The two things with an expiry date

**Files:**
- Modify: `.pre-commit-config.yaml` (the `local` ty hook, and the `ci: skip:` list)
- Modify: `pyproject.toml:13` (dated comment beside `requires-python`)
- Modify: `RELEASING.md`

**Interfaces:**
- Consumes: nothing.
- Produces: nothing consumed later.

- [ ] **Step 1: Replace the local ty hook with the official repository**

In `.pre-commit-config.yaml`, delete the whole `- repo: local` block containing the `ty` hook and add:

```yaml
-   repo: https://github.com/astral-sh/ty-pre-commit
    rev: v0.0.66
    hooks:
    -   id: ty
```

The point is not the version, it is where the version lives. `entry: uvx ty@0.0.17 check` is a string no tool updates: `pre-commit autoupdate` rewrites `rev:` on remote repositories only, and no Renovate manager reads a version out of an `entry`. That pin sat 49 releases behind. In a `rev:` it is inside pre-commit.ci's monthly autoupdate.

The upstream hook is already `pass_filenames: false` and `always_run: true`, matching the local hook it replaces.

- [ ] **Step 2: Take ty out of the pre-commit.ci skip list**

In the `ci:` block at the top of `.pre-commit-config.yaml`:

```yaml
    skip: [check-manifest, pyroma]
```

`ty` was skipped because a `local` hook shelling out to `uvx` cannot run in pre-commit.ci's sandbox. A remote hook can.

- [ ] **Step 3: Run it and expect new diagnostics**

Run: `uvx --with tox-uv tox -e lint`

Expected: **possibly FAIL.** ty is pre-1.0 and this jumps 49 releases. Read what it reports:

- A diagnostic pointing at a real problem: fix the code.
- A diagnostic from a rule stricter than the project wants right now: add it to `[tool.ty.rules]` as `"warn"`, next to the four already there, with a comment saying why.

Do not silence a category wholesale without reading its instances.

- [ ] **Step 4: Commit the hook change separately**

```bash
git add .pre-commit-config.yaml pyproject.toml
git commit -m "build: run ty from its own pre-commit repository

The local hook pinned ty inside an entry string as uvx ty@0.0.17, where
nothing could update it: pre-commit autoupdate only rewrites rev: on remote
repositories. It had fallen 49 releases behind. In a rev: it is inside
pre-commit.ci's monthly autoupdate, which also lets it come off the skip
list."
```

- [ ] **Step 5: Mark the Python 3.10 end of life**

In `pyproject.toml`, directly above `requires-python` on line 13:

```toml
# Python 3.10 reaches end of life on 2026-10-31. Dropping it narrows this
# field, which is a breaking change for consumers, so it gets its own release
# rather than riding along with something else. Everything that changes with
# it: requires-python below, the 3.10 classifier, [tool.ruff] target-version,
# [tool.ty.environment] python-version, [tool.tox] env_list,
# [tool.tox.gh.python], and the matrix in .github/workflows/tests.yaml.
requires-python = ">=3.10"
```

- [ ] **Step 6: Add it to the release checklist**

In `RELEASING.md`, under "Creating a Release", add as a new first item in the numbered list:

```markdown
1. Check whether any supported Python version has reached end of life
   (<https://endoflife.date/python>). Dropping one narrows `requires-python`
   and is a breaking change: it needs its own release and a note in the
   release description, not a quiet ride along with other work.
```

Renumber the items that follow.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml RELEASING.md
git commit -m "docs: record the Python 3.10 end of life and what it touches

3.10 goes end of life on 2026-10-31. Support is not dropped here — that
narrows requires-python and belongs in its own release — but the date and the
seven places that change with it are now written down where someone cutting a
release will read them."
```

---

### Task 4: ruff rule groups B and S

**Files:**
- Modify: `pyproject.toml` (`[tool.ruff.lint]`)
- Modify: `src/edutap/wallet_google/handlers/fastapi.py` (7 × B904), `handlers/validate.py:334` (B904), `registry.py:223,238` (B007), `credentials.py:21` (B019)
- Modify: `src/edutap/wallet_google/clientpool.py:59`, `models/datatypes/enums.py:175,177` (S105)
- Modify: `tests/test_check_models.py:28` (B007), `tests/test_handler_validate.py:100` (B017), `tests/test_settings.py:44,52` (B018)

**Interfaces:**
- Consumes: `make lint` from Task 2.
- Produces: `select` containing `B` and `S`. Task 5 extends the same list with `D`.

- [ ] **Step 1: Enable B and S and see the full list**

In `pyproject.toml`, `[tool.ruff.lint]`:

```toml
select = ["B", "E", "F", "I", "S", "UP", "W"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
# assert *is* the test framework here; S101 in tests is not a finding.
"tests/**" = ["S101"]
```

Run: `.venv/bin/python -m ruff check src tests`

Expected: 15 `B` findings and 1 `S101` in `src`, plus 3 `S105`. The 404 `S101` in `tests` must be gone — if they are not, the `per-file-ignores` pattern is wrong.

- [ ] **Step 2: Fix the eight B904 findings**

Seven in `src/edutap/wallet_google/handlers/fastapi.py` (lines 39, 74, 96, 119, 126, 130, 135) and one in `src/edutap/wallet_google/handlers/validate.py:334`. Each is a `raise` inside an `except` block that drops the original traceback. The shape:

```python
    except ValueError as error:
        raise HTTPException(status_code=400, detail="…") from error
```

Use `from error` where the original exception adds information to a debugging session, and `from None` where the original is noise the caller must not see — for example when the original carries a credential or an internal path. Decide per site; do not apply one of them mechanically to all eight.

- [ ] **Step 3: Fix the four B007 findings**

`src/edutap/wallet_google/registry.py:223` (`name`), `:238` (`enum`), and `tests/test_check_models.py:28` (`name`). A loop control variable that is never used gets an underscore prefix:

```python
    for _name, value in mapping.items():
```

Do this only where the variable really is unused. If it turns out to be used further down, the finding was telling you the loop is wrong, not the name.

- [ ] **Step 4: Fix B017, B018 and B019**

- `tests/test_handler_validate.py:100` — `B017`, `pytest.raises(Exception)` asserts nothing useful, because every failure mode matches. Narrow it to the exception the code under test actually raises. If that is genuinely unknown, run the test and read what comes out.
- `tests/test_settings.py:44` and `:52` — `B018`, an expression whose value is discarded. Either it was meant to be an assertion, in which case make it one, or it is dead and gets deleted. Read the surrounding test before choosing.
- `src/edutap/wallet_google/credentials.py:21` — `B019`, `functools.cache` on a method keeps `self` alive for the process lifetime. This one is a design question, not a lint fix: the cache belongs on a module-level function keyed by the argument, or on the instance. If the class is a long-lived singleton the leak is bounded and a `# noqa: B019` with that reasoning is defensible — but write the reasoning.

- [ ] **Step 5: Annotate the three S105 false positives**

All three are `S105 hardcoded-password-string` matching on a *name*, not a value:

`src/edutap/wallet_google/clientpool.py:59`:

```python
        token_endpoint = "https://oauth2.googleapis.com/token"  # noqa: S105  # a URL, not a secret
```

`src/edutap/wallet_google/models/datatypes/enums.py:175` and `:177`:

```python
    GENERIC_SEASON_PASS = "GENERIC_SEASON_PASS"  # noqa: S105  # an enum member, not a secret
    GENERIC_PARKING_PASS = "GENERIC_PARKING_PASS"  # noqa: S105  # an enum member, not a secret
```

Per-line `noqa` rather than ignoring `S105` project-wide, so a genuinely hardcoded secret would still be caught.

- [ ] **Step 6: Deal with the one S101 in src**

It is at `src/edutap/wallet_google/api.py:316`.

An `assert` in library code is removed by `python -O` and must not be load-bearing. Read what it guards: if it is an invariant a caller could violate, it becomes a real `raise` with a message; if it is a developer note about something the type system already guarantees, delete it. Do not add a `# noqa` — that keeps a statement that vanishes under `-O`.

- [ ] **Step 7: Verify**

```bash
make lint
make test-local
```

Expected: both PASS, no `B` or `S` findings.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml src tests
git commit -m "style: enable ruff's bugbear and security rules

B found fifteen issues, eight of them raise statements inside except blocks
that discarded the original traceback, plus a functools.cache on a method.

S is almost entirely S101 in tests, which is what pytest is — ignored per
file rather than project-wide. The three S105 in src are a URL constant and
two enum members, annotated individually so a real hardcoded secret would
still be caught."
```

---

### Task 5: ruff rule group D

**Files:**
- Modify: `pyproject.toml` (`[tool.ruff.lint]`)
- Modify: most modules under `src/` and `tests/`

**Interfaces:**
- Consumes: the `select` list from Task 4.
- Produces: nothing consumed later.

Measured on `main` with `convention = "pep257"` set: 508 `D` findings, 201 after
`--fix --unsafe-fixes`, of which 144 are the "undocumented" `D1xx` rules and 57 are wording
and layout of docstrings that already exist.

The convention matters to those numbers. Without it there are 864 findings, because
`D212`, `D213`, `D415` and `D404` are all active; `pep257` switches off the ones that
belong to other conventions. It also resolves the `D203`/`D211` and `D212`/`D213`
incompatibility warnings on its own — verified, they disappear from ruff's output — so no
explicit `ignore` entry for them is needed.

- [ ] **Step 1: Enable D with the undocumented rules excluded**

In `pyproject.toml`, `[tool.ruff.lint]`:

```toml
select = ["B", "D", "E", "F", "I", "S", "UP", "W"]
ignore = [
    "E501",
    # The "undocumented public …" rules. 144 findings, every one of which needs
    # a docstring written rather than a fix applied. Enabling them now would buy
    # 144 hasty docstrings or a permanent blanket ignore. Write the docstrings,
    # then delete these lines — not the other way round.
    "D100",
    "D101",
    "D102",
    "D103",
    "D104",
    "D107",
]

[tool.ruff.lint.pydocstyle]
# Also settles the D203/D211 and D212/D213 incompatibilities, which ruff
# otherwise warns about on every single run.
convention = "pep257"
```

- [ ] **Step 2: Count what that leaves**

Run: `.venv/bin/python -m ruff check --statistics --select D src tests`

Expected: 364 findings — 508 minus the 144 now-ignored `D1xx`. If you see roughly 720, the `[tool.ruff.lint.pydocstyle]` block did not take effect; check it is a top-level table and not nested inside another.

- [ ] **Step 3: Apply the fixes and read the diff**

Only 2 of these are *safe* fixes; the other 305 need `--unsafe-fixes`. A separate safe-only commit would therefore contain two lines and waste a review round, so this is one commit — but one whose diff has to be read rather than trusted.

```bash
.venv/bin/python -m ruff check --select D --fix --unsafe-fixes src tests
.venv/bin/python -m ruff format src tests
git diff
```

`--unsafe-fixes` rewrites docstring *text*: it moves summary lines onto the first line, reflows single-line docstrings that were wrapped, and adjusts punctuation. Read it. A docstring that now says something false is worse than one that was merely punctuated wrongly, and ruff cannot tell the difference.

- [ ] **Step 4: Verify and commit**

```bash
make test-local
git add -A src tests
git commit -m "style: apply ruff's pydocstyle fixes

Almost all of these need --unsafe-fixes, which rewrites docstring text rather
than only layout, so the diff was read rather than trusted."
```

- [ ] **Step 5: Fix the 57 remaining by hand**

Run: `.venv/bin/python -m ruff check --select D src tests`

Expected: 57, in three kinds:

- `D401` (30) `non-imperative-mood` — "Returns the client" becomes "Return the client".
- `D205` (25) `missing-blank-line-after-summary` — insert a blank line between the one-line summary and the body.
- `D400` (2) `missing-trailing-period`.

`D401` is the one to be careful with: rewriting the mood is easy, but if the resulting sentence no longer describes what the function does, fix the sentence rather than the mood.

- [ ] **Step 6: Verify**

```bash
make lint
make test-local
```

Expected: both PASS, no `D` findings outside the ignored `D1xx`.

- [ ] **Step 7: Commit**

```bash
git add -A src tests
git commit -m "style: fix the docstrings ruff could not fix automatically

Mood, summary-line layout and punctuation across 57 docstrings. The 144
missing docstrings the D1xx rules would report stay ignored and are separate
work; see the comment in pyproject.toml."
```

---

### Task 6: Full verification and pull request preparation

**Files:** none modified.

**Interfaces:**
- Consumes: Tasks 1-5.
- Produces: a branch ready for review.

- [ ] **Step 1: Everything green from the Makefile**

```bash
make lint
make test-local
make test-matrix
```

Expected: all PASS. `test-matrix` builds five environments and is slow; it is also the only step that proves the dependency-group change works on every supported interpreter rather than just the one in `.venv`.

- [ ] **Step 2: Confirm no stale reference to the removed extras**

Run: `grep -rn "\[test\]\|\[typecheck\]\|\[develop\]\|test,develop" --exclude-dir=.git --exclude-dir=.venv .`

Expected: no hits in `pyproject.toml`, the workflows, `CONTRIBUTING.md`, `CLAUDE.md` or `RELEASING.md`. `.github/workflows/` installs tox rather than the extras, so it should already be clean — check rather than assume.

- [ ] **Step 3: Confirm `MANIFEST.in` is gone and nothing references it**

Run: `grep -rn "MANIFEST" --exclude-dir=.git --exclude-dir=.venv .`

Expected: no hits. In particular `[tool.check-manifest]` may still list entries that only made sense with it; leave the section, it is check-manifest's own configuration.

- [ ] **Step 4: Review the whole diff by area**

```bash
git diff main...HEAD -- pyproject.toml Makefile .pre-commit-config.yaml
git diff main...HEAD --stat -- src tests
```

The first is the substance and should be read line by line. The second is mostly docstring churn from Task 5 and is reviewed by its own commits.

- [ ] **Step 5: Write the pull request description**

Structure it by the five commits' subjects, and state:

1. `[test]`, `[typecheck]` and `[develop]` no longer exist — the install command is now `uv pip install -e ".[callback]" --group dev`. Anyone with a sibling checkout referencing the old extras has to change it.
2. The sdist lost about 40 files of CI configuration and internal notes; `src/` and `tests/` are unchanged, verified by a file-list diff.
3. Python 3.10 support is deliberately **not** dropped, and why.
4. The `D1xx` docstring rules are deliberately ignored, with the count (144) and where the comment explaining it lives.
5. The ty jump from 0.0.17 to 0.0.66 and anything it made necessary in `[tool.ty.rules]`.

- [ ] **Step 6: Stop**

Do not push. The user pushes and opens the pull request.
