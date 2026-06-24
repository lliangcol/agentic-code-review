# 深度报告优化任务清单

英文版：[deep-research-optimization-backlog.md](deep-research-optimization-backlog.md)

实施状态日期：2026-06-24。

## 范围

本清单从本地深度报告中提取优化项、风险和技术债，并与当前工作树逐项核对。当前仓库仍然是 shared Skill 包，不是托管式 review 服务。凡是报告和当前代码都没有说明的细节，统一标记为 `unspecified`。

约束：

- 保持共享的 `skills/agentic-code-review` 包。
- 保持 review-only 默认行为和人类 merge owner。
- 保持 Codex 与 Claude Code 双运行时支持。
- 保持 Python 3.10+、PowerShell 和 CI 兼容。
- 除非后续任务记录更强理由，否则避免重依赖。
- 新增配置必须提供默认值和示例。

## 当前代码事实

- 仓库已经通过 `actions/setup-python` 明确覆盖 Python 3.10/3.11/3.12。
- `scripts/check-skill.ps1` 已经拦截旧仓库 slug、本地私有路径、生成类包内文件、非法 JSON、缺失双语 Markdown 伴随文件以及 secret-like 值。
- `skills/agentic-code-review/scripts/run_review_passes.py` 已经提供可选 `mock` 和 `command` providers、prompt manifest 加载、超时/重试/fallback、估算 token 与成本统计，以及和 `measure_diff.py` 的规则信号融合。
- `skills/agentic-code-review/assets/review-prompt-manifest.json` 已经包含版本化 prompt templates 和结构化 review 输出契约。
- `skills/agentic-code-review/scripts/collect_github_metrics.py` 已经接受 adjudication overlay，用于填充 `valid_ai_findings`、`false_positive_ai_findings` 和 `reviewer_overlap_count`。
- 当前代码没有 GitHub About 元数据的本地证据。该项从本地工作树看是 `unspecified`，如需处理必须在仓库外部验证或修改。

## 优先级定义

| 优先级 | 含义 |
| --- | --- |
| P0 | 不能回退，因为它保护安全、可安装性、review-only 行为或双运行时兼容性。 |
| P1 | 高价值正确性、可运营性或校验工作，直接关闭报告风险或保护当前新增 runner 行为。 |
| P2 | 有用的加固或可维护性工作，但即时影响范围较小。 |
| P3 | 文档、示例、打包润色或可选规模化工作。 |

## P0 任务

| ID | 事项 | 当前事实 | 状态 | 决策和原因 |
| --- | --- | --- | --- | --- |
| P0-01 | 保持 review-only 行为和人类 merge owner。 | `SKILL.md`、输出引用、README 和 runner mock 输出都避免声明 merge approval。 | 护栏项，后续每次变更都保持打开。 | 作为 P0 保留，因为这是 Skill 的核心安全边界。 |
| P0-02 | 保持 shared Skill 包和 Codex/Claude Code 兼容。 | `install-local.ps1`、README、`check-skill.ps1` 和测试覆盖 Codex 与 Claude Code 安装形态。 | 护栏项，后续每次变更都保持打开。 | 除非后续任务增加明确 packaging profiles，否则不拆分运行时内容。 |
| P0-03 | 保持默认校验离线且不需要 secrets。 | README 声明不需要 API key；默认 runner 配置使用 mock providers；检查脚本扫描 secret-like 值。 | 护栏项，后续每次变更都保持打开。 | 外部 providers 必须继续是 opt-in command providers，并从自己的环境读取 secrets。 |
| P0-04 | 保持项目在 Python 3.10+、PowerShell 和 CI 中可安装、可运行、可测试。 | CI 矩阵和本地校验已经覆盖 Python helpers、测试和 PowerShell install smoke checks。 | 护栏项，后续每次变更都保持打开。 | 任何新能力都必须包含不依赖外部服务的 smoke 路径。 |

## P1 任务

