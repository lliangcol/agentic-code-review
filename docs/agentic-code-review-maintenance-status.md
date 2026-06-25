# Agentic Code Review Maintenance Status

Last updated: 2026-06-25

## Project Positioning

`agentic-code-review` is an evidence-gated, risk-tiered Agent Skill for reviewing AI-generated or human-written code changes in Codex and Claude Code. It is not an automatic fixer, general lint replacement, CI replacement, single-model approval wrapper, or merge approval system.

Default behavior stays review-only. The workflow must check reviewability first, prefer cheap review-effort signals before expensive review, tier review depth by blast radius, code lifetime, and shared understanding, inspect test changes separately, preserve CI and gate integrity, treat AI reviewer output as evidence only, and leave final merge responsibility with the human owner.

## Key File Index

- Root docs: `README.md`, `README.zh-CN.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md`.
- Maintainer docs: `docs/agentic-code-review-implementation-analysis.md`, `docs/agentic-code-review-source-notes.md`, `docs/codebase-graph.md`, `docs/source-refresh-checklist.md`, `docs/open-source-readiness.md`.
- Canonical Skill: `skills/agentic-code-review/SKILL.md`.
- Skill references: `skills/agentic-code-review/references/`.
- Skill assets: `skills/agentic-code-review/assets/`.
- Core tests: `tests/test_skill_scripts.py`.
- Local validation: `scripts/check-skill.ps1`.
- Local install: `scripts/install-local.ps1`.
- CI entry: `.github/workflows/validate.yml`.

## Script Entrypoints

- `skills/agentic-code-review/scripts/measure_diff.py`: cheap review-effort and risk signal measurement.
- `skills/agentic-code-review/scripts/run_review_passes.py`: optional local review runner with mock and command providers.
- `skills/agentic-code-review/scripts/validate_review_runner.py`: runner config and prompt manifest validation.
- `skills/agentic-code-review/scripts/validate_batch_triage.py`: batch triage record validation.
- `skills/agentic-code-review/scripts/validate_hostile_fixtures.py`: hostile input fixture validation.
- `skills/agentic-code-review/scripts/validate_metrics.py`: review-capacity metrics validation.
- `skills/agentic-code-review/scripts/validate_reviewer_comparison.py`: reviewer comparison validation.
- `skills/agentic-code-review/scripts/collect_github_metrics.py`: local GitHub export to review-capacity metrics conversion.
- `skills/agentic-code-review/scripts/detect_review_fix_loop.py`: optional review-fix-loop configuration detection.

## Test And CI Entrypoints

- Repository validation: `pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1`.
- Unit and smoke tests: `python -m unittest discover -s tests`.
- Runner dry run: `python ./skills/agentic-code-review/scripts/run_review_passes.py --format json --dry-run --no-diff`.
- Runner config validation: `python ./skills/agentic-code-review/scripts/validate_review_runner.py --format json`.
- CI workflow: `.github/workflows/validate.yml` runs the local validation script, JSON smoke checks, unit tests, and install smoke on Linux, macOS, and Windows.

## Current Known Risks

- The current branch contains broad changes across README, changelog, runner, validators, diff measurement, metrics collection, and tests. Treat those as existing work and avoid unrelated rewrites.
- JSON stdout purity and structured error consistency remain the highest-value stability theme for CLI users and automation.
- Runner command providers remain sensitive because they execute local commands. Config examples and docs must keep secrets in environment-owned provider configuration, never in repository files.
- Markdown validation is intentionally strict about private path leakage, secret-like values, localized companions, and CI gate weakening.
- Prompt and reviewer artifacts are evidence only. They must not imply real security guarantees, merge approval, or replacement of human ownership.

## Backlog

1. Add focused tests for JSON stdout purity across remaining validator and runner failure paths.
2. Keep cross-platform quoting coverage for config, manifest, prompt-manifest override, and context-file paths containing spaces.
3. Expand runner provider failure summaries for timeout, retry exhaustion, fallback, empty output, invalid JSON output, and command-not-found behavior.
4. Tighten documentation for remaining runner CLI edge cases without introducing write-capable defaults.
5. Continue expanding hostile fixtures as new risky review surfaces are discovered.
6. Keep README, Simplified Chinese README, Skill references, assets, and local validators synchronized without claiming review quality or cost savings.

## Completed Rounds

- Created this maintenance status file to support state-file-driven, small-step maintenance.
- Added the Simplified Chinese companion file so local Markdown structure and localization checks remain enforceable.
- Added a focused `validate_review_runner.py --format json` invalid-config test that proves structured errors are emitted on stdout, stderr stays empty, and the exit code is non-zero.
- Added a focused runner retry-exhaustion test that proves each failed command provider attempt is preserved in pass-level and fusion-level provider failure summaries while global stderr stays empty.
- Strengthened the missing-command fallback test so command-not-found failures must appear in both pass-level and fusion-level provider failure summaries without relying on traceback absence alone.
- Added a focused command provider timeout test that verifies timeout attempts are preserved in pass-level and fusion-level provider failure summaries and still produce a `Needs confirmation` fusion verdict.
- Added a focused empty-output command provider test that verifies a zero-exit command with empty stdout is still reported as a provider failure without leaking to global stderr.
- Added a focused non-JSON command provider output test that verifies bounded raw output, output-contract warnings, a `Needs confirmation` fusion verdict, and clean global stderr.
- Tightened prompt recording so rendered prompts are omitted by default, only `--include-prompts` records them, and `run.include_prompt_in_report` is rejected as config-level prompt recording.
- Added fail-closed runner config validation for unknown `run` keys so stale or risky controls such as auto-merge or write-file flags cannot be silently ignored.
- Added fail-closed provider config validation for unknown provider keys so misplaced secrets or misspelled timeout fields cannot be silently accepted.
- Added fail-closed pricing config validation for unknown pricing keys so misspelled cost fields cannot be treated as zero-cost defaults.
- Added fail-closed top-level runner config validation for unknown keys so stale controls outside `run`, `providers`, and `review_passes` cannot be silently accepted.
- Added fail-closed review pass config validation for unknown pass-level keys so stale or risky per-pass controls cannot be silently accepted.
- Documented runner stdout/stderr, exit-code, dry-run, and no-write behavior in the English and Simplified Chinese READMEs.
- Added runner invalid-config JSON stdout purity coverage for `run_review_passes.py --format json`.
- Expanded hostile fixture coverage for prompt injection, workflow weakening, dependency metadata, release metadata, tool execution, and secret exposure examples.
- Added runner missing-prompt-manifest JSON stdout purity coverage, including a manifest path containing spaces.
- Added validator missing-prompt-manifest JSON stdout purity coverage, including a manifest path containing spaces.
- Added runner and validator `--prompt-manifest` override quoting tests for manifest paths containing spaces.

## Next Round Recommendation

Continue with focused JSON stdout purity or documentation polish as new edge cases are found, plus additional hostile fixture categories as new risky review surfaces are discovered.
