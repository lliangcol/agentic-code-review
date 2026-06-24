# Codex and Claude Code Support Plan

Status: implemented. This document records the plan used for the dual-runtime support change; "current repository" statements in the background section describe the pre-change state that motivated the implementation.

## 1. Background & Problem Statement

Before this change, the repository packaged `agentic-code-review` primarily as a Codex Skill. The reusable review workflow was mostly agent-host neutral, but the public description, installer defaults, support templates, and validation gates still described Codex as the only supported runtime.

Pre-change repository evidence:

- `skills/agentic-code-review/SKILL.md` already loads both `AGENTS.md` and `CLAUDE.md`, so the core review workflow does not depend only on Codex.
- `README.md`, `SUPPORT.md`, issue templates, and `scripts/install-local.ps1` still describe Codex-only installation and support.
- `skills/agentic-code-review/agents/openai.yaml` is an OpenAI/Codex-specific integration artifact, with no Claude Code-specific companion.
- Root `.agents/` and `.codex/` directories are empty and not tracked, so they do not currently provide runtime support.

External runtime evidence to verify during implementation:

- Claude Code skills use a `SKILL.md` file in skill directories and can be invoked directly as `/skill-name`.
- Claude Code discovers skills under `~/.claude/skills/`, project `.claude/skills/`, and `.claude/skills/` inside added directories.
- Claude Code reads `CLAUDE.md` files as persistent project, user, or organization instructions.

Sources:

