# Deep Research Optimization Backlog

Simplified Chinese: [deep-research-optimization-backlog.zh-CN.md](deep-research-optimization-backlog.zh-CN.md)

Implementation status date: 2026-06-24.

## Scope

This backlog extracts optimization items, risks, and technical debt from the local deep research report and reconciles them against the current worktree. The repository remains a shared Skill package, not a hosted review service. Any detail not established by the report or current code is marked `unspecified`.

Guardrails:

- Preserve the shared `skills/agentic-code-review` package.
- Preserve review-only default behavior and human merge ownership.
- Preserve Codex and Claude Code dual-runtime support.
- Preserve Python 3.10+, PowerShell, and CI compatibility.
- Avoid heavy dependencies unless a later task records a stronger reason.
- Give any new configuration a default and an example.

## Current Code Facts

- The repository already has explicit Python 3.10/3.11/3.12 CI coverage through `actions/setup-python`.
- `scripts/check-skill.ps1` already blocks the legacy repository slug, local private paths, generated package artifacts, malformed JSON, missing bilingual Markdown companions, and secret-like values.
- `skills/agentic-code-review/scripts/run_review_passes.py` already provides optional `mock` and `command` providers, prompt manifest loading, timeout/retry/fallback behavior, estimated token and cost accounting, and rule-plus-review fusion with `measure_diff.py`.
- `skills/agentic-code-review/assets/review-prompt-manifest.json` already contains versioned prompt templates and a structured review output contract.
- `skills/agentic-code-review/scripts/collect_github_metrics.py` already accepts adjudication overlays to populate `valid_ai_findings`, `false_positive_ai_findings`, and `reviewer_overlap_count`.
- The current code has no local evidence for GitHub About metadata. That item is `unspecified` from the local worktree and must be verified or changed outside this repository if needed.

## Priority Definitions

| Priority | Meaning |
| --- | --- |
| P0 | Must not regress because it protects safety, installability, review-only behavior, or dual-runtime compatibility. |
| P1 | High-value correctness, operability, or validation work that directly closes report risks or protects current new runner behavior. |
| P2 | Useful hardening or maintainability work with lower immediate blast radius. |
| P3 | Nice-to-have documentation, examples, packaging polish, or optional scale work. |

## P0 Tasks

| ID | Item | Current fact | Status | Decision and reason |
| --- | --- | --- | --- | --- |
| P0-01 | Preserve review-only behavior and human merge ownership. | `SKILL.md`, output references, README, and runner mock output all avoid merge approval. | Guardrail, open for every future change. | Keep as P0 because it is the core safety boundary of the Skill. |
| P0-02 | Preserve shared Skill package and Codex/Claude Code compatibility. | `install-local.ps1`, README, `check-skill.ps1`, and tests cover Codex and Claude Code installation shape. | Guardrail, open for every future change. | Do not split runtime content unless a later task adds explicit packaging profiles. |
| P0-03 | Keep default validation offline and secret-free. | README states no API key is required; default runner config uses mock providers; check script scans secret-like values. | Guardrail, open for every future change. | External providers must stay opt-in command providers that read secrets from their own environment. |
| P0-04 | Keep project installable, runnable, and testable on Python 3.10+, PowerShell, and CI. | CI matrix and local validation already exercise Python helpers, tests, and PowerShell install smoke checks. | Guardrail, open for every future change. | Any new feature must include a smoke path that does not require external services. |

## P1 Tasks

| ID | Item | Current fact | Status | Decision and reason |
| --- | --- | --- | --- | --- |
| P1-01 | Validate review runner configuration and prompt manifest shape. | `validate_review_runner.py` now checks runner config, prompt manifest, providers, fallbacks, templates, passes, and output contracts. | Complete in round 3. | Add a lightweight standard-library validator because the runner is now the main LLM abstraction surface. |
| P1-02 | Enforce structured review output contracts from command providers. | The runner now validates structured output required fields and top-level field types before fusion. | Complete in round 2. | Treat invalid reviewer output as non-blocking evidence that needs confirmation, not as a clean pass. |
| P1-03 | Strengthen prompt template versioning policy. | Templates have IDs and versions; change policy and schema checks are only partially explicit. | Open. | Add validation and documentation so prompt changes are auditable and rollback-friendly. |
| P1-04 | Keep multi-provider behavior minimal but explicit. | `mock` and `command` providers support many external tools without SDK dependencies. Native OpenAI/Anthropic SDK providers are `unspecified`. | Open as design decision. | Avoid SDK providers for now to keep dependency weight low; document command-provider contract as the supported extension point. |
| P1-05 | Improve timeout, retry, fallback, and failure observability. | Runner reports now include pass-level `attempt_failures` and fusion-level `provider_failures`; provider degradation forces `Needs confirmation`. Backoff policy is `unspecified`. | Complete in round 4 for reporting and fusion. | Keep immediate retries for now; add clearer failure summaries before adding configurable backoff. |
| P1-06 | Protect rule-check plus LLM fusion semantics. | Fusion now treats structured output errors and provider failures as `Needs confirmation` signals. | Complete in rounds 2 and 4. | Add tests that malformed or incomplete LLM output cannot produce `Ready`. |
| P1-07 | Keep metrics calibration closed-loop. | Adjudication overlays now populate AI finding quality fields and are validated against the reviewer-comparison contract before import. | Complete in round 5. | Validate overlay records before calculating team metrics so calibration data cannot silently drift. |
| P1-08 | Maintain CI and security gate integrity. | Local validation now enforces Validate workflow permission, credential, setup-python, matrix-version, and full-SHA action pinning guards. CodeQL, coverage gate, and PowerShell analyzer remain `unspecified`. | Partially complete in round 6. | Prefer low-dependency checks first; heavier analyzers remain `unspecified` until the project accepts extra setup cost. |
| P1-09 | Document external GitHub metadata drift handling. | Local files no longer expose the old repository slug; GitHub About metadata is not in local code. | Open external task. | Track as manual release checklist work because it cannot be changed by local code edits. |

