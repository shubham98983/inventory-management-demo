#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 [--dry-run] [minimum-approvals]" >&2
}

dry_run=false
minimum=1
minimum_set=false
for argument in "$@"; do
  case "$argument" in
    --dry-run) dry_run=true ;;
    -* ) usage; exit 2 ;;
    * )
      if [[ "$minimum_set" == true ]]; then usage; exit 2; fi
      minimum="$argument"
      minimum_set=true
      ;;
  esac
done

if ! [[ "$minimum" =~ ^[0-9]+$ ]]; then
  echo "Minimum approving reviews must be a positive integer." >&2
  exit 2
fi
minimum_num=$((10#$minimum))
if (( minimum_num < 1 )); then
  echo "Minimum approving reviews must be a positive integer." >&2
  exit 2
fi

payload=$(cat <<JSON
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Lint and test",
      "Security scans",
      "Docker build and health check",
      "Team approval gate"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": $minimum_num
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
)

if [[ "$dry_run" == true ]]; then
  printf '%s\n' "$payload"
  exit 0
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required." >&2
  exit 1
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "Authenticate with gh before applying branch protection." >&2
  exit 1
fi
printf '%s\n' "$payload" | gh api -X PUT repos/{owner}/{repo}/branches/main/protection --input -
