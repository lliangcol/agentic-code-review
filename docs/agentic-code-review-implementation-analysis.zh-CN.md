# Agentic Code Review 实现对比分析

## 范围

本文档对比 `docs/agentic-code-review-source-notes.zh-CN.md` 中整理的来源参考笔记与当前仓库实现。

本仓库是支持 Codex 和 Claude Code 的 Agent Skill package。主要运行入口是 `skills/agentic-code-review/SKILL.md`；详细行为位于 `skills/agentic-code-review/references/`；可复用接入素材位于 `skills/agentic-code-review/assets/`；Codex 专属元数据位于 `skills/agentic-code-review/agents/openai.yaml`；仓库校验位于 `scripts/check-skill.ps1`。

本次对比基于当前 checkout 文件完成。

## 总体结论

当前实现较完整地覆盖了文章核心模型。以下主线已经存在：

- 按风险 review，而不是按作者身份 review。
- 深度 review 前检查 reviewability。
- 使用影响半径、代码寿命、共享理解三轴。
- 把缺失意图和缺失证据视为 review blocker。
- 在昂贵 review 前使用低成本 review-effort signals。
- 谨慎读取测试变更。
- 将 CI 作为硬边界。
- 对高风险工作使用 heterogeneous AI review evidence。
- 把 AI review 视为 signal，而不是 approval。
- 保持 human owner 对 merge 负责。
- 支持 batch triage 和团队级 review metrics。

当前实现已经将初始优化清单落地为定量 review-effort 阈值、具体 reviewer role prompts、advisory diff measurement、阶段转换触发器，以及更强的 CI/gate review 指南。

## 覆盖矩阵

| 来源观点 | 当前实现 | 判断 |
| --- | --- | --- |
| review 从写代码转向证明可信 | `README.md`, `SKILL.md`, `output-format.md` | 已覆盖 |
| review 取决于影响半径、寿命、共享理解 | `references/risk-model.md` | 已覆盖 |
| solo、小团队、大系统工作流不同 | `references/adoption.md` | 已覆盖，包含 transition triggers |
| 缺失意图会让 review 变贵 | `references/review-intake.md` | 已覆盖 |
| agent-authored work 需要 decision log | `review-intake.md`, PR templates | 已覆盖 |
| 拒绝 evidence-poor changes | `review-intake.md`, `review-effort-signals.md` | 已覆盖 |
| 先用低成本 circuit-breaker signals | `review-effort-signals.md` | 已覆盖，包含定量默认阈值 |
| PR 应保持小且可切片 | `review-intake.md`, `review-effort-signals.md`, PR templates | 已覆盖 |
| 先 review 测试，再信任实现 | `test-change-review.md` | 已覆盖 |
| 高风险行为需要 mutation 或 negative tests | `test-change-review.md` | 已覆盖 |
| CI 不能被削弱 | `SKILL.md`, `test-change-review.md`, `ci-gate-integrity.md` | 已覆盖，包含专门 gate checks |
| LLM prompt/tool 安全和 prompt injection | `llm-security-review.md` | 已覆盖 |
| 异构 AI reviewers 能捕捉不同问题 | `heterogeneous-reviewers.md`, `reviewer-prompts.md` | 已覆盖，包含可直接运行的 role prompts |
| AI review 是证据，不是批准 | `SKILL.md`, `output-format.md`, `heterogeneous-reviewers.md` | 已覆盖 |
| batch triage 用来分配注意力 | `batch-triage.md` | 已覆盖 |
| 人类负责合并 | `SKILL.md`, `review-depth.md`, `output-format.md` | 已覆盖 |
| 团队 review capacity metrics | `team-adoption-metrics.md` | 已覆盖 |
| 闭环 agent review 风险 | `llm-security-review.md`, `human-on-the-loop-audit.md`, `review-depth.md` | 已覆盖 |
| fast-fail agent PR abandonment risk | `review-effort-signals.md`, `team-adoption-metrics.md` | 已覆盖 |
| 来源参考保存 | `docs/agentic-code-review-source-notes.zh-CN.md` | 已覆盖 |

## 已实现优点

1. Skill 默认只 review。这符合文章中“review 是负责任决策过程，而不是自动修复”的边界。

2. `review-intake.md` 落地了文章最强的操作性洞见：缺失 intent 和 validation 时，应该阻断深度 review，而不是消耗 reviewer 时间。

3. `risk-model.md` 直接编码了文章三轴：blast radius、code lifetime、shared understanding。

4. `review-depth.md` 将风险层级转成可执行要求：review depth、独立 passes、validation、human ownership。

5. `test-change-review.md` 捕捉了关键 agent failure mode：测试可能被改写成认可错误的新行为。

6. `llm-security-review.md` 增加了 agent-built systems 必须考虑的扩展：不可信文本可能影响 prompts、tool calls、files、commands、secrets 或 external actions。

7. `heterogeneous-reviewers.md` 正确避免把重复相同 prompt 当作独立证据。

