# Changelog

This project follows a lightweight changelog format inspired by Keep a Changelog.

## Unreleased

Added optional provider-abstracted review runner assets and script with prompt manifest versioning, dry-run/mock defaults, command-provider fallback, estimated token/cost reporting, and diff-rule fusion.

Added review runner config and prompt manifest validation, including provider, fallback, template, and output-contract checks.

Added reviewer adjudication overlays for GitHub metrics collection so AI finding quality fields can be derived from reviewer-comparison records instead of staying fixed at zero.

Strengthened CI and repository validation with explicit Python 3.10/3.11/3.12 coverage, runner smoke checks, legacy repository slug detection, and secret-like value scanning.

Initial project skeleton for `agentic-code-review`.

Added bilingual documentation, GitHub community files, Skill references, adoption templates, and optional `review-fix-loop` integration guidance.

Strengthened local validation to require repository metadata, scan dotfiles and `CODEOWNERS`, enforce configured line endings, and require final newlines.

Documented Linux/macOS `pwsh` usage and expanded GitHub Actions validation across Ubuntu, macOS, and Windows.

Added review intake, `Not reviewable` verdict support, LLM security review guidance, batch triage, team adoption metrics, and stronger PR review context templates.

Added install target overlap protection so `install-local.ps1 -Force` cannot delete or recursively copy the source Skill.

Added localized Markdown heading-count validation to catch English and Simplified Chinese companion structure drift.

Added review-effort circuit breakers, heterogeneous reviewer guidance, AI review evidence output, decision-log and slice-map template fields, hostile-input checks, adoption profiles, calibration metrics, worked examples, and richer example gate profiles.

Added paraphrased source notes, implementation analysis, quantitative review-effort thresholds, CI/gate integrity guidance, reviewer prompt templates, human-on-the-loop audit guidance, reviewer calibration protocol, stronger PR validation fields, and an optional diff measurement script.

Added Git file-list based installation, dynamic bilingual Markdown discovery, localized marker parity checks, review-capacity metric templates, package-artifact validation, and diff-line high-risk term reporting.

Added configurable diff-effort thresholds, script regression tests, review-capacity metrics validation, reviewer-comparison assets, hostile-input fixtures, reproducible audit sampling guidance, and review-fix-loop command-record guidance.

Added graph maintenance and source-refresh checklists, machine-readable batch triage and hostile-input assets, batch triage, reviewer comparison, and hostile fixture validators, stronger metrics cross-field checks, install smoke tests, and pinned GitHub Actions checkout.

Added GitHub PR JSON metrics collection, read-only review-fix-loop detection, and forward-test scenario assets.

Added explicit Codex and Claude Code runtime support documentation, Claude Code adoption snippets, runtime-selectable local installation, and runtime-specific validation guidance.

Added schema-to-validator consistency tests guarding the batch triage, reviewer comparison, and review-capacity metrics assets against drift, and made the metrics validator report malformed CSV rows that have too few or too many values.

Added an open source readiness checklist and explicit ignore rules for local agent runtime state.
