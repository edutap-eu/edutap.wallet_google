# Package modernisation: Makefile, packaging metadata, tool pins, linter rules

Status: designed, ready to implement.

## Why

The package is already on the current toolchain in the ways that matter most — uv drives
CI and tox, ruff is the only linter and formatter, ty is the type checker, the tox matrix
lives in `[tool.tox]` as native TOML, and the version comes from `hatch-vcs`. What is left
are four gaps, each verified rather than assumed:

1. There is no `Makefile`, so there is no uniform entry point to the common workflows.
2. Two things carry a silent expiry date: the `ty` pin and Python 3.10 support.
3. Two packaging standards the project can now adopt — one of which its own `pyproject.toml`
   already carries a TODO for — plus an `sdist` that ships internal working documents.
4. The ruff rule selection is narrower than the project standard.
5. None of the repository's Python dependencies are actionable by Renovate — not because
   Renovate is misconfigured, but because of how they are declared here, verified from
   Renovate's source during a sibling branch's review.

These are grouped into five parts below. They land on one branch,
`chore/package-modernisation`, because they overlap heavily in `pyproject.toml` and
splitting them would mean five branches rebasing over each other for the same file.

## Part 1: Makefile and prek

### Makefile

`edutap.data_provider` already has one, and it is the template: a `PYTHON := .venv/bin/python`
variable, a self-documenting `help` default goal, and `venv` as a prerequisite of every
other target so no one runs `make lint` against a missing environment.

The targets, matching the project standard:

| Target | Does |
| --- | --- |
| `help` | lists the targets (default goal) |
| `venv` | `uv venv` plus `uv pip install -U -e ".[callback]" --group dev` |
| `lint` | `ruff check`, `ruff format --check`, `ty check` |
| `reformat` | `ruff format`, `ruff check --fix` |
| `test-local` | `pytest` — the unit suite |
| `test-integration` | `pytest --run-integration` — needs Google credentials |
| `test-matrix` | `uvx --with "tox-uv,tox-gh" tox` — every supported Python |

`test-matrix` is this package's third suite, in the slot the standard leaves open for
"further, more expensive suites". It is separate from `test-local` because it builds five
interpreters' worth of environments.

Tools are called through `$(PYTHON) -m …` rather than `uv run`, for data_provider's
recorded reason: this package declares an entry point group, and a bare `uv run` resolves
it against the whole environment.

### prek

`prek` replaces `pre-commit` as the local hook runner. It reads the same
`.pre-commit-config.yaml`, so nothing about the hooks changes — only the two tox
environments `format` and `lint`, whose `deps` and `commands` name `pre-commit` today.

pre-commit.ci keeps running server-side on the real `pre-commit`; the two coexist by
design, and the `ci:` block in `.pre-commit-config.yaml` is untouched.

## Part 2: Packaging metadata

### PEP 639 — the TODO in `pyproject.toml` is now redeemable

`pyproject.toml` carries an eight-line comment asking for the SPDX license expression
"when implemented in PyPI, twine, pyroma, etc." It is implemented. Verified by building a
throwaway package with hatchling 1.31:

```
Metadata-Version: 2.4
License-Expression: EUPL-1.2
License-File: LICENSE
```

So `license = { text = "EUPL 1.2" }` becomes `license = "EUPL-1.2"`, `license-files =
["LICENSE"]` is added, the `License :: OSI Approved :: …` classifier goes (PEP 639 forbids
carrying both), and the TODO block is deleted.

### PEP 735 — dev dependencies are not extras

`test`, `typecheck` and `develop` are declared as extras today, which publishes them in the
wheel metadata even though no consumer of the library would ever install
`edutap.wallet-google[test]`. They become `[dependency-groups]`, which is the standard for
exactly this, and `develop` is renamed `dev` in the move — free, because dependency groups
are not published metadata.

`callback` stays a real extra. It is the one a consumer genuinely installs.

**The self-reference has to go.** The `test` extra currently begins with
`"edutap.wallet-google[callback]"`. Inside `[project.optional-dependencies]` that is a
well-defined recursive self-reference; inside a dependency group it is not special-cased at
all and would be resolved against an index, i.e. it would pull the *published* package from
PyPI over the local checkout. So `callback` comes off the group and onto the install
command, and `dev` pulls the other groups in through `include-group`:

```toml
[project.optional-dependencies]
callback = ["fastapi"]

[dependency-groups]
test = ["freezegun", "pytest", "pytest-asyncio", "pytest-cov", "pytest-explicit", "respx", "tox"]
typecheck = ["ty"]
dev = [
    {include-group = "test"},
    {include-group = "typecheck"},
    "pdbp>=1.7.1",
]
```

