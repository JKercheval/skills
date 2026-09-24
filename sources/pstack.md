# pstack (cursor/plugins)

- Repo: https://github.com/cursor/plugins
- Skills path: `pstack/skills/` (plus `pstack/agents/` and `pstack/automations/benny/skills/`)
- Author: Lauren Tan (poteto). Built for Cursor, and for TypeScript, React, Electron, and iOS work at a large company.
- Last reviewed commit: `12d587dfb20741cafc376c42c696c5f6e2a64487` (2026-09-23, "fix(pstack): resolve rule conflicts and read the model rule the same way (#422)")
- Last reviewed on: 2026-09-23

## How pstack is built

- `poteto-mode` is the entry point. It routes a task to one of 23 playbooks in `poteto-mode/playbooks/` and holds an inline index of the principles.
- The 23 `principle-*` skills are short rules, each one file, all with `disable-model-invocation: true`. Other skills mostly reference them by name ("the **prove-it-works** principle skill"), not by path. That works in Cursor but not in Claude Code, which blocks invoking a skill with that flag. When porting, link them by relative path or fold them into one principles skill with a `references/` folder.
- Several skills (`arena`, `interrogate`, `architect`, `reflect`, `how`, `why`, `swarm`) send subagents to GPT, Grok, and Claude models through a Cursor rule file. Claude Code and Codex can't mix vendors in subagents.

## Decisions

The first review recommended the decisions below. They are still `undecided` until the user confirms each one.

| Upstream skill | Recommendation | Reason | Decision | Local name |
|---|---|---|---|---|
| how | port | Parallel explorers, then one explainer. Only the model routing is Cursor-specific | undecided | |
| why | adapt | Good method and confidence rules. Cut the evidence sources down to git, GitHub, and whatever the user has connected | undecided | |
| recall | adapt | Rebuilds recent context from transcripts. Needs Claude Code and Codex transcript paths | undecided | |
| blast-radius | port | Proves the one fact a change's safety rests on. Almost no Cursor dependency | undecided | |
| architect | adapt | Types and signatures before code, two designs minimum. Depends on multi-model `arena` | undecided | |
| arena | adapt | N attempts, pick a base, graft the best parts. Loses cross-vendor diversity | undecided | |
| swarm | adapt | Parallel workers, one report. Uses Cursor cloud workers | undecided | |
| interrogate | adapt | Multi-model review with Act on / Consider / Noted / Dismissed. Overlaps Claude Code `/code-review` | ported 2026-09-24: reviewers differ by lens (correctness and security, design, code quality) instead of by model; reviewers read the diff themselves; large diffs split by area; report only, never posts to the PR. Compare with Tiddly `code-review`, `pre-pr-review`, `ai-review-feedback` later | interrogate |
| figure-it-out | port | Designs a custom playbook for large migrations | undecided | |
| show-me-your-work | port | Append-only decision log for long unattended runs | undecided | |
| tdd | port | Failing test first only when cheap | undecided | |
| teach | port | Explains with `how` and `why`, builds diagrams up step by step | undecided | |
| technical-writing | port | Diátaxis, Google style, STE, and Global English. Drop the house rules | undecided | |
| unslop | adapt | List of AI-writing tells. Trim the author's punctuation bans. Overlaps local `improve-writing` | undecided | |
| bro | port | One line: restate plainly | undecided | |
| no-comments (+ Comment Sicko agent) | skip | Extreme no-comments stance, TypeScript and ESLint focus | undecided | |
| typescript-best-practices | skip | TypeScript only. Ideas could feed `python-coding-guidelines` | undecided | |
| create-verification-skill | port | Generates a per-project skill that drives the real app and captures evidence | undecided | |
| maintain-verification-skill | adapt | Only useful after adopting `create-verification-skill`. Opens a PR | undecided | |
| reflect | adapt | Turns a session's lessons into skill edits. Needs transcript paths and `skill-creator` | undecided | |
| automate-me | adapt | Drafts a personal mode skill from transcripts. Commits and opens a PR, which must go | undecided | |
| poteto-mode (and its 23 playbooks) | skip as a whole | Personal router, bound to Cursor, Bugbot, and `cursor-team-kit`. Mine individual ideas instead | undecided | |
| setup-pstack | skip | Writes a Cursor rule for model routing | undecided | |
| make-bot-ui | skip | Cursor Grok Bot webhooks | undecided | |
| poteto-agent | skip | Wrapper that loads `poteto-mode` | undecided | |
| benny (setup-benny, triage-issue-reports, reproduce-and-fix-issues) | skip | Slack bug-triage bots on Cursor Automations. The fail-closed safety rules are worth reading | undecided | |
| principle-* (23) | adapt | Most are general engineering rules. Port as one principles skill with one reference file per principle. Review `never-block-on-the-human`, `outcome-oriented-execution`, and `migrate-callers-then-delete-legacy-apis` against the user's own stance | undecided | |
