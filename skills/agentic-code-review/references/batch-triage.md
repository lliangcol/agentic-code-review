# Batch Triage

## Purpose

Use batch triage to allocate human attention across many PRs, branches, commits, or diffs.

Triage is not merge approval. It is a first pass that decides what deserves deep review, what needs evidence, and what looks low risk.

## Categories

Assign each item to one category:

- `Safe-looking`: low-risk, small, clear intent, relevant validation present.
- `Needs work`: likely reviewable, but has concrete defects or missing fixes.
- `High-risk`: auth, money, user data, deletion, migrations, production config, LLM tool actions, broad refactors, or durable shared code.
- `Not reviewable`: missing intent, validation evidence, slice map, owner, or readable diff shape.

## Output

Keep output compact so the owner can decide where to spend time.

```md
## Batch Triage

### High-risk
- PR or diff: reason, required next evidence

### Not reviewable
- PR or diff: smallest missing evidence

### Needs work
- PR or diff: confirmed issue summary

### Safe-looking
- PR or diff: why it can receive lighter review

## Human Attention Plan
What to review first and why
```

## Rules

Do not auto-merge from a triage result.

Use `assets/batch-triage.template.json` and `assets/batch-triage.schema.json` when triage output must feed a dashboard, metrics report, or follow-up automation. The JSON category is still attention allocation, not merge approval.

Run `scripts/validate_batch_triage.py path/to/batch-triage.json` before importing machine-readable triage records.

Use `references/review-effort-signals.md` when patch size, file types, test-change ratio, generated code, or missing evidence determine where human attention should go first.

Escalate any small high-risk slice even when the surrounding PR is low risk.

Prefer rejecting or splitting unreadable changes over doing a shallow review of a large mixed diff.
