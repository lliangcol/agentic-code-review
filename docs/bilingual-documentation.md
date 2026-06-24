# Documentation Language Policy

## Rule

Public Markdown documentation in this repository is split by language.

English files keep the original `*.md` path. Simplified Chinese files use a sibling `*.zh-CN.md` path.

Do not mix paired `EN:` and `ZH:` content in the same Markdown file.

## Exceptions

Legal license text remains the official upstream English text. Chinese explanations may summarize the license but must not replace it.

Machine-readable files such as YAML, JSON, and GitHub workflow files may stay English-only when translated text would reduce reliability.

Source-reference and implementation-analysis documents are public Markdown and should keep English plus `.zh-CN.md` companion files.

Maintenance documents such as `docs/codebase-graph.md` and `docs/source-refresh-checklist.md` also require Simplified Chinese companions.
