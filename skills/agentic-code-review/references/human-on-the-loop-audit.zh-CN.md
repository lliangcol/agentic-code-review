# Human On The Loop 审计

## 目的

当 review volume 高到人类无法逐行阅读，或 agent loop 在人类看到之前负责编写、评审和判断代码时，使用本引用。

目标是 audit 和 attention allocation，不是自动合并批准。

## 审计计划

建立明确计划：

- 永远需要人类 review 的高风险片段。
- 低风险片段的随机抽样大小。
- 对测试、CI gates、生成代码和重复 helpers 的 spot checks。
- 当 AI reviewer、gate 或样本发现 confirmed issue 时的升级规则。
- 对 merge、rollback 和 residual risk 负责的人类 owner。

## 可复现抽样

对低风险片段，记录：

- 总体规模和排除项。
- 随机种子或确定性排序键。
- 样本量或比例。
- 选择命令或方法。
- 结果摘要和升级决策。

当批次混合 docs、tests、generated files、runtime code 和 configuration 时，使用分层抽样。高风险片段不要放入随机池，因为它们需要直接人类 review。

## Model-Only Loop Guardrails

不要让 model-only loop 在缺少以下条件时批准高风险工作：

- model judgment 之前先运行 deterministic gates。
- 可行时使用独立 review roles 或 model families。
- 不可逆动作前有人类批准。
- residual-risk note 命名任何相关模型盲点。

## 输出

```md
## Audit Scope
抽样、spot-check 和排除的范围

## High-Risk Human Review
需要直接人类注意力的片段

## Sampling Plan
总体、排除项、随机种子或排序键、样本量、选择方法和结果

## Escalations
改变 review depth 的 confirmed issues 或 gate failures

## Human Owner
对 merge 和 rollback 负责的人
```
