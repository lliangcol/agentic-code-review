# LLM Security Review

## When To Use

Use this reference for changes that send untrusted text into prompts, LLM calls, retrieval, agent loops, tool calls, code execution, file writes, network requests, or external actions.

Treat these changes as at least `L3` when model output can affect permissions, money, user data, production state, secrets, files, commands, or external systems.

## Trust Boundaries

Identify every boundary crossed by user, document, web, issue, PR, email, retrieval, or tool output text.

Distinguish normal content from text that can alter instructions, tool arguments, file paths, shell commands, credentials, or approval decisions.

## Flag These Patterns

- Untrusted input is concatenated into system, developer, or tool-control prompts without delimiting or policy separation.
- Model output directly triggers writes, deletes, shell commands, network calls, purchases, approvals, or messages.
- Retrieved documents or PR text can override instructions or change tool targets.
- Secrets, tokens, credentials, private paths, or sensitive logs are included in prompts or review output.
- The change relies on "the model will ignore malicious text" instead of explicit constraints, validation, and human confirmation.
- The agent loop judges its own work without an independent gate on high-risk actions.
- Similar model families write, review, and judge the same high-risk change without deterministic checks or human approval.

## Required Evidence

For high-risk LLM paths, require tests or demonstrations that hostile input cannot redirect instructions, tools, or outputs.

Require an explicit human confirmation point before irreversible external actions.

If the trust boundary is unclear, use `Needs confirmation` or `Not reviewable` instead of accepting the risk silently.

For closed-loop agent review, require deterministic checks before model judges, independent review perspectives for `L3+`, and human approval before writes, deletes, messages, network calls, purchases, releases, or other irreversible external actions.

## Hostile Input Checks

For prompt, retrieval, or tool-action surfaces, look for a negative test or manual demonstration using hostile text that tries to:

- Override system or developer instructions.
- Change tool arguments, file paths, shell commands, recipients, URLs, approvals, or payment targets.
- Exfiltrate secrets, private paths, hidden prompts, or unrelated user data.
- Convert read-only analysis into writes, deletes, messages, network calls, or other external actions.

The expected result should be explicit: the hostile instruction is treated as data, tool arguments are validated, and irreversible actions require human confirmation.

Use `assets/hostile-input-fixtures.md` as safe starter test data. Adapt the expected result to the target repository's real trust boundary and tool policy.

Use `assets/hostile-input-fixtures.json` and `scripts/validate_hostile_fixtures.py` when a target repository needs machine-readable hostile-input cases.
