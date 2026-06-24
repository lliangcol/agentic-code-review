# Review Depth

## L0 / L0

Read changed files lightly. Run cheap formatting or documentation checks when obvious. Do not over-review generated metadata unless it affects release or governance.

## L1 / L1

Review the localized behavior and rollback path. One AI review pass plus a human glance is usually enough.

## L2 / L2

Review implementation and tests. Require relevant validation evidence. Confirm that changed behavior matches stated intent.

If validation evidence is missing or only asserted, use `Not reviewable` or list the exact missing evidence before giving a merge verdict.

## L3 / L3

Run or simulate two independent review passes when feasible, using different review perspectives: correctness/regression, test integrity, security or abuse, and operational rollback.

Read `references/heterogeneous-reviewers.md` when using multiple AI reviewers or comparing independent review passes. Prefer different tools, model families, prompts, or review roles when available.

Require targeted validation where practical. If validation cannot be run, state the residual risk directly.

Require a human owner who accepts the residual risk for auth, money, user data, deletion, production config, security boundaries, or LLM tool-action paths.

## L4 / L4

Prefer a plan or design review before implementation review. Split broad changes when possible. Verify invariants, migration path, rollback, and cross-system compatibility.

For large mixed diffs, broad refactors, generated-code churn, or many test rewrites, ask for a slice map or smaller PRs before deep implementation review.

Do not give a merge-ready verdict without strong evidence and a clear human owner.