## P2 Tasks

| ID | Item | Current fact | Status | Decision and reason |
| --- | --- | --- | --- | --- |
| P2-01 | Refactor runner module boundaries. | `run_review_passes.py` contains config loading, provider execution, prompt rendering, cost estimation, output parsing, and fusion in one script. | Open. | Keep the single file until validation is stronger, then split into focused helpers without changing CLI behavior. |
| P2-02 | Improve typing and exception consistency. | Scripts use type hints and custom `ConfigError` in the runner, but no static type gate exists. | Open. | Avoid mypy until dependency policy is explicit; add focused runtime tests first. |
| P2-03 | Add local observability artifacts. | Runner reports include `run_id`, timestamps, attempts, elapsed time, token estimates, cost estimates, and fusion status. Metrics/traces export backend is `unspecified`. | Open. | Prefer JSON report fields and optional trace files over a heavy telemetry dependency. |
| P2-04 | Add larger integration and E2E fixtures. | Unit tests cover many scripts and install paths; no external live-model E2E exists. | Open. | Keep live providers out of CI; add deterministic command-provider E2E fixtures. |
| P2-05 | Add optional reproducible development environment. | No devcontainer or Dockerfile is present. Deployment target is `unspecified`. | Open. | Add only an optional validation environment; do not turn the Skill into a service container. |
| P2-06 | Add performance and scale baselines. | `measure_diff.py`, metrics collection, and repository validation are linear local scripts; no benchmark exists. | Open. | Add opt-in benchmark scripts or workflow-dispatch checks only after functional gates are stable. |
| P2-07 | Improve release and deployment documentation. | README covers local install and validation; release packaging and versioned distribution are lightweight. | Open. | Treat deployment as Skill distribution, not service deployment, unless a later product direction changes. |
| P2-08 | Extend security automation carefully. | Secret-like scanning exists; external secret scanning, CodeQL, Semgrep, Bandit, and PSScriptAnalyzer are not configured. | Open. | Introduce only checks that do not break cross-platform installability or add heavy dependency cost without clear value. |

## P3 Tasks

| ID | Item | Current fact | Status | Decision and reason |
| --- | --- | --- | --- | --- |
| P3-01 | Add more examples for command-provider integrations. | README gives a generic command provider example. Specific Codex/Claude/external model commands are `unspecified`. | Open. | Keep examples generic until real provider commands can be verified. |
| P3-02 | Add more adoption and rollout checklists. | Adoption docs exist, but organization-specific rollout cadence is `unspecified`. | Open. | Keep generic guidance; avoid inventing team policy. |
| P3-03 | Add diagram updates when architecture changes. | `docs/codebase-graph.md` exists. | Open as maintenance. | Update diagrams only when module boundaries actually change. |
| P3-04 | Add optional coverage reporting. | CI runs tests but does not report coverage. Coverage threshold is `unspecified`. | Open. | Do not add a threshold until the project decides which behavior should be coverage-critical. |
| P3-05 | Add source refresh reminders. | Source refresh checklist exists. Automation schedule is `unspecified`. | Open. | Keep manual unless stale-source incidents appear. |

## Round 1 Execution Record

Current problem: the deep report is broader and partly older than the current repository. Several risks it calls out are now fixed, while newer runner surfaces introduce validation and contract risks that need a concrete backlog.

Proposed solution: add this backlog as a tracked documentation artifact with P0-P3 items, current-code evidence, `unspecified` markers, and decision reasons.

Code or configuration changes: no runtime code or configuration changes in this slice; documentation only.

Tests: run repository validation and Python unit tests after adding the document.

Documentation update: this file and the Simplified Chinese companion file.

Compatibility impact: none. This slice does not alter Skill packaging, default review-only behavior, Codex/Claude Code runtime support, Python requirements, PowerShell scripts, or CI.

