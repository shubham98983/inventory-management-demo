# Pull request governance

AI-generated pull requests are identified by the `ai-generated` label, an `ai/` or `ai-fix/` head branch, or an `AI-Assisted:` commit trailer. Each configured username in `.github/APPROVERS` other than the PR author must have a latest review that is `APPROVED` for the current head commit. The Team approval gate reports outstanding usernames; its status check must pass before merge.

To add a team member, add their GitHub username on its own line in `.github/APPROVERS` and update `.github/CODEOWNERS` when they should own files. Changes to `.github/` require human review because they change the controls that decide who may approve and merge work.

For an emergency, a repository administrator may use GitHub's administrative bypass after recording the reason, PR URL, and bypassing administrator in the PR conversation or an audit issue. Restore normal protections immediately and review the bypass afterward.

Branch protection is required: the workflow only reports a status and cannot prevent a merge on its own. Configure required status checks, code-owner review, stale-approval dismissal, and administrator enforcement with `scripts/setup_branch_protection.sh`.

Limitations: approval is based on each user's latest review visible through the GitHub API and the current head SHA; the gate depends on the GitHub CLI and configured approver file from the base branch. Placeholder usernames must be replaced. This workflow does not verify reviewer identity beyond GitHub's review records, and repository administrators can bypass protections.