| ID | 事项 | 当前事实 | 状态 | 决策和原因 |
| --- | --- | --- | --- | --- |
| P1-01 | 校验 review runner 配置和 prompt manifest 形态。 | `validate_review_runner.py` 现在会检查 runner config、prompt manifest、providers、fallbacks、templates、passes 和 output contracts。 | 第 3 轮完成。 | 增加仅依赖标准库的轻量 validator，因为 runner 已经是主要 LLM 抽象面。 |
| P1-02 | 强制校验 command provider 的结构化 review 输出契约。 | runner 现在会在 fusion 前校验结构化输出必要字段和顶层字段类型。 | 第 2 轮完成。 | 非法 reviewer 输出应作为需要确认的证据，而不是干净通过。 |
| P1-03 | 加强 prompt template 版本策略。 | Templates 已经有 ID 和 version；变更策略与 schema 检查只部分显式。 | 未完成。 | 增加校验和文档，让 prompt 变更可审计、可回滚。 |
| P1-04 | 保持 multi-provider 行为最小但明确。 | `mock` 和 `command` providers 可以覆盖多种外部工具且不引入 SDK 依赖。原生 OpenAI/Anthropic SDK providers 是 `unspecified`。 | 作为设计决策保持打开。 | 暂不加 SDK providers，以降低依赖重量；把 command-provider contract 记录为受支持扩展点。 |
| P1-05 | 改善超时、重试、fallback 和失败可观测性。 | Runner report 现在包含 pass 级 `attempt_failures` 和 fusion 级 `provider_failures`；provider 降级会强制 `Needs confirmation`。Backoff 策略是 `unspecified`。 | 第 4 轮完成 reporting 和 fusion。 | 当前保留立即重试；先补更清晰的失败摘要，再决定是否加可配置 backoff。 |
| P1-06 | 保护规则检查与 LLM 融合语义。 | Fusion 现在会把结构化输出错误和 provider failures 作为 `Needs confirmation` 信号。 | 第 2 轮和第 4 轮完成。 | 增加测试，确保格式错误或字段不完整的 LLM 输出不能产生 `Ready`。 |
| P1-07 | 保持 metrics calibration 闭环。 | Adjudication overlays 已经可以填充 AI finding quality 字段，并会在导入前按 reviewer-comparison contract 校验。 | 第 5 轮完成。 | 计算团队 metrics 前先校验 overlay records，避免校准数据静默漂移。 |
| P1-08 | 维护 CI 与安全门禁完整性。 | 本地校验现在强制 Validate workflow 的 permission、credential、setup-python、matrix-version 和完整 SHA action pinning 护栏。CodeQL、coverage gate 和 PowerShell analyzer 仍是 `unspecified`。 | 第 6 轮部分完成。 | 优先低依赖检查；重型 analyzers 在项目接受额外 setup 成本前保持 `unspecified`。 |
| P1-09 | 记录外部 GitHub metadata 漂移处理。 | 本地文件已不暴露旧仓库 slug；GitHub About metadata 不在本地代码中。 | 外部任务未完成。 | 作为手动 release checklist 事项跟踪，因为它不能靠本地代码编辑完成。 |

## P2 任务

| ID | 事项 | 当前事实 | 状态 | 决策和原因 |
| --- | --- | --- | --- | --- |
| P2-01 | 重构 runner 模块边界。 | `run_review_passes.py` 在一个脚本内包含配置加载、provider 执行、prompt 渲染、成本估算、输出解析和 fusion。 | 未完成。 | 先加强校验，再拆成聚焦 helpers，并保持 CLI 行为不变。 |
| P2-02 | 改善 typing 和异常一致性。 | 脚本使用 type hints，runner 有自定义 `ConfigError`，但没有静态类型门禁。 | 未完成。 | 在依赖策略明确前不引入 mypy；先增加聚焦的运行时测试。 |
| P2-03 | 增加本地可观测性 artifacts。 | Runner report 包含 `run_id`、时间戳、attempts、耗时、token 估算、成本估算和 fusion status。Metrics/traces 导出后端是 `unspecified`。 | 未完成。 | 优先 JSON report 字段和可选 trace 文件，不引入重型 telemetry 依赖。 |
| P2-04 | 增加更大的集成和 E2E fixtures。 | 单元测试覆盖多个脚本和安装路径；没有外部 live-model E2E。 | 未完成。 | Live providers 不进入 CI；增加确定性的 command-provider E2E fixtures。 |
| P2-05 | 增加可选的可复现开发环境。 | 当前没有 devcontainer 或 Dockerfile。部署目标是 `unspecified`。 | 未完成。 | 只增加可选验证环境；不把 Skill 改造成服务容器。 |
| P2-06 | 增加性能和规模基线。 | `measure_diff.py`、metrics collection 和仓库校验都是线性本地脚本；没有 benchmark。 | 未完成。 | 功能门禁稳定后，再增加 opt-in benchmark 脚本或 workflow-dispatch 检查。 |
| P2-07 | 改善 release 和部署文档。 | README 覆盖本地安装与校验；release packaging 和版本化分发较轻量。 | 未完成。 | 除非后续产品方向改变，否则将部署视为 Skill 分发，而不是服务部署。 |
| P2-08 | 谨慎扩展安全自动化。 | 已有 secret-like scanning；未配置外部 secret scanning、CodeQL、Semgrep、Bandit 和 PSScriptAnalyzer。 | 未完成。 | 只引入不破坏跨平台安装或不会无理由增加重依赖成本的检查。 |

