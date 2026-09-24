# skills

My agent skills and global instructions for Claude Code and Codex, kept in one place and synced to every machine with `make sync`.

| What | Source in this repo | Claude Code reads | Codex reads |
|---|---|---|---|
| Skills | `skills/<name>/` | `~/.claude/skills/<name>` (symlink) | `~/.agents/skills/<name>` (symlink) |
| Working rules, then communication style | `global/rules.md`, then `global/style.md` | `~/.claude/CLAUDE.md` (copy) | `~/.codex/AGENTS.md` (copy) |

Both tools get the same global text and load it in every session. There's nothing to select or switch.

## Set up a machine

Requires `make` and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/shane-kercheval/skills.git ~/repos/skills
cd ~/repos/skills
make sync
```

If the machine already has a hand-written `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md`, `make sync` leaves it alone and says so. Move anything worth keeping into `global/rules.md`, then run `make sync FORCE=1`. `FORCE=1` saves a timestamped backup (for example `CLAUDE.md.bak-20260924-094233`) before replacing the file.

On a work machine, copy `local.mk.example` to `local.mk` to add extra skill folders.

## Day to day

| Task | Command |
|---|---|
| Get changes from other machines | `make pull` |
| Create a skill | `make new NAME=my-skill` (add `MANUAL=1` for invoke-only), fill in `SKILL.md`, then `make validate sync` |
| Move a skill created in `~/.claude/skills` into the repo | `make adopt NAME=my-skill` |
| Change global rules or style | Edit `global/rules.md` or `global/style.md`, then `make sync` |
| Check what's linked and generated | `make status` |
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

- **Skill suggester.** A skill that fires on "the user keeps repeating themselves" probably wouldn't load, because agents pick skills by matching the task, and frustration isn't a task. Two options that would work instead:
  - A user-invoked skill that mines recent Claude Code and Codex transcripts for repeated instructions and corrections, and proposes new skills or edits. pstack's `reflect` and `automate-me` are starting points.
  - One line in `global/rules.md`: "When I give the same instruction or correction for the second time, suggest capturing it in a skill."
