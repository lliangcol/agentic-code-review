# CI Gate Integrity

## When To Use

Use this reference when a change touches workflows, required checks, lint, test commands, coverage, security scans, dependency policy, release metadata, build scripts, or generated gate configuration.

Treat gate weakening as at least `L3` when it can hide product, security, release, or governance failures.

## Flag These Patterns

- Required jobs, checks, or branch-protection references are removed or renamed without replacement.
- `continue-on-error`, allow-failure, broad exclusions, skipped paths, or conditional guards make a gate easier to bypass.
- Coverage, lint, typecheck, test, security, dependency, or documentation thresholds are lowered.
- Failing assertions, failing tests, or security findings are deleted instead of fixed.
- Build or release scripts stop failing on command errors.
- Dependency pins, lockfiles, provenance checks, or artifact validation are weakened.
- Generated release or governance metadata changes without a source explanation.

## Required Evidence

Require the submitter to show:

- Which gate changed and why.
- The before and after command or workflow behavior.
- Evidence that the new gate fails on the class of defect it is meant to catch.
- The owner who accepts any reduced coverage or skipped check.

If gate behavior is unclear, use `Not reviewable` until the old and new behavior are demonstrated.

## Reviewer Actions

Prefer restoring strict gates over accepting compensating prose.

When a gate intentionally changes, require a replacement guard, a narrower exclusion, or a documented sunset date.

Never treat a clean AI review as evidence that weakened CI is acceptable.
