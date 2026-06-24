# 文档语言策略

## 规则

本仓库面向公众的 Markdown 文档按语言拆分。

英文文件保留原始 `*.md` 路径。简体中文文件使用同目录的 `*.zh-CN.md` 路径。

不要在同一个 Markdown 文件中混用成对的 `EN:` 和 `ZH:` 内容。

## 例外

法律许可证文本保留官方英文原文。中文说明可以概述许可证，但不能替代正式文本。

YAML、JSON 和 GitHub workflow 等机器可读文件可以保持仅英文，以避免翻译文本降低可靠性。

来源参考和实现分析文档属于公开 Markdown，应保持英文文件和 `.zh-CN.md` companion 文件。

`docs/codebase-graph.md` 和 `docs/source-refresh-checklist.md` 等维护文档也必须保留简体中文 companion。