## P3 任务

| ID | 事项 | 当前事实 | 状态 | 决策和原因 |
| --- | --- | --- | --- | --- |
| P3-01 | 增加更多 command-provider 集成示例。 | README 提供通用 command provider 示例。具体 Codex/Claude/外部模型命令是 `unspecified`。 | 未完成。 | 在真实 provider 命令可验证前，保持示例通用。 |
| P3-02 | 增加更多 adoption 和 rollout checklists。 | 已有 adoption 文档，但组织级 rollout 节奏是 `unspecified`。 | 未完成。 | 保持通用建议；不虚构团队策略。 |
| P3-03 | 架构变化时更新图谱。 | `docs/codebase-graph.md` 已存在。 | 作为维护项打开。 | 只有模块边界实际变化时才更新图。 |
| P3-04 | 增加可选 coverage reporting。 | CI 跑测试，但不报告 coverage。Coverage threshold 是 `unspecified`。 | 未完成。 | 在项目决定哪些行为必须覆盖前，不增加阈值。 |
| P3-05 | 增加来源刷新提醒。 | 已有 source refresh checklist。自动化计划是 `unspecified`。 | 未完成。 | 除非出现来源过期问题，否则保持手动。 |

## 第 1 轮执行记录

当前问题：深度报告覆盖面很广，而且部分结论已经落后于当前仓库。若不先核对，会把已修复风险重复列为待修复，同时忽略新增 runner surface 带来的校验与契约风险。

拟议方案：新增本清单作为受版本控制的文档 artifact，记录 P0-P3 任务、当前代码证据、`unspecified` 标记和决策原因。

代码或配置改动：本切片不改运行时代码或配置；仅更新文档。

测试：新增文档后运行仓库校验和 Python 单元测试。

文档更新：本文件及英文伴随文件。

兼容性影响：无。本切片不改变 Skill 打包、review-only 默认行为、Codex/Claude Code 运行时支持、Python 要求、PowerShell 脚本或 CI。

