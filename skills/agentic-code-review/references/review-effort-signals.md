# Review Effort Signals

## Purpose

Use cheap signals before deep review to decide whether a change is ready for human attention, needs splitting, or should be marked `Not reviewable`.

These signals do not replace risk tiering. A small high-risk slice still escalates, and a large low-risk generated update can still be light if evidence is clear.

## Cheap Signals

Check these before spending expensive review time:

- Patch size: files changed, lines changed, binary or generated artifacts, and whether the diff fits in one readable pass.
- File types: migrations, auth, billing, permissions, production config, prompt/tool code, generated code, fixtures, and release metadata.
- Scope mix: unrelated features, refactors, tests, formatting, dependency updates, or generated files in one change.
- Test-change ratio: tests or fixtures dominate the diff, especially when assertions are weakened or replaced.
- Review back-and-forth risk: subjective requirements, unclear acceptance criteria, or a change that needs product judgment the author did not supply.
- Evidence quality: missing commands, pasted summaries without output, stale CI, or no proof that validation ran.
- Comprehension debt: duplicated helpers, hidden behavior behind generated code, broad abstractions, or missing slice maps.

## Default Circuit-Breaker Thresholds

Use these as starting heuristics when the repository has no stricter local rule:

- More than 20 changed files, more than 800 changed lines, or more than 3 unrelated behavior slices: ask for a slice map before deep review.
- More than 40 changed files, more than 1,500 changed lines, or behavior mixed with generated/vendor churn: default to `Not reviewable` until split or mapped.
- Tests or fixtures over half of the diff: read `references/test-change-review.md` first and require a test-change explanation.
- Any high-risk file path or symbol in auth, permissions, billing, payments, deletion, migrations, production config, LLM tools, prompts, or CI gates: escalate to at least `L3` even if the diff is small.
- Workflow, coverage, lint, dependency, security, or release-gate changes: read `references/ci-gate-integrity.md`.

When available, run `scripts/measure_diff.py` as an advisory helper. It reports path-based signals plus high-risk terms found in changed diff lines. Treat its output as a signal, not as a verdict.

Use `assets/review-effort.config.example.json` as a starting point when a target repository needs stricter local thresholds or project-specific path patterns. Pass it with `scripts/measure_diff.py --config path/to/review-effort.json`.

## High-Maintenance Agent PR Signals

Fast-fail a change before deep review when the agent-authored PR is likely to stall in subjective back-and-forth:

- Acceptance criteria are subjective, missing, or contradicted by the diff.
- The agent made broad design choices without a decision log.
- The change mixes implementation, refactor, test rewrites, formatting, and generated output.
- A previous review asked for judgment or product clarification and the agent only regenerated code.
- The author cannot name a human owner who will respond to non-mechanical feedback.

Use the smallest corrective action: require acceptance criteria, a tighter plan, a smaller slice, or a human owner before spending senior review time.

## Circuit Breaker Decisions

Use the cheapest defensible action:

- Proceed with light review when the change is small, low-risk, clearly scoped, and validated.
- Ask for missing evidence when intent, commands, decision log, or owner information is incomplete but easy to supply.
- Ask for a slice map or smaller PR when unrelated scopes or broad churn obscure the behavioral change.
- Return `Not reviewable` when the reviewer would mostly reconstruct missing intent, validation, ownership, or diff shape.
- Escalate to `L3` or `L4` when cheap signals reveal high blast radius, durable shared code, security boundaries, or merge-readiness risk.

## Reviewer Actions

Record which cheap signals drove the decision.

Do not reject by size alone. Explain the smallest change that would make the review tractable: split by behavior, attach validation output, restore test intent, add a decision log, or name a human owner.

Do not let a clean AI review override circuit-breaker evidence. Treat AI review as a sensor, not a verdict.

Before accepting new helpers or abstractions in durable code, search for existing helpers with the same responsibility. Flag duplicated business logic as comprehension debt when it can diverge over time.
