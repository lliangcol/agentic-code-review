# Test Change Review

## Rule

Read test changes more carefully than implementation changes when an agent may have generated or repaired code.

A passing test suite is not enough if tests were weakened to fit the implementation.

Treat real command output as stronger evidence than a statement that tests passed.

## Flag These Patterns

- Deleted tests without equivalent replacement.
- Weakened assertions, broader matchers, or reduced expected values.
- Skipped, disabled, quarantined, or renamed tests that avoid execution.
- Over-mocking that hides real behavior.
- Happy-path-only tests for risky behavior.
- Tests changed to match implementation instead of product intent.
- Regression tests removed after a bug fix.
- Coverage moved from public behavior to implementation detail.
- Coverage thresholds, lint rules, or required gates were lowered.
- Fixtures, regression samples, or negative cases were deleted without replacement.
- Large test rewrites do not explain why old expectations were wrong.

## High-Risk Validation

For high-risk behavior, consider mutation testing or an equivalent negative test to prove the test would fail if the implementation regressed.

Review test intent before trusting implementation when the diff rewrites many tests or fixtures.

For large test rewrites, require an explanation of why the old expectation was wrong or obsolete. If that explanation is missing, treat the implementation review as blocked or incomplete.

## Output

Always include a `Test Review` section when tests changed, even if no issue was found.

When tests dominate the diff or assertions were rewritten, put `Test Review` before implementation findings and state whether the tests still protect the original product intent.
