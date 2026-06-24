# Human On The Loop Audit

## Purpose

Use this reference when review volume is too high for a human to read every line, or when an agent loop writes, reviews, and judges code before a human sees it.

The goal is audit and attention allocation, not automatic merge approval.

## Audit Plan

Build an explicit plan:

- High-risk slices that always receive human review.
- Random sample size for low-risk slices.
- Spot checks for tests, CI gates, generated code, and duplicated helpers.
- Escalation rules when an AI reviewer, gate, or sample finds a confirmed issue.
- Human owner for merge, rollback, and residual risk.

## Reproducible Sampling

For low-risk slices, record:

- Population size and exclusions.
- Random seed or deterministic ordering key.
- Sample size or percentage.
- Selection command or method.
- Result summary and escalation decision.

Use stratified sampling when the batch mixes docs, tests, generated files, runtime code, and configuration. Keep high-risk slices out of the random pool because they require direct human review.

## Model-Only Loop Guardrails

Do not let a model-only loop approve high-risk work without:

- Deterministic gates that run before model judgment.
- Independent review roles or model families where feasible.
- Human approval for irreversible actions.
- A residual-risk note that names any correlated model blind spot.

## Output

```md
## Audit Scope
What was sampled, spot-checked, and excluded

## High-Risk Human Review
Slices that required direct human attention

## Sampling Plan
Population, exclusions, seed or ordering key, sample size, selection method, and results

## Escalations
Confirmed issues or gate failures that changed review depth

## Human Owner
Person accountable for merge and rollback
```
