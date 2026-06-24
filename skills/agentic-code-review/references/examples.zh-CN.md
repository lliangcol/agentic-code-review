# 示例

## 目的

当预期评审输出形态不清楚时，使用这些紧凑示例。根据真实仓库证据调整内容和措辞；不要在缺少源码支撑时复制结论。

当需要用代表性 prompts forward-test 本 Skill 时，使用 `assets/forward-test-scenarios.json`。它是 scenario checklist，不是 source evidence。

## L1 局部变更

```md
## Verdict
Ready

## Risk Tier
L1 - localized behavior with easy rollback.

## Reviewability
Intent, scope, and validation output are present.

## Findings
None.

## Test Review
No tests changed.

## CI / Validation
Reviewed command output: targeted unit test passed.

## Residual Risk
Low; limited to the touched helper.
```

## L3 高风险变更

```md
## Verdict
Needs confirmation

## Risk Tier
L3 - user data and permission boundary changed.

## Reviewability
Implementation and tests are reviewable, but rollback owner is missing.

## Findings
[P2] path/file.ext:42 - confirmed issue with authorization fallback.

## Test Review
Tests cover the happy path, but no negative permission case is present.

## AI Review Evidence
Correctness pass found the authorization issue. Security pass found no additional confirmed issue. The passes used different review roles.

## CI / Validation
Targeted tests passed. Negative permission test was not present.

## Human Merge Notes
Name the owner who accepts residual permission risk before merge.
```

## Not Reviewable

```md
## Verdict
Not reviewable

## Risk Tier
L4 - broad mixed diff across runtime, tests, generated files, and config.

## Reviewability
Missing slice map, decision log, validation output, and human merge owner.

## Required Evidence Missing
Provide a slice map, commands with output, test-change explanation, and owner for high-risk files.

## Findings
No speculative findings. The diff shape prevents responsible review.
```

## Not Reviewable 入口模式

- 缺少 validation：先提供准确命令和相关输出，才能评估 merge readiness。
- 缺少 decision log：对这个非平凡 agent-authored change，提供执行方案、关键假设、被排除替代方案和人类判断点。
- 生成代码 churn：将生成输出与行为变更拆开，或提供切片图说明哪些文件需要真实 review。
- 缺少高风险 owner：先命名人类负责人和 rollback path，review 才能支持合并结论。
- LLM trust boundary 不清楚：说明如何分隔、校验不可信输入，并阻止它改变 tool targets 或 approval decisions。

## 批量分流

```md
## Batch Triage

### High-risk
- PR A: touches billing retry behavior; needs owner, targeted tests, and rollback notes.

### Not reviewable
- PR B: large mixed agent change with no slice map or validation output.

### Needs work
- PR C: confirmed failing gate and weakened assertion.

### Safe-looking
- PR D: docs-only, clear intent, validation present.

## Human Attention Plan
Review PR A first, reject PR B until evidence is supplied, then handle PR C.
```

## LLM 安全评审

```md
## Verdict
Not ready

## Risk Tier
L3 - untrusted document text can influence tool arguments.

## Findings
[P1] path/file.ext:88 - model output can directly choose a file path used for writes without validation.

## Test Review
No hostile-input test proves that prompt injection is treated as data.

## CI / Validation
No security test was run for tool-argument redirection.

## Human Merge Notes
Require path allowlisting and human confirmation before irreversible writes.
```
