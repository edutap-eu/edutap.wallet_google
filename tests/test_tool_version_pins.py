"""Keep the ruff and ty version pins in sync between two files that duplicate them.

``pyproject.toml``'s ``dependency-groups.lint``/``.typecheck`` entries and
``.pre-commit-config.yaml``'s ``rev:`` lines both pin ruff and ty, and both
files carry a comment claiming the two "cannot silently disagree" — but
nothing enforced that claim. pre-commit.ci rewrites the ``rev:`` lines on its
monthly autoupdate schedule regardless of the ``ci: skip:`` list, so the pins
can drift apart with no failure anywhere except a confusing local/CI mismatch
weeks later. These tests make that drift a fast, obvious test failure instead.
"""

from pathlib import Path

import re


REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_TEXT = (REPO_ROOT / "pyproject.toml").read_text()
PRE_COMMIT_CONFIG_TEXT = (REPO_ROOT / ".pre-commit-config.yaml").read_text()


def _dependency_group_floor(package: str) -> str:
    """Return the floor version pinned for ``package`` in a dependency group."""
    match = re.search(rf'"{re.escape(package)}>=([0-9.]+)', PYPROJECT_TEXT)
    assert match, f"no {package!r} floor found in pyproject.toml's dependency-groups"
    return match.group(1)


def _pre_commit_rev(repo_url: str) -> str:
    """Return the ``rev:`` pinned for the pre-commit repo at ``repo_url``."""
    match = re.search(
        rf"-\s+repo:\s+{re.escape(repo_url)}.*?rev:\s+v?([0-9.]+)",
        PRE_COMMIT_CONFIG_TEXT,
        re.DOTALL,
    )
    assert match, f"no rev: found for repo {repo_url!r} in .pre-commit-config.yaml"
    return match.group(1)


def test_ruff_version_matches_across_pyproject_and_pre_commit():
    group_floor = _dependency_group_floor("ruff")
    hook_rev = _pre_commit_rev("https://github.com/astral-sh/ruff-pre-commit")
    assert group_floor == hook_rev, (
        f"pyproject.toml pins ruff>={group_floor} but .pre-commit-config.yaml "
        f"pins rev: v{hook_rev} — update both together."
    )


def test_ty_version_matches_across_pyproject_and_pre_commit():
    group_floor = _dependency_group_floor("ty")
    hook_rev = _pre_commit_rev("https://github.com/astral-sh/ty-pre-commit")
    assert group_floor == hook_rev, (
        f"pyproject.toml pins ty>={group_floor} but .pre-commit-config.yaml "
        f"pins rev: v{hook_rev} — update both together."
    )
