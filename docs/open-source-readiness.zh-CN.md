# 开源就绪核对清单

在第一次公开推送到 GitHub 前，以及之后每次公开发布前，使用本清单。

## 本地门禁

- 工作区状态是有意的；没有生成缓存、本地 runtime 状态、私有笔记或下载的文章原文产物被暂存。
- `scripts/check-skill.ps1` 在当前工作区通过。
- `python -m unittest discover -s tests` 通过。
- `python skills/agentic-code-review/scripts/run_review_passes.py --dry-run --no-diff --format json` 通过，且不访问模型 provider。
- 当 Codex validator 可用时，运行 Codex Skill 校验。
- 本地安全扫描没有在已跟踪文件中发现 secrets、私钥、token 或私有工作站路径。
- 公开文件不包含来自旧项目名的旧仓库链接。
- 已安装 Skill 的 smoke check 只复制受支持 runtime 所需的 `SKILL.md`、`references/`、`assets/`、`scripts/` 和 runtime 元数据。

## 公开仓库文件

- `LICENSE`、`README.md`、`CONTRIBUTING.md`、`SECURITY.md`、`SUPPORT.md`、`CODE_OF_CONDUCT.md` 和 `CHANGELOG.md` 均存在。
- 除正式 license 文本外，公开 Markdown 文件都有使用 `.zh-CN.md` 的简体中文 companion。
- `.github/` 下存在 GitHub 元数据：`CODEOWNERS`、Dependabot 配置、issue templates、pull request template 和 validation workflow。
- README 中的安装和校验命令与本仓库真实脚本一致。
- 来源笔记保持转述；本仓库不得再分发复制的来源文章正文。

## GitHub 设置

- 在依赖 badges 或 issue links 前，先用预期 owner 和名称创建 GitHub 仓库。
- 将 `main` 设置为默认分支。
- 为 `main` 启用 branch protection，并要求 `Validate` workflow 通过后才能合并。
- 启用 private vulnerability reporting，或记录维护者的私密报告渠道。
- 在 GitHub UI 中确认 repository description、topics、license detection 和 README 渲染。
- 确认 Dependabot 能创建 GitHub Actions 更新 pull request。

## 发布边界

- 本地校验通过且维护者明确批准外部动作前，不要 tag、push、publish 或创建 GitHub release。
- 将外部发布证据与本地就绪状态分开。干净的本地门禁表示仓库已具备发布条件，不表示 GitHub 设置或远端检查已经通过。
