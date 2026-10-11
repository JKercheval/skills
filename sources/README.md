# Upstream skill sources

Other people's skill repos are good raw material, but their skills fit their tools and habits. This folder tracks which upstream repos have been reviewed, up to which commit, and what was decided about each skill.

Each upstream repo gets one ledger file, such as `pstack.md`, with:

- The repo URL and the path of the skills inside it.
- The last reviewed commit: full SHA and date. Use the SHA to find what changed. The date is a fallback if upstream rewrites history.
- One row per upstream skill: its decision (`port`, `adapt`, `skip`, or `undecided`), the reason, and the local skill name if ported.

## Reviewing an upstream repo

1. Clone or update the repo into a scratch folder, not into this repo.
2. Read the ledger's last reviewed SHA. List what changed since then:

   ```bash
   git log --oneline <last-sha>..HEAD -- <skills-path>
   git diff --stat <last-sha>..HEAD -- <skills-path>
   ```

   On the first review, every skill is new.
3. For each new or changed skill, read the whole `SKILL.md` and the files it references. Judge it against the selection criteria below.
4. Present a short triage to the user: new skills, changed skills that were ported earlier (and whether the change matters for the local copy), and a recommended decision for each. Don't port anything before the user agrees.
5. Update the ledger: the decisions, and the new last reviewed SHA and date.

## Porting a skill

Porting means rewriting for this repo, not copying.

- Strip tool-specific mechanics. Replace them with tool-neutral instructions, or with the Claude Code and Codex equivalents (see the table below).
- Strip the upstream author's personal preferences unless the user shares them: writing style bans, naming habits, their company's services and tools.
- Keep the core idea and the steps that make the skill work. Cut everything else.
- Replace references to other upstream skills with relative file links to local skills. If the referenced skill isn't ported, inline the one or two sentences that matter or drop the reference.
- Rewrite the description to the rules in `AGENTS.md`.
- Rename a joke or metaphor name to a plain one that says what the skill does: `interrogate` became `review-adversarial`.
- Merge two upstream skills only when they serve the same situation. Shared steps or overlapping content don't justify a merge or a skip: compare what the user is doing, the result they want, the size of the task, and whether they approve a plan first. Handle overlapping content with a link.
- When porting a skill from a review already in the ledger, check out the ledger's last reviewed SHA in the scratch clone, so you port the version that was reviewed.
- Credit the source in `metadata`, for example `metadata: {source: "cursor/plugins pstack/skills/how @ 12d587d"}`. If the upstream license requires it (MIT does), keep one copy of its license file in `sources/` as `<repo>-LICENSE.txt` (for example `sources/pstack-LICENSE.txt`), and add a `license:` line to the skill naming the source and that file.
- Add the skill's row to the README's Skills table.
- Run `make validate`, then test the skill as `AGENTS.md` describes.
- Update the ledger row: the decision, what changed from upstream, and what was tested (which tools, and whether it was a trigger check or a real task).

| Upstream mechanic | Local replacement |
|---|---|
| Cursor `Task` tool, `subagent_type: generalPurpose`, `readonly: true` | "Spawn a read-only subagent" |
| `AskQuestion` | "Ask the user" (Claude Code has `AskUserQuestion`, Codex asks in chat) |
| Routing roles to GPT or Grok models | Claude Code and Codex subagents can't mix vendors. Vary the reviewer's prompt or angle instead, or call another CLI from the shell if the user wants cross-vendor review |
| `~/.cursor/...` paths, `.mdc` rules | Drop, or use `~/.claude/` and `~/.codex/` equivalents |
| `~/.cursor/projects/<slug>/agent-transcripts/` | Claude Code: `~/.claude/projects/<slug>/*.jsonl`. Codex: `~/.codex/sessions/` |
| Cursor built-in `create-skill` | Claude Code `skill-creator`, Codex `$skill-creator` |

## Selection criteria (draft, the user should edit this)

What the user wants:

- Skills that work in both Claude Code and Codex.
- One mechanism that works the same way in both tools, over a tool-specific feature that needs per-machine setup.
- General engineering practice: verification, root-causing, design before code, clear writing, tests that check behavior.
- Python first. Skills tied to TypeScript, React, Electron, or iOS only if the user asks.

What the user doesn't want:

- Skills that open, merge, or close PRs, merge into `main`, or post to chat on their own. Committing and pushing to a working branch is fine (see `global/rules.md`).
- One author's personal style presented as a rule.
- Skills that only work with a big company's tool stack (Slack bots, Datadog, Sentry, analytics warehouses) or a specific vendor's platform.
- Heavy multi-agent orchestration where one careful agent would do.

Not decided yet:

- Which skills belong in the separate Clerk (work) setup instead of here.
