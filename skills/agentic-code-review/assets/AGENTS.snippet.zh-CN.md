## Agentic Code Review

评审分支变更时，使用 `agentic-code-review` skill。

先读取仓库本地规则，再按风险对变更片段分层。

深度评审前先检查是否具备评审条件。如果缺少意图、验证证据、负责人、决策日志、切片图或 diff 形态，返回 `Not reviewable` 并列出最小缺失证据。

在昂贵评审前使用低成本 review-effort 信号。大范围 churn、生成文件或无关范围掩盖行为时，要求更小 PR 或切片图。

仔细审查测试变更。不要弱化 CI、跳过测试，或把 AI 评审当作合并批准。

当 workflows、lint、coverage、安全扫描、依赖策略、发布元数据或 required checks 发生变化时，先评审 CI/gate 完整性，再相信绿色状态。

对 LLM、prompt、检索、agent 循环或工具动作变更，评审不可信输入边界和 prompt injection 风险。

对批量 PR 评审，分流为 `Safe-looking`、`Needs work`、`High-risk` 和 `Not reviewable`；不要把分流当作合并批准。

对高风险评审，优先使用异构 AI 评审视角，并把 AI reviewer 证据报告为信号，而不是批准。

对高吞吐 agent review loops，使用 sampling 和 spot-check 审计计划。保持人类 owner 对 merge 和 rollback 负责。

如果配置了 `review-fix-loop`，在 review/fix/re-review 循环中使用 fresh snapshot。
