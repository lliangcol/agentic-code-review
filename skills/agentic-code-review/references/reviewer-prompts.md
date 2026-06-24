# Reviewer Prompts

## Use

Use these prompts for independent review passes. Run each pass separately and compare only after all passes finish.

Replace bracketed placeholders with the target repository, diff, or command output. Do not paste one pass's findings into another pass unless the task is explicitly verification.

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
