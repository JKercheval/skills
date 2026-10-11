---
name: reflect
description: Reviews the current session for durable lessons (mistakes and corrections, user preferences, tool quirks, context the agent should have fetched itself, skills that should have fired) and proposes edits to the user's skills, global rules, style candidates, or the project's AGENTS.md, applied only after the user approves each one. Use when the user invokes /reflect or $reflect.
license: MIT. Adapted from pstack by Lauren Tan. See sources/pstack-LICENSE.txt in the skills repo
metadata:
  source: "cursor/plugins pstack/skills/reflect @ 12d587d"
disable-model-invocation: true
---

# Reflect

Turn what this session taught into durable edits. Nothing is edited until the user approves it.

Skip it for a trivial session, or when every lesson is already covered by a skill the session followed correctly. A one-off is not a lesson.

## 1. Condense the transcript

Run the bundled script with the session's working directory, writing to a temporary file:

```bash
python3 <this skill's folder>/scripts/transcript.py --cwd <session working directory> --out <temp dir>/reflect-transcript.txt
```

It finds this session's transcript in Claude Code or Codex (the most recently modified one for that directory) and keeps only the conversation plus one line per tool call. Check that the first user messages in its output match this conversation. If they don't, or it finds nothing, write a digest of the session yourself and use that, and say so.

If the user names an earlier session's transcript file instead, pass it with `--path <file>` and review that session. Either tool's format works.

## 2. Find the skills repo

Resolve this skill's folder to its real path. The skills are symlinks into the user's skills repo, so the repo root is two levels up (for example, `realpath` of the skill folder, then its parent's parent). Confirm the root has `AGENTS.md`, `global/rules.md`, and `skills/`. If it doesn't, ask the user where the repo is.

Read the repo's `AGENTS.md` before proposing any edit to it.

## 3. Review in parallel

Spawn three read-only subagents in one message, one per lens in [references/lenses.md](references/lenses.md): judgment, tooling, and divergent. Build each prompt from [references/reviewer-prompt.md](references/reviewer-prompt.md), with that lens, the condensed transcript's path, and the skills repo's path. Follow [delegate to subagents](../engineering-principles/references/delegate-to-subagents.md). If you can't spawn subagents, apply the three lenses yourself, one at a time, each as a separate pass over the transcript.

## 4. Filter

Merge duplicate findings, noting which lenses raised each. Then apply [references/filter.md](references/filter.md) to every finding. Read each target file before accepting a finding against it, to check the lesson isn't already there.

## 5. Present for approval

Reply with three sections:

- **Proposed edits:** a table with a number, the problem, the proposed change, and where it goes. One row per edit, one sentence per cell.
- **Rejected:** one line each, with the reason.
- **Backlog:** lessons better enforced by a script, lint rule, or check than by prose, each with the mechanism to build.

Ask which rows to apply. The user may approve some, reject some, or redirect where one goes. Don't edit anything before they answer.

## 6. Apply the approved edits

Where a lesson goes:

- **A skill in the skills repo:** edit it under `<repo>/skills/<name>/`, never through `~/.claude/skills/` or `~/.agents/skills/`.
- **A skill's description,** when it should have triggered and didn't.
- **`<repo>/global/rules.md`:** only rules that apply to every session in every project. Keep it short.
- **Communication style:** `<repo>/global/style.md`.
- **The current project's `AGENTS.md`** (or `CLAUDE.md`, if that's what the project uses): lessons specific to that codebase.
- **A new skill:** only when the pattern recurs and no existing skill is a real home. Follow the repo's `AGENTS.md` authoring rules, including its README row.

After editing the skills repo, run `make validate` there and fix what it reports. Run `make sync` if anything in `global/` changed or a skill was added. Commit, following the global rules.

## 7. Report

- **Applied:** each file changed, with one line on what changed.
- **Backlog:** each mechanism worth building.
- **Dropped:** each rejected finding, with its reason.