验证步骤：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
python -m unittest discover -s tests
```

## 第 2 轮执行记录

当前问题：可选 review runner 会把 provider stdout 解析为 JSON，但没有在 fusion 前强制执行 `structured-review-v1` 契约。Provider 可能返回字段不完整的 JSON，却仍表现为 `ok` reviewer pass。

拟议方案：provider 执行后校验结构化输出的必要字段和顶层字段类型。Provider 进程状态与输出契约有效性分开记录；当存在输出契约错误时，fusion 返回 `Needs confirmation`。

代码或配置改动：更新 `run_review_passes.py`，增加结构化输出校验和 output-contract warnings；增加一个 incomplete command-provider response 的测试；不改变配置格式。

测试：运行聚焦的 review-runner 测试类、全量单元测试和仓库校验。

文档更新：在本 backlog 中标记 P1-02 完成，并记录本轮切片。

兼容性影响：只新增 report 字段。现有 configs、mock defaults、command-provider contract、安装路径和 review-only 行为保持不变。

验证步骤：

```powershell
python -m unittest tests.test_skill_scripts.ReviewRunnerTests
python -m unittest discover -s tests
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
```

## 第 3 轮执行记录

当前问题：runner config 和 prompt manifest assets 可能 JSON 合法，但仍包含非法 provider 引用、fallback 目标、template 引用或 output-contract metadata。默认 runner smoke check 只覆盖启用的 mock passes。

拟议方案：新增一个仅依赖标准库的 validator，在不访问模型 provider 的情况下校验 config、prompt manifest、provider definitions、fallback references、review passes、templates、run settings 和 output contracts。

代码或配置改动：新增 `validate_review_runner.py`；接入仓库校验、CI py_compile 和 CI JSON smoke；在 README 记录命令；增加默认配置通过和 missing fallback 失败测试。

测试：运行聚焦的 review-runner 测试、全量单元测试和仓库校验。

文档更新：在本 backlog 中标记 P1-01 完成，更新 README 和 changelog。

兼容性影响：只新增脚本和 CI 检查。现有 runner config shape、command-provider 行为、mock defaults、Skill 打包和 runtime 支持保持不变。

验证步骤：

```powershell
python -m unittest tests.test_skill_scripts.ReviewRunnerTests
python -m unittest discover -s tests
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
```

## 第 4 轮执行记录

当前问题：provider attempts 已包含失败细节，但用户必须逐条检查 attempts 才能看出 timeout、retry 或 fallback 降级。成功 fallback 也可能掩盖 primary provider 曾经失败。

拟议方案：新增 pass 级 `attempt_failures` 和 fusion 级 `provider_failures`，并让任何 provider attempt failure 都把融合 verdict 保持为 `Needs confirmation`。

代码或配置改动：更新 `run_review_passes.py` 的 report 和 fusion 输出；增加 mock fallback 与 successful command fallback 测试；更新 README、changelog 和本 backlog。

测试：运行聚焦的 review-runner 测试、全量单元测试和仓库校验。

文档更新：在本 backlog 中标记 P1-05 reporting 和 fusion 完成，更新 README 和 changelog。

兼容性影响：新增 report 字段，并在 fallback 前曾发生 provider attempt failure 时使用更保守的 fusion verdict。CLI、config shape、provider 执行、retry 次数和 fallback 机制保持不变。

验证步骤：

```powershell
python -m unittest tests.test_skill_scripts.ReviewRunnerTests
python -m unittest discover -s tests
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
```

## 第 5 轮执行记录

当前问题：GitHub metrics adjudication overlays 可以在只有局部类型检查的情况下用于计算 AI finding quality 字段，仍可能偏离 reviewer-comparison contract。

拟议方案：在 `collect_github_metrics.py` 导入 adjudication overlay records 前复用现有 reviewer-comparison validator。

代码或配置改动：更新 `collect_github_metrics.py`，校验抽取出的 overlay records；增加非法 reviewer counts 的失败路径测试；更新 README、changelog 和本 backlog。

测试：运行聚焦的 metrics collection 测试、全量单元测试和仓库校验。

文档更新：在本 backlog 中标记 P1-07 完成，README 澄清 overlay validation，并更新 changelog。

兼容性影响：合法 overlay 文件不变。非法 overlays 现在会更早失败，并给出清晰 validation error，而不是产出派生 metrics。

验证步骤：

```powershell
python -m unittest tests.test_skill_scripts.MetricsCollectionTests
python -m unittest discover -s tests
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
```

## 第 6 轮执行记录

当前问题：Validate workflow 已经使用低风险设置，但这些设置并未全部由本地仓库门禁强制保护。后续编辑可能静默削弱 permissions、action pinning 或 Python setup。

拟议方案：在本地 `check-skill.ps1` 中增加护栏，检查 `contents: read`、禁用 checkout credential persistence、显式 `actions/setup-python`、基于 matrix 的 Python version selection，以及每个 `uses:` action 都使用完整 commit SHA pin。

代码或配置改动：更新 `check-skill.ps1`；增加一个把 `actions/setup-python` 改成 tag 并期望校验失败的回归测试；更新 changelog 和本 backlog。

测试：运行聚焦的 repository workflow 测试、全量单元测试和仓库校验。

文档更新：在本 backlog 中标记 P1-08 的低依赖部分完成，并更新 changelog。

兼容性影响：本地校验更严格。只要 workflow 保持现有护栏，运行时行为、安装路径、runner 行为和 workflow 行为都不变。

验证步骤：

```powershell
python -m unittest tests.test_skill_scripts.RepositoryWorkflowTests
python -m unittest discover -s tests
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
```

## 决策日志

| 决策 | 原因 |
| --- | --- |
| 将第一轮切片定为 backlog 文档。 | 先让报告到代码的核对结果可审查，再改行为。 |
| 将外部 GitHub metadata 标记为本地 `unspecified`。 | 本地工作树不能证明或编辑 GitHub About metadata。 |
| 当前保持 command-based provider 支持。 | 这样能支持多 provider，同时不新增 SDK 依赖，也不把 secrets 写入配置。 |
| 下一步优先处理 runner 配置和输出校验。 | Runner 是最新的高价值 surface，校验缺口会影响 review verdict 的可信度。 |
