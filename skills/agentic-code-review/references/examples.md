# Examples

## Purpose

Use these compact examples when the expected review shape is unclear. Adapt the evidence and wording to the actual repository; do not copy verdicts without source support.

Use `assets/forward-test-scenarios.json` when forward-testing the Skill against representative prompts. Treat it as a scenario checklist, not as source evidence.

## L1 Localized Change

```md
## Verdict
Ready

## Risk Tier
L1 - localized behavior with easy rollback.

## Reviewability
Intent, scope, and validation output are present.

## Findings
None.

## Test Review
No tests changed.

## CI / Validation
Reviewed command output: targeted unit test passed.

## Residual Risk
Low; limited to the touched helper.
```

## L3 High-Risk Change

```md
## Verdict
Needs confirmation

## Risk Tier
L3 - user data and permission boundary changed.

## Reviewability
Implementation and tests are reviewable, but rollback owner is missing.

## Findings
[P2] path/file.ext:42 - confirmed issue with authorization fallback.

## Test Review
Tests cover the happy path, but no negative permission case is present.

## AI Review Evidence
Correctness pass found the authorization issue. Security pass found no additional confirmed issue. The passes used different review roles.

## CI / Validation
Targeted tests passed. Negative permission test was not present.

## Human Merge Notes
Name the owner who accepts residual permission risk before merge.
```

## Not Reviewable

```md
## Verdict
Not reviewable

## Risk Tier
L4 - broad mixed diff across runtime, tests, generated files, and config.

## Reviewability
Missing slice map, decision log, validation output, and human merge owner.

## Required Evidence Missing
Provide a slice map, commands with output, test-change explanation, and owner for high-risk files.

## Findings
No speculative findings. The diff shape prevents responsible review.
```

## Not Reviewable Intake Patterns

- Missing validation: "Provide the exact commands and relevant output before merge readiness can be assessed."
- Missing decision log: "Provide the plan followed, key assumptions, alternatives rejected, and human judgment points for this non-trivial agent-authored change."
- Generated-code churn: "Separate generated output from behavioral changes or provide a slice map naming files that require real review."
- High-risk owner absent: "Name the human owner and rollback path before review can support a merge verdict."
- LLM trust boundary unclear: "Explain how untrusted input is delimited, validated, and prevented from changing tool targets or approval decisions."

## Batch Triage

```md
## Batch Triage

### High-risk
- PR A: touches billing retry behavior; needs owner, targeted tests, and rollback notes.

### Not reviewable
- PR B: large mixed agent change with no slice map or validation output.

### Needs work
- PR C: confirmed failing gate and weakened assertion.

### Safe-looking
- PR D: docs-only, clear intent, validation present.

## Human Attention Plan
Review PR A first, reject PR B until evidence is supplied, then handle PR C.
```

## LLM Security Review

```md
## Verdict
Not ready

## Risk Tier
L3 - untrusted document text can influence tool arguments.

## Findings
[P1] path/file.ext:88 - model output can directly choose a file path used for writes without validation.

## Test Review
No hostile-input test proves that prompt injection is treated as data.

## CI / Validation
No security test was run for tool-argument redirection.

## Human Merge Notes
Require path allowlisting and human confirmation before irreversible writes.
```
