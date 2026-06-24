## Agentic Code Review

Use these instructions in `CLAUDE.md` when a project should use the installed `agentic-code-review` skill for code review.

When reviewing branch changes, invoke `/agentic-code-review` or ask Claude Code to use the `agentic-code-review` skill.

Load repository-local rules first, then classify changed slices by risk.

Check reviewability before deep review. If intent, validation evidence, owner, decision log, slice map, or diff shape is missing, return `Not reviewable` with the smallest missing evidence.

Use cheap review-effort signals before expensive review. Ask for smaller PRs or a slice map when broad churn, generated files, or unrelated scopes obscure the behavior.

Inspect test changes carefully. Do not weaken CI, skip tests, or treat AI review as merge approval.

When workflows, lint, coverage, security scans, dependency policy, release metadata, or required checks changed, review CI/gate integrity before trusting green status.

For LLM, prompt, retrieval, agent loop, or tool-action changes, review untrusted input boundaries and prompt-injection risk.

For batch PR review, triage into `Safe-looking`, `Needs work`, `High-risk`, and `Not reviewable`; do not treat triage as merge approval.

For high-risk review, prefer heterogeneous AI review perspectives and report AI reviewer evidence as signals, not approval.

For high-volume agent review loops, use sampling and spot-check audit plans. Keep a human owner accountable for merge and rollback.

Default to review-only. Do not edit files, commit, push, publish, install tools, or contact external systems unless the user explicitly asks for that action.

Preserve `Needs confirmation` for claims that are plausible but not verified. Do not treat AI review output as human approval.

If `review-fix-loop` is configured, use fresh snapshots for review/fix/re-review loops.
