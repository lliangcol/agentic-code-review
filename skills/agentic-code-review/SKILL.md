---
name: agentic-code-review
description: Evidence-gated, risk-tiered AI-assisted code review workflow compatible with Codex and Claude Code. Use when reviewing a PR/current branch/diff, reviewing agent-generated code, validating review findings, triaging batches of PRs, checking merge readiness, auditing high-volume agent review loops, calibrating AI reviewers, or reviewing AI-generated code. Defaults to review-only. Emphasizes reviewability intake, Not reviewable verdicts, cheap review-effort circuit breakers, risk tiering, test-change scrutiny, heterogeneous AI review evidence, CI/gate integrity, LLM/prompt security, optional diff measurement, optional fresh re-review via review-fix-loop, and human merge ownership.
---

# Agentic Code Review

## Purpose

Use this Skill to review code changes by risk, not by author. Preserve human attention for changes where being wrong is expensive.

Default to review-only. Do not edit files, commit, push, publish, install tools, or contact external systems unless the user explicitly asks for that action.

## Workflow

1. Load repo-local instructions first: `AGENTS.md`, `CLAUDE.md`, module rules, and project review docs.
2. Determine the review target: current diff, branch, PR, pasted finding, or merge-readiness question.
3. Check reviewability before deep review. Read `references/review-intake.md` when intent, scope, decision log, validation evidence, test output, human owner, or diff readability is incomplete.
4. Use cheap review-effort signals before expensive review. Read `references/review-effort-signals.md` for large, mixed, generated, high-churn, or unclear changes.
5. Classify risk using blast radius, code lifetime, and shared understanding. Read `references/risk-model.md` when risk is not obvious.
6. Map the highest-risk slice to `L0-L4` review depth. Read `references/review-depth.md` for required depth.
7. Inspect test changes separately before trusting implementation changes. Read `references/test-change-review.md` whenever tests changed.
8. Read `references/llm-security-review.md` for changes that route untrusted text into prompts, LLM calls, agent loops, retrieval, or tool execution.
9. Preserve CI and gate integrity. Read `references/ci-gate-integrity.md` when workflows, lint, coverage, security scans, dependency policy, release metadata, or required checks changed.
10. Separate confirmed defects from `Needs confirmation`. Do not present assumptions as verified facts.
11. Use `references/output-format.md` for final review output.

## Reference Routing

For batch PR or multi-diff triage, read `references/batch-triage.md` and treat the output as attention allocation, not merge approval.

For high-risk review, multi-pass review, or AI-reviewer comparison, read `references/heterogeneous-reviewers.md`. Read `references/reviewer-prompts.md` when concrete independent reviewer prompts are useful.

For high-volume agent review loops, sampling, spot-checking, or model-only review audit, read `references/human-on-the-loop-audit.md`.

For solo, small-team, or large-system adoption profiles and transition triggers, read `references/adoption.md`.

For team rollout, process metrics, review-capacity questions, or reviewer calibration, read `references/team-adoption-metrics.md`.

For output examples or forward-testing the Skill on realistic review tasks, read `references/examples.md`.

## Optional review-fix-loop

`review-fix-loop` is optional. Use it only when the user explicitly asks for it, a repository configuration is present, or the task asks for review/fix/re-review until clean.

When active, read `references/integrations/review-fix-loop.md` and use it as the fresh-snapshot execution contract.

## Merge Verdict

Give `Ready`, `Not ready`, `Needs confirmation`, or `Not reviewable` only when the evidence supports it. For high-risk changes, cite validation commands or state what could not be run.
