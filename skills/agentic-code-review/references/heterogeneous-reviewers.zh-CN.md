# 异构 Reviewer

## 目的

使用多个评审视角捕捉不同缺陷类别，但不要把任何 AI reviewer 当作合并批准。

异构性重要，是因为相同 prompt、模型或工具通常共享盲点。可用时优先选择不同工具、模型家族、prompt 或评审角色。

## 何时使用

以下场景使用本引用资料：

- `L3` 或 `L4` 评审。
- 认证、资金、用户数据、删除、生产配置、LLM 工具动作路径，或大范围长期抽象。
- 需要在多个变更间分配人工注意力的批量分流。
- 修复后的重新评审，因为首轮发现集可能已被变更失效。
- 团队在真实代码上比较 AI reviewer 有效性的校准工作。

## 如何运行

保持各轮评审相互独立。除非任务明确是验证 pass，否则不要把一个 reviewer 的发现喂给另一个 reviewer。

使用刻意不同的视角：

- 正确性和回归。
- 测试完整性、mutation 或负向用例覆盖。
- 安全、滥用、prompt injection 和信任边界。
- 运维回滚、可观测性、迁移和生产故障模式。
- 架构、共享所有权和理解债务。

如果只有一个模型或工具可用，通过不同评审角色和重置假设来模拟异构性。不要把同一个 prompt 重复两次当作独立证据。

需要具体 role prompts 时，读取 `references/reviewer-prompts.md`。比较前保持每个 pass 不知道其他 pass 的结果。

当 reviewer evidence 需要为校准、审计或高风险合并决策留档时，使用 `assets/reviewer-comparison.template.md` 或 `assets/reviewer-comparison.schema.json`。

将 JSON reviewer comparison records 导入团队指标或 review reports 前，使用 `scripts/validate_reviewer_comparison.py` 校验。

## 对比结果

总结重叠和分歧：

- 已由源码证据确认的问题。
- 每个 reviewer 独有的问题。
- 重复项或误报。
- 被拒绝的问题及原因。
- 仍需人类判断的剩余风险。

人类负责人保留合并决定。AI reviewer 一致只是支撑证据，不是批准。

对 model-only 或 loop-driven review，读取 `references/human-on-the-loop-audit.md`，并说明相关模型盲点带来的 residual risk。

## 校准

团队接入时，在自己的代码上跟踪 reviewer 质量：

- 每个 reviewer 独有的有效发现。
- 误报率或被拒绝发现比例。
- reviewer 之间的重叠。
- 后续由测试、事故或人工评审发现的漏报。
- 每个 reviewer 擅长或不擅长的缺陷类别。

使用校准结果选择 reviewer 组合和 prompt。不要假设某个 benchmark 结果会原样迁移到另一个代码库。
