# 变更日志

本项目采用受 Keep a Changelog 启发的轻量变更日志格式。

## 未发布

增加可选的 provider 抽象 review runner 资产和脚本，支持 prompt manifest 版本管理、dry-run/mock 默认值、command-provider fallback、估算 token/cost 报告，以及 diff 规则信号融合。

增加 review runner config 和 prompt manifest 校验，覆盖 provider、fallback、template 和 output-contract 检查。

加强 review runner 校验，在执行前拒绝 provider fallback cycles。

调整 `run_review_passes.py --format json` config failure 行为：在 stdout 输出结构化 JSON 错误，同时返回非零退出码。

调整 `measure_diff.py --format json` argument、config、missing-Git 和 Git context failure 行为：在 stdout 输出结构化 JSON 错误，同时返回非零退出码。

调整 `collect_github_metrics.py --format json` input 和 validation failure 行为：在 stdout 输出结构化 JSON 错误，同时返回非零退出码。

调整 `validate_metrics.py --format json` input 和 schema failure 行为：在 stdout 输出结构化 JSON 错误，同时返回非零退出码。

调整 `validate_batch_triage.py --format json` input failure 行为：在 stdout 输出结构化 JSON 错误，同时返回非零退出码。

调整 `validate_reviewer_comparison.py --format json` input failure 行为：在 stdout 输出结构化 JSON 错误，同时返回非零退出码。

调整 `validate_hostile_fixtures.py --format json` input failure 行为：在 stdout 输出结构化 JSON 错误，同时返回非零退出码。

调整 review runner 行为：当 diff measurement 非零退出时，在 `diff.errors` 中保留结构化 `measure_diff.py --format json` helper errors。

增加 review runner smoke coverage，覆盖包含空格的 config 路径，以及基于 config 文件目录解析的相对 prompt manifest。

增加 review runner validator smoke coverage，覆盖包含空格的 config 路径，以及基于 config 文件目录解析的相对 prompt manifest。

增加 review runner smoke coverage，覆盖包含空格的 context file 路径，以及不可读取 context file 的结构化 JSON 错误。

调整 review runner 行为：command provider stdout/stderr 写入 provider output 和 attempt summaries 前，会对常见 secret-like 值做 redaction。

增加 review runner Markdown smoke coverage，覆盖已 redacted 的 provider failure summaries。

增加 review runner raw-output smoke coverage，覆盖不满足 structured output contract 的 command provider stdout redaction。

增加 review runner provider failure summaries，使 timeout、retry 和 fallback 降级需要确认。

在计算 AI finding quality 字段前，按 reviewer-comparison contract 校验 GitHub metrics adjudication overlays。

增加 Validate workflow 的本地校验护栏，覆盖权限、credential persistence、Python setup 和完整 SHA action pinning。

为 GitHub metrics collection 增加 reviewer adjudication overlay，使 AI finding quality 字段可从 reviewer-comparison 记录推导，而不是固定为零。

加强 CI 和仓库校验，增加明确的 Python 3.10/3.11/3.12 覆盖、runner smoke checks、旧仓库 slug 检测和 secret-like value 扫描。

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
