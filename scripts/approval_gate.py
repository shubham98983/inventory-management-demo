#!/usr/bin/env python3
"""Evaluate the required team approvals for a pull request using the gh CLI."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

USERNAME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


class EvaluationError(Exception):
    """Raised when an AI pull request cannot be evaluated safely."""


@dataclass(frozen=True)
class Decision:
    passed: bool
    ai_generated: bool
    message: str
    missing: tuple[str, ...] = ()


def is_ai_generated(labels: list[Any], head_ref: str, commits: list[Any]) -> bool:
    if not isinstance(labels, list) or any(
        not isinstance(label, dict) or not isinstance(label.get("name"), str)
        for label in labels
    ):
        raise EvaluationError("Unexpected pull request label response")
    if not isinstance(commits, list) or any(
        not isinstance(commit, dict)
        or not isinstance(commit.get("commit"), dict)
        or not isinstance(commit["commit"].get("message"), str)
        for commit in commits
    ):
        raise EvaluationError("Unexpected pull request commit response")
    if any(
        label.get("name") == "ai-generated" for label in labels
    ):
        return True
    if head_ref.startswith(("ai/", "ai-fix/")):
        return True
    return any(
        "AI-Assisted:" in str(commit.get("commit", {}).get("message", ""))
        for commit in commits
        if isinstance(commit, dict)
    )


def parse_approvers(contents: str) -> list[str]:
    approvers: list[str] = []
    invalid: list[str] = []
    for line_number, raw in enumerate(contents.splitlines(), start=1):
        entry = raw.split("#", 1)[0].strip()
        if not entry:
            continue
        if not USERNAME.fullmatch(entry):
            invalid.append(str(line_number))
        elif entry.casefold() not in {name.casefold() for name in approvers}:
            approvers.append(entry)
    if invalid:
        raise EvaluationError("Malformed .github/APPROVERS entries on line(s): " + ", ".join(invalid))
    if not approvers:
        raise EvaluationError(".github/APPROVERS is missing or contains no usernames")
    return approvers


def _review_key(review: dict[str, Any]) -> tuple[str, int]:
    # submitted_at is the authoritative chronology; id makes equal timestamps deterministic.
    review_id = review.get("id")
    return (str(review.get("submitted_at") or ""), review_id if isinstance(review_id, int) else 0)


def evaluate(
    *,
    labels: list[Any],
    head_ref: str,
    commits: list[Any],
    author: str,
    head_sha: str,
    reviews: list[Any],
    approver_contents: str | None,
) -> Decision:
    ai = is_ai_generated(labels, head_ref, commits)
    if not ai:
        return Decision(True, False, "Non-AI pull request; team approval gate passed.")

    if not author or not head_sha:
        raise EvaluationError("Pull request author or current head SHA is unavailable")
    if approver_contents is None:
        raise EvaluationError("Could not read .github/APPROVERS from the base branch")
    required = [
        username for username in parse_approvers(approver_contents)
        if username.casefold() != author.casefold()
    ]

    latest: dict[str, dict[str, Any]] = {}
    for review in reviews:
        if not isinstance(review, dict):
            raise EvaluationError("Unexpected review response")
        user = review.get("user")
        username = user.get("login") if isinstance(user, dict) else None
        if not isinstance(username, str) or not username:
            # Deleted users can appear as null; their historical review cannot satisfy an approver.
            continue
        key = username.casefold()
        if key not in latest or _review_key(review) > _review_key(latest[key]):
            latest[key] = review

    missing = []
    for username in required:
        review = latest.get(username.casefold())
        if not review or review.get("state") != "APPROVED" or review.get("commit_id") != head_sha:
            missing.append(username)
    if missing:
        return Decision(False, True, "Missing current-head approvals: " + ", ".join(missing), tuple(missing))
    return Decision(True, True, "All required team approvals are valid for the current head SHA.")


def gh_json(*args: str) -> Any:
    try:
        result = subprocess.run(
            ["gh", "api", *args], check=True, capture_output=True, text=True,
            env=os.environ.copy(),
        )
    except FileNotFoundError as error:
        raise EvaluationError("GitHub CLI (gh) is unavailable") from error
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or f"gh api exited {error.returncode}"
        raise EvaluationError(f"GitHub API request failed: {detail}") from error
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise EvaluationError("GitHub CLI returned malformed JSON") from error


def _flatten_pages(value: Any) -> list[Any]:
    if not isinstance(value, list):
        raise EvaluationError("Unexpected paginated API response")
    flattened: list[Any] = []
    for page in value:
        if not isinstance(page, list):
            raise EvaluationError("Unexpected page in paginated API response")
        flattened.extend(page)
    return flattened


def run_from_github_event() -> Decision:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not event_path or not repository or not os.environ.get("GH_TOKEN"):
        raise EvaluationError("Required GitHub Actions event, repository, or GH_TOKEN context is missing")
    try:
        with open(event_path, encoding="utf-8") as event_file:
            event = json.load(event_file)
    except (OSError, json.JSONDecodeError) as error:
        raise EvaluationError("Could not read GitHub event payload") from error
    pull = event.get("pull_request")
    if not isinstance(pull, dict):
        raise EvaluationError("Event does not contain a pull request")
    number = pull.get("number") or event.get("number")
    if not isinstance(number, int):
        raise EvaluationError("Pull request number is unavailable")

    base = pull.get("base", {}).get("ref")
    head_sha = pull.get("head", {}).get("sha")
    head_ref = pull.get("head", {}).get("ref", "")
    author = pull.get("user", {}).get("login", "")
    if not isinstance(base, str) or not base or not isinstance(head_sha, str) or not head_sha:
        raise EvaluationError("Pull request base branch or head SHA is unavailable")

    pr = gh_json(f"repos/{repository}/pulls/{number}")
    commits = _flatten_pages(gh_json("--paginate", "--slurp", f"repos/{repository}/pulls/{number}/commits?per_page=100"))
    labels = pr.get("labels") if isinstance(pr, dict) else None
    if not isinstance(labels, list):
        raise EvaluationError("Unexpected pull request label response")

    if not is_ai_generated(labels, head_ref, commits):
        return Decision(True, False, "Non-AI pull request; team approval gate passed.")
    if not isinstance(pr, dict):
        raise EvaluationError("Unexpected pull request response")
    reviews = _flatten_pages(
        gh_json("--paginate", "--slurp", f"repos/{repository}/pulls/{number}/reviews?per_page=100")
    )

    # Avoid consulting PR-proposed configuration. Fetch only the base branch version.
    fetch = subprocess.run(
        ["git", "fetch", "origin", f"refs/heads/{base}:refs/remotes/origin/{base}"],
        capture_output=True,
        text=True,
    )
    if fetch.returncode:
        raise EvaluationError("Could not fetch base branch: " + (fetch.stderr.strip() or "git fetch failed"))
    config = subprocess.run(
        ["git", "show", f"origin/{base}:.github/APPROVERS"], capture_output=True, text=True
    )
    approvers = config.stdout if config.returncode == 0 else None
    return evaluate(
        labels=labels,
        head_ref=head_ref,
        commits=commits,
        author=author,
        head_sha=head_sha,
        reviews=reviews,
        approver_contents=approvers,
    )


def main() -> int:
    try:
        decision = run_from_github_event()
    except EvaluationError as error:
        print(f"::error::{error}", file=sys.stderr)
        return 1
    print(decision.message)
    return 0 if decision.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
