# Codebase Graph Maintenance

This repository is small enough to review with direct file reads, but project instructions prefer code graph tools when an index exists.

## When To Build

Build or refresh a code graph when:

- New runtime scripts, validators, or test suites are added.
- Review questions depend on relationships between scripts, assets, references, and CI.
- A maintainer wants graph-backed discovery instead of file search.

## Expected Project Identity

Use the repository root as the project boundary:

```text
<repository-root>/agentic-code-review
```

If `codebase-memory-mcp` does not list the repository root, state that graph discovery is unavailable and fall back to Git, `rg`, and direct file reads.

## Refresh Checklist

- Confirm the working tree is clean or record the intended dirty scope.
- Run the repository validator first: `pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/check-skill.ps1`.
- Index source files, docs, tests, scripts, and Skill assets.
- Exclude `.git`, Python caches, local logs, and generated package output.
- After indexing, verify that the project appears in MCP project listing before relying on graph search.
