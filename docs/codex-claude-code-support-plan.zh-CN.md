# Codex 与 Claude Code 支持修改方案

状态：已实现。本文档记录 dual-runtime support 变更使用的方案；背景部分中的“当前仓库”表述描述的是驱动本次实现的变更前状态。

## 1. 背景与问题陈述

本次变更前，仓库主要把 `agentic-code-review` 包装为 Codex Skill。可复用的 review 工作流大体不依赖单一 agent 宿主，但公开描述、安装脚本默认值、支持模板和校验 gate 仍把 Codex 描述为唯一受支持的运行时。

变更前仓库证据：

- `skills/agentic-code-review/SKILL.md` 已经读取 `AGENTS.md` 和 `CLAUDE.md`，因此核心 review 工作流并不只依赖 Codex。
- `README.md`、`SUPPORT.md`、issue 模板和 `scripts/install-local.ps1` 仍描述 Codex-only 安装和支持。
- `skills/agentic-code-review/agents/openai.yaml` 是 OpenAI/Codex 专属集成 artifact，没有 Claude Code 伴随 artifact。
- 根目录 `.agents/` 和 `.codex/` 当前为空且未被 Git 跟踪，因此不提供真实运行时支持。

实现时需要复核的外部运行时证据：

- Claude Code skills 使用 skill 目录中的 `SKILL.md`，并可通过 `/skill-name` 直接调用。
- Claude Code 会发现 `~/.claude/skills/`、项目 `.claude/skills/`，以及 added directories 下的 `.claude/skills/`。
- Claude Code 会读取 `CLAUDE.md` 作为项目、用户或组织级持久指令。

来源：