Verified in a throwaway project: `uv pip install -e ".[callback]" --group dev` resolves the
local editable package, the extra and all three groups transitively. tox 4.58 ships native
`dependency_groups` support (`tox/tox_env/python/dependency_groups.py`, registered as a
config key in `tox_env/python/runner.py`) and accepts it alongside `extras`, so the tox
environments change from `extras = ["test", "develop"]` to `extras = ["callback"]` plus
`dependency_groups = ["dev"]`.

### The sdist ships internal working documents

`MANIFEST.in` is dead. It is a setuptools file, hatchling does not read it, and the sdist
proves it: `MANIFEST.in` says `recursive-exclude docs *` and `recursive-exclude .claude *`,
yet an sdist built from `main` contains both. The full top level of the current sdist:

```
.claude  .dockerignore  .editorconfig  .github  .gitignore  .pre-commit-config.yaml
CLAUDE.md  CONTRIBUTING.md  LICENSE  MANIFEST.in  PKG-INFO  README.md  RELEASING.md
docs  examples  pyproject.toml  src  superpowers  tests
```

108 files, including `superpowers/` (internal specs and plans), `CLAUDE.md`, `.claude/` and
the CI configuration. None of that belongs in a distribution on PyPI.

The fix is an explicit `[tool.hatch.build.targets.sdist]` section. `tests/` **stays** — a
consumer packaging this for a distribution wants to run the suite — and so do `README.md`,
`LICENSE`, `CONTRIBUTING.md` and `pyproject.toml`. Everything else at the top level goes,
and `MANIFEST.in` is deleted with it.

`check-manifest` stays as a hook. Its job — noticing that a file tracked in git is missing
from the sdist — is still worth doing, and it is the thing that will complain if the new
`sdist` section is too aggressive.

## Part 3: The two things with an expiry date

### The `ty` pin cannot be updated by anything

`.pre-commit-config.yaml` runs ty as a `local` hook: `entry: uvx ty@0.0.17 check`. That pin
is at 0.0.17; ty is at 0.0.66. Nothing will ever move it — pre-commit's `autoupdate` only
rewrites the `rev:` of remote repositories, and no Renovate manager reads a version out of
an `entry` string. It has been stuck for 49 releases and would stay stuck.

`astral-sh/ty-pre-commit` exists and is the official hook repository. Switching to it puts
the version in a `rev:` where pre-commit.ci's monthly autoupdate can reach it:

```yaml
-   repo: https://github.com/astral-sh/ty-pre-commit
    rev: v0.0.66
    hooks:
    -   id: ty
```

The hook is `pass_filenames: false` and `always_run: true`, matching the current local
hook's behaviour.

This section originally expected `ty` to come out of the `skip:` list in the `ci:` block
once it was a remote hook, hedged with "unless it turns out to be too slow there".
**Measured on PR #96: it stays skipped, and the reason is not slowness.** The hook's entry
is `uv check --quiet --preview-features=check-command --ty-version=0.0.66`, and `uv check`
builds the project, which resolves `build-system.requires` against PyPI. pre-commit.ci
disables network access while hooks run, so the build fails with
`dns error: Temporary failure in name resolution` before ty type-checks anything. That is
architectural — no pin, rev bump or timeout setting changes it — and it applies to any
hook that resolves dependencies at run time, not just this one.

The hedge's conclusion still holds, and is the actual point of the change: the *revision*
is maintained either way, because `rev:` is what pre-commit.ci's monthly autoupdate
rewrites, whether or not the hook is in `skip:`. And ty is not left unchecked — the
GitHub Actions `lint` job runs `tox -e lint`, which runs every hook including ty, with
network available. Verified passing at v0.0.66 on PR #96.

Given ty is pre-1.0 and moves fast, expect the jump from 0.0.17 to 0.0.66 to surface new
diagnostics. `[tool.ty.rules]` already downgrades four rules to warnings; anything new gets
the same treatment or a fix, and the jump is its own commit so the noise is reviewable.

### Python 3.10 reaches end of life on 2026-10-31

That is under three months away. The package declares `requires-python = ">=3.10"` and
tests py310 through py314.

**Support is not dropped in this branch.** 3.10 is still supported today, and narrowing
`requires-python` in a published library is a breaking change for consumers — it belongs in
its own release with its own note, not smuggled into a modernisation branch.