- [Claude Code skills documentation](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Claude Code `.claude` directory documentation](https://code.claude.com/docs/en/claude-directory)
- [Claude Code memory documentation](https://docs.anthropic.com/en/docs/claude-code/memory)

The problem to solve is not the review model itself. The problem is that implementation and documentation imply Codex-only support while the project is expected to run in both Codex and Claude Code.

## 2. Goals & Non-Goals

Goals:

- Make support for Codex and Claude Code explicit, accurate, and testable.
- Preserve the existing Codex Skill package and Codex validator path.
- Add a documented Claude Code installation path using the same canonical Skill content.
- Keep the Skill behavior review-only by default unless a user explicitly requests fixes, commits, pushes, publishing, or external actions.
- Keep repository-local adoption instructions usable through `AGENTS.md` and `CLAUDE.md`.
- Ensure final documentation keeps `Not reviewable`, `Needs confirmation`, risk tier, validation, human owner, decision log, slice map, CI gate, LLM trust boundary, and heterogeneous reviewers concepts intact across languages.

Non-goals:

- Do not rewrite the review methodology.
- Do not introduce hosted bots, model services, MCP servers, or external automation.
- Do not make `review-fix-loop` mandatory.
- Do not remove `agents/openai.yaml` or weaken Codex behavior.
- Do not use this planning record as authorization for unrelated implementation beyond the dual-runtime support change.

## 3. Constraints & Assumptions

Constraints:

- Public Markdown files require Simplified Chinese companions with matching structure.
- `scripts/check-skill.ps1` remains the repository-level hygiene gate.
- Codex-specific validation through the Codex Skill validator is optional because not every environment has the Codex system skill validator installed.
- Claude Code-specific validation should not rely on private local paths or account-specific state.
- Generated caches, bytecode, logs, and local-only artifacts must stay out of the install package.

Assumptions:

- The canonical Skill source remains `skills/agentic-code-review/`.
- Claude Code can consume the same `SKILL.md`, `references/`, `assets/`, and `scripts/` folder shape when installed under a Claude Code skill directory.
- Codex can continue consuming the same folder under `~/.codex/skills/`.
- Runtime-specific metadata should be additive rather than changing the common workflow semantics.

## 4. Alternatives Considered

Alternative A: Keep Codex-only packaging and only mention Claude Code in docs.

- Pros: Smallest change.
- Cons: Leaves installation and validation unsupported; users can still misread runtime scope.
- Rejected because it does not make Claude Code support testable.

Alternative B: Fork separate Codex and Claude Code skill directories.

- Pros: Clear runtime separation.
- Cons: Duplicates review rules and creates drift risk across `SKILL.md`, references, scripts, and assets.
- Rejected because the review workflow should remain single-source.

Alternative C: Keep `skills/agentic-code-review/` as canonical and add runtime-specific install/documentation surfaces.

- Pros: Preserves one source of truth while making both runtimes explicit.
- Cons: Requires installer, docs, and validation updates.
- Selected because it fixes the support gap without duplicating the review workflow.

## 5. Final Approach & Rationale

Use `skills/agentic-code-review/` as the canonical Agent Skill package for both runtimes.

Keep Codex-specific integration under `skills/agentic-code-review/agents/openai.yaml`. Add Claude Code support through installation and documentation rather than by forking the Skill body. The installer should support Codex, Claude Code, or both. Documentation should name the project as a cross-runtime Agent Skill package that currently includes Codex-specific metadata and Claude Code-compatible installation.

This approach accepts a small amount of runtime-specific installer logic to avoid duplicating the review workflow. It keeps human owner accountability, CI gate integrity, LLM trust boundary review, heterogeneous reviewers, decision log, slice map, validation evidence, and `Not reviewable` behavior unchanged.

## 6. Step-by-Step Modification Plan

Phase 1: Terminology and scope alignment.

- Update `README.md` and `README.zh-CN.md` overview text from Codex-only wording to Codex and Claude Code-compatible wording.
- Keep "Codex Skill" where referring specifically to Codex packaging or the Codex validator.
- Add a short runtime support matrix covering Codex, Claude Code, shared Skill content, and runtime-specific metadata.
- Update `docs/agentic-code-review-implementation-analysis.md` and `.zh-CN.md` so the package is no longer described as Codex-only.
- Update `SUPPORT.md`, `SUPPORT.zh-CN.md`, and bug report templates to ask for runtime/surface instead of Codex surface only.
- Update `CHANGELOG.md` and `CHANGELOG.zh-CN.md` with the dual-runtime support change before release.

Phase 2: Claude Code adoption artifact.

- Add a Claude Code project-instruction snippet, for example `skills/agentic-code-review/assets/CLAUDE.snippet.md` and `CLAUDE.snippet.zh-CN.md`.
- Keep it aligned with `AGENTS.snippet.md` but phrase it for `CLAUDE.md` project memory.
- Include explicit boundaries: review-only default, no external actions without user approval, preserve `Needs confirmation`, and do not treat AI review as approval.
- Add both snippet files to repository validation so missing localized companions or stale required artifacts fail fast.

Phase 3: Installer support.

- Extend `scripts/install-local.ps1` with runtime selection, for example `-Runtime Codex`, `-Runtime ClaudeCode`, or `-Runtime Both`.
- Preserve current default behavior unless the project intentionally chooses a breaking default change.
- Keep current Codex default destination as `$CODEX_HOME/skills` or `~/.codex/skills`.
- Add Claude Code default destination as `$CLAUDE_CONFIG_DIR/skills` when `CLAUDE_CONFIG_DIR` is set, otherwise `~/.claude/skills`, with explicit `-ClaudeDestination` override support.
- Install the same canonical Skill package to each selected runtime destination.
- Preserve target-overlap protection for both destinations.
- Continue excluding `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.pyc`, `.pyo`, and `.log` artifacts.
- Emit clear install output showing every runtime and destination installed.

Phase 4: Documentation updates.

- Add README installation examples for Codex only, Claude Code only, and both.
- Explain project-local Claude Code adoption using `.claude/skills/agentic-code-review/` only when the user wants repository-scoped skills; otherwise use `~/.claude/skills/`.
- Keep `AGENTS.md` adoption instructions and add parallel `CLAUDE.md` adoption instructions.
- Update `CONTRIBUTING.md` and `.zh-CN.md` so new public references are linked when Codex or Claude Code needs routing information, not Codex only.
- Update PR template validation checklist from "Codex Skill validator" to runtime-specific validation where available.
- Update `review-fix-loop.gates.example.json` to name the Codex validator as optional and Codex-specific.

Phase 5: Validation and tests.

- Add installer tests for `-Runtime Codex`, `-Runtime ClaudeCode`, and `-Runtime Both`.
- Add tests that Claude Code installs contain `SKILL.md`, `references/`, `assets/`, and `scripts/`.
- Add tests that install exclusions and target-overlap protections apply to Claude Code destinations.
- Extend `scripts/check-skill.ps1` required files to include Claude Code snippets and updated bilingual docs.
- Extend `scripts/check-skill.ps1` marker checks so future changes cannot silently remove the Claude Code support claim or the Codex/Claude Code runtime split.
- Keep the current Codex validator command documented as optional.
- Add a lightweight manual Claude Code smoke checklist: install to a test repository `.claude/skills` path or the configured global Claude skills directory, confirm the folder shape, and document the expected `/agentic-code-review` invocation.

Phase 6: Final review and release readiness.

- Run repository validation: `pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1`.
- Run script tests: `python -m pytest tests/test_skill_scripts.py`.
- Run the Codex Skill validator when available.
- Run a final `rg` audit for stale Codex-only wording, allowing only intentional Codex-specific references.
- Confirm that all English public Markdown changes have `.zh-CN.md` companions with matching heading counts.

## 7. Risks & Mitigations

Risk: Claude Code runtime requirements drift.

- Mitigation: Base implementation on current official Claude Code docs and isolate runtime-specific assumptions in README and installer comments.

Risk: Codex behavior regresses while adding Claude Code support.

- Mitigation: Preserve existing default installation path, keep `agents/openai.yaml`, and retain Codex validator as an optional gate.

Risk: The common Skill becomes cluttered with host-specific wording.

- Mitigation: Keep common behavior in `SKILL.md`; place runtime-specific installation and support language in README, snippets, and installer help text.

Risk: Bilingual documentation drifts.

- Mitigation: Keep English and Simplified Chinese updates in the same change and rely on `scripts/check-skill.ps1` heading and marker checks.

Risk: Users interpret AI review as merge approval.

- Mitigation: Preserve review-only default, human owner language, CI gate integrity, and `Not reviewable` / `Needs confirmation` verdict boundaries across all runtime docs.

## 8. Test & Validation Strategy

Required automated checks:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1`
- `python -m pytest tests/test_skill_scripts.py`

Recommended runtime-specific checks:

- Codex: run the Codex Skill validator when available.
- Claude Code: install to a test repository `.claude/skills` destination or the configured global Claude skills directory and verify the expected folder shape.
- Documentation: run `rg -n "Codex-only|for Codex|Codex surface|Codex environment|Codex skills directory"` and classify each remaining hit as intentional or stale.

Acceptance criteria:

- Documentation states that the workflow supports Codex and Claude Code.
- The installer can install to Codex, Claude Code, or both.
- Claude Code support does not require copying files by hand.
- Codex-specific validator and metadata remain available.
- `AGENTS.md` and `CLAUDE.md` adoption paths are both documented.
- No `Not reviewable`, validation, risk tier, human owner, decision log, slice map, CI gate, LLM trust boundary, or heterogeneous reviewers guidance is lost.

## 9. Rollback Strategy

Rollback conditions:

- Codex installation breaks.
- Repository validation fails because bilingual documentation or required package files are inconsistent.
- Claude Code installation assumptions are contradicted by current official docs or local smoke checks.

Rollback steps:

- Revert installer changes first if installation behavior regresses.
- Revert documentation wording only where it claims unsupported Claude Code behavior.
- Keep any neutral wording improvements that remain accurate for Codex.
- Re-run `scripts/check-skill.ps1` and `pytest` after rollback.

Rollback limitations:

- Rolling back docs alone may leave installer behavior mismatched; rollback must keep docs, tests, and installer behavior aligned.
- If Claude Code docs change, the correct action may be a follow-up compatibility patch rather than reverting all dual-runtime language.

## 10. Review-Fix-Re-Review Log

Round 1 review finding: The first plan draft made Claude Code support a documentation-only change and did not make installation testable.

- Fix applied: Added installer runtime selection, Claude Code destination handling, and installer tests.

Round 2 review finding: The first installer plan risked weakening Codex compatibility by changing the default path implicitly.

- Fix applied: Preserved the current Codex default unless a breaking default change is explicitly chosen.

Round 3 review finding: The plan did not distinguish repository validation from runtime-specific validators.

- Fix applied: Kept `scripts/check-skill.ps1` as the required repository gate, kept the Codex validator optional, and added a Claude Code smoke checklist.

Round 4 review finding: The plan could allow stale Codex-only wording to remain unnoticed.

- Fix applied: Added a final `rg` audit and explicit classification of intentional Codex-specific references.

Round 5 review finding: The plan missed release bookkeeping and did not require validation to preserve the new runtime-support promise.

- Fix applied: Added `CHANGELOG` updates and a `check-skill.ps1` marker requirement for the Codex/Claude Code runtime split.

Round 6 review finding: The installer default ignored Claude Code's `CLAUDE_CONFIG_DIR` override for the global configuration directory.

- Fix applied: Added `CLAUDE_CONFIG_DIR` support to the Claude Code default destination, covered it with tests, and updated README guidance.

Final re-review verdict: Implemented and validated as the dual-runtime support change. Future changes should keep installer behavior, documentation, and validation gates aligned.
