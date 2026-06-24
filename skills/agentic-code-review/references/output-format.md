# Output Format

Use this structure for review output. Keep findings first and evidence-backed.

```md
## Verdict
Ready / Not ready / Needs confirmation / Not reviewable

## Risk Tier
L0-L4 with reason

## Reviewability
Evidence present, missing, or too weak for deep review

## Required Evidence Missing
Smallest evidence needed to continue when verdict is Not reviewable

## Review Scope
Diff/source/rules inspected

## Findings
[P1/P2/P3] file:line - confirmed issue

## Test Review
Test changes, weakened tests, missing coverage. Move this section before `Findings` when tests dominate the diff or assertions were rewritten.

## Needs Confirmation
Unconfirmed product/owner/context questions

## CI / Validation
Checks run, checks skipped, limitations

## AI Review Evidence
Reviewers/tools used, independent perspectives, overlap, disagreements, rejected findings

## Human Merge Notes
What the human owner must accept

## Residual Risk
Known remaining risk
```

## Verdict Meanings

`Ready` means the inspected evidence supports merge or acceptance within the stated risk.

`Not ready` means confirmed defects or failed gates should block merge.

`Needs confirmation` means product, owner, or context facts are unresolved after review.

`Not reviewable` means missing intent, evidence, owner, validation, or diff shape prevents a responsible review.

## AI Review Evidence Rules

Treat AI reviews as signals. Do not present AI reviewer agreement as approval.

When multiple AI reviewers or passes were used, summarize unique confirmed findings, disagreements, and false positives. If only one reviewer or perspective was used for an `L3+` change, state that limitation in residual risk.

## Severity

`P1` blocks merge because it can cause incorrect behavior, data/security exposure, user-visible production failure, or broken governance.

`P2` should be fixed before merge unless the owner consciously accepts the risk.

`P3` is useful cleanup, clarity, or maintainability feedback.
