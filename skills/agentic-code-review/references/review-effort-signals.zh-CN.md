# Review Effort 信号

## 目的

在深度评审前使用低成本信号，判断变更是否已经适合投入人工注意力、是否需要拆分，或是否应标记为 `Not reviewable`。

这些信号不能取代风险分层。很小的高风险片段仍然要升级；证据清晰的大型低风险生成更新仍可轻量处理。

## 低成本信号

在投入昂贵评审时间前，先检查：

- Patch 大小：变更文件数、行数、二进制或生成产物，以及 diff 是否能在一次可读评审中看完。
- 文件类型：迁移、认证、账单、权限、生产配置、prompt 或工具代码、生成代码、fixture 和发布元数据。
- 范围混杂：无关功能、重构、测试、格式化、依赖更新或生成文件混在一个变更中。
- 测试变更比例：测试或 fixture 主导 diff，尤其是断言被削弱或替换时。
- 评审往返风险：主观需求、不清晰验收条件，或需要产品判断但作者未提供的变更。
- 证据质量：缺少命令、只有摘要没有输出、CI 过期，或没有证明验证确实运行。
- 理解债务：重复 helper、行为隐藏在生成代码后、大范围抽象，或缺少切片图。

## 默认熔断阈值

当仓库没有更严格的本地规则时，使用这些启发式起点：

- 超过 20 个变更文件、超过 800 行变更，或超过 3 个无关行为片段：深度评审前要求切片图。
- 超过 40 个变更文件、超过 1,500 行变更，或行为变更与生成、vendor churn 混杂：默认 `Not reviewable`，直到拆分或映射清楚。
- 测试或 fixture 超过 diff 的一半：先读取 `references/test-change-review.md`，并要求测试变更说明。
- auth、permissions、billing、payments、deletion、migrations、production config、LLM tools、prompts 或 CI gates 中的任何高风险路径或符号：即使 diff 很小，也至少升级到 `L3`。
- workflow、coverage、lint、dependency、security 或 release-gate 变更：读取 `references/ci-gate-integrity.md`。

可用时，运行 `scripts/measure_diff.py` 作为 advisory helper。它会报告基于路径的信号，以及变更 diff 行中出现的高风险术语。它的输出是信号，不是结论。

当目标仓库需要更严格的本地阈值或项目专属路径模式时，使用 `assets/review-effort.config.example.json` 作为起点。通过 `scripts/measure_diff.py --config path/to/review-effort.json` 传入配置。

## 高维护成本 Agent PR 信号

当 agent-authored PR 可能陷入主观来回反馈时，在深度评审前尽早熔断：

- 验收标准主观、缺失，或与 diff 矛盾。
- agent 做了大范围设计选择，但没有 decision log。
- 变更混合实现、重构、测试重写、格式化和生成输出。
- 上一轮 review 要求判断或产品澄清，而 agent 只是重新生成代码。
- 作者无法命名一个会响应非机械反馈的人类负责人。

使用最小纠正动作：先要求验收标准、更紧的方案、更小切片或人类负责人，再投入 senior review 时间。

## 熔断决策

使用成本最低且可辩护的动作：

- 变更小、低风险、范围清晰且已有验证时，继续轻量评审。
- 意图、命令、决策日志或负责人信息不完整但容易补齐时，要求补充缺失证据。
- 无关范围或大范围 churn 掩盖行为变更时，要求切片图或更小 PR。
- 评审者主要是在重建缺失的意图、验证、负责人或 diff 形态时，返回 `Not reviewable`。
- 低成本信号暴露高影响半径、长期共享代码、安全边界或合并就绪风险时，升级到 `L3` 或 `L4`。

## 评审者动作

记录哪些低成本信号驱动了决策。

不要只因为大小就拒绝。说明让评审变得可处理所需的最小改动：按行为拆分、附上验证输出、恢复测试意图、增加决策日志，或指定人类负责人。

不要让干净的 AI 评审覆盖熔断证据。把 AI review 当作传感器，而不是结论。

在长期代码中接受新 helper 或抽象前，搜索是否已有相同职责的 helper。当重复业务逻辑会随时间分叉时，将其标记为理解债。