Validation steps:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
python -m unittest discover -s tests
```

## Round 2 Execution Record

Current problem: the optional review runner parsed provider stdout as JSON but did not enforce the `structured-review-v1` contract before fusion. A provider could return incomplete JSON and still appear as an `ok` reviewer pass.

Proposed solution: validate required structured output fields and top-level field types after provider execution. Keep provider process status separate from output-contract validity, and make fusion return `Needs confirmation` when output-contract errors are present.

Code or configuration changes: update `run_review_passes.py` to add structured output validation and output-contract warnings; update tests with an incomplete command-provider response; no config format change.

Tests: run the focused review-runner test class, full unit suite, and repository validation.

Documentation update: mark P1-02 complete in this backlog and record this slice.

Compatibility impact: additive report fields only. Existing configs, mock defaults, command-provider contract, install paths, and review-only behavior remain unchanged.

Validation steps:

```powershell
python -m unittest tests.test_skill_scripts.ReviewRunnerTests
python -m unittest discover -s tests
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
```

## Round 3 Execution Record

Current problem: runner config and prompt manifest assets could be JSON-valid while still containing invalid provider references, fallback targets, template references, or output-contract metadata. The default runner smoke check only exercised enabled mock passes.

Proposed solution: add a standard-library validator that checks config, prompt manifest, provider definitions, fallback references, review passes, templates, run settings, and output contracts without contacting a model provider.

Code or configuration changes: add `validate_review_runner.py`; wire it into repository validation, CI py_compile, and CI JSON smoke; document the command in README; add unit tests for the default config and a missing fallback failure.

Tests: run the focused review-runner tests, full unit suite, and repository validation.

Documentation update: mark P1-01 complete in this backlog, update README, and update the changelog.

Compatibility impact: additive script and CI check only. Existing runner config shape, command-provider behavior, mock defaults, Skill packaging, and runtime support remain unchanged.

Validation steps:

```powershell
python -m unittest tests.test_skill_scripts.ReviewRunnerTests
python -m unittest discover -s tests
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
```

## Round 4 Execution Record

Current problem: provider attempts already contained failure details, but users had to inspect every attempt to see timeout, retry, or fallback degradation. A successful fallback could otherwise hide that the primary provider failed.

Proposed solution: add pass-level `attempt_failures` and fusion-level `provider_failures`, and make any provider attempt failure keep the fused verdict at `Needs confirmation`.

Code or configuration changes: update `run_review_passes.py` report and fusion output; add tests for mock fallback and successful command fallback; update README, changelog, and this backlog.

Tests: run the focused review-runner tests, full unit suite, and repository validation.

Documentation update: mark P1-05 reporting and fusion complete in this backlog, update README, and update the changelog.

Compatibility impact: additive report fields plus a more conservative fusion verdict when a provider attempt fails before fallback. CLI, config shape, provider execution, retry counts, and fallback mechanics remain unchanged.

Validation steps:

```powershell
python -m unittest tests.test_skill_scripts.ReviewRunnerTests
python -m unittest discover -s tests
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
```

## Round 5 Execution Record

Current problem: GitHub metrics adjudication overlays could be used to calculate AI finding quality fields with only partial local type checks. That left room for drift from the reviewer-comparison contract.

Proposed solution: reuse the existing reviewer-comparison validator before importing adjudication overlay records into `collect_github_metrics.py`.

Code or configuration changes: update `collect_github_metrics.py` to validate extracted overlay records; add a failure-path test for invalid reviewer counts; update README, changelog, and this backlog.

Tests: run the focused metrics collection tests, full unit suite, and repository validation.

Documentation update: mark P1-07 complete in this backlog, clarify overlay validation in README, and update the changelog.

Compatibility impact: valid overlay files are unchanged. Invalid overlays now fail earlier with a clear validation error instead of producing derived metrics.

Validation steps:

```powershell
python -m unittest tests.test_skill_scripts.MetricsCollectionTests
python -m unittest discover -s tests
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
```

## Round 6 Execution Record

Current problem: the Validate workflow already used low-risk settings, but those settings were not all enforced by the local repository gate. Future edits could silently weaken permissions, action pinning, or Python setup.

Proposed solution: add local `check-skill.ps1` guards for `contents: read`, disabled checkout credential persistence, explicit `actions/setup-python`, matrix-driven Python version selection, and full commit SHA pinning for every `uses:` action.

Code or configuration changes: update `check-skill.ps1`; add a regression test that rewrites `actions/setup-python` to a tag and expects validation failure; update changelog and this backlog.

Tests: run the focused repository workflow test, full unit suite, and repository validation.

Documentation update: mark the low-dependency portion of P1-08 complete in this backlog and update the changelog.

Compatibility impact: local validation is stricter. Runtime behavior, install paths, runner behavior, and workflow behavior are unchanged when the workflow keeps the existing guardrails.

Validation steps:

```powershell
python -m unittest tests.test_skill_scripts.RepositoryWorkflowTests
python -m unittest discover -s tests
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
```

## Decision Log

| Decision | Reason |
| --- | --- |
| Treat the first slice as backlog documentation. | It makes the report-to-code reconciliation reviewable before behavior changes. |
| Mark external GitHub metadata as `unspecified` locally. | The local worktree cannot prove or edit GitHub About metadata. |
| Keep provider support command-based for now. | It gives multi-provider support without adding SDK dependencies or secrets to config. |
| Prioritize runner config and output validation next. | The runner is the newest high-value surface and validation gaps can affect review verdict trust. |