What this branch does is make sure it is not forgotten: a dated comment beside
`requires-python` naming the date and listing every place that changes with it
(`requires-python`, `classifiers`, `[tool.ruff] target-version`, `[tool.ty.environment]
python-version`, `[tool.tox] env_list`, `[tool.tox.gh.python]`, the CI matrix in
`tests.yaml`), plus a line in `RELEASING.md`.

## Part 4: ruff rule groups

Current selection is `["E", "F", "W", "I", "UP"]`. The project standard also names `B`
(bugbear), `S` (bandit/security) and `D` (pydocstyle). Measured against the code on `main`
with ruff 0.16.1:

### B — 15 findings, all worth fixing

```
8  B904  raise-without-from-inside-except
3  B007  unused-loop-control-variable
2  B018  useless-expression
1  B017  assert-raises-exception
1  B019  cached-instance-method
```

`B904` is the substantive one: eight `raise` statements inside `except` blocks that lose
the original traceback. `B019` (`cached-instance-method`) is a genuine memory-leak class of
bug and needs looking at rather than silencing.

### S — 408 findings, of which 4 are in `src` and 3 of those are false positives

```
src:    3 S105 hardcoded-password-string, 1 S101 assert
tests:  404 S101 assert
```

`S101` in tests is what pytest is: `per-file-ignores` for `tests/**`. The three `S105` are
a `token_endpoint` URL constant, an enum member named `GENERIC_SEASON_PASS`, and one
further match — each gets a `# noqa: S105` with the reason, not a blanket ignore, so a real
hardcoded secret would still be caught.

### D — 508 findings, 201 after autofix, 57 after excluding the undocumented rules

`D` is enabled together with `[tool.ruff.lint.pydocstyle] convention = "pep257"`. The
convention is not cosmetic: without it there are 864 findings rather than 508, because
`D212`, `D213`, `D415` and `D404` are all active, and those belong to conventions this
project does not follow. It also settles the `D203`/`D211` and `D212`/`D213`
incompatibilities that ruff otherwise warns about on every run, so no explicit `ignore`
entry is needed for them — verified, the warnings disappear.

Measured on a scratch copy with the convention set: `ruff check --select D --fix
--unsafe-fixes` takes 508 down to 201. What is left splits cleanly:

| | Count | Nature |
| --- | --- | --- |
| `D100`/`D101`/`D102`/`D103`/`D104`/`D107` | 144 | missing docstrings — writing prose |
| `D401`, `D205`, `D400` | 57 | wording and layout of docstrings that exist |

So `D` is enabled with the `D1xx` "undocumented" rules ignored, the 57 remaining fixed by
hand, and writing the 144 missing docstrings left as separate future work. Enabling `D1xx`
now would mean either 144 hastily-written docstrings or a permanent blanket ignore, and
both are worse than an honest, narrow exclusion.

Only 2 of the fixes are *safe*; the other 305 need `--unsafe-fixes`, which rewrites
docstring text rather than only layout. That pass is therefore reviewed rather than
trusted — but it is not worth splitting off a safe-only commit containing two lines.

## Part 5: Dependency version constraints, so Renovate has something to act on

