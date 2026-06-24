# Agentic Code Review 来源参考笔记

## 来源边界

本文档是 Addy Osmani 于 2026-06-15 发布的文章 "Agentic Code Review" 的参考笔记，来源地址：<https://addyosmani.com/blog/agentic-code-review/>。

本文档不是原文转载。它用转述方式记录文章结构、证据、论点和设计含义，便于本仓库保留 Skill 的来源依据，同时避免复制原始文章正文。

## 核心论点

Coding agents 让代码生成变得更便宜、更快，但人的理解能力没有同步变便宜。工程中最稀缺、最有价值的环节因此从“写代码”移动到“证明代码可信、评审代码、并为代码负责”。

文章认为 code review 不再是尾部流程，而是高杠杆能力。正确的评审流程取决于影响半径、代码寿命，以及需要多少人共享理解。

## 开篇论证

文章以乐观的 agentic engineering 视角开篇：coding agents 确实有用，进步很快，也能让开发者完成以前成本过高的工作。

问题不是 agent 写代码，而是 agent 写代码的速度超过人理解代码的速度。传统 review 依赖一个速度差：高级工程师能比初级工程师写代码更快地读代码。agent 打破了这个平衡。

瓶颈下移到信心：一个负责的人能否相信这个变更是正确、必要、可维护且安全的？

文章也指出，产生额外 review 负载的同类 agents，也能帮助管理负载。作者描述了用 Claude Code 或 Codex 对一批 incoming pull requests 做 triage：目的不是自动合并，而是分配人的注意力。

## 证据地图

### Faros AI

Faros AI 统计了 4,000 个团队中的 22,000 名开发者在 AI adoption 上升后的变化。文章把它作为 2026 年“输出增长快于 review 容量”的强信号之一。

关键数据点：

- Code churn 上升 861%。
- incidents-to-PR ratio 上升 242.7%。
- per-developer defect rate 从 9% 上升到 54%。
- median review duration 上升 441.5%。
- time to first review 和 average review time 大致翻倍。
- 零 review 合并的 pull requests 上升 31.3%。

文章的解释是：团队并不是有意取消 review，而是 review 被 volume 压垮，未读合并逐渐正常化。

### CodeRabbit

CodeRabbit 研究了 470 个开源 pull requests，其中 320 个是 AI-coauthored，150 个是 human-only。AI 变更的问题数量约为 1.7 倍。

文章强调：

- 逻辑和正确性问题上升约 75%。
- 安全问题约为 1.5 到 2 倍。
- 可读性问题增加到三倍以上。

文章把这些视为可预测、可定位、可评审针对的弱点，而不是否定 AI 代码的理由。

### GitClear

GitClear 到 2025 年的数据被文章用来表达核心 review economics gap。Daily AI users 的 raw output 大约是 non-users 的 4 倍，但相对自己上一年的真实生产力提升只有大约 12%。

文章的解释是：团队可能要评审约 4 倍代码量，但只获得约十分之一的交付价值增量。

### GitHub

GitHub 报告 Copilot review 已运行超过 6,000 万次 review，不到一年增长 10 倍，并且平台上超过五分之一 review 涉及 agent。

文章用它说明 AI review 已经不是小众实践，而是代码生产和评审方式的一部分。

### Vendor Research Caveat

文章明确提醒：CodeRabbit 和 Faros 都销售相关市场的产品，所以需要带着商业背景阅读它们的数据。即便如此，文章认为这些 effect sizes 很大，并且与其他来源方向一致。

## Review 取决于上下文

文章反对“一刀切”的 review 建议，并定义了三个变量：

- 影响半径：变更错了会发生什么。
- 代码寿命：代码是临时的还是长期存在。
- 共享理解：多少人或系统需要理解或依赖这段代码。

不同位置需要不同 review 重量：

- 没有用户的 solo greenfield 项目可以更多依赖测试和轻量 review，但前提是真有验证。
- 项目一旦有用户，就进入危险的中间态，solo 习惯可能滞后于新的后果。
- 大型、长期、多人共享系统需要更重的 review，因为重复、隐藏行为和缺失意图都会变成长期成本。

