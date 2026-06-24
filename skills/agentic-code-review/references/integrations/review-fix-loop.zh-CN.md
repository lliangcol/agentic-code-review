# review-fix-loop 集成

## 职责划分

`agentic-code-review` 负责决定风险等级、评审深度、问题和合并就绪表述。

`review-fix-loop` 负责强制 fresh snapshot、gate 执行、run record，以及对失效片段重新评审。

## 启用条件

仅在满足以下条件之一时使用此集成：

- 用户明确提到 `review-fix-loop`。
- 仓库存在 `review-fix-loop.gates.json`。
- 仓库存在 `.review-fix-loop` 或 `.git/review-fix-loop`。
- 用户要求执行 review/fix/re-review 直到收敛。
- 任务是高风险合并就绪检查，且仓库已经使用 review-fix-loop。

## 工作流

1. 检测 CLI 和仓库配置，但不要初始化新配置。
2. 运行或请求第一轮 fresh snapshot。
3. 对变更片段应用本 Skill 的风险模型。
4. 评审问题，并将确认缺陷与 `Needs confirmation` 分开。
5. 只有用户明确要求修复时才修复。
6. 执行计划中的 gates，不弱化它们。
7. 执行后续 fresh snapshot，并重新评审失效片段。
8. 只有 fresh re-review 没有新的范围内问题且阻塞 gates 通过时才停止。

## 命令记录

记录每个阶段使用的精确本地命令或工具动作。根据目标仓库已安装的 `review-fix-loop` 接口调整名称。

```text
detect:   review-fix-loop status
record:   review-fix-loop record --target <branch-or-diff>
gates:    review-fix-loop gates run
snapshot: review-fix-loop record --fresh
finalize: review-fix-loop finalize
```

如果某条命令不可用，说明它不可用，不要把该阶段当作已通过。

使用 `scripts/detect_review_fix_loop.py --root . --format json` 执行只读可用性检查。它会报告仓库配置和 CLI 是否存在，但不会初始化新配置。

## 边界

不要自动初始化 review-fix-loop 配置。

不要复用旧 diff 作为最终 re-review 证据。

不要隐藏 gate 失败，也不要把不可用 gate 当作已通过。

除非用户明确要求，否则不要修复、提交、推送、发布或访问外部系统。
