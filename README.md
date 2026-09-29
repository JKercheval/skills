# skills

My agent skills and global instructions for Claude Code and Codex, kept in one place and synced to every machine with `make sync`.

| What | Source in this repo | Claude Code reads | Codex reads |
|---|---|---|---|
| Skills | `skills/<name>/` | `~/.claude/skills/<name>` (symlink) | `~/.agents/skills/<name>` (symlink) |
| Working rules, then communication style | `global/rules.md`, then `global/style.md` | `~/.claude/CLAUDE.md` (copy) | `~/.codex/AGENTS.md` (copy) |
| Hooks | `hooks/session_context.py` | `hooks` in `~/.claude/settings.json` | `~/.codex/hooks.json` |

Both tools get the same global text and load it in every session. There's nothing to select or switch.

`make sync` never overwrites a `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md` that it didn't write, such as one that already exists on a new machine. It skips the file and says so. `make sync FORCE=1` replaces it after saving a backup. See [Set up a machine](#set-up-a-machine) before using it.

The hooks add two things the global text can't:

- **The time on every message.** Neither tool tells the agent when a message was sent, so it can't tell that hours or days passed. The hook adds a line like "User message sent Mon 2026-09-28 21:40 PDT" to each of your messages, and the style tells the agent to re-introduce earlier context after a long gap.
- **The style again after compaction.** When a long session is summarized to free space, the hook adds `global/style.md` back in with a note to follow it. For drift before that, run `/bro`: it re-reads the style, rewrites its last reply, and follows the style from then on.

## Skills

**Automatic** skills load on their own when a request matches; you can also invoke them by name. **Manual** skills run only when you invoke them: `/name` in Claude Code, `$name` in Codex.

| Skill | Mode | Reach for it when | Example |
|---|---|---|---|
| `how` | Automatic | You want to understand code before changing it, or ask where something should live | "How does `make sync` decide whether to overwrite `CLAUDE.md`?" |
| `blast-radius` | Automatic | A change looks small but you don't trust it. It proves what the change is safe because of, by running code | "What could commit 04168bc break?" |
| `tdd` | Automatic | Fixing a bug that has a cheap test path, or you want a failing test first | "Bug: `slugify('Hello, World!')` returns `hello,-world!`. Fix it." |
| `technical-writing` | Automatic | Writing something a reader sees cold: a README, docs, a PR description, a commit message, a ticket | "Write a PR description for this branch." |
| `unslop` | Automatic | Cleaning up text that already exists, or making it sound less AI-written | "Clean up this paragraph: ..." |
| `review-code` | Manual | You want a change reviewed in one pass for design problems, code smells, and bugs. Reviews uncommitted changes by default, then the branch. Confirms each finding against the code, running code where that proves it, and labels any it couldn't confirm | `/review-code` or `/review-code the auth changes, focus on error handling` |
| `review-adversarial` | Manual | Reviewing a PR or a large change. Three reviewers attack it from different angles, then the findings are filtered into Act on, Consider, Noted, and Dismissed | `/review-adversarial review PR 123` |
| `architect` | Manual | The design is still open: a new module, API, or data model with several viable shapes. Proposes 2 or 3 designs as real types and signatures, recommends one, and stops | `/architect a cache for the pricing API` |
| `implementation-plan` | Manual | The approach is agreed and you want it written down for an agent that wasn't in the conversation: milestones ordered by dependency, each with its outcomes, an implementation outline, and a definition of done. Saves to the path you give | `/implementation-plan docs/plans/search.md focus on the API first` |
| `implementation-plan-review` | Manual | You have a plan and want it challenged before any code is written. Checks the plan's claims against the code and whether an agent could implement it without guessing, then lists findings by severity. Doesn't edit anything | `/implementation-plan-review docs/plans/search.md` |
| `implementation-plan-execute` | Manual | A reviewed plan is ready to build. Asks its open questions first, then builds one milestone at a time, running the tests and checking the real result, and stops for your review after each. Commits a milestone only after you approve it | `/implementation-plan-execute docs/plans/search.md` |
| `why` | Manual | You want the reason code is the way it is, from git history, PRs, tickets, and docs. Grades every claim by confidence, and says exactly what it couldn't find. Not for debugging a failure | `/why is the retry limit 3 in the upload client?` |
| `figure-it-out` | Manual | A medium task you want done carefully without writing a plan: it defines done, captures a baseline, and works in small verified steps | `/figure-it-out move every caller from SyncStore to AsyncStore` |
| `teach` | Manual | You want to actually understand a change, subsystem, or concept, not just get a summary. Starts from a plain definition, gives the smallest answer first, and builds diagrams up piece by piece as you ask for more | `/teach how the global file sync decides what's safe to overwrite` |
| `reflect` | Manual | A session went sideways or taught something worth keeping. Three reviewers read the session, the findings are filtered hard, and you approve each proposed edit to a skill, the global rules, or the project's `AGENTS.md` | `/reflect` |
| `bro` | Manual | A reply was too dense or full of jargon. Restates it plainly | `/bro` |
| `engineering-principles` | Manual | You want the principle index in context. Other skills link to individual principles, so you rarely need this | `/engineering-principles` |