A sibling branch, `chore/renovate` (PR #95), added a Renovate configuration to this
repository. Its review turned up something the Renovate configuration itself cannot fix:
measured against `pyproject.toml` on `main`, Renovate can act on none of the Python
dependencies.

| Block | Entries | Actionable | Why not |
| --- | --- | --- | --- |
| `[project.dependencies]` | 6 | 0 | `httpx`, `joserfc` are bare names; `authlib>=1.7.2`, `cryptography>=48.0.1`, `pydantic-settings>=2.14.2`, `pydantic[email]>=2.0` are open floors |
| `[project.optional-dependencies]` | 11 | 0 | ten bare names (`fastapi`, `freezegun`, `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-explicit`, `respx`, `tox`, `ty`, and the `edutap.wallet-google[callback]` self-reference); one open floor, `pdbp>=1.7.1` |
| `[build-system.requires]` | 2 | 0 | `hatchling`, `hatch-vcs`, both bare |

### The mechanism

Confirmed by running Renovate itself against the repository (`--dry-run=full`, v44.11.6),
not only by reasoning from its source. An earlier version of this section relied on the
source-code mechanism alone and got the next section's conclusion wrong — see "Floors are
necessary but not sufficient" below for what the dry run corrected.

Two separate reasons produce the same zero in the table above:

A dependency with no version operator at all — `httpx`, `joserfc`, and the ten bare names
above — gets `skipReason: "unspecified-version"` in Renovate's pep621 manager and is
skipped before any update logic runs. The dry run reports exactly 15 of these.

A dependency with an open `>=` floor and no ceiling *is* processed, but the pep621
manager's default `rangeStrategy` is `replace`, and `replace` only rewrites a range when
the candidate version does not already satisfy it. An open floor is satisfied by every
future release by construction, so `replace` returns the range unchanged forever. This is
not specific to runtime dependencies — it is exactly why `pdbp>=1.7.1` is equally inert
today, and the dry run confirms it: `authlib`, `cryptography`, `pydantic-settings`,
`pydantic` and `pdbp` are all extracted with no `skipReason`, and not one of them produces
an update.

The one thing that does move an open floor without a config change is a security advisory:
Renovate's `vulnerabilityAlerts` preset defaults `rangeStrategy` to `bump` with no lockfile
involved, `prCreation` to `"immediate"`, and `schedule` to empty — none of the usual
scheduling or range-preservation rules apply to a vulnerability fix. That is not
hypothetical: it is how `authlib>=1.7.2`, `cryptography>=48.0.1` and
`pydantic-settings>=2.14.2` reached their current floors, in PR #93 ("chore: stop tracking
uv.lock and raise runtime dependency floors").

So Renovate's effective coverage of this repository, as configured on `chore/renovate`
before this part, is GitHub Actions and nothing in `pyproject.toml`: the dry run's only two
proposed branches, repository-wide, are `renovate/astral-sh-setup-uv-9.x` and
`renovate/hynek-build-and-inspect-python-package-3.x`.

### Runtime dependencies keep their open floors

This is deliberate, not an oversight left for later. An upper bound on a *library's*
runtime dependency creates an unsolvable resolution conflict for every consumer who needs
a newer release of that dependency for a reason of their own — this package does not get
to decide that for them. The floors themselves are security floors: the comment already
sitting above `[project.dependencies]` says "Keep them as floors, not equalities," and that
comment is untouched by this plan.

`rangeStrategy: "bump"` — the fix this part applies elsewhere, see below — is rejected here
project-wide for the identical reason a ceiling is: it would ratchet every runtime floor to
the newest release on every publication of `authlib`, `cryptography`, and the rest, forcing
every downstream consumer onto that floor in lockstep with a package they may not otherwise
need to touch. That contrast is exactly why `bump` is safe for the dependency groups below
and rejected here: nothing downstream resolves a dependency group, but every consumer of
this library resolves `[project.dependencies]`.

The one path that legitimately moves a runtime floor is exactly the one already in use — a
`vulnerabilityAlerts`-triggered PR, as in PR #93. Nothing in this part changes that path or
touches the six entries in `[project.dependencies]`. This is written down here so it
survives contact with someone who, on seeing the Renovate coverage table above,
"helpfully" adds ceilings to fix it.

### Floors are necessary but not sufficient

The first version of this part said "every entry gets at least a floor" and treated that as
the fix. It is necessary — an unfloored entry is skipped outright — but the dry run showed
it is not sufficient: `pdbp>=1.7.1` is the control case. It was already a floored,
already-a-dependency-group-shaped entry before any of this part's other changes, and
Renovate's dry run still produced nothing for it, for the mechanism reason above —
`replace` leaves a satisfied floor untouched. Giving every other entry in
`[dependency-groups]` the same kind of open floor would have reproduced exactly the same
nothing. Two branches, both GitHub Actions, is what the whole repository's Renovate
configuration currently proposes; zero of them touch a Python dependency.

The fix is pairing the floor with `rangeStrategy: "bump"` on the packageRule that matches
these entries in `renovate.json5` — not on the manager or the repository as a whole, only
on the rule that already groups them as "development dependencies." `bump` raises the floor
itself to each new release, rather than leaving a satisfied floor alone. That is exactly the
mechanism the `vulnerabilityAlerts` preset already uses for a security advisory (previous
section); this part turns it on permanently, but only for the entries where doing so is
free — nothing downstream resolves a dependency group, an optional extra nobody but this
repository's own tooling installs, or `[build-system.requires]`, so ratcheting all three
forward on every release costs no consumer anything. `[project.dependencies]` gets none of
this, for the reason in the previous section.

`renovate.json5` is not in this checkout. It lives on `chore/renovate` (PR #95), still
open. This branch can state the rule change here and write it into the implementation plan,
but cannot make the edit until #95 merges to `main` and `chore/package-modernisation` is
rebased onto the result — see Global Constraints in the plan, and Task 1's final steps.

### The non-published dependencies get real version constraints

After this plan's Task 1, everything except `callback` lives in `[dependency-groups]`, and
a dependency group is never written into the wheel or sdist metadata — nothing that
installs this package as a dependency ever resolves it. Constraining these costs a
consumer of the library nothing, which is what makes `bump` safe for them; the constraint
itself is what stops Renovate skipping them outright.

Every entry gets at least a floor, and the floor is the version measured resolving in a
fresh install on 2026-08-05 — `uv venv` followed by `uv pip install -e
".[callback,test,typecheck]"` in a clean checkout, cross-checked against the version PyPI
reports as current the same day — not a guess:

| Dependency | Floor | Source |
| --- | --- | --- |
| `fastapi` | `>=0.141.1` | fresh install |
| `freezegun` | `>=1.5.5` | fresh install |
| `pytest` | `>=9.1.1` | fresh install |
| `pytest-asyncio` | `>=1.4.0` | fresh install |
| `pytest-cov` | `>=7.1.0` | fresh install |
| `pytest-explicit` | `>=1.0.1` | fresh install |
| `respx` | `>=0.23.1` | fresh install |
| `tox` | `>=4.58.0` | fresh install |
| `pdbp` | `>=1.7.1` (unchanged) | already floored, for an unrelated reason — see its own comment; the entry `bump` is defined against |

Two tools get a ceiling as well as a floor. With `bump` in place this is no longer what
makes them visible to Renovate — every entry in the group gets that from `bump` regardless
of a ceiling — so the ceilings are kept on their own merits, not as part of the
actionability mechanism:

- **`ruff`** — a minor release changes what the linter flags and reformats files that were
  correct under the previous minor. This is exactly `edutap.data_provider`'s own
  `ruff>=0.16,<0.17`, and the floor here — `>=0.16.1,<0.17` — is the version currently
  pinned in `.pre-commit-config.yaml` (`v0.16.1`) and confirmed as PyPI's latest release on
  2026-08-05, so the pre-commit hook and the dependency-group entry cannot silently
  disagree. `ruff` was not previously a project dependency at all — it only ever ran inside
  `pre-commit`/`prek`'s own isolated environment — so this also closes a latent gap: without
  it, `make lint`'s `$(PYTHON) -m ruff …` (Task 2) would have nothing installed to find. The
  ceiling means `bump` can keep advancing the floor silently through patch releases inside
  `0.16.x`, which ruff's own release policy keeps behaviour-stable, while a release that
  crosses into `0.17` still needs a deliberate ceiling change — whether `bump` actually
  respects an upper bound that way, rather than proposing to jump straight past it, is
  unverified and worth checking the first time Task 1's Step 13 dry run sees a `0.17`
  release available.
- **`ty`** — pre-1.0 and moving fast enough that this plan's Task 3 jumps it 49 releases in
  one commit. `ty`'s releases are all `0.0.x`; there is no separate minor line to float
  within, so the ceiling — `>=0.0.66,<0.0.67` — pins the exact current release, meaning
  every single subsequent release needs a deliberate ceiling change and a look at the
  diagnostics it adds (per Task 3), `bump` or not. That is the right amount of friction for
  a tool this early in its life.

`[build-system.requires]` gets floors too, and — since it is exactly as unpublished as a
dependency group — the same `bump` rangeStrategy, via the same `renovate.json5` rule
extended to match it:

- **`hatchling`** needs one anyway, for a reason independent of Renovate: this plan's Task 1
  adopts PEP 639, and `license = "EUPL-1.2"` with `license-files = ["LICENSE"]` only
  produces a `Metadata-Version: 2.4` build with `License-Expression`/`License-File` fields
  from a hatchling that understands the array-of-strings form of `license-files`. Verified
  by building a throwaway package against four hatchling releases: 1.24.0 and 1.25.0 reject
  the syntax outright (`TypeError: Field 'project.license-files' must be a table` — the
  pre-PEP-639 table-of-globs form); 1.26.0 through 1.26.3 accept it without error but
  silently build `Metadata-Version: 2.3` with no license fields at all; 1.27.0 is the first
  release that emits `Metadata-Version: 2.4`, `License-Expression: EUPL-1.2`,
  `License-File: LICENSE`. The floor is `hatchling>=1.27.0` — the minimum that makes Task
  1's own change work, not merely the version that happens to be installed today (1.31.0).
  This makes Task 1's implicit requirement explicit instead of leaving it to be discovered
  as an opaque, silent metadata downgrade.
- **`hatch-vcs`** has no such constraint driving it; its floor, `>=0.5.0`, is simply the
  version PyPI reports as current on 2026-08-05.

### The `renovate.json5` change this depends on

The floors above are this branch's job and land in Task 1 regardless. The pairing with
`rangeStrategy: "bump"` is a `renovate.json5` edit, and that file does not exist on
`chore/package-modernisation` — it is being added by the sibling `chore/renovate` branch
(PR #95), still open at the time of writing. Concretely, the "development dependencies"
packageRule there currently reads `matchDepTypes: ["project.optional-dependencies"]`; after
Task 1 moves most of what it matches into `[dependency-groups]`, that needs to become
`matchDepTypes: ["project.optional-dependencies", "dependency-groups",
"build-system.requires"]` with `rangeStrategy: "bump"` added — folding
`build-system.requires` into the same rule closes a gap `chore/renovate`'s own comment
already flags ("build-system.requires … match neither rule … acknowledged rather than given
a third rule"), rather than leaving it to become a second, near-identical rule.

This branch can write that change down — Task 1's Steps 12-13 do — but cannot commit it
until #95 merges to `main` and `chore/package-modernisation` is rebased onto the result.
Until then, this part's floors are real and the `bump` pairing is designed but not yet
applied.

## Non-goals

Writing the 144 missing docstrings. Dropping Python 3.10. Replacing tox, hatchling or
pytest. Adding a local `docs/conf.py` — the documentation is built centrally for
docs.edutap.eu, and giving this repository a second, divergent Sphinx configuration would
create a build that agrees with nothing. It is a real gap, noted here so it is not
rediscovered, and it needs a decision at the level of the whole eduTAP documentation
tree rather than in this package. **Adding upper bounds to the six runtime dependencies in
`[project.dependencies]`** — Part 5 explains why that is a deliberate non-goal, not
something left for later: it would break dependency resolution for consumers.

## Risks

- **The ty jump from 0.0.17 to 0.0.66 will surface diagnostics.** Expected, its own commit.
- **The `--unsafe-fixes` docstring pass touches a lot of files.** Its whole value is the
  reviewable diff; anyone merging without reading it gets what they deserve.
- **The new `[tool.hatch.build.targets.sdist]` could exclude something needed.** The check
  is a file-list comparison of the sdist before and after, not a guess. `check-manifest`
  stays as the second net.
- **Renaming the `develop` extra to a `dev` group breaks anyone installing
  `edutap.wallet-google[develop]`.** That is a development-only extra of a library, so the
  blast radius is this repository and any sibling checkout that names it. `grep` for it
  before merging.
- **The `ruff` and `ty` ceilings mean every one of their releases needs a manual (or
  Renovate-proposed) bump, not just the ones that matter.** That is the intended trade-off
  for two tools whose minor releases change behaviour — see Part 5 — but it means more
  version-bump PRs to review than the other dependency-group entries generate.
- **The `renovate.json5` half of Part 5 cannot land with this branch.** It depends on PR
  #95 merging first; until then the floors this branch adds are real but inert in exactly
  the way `pdbp>=1.7.1` already is. Task 1's Steps 12-13 exist to make sure that edit does
  not get forgotten once #95 merges — the floors alone are easy to mistake for "done."
- **Whether Renovate's `bump` strategy respects an explicit ceiling, rather than proposing
  to jump straight past it, is asserted here but not yet verified against this repository.**
  The first dry run that sees a release cross one of the `ruff`/`ty` ceilings (Task 1, Step
  13) is the actual test.

## Verification

`make lint`, `make test-local` and `make test-matrix` all green. An sdist built before and
after, with the two file lists diffed explicitly. `uv pip install -e ".[callback]" --group
dev` resolving in a clean environment. A wheel's `METADATA` showing
`License-Expression: EUPL-1.2`. Every entry in `[dependency-groups]`, the `callback`
extra, and `[build-system.requires]` carrying a version constraint — `grep` confirms no
bare names remain — with `ruff`'s floor matching what `.pre-commit-config.yaml` pins, so
`make lint` and the pre-commit hook cannot silently run different versions. Once #95 has
merged and this branch is rebased: a Renovate dry run (`--dry-run=full`) showing the
`development dependencies` rule's entries extracted with `rangeStrategy: "bump"` and no
`skipReason` — the same dry run that, before the `renovate.json5` change, produced only
two branches repository-wide and none for a Python dependency.
