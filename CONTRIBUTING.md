# Contributing

## Scope

Contributions should improve the `agentic-code-review` Skill, its references, adoption templates, or validation scripts.

Keep the Skill generic. Do not hard-code private repository rules, company names, credentials, or local machine paths.

## Documentation Style

Public Markdown documentation must use separate English and Simplified Chinese files.

Keep English content in the original `*.md` path and Simplified Chinese content in a sibling `*.zh-CN.md` file.

Do not use paired `EN:` and `ZH:` paragraphs in the same Markdown file.

## Skill Design Rules

Keep `SKILL.md` short and procedural. Move detailed checklists into `references/`.

Keep integrations optional. `review-fix-loop` must remain a soft dependency.

Default behavior must remain review-only unless a user explicitly asks for fixes, commits, pushes, publishing, or external actions.

When changing Skill behavior, update the relevant reference files, `README.md`, adoption templates, and `scripts/check-skill.ps1` in the same change.

New public reference files must stay concise, include a `.zh-CN.md` companion, and be linked from `SKILL.md` only when Codex or Claude Code needs routing information for when to read them.

Do not copy article text, benchmark tables, or local downloaded artifacts into the repository. Capture durable review principles instead.

## Validation

Before opening a pull request, run:

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

If your environment does not have the Codex Skill validator, run `.\scripts\check-skill.ps1` and state that the Codex-specific validator was unavailable. For Claude Code changes, also run a smoke install to a test repository `.claude/skills` destination or the configured global Claude skills directory when possible.