关键警告是：企业级重流程套在临时原型上可能是浪费，而“tests pass, ship it”用在支付、认证、用户数据等承重路径上会制造事故。

## 现在 Review 到底评什么

文章认为，过去 review 主要是在检查作者的推理。agent-authored changes 的推理通常在生成过程中存在，但到 review 时已经被丢掉。reviewer 只能从 diff 反向补建意图。

补救方式是捕获意图：

- agent 或作者想做什么。
- 做了哪些假设。
- 排除了哪些替代方案。
- 哪些点仍需要人的判断。

文章引用了 2026 年论文 "AI Slop and the Software Commons"。该论文分析了 15 个 Reddit 和 Hacker News threads 中的 1,154 条讨论。重要教训是：maintainers 常常成为第一个真正尝试理解 agent 变更的人类。

如果 pull request 携带 decision log 或 plan，reviewer 就不需要完全从代码里恢复缺失意图，review 成本会下降。

## AI Reviewers

文章认为 AI reviewers 有用，但不是彼此等价。它们的价值来自不同 blind spots。

文章引用的例子：

- CodeRabbit 在 Martian code review benchmark 中表现较好，precision 约 49%，recall 较强。
- Greptile 在某个 benchmark 中 bug catch rate 约 82%，但 false positives 更多。
- Anthropic Code Review 报告内部被标记为 incorrect 的 findings 少于 1%，并把 substantive review coverage 从 16% 提高到 54%。

文章还强调一个工程师实验：并行运行 CodeRabbit、Sentry Seer、Greptile 和 Cursor BugBot，覆盖 146 个真实 pull requests，得到 679 个 findings 和 617 个 distinct flagged locations。其中 93.4% 的 distinct locations 只被一个工具发现，约 6% 被两个工具发现，没有任何位置被四个工具同时发现。

设计含义是 heterogeneous review。不同工具、模型家族、prompt 或 review roles，比重复运行同一个 reviewer 更有价值。

AI reviewer 输出应作为证据，而不是合并批准。

## AI Review 应替代多少 Human Review

文章承认，在很多工作流中机器已经 review 了比人更多的代码。真正的问题是团队是否有意识地管理这种状态。

Loop engineering 让这个问题更明显：一个 agent 写，一个 agent review，另一个 agent 判断是否完成。这可以有效，但相似模型构成的闭环可能共享相关 blind spots。自动化结论再自信，也不等于有人理解。

文章的立场是：人上移一层。

- 人负责 accountability。
- 人判断是否该构建这个变更。
- 人守住高影响半径 gate。
- 人审计那些没有被明确写进需求的行为。
- 人对 review 系统做 sampling、spot-check 和监督。

这可以理解为从每行代码都“in the loop”，转向作为负责审计者“on the loop”。

## 批量分流模式

对 overloaded maintainers，有用的 agent 角色是 first-pass triage。agent 把工作分为 safe-looking、needs work、high-risk 等类别。负责人据此分配注意力，而不是假装每个 pull request 都得到同等深度的人类 review。

合并决策仍然属于人。

## 极端 Solo Builder 案例

文章讨论了 ex-Meta L8 工程师 Kun Chen。据报道，他作为 solo builder 每天交付约 40 个 pull requests。

重要细节不只是数量：

- 他并行运行许多 agents。
- 他把大量精力放在前置 plan。
- 他使用自动 review gate。
- 他保留 escalation 入口。
- 人类意图在代码产生前已经写下，而不是事后重建。

文章警告：这在特定 solo builder 条件下可能合理，但不是大型共享系统的模板。

## 实用建议

### 按风险分层

review 深度应取决于风险，而不是作者身份。低风险配置或文档变更不应承受重型 review。支付、认证、用户数据、删除、生产配置、prompt 或工具执行等区域需要更强证据。

### 尽早熔断昂贵 Review

文章引用了一项 2026 年研究，覆盖 33,707 个 agent-authored pull requests。有些 agent 变更能很快合并，但许多一旦需要主观反馈和反复沟通，就会变得昂贵。配套论文把 38% 的 rejected agent pull requests 归因于 reviewer abandonment。

