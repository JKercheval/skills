# Agent instructions for this repo

This repo holds the user's personal agent skills and global instructions for Claude Code and Codex.

- Each directory in `skills/` is one skill. `make sync` symlinks every skill into `~/.claude/skills/` (Claude Code) and `~/.agents/skills/` (Codex).
- `global/` is the source for the instructions both tools load in every session. `make sync` writes it into `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`.

This file is for agents working on this repo. It is not one of the global files.

## Rules

- Pushing to `main` is fine in this repo.
- Create and edit skills in `skills/`, never in `~/.claude/skills/` or `~/.agents/skills/`. New skills there are invisible to other machines.
- Edit global instructions in `global/`, never in `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md`. `make sync` refuses to overwrite a generated file that was edited by hand, so edits there block the next sync.
- Never edit `~/.claude/skills/synced/`. Claude Code downloads it from the user's claude.ai account and overwrites it.
- After adding, renaming, or editing a skill or anything in `global/`, run `make validate`, fix every ERROR, and fix warnings unless there is a stated reason. Then run `make sync`.
- When you add or rename a skill, update the Skills table in `README.md`: mode, when the user would reach for it, and a realistic example of what they'd type. If it combines with other skills or the user's prompts in a sequence, add or update a flow under Workflows. `make validate` warns when a skill is missing from the table.
- The README describes what's here and how to use it. Keep out meta commentary: why a section exists, what a skill replaced, where an idea came from, and when something was tested. That history goes in the `sources/` ledgers.
- If you change anything in `scripts/`, run `make test`.

## Commands

| Command | Does |
|---|---|
| `make new NAME=x` | Create `skills/x/SKILL.md` from the template |
| `make validate` | Check every skill against the spec and the rules below |
| `make sync` | Remove stale links, link every skill into both tools, and generate the global files. `FORCE=1` overwrites a global file that was hand-edited or not generated here, after backing it up |
| `make status` | Show each skill's link state, plus skills in the tool folders that this repo does not manage |
| `make adopt NAME=x` | Move a skill that was created directly in a tool folder into `skills/` and link it back |
| `make unlink` | Remove every link this repo created |

Per-machine extra skill folders (for example a separate work repo) go in `local.mk`. See `local.mk.example`.

## Writing a skill

### Hard limits

`make validate` enforces these. They come from the Agent Skills spec, which Claude Code and Codex both follow.

| Field | Limit |
|---|---|
| `name` | Required. 1 to 64 characters. Lowercase letters, digits, and single hyphens. No leading or trailing hyphen. Must equal the directory name. |
| `description` | Required. 1 to 1,024 characters. No XML tags. |
| `compatibility` | Optional. At most 500 characters. |

Claude Code shows at most 1,536 characters of `description` plus `when_to_use`. The Claude API rejects names that contain "anthropic" or "claude".

### Descriptions decide whether a skill is used

At startup each tool sees only every skill's `name` and `description`. The agent picks a skill by matching the task against the description, so a weak description means the skill never loads.

- Say what the skill does and when to use it: "Reviews Python diffs for missing type hints and imports inside functions. Use when reviewing Python code or before the user commits Python changes."
- Write in third person. "Reviews diffs", not "I can review" or "You can use this to".
- Put the trigger words first. Both tools shorten descriptions when many skills are installed.
- Use the words the user would actually type: file types, tool names, task names.
- Keep skills from overlapping. If two descriptions match the same request, the agent picks unpredictably. Narrow one or merge them.
- Name skills by activity or subject. Avoid vague names like `helper` or `utils`.
- Give related skills a shared prefix so they group together when the user types `/` or `$`: `review-adversarial`, `review-plan`. Don't reuse a name a tool already ships, such as Claude Code's `/code-review`.

### Automatic or invoke-only

Every automatic skill puts its name and description into both tools' startup listings. The listings have a fixed budget, and overlapping descriptions make the agent's choice unpredictable. So keep the automatic set small and distinct.

A trigger must be distinct from everyday requests too, not only from other skills. "Why" also starts debugging questions ("why does this test fail?"), which is why `why` is invoke-only.

| Kind | Setting | Examples |
|---|---|---|
| Rules that apply to every task | Not a skill. One line each in the user's global `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`. Keep it to about five lines | "Verify against the real result, not 'it compiles'" |
| Task skill with a distinct trigger | Automatic (the default) | `how` ("how does X work"), `blast-radius` ("what could this break") |
| Workflow the user starts on purpose | Invoke-only: `make new NAME=x MANUAL=1` | `architect`, `review-adversarial` |
| Library that other skills read | Invoke-only, with content in `references/` | `engineering-principles` |

