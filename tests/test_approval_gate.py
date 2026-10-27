import pytest

from scripts.approval_gate import (
    EvaluationError,
    _flatten_pages,
    evaluate,
    is_ai_generated,
    parse_approvers,
)


HEAD = "abc123"
APPROVERS = "# reviewers\nalice\nbob\n"


def review(user, state="APPROVED", commit_id=HEAD, submitted_at="2026-01-01T00:00:00Z", review_id=1):
    return {
        "user": {"login": user},
        "state": state,
        "commit_id": commit_id,
        "submitted_at": submitted_at,
        "id": review_id,
    }


def decide(reviews, *, author="author", config=APPROVERS, labels=None, branch="feature/change", commits=None):
    return evaluate(
        labels=labels if labels is not None else [{"name": "ai-generated"}],
        head_ref=branch,
        commits=commits or [],
        author=author,
        head_sha=HEAD,
        reviews=reviews,
        approver_contents=config,
    )


def test_non_ai_pr_passes_immediately():
    result = evaluate(
        labels=[], head_ref="feature/change", commits=[], author="author",
        head_sha=HEAD, reviews=[], approver_contents=None,
    )
    assert result.passed and not result.ai_generated


def test_ai_pr_with_all_required_approvals_passes():
    result = decide([review("alice"), review("bob", review_id=2)])
    assert result.passed


def test_missing_approvals_fail_and_report_usernames():
    result = decide([review("alice")])
    assert not result.passed
    assert result.missing == ("bob",)
    assert "bob" in result.message


def test_stale_head_approval_does_not_count():
    result = decide([review("alice", commit_id="old-head"), review("bob", review_id=2)])
    assert not result.passed
    assert result.missing == ("alice",)


def test_latest_review_supersedes_earlier_approval():
    result = decide([
        review("alice", "APPROVED", submitted_at="2026-01-01T00:00:00Z"),
        review("alice", "CHANGES_REQUESTED", submitted_at="2026-01-02T00:00:00Z", review_id=2),
        review("bob", review_id=3),
    ])
    assert not result.passed
    assert result.missing == ("alice",)


def test_pr_author_is_excluded_from_required_approvals():
    result = decide([review("bob")], author="alice")
    assert result.passed


@pytest.mark.parametrize(
    "labels,branch,commits",
    [
        ([{"name": "ai-generated"}], "feature/change", []),
        ([], "ai/fix-thing", []),
        ([], "ai-fix/thing", []),
        ([], "feature/change", [{"commit": {"message": "Fix\n\nAI-Assisted: Codex"}}]),
    ],
)
def test_all_ai_detection_rules(labels, branch, commits):
    assert is_ai_generated(labels, branch, commits)


def test_non_ai_rules_do_not_match_similar_names_or_trailers():
    assert not is_ai_generated([{"name": "not-ai-generated"}], "aifix/thing", [{"commit": {"message": "AI assisted"}}])


def test_unexpected_api_shapes_fail_closed():
    with pytest.raises(EvaluationError, match="label response"):
        is_ai_generated(["ai-generated"], "feature/change", [])
    with pytest.raises(EvaluationError, match="commit response"):
        is_ai_generated([], "feature/change", [None])
    with pytest.raises(EvaluationError, match="paginated API response"):
        _flatten_pages({"message": "API error"})


def test_missing_and_malformed_approver_configuration_fail_safely():
    with pytest.raises(EvaluationError, match="missing or contains no usernames"):
        parse_approvers("# nobody configured\n")
    with pytest.raises(EvaluationError, match="Malformed"):
        parse_approvers("alice\nnot a username\n")
    with pytest.raises(EvaluationError, match="Could not read"):
        decide([], config=None)


def test_comments_and_duplicate_approvers_are_supported():
    assert parse_approvers("# team\nalice # reviewer\nalice\n") == ["alice"]


def test_dismissed_latest_review_supersedes_approval():
    result = decide([
        review("alice", "APPROVED", submitted_at="2026-01-01T00:00:00Z"),
        review("alice", "DISMISSED", submitted_at="2026-01-02T00:00:00Z", review_id=2),
        review("bob", review_id=3),
    ])
    assert not result.passed
    assert result.missing == ("alice",)
