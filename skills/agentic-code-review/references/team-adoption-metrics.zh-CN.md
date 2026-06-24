# 团队接入指标

## 目的

当团队希望接入 agentic review、调整评审容量，或理解 AI 生成评审负载是否可持续时，使用这些指标。

这些是接入信号，不是每次调用 Skill 的必需 gate。

## 跟踪项

- 零评审合并：没有人类负责人评审就合并的变更。
- 首次评审时间：可信评审者看到变更前等待了多久。
- 评审持续时间：从首次评审到解决的耗时。
- PR 或 diff 大小：变更文件、变更行数、生成代码和混杂范围信号。
- 测试变更比例：diff 中有多少在重写测试或 fixture。
- 重新评审次数：修复后需要多少轮 fresh pass。
- gate 失败：测试、lint、覆盖率、安全、文档或治理失败。
- 不可评审比例：PR 缺少足够证据的频率。
- 决策日志完整度：agent 生成变更解释意图、假设和替代方案的频率。
- Reviewer 校准：按 reviewer 或工具统计有效独有发现、误报、重叠和漏报缺陷类别。
- Agent PR abandonment：主观反馈后停滞、缺少 owner 响应，或反复重新生成但没有处理意图的 review。

## 动作阈值

把趋势变化视为调整流程的信号：

- 零评审合并上升：合并前要求指定人类合并负责人。
- 首次评审时间或评审持续时间上升：减少进行中工作，并更早拒绝低证据变更。
- PR 或 diff 大小上升：要求更小 PR、切片图，或分离生成代码。
- 测试变更比例上升：先评审测试，并要求测试变更说明。
- gate 失败或重新评审次数上升：强化确定性 gate，并要求修复后 fresh re-review。
- 不可评审比例上升：在 PR 模板或仓库规则中强制入口字段。
- Reviewer 误报或重叠上升：重新校准 prompt、更换 reviewer 组合，或收窄每个 reviewer 的角色。
- Agent PR abandonment 上升：review 前要求验收标准、更小切片和人类 owner。

## Reviewer 校准协议

信任 reviewer 组合前，使用轻量校准集：

- 从团队自己的代码中选择有代表性的已合并、已拒绝和关联事故的变更。
- 指定 adjudication owner，判断 finding 是 valid、duplicate、false positive 还是 out of scope。
- 按 reviewer 跟踪 unique valid findings、false positives、overlap、missed defects 和 defect classes。
- 当 overlap 偏高或某 reviewer 反复漏掉某类问题时，轮换 prompts、roles 或 tools。
- 不要在没有本地校准的情况下把 benchmark 排名直接变成政策。

## 指标模板

使用 `assets/review-capacity-metrics.template.csv` 作为每周或每个发布周期跟踪的轻量起点。

当团队希望在导入 dashboard 或 review report 前校验收集到的指标时，使用 `assets/review-capacity-metrics.schema.json`。

发布或导入收集到的指标前，运行 `scripts/validate_metrics.py path/to/metrics.csv`。它不依赖外部包，会校验必要列、数值范围和日期形态。

使用 `scripts/collect_github_metrics.py exported-prs.json --repository owner/repo --period-start YYYY-MM-DD --period-end YYYY-MM-DD` 从 GitHub PR JSON 生成起始 metrics row。

完成人工 adjudication 后，用 `--adjudication-json path/to/reviewer-comparison.json` 传入 reviewer-comparison 记录，填充 `valid_ai_findings`、`false_positive_ai_findings` 和 `reviewer_overlap_count`。没有经过裁定的 reviewer evidence 时可省略该参数；CSV 保持向后兼容，这些字段仍为 `0`。

## 使用

使用指标调整入口规则、PR 大小预期、评审者分配和自动化 gate。

不要只用吞吐量证明评审质量提升。

如果评审容量饱和，先提高入口门槛，而不是降低安全检查。
