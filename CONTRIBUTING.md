# Contributing to edutap.wallet_google

Be excellent to each other!

All contributions are under the [EUPL 1.2](https://eupl.eu/).

Do not use material protected by copyright, patents or similar, only your very own work.

## We love contributions

When contributing to this repository, please first discuss the change you wish to make via issue, with the core contributors of this repository before making a change.

We encourage you to contribute to this project.
Contributing is possible by i.e.:
- spreading the word about this package
- reporting issues
- proposing changes/improvements to the documentation
- fixing issues
- improving tests
- proposing/discussing features
- implementing features

## Reporting issues

Issues are reported at the [packages issue tracker at Github](https://github.com/edutap-eu/edutap.wallet_google/issues).

Please search for existing issues on GitHub before reporting new ones.
This approach minimizes duplicates, streamlines issue management, and saves time for both reporters and maintainers.

Use the issue template addressing your problem.

## Pull Requests

First check if someone else already created a pull request solving your problem.
If so, get in contact with the author(s) and coordinate with them.

If you're the first, fork the repository and work on the code.
We recommend to create a branch in the fork too in order to make it easier to update the base branch.

Create a draft pull request after the first commit and mark it as draft.
This way you communicate your work to other developers, reducing the risk of duplicate work,

While working on the pull request ensure to run tests and linter before each commit and push.

If work is ready, remove the draft status from the PR to signalize readiness for review.

On of the core contributors will review, comment and - if all is fine - merge it.

## Dependency updates

Dependency updates arrive as pull requests from up to three bots, none of
which merges anything on its own:

- **Renovate** (hosted Mend app, configured in `renovate.json5`) watches the
  actions in `.github/workflows/` and the dependencies in `pyproject.toml`.
  It checks in before 4 AM every Monday, except for security advisories,
  which bypass the schedule and arrive immediately.
- **Dependabot** (`.github/dependabot.yml`) also watches
  `.github/workflows/`, in parallel with Renovate, on purpose, for a
  transition period: seeing two pull requests for the same action bump is
  the visible, harmless proof that Renovate is actually working here. Once
  Renovate has demonstrably opened pull requests and its "Dependency
  Dashboard" issue exists, one of the two gets switched off — that has not
  happened yet.
- **pre-commit.ci** watches the hook revisions in `.pre-commit-config.yaml`
  and opens a pull request monthly.

**Renovate currently opens no pull requests for `pyproject.toml`.** Every
entry in `[project.dependencies]` and `[project.optional-dependencies]` is
either a bare name with no version specifier (Renovate skips those outright:
`skipReason: "unspecified-version"`) or an open `>=` floor, which Renovate's
default range strategy leaves unchanged whenever the currently released
version already satisfies it — which an open floor always does. Do not
expect a Python dependency pull request from a routine Monday run. Adding
proper version ranges so Renovate can act on them is being addressed
separately, on `chore/package-modernisation`. Until that lands, the one
exception is a published *security advisory*: that bypasses the range logic
above and raises a floor immediately, any day of the week — see
`renovate.json5` for the mechanism, and keep Dependabot's security alerts
(a repository setting, independent of `dependabot.yml`) switched on, since
that is what feeds Renovate's advisory data too.

Renovate also maintains a "Dependency Dashboard" issue listing everything it
is holding back. If Renovate appears to have stopped, check that issue first.

## Documentation

We love improvements to the documentation.

We try to follow the [Diátaxis](https://diataxis.fr/) approach as best as we can.

The documentation for this package is written to be rendered with Sphinx and MyST (a Markdown dialect).
The actual documentation is located at our [documentation](https://github.com/edutap-eu/documentation/) repository.
This package is there included as Git submodule.
However, do not edit in a clone of the documentation repository, but here.

Follow the pull request path also for documentation changes.
