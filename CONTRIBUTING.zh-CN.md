# 贡献指南

## 范围

贡献应聚焦于改进 `agentic-code-review` Skill、引用资料、接入模板或校验脚本。

保持 Skill 的通用性。不要硬编码私有仓库规则、公司名称、凭据或本机路径。

## 文档风格

面向公众的 Markdown 文档必须拆分为独立的英文文件和简体中文文件。

英文内容保留在原始 `*.md` 路径，简体中文内容放在同目录的 `*.zh-CN.md` 文件。

不要在同一个 Markdown 文件中使用成对的 `EN:` 和 `ZH:` 段落。

## Skill 设计规则

保持 `SKILL.md` 简短、流程化。详细清单放入 `references/`。

保持集成为可选项。`review-fix-loop` 必须保持为软依赖。

默认行为必须保持只评审；只有用户明确要求时，才执行修复、提交、推送、发布或外部操作。

修改 Skill 行为时，应在同一变更中更新相关引用资料、`README.md`、接入模板和 `scripts/check-skill.ps1`。

新增公开引用资料必须保持简洁，包含 `.zh-CN.md` 伴随文件，并且只有在 Codex 或 Claude Code 需要读取路由信息时，才从 `SKILL.md` 链接。

不要把文章正文、benchmark 表格或本地下载 artifact 复制进仓库。应沉淀长期有效的评审原则。

## 校验

提交 pull request 前运行：

```powershell
.\scripts\check-skill.ps1
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$env:PYTHONUTF8 = "1"
python (Join-Path $codexHome "skills/.system/skill-creator/scripts/quick_validate.py") .\skills\agentic-code-review
```

在 Linux 或 macOS 上，对仓库校验脚本使用 `pwsh`：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$env:PYTHONUTF8 = "1"
python (Join-Path $codexHome "skills/.system/skill-creator/scripts/quick_validate.py") ./skills/agentic-code-review
```

如果环境没有 Codex Skill 官方校验器，请运行 `.\scripts\check-skill.ps1`，并说明 Codex 专属校验器不可用。对于 Claude Code 变更，也应在可行时安装到测试仓库 `.claude/skills` 目标目录或已配置的全局 Claude skills 目录做 smoke check。
