# Review Intake

## Purpose

Decide whether a change is ready for review before spending deep review effort.

`Not reviewable` means the submission lacks the evidence or shape needed for a responsible review. It is different from `Needs confirmation`, which means product, owner, or context facts are still uncertain after review.

## Required Evidence

Before deep review, look for these inputs:

- Intent: what the change is for and which behavior should change.
- Scope: files, modules, services, or user flows affected.
- Slice map for broad changes: behavior slices, generated files, mechanical churn, and files needing real review.
- Decision log for agent-authored changes: plan followed, key assumptions, alternatives rejected, and human judgment points.
- Risk statement: expected `L0-L4` tier or the author's risk rationale.
- Validation evidence: commands run and relevant output, not only "tests pass".
- Test-change explanation: why tests changed and what behavior they protect.
- Rollback or mitigation notes for `L2+` changes.
- Human merge owner for `L3+` or merge-readiness work.

## Not Reviewable Signals

Use `Not reviewable` when a responsible review would mostly reconstruct missing intent or evidence.

- The diff is too large or mixed to inspect as one review, and no plan or slice map is supplied.
- The author asks for merge-readiness without validation evidence.
- A non-trivial agent-authored change lacks a decision log, so the reviewer must reconstruct intent from the diff.
- Tests were heavily rewritten without explaining why the old expectations were wrong.
- Generated code, vendored code, or mechanical churn obscures the behavioral change.
- High-risk areas changed without a human owner or rollback path.
- LLM, prompt, retrieval, or tool-execution behavior changed without a trust-boundary explanation.

## Reviewer Actions

For `Not reviewable`, list the smallest missing evidence needed to start review.

Do not convert missing evidence into speculative findings.

Read `references/review-effort-signals.md` when cheap signals suggest the change may be too large, mixed, high-churn, or evidence-poor for responsible deep review.

If only part of the change is reviewable, review that part and mark the rest as `Not reviewable`.
