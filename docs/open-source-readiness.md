# Open Source Readiness Checklist

Use this checklist before the first public GitHub push and before any later public release.

## Local Gate

- Worktree status is intentional. No generated caches, local runtime state, private notes, or downloaded article artifacts are staged.
- `scripts/check-skill.ps1` passes on the current worktree.
- `python -m unittest discover -s tests` passes.
- `python skills/agentic-code-review/scripts/run_review_passes.py --dry-run --no-diff --format json` passes without contacting a model provider.
- Codex Skill validation runs when the Codex validator is available.
- A local security scan finds no secrets, private keys, tokens, or private workstation paths in tracked files.
- Public files contain no legacy repository links from the previous project name.
- The installed Skill smoke check copies only `SKILL.md`, `references/`, `assets/`, `scripts/`, and runtime metadata needed by supported runtimes.

## Public Repository Files

- `LICENSE`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md`, and `CHANGELOG.md` are present.
- Public Markdown files have Simplified Chinese companions using `.zh-CN.md`, except the official license text.
- GitHub metadata exists under `.github/`: `CODEOWNERS`, Dependabot configuration, issue templates, pull request template, and validation workflow.
- README install and validation commands match the real scripts in this repository.
- Source notes stay paraphrased; this repository must not redistribute copied source article text.

## GitHub Setup

- Create the GitHub repository with the intended owner and name before relying on badges or issue links.
- Set `main` as the default branch.
- Enable branch protection for `main` and require the `Validate` workflow before merge.
- Enable private vulnerability reporting or document the maintainer's private reporting channel.
- Confirm repository description, topics, license detection, and README rendering in the GitHub UI.
- Confirm Dependabot can open GitHub Actions update pull requests.

## Release Boundary

- Do not tag, push, publish, or create a GitHub release until local validation passes and the maintainer explicitly approves the external action.
- Keep external publication evidence separate from local readiness. A clean local gate means the repository is ready to publish, not that GitHub settings or remote checks have already passed.
