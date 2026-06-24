# Heterogeneous Reviewers

## Purpose

Use multiple review perspectives to catch different defect classes without treating any AI reviewer as merge approval.

Heterogeneity matters because identical prompts, models, or tools often share blind spots. Prefer different tools, model families, prompts, or review roles when available.

## When To Use

Use this reference for:

- `L3` or `L4` reviews.
- Auth, money, user data, deletion, production config, LLM tool-action paths, or broad durable abstractions.
- Batch triage where human attention must be allocated across many changes.
- Re-review after fixes when the first finding set may be invalidated.
- Team calibration work comparing AI reviewer usefulness on real code.

## How To Run

Keep passes independent. Do not feed one reviewer another reviewer's findings unless the task is explicitly a verification pass.

Use deliberately different perspectives:

- Correctness and regression.
- Test integrity and mutation or negative-case coverage.
- Security, abuse, prompt injection, and trust boundaries.
- Operational rollback, observability, migrations, and production failure modes.
- Architecture, shared ownership, and comprehension debt.

If only one model or tool is available, simulate heterogeneity by running separate passes with different review roles and by resetting assumptions between passes. Do not count the same prompt repeated twice as independent evidence.

Read `references/reviewer-prompts.md` when you need concrete role prompts. Keep each pass blind to the other passes until comparison.

Use `assets/review-prompt-manifest.json` and `scripts/run_review_passes.py` when you need a local, versioned, provider-abstracted runner for independent passes. Keep the default `mock` provider for CI or dry-run validation; configure command providers only in repositories that own the external model invocation.

Use `assets/reviewer-comparison.template.md` or `assets/reviewer-comparison.schema.json` when reviewer evidence must be persisted for calibration, audit, or a high-risk merge decision.

Use `scripts/validate_reviewer_comparison.py` to validate JSON reviewer comparison records before importing them into team metrics or review reports.

## Compare Results

Summarize overlap and disagreement:

- Findings confirmed by source evidence.
- Unique findings from each reviewer.
- Duplicates or false positives.
- Findings rejected and why.
- Residual risk that still needs human judgment.

The human owner keeps the merge decision. AI reviewer agreement is supporting evidence, not approval.

For model-only or loop-driven review, read `references/human-on-the-loop-audit.md` and state the residual risk from correlated model blind spots.

## Calibration

For team adoption, track reviewer quality on your own code:

- Unique valid findings per reviewer.
- False-positive rate or rejected-finding rate.
- Overlap between reviewers.
- Missed defects later caught by tests, incidents, or human review.
- Defect classes each reviewer handles well or poorly.

Use calibration to choose reviewer combinations and prompts. Do not assume a benchmark result transfers unchanged to another codebase.
