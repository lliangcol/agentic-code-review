# Reviewer Prompts

## 使用

这些 prompts 用于独立 review passes。每个 pass 单独运行，所有 pass 完成后再比较。

用目标仓库、diff 或命令输出替换方括号占位符。除非任务明确是 verification，否则不要把一个 pass 的 findings 粘贴给另一个 pass。

## Correctness And Regression

Review `[target]` for confirmed correctness regressions. Focus on changed behavior, edge cases, existing contracts, data transformations, and caller expectations. Ignore style-only comments. Return only source-backed findings with file and line evidence, plus any validation that would confirm or falsify them.

## Test Integrity

Review `[target]` with tests first. Identify deleted, weakened, skipped, over-mocked, or implementation-mirroring tests. For each issue, explain the original behavior the test should protect and whether a negative or mutation-style test is needed.

## Security And Abuse

Review `[target]` for auth, permissions, data exposure, injection, secret handling, hostile input, prompt injection, and tool-action abuse. Treat untrusted text as attacker-controlled. Return only exploitable or plausibly reachable findings.

## Operations And Rollback

Review `[target]` for deployment risk, migrations, observability, rollback, retry behavior, queues, cache consistency, production config, and incident impact. Identify what must be validated before merge and what a human owner must accept.

## Architecture And Comprehension Debt

Review `[target]` for durable shared abstractions, duplicated helpers, hidden behavior, broad refactors, cross-module contracts, and maintainability risk. Prefer concrete future bug surfaces over style preferences.

## LLM Trust Boundary

Review `[target]` for LLM, prompt, retrieval, agent-loop, and tool-call trust boundaries. Identify where untrusted input can affect instructions, tool arguments, file paths, shell commands, network calls, messages, approvals, secrets, money, or user data.

## Comparison Prompt

Compare the independent review outputs. Group confirmed findings, duplicates, rejected findings, disagreements, and residual human-judgment risks. Do not treat reviewer agreement as merge approval.
