# review-fix-loop Integration

## Role Split

`agentic-code-review` decides risk tier, review depth, findings, and merge-readiness language.

`review-fix-loop` enforces fresh snapshots, gate execution, run records, and re-review of invalidated slices.

## Activation

Use this integration only when one of these is true:

- The user explicitly mentions `review-fix-loop`.
- The repository has `review-fix-loop.gates.json`.
- The repository has `.review-fix-loop` or `.git/review-fix-loop`.
- The user asks for review/fix/re-review until clean.
- The task is high-risk merge readiness and the repository already uses review-fix-loop.

## Workflow

1. Detect the CLI and repository configuration without initializing new config.
2. Run or request the first fresh snapshot.
3. Apply this Skill's risk model to changed slices.
4. Review findings and separate confirmed defects from `Needs confirmation`.
5. Fix only if the user explicitly asked for fixes.
6. Run planned gates without weakening them.
7. Run a fresh follow-up snapshot and re-review invalidated slices.
8. Stop only when fresh re-review has no new in-scope findings and blocking gates pass.

## Command Record

Record the exact local commands or tool actions used for each phase. Adapt names to the target repository's installed `review-fix-loop` interface.

```text
detect:   review-fix-loop status
record:   review-fix-loop record --target <branch-or-diff>
gates:    review-fix-loop gates run
snapshot: review-fix-loop record --fresh
finalize: review-fix-loop finalize
```

If a command is unavailable, state that it was unavailable rather than treating the phase as passed.

Use `scripts/detect_review_fix_loop.py --root . --format json` for a read-only availability check. It reports repository configuration and CLI presence without initializing new configuration.

## Boundaries

Do not auto-initialize review-fix-loop configuration.

Do not reuse an old diff as final re-review evidence.

Do not hide gate failures or treat unavailable gates as passed.

Do not fix, commit, push, publish, or contact external systems unless the user explicitly asks.
