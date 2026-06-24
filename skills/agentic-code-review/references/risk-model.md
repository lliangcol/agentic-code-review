# Risk Model

## Core Axes

Classify by risk, not by whether a human or agent wrote the change.

Use three axes:

- Blast radius: what breaks if this is wrong?
- Code lifetime: is this throwaway, short-lived, or durable system code?
- Shared understanding: how many people or systems need to understand or depend on it?

## Risk Tiers

`L0` means documentation, comments, formatting, generated metadata, or other changes with no runtime behavior.

`L1` means localized low-risk behavior with easy rollback and low blast radius.

`L2` means normal product or API behavior where meaningful tests are expected.

`L3` means high blast radius or durable shared code, including auth, permissions, money movement, user data, deletion, queues, cache consistency, infrastructure, production config, and security boundaries.

Treat LLM, prompt, retrieval, agent-loop, or tool-execution changes as `L3` when untrusted input can influence actions, permissions, files, commands, secrets, money, or user data.

`L4` means architecture, cross-service protocol, core data model, irreversible migration, broad refactor, history rewrite, or merge-readiness work across many slices.

## Escalation Rule

Classify the whole review by the highest-risk changed slice. A small high-risk file in a large low-risk PR still raises the review tier.

Escalate when a change creates comprehension debt: large churn without a slice map, duplicated helpers, mixed concerns, durable shared abstractions, or behavior hidden behind generated code.

Escalate when tests are heavily rewritten, deleted, skipped, or changed to match implementation rather than product intent.
