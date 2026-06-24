# CI Gate 完整性

## 使用时机

当变更触及 workflows、required checks、lint、test commands、coverage、安全扫描、依赖策略、发布元数据、构建脚本或生成的 gate 配置时，使用本引用。

当 gate weakening 可能隐藏产品、安全、发布或治理失败时，至少按 `L3` 处理。

## 标记这些模式

- Required jobs、checks 或 branch-protection references 被删除或重命名，但没有等价替换。
- `continue-on-error`、allow-failure、宽泛排除、skipped paths 或条件 guard 让 gate 更容易绕过。
- Coverage、lint、typecheck、test、security、dependency 或 documentation thresholds 被降低。
- 删除 failing assertions、failing tests 或 security findings，而不是修复。
- Build 或 release scripts 不再在命令失败时失败。
- Dependency pins、lockfiles、provenance checks 或 artifact validation 被削弱。
- 生成的 release 或 governance metadata 变化，但没有源头解释。

## 必要证据

要求提交者说明：

- 哪个 gate 变了，以及为什么变。
- 变更前后的命令或 workflow 行为。
- 新 gate 仍会在目标缺陷类型出现时失败的证据。
- 接受 coverage 降低或 skipped check 的 owner。

如果 gate 行为不清楚，使用 `Not reviewable`，直到旧行为和新行为被证明。

## Reviewer 动作

优先恢复严格 gate，而不是接受补偿性说明。

当 gate 有意变更时，要求 replacement guard、更窄的 exclusion，或明确 sunset date。

不要把干净的 AI review 当作 weakened CI 可接受的证据。
