# Agentic Code Review 维护状态

最后更新：2026-06-25

## 项目定位

`agentic-code-review` 是一个面向 Codex 和 Claude Code 的 Agent Skill，用于对 AI 或人类生成的代码变更进行 evidence-gated、risk-tiered 评审。它不是自动修复器、通用 lint 替代品、CI 替代品、单模型批准包装器或合并批准系统。

默认行为保持只评审。工作流必须先检查是否可评审，在昂贵评审前优先使用低成本 review-effort 信号，按影响半径、代码生命周期和共享理解成本分层评审深度，单独审查测试变更，保护 CI 和 gate 完整性，只把 AI reviewer 输出当作证据，并把最终合并责任留给 human owner。

## 关键文件索引

- 根文档：`README.md`、`README.zh-CN.md`、`CHANGELOG.md`、`CONTRIBUTING.md`、`SECURITY.md`、`SUPPORT.md`、`CODE_OF_CONDUCT.md`。
- 维护文档：`docs/agentic-code-review-implementation-analysis.md`、`docs/agentic-code-review-source-notes.md`、`docs/codebase-graph.md`、`docs/source-refresh-checklist.md`、`docs/open-source-readiness.md`。
- Canonical Skill：`skills/agentic-code-review/SKILL.md`。
- Skill references：`skills/agentic-code-review/references/`。
- Skill assets：`skills/agentic-code-review/assets/`。
- 核心测试：`tests/test_skill_scripts.py`。
- 本地校验：`scripts/check-skill.ps1`。
- 本地安装：`scripts/install-local.ps1`。
- CI 入口：`.github/workflows/validate.yml`。

## 脚本入口

- `skills/agentic-code-review/scripts/measure_diff.py`：低成本 review-effort 和风险信号测量。
- `skills/agentic-code-review/scripts/run_review_passes.py`：可选本地 review runner，支持 mock 和 command providers。
- `skills/agentic-code-review/scripts/validate_review_runner.py`：runner config 和 prompt manifest 校验。
- `skills/agentic-code-review/scripts/validate_batch_triage.py`：batch triage record 校验。
- `skills/agentic-code-review/scripts/validate_hostile_fixtures.py`：hostile input fixture 校验。
- `skills/agentic-code-review/scripts/validate_metrics.py`：review-capacity metrics 校验。
- `skills/agentic-code-review/scripts/validate_reviewer_comparison.py`：reviewer comparison 校验。
- `skills/agentic-code-review/scripts/collect_github_metrics.py`：把本地 GitHub 导出转换为 review-capacity metrics。
- `skills/agentic-code-review/scripts/detect_review_fix_loop.py`：检测可选 review-fix-loop 配置。

## 测试和 CI 入口

- 仓库校验：`pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1`。
- 单元和 smoke 测试：`python -m unittest discover -s tests`。
- Runner dry run：`python ./skills/agentic-code-review/scripts/run_review_passes.py --format json --dry-run --no-diff`。
- Runner config 校验：`python ./skills/agentic-code-review/scripts/validate_review_runner.py --format json`。
- CI workflow：`.github/workflows/validate.yml` 在 Linux、macOS 和 Windows 上运行本地校验脚本、JSON smoke checks、单元测试和安装 smoke。

## 当前已知风险

- 当前工作区已经存在覆盖 README、changelog、runner、validators、diff measurement、metrics collection 和 tests 的较大范围改动。后续应把这些视为既有工作，避免无关重写。
- JSON stdout purity 和结构化错误一致性仍是 CLI 用户和自动化场景中收益最高的稳定性主题。
- Runner command providers 仍然敏感，因为它们会执行本地命令。配置示例和文档必须让 secrets 留在 provider 自己的环境中，不能写入仓库文件。
- Markdown 校验会严格检查 private path leakage、secret-like values、中英文伴随文件和 CI gate weakening。
- Prompt 和 reviewer artifacts 只能作为证据。它们不能暗示真实安全保证、合并批准或替代 human ownership。

## Backlog

1. 为剩余 validator 和 runner failure paths 补充 JSON stdout purity 聚焦测试。
2. 为包含空格的 config、manifest、context-file 和 output paths 补充跨平台 quoting 测试。
3. 扩展 runner provider failure summaries，覆盖 timeout、retry exhaustion、fallback、empty output、invalid JSON output 和 command-not-found 行为。
4. 收紧 `--dry-run`、`--no-write`、`--format json`、stdout 和 stderr contract、exit codes、写文件行为的文档说明。
5. 为 prompt injection、workflow weakening、dependency metadata、release metadata、tool execution 和 secret exposure 示例增加 hostile fixture 覆盖。
6. 保持 README、简体中文 README、Skill references、assets 和本地 validators 同步，并避免夸大 review quality 或 cost savings。

## 已完成轮次

- 创建此维护状态文件，用于支持 state-file-driven、小步维护。
- 增加简体中文伴随文件，确保本地 Markdown 结构和本地化校验继续可执行。
- 新增一个聚焦的 `validate_review_runner.py --format json` invalid-config 测试，证明结构化错误写入 stdout、stderr 保持为空，并返回非零退出码。

## 下一轮建议

聚焦一个 runner failure-summary 缺陷。最合适的下一步是为 command provider retry exhaustion 或 command-not-found 行为添加聚焦 unittest；只有当观察到的 report 含糊或不安全时，才修改 `run_review_passes.py`。
