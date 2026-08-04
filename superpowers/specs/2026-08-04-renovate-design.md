# Renovate for dependency updates

Status: designed, ready to implement. Branched from `main` after PR #93
(`chore/drop-uv-lock`) landed.

**This goes to `main` first**, ahead of the `chore/httpx2-migration` branch. It helps
regardless of what else is in flight, and it is independent of the httpx2 work, which is
deliberately parked until authlib publishes its httpx2 release.

## Why

Today the only automation watching dependencies here is `.github/dependabot.yml`, and it
watches exactly one ecosystem: GitHub Actions, weekly. The Python dependencies in
`pyproject.toml` are watched by nothing.

`edutap.data_provider` already runs Renovate, and its
[`renovate.json5`](https://github.com/edutap-collective/edutap.data_provider/blob/main/renovate.json5)
is the reference for this. This spec follows it, and records every place where it
deliberately does not.

## How Renovate runs: the hosted app, not a workflow

Renovate runs as the **hosted Mend GitHub App**, installed on the `edutap-eu`
organisation. There is no workflow of ours driving it.

The reasoning is data_provider's, and it holds here: a self-hosted run authenticating with
`GITHUB_TOKEN` opens pull requests that GitHub refuses to let trigger workflows, so every
update would arrive untested. A self-hosted run using a **GitHub App token** does not have
that defect — app tokens do trigger workflows — so the objection is not absolute. It was
still rejected, on the grounds that the app-token route needs a GitHub App created and
installed on the organisation *plus* a workflow file and two repository secrets, where the
hosted app needs the install and nothing else. Same prerequisite, less machinery, and
consistent with data_provider.

**This requires a manual step that cannot be done from this branch:** installing the Mend
Renovate app on the `edutap-eu` organisation, or at minimum granting it this repository.
Until that happens the config file sits inert. The pull request description must say so.

## Configuration

`renovate.json5` at the repository root — JSON5, not JSON, so the reasoning for each rule
lives beside it. This file decides what turns up unasked in the pull request list, and a
rule nobody understands is a rule somebody switches off.

Carried over from data_provider:

- `extends: ["config:recommended", "schedule:earlyMondays"]` — a Monday morning batch gets
  read; a stream through the week gets dismissed.
- `timezone: "Europe/Berlin"`.
- **No automerge anywhere.** Green CI proves the suite still passes, not that the update is
  one we want.
- `packageRules` grouping GitHub Actions into one pull request and the
  `[project.optional-dependencies]` extras (`callback`, `test`, `typecheck`, `develop`)
  into another, since none of that reaches a consumer of the library. Runtime dependencies
  stay ungrouped: each one gets a pull request about that library.

Deliberately **not** carried over:

- **`:enablePreCommit`.** data_provider enables it because its pre-commit revisions are
  otherwise unwatched. This repository's `.pre-commit-config.yaml` has a `ci:` block with
  `autoupdate_schedule: monthly`, so pre-commit.ci already opens those pull requests — PR
  #94 was one. Enabling Renovate's pre-commit manager here would duplicate them, the same
  trap as running Dependabot and Renovate on GitHub Actions at once. The JSON5 comment
  records this, so a later reader does not mistake the omission for an oversight.
- **`lockFileMaintenance` on `uv.lock`.** Renovate's `pep621` manager supports uv
  lockfiles, but PR #93 stopped tracking `uv.lock` on the grounds that a library's
  consumers never read it. There is no lockfile left to maintain.
- **The `dockerfile` manager rule.** data_provider ships a service image whose Dockerfile
  hardcodes a `site-packages` path tied to the Python base image. Nothing here does.

New here: `ruff` is pinned by revision in `.pre-commit-config.yaml` rather than as a
version range in `pyproject.toml`, so it arrives through pre-commit.ci and needs no
Renovate rule of its own. data_provider gives `ruff` a dedicated rule because it *is* a
`pep621` dependency there.

## Dependabot

`.github/dependabot.yml` is deleted. It covers only GitHub Actions, which Renovate now
covers, and leaving both configured produces two pull requests for every action bump — it
is demonstrably active, PR #91 bumped `actions/checkout` from 6 to 7. data_provider has no
`dependabot.yml`.

This does **not** turn off Dependabot **security alerts** — those are a repository setting,
not something `dependabot.yml` controls, and they stay on. The nineteen open alerts were
addressed by PR #93 removing the lockfile they all originated from, not by this branch.

## Risks

- **Nothing happens until the app is installed.** The failure mode is silence, not an
  error. Whoever merges this needs to check that the dependency dashboard issue appears.
- **First run is noisy.** `config:recommended` opens a pull request per outstanding
  update. Expected once, on the first Monday after installation.
