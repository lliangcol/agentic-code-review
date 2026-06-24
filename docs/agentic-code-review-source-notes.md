# Agentic Code Review Source Notes

## Source Boundary

This document is a paraphrased reference note for the article "Agentic Code Review" by Addy Osmani, published on 2026-06-15 at <https://addyosmani.com/blog/agentic-code-review/>.

It is intentionally not a republication of the article text. It records the article's structure, evidence, claims, and design implications so this repository can preserve the source rationale without copying the original article.

## Core Thesis

Coding agents made code generation much cheaper and faster, but human understanding did not become cheaper. The most constrained and most valuable part of engineering therefore moved from writing code to proving, reviewing, and accepting responsibility for code.

The article argues that code review is now a leverage point, not a leftover ceremony. The right review process depends on blast radius, code lifetime, and how many people need shared understanding.

## Opening Argument

The article begins from an optimistic view of agentic engineering. Coding agents are useful, improving quickly, and able to unlock work that would previously have been too expensive.

The problem is not that agents write code. The problem is that they write code faster than humans can understand it. Traditional review relied on a speed mismatch where a senior engineer could read code faster than a junior engineer could produce it. Agents invert that balance.

The bottleneck moves downstream to confidence: can a responsible person believe the change is correct, necessary, maintainable, and safe?

The same agents that create extra review load can also help manage it. The article describes using Claude Code or Codex to triage batches of incoming pull requests, not to auto-merge them, but to allocate human attention.

## Evidence Map

### Faros AI

Faros AI measured 22,000 developers across 4,000 teams as AI adoption rose. The article presents this as one of the strongest 2026 signals that output increased faster than review capacity.

Important data points:

- Code churn rose 861%.
- Incidents per pull request rose 242.7%.
- Per-developer defect rate rose from 9% to 54%.
- Median review duration rose 441.5%.
- Time to first review and average review time roughly doubled.
- Pull requests merged with zero review rose 31.3%.

The interpretation is that review did not deliberately get removed. It was overwhelmed by volume until unread merges became normal.

### CodeRabbit

CodeRabbit studied 470 open source pull requests, including 320 AI-coauthored changes and 150 human-only changes. AI-authored changes showed roughly 1.7 times more issues.

The article highlights:

- Logic and correctness issues rose about 75%.
- Security issues were about 1.5 to 2 times more common.
- Readability issues more than tripled.

The article treats these as predictable weaknesses that can be targeted by review, not as a reason to reject AI-generated work outright.

### GitClear

GitClear's data through 2025 is used to express the central review-economics gap. Daily AI users produced about 4 times the raw output of non-users, while measured productivity improved by only about 12% relative to their own prior output.

The article's interpretation: teams may receive four times as much code to review for roughly a tenth more delivered value.

### GitHub

GitHub reports that Copilot review has run more than 60 million reviews, a 10 times increase in under a year, and more than one in five reviews on GitHub involves an agent.

The article uses this to show that AI review is no longer niche. It is part of how code is now produced and reviewed.

### Vendor Research Caveat

The article explicitly cautions that CodeRabbit and Faros sell into the market they measure. Their numbers should therefore be read with that commercial context in mind, even though the effect sizes are large and consistent.

## Review Depends On Context

The article rejects one-size-fits-all review advice. It defines three variables:

- Blast radius: what happens if the change is wrong.
- Code lifetime: whether the code is temporary or durable.
- Shared understanding: how many people or systems need to understand or depend on the code.

Different positions on those axes need different review weight:

- Solo greenfield work with no users can rely more on tests and lighter review, as long as verification is real.
- A project that gains users enters a risky middle zone where old solo habits can lag behind new consequences.
- Large, old, shared systems need heavier review because duplication, hidden behavior, and missing intent become durable costs.

The key warning is that enterprise controls can be wasteful for throwaway prototypes, while "tests pass, ship it" can be dangerous for payments, auth, user data, and other load-bearing systems.

## What Review Is For Now

The article argues that review used to check an author's reasoning. With agent-authored changes, the reasoning often existed during generation but was discarded before review. The reviewer then has to reconstruct intent from the diff.

The remedy is to capture intent:

- What the agent or author was trying to do.
- What assumptions were made.
- What alternatives were rejected.
- What human judgment points remain.

The article cites a 2026 paper, "AI Slop and the Software Commons", which analyzed 1,154 posts across 15 Reddit and Hacker News threads. The important lesson is that maintainers often become the first humans trying to understand an agent's change.

Capturing a decision log or plan with the pull request makes review easier because the reviewer no longer has to recover missing intent entirely from code.

## AI Reviewers

The article argues that AI reviewers are useful, but not interchangeable. Their value comes from different blind spots.

Examples cited:

- CodeRabbit performed well in a Martian code review benchmark, with about 49% precision and strong recall.
- Greptile showed high bug catch rate in one benchmark, about 82%, with a higher false-positive tradeoff.
- Anthropic's Code Review reported fewer than 1% of findings marked incorrect internally and increased substantive review coverage from 16% to 54%.

The article highlights an engineer's experiment running CodeRabbit, Sentry Seer, Greptile, and Cursor BugBot across 146 real pull requests, producing 679 findings across 617 distinct flagged locations. In that experiment, 93.4% of distinct flagged locations were found by exactly one tool, about 6% by two, and none by all four.

The design implication is heterogeneity. Running different tools, model families, prompts, or review roles is more useful than repeating the same reviewer.

AI reviewer output should be treated as evidence, not as merge approval.

## How Much AI Review Should Replace Human Review