- [Claude Code skills documentation](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Claude Code `.claude` directory documentation](https://code.claude.com/docs/en/claude-directory)
- [Claude Code memory documentation](https://docs.anthropic.com/en/docs/claude-code/memory)

要解决的问题不是 review 模型本身。问题是实现和文档暗示只支持 Codex，而项目预期同时运行在 Codex 和 Claude Code 中。

## 2. 目标与非目标

目标：

- 明确、准确、可测试地支持 Codex 和 Claude Code。
- 保留现有 Codex Skill package 和 Codex validator 路径。
- 使用同一份 canonical Skill 内容，增加文档化的 Claude Code 安装路径。
- 默认保持只评审；只有用户明确要求时才执行修复、提交、推送、发布或外部动作。
- 保持通过 `AGENTS.md` 和 `CLAUDE.md` 的仓库本地接入方式。
- 确保最终文档在双语中保留 `Not reviewable`、`Needs confirmation`、风险分层、validation、human owner、decision log、slice map、CI gate、LLM trust boundary 和 heterogeneous reviewers 等核心概念。

非目标：

- 不重写 review 方法论。
- 不引入托管 bot、模型服务、MCP server 或外部自动化。
- 不把 `review-fix-loop` 改为强依赖。
- 不移除 `agents/openai.yaml`，也不削弱 Codex 行为。
- 不把本文档作为 dual-runtime support 之外其他实现变更的授权依据。

## 3. 约束与假设

约束：

- 公开 Markdown 文件需要简体中文伴随文件，并保持结构匹配。
- `scripts/check-skill.ps1` 继续作为仓库级 hygiene gate。
- Codex Skill validator 是 Codex 专属可选校验，因为不是所有环境都有 Codex system skill validator。
- Claude Code 专属校验不应依赖私有本地路径或账号状态。
- generated cache、bytecode、log 和 local-only artifact 不能进入安装包。

假设：

- canonical Skill 源目录保持为 `skills/agentic-code-review/`。
- 当安装到 Claude Code skill 目录后，Claude Code 可以消费同一份 `SKILL.md`、`references/`、`assets/` 和 `scripts/` 目录形态。
- Codex 可以继续消费 `~/.codex/skills/` 下的同一份目录。
- runtime-specific metadata 应该以追加方式存在，而不是改变通用 workflow 语义。

## 4. 已考虑替代方案

替代方案 A：保持 Codex-only package，只在文档中提到 Claude Code。

- 优点：改动最小。
- 缺点：安装和 validation 仍没有支持；用户仍可能误解运行时范围。
- 拒绝原因：不能让 Claude Code 支持变得可测试。

替代方案 B：拆分独立的 Codex 和 Claude Code skill 目录。

- 优点：运行时边界清晰。
- 缺点：会复制 review 规则，导致 `SKILL.md`、references、scripts 和 assets 漂移。
- 拒绝原因：review 工作流应保持单一来源。

替代方案 C：保持 `skills/agentic-code-review/` 为 canonical，增加 runtime-specific 安装和文档表面。

- 优点：保留单一事实源，同时显式支持两个运行时。
- 缺点：需要更新安装脚本、文档和 validation。
- 选择原因：能修复支持缺口，同时避免复制 review 工作流。

## 5. 最终方案与理由

把 `skills/agentic-code-review/` 作为 Codex 和 Claude Code 共用的 canonical Agent Skill package。

保留 `skills/agentic-code-review/agents/openai.yaml` 作为 Codex 专属集成。通过安装和文档增加 Claude Code 支持，而不是 fork Skill body。安装脚本应支持 Codex、Claude Code 或同时安装到两者。文档应把项目称为跨运行时 Agent Skill package，并说明当前包含 Codex-specific metadata 和 Claude Code-compatible installation。

该方案接受少量 runtime-specific installer 逻辑，以避免复制 review workflow。human owner 责任、CI gate 完整性、LLM trust boundary review、heterogeneous reviewers、decision log、slice map、validation evidence 和 `Not reviewable` 行为保持不变。

## 6. 分步骤修改计划

阶段 1：术语和范围对齐。

- 将 `README.md` 和 `README.zh-CN.md` 概览从 Codex-only wording 改为 Codex 与 Claude Code-compatible wording。
- 只在明确指代 Codex package 或 Codex validator 时保留 “Codex Skill”。
- 增加简短 runtime support matrix，覆盖 Codex、Claude Code、共享 Skill content 和 runtime-specific metadata。
- 更新 `docs/agentic-code-review-implementation-analysis.md` 和 `.zh-CN.md`，不再把 package 描述为 Codex-only。
- 更新 `SUPPORT.md`、`SUPPORT.zh-CN.md` 和 bug report templates，要求填写 runtime/surface，而不是只填写 Codex surface。
- 发布前更新 `CHANGELOG.md` 和 `CHANGELOG.zh-CN.md`，记录 dual-runtime support change。

阶段 2：Claude Code 接入 artifact。

- 增加 Claude Code 项目指令片段，例如 `skills/agentic-code-review/assets/CLAUDE.snippet.md` 和 `CLAUDE.snippet.zh-CN.md`。
- 与 `AGENTS.snippet.md` 保持语义一致，但面向 `CLAUDE.md` project memory 表述。
- 包含明确边界：默认只评审、没有用户批准不执行外部动作、保留 `Needs confirmation`、不要把 AI review 当作 approval。
- 将两个 snippet 文件加入仓库 validation，缺少 localized companion 或 required artifact stale 时快速失败。

阶段 3：安装脚本支持。

- 扩展 `scripts/install-local.ps1`，增加 runtime 选择，例如 `-Runtime Codex`、`-Runtime ClaudeCode` 或 `-Runtime Both`。
- 除非项目明确选择 breaking default change，否则保留当前默认行为。
- 保持当前 Codex 默认目标为 `$CODEX_HOME/skills` 或 `~/.codex/skills`。
- 增加 Claude Code 默认目标：设置 `CLAUDE_CONFIG_DIR` 时使用 `$CLAUDE_CONFIG_DIR/skills`，否则使用 `~/.claude/skills`，并支持显式 `-ClaudeDestination` override。
- 将同一份 canonical Skill package 安装到所选 runtime 目标。
- 对两个目标都保留 target-overlap protection。
- 继续排除 `__pycache__`、`.pytest_cache`、`.mypy_cache`、`.ruff_cache`、`.pyc`、`.pyo` 和 `.log` artifact。
- 输出清晰安装日志，列出每个 runtime 和 destination。

阶段 4：文档更新。

- 在 README 中增加 Codex only、Claude Code only 和 both 的安装示例。
- 说明只有当用户需要 repository-scoped skills 时，才使用 project-local Claude Code `.claude/skills/agentic-code-review/`；否则使用 `~/.claude/skills/`。
- 保留 `AGENTS.md` 接入说明，并增加并行的 `CLAUDE.md` 接入说明。
- 更新 `CONTRIBUTING.md` 和 `.zh-CN.md`，使新增公开引用资料在 Codex 或 Claude Code 需要 routing 信息时被链接，而不是只提 Codex。
- 将 PR template 的 validation checklist 从 “Codex Skill validator” 改为可用时运行 runtime-specific validation。
- 更新 `review-fix-loop.gates.example.json`，把 Codex validator 命名为 optional 且 Codex-specific。

阶段 5：validation 和 tests。

- 增加 `-Runtime Codex`、`-Runtime ClaudeCode` 和 `-Runtime Both` 的 installer tests。
- 增加测试，确认 Claude Code 安装包含 `SKILL.md`、`references/`、`assets/` 和 `scripts/`。
- 增加测试，确认 install exclusions 和 target-overlap protection 也适用于 Claude Code destination。
- 扩展 `scripts/check-skill.ps1` required files，加入 Claude Code snippets 和更新后的双语 docs。
- 扩展 `scripts/check-skill.ps1` marker checks，确保后续变更不能静默移除 Claude Code support claim 或 Codex/Claude Code runtime split。
- 保留当前 Codex validator command，并说明它是 optional。
- 增加轻量 Claude Code manual smoke checklist：安装到测试仓库 `.claude/skills` path 或已配置的全局 Claude skills 目录，确认 folder shape，并记录预期 `/agentic-code-review` invocation。

阶段 6：最终 review 和 release readiness。

- 运行仓库 validation：`pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1`。
- 运行脚本测试：`python -m pytest tests/test_skill_scripts.py`。
- 环境可用时运行 Codex Skill validator。
- 运行最终 `rg` audit，检查 stale Codex-only wording，只允许有意保留的 Codex-specific references。
- 确认所有英文公开 Markdown 变更都有 `.zh-CN.md` companion，且 heading counts 匹配。

## 7. 风险与缓解

风险：Claude Code runtime requirements 发生漂移。

- 缓解：实现基于当前官方 Claude Code docs，并把 runtime-specific 假设隔离在 README 和 installer 注释中。

风险：增加 Claude Code 支持时造成 Codex 行为回归。

- 缓解：保留现有默认安装路径，保留 `agents/openai.yaml`，保留 Codex validator 作为 optional gate。

风险：common Skill 被 host-specific wording 污染。

- 缓解：把 common behavior 保持在 `SKILL.md`；将 runtime-specific installation 和 support language 放在 README、snippets 和 installer help text。

风险：双语文档漂移。

- 缓解：英文和简体中文在同一变更中更新，并依赖 `scripts/check-skill.ps1` 的 heading 和 marker checks。

风险：用户把 AI review 解读为 merge approval。

- 缓解：在所有 runtime docs 中保留只评审默认值、human owner 语言、CI gate 完整性，以及 `Not reviewable` / `Needs confirmation` verdict boundary。

## 8. 测试与校验策略

必需自动化检查：

- `pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1`
- `python -m pytest tests/test_skill_scripts.py`

建议 runtime-specific checks：

- Codex：环境可用时运行 Codex Skill validator。
- Claude Code：安装到测试仓库 `.claude/skills` destination 或已配置的全局 Claude skills 目录，并确认预期 folder shape。
- 文档：运行 `rg -n "Codex-only|for Codex|Codex surface|Codex environment|Codex skills directory"`，将每个剩余命中分类为 intentional 或 stale。

验收标准：

- 文档说明 workflow 支持 Codex 和 Claude Code。
- installer 可以安装到 Codex、Claude Code 或两者。
- Claude Code 支持不需要手工复制文件。
- Codex-specific validator 和 metadata 仍可用。
- `AGENTS.md` 和 `CLAUDE.md` 接入路径都被文档化。
- `Not reviewable`、validation、风险分层、human owner、decision log、slice map、CI gate、LLM trust boundary 或 heterogeneous reviewers 指导没有丢失。

## 9. 回滚策略

回滚条件：

- Codex installation 失败。
- 仓库 validation 因双语文档或 required package files 不一致而失败。
- Claude Code 安装假设被当前官方 docs 或本地 smoke checks 否定。

回滚步骤：

- 如果安装行为回归，先 revert installer changes。
- 只 revert 宣称不受支持 Claude Code 行为的文档 wording。
- 保留仍适用于 Codex 的 neutral wording improvements。
- 回滚后重新运行 `scripts/check-skill.ps1` 和 `pytest`。

回滚限制：

- 只回滚 docs 可能导致 installer behavior 不匹配；回滚必须保持 docs、tests 和 installer behavior 对齐。
- 如果 Claude Code docs 变化，正确动作可能是 follow-up compatibility patch，而不是回滚所有双运行时表述。

## 10. Review-Fix-Re-Review 记录

第一轮 review 发现：初稿把 Claude Code 支持做成 documentation-only change，没有让安装变得可测试。

- 已修复：加入 installer runtime selection、Claude Code destination handling 和 installer tests。

第二轮 review 发现：初稿的 installer plan 可能通过隐式改变默认路径削弱 Codex 兼容性。

- 已修复：除非明确选择 breaking default change，否则保留当前 Codex default。

第三轮 review 发现：方案没有区分 repository validation 和 runtime-specific validators。

- 已修复：将 `scripts/check-skill.ps1` 保持为必需仓库 gate，将 Codex validator 保持为 optional，并增加 Claude Code smoke checklist。

第四轮 review 发现：方案可能允许 stale Codex-only wording 未被发现。

- 已修复：加入最终 `rg` audit，并要求将有意保留的 Codex-specific references 和 stale wording 显式分类。

第五轮 review 发现：方案漏掉 release bookkeeping，也没有要求 validation 保持新的 runtime-support promise。

- 已修复：加入 `CHANGELOG` 更新，并为 Codex/Claude Code runtime split 增加 `check-skill.ps1` marker requirement。

第六轮 review 发现：安装脚本默认目标没有遵循 Claude Code 用于全局配置目录的 `CLAUDE_CONFIG_DIR` override。

- 已修复：为 Claude Code 默认目标增加 `CLAUDE_CONFIG_DIR` 支持，补充测试，并更新 README guidance。

最终 re-review 结论：已作为 dual-runtime support 变更实现并完成校验。后续变更应保持 installer 行为、文档和 validation gates 对齐。
