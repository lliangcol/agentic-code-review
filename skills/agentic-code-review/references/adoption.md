# Adoption

## Zero-Intrusion Use

Install the Skill globally and invoke it explicitly from any repository.

```text
Use agentic-code-review to review the current branch.
```

## Project Hint

For repeated use in one repository, add the content from `assets/AGENTS.snippet.md` to that repository's `AGENTS.md`.

Keep repository-specific high-risk areas in the target repository's own instructions, not in this generic Skill.

## Adoption Profiles

For a solo prototype with no users, keep the workflow light: require real tests, preserve CI, read test changes first, and use risk tiering to avoid over-reviewing throwaway code.

For a small team or project with users, require reviewability intake, validation output, small PRs, rollback notes for `L2+`, and a human merge owner for user-visible or durable changes.

For a large or long-lived system, make evidence mandatory: slice maps for broad diffs, decision logs for agent-authored changes, heterogeneous review for high-risk paths, team metrics, and explicit human ownership for load-bearing code.

## Transition Triggers

Move to the next heavier profile when any trigger appears:

- First external user or customer-visible workflow.
- User data, deletion, auth, permissions, payments, billing, secrets, or production config.
- Shared ownership, on-call, durable API behavior, migrations, or cross-service protocol.
- Agent-generated PR volume that increases review wait time, review duration, zero-review merges, or `Not reviewable` rate.
- A change requires product judgment that the agent or submitter did not write down.

## Pull Request Template

`assets/pull_request_template.md` can be copied into `.github/pull_request_template.md` of a target project.

This is optional and should not be required for the Skill to work.
