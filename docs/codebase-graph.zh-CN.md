# Codebase Graph 维护

本仓库足够小，可以直接读取文件完成 review，但项目指令要求当索引存在时优先使用代码图工具。

## 何时构建

在以下场景构建或刷新代码图：

- 新增 runtime scripts、validators 或 test suites。
- Review 问题依赖 scripts、assets、references 和 CI 之间的关系。
- 维护者希望使用 graph-backed discovery，而不是文件搜索。

## 预期项目身份

使用仓库根目录作为项目边界：

```text
<repository-root>/agentic-code-review
```

如果 `codebase-memory-mcp` 没有列出该仓库根目录，说明 graph discovery 不可用，并回退到 Git、`rg` 和直接文件读取。

## 刷新清单

- 确认工作树干净，或记录预期 dirty scope。
- 先运行仓库校验：`pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1`。
- 索引 source files、docs、tests、scripts 和 Skill assets。
- 排除 `.git`、Python caches、本地 logs 和生成的 package output。
- 索引完成后，先确认该项目出现在 MCP project listing 中，再依赖 graph search。
