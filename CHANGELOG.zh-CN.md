# 变更日志

本项目采用受 Keep a Changelog 启发的轻量变更日志格式。

## 未发布

初始化 `agentic-code-review` 项目骨架。

增加双语文档、GitHub 社区文件、Skill 引用资料、接入模板和可选 `review-fix-loop` 集成指南。

加强本地校验，要求仓库元数据存在，覆盖仓库 dotfiles 和 `CODEOWNERS`，强制配置的行尾格式，并要求文件末尾换行。

补充 Linux/macOS 的 `pwsh` 使用说明，并将 GitHub Actions 校验扩展到 Ubuntu、macOS 和 Windows。

增加评审入口门槛、`Not reviewable` 结论支持、LLM 安全评审指南、批量分流、团队接入指标和更强的 PR 评审上下文模板。

增加安装目标重叠保护，避免 `install-local.ps1 -Force` 删除源 Skill 或递归复制源目录。

增加本地化 Markdown 标题数量校验，用于发现英文和简体中文 companion 的结构漂移。

增加 review-effort 熔断信号、异构 reviewer 指南、AI 评审证据输出、决策日志和切片图模板字段、恶意输入检查、接入画像、校准指标、worked example，以及更丰富的示例 gate profile。

增加转述型来源笔记、实现对比分析、定量 review-effort 阈值、CI/gate 完整性指南、reviewer prompt 模板、human-on-the-loop 审计指南、reviewer 校准协议、更强的 PR 验证字段，以及可选 diff measurement 脚本。

增加基于 Git 文件清单的安装、动态双语 Markdown 发现、本地化 marker 对齐检查、review-capacity 指标模板、包产物校验，以及 diff 行高风险术语报告。

增加可配置 diff-effort 阈值、脚本回归测试、review-capacity 指标校验、reviewer 对比资产、恶意输入 fixtures、可复现审计抽样指南，以及 review-fix-loop 命令记录指南。

增加 graph 维护和来源刷新清单、machine-readable batch triage 和 hostile-input assets、batch triage、reviewer comparison 与 hostile fixture validators、更强的 metrics 跨字段检查、install smoke tests，以及 pinned GitHub Actions checkout。

增加 GitHub PR JSON 指标采集、只读 review-fix-loop 检测，以及 forward-test scenario assets。

增加明确的 Codex 与 Claude Code runtime 支持文档、Claude Code 接入 snippet、可选择 runtime 的本地安装，以及 runtime 专属校验说明。

增加 schema 与 validator 的一致性测试,防止 batch triage、reviewer comparison 与 review-capacity 指标资产发生漂移;并让 metrics validator 报告字段过少或过多的非法 CSV 行。

增加开源就绪核对清单，并为本地 agent runtime 状态补充明确忽略规则。