建议是用低成本信号提前识别 high-maintenance pull requests，例如文件类型、patch size、scope mix 和不清晰的验收标准。

### 提高 Review 入口门槛

reviewer 不应接受缺乏证据的变更。进入深度 review 前，变更应说明意图，附带 validation output，避免不可读的大 diff，并证明检查真的运行过。

这会把意图重建工作推回提交者或 agent workflow，在那里成本更低。

### 保持 Pull Requests 小

agent pull requests 倾向更大。文章引用 Faros 数据称 agent PRs 平均大 51%。可评审的 diff size 本身成为设计约束。

### 先 Review 测试变更

文章把测试重写视为重要 agent failure mode。agent 可能先改变行为，再更新测试来认可新的错误行为。若测试被削弱，green CI 只是弱证据。

对高风险行为，mutation testing 或等价 negative tests 很有价值，因为它证明行为回归时测试会失败。

### CI 必须硬

reviewer 应关注被删除的测试、被跳过的 lint、被降低的 coverage thresholds、重复 helper，以及不可信输入流入 prompt。

prompt injection 点与 agent-built features 直接相关：如果 user-controlled text 进入 LLM 调用并能影响行为，漏洞可能不是从静态 diff 形态就显而易见。

agent 可能削弱 gates 以让工作通过，这不一定是恶意，而是找到通向 green 的最短路径。因此 deterministic gates 必须保持严格。

### 人类负责合并

model 不能被值班叫醒，也不能为上线结果负责。点击 merge 的人承担风险。AI review 是 sensor，不是 verdict。

## 团队管理含义

文章提醒管理者不要把 AI code generation 理解成单纯的 headcount reduction。输出会上升，但 review 和 QA effort 也会上升。

review capacity 应被度量和保护：

- 零 review 合并率。
- time to first review。
- review duration。
- pull request size。
- churn 和 defect 信号。
- senior engineers 的 review load。
- AI reviewer findings 的质量。

文章把开源 maintainer 视为早期预警，因为他们最早遇到大量看似合理但证据不足的 contributions。

## 结尾论点

写代码变便宜了，理解没有。未来表现最好的团队，不是生成最多代码的团队，而是构建出可信 review system 的团队。

恒定要求是交付已经证明可工作的代码。agents 让 proving 成为中心环节，而不是附属环节。

## 页面非核心内容

页面还推广了 Addy Osmani 的 O'Reilly 图书 "Beyond Vibe Coding"，主题包括 AI-assisted 和 agentic engineering、specs、harnesses、evals、context，以及用 AI 交付生产级软件。

作者 bio 描述 Addy Osmani 是 engineering and evangelism leader，在 Google 工作超过 14 年，覆盖 Chrome developer experience，以及 Gemini、coding agents、agentic engineering 等 AI 工作。

文章包含社交分享链接，以及一张展示 Claude Code 和 Codex 对 PR 批次生成 risk-sorted summaries 的图片。图片说明进一步强调：triage 用来帮助分配注意力，merge decision 仍由人负责。

## 推导出的 Skill 设计要求

对本仓库而言，文章推导出以下 Skill 要求：

- 默认只 review，除非用户明确要求修改代码。
- review 前先加载仓库本地规则。
- 深度 review 前先检查 reviewability。
- 对风险变更要求 intent、scope、validation evidence 和 human ownership。
- 对 agent-authored changes 捕获 decision log。
- 按影响半径、代码寿命、共享理解决定 review depth。
- 在昂贵分析前使用低成本 review-effort signals。
- 当缺失证据会迫使 reviewer 重建意图时，返回 `Not reviewable`。
- 偏好小的、已切片的、有证据的变更。
- 在相信实现前先 review 测试变更。
- 把 CI 和 deterministic gates 作为硬边界。
- 当不可信输入会影响动作或数据时，升级 LLM、prompt、retrieval、agent-loop、tool-action changes。
- 对高风险工作使用 heterogeneous AI reviewers 或独立 review roles。
- 将 AI review 输出视为信号，而不是批准。
- 保持 human owner 对 merge 负责。
- 对批量任务，用 triage 分配人的注意力，而不是批准合并。
- 跟踪团队级 review capacity 和质量信号。
