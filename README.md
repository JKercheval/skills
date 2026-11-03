# skills

My agent skills and global instructions for Claude Code and Codex, kept in one place and synced to every machine with `make sync`.

## Quickstart on a new machine

Requires `make`, [uv](https://docs.astral.sh/uv/), and `python3`. Details are in [Set up a machine](#set-up-a-machine).

```bash
git clone https://github.com/shane-kercheval/skills.git ~/repos/skills   # any folder name works
cd ~/repos/skills
make check-global   # shows how any existing CLAUDE.md or AGENTS.md differs from what sync writes
make sync           # links the skills, writes the global files, installs the hooks
```

- If `make check-global` printed a file, move anything worth keeping into `global/rules.md` before you sync. `make sync` backs the file up and replaces it.
- In Codex, open `/hooks` once and approve the two hooks.

## What `make sync` sets up

| What | Source in this repo | Claude Code reads | Codex reads |
|---|---|---|---|
| Skills | `skills/<name>/` | `~/.claude/skills/<name>` (symlink) | `~/.agents/skills/<name>` (symlink) |
| Working rules, then any other repo's rules named in `local.mk`, then writing and communication style | `global/rules.md`, then each `GLOBAL_EXTRA` file, then `global/style.md` | `~/.claude/CLAUDE.md` (copy) | `~/.codex/AGENTS.md` (copy) |
| Hooks | `hooks/session_context.py` | `hooks` in `~/.claude/settings.json` | `~/.codex/hooks.json` |

Both tools get the same global text and load it in every session. There's nothing to select or switch.

The hooks add two things the global text can't:

- **The time on every message.** Neither tool tells the agent when a message was sent, so it can't tell that hours or days passed. The hook adds a line like "User message sent Mon 2026-09-28 21:40 PDT" to each of your messages, and the style tells the agent to re-introduce earlier context after a long gap.
- **The style again after compaction.** When a long session is summarized to free space, the hook adds `global/style.md` back in with a note to follow it. For drift before that, invoke `my-unslop` with no text: it rereads the writing rules and rewrites its last reply.

## Skills

**Automatic** skills load on their own when a request matches; you can also invoke them by name. **Manual** skills run only when you invoke them: `/name` in Claude Code, `$name` in Codex.

| Skill | Mode | Use it when | Example |
|---|---|---|---|
| `my-how` | Automatic | You want to understand code before changing it, or ask where something should live | "How does `make sync` decide whether to overwrite `CLAUDE.md`?" |
| `my-blast-radius` | Automatic | A change looks small but you don't trust it. It proves what the change is safe because of, by running code | "What could commit 04168bc break?" |
| `my-tdd` | Automatic | Fixing a bug that has a cheap test path, or you want a failing test first | "Bug: `slugify('Hello, World!')` returns `hello,-world!`. Fix it." |
| `my-technical-writing` | Automatic | Writing a document a reader sees cold: a README, docs, a design doc, a plan, a ticket, a commit message. It adds document types and formats to the writing rules in `global/style.md` | "Write a README section on how to run the tests." |
| `my-pr-description` | Automatic | Writing a PR title and description: why the change exists and what it does, then how | "Write a PR description for this branch." |
| `my-requirements-doc` | Automatic | A build has open design questions and needs a requirements document before any plan: what's needed, what exists, the problems to solve, and the decisions to make | "Write a requirements doc for the payment-metrics model." |
| `my-unslop` | Automatic | Cleaning up or reviewing existing text against the writing rules, or making the agent redo its last reply when it broke them | "Clean up this paragraph: ..." |
| `my-review-adversarial` | Manual | Reviewing a PR or a large change. Three reviewers each look for a different kind of problem (correctness and security, design, code quality), then the findings are filtered into Act on, Consider, Noted, and Dismissed | `/my-review-adversarial review PR 123` |
| `my-review-ai-feedback` | Manual | Deciding what to do about reviews written by AI agents. It checks each finding against the code or plan, confirms or refutes it, and says which decisions are yours and which the agent's | `/my-review-ai-feedback reviews.md` |
| `my-review-code` | Manual | A one-pass review of a code change for design flaws, code smells, and bugs, each finding confirmed against the code. Uncommitted changes by default, else the branch | `/my-review-code` |
| `my-review-pre-pr` | Manual | The last review before a pull request: what only the whole branch shows, such as consistency across files, leftovers, drifted names, and completeness against the plan | `/my-review-pre-pr plans/2026-11-03-done-column.md` |
| `my-review-followup` | Manual | Handing a plan or change to another agent for a follow-up review. Drafts the brief: what to read, what is decided and why, what changed, where to focus | `/my-review-followup` |
| `my-architect` | Manual | The design is still open: a new module, API, or data model with several viable shapes. Proposes 2 or 3 designs as real types and signatures, recommends one, and stops | `/my-architect a cache for the pricing API` |
| `my-why` | Manual | You want the reason code is the way it is, from git history, PRs, tickets, and docs. Grades every claim by confidence, and says exactly what it couldn't find. Not for debugging a failure | `/my-why is the retry limit 3 in the upload client?` |
| `my-reflect` | Manual | A session went wrong or taught something worth keeping. Three reviewers read the session, most findings are dropped, and you approve each proposed edit to a skill, the global rules, or the project's `AGENTS.md` | `/my-reflect` |
| `my-implementation-plan` | Manual | Writing a milestone-by-milestone plan for a coding agent that was not in the conversation, after the approach is agreed | `/my-implementation-plan plans/2026-11-03-done-column.md` |
| `my-implementation-plan-review` | Manual | Reviewing an implementation plan against the code before anything is built. Read-only | `/my-implementation-plan-review plans/2026-11-03-done-column.md` |
| `my-implementation-plan-execute` | Manual | Building a plan one milestone at a time, surfacing open questions first and stopping for your review after each milestone | `/my-implementation-plan-execute plans/2026-11-03-done-column.md` |
| `my-project-plan` | Manual | Writing a plan for a multi-step project that is not all code: tools, documents, people | `/my-project-plan plans/evals.md` |
| `my-project-plan-review` | Manual | Reviewing a project plan: goal, milestone order, evidence of done, and the tool assumptions it relies on. Read-only | `/my-project-plan-review plans/evals.md` |
| `my-figure-it-out` | Manual | A task too big to just do and too small for a written plan. Frames a checkable definition of done, captures a baseline, and works in small verified units | `/my-figure-it-out move every caller to AsyncStore` |
| `my-teach` | Manual | Understanding a change, subsystem, or concept, not just getting a summary. Starts from a plain definition and builds diagrams up one piece at a time | `/my-teach the retry worker` |
| `my-create-git-worktree` | Manual | Starting a branch in its own folder next to the repo, from the remote's latest base, with no upstream until the first push | `/my-create-git-worktree ui-updates` |
| `my-switchboard-orchestrator` | Manual | Directing Switchboard's coding agents from this session: briefing, review rounds, and reports, without writing code. Add `plan`, `analysis`, or `data science` after it | `/my-switchboard-orchestrator plan` |
| `my-engineering-principles` | Manual | You want the principle index in context. Other skills link to individual principles, so you rarely need this | `/my-engineering-principles` |

## Workflows

Two ways of working use the same skills: you directing one agent in Claude Code or Codex, and the `my-switchboard-orchestrator` skill directing several agents through Switchboard. The table maps each step to what runs it. Every piece is a skill in this repo, except Switchboard's two builtin prompts (`code-review` and `analyze-ai-reviews`), which live in the Switchboard repo as copies of `my-review-code` and `my-review-ai-feedback`.

| Step | You, with one agent | The orchestrator, with Switchboard agents |
|---|---|---|
| Agree the approach | Discuss it. `/my-architect` when the shape is still open | Plan mode: agents investigate. The orchestrator settles what the evidence settles and brings you every choice of scope, direction, or tradeoff |
| Write the plan | `/my-implementation-plan`, or `/my-project-plan` when the work is not all code | The writer agent gets `/my-implementation-plan` with the decisions and their reasons |
| Read the plan | You, before any agent reviews it | You, before any review round |
| Review the plan | `/my-implementation-plan-review` (`/my-project-plan-review` for a project plan), ideally in the other tool, then `/my-review-ai-feedback` to decide | Reviewer agents get `/my-implementation-plan-review` or `/my-project-plan-review`. Disputes come to you, and you approve the plan |
| Build | `/my-implementation-plan-execute`, which stops after each milestone. `/my-figure-it-out` for a task with no plan | Execute mode: the implementer builds one milestone and leaves it uncommitted |
| Review the change | `/my-review-code`. `/my-review-adversarial` for a large or risky change. "What could this break?" for impact outside the diff | Switchboard's review workflows, with its builtin `code-review` and `analyze-ai-reviews` prompts. `/my-review-ai-feedback` when a round runs without a workflow |
| Decide what to act on | `/my-review-ai-feedback` | The orchestrator settles technical findings and brings you the rest |
| Re-review after fixes | `/my-review-followup` drafts the brief for the next reviewer | Another round with the same reviewers, with what is already decided in the brief |
| Before the PR | `/my-review-pre-pr` | A new reviewer gets `/my-review-pre-pr`. The implementer drafts with `my-pr-description` |
| Open the PR | You | The orchestrator proposes it and opens it on your yes |

**Building something where the design isn't settled.**

1. Discuss the problem with the agent.
2. Run `/my-architect` if the shape is still open. It proposes two or three designs as real types and signatures, recommends one, and stops.
3. Review and adjust the sketch in conversation until you agree.
4. Write the plan with `/my-implementation-plan`. The agreed sketch is part of the discussion, so the plan builds on it. Its first milestone is usually filling in the stubs.
5. Review it with `/my-implementation-plan-review`, ideally in the other tool, and decide what to change with `/my-review-ai-feedback`. Then build it with `/my-implementation-plan-execute`, which stops after each milestone for your review.

If the approach is already clear from the discussion, skip step 2.

**A medium task without a plan.** `/my-figure-it-out`. It stops to show you its framing first only if the run will take hours.

**Fixing a bug.** Describe the bug. `my-tdd` loads on its own when there's a cheap test path: it writes a failing test, fixes the bug, and shows the test passing. If the fix touches something shared, ask "what could this break?" before merging, which loads `my-blast-radius`.

**Reviewing a change.** `/my-review-adversarial` for a large or risky change, where three reviewers each look for a different kind of problem. Ask "what could this break?" for the narrower question of impact outside the diff. For a one-pass review, the last pass before a PR, or deciding what to act on from the reviews, use `/my-review-code`, `/my-review-pre-pr`, and then `/my-review-ai-feedback`.

**Working in unfamiliar code.** Ask how it works first. `my-how` answers a narrow question directly, and spreads a question about a whole subsystem across parallel explorers. Before changing something whose shape looks odd, run `/my-why` on it: it ends with what the history says to preserve, change, and avoid.

**Writing.** The writing rules in `global/style.md` load in every session and cover replies and documents alike. Asking for a PR description loads `my-pr-description`. Asking for a README, plan, or commit message loads `my-technical-writing`, which adds what only documents need. Asking to clean up existing text loads `my-unslop`. When a reply or a document is hard to follow, invoke `my-unslop` with no text. To understand a change or subsystem rather than just get a summary, `/my-teach`.

**Checking a change in the running app, not just the tests.** In Claude Code, `/verify` after the change. For a project with a multi-step setup, run `/run-skill-generator` in it once first. See [Built into Claude Code](#built-into-claude-code).

## Built into Claude Code

Claude Code ships these skills itself. They aren't in this repo, and Codex has no equivalent.

| Skill | Does | Example |
|---|---|---|
| `/verify` | Builds and starts your project, then checks that a code change does what it should in the running app, without falling back to tests or type checks. If it had to work out how to start the app, it saves the steps to `.claude/skills/verify/SKILL.md` in the project | After fixing Tiddly's search box: `/verify search returns notes that match body text` |
| `/run` | Starts your project and drives it so you can see a change working | `/run and open the notes list` |
| `/run-skill-generator` | Works out how to start the project from a clean environment (installs, env vars, database, launch commands) and saves the steps as a skill at `.claude/skills/run-<name>/`. `/run`, `/verify`, and other agents in the project then follow those steps instead of guessing them from the README | Once per project, and again when the setup changes |

`/run` and `/verify` work without setup on simple projects, but guess wrong when starting the app takes several steps. Run `/run-skill-generator` once in those projects. Claude edits the saved steps itself when one fails. The generated skill is committed to that project, not this repo.

To let Codex use the saved steps too, link them into the folder Codex reads project skills from, and commit the link:

```bash
mkdir -p .agents/skills && ln -s ../../.claude/skills/run-<name> .agents/skills/run-<name>
```

## Skill or Tiddly prompt

- **A skill,** when a coding agent (Claude Code or Codex) will run it, or it needs extra files, scripts, or links to other skills. Codex can't use Tiddly's prompts at all.
- **A Tiddly prompt,** when it's a fill-in template used in chat apps (the Chat tab, claude.ai, ChatGPT), where skills aren't available.
- **Both,** rarely. Keep the skill as the real version and update the prompt copy when it changes.

## Set up a machine

Requires `make` and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/shane-kercheval/skills.git ~/repos/skills
cd ~/repos/skills
make sync
```

The folder can have any name and location, for example `~/repos/skills-personal` where `skills` is taken. `make sync` links to wherever the repo is.

If the machine already has a `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md` that sync didn't write, `make sync` saves a timestamped backup (for example `CLAUDE.md.bak-20260924-094233`) and replaces it. Run `make check-global` first to see the file, and move anything worth keeping into `global/rules.md`.

Codex runs a new or changed hook only after you approve it. After the first `make sync`, and after any change to the hook commands, run `codex` and open `/hooks` to approve them. Claude Code runs them right away.

On a work machine, copy `local.mk.example` to `local.mk` and set two things there. `EXTRA_SOURCES` adds another repo's skill folders. `GLOBAL_EXTRA` names another repo's rules file, such as `~/repos/work-skills/global/rules.md`, and `make sync` puts its text into both global files after `global/rules.md`. That repo's own sync must not write to the global files, because this sync replaces them whole.

## Day to day

| Task | Command |
|---|---|
| Update this computer with changes pushed from another one (runs `git pull`, then `make sync`) | `make pull` |
| Create a skill | `make new NAME=my-skill` (add `MANUAL=1` for invoke-only), fill in `SKILL.md`, then `make validate sync` |
| Move a skill created in `~/.claude/skills` into the repo | `make adopt NAME=my-skill` |
| Change global rules or style | Edit `global/rules.md` or `global/style.md`, then `make sync` |
| Change another repo's rules that `GLOBAL_EXTRA` includes, such as the work rules | Edit that repo's rules file, then `make sync` here |
| Check what's linked and generated | `make status` |
| See how existing global files differ from what sync writes | `make check-global` |
| List all commands | `make` |

What needs `make sync`:

- **Editing an existing skill: no.** The tool folders are symlinks into this repo, so edits apply right away.
- **Adding, renaming, or deleting a skill: yes.** A symlink has to be created or removed.
- **Editing anything in `global/`: yes.** Those files are copies, so a change takes effect only after `make sync` rewrites them, and only in sessions started after that.

## Why skills are symlinks but global files are copies

Symlinks are simpler, and skills work fine as symlinks in both tools. The global files can't be:

- Claude Code skips a symlinked `~/.claude/CLAUDE.md` in Cowork sessions. Its memory docs say so.
- Codex has no way to import one file into another, so its only global file, `~/.codex/AGENTS.md`, has to hold the rules and the style together. `make sync` assembles it, and writes the same text to `~/.claude/CLAUDE.md`.

Each generated file starts with an HTML comment naming its source and a hash of its contents. Claude Code strips that comment before the model sees it. The hash lets `make sync` tell a file it wrote and nobody touched from one that changed since: a hand edit, or a line added by Claude Code's memory commands. Sync always writes the file. When it had changed, sync saves a timestamped backup first, prints the diff (lines starting with `-` are gone from the file), and asks whether to delete the backup. Run without a terminal, as when an agent runs it, sync keeps the backup and prints a note telling the agent to report the diff and backup to you.

## Why the style isn't a Claude Code output style

Claude Code has output styles, a slot for "every response in a certain voice, length, or format". We don't use one:

- A style applies only once `outputStyle` in each machine's `~/.claude/settings.json` names it. A machine without that setting silently has no style.
- Codex has no output styles, so the style text has to go into `~/.codex/AGENTS.md` anyway. Putting the same text into `~/.claude/CLAUDE.md` gives one mechanism for both tools.
- `CLAUDE.md` also reaches Claude Code's general-purpose subagents. Output styles don't.

An output style sits in Claude Code's system prompt, while `CLAUDE.md` arrives as context. We have no evidence that this changes how well Claude follows it. If Claude ever follows the style noticeably worse than Codex, an output style is the thing to try.

`claude -p` loads `~/.claude/CLAUDE.md` like an interactive session. `claude --bare -p` skips everything in `~/.claude`, so it gets neither the rules nor the style.

## Other files

- `AGENTS.md` has the authoring rules and repo rules for agents working on this repo. `CLAUDE.md` imports it for Claude Code. Neither is a global file.
- `sources/` tracks upstream skill repos, the last commit reviewed, and what was ported.

## Ideas

- **Skill suggester.** Mine recent sessions for corrections I repeat, and propose capturing each as a skill or rule. `my-reflect`'s transcript script would need to cover a window of days across projects. A lighter option: one line in `global/rules.md`, "When I give the same instruction or correction for the second time, suggest capturing it in a skill."
