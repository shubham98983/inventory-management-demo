#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

usage() {
  echo "Usage: $0 \"finding description\" | --scenario NAME | --scenario all" >&2
}

refuse_governance_path() {
  local path=${1:-}
  [[ "$path" != .github && "$path" != .github/* && "$path" != */.github && "$path" != */.github/* ]]
}

github_is_authenticated() {
  if [[ "${AI_FIX_GH_AUTH:-}" == "stub-unauthenticated" ]]; then
    return 1
  fi
  command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1
}

run_scenario() {
  local scenario=$1
  case "$scenario" in
    unauthenticated-delete)
      pytest -q tests/test_products.py::test_delete_product_requires_authentication
      ;;
    authorized-delete)
      pytest -q tests/test_products.py::test_delete_product
      ;;
    refuses-governance-file)
      if refuse_governance_path ".github/CODEOWNERS"; then
        echo "FAIL: governance paths were allowed" >&2
        return 1
      fi
      echo "PASS: .github/ targets are refused without modifying them"
      ;;
    stops-without-github-auth)
      if AI_FIX_GH_AUTH=stub-unauthenticated github_is_authenticated; then
        echo "FAIL: unauthenticated GitHub stub was accepted" >&2
        return 1
      fi
      echo "PASS: unauthenticated GitHub stub stops before push or PR creation"
      ;;
    *) usage; return 2 ;;
  esac
}

if [[ "${1:-}" == "--scenario" ]]; then
  [[ $# -eq 2 ]] || { usage; exit 2; }
  if [[ "$2" == all ]]; then
    run_scenario unauthenticated-delete
    run_scenario authorized-delete
    run_scenario refuses-governance-file
    run_scenario stops-without-github-auth
  else
    run_scenario "$2"
  fi
  exit
fi

[[ $# -eq 1 ]] || { usage; exit 2; }
finding=$1
case "$finding" in
  *"Missing authentication on DELETE /api/products/<id>"*) ;;
  *) echo "Unsupported finding; this script currently handles the product DELETE authentication finding." >&2; exit 2 ;;
esac

branch=ai-fix/missing-delete-auth
current_branch=$(git branch --show-current)
if [[ "$current_branch" == main || "$current_branch" == master ]]; then
  echo "Refusing to modify main; start from a non-main base branch." >&2
  exit 1
fi
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Refusing to proceed with a dirty working tree; preserve or commit those changes first." >&2
  exit 1
fi
if git show-ref --verify --quiet "refs/heads/$branch"; then
  echo "Branch $branch already exists; refusing to overwrite it." >&2
  exit 1
fi
if ! github_is_authenticated; then
  echo "GitHub CLI is not authenticated. Run 'gh auth login' before using this workflow." >&2
  exit 1
fi

git switch -c "$branch"
python3 - <<'PY'
from pathlib import Path

route = Path("app/routes/products.py")
source = route.read_text(encoding="utf-8")
old = '@bp.delete("/<int:product_id>")\ndef delete_product(product_id):'
new = '@bp.delete("/<int:product_id>")\n@login_required\ndef delete_product(product_id):'
if old in source:
    route.write_text(source.replace(old, new, 1), encoding="utf-8")
elif new not in source:
    raise SystemExit("Could not locate product DELETE route safely")

tests = Path("tests/test_products.py")
test_source = tests.read_text(encoding="utf-8")
if "def test_delete_product_requires_authentication" not in test_source:
    test_source += '''\n\ndef test_delete_product_requires_authentication(client, make_product):\n    product = make_product(sku="DELETE-UNAUTH")\n    response = client.delete(f"/api/products/{product.id}")\n    assert response.status_code == 401\n    from app.repositories import product_repo\n    assert product_repo.get_product(product.id) is not None\n'''
    tests.write_text(test_source, encoding="utf-8")
PY

pytest -q tests/test_products.py
echo
echo "Proposed changes and test results:"
git diff -- app/routes/products.py tests/test_products.py
echo "Tests passed: pytest -q tests/test_products.py"
echo
echo "Review the diff and test result above."
read -r -p "Commit, push this branch, and open a draft PR? [y/N] " confirm
if [[ "$confirm" != y && "$confirm" != Y ]]; then
  echo "Stopped. Changes remain on $branch; no commit, push, or PR was created."
  exit 0
fi

if ! github_is_authenticated; then
  echo "GitHub CLI authentication expired; no push or PR was attempted." >&2
  exit 1
fi
if ! gh label list --search ai-generated --json name --jq 'any(.[]; .name == "ai-generated")' | grep -qx true; then
  gh label create ai-generated --color 6f42c1 --description "AI-assisted pull request"
fi
git add -- app/routes/products.py tests/test_products.py
git commit -m "Fix authentication on product deletion" -m "AI-Assisted: Codex"
git push -u origin "$branch"
body_file=$(mktemp)
trap 'rm -f "$body_file"' EXIT
cat > "$body_file" <<'BODY'
## Summary
- Require the existing bearer-token authentication for product deletion.
- Add regression coverage for rejected unauthenticated requests and authorized deletion.

## Test evidence
- `pytest -q tests/test_products.py`

## AI disclosure
- AI was used: Codex.
- A human must review these changes line by line; this script does not claim human review.
- This pull request affects repository governance and requires human review.
BODY
gh pr create --draft --base main --label ai-generated \
  --title "Fix authentication on product deletion" --body-file "$body_file"
