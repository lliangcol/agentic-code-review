# Agentic Code Review Skill

Simplified Chinese: [README.zh-CN.md](README.zh-CN.md)

[![Validate](https://github.com/lliangcol/agentic-code-review/actions/workflows/validate.yml/badge.svg)](https://github.com/lliangcol/agentic-code-review/actions/workflows/validate.yml)

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

## Requirements

- Python 3.10 or newer for local helper scripts and tests.
- Git for diff measurement, install packaging, and repository validation.
- PowerShell 7 or newer for cross-platform `.ps1` execution. Windows PowerShell can run the scripts on Windows, but CI validates with `pwsh`.
- No API key is required for repository validation. Optional command providers for the review runner should read secrets from their own environment and must not store secrets in config files.

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

When `validate_batch_triage.py` is called with `--format json`, input failures such as invalid JSON emit structured JSON errors on stdout with a non-zero exit code; record-level validation failures stay in the normal JSON result's `errors` array.

When `validate_reviewer_comparison.py` is called with `--format json`, input failures such as invalid JSON emit structured JSON errors on stdout with a non-zero exit code; record-level validation failures stay in the normal JSON result's `errors` array.

When `validate_hostile_fixtures.py` is called with `--format json`, input failures such as invalid JSON emit structured JSON errors on stdout with a non-zero exit code; fixture-level validation failures stay in the normal JSON result's `errors` array.

## Source Notes

The article source rationale is preserved as paraphrased notes in `docs/agentic-code-review-source-notes.md`. The implementation comparison and improvement inventory live in `docs/agentic-code-review-implementation-analysis.md`.

Use `docs/source-refresh-checklist.md` when refreshing source claims or external evidence. Use `docs/codebase-graph.md` when maintaining graph-backed code discovery for this repository.

Use `docs/open-source-readiness.md` before the first public GitHub push or any later public release.

## Team Capacity

AI-generated throughput can increase review and QA load. Do not use throughput alone as proof of review quality. Track review capacity, zero-review merges, review duration, `Not reviewable` rate, gate failures, and reviewer calibration before reducing safety checks.

Use `skills/agentic-code-review/assets/review-capacity-metrics.template.csv` and `skills/agentic-code-review/assets/review-capacity-metrics.schema.json` as starter artifacts for team metric collection. Validate collected metrics with `skills/agentic-code-review/scripts/validate_metrics.py`; derive starter rows from exported GitHub PR JSON with `skills/agentic-code-review/scripts/collect_github_metrics.py`.

When `validate_metrics.py` is called with `--format json`, input and schema failures emit structured JSON errors on stdout with a non-zero exit code; row-level validation failures stay in the normal JSON result's `errors` array.

When `collect_github_metrics.py` is called with `--format json`, input and validation failures such as unsupported payload shapes or invalid periods emit structured JSON errors on stdout with a non-zero exit code.

To include AI reviewer quality fields, pass one or more reviewer-comparison or adjudication records:

```powershell
python .\skills\agentic-code-review\scripts\collect_github_metrics.py .\prs.json `
  --repository owner/repo `
  --period-start 2026-01-01 `
  --period-end 2026-01-07 `
  --adjudication-json .\reviewer-comparison.json
```

Adjudication overlays are validated against the reviewer-comparison contract before metrics are calculated.

## Optional Review Runner

The repository includes an optional standard-library runner for teams that want a local, auditable LLM/agent call chain without binding this Skill to one SDK or provider. The default config uses `mock` providers, so it is safe for CI and smoke tests.

```powershell
python .\skills\agentic-code-review\scripts\run_review_passes.py --dry-run --no-diff --format json
```

The runner provides:

- Provider abstraction through `mock` and `command` providers.
- Multi-pass prompt orchestration from `assets/review-prompt-manifest.json`.
- Prompt versioning through template IDs and versions.
- Timeout, retry, and fallback provider behavior.
- Config validation for invalid providers, unknown fallback references, and fallback cycles before execution.
- Provider attempt failure summaries for timeout, retry, and fallback review.
- Best-effort redaction of common secret-like values in provider stdout/stderr before structured or raw provider output and attempt summaries are written to JSON or Markdown reports.
- Estimated token and cost accounting.
- Structured JSON reports with diff-rule fusion from `measure_diff.py`, including structured diff-measurement failure reasons when the helper exits non-zero.
- Structured `--format json` error output on stdout for config failures, with a non-zero exit code.
- Prompt omission by default; pass `--include-prompts` only when you intentionally want rendered prompts in the report.

Configure it with `skills/agentic-code-review/assets/review-runner.config.example.json`. A command provider receives the rendered prompt on stdin and must write its review output to stdout. Providers must still avoid printing secrets; output-stream redaction is a report-safety fallback, not a guarantee.

The runner writes reports to stdout only; it has no output-file mode and no `--no-write` flag is needed to keep it from modifying files. `--dry-run` renders prompts, estimates tokens and cost, and skips provider calls. In `--format json`, runner config and context-file failures emit structured `review-runner-error-v1` JSON on stdout with stderr empty and a non-zero exit code. In `--format markdown`, configuration failures are printed to stderr and still return a non-zero exit code.

Relative `prompt_manifest` paths are resolved from the runner config file directory. The smoke tests cover config and manifest paths containing spaces so automation should pass paths as argument-array values rather than shell-concatenated command strings.

`--context-file` accepts repeated local file paths and reads them into the rendered prompt. In `--format json` mode, unreadable context files emit structured `review-runner-error-v1` errors on stdout with a non-zero exit code. The smoke tests cover context file paths containing spaces.

Diff measurement defaults to the unstaged working-tree diff through `measure_diff_args: ["--no-untracked"]`. For a staged commit candidate, use `["--staged", "--no-untracked"]`; for a branch or working tree against a base revision, use `["--base", "origin/main", "--no-untracked"]`. When `measure_diff.py` is called directly with `--format json`, argument, config, missing-Git, and Git-context failures emit structured JSON errors on stdout with a non-zero exit code. The runner preserves those helper errors in `diff.errors` instead of replacing them with a generic subprocess failure.

```json
{
  "type": "command",
  "model": "external-reviewer-command",
  "command": ["example-reviewer", "--format", "json"],
  "timeout_seconds": 120,
  "max_retries": 1,
  "fallback": "mock-fallback",
  "pricing": {
    "input_per_million_tokens_usd": 0,
    "output_per_million_tokens_usd": 0
  }
}
```

Compatibility impact: this runner is additive. Existing Skill installation, prompts, validators, and review-only behavior continue to work without using it.

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

For a local runner smoke check that does not contact a model provider:

```powershell
python .\skills\agentic-code-review\scripts\run_review_passes.py --dry-run --no-diff --format json
```

Validate the runner config and prompt manifest without contacting a model provider:

```powershell
python .\skills\agentic-code-review\scripts\validate_review_runner.py --format json
```

`validate_review_runner.py --config` uses the same config-relative `prompt_manifest` resolution as the runner. The smoke tests cover validator config and manifest paths containing spaces.

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
skills/agentic-code-review/assets/review-prompt-manifest.json
skills/agentic-code-review/assets/review-runner.config.example.json
skills/agentic-code-review/assets/review-capacity-metrics.template.csv
skills/agentic-code-review/assets/review-capacity-metrics.schema.json
skills/agentic-code-review/assets/reviewer-comparison.example.json
skills/agentic-code-review/assets/reviewer-comparison.template.md
skills/agentic-code-review/assets/reviewer-comparison.schema.json
skills/agentic-code-review/agents/openai.yaml
skills/agentic-code-review/scripts/collect_github_metrics.py
skills/agentic-code-review/scripts/detect_review_fix_loop.py
skills/agentic-code-review/scripts/measure_diff.py
skills/agentic-code-review/scripts/run_review_passes.py
skills/agentic-code-review/scripts/validate_batch_triage.py
skills/agentic-code-review/scripts/validate_hostile_fixtures.py
skills/agentic-code-review/scripts/validate_metrics.py
skills/agentic-code-review/scripts/validate_reviewer_comparison.py
skills/agentic-code-review/scripts/validate_review_runner.py
tests/test_skill_scripts.py
scripts/check-skill.ps1
scripts/install-local.ps1
```

## License

Licensed under the Apache License 2.0. The official legal license text is in `LICENSE`.