Invoke-only needs both settings: `disable-model-invocation: true` in `SKILL.md` (Claude Code) and `policy: allow_implicit_invocation: false` in `agents/openai.yaml` (Codex). Tested on 2026-09-23: with those, neither tool lists the skill, and `/name` or `$name` still invokes it. `make validate` warns when only one is set, and reports how much of the listing budget the automatic skills use.

### The body

- The whole `SKILL.md` loads when the skill fires. Keep it under 500 lines (Anthropic recommends under about 5,000 tokens).
- Include only what the agent does not already know. Cut explanations of common concepts.
- Move long reference material into `references/`, scripts into `scripts/`, and templates into `assets/`. Link each file from `SKILL.md` with a relative path and say when to read it. Keep references one level deep.
- Prefer a script over prose for anything that must be exact or repeatable.
- Avoid facts that go stale (dates, versions, "the new API"), unless the skill says when they were checked.

### Work in both Claude Code and Codex

- Write tool-neutral instructions: "read the file", "run the tests", "spawn a subagent". Don't name a single tool's functions (`AskUserQuestion`, `Task`) unless the skill only makes sense in that tool. If so, say so in the description.
- To point at another skill's content, link the file by relative path: `[prove it works](../engineering-principles/references/prove-it-works.md)`. Don't rely on the agent invoking a skill by name, because Claude Code blocks invoking an invoke-only skill. Reading its files still works. Both tools tell the agent the skill's folder, and `make sync` puts every skill side by side, so `../` links resolve. `make validate` reports any relative link whose target doesn't exist, so rename a file and fix its links in the same change.
- Use plain relative links, not `${CLAUDE_SKILL_DIR}`. Codex doesn't substitute it.
- Claude Code-only frontmatter (`disable-model-invocation`, `user-invocable`, `allowed-tools`, `context`, `model`, `paths`) is not in Codex's docs. Assume Codex ignores it.

### Test a new skill

After `make sync`, test the skill in fresh sessions of both tools. A skill added during a session may not appear in that session.

1. **It fires when it should.** From a directory where the request makes sense, send a request that doesn't name the skill: `claude -p "<request>" --output-format stream-json --verbose` and `codex exec "<request>"`. Confirm it fired from the tool calls, not from the agent's own account: a `Skill` call naming it in Claude Code's log, or a read of its `SKILL.md` in Codex's output. Invoke an invoke-only skill by name instead (`/name` or `$name`).
2. **It stays quiet when it shouldn't.** For an automatic skill, also send the nearest everyday request it shouldn't take, and confirm it doesn't fire. For `why`, that would be a debugging question.
3. **It does what it says.** Check the output against the skill's steps. Use a throwaway project for skills that edit code.

## Global instructions

`make sync` writes the same text into `~/.claude/CLAUDE.md` (Claude Code) and `~/.codex/AGENTS.md` (Codex): `global/rules.md`, then `global/style.md` if it exists. Both tools load that file in every session.

- `rules.md` holds working rules for every task. `style.md` holds how to communicate. Both are plain Markdown with no frontmatter.
- Keep the combined text short. Claude Code's docs target under 200 lines per `CLAUDE.md` and say longer files reduce adherence. Codex reads at most 32 KiB by default. `make validate` warns past either limit.
- The style is deliberately not a Claude Code output style. An output style needs a per-machine `outputStyle` setting and doesn't exist in Codex, so one text in both global files is simpler. If Claude Code ever follows the style noticeably worse than Codex, an output style is the thing to try.

## Keeping these rules current

Last checked against the docs on 2026-09-23. To re-check, fetch these pages (the `.md` URLs return raw markdown), compare them with this file and with the constants at the top of `scripts/skills.py`, and update both along with the date above.

- Agent Skills spec: https://agentskills.io/specification.md
- Claude Code skills: https://code.claude.com/docs/en/skills.md
- Anthropic authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md
- Codex skills: https://developers.openai.com/codex/skills.md
- Claude Code memory (CLAUDE.md): https://code.claude.com/docs/en/memory.md
- Codex AGENTS.md: https://developers.openai.com/codex/guides/agents-md.md

## Porting skills from other repos

Read `sources/README.md` before reviewing or porting skills from an upstream repo. It has the review procedure, the porting rules, and the user's selection criteria. Each upstream repo has a ledger in `sources/` that records the last commit reviewed.
