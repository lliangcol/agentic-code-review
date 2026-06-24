# Team Adoption Metrics

## Purpose

Use these metrics when a team wants to adopt agentic review, tune review capacity, or understand whether AI-generated review load is sustainable.

These are adoption signals, not mandatory gates for every Skill invocation.

## Track

- Zero-review merges: changes merged without human owner review.
- Time to first review: how long work waits before a trusted reviewer sees it.
- Review duration: elapsed time from first review to resolution.
- PR or diff size: files changed, lines changed, generated code, and mixed-scope signals.
- Test-change ratio: how much of the diff rewrites tests or fixtures.
- Re-review count: how many fresh passes were needed after fixes.
- Gate failures: test, lint, coverage, security, documentation, or governance failures.
- Not reviewable rate: how often PRs arrive without enough evidence.
- Decision-log completeness: how often agent-authored changes explain intent, assumptions, and alternatives.
- Reviewer calibration: valid unique findings, false positives, overlap, and missed defect classes by reviewer or tool.
- Agent PR abandonment: reviews that stall after subjective feedback, missing owner response, or repeated regeneration without addressing intent.

## Action Thresholds

Treat trend changes as prompts to adjust the process:

- Zero-review merges rising: require a named human merge owner before merge.
- Time to first review or review duration rising: reduce work in progress and reject low-evidence changes earlier.
- PR or diff size rising: require smaller PRs, slice maps, or generated-code separation.
- Test-change ratio rising: review tests first and require test-change explanations.
- Gate failures or re-review count rising: strengthen deterministic gates and require fresh re-review after fixes.
- Not reviewable rate rising: make intake fields mandatory in PR templates or repository rules.
- Reviewer false positives or overlap rising: recalibrate prompts, swap reviewer combinations, or narrow each reviewer role.
- Agent PR abandonment rising: require acceptance criteria, smaller slices, and a human owner before review.

## Reviewer Calibration Protocol

Use a lightweight calibration set before trusting a reviewer mix:

- Select representative merged, rejected, and incident-linked changes from the team's own code.
- Name an adjudication owner who decides whether a finding is valid, duplicate, false positive, or out of scope.
- Track unique valid findings, false positives, overlap, missed defects, and defect classes per reviewer.
- Rotate prompts, roles, or tools when overlap is high or one reviewer repeatedly misses a class.
- Do not import benchmark rankings as policy without local calibration.

## Metrics Template

Use `assets/review-capacity-metrics.template.csv` as a lightweight starting point for weekly or per-release tracking.

Use `assets/review-capacity-metrics.schema.json` when a team wants to validate collected metrics before importing them into a dashboard or review report.

Run `scripts/validate_metrics.py path/to/metrics.csv` before publishing or importing collected metrics. It validates required columns, numeric ranges, and date shape without external dependencies.

Use `scripts/collect_github_metrics.py exported-prs.json --repository owner/repo --period-start YYYY-MM-DD --period-end YYYY-MM-DD` to derive a starter metrics row from GitHub PR JSON. AI finding quality fields still require human adjudication.

## Use

Use metrics to adjust intake rules, PR size expectations, reviewer allocation, and automation gates.

Do not use throughput alone as proof that review quality improved.

If review capacity is saturated, raise the intake bar before reducing safety checks.
