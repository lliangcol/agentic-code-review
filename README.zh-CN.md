# Agentic Code Review Skill

English: [README.md](README.md)

[![Validate](https://github.com/lliangcol/agentic-code-review/actions/workflows/validate.yml/badge.svg)](https://github.com/lliangcol/agentic-code-review/actions/workflows/validate.yml)

## 概览

`agentic-code-review` 是一个 Agent Skill package，用于对 AI 或人类生成的代码变更进行证据门槛和风险分层评审。它包含 Codex 打包方式和 Claude Code 安装支持，两者共享同一份 canonical Skill 内容。

它默认只评审，不修改代码；会检查变更是否具备评审条件，在昂贵评审前使用低成本 review-effort 信号，重点关注测试变更和 CI 完整性，并可选集成 `review-fix-loop` 执行基于 fresh snapshot 的 review/fix/re-review 循环。

## Runtime Support

| Runtime 或使用方式 | 支持情况 |
| --- | --- |
| Codex | 通过 `skills/agentic-code-review/`、Codex Skill 安装和 `agents/openai.yaml` 元数据支持。 |
| Claude Code | 通过把同一 Skill 目录安装到已配置的 Claude skills 目录支持，通常是 `~/.claude/skills/agentic-code-review/`，设置了 `CLAUDE_CONFIG_DIR` 时则是 `$CLAUDE_CONFIG_DIR/skills/agentic-code-review/`，也可安装到项目 `.claude/skills/agentic-code-review/` 目录。 |
| 共享 Skill 内容 | `SKILL.md`、`references/`、`assets/` 和 `scripts/` 对两个 runtime 保持单一来源。 |
| Runtime 专属元数据 | Codex 专属元数据保留在 `agents/openai.yaml`；Claude Code 使用基于目录的 skill discovery 和 `CLAUDE.md` 项目记忆说明。 |

## 运行要求

- Python 3.10 或更高版本，用于本地辅助脚本和测试。
- Git，用于 diff measurement、安装打包和仓库校验。
- PowerShell 7 或更高版本，用于跨平台执行 `.ps1`。Windows 上可用 Windows PowerShell 运行脚本，但 CI 使用 `pwsh` 校验。
- 仓库校验不需要 API key。可选 review runner 的 command providers 应从自己的环境读取 secrets，不能把 secrets 写入配置文件。

## 为什么

编程代理生成变更的速度已经超过人类评审速度。有效做法不是对所有变更使用同样深度的评审，而是把人的注意力投入到出错代价高的地方。

本工作流受 Addy Osmani 的文章 [Agentic Code Review](https://addyosmani.com/blog/agentic-code-review/) 启发。本仓库不复制或再分发该文章正文。

## 本地安装

在本仓库根目录运行默认 Codex 安装：

```powershell
.\scripts\install-local.ps1
```

在 Linux 或 macOS 上，使用 PowerShell 7+ 运行同一脚本：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/install-local.ps1
```

如需安装到自定义 Codex skills 目录：

```powershell
.\scripts\install-local.ps1 -Destination "C:\Users\you\.codex\skills"
```

在 Linux 或 macOS 上，传入 POSIX 形式的目标路径：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/install-local.ps1 -Destination "$HOME/.codex/skills"
```

如需全局安装到 Claude Code：

```powershell
.\scripts\install-local.ps1 -Runtime ClaudeCode
```

默认 Claude Code 目标目录在设置 `CLAUDE_CONFIG_DIR` 时是该目录下的 `skills`；否则是 `$HOME/.claude/skills`。

如需同时安装到 Codex 和 Claude Code：

```powershell
.\scripts\install-local.ps1 -Runtime Both
```

如需安装为仓库级 Claude Code skill，将 Claude 目标目录指向该仓库的 `.claude/skills`：

```powershell
.\scripts\install-local.ps1 -Runtime ClaudeCode -ClaudeDestination ".\.claude\skills"
```

## 使用

常用触发方式：

```text
Use agentic-code-review to review the current branch.
使用 agentic-code-review review 当前分支。

Use agentic-code-review to validate these review findings.
使用 agentic-code-review 验证这些 review 结果。

Use agentic-code-review to decide whether this branch is merge-ready.
使用 agentic-code-review 判断当前分支是否可合并。

Use agentic-code-review + review-fix-loop to review/fix/re-review until clean.
使用 agentic-code-review + review-fix-loop 执行 review/fix/re-review 直到收敛。

Use agentic-code-review to triage these PRs by review risk.
使用 agentic-code-review 按评审风险分流这些 PR。
```

## 检查内容

该 Skill 使用三个维度进行风险判断：影响半径、代码生命周期、共享理解成本。

它先检查是否具备评审条件，再将变更映射到 `L0-L4` 评审深度，对大型或混杂 diff 使用熔断信号，单独审查测试变更，把 CI 作为硬边界，在相关场景评审 LLM、prompt 和工具动作信任边界，把 AI reviewer 证据记录为信号，并保留人类合并责任。

当变更缺少意图、验证证据、负责人、决策日志、切片图或可读 diff 形态时，该 Skill 可以返回 `Not reviewable`，并列出继续评审所需的最小缺失证据。

对批量 PR 或 diff，它可以将工作分流为 `Safe-looking`、`Needs work`、`High-risk` 和 `Not reviewable`，让人工注意力投入正确位置。

可选引用资料覆盖 CI/gate 完整性、可直接运行的异构 reviewer prompts、可留档的 reviewer 对比记录、machine-readable batch triage、恶意输入 fixtures、human-on-the-loop 审计计划、reviewer 校准，以及用于低成本 review-effort 信号的 diff measurement helper。

调用 `validate_batch_triage.py --format json` 时，invalid JSON 等 input failures 会在 stdout 输出结构化 JSON 错误并返回非零退出码；record-level validation failures 仍保留在普通 JSON result 的 `errors` 数组中。

调用 `validate_reviewer_comparison.py --format json` 时，invalid JSON 等 input failures 会在 stdout 输出结构化 JSON 错误并返回非零退出码；record-level validation failures 仍保留在普通 JSON result 的 `errors` 数组中。

调用 `validate_hostile_fixtures.py --format json` 时，invalid JSON 等 input failures 会在 stdout 输出结构化 JSON 错误并返回非零退出码；fixture-level validation failures 仍保留在普通 JSON result 的 `errors` 数组中。

## 来源笔记

文章来源依据以转述笔记保存于 `docs/agentic-code-review-source-notes.zh-CN.md`。实现对比和优化清单位于 `docs/agentic-code-review-implementation-analysis.zh-CN.md`。

刷新来源 claims 或外部证据时，使用 `docs/source-refresh-checklist.zh-CN.md`。维护本仓库 graph-backed code discovery 时，使用 `docs/codebase-graph.zh-CN.md`。

第一次公开推送到 GitHub 前，或之后进行任何公开发布前，使用 `docs/open-source-readiness.zh-CN.md`。

## 团队容量

AI-generated throughput 可能增加 review 和 QA 负载。不要只用吞吐量证明 review 质量提升。在降低安全检查前，跟踪 review capacity、零 review 合并、review duration、`Not reviewable` rate、gate failures 和 reviewer calibration。

使用 `skills/agentic-code-review/assets/review-capacity-metrics.template.csv` 和 `skills/agentic-code-review/assets/review-capacity-metrics.schema.json` 作为团队指标采集的起始素材。使用 `skills/agentic-code-review/scripts/validate_metrics.py` 校验收集到的指标；使用 `skills/agentic-code-review/scripts/collect_github_metrics.py` 从导出的 GitHub PR JSON 生成起始行。

调用 `validate_metrics.py --format json` 时，input 和 schema failures 会在 stdout 输出结构化 JSON 错误并返回非零退出码；row-level validation failures 仍保留在普通 JSON result 的 `errors` 数组中。

调用 `collect_github_metrics.py --format json` 时，unsupported payload shapes 或 invalid periods 等 input/validation failures 会在 stdout 输出结构化 JSON 错误并返回非零退出码。

如需包含 AI reviewer quality 字段，可传入一个或多个 reviewer-comparison 或 adjudication 记录：

```powershell
python .\skills\agentic-code-review\scripts\collect_github_metrics.py .\prs.json `
  --repository owner/repo `
  --period-start 2026-01-01 `
  --period-end 2026-01-07 `
  --adjudication-json .\reviewer-comparison.json
```

计算 metrics 前会先按 reviewer-comparison contract 校验 adjudication overlays。

## 可选 Review Runner

仓库包含一个仅依赖标准库的可选 runner，适合团队在不绑定某个 SDK 或 provider 的前提下，建立本地、可审计的 LLM/agent 调用链。默认配置使用 `mock` providers，因此可安全用于 CI 和 smoke tests。

```powershell
python .\skills\agentic-code-review\scripts\run_review_passes.py --dry-run --no-diff --format json
```

Runner 提供：

- 通过 `mock` 和 `command` providers 抽象 provider。
- 从 `assets/review-prompt-manifest.json` 进行多 pass prompt 编排。
- 通过 template ID 和 version 管理 prompt 版本。
- 超时、重试和 fallback provider 行为。
- 执行前校验 invalid providers、unknown fallback references 和 fallback cycles。
- Provider attempt failure summaries，用于复核 timeout、retry 和 fallback。
- Provider stdout/stderr 作为 structured 或 raw provider output 与 attempt summaries 写入 JSON 或 Markdown report 前，会对常见 secret-like 值做 best-effort redaction。
- 估算 token 和成本统计。
- 融合 `measure_diff.py` 规则信号的结构化 JSON 报告；当 helper 非零退出时，保留结构化 diff-measurement failure reasons。
- 对 config failure，`--format json` 会在 stdout 输出结构化错误并返回非零退出码。
- 默认不记录渲染后的 prompt；只有明确传入 `--include-prompts` 时才写入报告。

使用 `skills/agentic-code-review/assets/review-runner.config.example.json` 配置。Command provider 通过 stdin 接收渲染后的 prompt，并将 review 输出写到 stdout。Providers 仍必须避免打印 secrets；output-stream redaction 只是 report-safety fallback，不是安全保证。

相对 `prompt_manifest` 路径会基于 runner config 文件所在目录解析。Smoke tests 覆盖包含空格的 config 和 manifest 路径，因此自动化脚本应以 argument-array values 传递路径，而不是拼接 shell command string。

`--context-file` 接受可重复的本地文件路径，并把内容读入渲染后的 prompt。在 `--format json` 模式下，不可读取的 context file 会在 stdout 输出结构化 `review-runner-error-v1` 错误并返回非零退出码。Smoke tests 覆盖包含空格的 context file 路径。

Diff measurement 默认通过 `measure_diff_args: ["--no-untracked"]` 检查未暂存 working-tree diff。评审暂存提交候选时使用 `["--staged", "--no-untracked"]`；评审分支或工作区相对某个基线版本时使用 `["--base", "origin/main", "--no-untracked"]`。直接调用 `measure_diff.py --format json` 时，argument、config、missing-Git 和 Git context failure 会在 stdout 输出结构化 JSON 错误并返回非零退出码。Runner 会把这些 helper errors 保留在 `diff.errors` 中，而不是替换成通用 subprocess failure。

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

兼容性影响：该 runner 是增量能力。现有 Skill 安装、prompts、validators 和默认只评审行为都不需要使用它也能继续工作。

## 可选 review-fix-loop 集成

`review-fix-loop` 是可选依赖。当用户明确要求或仓库中检测到配置时，该 Skill 会把它作为 fresh snapshot 执行约束。

`agentic-code-review` 决定变更风险和评审深度；`review-fix-loop` 确保每一轮评审基于当前真实工作区。

## 仓库接入

最小侵入接入方式是全局安装 Skill，并在 Codex 或 Claude Code 中显式调用。

如需项目级提示，可将 `skills/agentic-code-review/assets/AGENTS.snippet.md` 复制到目标仓库的 `AGENTS.md`。

如需 Claude Code 项目记忆，可将 `skills/agentic-code-review/assets/CLAUDE.snippet.md` 复制到目标仓库的 `CLAUDE.md`。只有当 Skill 应限定在该仓库内使用时，才使用项目 `.claude/skills/agentic-code-review/` 安装；否则优先使用已配置的全局 Claude skills 目录（设置 `CLAUDE_CONFIG_DIR` 时为 `$CLAUDE_CONFIG_DIR/skills`，否则为 `~/.claude/skills/`）。

## 校验

发布变更前运行本地校验：

```powershell
.\scripts\check-skill.ps1
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$env:PYTHONUTF8 = "1"
python (Join-Path $codexHome "skills/.system/skill-creator/scripts/quick_validate.py") .\skills\agentic-code-review
```

在 Linux 或 macOS 上，对仓库校验脚本使用 `pwsh`：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$env:PYTHONUTF8 = "1"
python (Join-Path $codexHome "skills/.system/skill-creator/scripts/quick_validate.py") ./skills/agentic-code-review
```

仓库校验脚本是必跑项。Codex Skill 官方校验器是可选且 Codex 专属的，因为并非每个环境都安装了它。

如需运行不会访问模型 provider 的本地 runner smoke check：

```powershell
python .\skills\agentic-code-review\scripts\run_review_passes.py --dry-run --no-diff --format json
```

如需在不访问模型 provider 的情况下校验 runner config 和 prompt manifest：

```powershell
python .\skills\agentic-code-review\scripts\validate_review_runner.py --format json
```

`validate_review_runner.py --config` 使用与 runner 一致的、基于 config 文件目录的 `prompt_manifest` 解析。Smoke tests 覆盖包含空格的 validator config 和 manifest 路径。

Claude Code smoke check 可安装到测试仓库的 `.claude/skills` 目录或已配置的全局 Claude skills 目标目录，确认已安装目录包含 `SKILL.md`、`references/`、`assets/` 和 `scripts/`，再在该测试仓库的 Claude Code 中调用 `/agentic-code-review`。

## 项目结构

根目录文件面向 GitHub 和维护者。Skill 运行内容位于 `skills/agentic-code-review`。

简体中文伴随文件使用相同路径，并追加 `.zh-CN.md`。

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

## 许可证

本项目使用 Apache License 2.0。正式法律文本见 `LICENSE`。