## Workflows

**Building something where the design isn't settled.**

1. Discuss the problem with the agent.
2. Run `/architect` if the shape is still open. It proposes two or three designs as real types and signatures, recommends one, and stops.
3. Review and adjust the sketch in conversation until you agree.
4. Run `/implementation-plan <path>`. The agreed sketch is part of the discussion, so the plan builds on it. Its first milestone is usually filling in the stubs.
5. Run `/implementation-plan-review <path>`, ideally in the other tool, so the plan isn't reviewed by the agent that wrote it. Decide what to change with the `ai-review-feedback` prompt, and update the plan.
6. Run `/implementation-plan-execute <path>`. It asks its open questions, then builds one milestone at a time and stops after each. Review each milestone, then approve it, and the agent commits it.

If the approach is already clear from the discussion, skip step 2.

**A medium task without a plan.** `/figure-it-out <task>`. It stops to show you its framing first only if the run will take hours.

**Fixing a bug.** Describe the bug. `tdd` loads on its own when there's a cheap test path: it writes a failing test, fixes the bug, and shows the test passing. If the fix touches something shared, ask "what could this break?" before merging, which loads `blast-radius`.

**Reviewing a change.** `/review-code` for a one-pass review, for example after each milestone of `/implementation-plan-execute`. `/review-adversarial` for a large or risky change, where three reviewers attack it from different angles. Ask "what could this break?" for the narrower question of impact outside the diff.

**Working in unfamiliar code.** Ask how it works first. `how` answers a narrow question directly, and spreads a question about a whole subsystem across parallel explorers. Before changing something whose shape looks odd, run `/why` on it: it ends with what the history says to preserve, change, and avoid.

**Writing.** Asking for a PR description, README, or commit message loads `technical-writing`. Asking to clean up existing text loads `unslop`. When a reply in chat is hard to follow, `/bro`.

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
- **A Tiddly prompt,** when it's a fill-in template used in chat apps (the Chat tab, claude.ai, ChatGPT), which skills don't reach.
- **Both,** rarely. Keep the skill as the real version and update the prompt copy when it changes.

## Set up a machine

Requires `make` and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/shane-kercheval/skills.git ~/repos/skills
cd ~/repos/skills
make sync
```

The folder can have any name and location, for example `~/repos/skills-personal` where `skills` is taken. `make sync` links to wherever the repo is.

If the machine already has a `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md`, `make sync` leaves it alone and says so. Run `make check-global` to print any such file, move anything worth keeping into `global/rules.md`, then run `make sync FORCE=1`. `FORCE=1` saves a timestamped backup (for example `CLAUDE.md.bak-20260924-094233`) before replacing the file.

Codex runs a new or changed hook only after you approve it. After the first `make sync`, and after any change to the hook commands, run `codex` and open `/hooks` to approve them. Claude Code runs them right away.

On a work machine, copy `local.mk.example` to `local.mk` to add extra skill folders.

## Day to day

| Task | Command |
|---|---|
| Update this computer with changes pushed from another one (runs `git pull`, then `make sync`) | `make pull` |
| Create a skill | `make new NAME=my-skill` (add `MANUAL=1` for invoke-only), fill in `SKILL.md`, then `make validate sync` |
| Move a skill created in `~/.claude/skills` into the repo | `make adopt NAME=my-skill` |
| Change global rules or style | Edit `global/rules.md` or `global/style.md`, then `make sync` |
| Check what's linked and generated | `make status` |
| See existing global files that sync would skip, with their contents | `make check-global` |
| List all commands | `make` |

What needs `make sync`:

- **Editing an existing skill: no.** The tool folders are symlinks into this repo, so edits apply right away.
- **Adding, renaming, or deleting a skill: yes.** A symlink has to be created or removed.
- **Editing anything in `global/`: yes.** Those files are copies, so a change takes effect only after `make sync` rewrites them, and only in sessions started after that.

## Why skills are symlinks but global files are copies

Symlinks are simpler, and skills work fine as symlinks in both tools. The global files can't be:

- Claude Code skips a symlinked `~/.claude/CLAUDE.md` in Cowork sessions. Its memory docs say so.
- Codex has no way to import one file into another, so its only global file, `~/.codex/AGENTS.md`, has to hold the rules and the style together. `make sync` assembles it, and writes the same text to `~/.claude/CLAUDE.md`.

Each generated file starts with an HTML comment naming its source and a hash of its contents. Claude Code strips that comment before the model sees it. The hash lets `make sync` tell a file it wrote and nobody touched (safe to rewrite) from one that was edited by hand, for example by Claude Code's memory commands. It never overwrites a hand edit without `FORCE=1`.

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

- **Skill suggester.** Mine recent sessions for corrections I repeat, and propose capturing each as a skill or rule. `reflect`'s transcript script would need to cover a window of days across projects. A lighter option: one line in `global/rules.md`, "When I give the same instruction or correction for the second time, suggest capturing it in a skill."
