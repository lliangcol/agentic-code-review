# Agentic Code Review Skill

Simplified Chinese: [README.zh-CN.md](README.zh-CN.md)

[![Validate](https://github.com/lliangcol/agentic-code-review-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/lliangcol/agentic-code-review-skill/actions/workflows/validate.yml)

## Overview

`agentic-code-review` is an Agent Skill package for evidence-gated, risk-tiered code review of AI-generated or human-written changes. It includes Codex packaging and Claude Code installation support from the same canonical Skill content.

It defaults to review-only, checks whether a change is reviewable, uses cheap review-effort signals before expensive review, emphasizes test-change scrutiny and CI integrity, and can optionally use `review-fix-loop` for fresh snapshot based review/fix/re-review loops.

## Runtime Support

| Runtime or surface | Support |
| --- | --- |
| Codex | Supported through `skills/agentic-code-review/`, Codex Skill installation, and `agents/openai.yaml` metadata. |
| Claude Code | Supported by installing the same Skill directory under the configured Claude skills directory, normally `~/.claude/skills/agentic-code-review/` or `$CLAUDE_CONFIG_DIR/skills/agentic-code-review/` when set, or under a project `.claude/skills/agentic-code-review/` directory. |
| Shared Skill content | `SKILL.md`, `references/`, `assets/`, and `scripts/` stay single-source for both runtimes. |
| Runtime-specific metadata | Codex-specific metadata remains under `agents/openai.yaml`; Claude Code uses directory-based skill discovery and `CLAUDE.md` project memory guidance. |

## Why

Coding agents can produce changes faster than humans can review them. The useful response is not to review every change at the same depth, but to spend human attention where being wrong is expensive.

The workflow is inspired by Addy Osmani's article [Agentic Code Review](https://addyosmani.com/blog/agentic-code-review/). This repository does not copy or redistribute the article text.

## Install Locally

From this repository root, run the default Codex install:

```powershell
.\scripts\install-local.ps1
```

On Linux or macOS, run the same script with PowerShell 7+:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/install-local.ps1
```

To install to a custom Codex skills directory:

```powershell
.\scripts\install-local.ps1 -Destination "C:\Users\you\.codex\skills"
```

On Linux or macOS, pass a POSIX destination path:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/install-local.ps1 -Destination "$HOME/.codex/skills"
```

To install for Claude Code globally:

```powershell
.\scripts\install-local.ps1 -Runtime ClaudeCode
```

The default Claude Code destination is the `skills` directory under `CLAUDE_CONFIG_DIR` when that variable is set; otherwise it is `$HOME/.claude/skills`.

To install for both Codex and Claude Code:

```powershell
.\scripts\install-local.ps1 -Runtime Both
```

To install for a repository-scoped Claude Code skill, point the Claude destination at that repository's `.claude/skills` directory:

```powershell
.\scripts\install-local.ps1 -Runtime ClaudeCode -ClaudeDestination ".\.claude\skills"
```

## Use

Common prompts:

```text
Use agentic-code-review to review the current branch.

Use agentic-code-review to validate these review findings.

Use agentic-code-review to decide whether this branch is merge-ready.

Use agentic-code-review + review-fix-loop to review/fix/re-review until clean.

Use agentic-code-review to triage these PRs by review risk.
```

## What It Checks

The Skill classifies changes by three axes: blast radius, code lifetime, and shared understanding.

It checks reviewability first, maps changes to `L0-L4` review depth, uses circuit-breaker signals for large or mixed diffs, inspects tests separately, preserves CI as a hard boundary, reviews LLM/prompt/tool-action trust boundaries when relevant, records AI reviewer evidence as signals, and keeps merge responsibility with a human owner.

When a change lacks intent, validation evidence, ownership, decision log, slice map, or a readable diff shape, the Skill can return `Not reviewable` with the smallest missing evidence needed to continue.

For batches of PRs or diffs, it can triage work into `Safe-looking`, `Needs work`, `High-risk`, and `Not reviewable` so human attention goes to the right place.

Optional references cover CI/gate integrity, ready-to-run heterogeneous reviewer prompts, persisted reviewer-comparison records, machine-readable batch triage, hostile-input fixtures, human-on-the-loop audit plans, reviewer calibration, and a diff measurement helper for cheap review-effort signals.

## Source Notes

The article source rationale is preserved as paraphrased notes in `docs/agentic-code-review-source-notes.md`. The implementation comparison and improvement inventory live in `docs/agentic-code-review-implementation-analysis.md`.

Use `docs/source-refresh-checklist.md` when refreshing source claims or external evidence. Use `docs/codebase-graph.md` when maintaining graph-backed code discovery for this repository.

Use `docs/open-source-readiness.md` before the first public GitHub push or any later public release.

## Team Capacity

AI-generated throughput can increase review and QA load. Do not use throughput alone as proof of review quality. Track review capacity, zero-review merges, review duration, `Not reviewable` rate, gate failures, and reviewer calibration before reducing safety checks.

Use `skills/agentic-code-review/assets/review-capacity-metrics.template.csv` and `skills/agentic-code-review/assets/review-capacity-metrics.schema.json` as starter artifacts for team metric collection. Validate collected metrics with `skills/agentic-code-review/scripts/validate_metrics.py`; derive starter rows from exported GitHub PR JSON with `skills/agentic-code-review/scripts/collect_github_metrics.py`.

## Optional review-fix-loop Integration

`review-fix-loop` is optional. When requested or detected, this Skill uses it as the fresh-snapshot execution contract.

`agentic-code-review` decides how risky a change is and how deeply it should be reviewed; `review-fix-loop` ensures each review pass is based on the current live worktree.

## Repository Adoption

The lowest-intrusion adoption path is to install the Skill globally and invoke it explicitly in Codex or Claude Code.

For a project-level hint, copy `skills/agentic-code-review/assets/AGENTS.snippet.md` into the target repository's `AGENTS.md`.

For Claude Code project memory, copy `skills/agentic-code-review/assets/CLAUDE.snippet.md` into the target repository's `CLAUDE.md`. Use a project `.claude/skills/agentic-code-review/` install only when the Skill should be scoped to that repository; otherwise prefer the configured global Claude skills directory (`$CLAUDE_CONFIG_DIR/skills` when set, otherwise `~/.claude/skills/`).

## Validate

Run local validation before publishing changes:

```powershell
.\scripts\check-skill.ps1
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$env:PYTHONUTF8 = "1"
python (Join-Path $codexHome "skills/.system/skill-creator/scripts/quick_validate.py") .\skills\agentic-code-review
```

On Linux or macOS, use `pwsh` for the repository validation script:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$env:PYTHONUTF8 = "1"
python (Join-Path $codexHome "skills/.system/skill-creator/scripts/quick_validate.py") ./skills/agentic-code-review
```

The repository validation script is required. The Codex Skill validator is optional and Codex-specific because not every environment has it installed.

For a Claude Code smoke check, install to a test repository's `.claude/skills` directory or the configured global Claude skills destination, confirm the installed folder contains `SKILL.md`, `references/`, `assets/`, and `scripts/`, then invoke `/agentic-code-review` in Claude Code from that test repository.

## Project Layout

Root-level files are for GitHub and maintainers. Skill runtime content lives under `skills/agentic-code-review`.

Simplified Chinese companion files use the same path with `.zh-CN.md`.

```text
skills/agentic-code-review/SKILL.md
skills/agentic-code-review/references/
skills/agentic-code-review/references/review-intake.md
skills/agentic-code-review/references/review-effort-signals.md
skills/agentic-code-review/references/risk-model.md
skills/agentic-code-review/references/review-depth.md
skills/agentic-code-review/references/test-change-review.md
skills/agentic-code-review/references/heterogeneous-reviewers.md
skills/agentic-code-review/references/reviewer-prompts.md
skills/agentic-code-review/references/llm-security-review.md
skills/agentic-code-review/references/ci-gate-integrity.md
skills/agentic-code-review/references/batch-triage.md
skills/agentic-code-review/references/human-on-the-loop-audit.md
skills/agentic-code-review/references/team-adoption-metrics.md
skills/agentic-code-review/references/output-format.md
skills/agentic-code-review/references/examples.md
skills/agentic-code-review/references/adoption.md
skills/agentic-code-review/references/integrations/review-fix-loop.md
skills/agentic-code-review/assets/
skills/agentic-code-review/assets/AGENTS.snippet.md
skills/agentic-code-review/assets/CLAUDE.snippet.md
skills/agentic-code-review/assets/batch-triage.template.json
skills/agentic-code-review/assets/batch-triage.schema.json
skills/agentic-code-review/assets/forward-test-scenarios.json
skills/agentic-code-review/assets/hostile-input-fixtures.md
skills/agentic-code-review/assets/hostile-input-fixtures.json
skills/agentic-code-review/assets/review-effort.config.example.json
skills/agentic-code-review/assets/review-capacity-metrics.template.csv
skills/agentic-code-review/assets/review-capacity-metrics.schema.json
skills/agentic-code-review/assets/reviewer-comparison.example.json
skills/agentic-code-review/assets/reviewer-comparison.template.md
skills/agentic-code-review/assets/reviewer-comparison.schema.json
skills/agentic-code-review/agents/openai.yaml
skills/agentic-code-review/scripts/collect_github_metrics.py
skills/agentic-code-review/scripts/detect_review_fix_loop.py
skills/agentic-code-review/scripts/measure_diff.py
skills/agentic-code-review/scripts/validate_batch_triage.py
skills/agentic-code-review/scripts/validate_hostile_fixtures.py
skills/agentic-code-review/scripts/validate_metrics.py
skills/agentic-code-review/scripts/validate_reviewer_comparison.py
tests/test_skill_scripts.py
scripts/check-skill.ps1
scripts/install-local.ps1
```

## License

Licensed under the Apache License 2.0. The official legal license text is in `LICENSE`.