8. `batch-triage.md` 符合文章中的 maintainer workflow：triage 是 attention allocation，不是 merge approval。

9. `team-adoption-metrics.md` 将文章对团队管理的担忧转成可跟踪信号。

10. `scripts/check-skill.ps1` 已经强制仓库卫生、双语 companion 覆盖、核心 review 概念 marker 对齐、换行、私有路径泄漏、JSON 有效性、指标模板形态、包产物洁净度，以及来源文章再分发边界。

## 已落地优化清单

初始对比识别出若干可执行化缺口，当前实现已处理：

1. 定量 cheap-signal 默认阈值已加入 `references/review-effort-signals.md`。
2. Agent PR abandonment 和高维护成本 review 信号已加入 `references/review-effort-signals.md` 与 `references/team-adoption-metrics.md`。
3. 可直接运行的 heterogeneous reviewer prompts 已加入 `references/reviewer-prompts.md`。
4. CI 与 gate integrity checks 已加入 `references/ci-gate-integrity.md`。
5. Human-on-the-loop sampling 与 audit guidance 已加入 `references/human-on-the-loop-audit.md`。
6. Adoption transition triggers 已加入 `references/adoption.md`。
7. Advisory diff measurement 已通过 `skills/agentic-code-review/scripts/measure_diff.py` 实现。
8. PR templates 已将 validation 拆成 commands、output、skipped checks 和 accepted failures。
9. Reviewer calibration protocol 已加入 `references/team-adoption-metrics.md`。
10. Closed-loop agent review guardrails 已加入 `references/llm-security-review.md` 与 `references/human-on-the-loop-audit.md`。
11. Existing-helper 与 duplication search guidance 已加入 `references/review-effort-signals.md`。
12. Test-heavy diff 输出变体已加入 `references/test-change-review.md` 与 `references/output-format.md`。
13. 额外 `Not reviewable` intake examples 已加入 `references/examples.md`。
14. README 已提醒 AI throughput 可能增加 review 和 QA load。
15. README 与文档语言策略已链接或覆盖转述型 source notes 和 implementation analysis。
16. `scripts/install-local.ps1` 在可用时从 Git 跟踪和未忽略的 Skill 文件清单安装，避免复制 Python bytecode cache 等被忽略的本地产物。
17. `scripts/check-skill.ps1` 现在动态发现需要简体中文 companion 的英文 Markdown，并检查本地化文件中的核心 marker 是否漂移。
18. 团队 review-capacity 跟踪已有起始资产：`assets/review-capacity-metrics.template.csv` 和 `assets/review-capacity-metrics.schema.json`。
19. `measure_diff.py` 现在会报告变更 diff 行中的高风险术语，不再只依赖高风险文件路径。
20. `measure_diff.py` 现在支持仓库专属 `--config` 覆盖，并避免因为文档中的通用 AI 或 schema 术语直接升级风险。
21. 脚本测试现在使用临时 Git 仓库覆盖 diff measurement 和 metrics validation 行为。
22. 团队指标在导入或发布前可通过 `scripts/validate_metrics.py` 校验。
23. Human-on-the-loop 审计指南现在包含可复现抽样字段：总体、排除项、随机种子或排序键，以及升级结果。
24. 异构 reviewer evidence 现在有可复用的对比模板和 JSON schema。
25. LLM 信任边界评审现在有 hostile-input fixture 文本，用于安全负向测试。
26. `review-fix-loop` 指南现在包含 snapshot、gate 和 finalize 阶段的命令记录模板。
27. Code graph 维护和来源刷新清单现在记录如何保持 graph-backed discovery 与外部证据更新。
28. Batch triage 现在有 machine-readable JSON template、schema assets 和 validator。
29. Hostile-input fixtures 现在有 machine-readable JSON 形式和 validator。
30. Reviewer comparison records 现在有 example JSON record 和 validator。
31. Metrics validation 现在校验真实日期、日期顺序和跨字段计数约束。
32. 回归测试现在覆盖 staged/base diff modes、invalid config、generated/test/untracked signals、install smoke 和 validator failure paths。
33. CI 现在将 checkout pin 到 commit SHA，并运行扩展后的 validator/test/install smoke suite。
34. 团队指标现在可通过 `scripts/collect_github_metrics.py` 从导出的 GitHub PR JSON 生成起始数据。
35. 可选 `review-fix-loop` 可用性现在可通过 `scripts/detect_review_fix_loop.py` 只读检测。
36. Forward-test scenario prompts 现在位于 `assets/forward-test-scenarios.json`。
37. Codex 与 Claude Code 支持现在共享同一 canonical Skill package，并提供可选择 runtime 的本地安装和 Claude Code 项目记忆 snippets。

## 剩余运行说明

当仓库图工具已经索引且可用时，优先用于代码发现。如果当前 checkout 没有可用图索引，则 fallback 到直接文件读取和 Git diff 检查。

## 无立即阻断缺口

当前 Skill 没有明显完全缺失的核心来源观点。最值得继续做的是把现有规则变得更可执行、更容易在不同仓库中一致应用。
