---
name: bro
description: Rewrites the agent's last message to follow the user's communication style, in plain language, and keeps following that style for the rest of the session. Use when the user types /bro or $bro after a reply that was hard to follow, or when replies have drifted from the style.
license: MIT. Adapted from pstack by Lauren Tan. See LICENSE.txt
metadata:
  source: "cursor/plugins pstack/skills/bro @ 12d587d"
disable-model-invocation: true
---

Rewrite your last message so the user can follow it, then keep writing that way for the rest of the session.

1. Re-read the user's global instructions in full: `~/.claude/CLAUDE.md` in Claude Code, `~/.codex/AGENTS.md` in Codex. The communication style is part of that file. Read the file itself, not your memory of it. Late in a long session your memory of it has drifted, which is usually why this was invoked.
2. Rewrite your last message by those rules, the way one person would explain it to another.
   - Keep every fact, reason, condition, decision, and question from the original. Plainer does not mean shorter: most hard-to-follow replies left out context, so the rewrite often needs a definition or an example the original skipped.
   - Replace terms and labels you made up during the conversation with what they refer to.
   - Check the wording against [unslop](../unslop/SKILL.md).
3. Give only the rewrite. Don't describe what you changed.