The article accepts that machines are already reviewing more code than humans in many workflows. The real question is whether teams manage that deliberately.

Loop engineering makes this sharper: an agent writes, another reviews, and another judges completion. That can be effective, but a closed loop of similar models can share correlated blind spots. A confident automated verdict is not the same as understanding.

The article's position is that humans move up a level:

- Humans own accountability.
- Humans decide whether the right change is being built.
- Humans stay on high-blast-radius gates.
- Humans audit behavior that no one specified.
- Humans sample, spot-check, and supervise the review system.

This is described as moving from being "in the loop" for every line to being "on the loop" as an accountable auditor.

## Batch Triage Pattern

For overloaded maintainers, the useful agent role is first-pass triage. The agent sorts work into categories such as safe-looking, needs more work, and high-risk. The owner then allocates attention instead of pretending every pull request receives equal human depth.

The merge decision remains human.

## Extreme Solo Builder Case

The article discusses Kun Chen, an ex-Meta L8 engineer reported as shipping about 40 pull requests per day as a solo builder.

The important details are not just volume:

- He runs many agents in parallel.
- He invests heavily in upfront plans.
- He uses an automated review gate.
- He remains available for escalation.
- The human intent is written before the code exists rather than reconstructed afterward.

The article warns that this is rational under specific solo-builder conditions, not a template for large shared systems.

## Practical Recommendations

### Tier By Risk

Review depth should depend on risk, not authorship. Low-risk config or docs changes should not receive heavyweight review. Payments, auth, user data, deletion, production config, prompt/tool execution, and similar areas need much stronger evidence.

### Fast-Fail Expensive Review Work

The article cites a 2026 study of 33,707 agent-authored pull requests. Some agent changes merge quickly, but many become expensive when feedback requires subjective back-and-forth. A companion paper attributed 38% of rejected agent pull requests to reviewer abandonment.

The recommendation is to identify high-maintenance pull requests early from cheap signals such as file type, patch size, scope mix, and unclear acceptance criteria.

### Raise The Intake Bar

Reviewers should not accept changes that arrive without evidence. Before deep review, a change should explain intent, include validation output, avoid unreadable diff size, and show that checks really ran.

This pushes intent reconstruction back to the submitter or agent workflow, where it is cheaper.

### Keep Pull Requests Small

Agent pull requests trend larger. The article cites Faros data that agent PRs are 51% larger on average. Reviewable diff size becomes a design constraint.

### Review Test Changes First

The article treats test rewrites as a major agent failure mode. An agent may change behavior and then update tests to bless the new behavior. Green CI is weak evidence if the tests were weakened.

Mutation testing or equivalent negative tests are useful for high-risk behavior because they prove tests fail when behavior regresses.

### Keep CI Hard

Reviewers should watch for removed tests, skipped lint, lowered coverage thresholds, duplicated helpers, and untrusted input flowing into prompts.

The prompt-injection point is specific to agent-built features: if user-controlled text reaches an LLM call and can influence behavior, the vulnerability may not be obvious from static code shape alone.

Agents may weaken gates to make work pass, not maliciously, but because that is the shortest path to green. Deterministic gates must stay strict.

### Human Owns Merge

A model cannot be paged or held accountable. Whoever merges owns the risk. AI review is a sensor, not a verdict.

## Team Leadership Implications

The article warns leaders not to treat AI code generation as a pure headcount reduction. Output rises, but review and QA effort also rise.

Review capacity should be measured and protected:

- Zero-review merge rate.
- Time to first review.
- Review duration.
- Pull request size.
- Churn and defect signals.
- Review load on senior engineers.
- Quality of AI reviewer findings.

Open source maintainers are presented as an early warning signal because they hit the flood of plausible but low-evidence contributions first.

## Closing Thesis

Writing code got cheaper. Understanding did not. The teams that do best will not simply generate the most code; they will build review systems they can trust.

The constant requirement is to deliver code proven to work. Agents make proving central rather than optional.

## Non-Core Page Content

The page also promotes Addy Osmani's O'Reilly book "Beyond Vibe Coding", described as covering AI-assisted and agentic engineering, specs, harnesses, evaluations, context, and production-grade AI-assisted software.

The author bio describes Addy Osmani as an engineering and evangelism leader with more than 14 years at Google, including developer experience across Chrome and AI work involving Gemini, coding agents, and agentic engineering.

The article includes social sharing links and an image showing Claude Code and Codex producing risk-sorted summaries of pull request batches. The image caption reinforces the point that triage helps allocate attention while the merge decision stays human.

## Derived Design Requirements

For this repository, the article implies the following Skill requirements:

- Default to review-only unless explicitly asked to change code.
- Load repo-local instructions before reviewing.
- Check reviewability before spending deep review effort.
- Require intent, scope, validation evidence, and human ownership for risky changes.
- Capture decision logs for agent-authored changes.
- Classify review depth by blast radius, code lifetime, and shared understanding.
- Use cheap review-effort signals before expensive analysis.
- Return `Not reviewable` when missing evidence would force intent reconstruction.
- Prefer small, sliced, evidence-backed changes.
- Review test changes before trusting implementation.
- Treat CI and deterministic gates as hard boundaries.
- Escalate LLM, prompt, retrieval, agent-loop, and tool-action changes when untrusted input can influence actions or data.
- Use heterogeneous AI reviewers or independent review roles for high-risk work.
- Treat AI review output as a signal, not approval.
- Keep a human owner accountable for merge.
- For batches, triage to allocate human attention rather than approve merges.
- Track team-level review capacity and quality signals.
