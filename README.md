# skills

My agent skills and global instructions for Claude Code and Codex, kept in one place and synced to every machine with `make sync`.

| What | Source in this repo | Claude Code reads | Codex reads |
|---|---|---|---|
| Skills | `skills/<name>/` | `~/.claude/skills/<name>` (symlink) | `~/.agents/skills/<name>` (symlink) |
| Working rules for every session | `global/rules.md` | `~/.claude/CLAUDE.md` (copy) | `~/.codex/AGENTS.md` (copy) |
| How to communicate | `global/style.md` | `~/.claude/output-styles/<name>.md` (copy) | `~/.codex/AGENTS.md` (copy, after the rules) |

## Set up a machine

Requires `make` and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/shane-kercheval/skills.git ~/repos/skills
cd ~/repos/skills
make sync
```

If the machine already has a hand-written `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md`, `make sync` leaves it alone and says so. Move anything worth keeping into `global/rules.md`, then run `make sync FORCE=1`. `FORCE=1` saves a timestamped backup (for example `CLAUDE.md.bak-20260924-094233`) before replacing the file.

To use the communication style in Claude Code, set it once in `~/.claude/settings.json`. The name comes from the `name` field in `global/style.md`:

```json
{ "outputStyle": "<name>" }
```

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
- **Editing anything in `global/`: yes.** Those files are copies, so a change takes effect only after `make sync` rewrites them. Claude Code also reads output styles at startup, so restart it after changing the style.

## Why skills are symlinks but global files are copies

Symlinks are simpler, and skills work fine as symlinks in both tools. The global files can't be:

- Claude Code skips a symlinked `~/.claude/CLAUDE.md` in Cowork sessions. Its memory docs say so.
- Codex has no output styles, and no way to import one file into another. Its only global file, `~/.codex/AGENTS.md`, has to hold the rules and the style together, so `make sync` assembles it.
- An output style needs frontmatter that the Codex copy must not include.

Each generated file starts with an HTML comment naming its source and a hash of its contents. Claude Code strips that comment before the model sees it. The hash lets `make sync` tell a file it wrote and nobody touched (safe to rewrite) from one that was edited by hand, for example by Claude Code's memory commands. It never overwrites a hand edit without `FORCE=1`.

## Where the output style applies

The style is a Claude Code output style. It applies to every response in a session once `outputStyle` names it. Claude never picks a style on its own.

| Surface | Uses the style? |
|---|---|
| Claude Code in the terminal | Yes. `/output-style <name>` switches for the session |
| `claude -p` | Yes (tested). `--settings '{"outputStyle":"x"}'` overrides it for one run. `--bare` skips everything in `~/.claude`, so no style and no `CLAUDE.md` |
| Code tab in the Claude desktop app | Yes, from `outputStyle` in settings |
| Chat tab in the desktop app, and claude.ai | No. Output styles are a Claude Code feature |
| Codex | Gets the same text through `~/.codex/AGENTS.md` |
| Subagents | No. They run with their own system prompt, so styles don't reach them |

## Other files

- `AGENTS.md` has the authoring rules and repo rules for agents working on this repo. `CLAUDE.md` imports it for Claude Code. Neither is a global file.
- `sources/` tracks upstream skill repos, the last commit reviewed, and what was ported.

## Ideas

- **Skill suggester.** A skill that fires on "the user keeps repeating themselves" probably wouldn't load, because agents pick skills by matching the task, and frustration isn't a task. Two options that would work instead:
  - A user-invoked skill that mines recent Claude Code and Codex transcripts for repeated instructions and corrections, and proposes new skills or edits. pstack's `reflect` and `automate-me` are starting points.
  - One line in `global/rules.md`: "When I give the same instruction or correction for the second time, suggest capturing it in a skill."
