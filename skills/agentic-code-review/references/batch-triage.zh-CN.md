# 批量分流

## 目的

使用批量分流在多个 PR、分支、提交或 diff 之间分配人工注意力。

分流不是合并批准。它是第一轮判断：哪些需要深度评审，哪些需要补证据，哪些看起来低风险。

## 分类

将每个项目归入一个分类：

- `Safe-looking`：低风险、小范围、意图清晰且有相关验证。
- `Needs work`：大体可评审，但存在具体缺陷或缺少修复。
- `High-risk`：认证、资金、用户数据、删除、迁移、生产配置、LLM 工具动作、大范围重构或长期共享代码。
- `Not reviewable`：缺少意图、验证证据、切片图、负责人或可读 diff 形态。

## 输出

输出保持紧凑，让负责人能决定把时间投入哪里。

```md
## Batch Triage

### High-risk
- PR or diff: reason, required next evidence

### Not reviewable
- PR or diff: smallest missing evidence

### Needs work
- PR or diff: confirmed issue summary

### Safe-looking
- PR or diff: why it can receive lighter review

## Human Attention Plan
What to review first and why
```

## 规则

不要根据分流结果自动合并。

当 triage 输出需要进入 dashboard、metrics report 或后续自动化时，使用 `assets/batch-triage.template.json` 和 `assets/batch-triage.schema.json`。JSON 分类仍然只是 attention allocation，不是 merge approval。

导入 machine-readable triage records 前，运行 `scripts/validate_batch_triage.py path/to/batch-triage.json`。

当 patch 大小、文件类型、测试变更比例、生成代码或缺失证据决定人工注意力优先级时，使用 `references/review-effort-signals.md`。

即使外围 PR 风险较低，也要升级其中任何小范围高风险片段。

对不可读的大型混杂 diff，优先拒收或要求拆分，而不是做浅层评审。
