---
name: bro
description: Restates the agent's last message in plain language, like one person talking to another, without jargon. Use when the user types /bro or $bro after a reply that was too dense or jargon-heavy.
license: MIT. Adapted from pstack by Lauren Tan. See LICENSE.txt
metadata:
  source: "cursor/plugins pstack/skills/bro @ 12d587d"
disable-model-invocation: true
---

Restate your last message. Say it more simply and briefly, the way one person would explain it to another.

- Keep every fact, decision, and question from the original. Drop only the jargon and the padding.
- Replace terms and labels you made up during the conversation with what they refer to.
- Lead with the point.
