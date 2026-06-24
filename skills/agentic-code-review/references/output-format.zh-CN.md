# 输出格式

使用以下结构输出评审结果。问题优先，并以证据支撑。

```md
## Verdict
Ready / Not ready / Needs confirmation / Not reviewable

## Risk Tier
L0-L4 with reason

## Reviewability
Evidence present, missing, or too weak for deep review

## Required Evidence Missing
Smallest evidence needed to continue when verdict is Not reviewable

## Review Scope
Diff/source/rules inspected

## Findings
[P1/P2/P3] file:line - confirmed issue

## Test Review
测试变更、被削弱的测试、缺失 coverage。当测试主导 diff 或断言被重写时，将本节移到 `Findings` 前。

## Needs Confirmation
未确认的产品、负责人或上下文问题

## CI / Validation
Checks run, checks skipped, limitations

## AI Review Evidence
Reviewers/tools used, independent perspectives, overlap, disagreements, rejected findings

## Human Merge Notes
What the human owner must accept

## Residual Risk
Known remaining risk
```

## 结论含义

`Ready` 表示已检查证据支持在所述风险范围内合并或接受。

`Not ready` 表示确认缺陷或 gate 失败应阻塞合并。

`Needs confirmation` 表示评审后仍有产品、负责人或上下文事实未确认。

`Not reviewable` 表示缺少意图、证据、负责人、验证或 diff 形态，导致无法负责任地评审。

## AI 评审证据规则

把 AI review 当作信号。不要把 AI reviewer 一致表述为批准。

使用多个 AI reviewer 或多个 pass 时，总结独有的确认问题、分歧和误报。对 `L3+` 变更如果只使用了一个 reviewer 或视角，在剩余风险中说明该限制。

## 严重级别

`P1` 阻塞合并，因为它可能导致错误行为、数据或安全暴露、用户可见生产故障，或治理破坏。

`P2` 应在合并前修复，除非负责人明确接受风险。

`P3` 是有价值的清理、清晰度或可维护性反馈。
