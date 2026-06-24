---
name: agentic-code-review
description: 兼容 Codex 和 Claude Code 的证据门槛和风险分层 AI 辅助代码评审工作流。用于评审 PR、当前分支、diff、agent 生成代码，验证 review 结果，批量分流 PR，判断是否可合并，审计高吞吐 agent review loop，校准 AI reviewers，或 review AI 生成代码。默认只评审。强调可评审性入口、Not reviewable 结论、低成本 review-effort 熔断信号、风险分层、测试变更审查、异构 AI 评审证据、CI/gate 完整性、LLM/prompt 安全、可选 diff measurement、可选 fresh re-review via review-fix-loop，以及人类合并责任。
---

# Agentic Code Review

## 目的

使用本 Skill 按风险而不是按作者评审代码变更。把人的注意力保留给出错代价高的变更。

默认只评审。除非用户明确要求，否则不要编辑文件、提交、推送、发布、安装工具或访问外部系统。

## 工作流

1. 先读取仓库本地规则：`AGENTS.md`、`CLAUDE.md`、模块规则和项目评审文档。
2. 确定评审目标：当前 diff、分支、PR、粘贴的问题，或是否可合并的问题。
3. 深度评审前先检查是否具备评审条件。当意图、范围、决策日志、验证证据、测试输出、人类负责人或 diff 可读性不完整时，读取 `references/review-intake.md`。
4. 在昂贵评审前使用低成本 review-effort 信号。对大型、混杂、生成代码、高 churn 或意图不清的变更，读取 `references/review-effort-signals.md`。
5. 使用影响半径、代码生命周期和共享理解成本进行风险分层。风险不明显时读取 `references/risk-model.md`。
6. 按最高风险片段映射到 `L0-L4` 评审深度。读取 `references/review-depth.md` 获取深度要求。
7. 在相信实现变更前，单独审查测试变更。只要测试有变化，就读取 `references/test-change-review.md`。
8. 当变更把不可信文本传入 prompt、LLM 调用、agent 循环、检索或工具执行时，读取 `references/llm-security-review.md`。
9. 保持 CI 和 gate 完整性。当 workflows、lint、coverage、安全扫描、依赖策略、发布元数据或 required checks 发生变化时，读取 `references/ci-gate-integrity.md`。
10. 将确认缺陷与 `Needs confirmation` 分开。不要把假设当作已验证事实。
11. 使用 `references/output-format.md` 组织最终评审输出。

## 引用资料路由

对批量 PR 或多 diff 分流，读取 `references/batch-triage.md`，并将输出视为注意力分配，而不是合并批准。

对高风险评审、多轮评审或 AI reviewer 对比，读取 `references/heterogeneous-reviewers.md`。需要具体独立 reviewer prompts 时，读取 `references/reviewer-prompts.md`。

当用户要求运行本地独立 reviewer passes 时，使用 `assets/review-prompt-manifest.json`、`assets/review-runner.config.example.json` 和 `scripts/run_review_passes.py`。把 runner report 视为 review evidence，而不是合并批准。

对高吞吐 agent review loop、sampling、spot-check 或 model-only review audit，读取 `references/human-on-the-loop-audit.md`。

对 solo、小团队或大系统接入画像和阶段转换触发器，读取 `references/adoption.md`。

对团队接入、流程指标、评审容量问题或 reviewer 校准，读取 `references/team-adoption-metrics.md`。

需要输出示例或用真实评审任务 forward-test 本 Skill 时，读取 `references/examples.md`。

## 可选 review-fix-loop

`review-fix-loop` 是可选项。仅在用户明确要求、仓库存在配置，或任务要求 review/fix/re-review 直到收敛时使用。

启用时，读取 `references/integrations/review-fix-loop.md`，并将其作为 fresh snapshot 执行约束。

## 合并结论

只有证据支持时才给出 `Ready`、`Not ready`、`Needs confirmation` 或 `Not reviewable`。对于高风险变更，引用验证命令，或说明哪些验证未能运行。
