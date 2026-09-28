---
name: why
description: Finds out why code is the way it is from the historical record (git history, pull requests, tickets, docs, chat), grading every claim by confidence and saying exactly what couldn't be found. For design rationale, history, and "why was this added", not for debugging a failure. Use when the user invokes /why or $why.
license: MIT. Adapted from pstack by Lauren Tan. See LICENSE.txt
metadata:
  source: "cursor/plugins pstack/skills/why @ 12d587d"
disable-model-invocation: true
---

# Why

Answer "why is this code like this?" from what people wrote down at the time. Code shows what it does, never why it exists.

Read [references/confidence.md](references/confidence.md) before writing the answer. Every claim gets a confidence grade, and the grade decides how the claim is worded.

## 1. Pin down the target and the question

- **The target:** a file and lines, a symbol, a feature, a threshold, or a named decision.
- **The question:** design rationale, a specific value, a tradeoff, apparently dead code, a regression, or broad history.

If the target is vague, infer it from the conversation (open files, recent edits, what was just discussed), state your reading, and proceed.

If the question contains a guess ("I assume it's for performance?"), treat the guess as one hypothesis to check against the evidence, not a conclusion to confirm.

## 2. Start with git history

Follow [references/git-history.md](references/git-history.md): blame the lines, follow the file's history through renames, search for when specific strings appeared, and read the pull requests (description and review comments) behind the commits that matter. Collect any ticket IDs, doc links, and incident references they mention.

Beware recency bias. The latest commit is often a small edit on top of the decision that explains the shape. Trace back to where the shape was introduced.

## 3. Widen only when git doesn't answer

Stop at git when it answers the question with Direct or Supported evidence (see the grades in `confidence.md`). Widen when:

- git gives no reason, only mechanics;
- the question is about product or business motivation ("why did we build this feature?");
- the commits or PRs point at tickets, docs, or incidents;
- the code looks defensive (retries, timeouts, null checks, rate limits, feature flags), so an incident may be behind it.

To widen, check which categories in [references/other-sources.md](references/other-sources.md) you have connected tools for: ticket tracker, documents, team chat, observability, error tracking, analytics. Spawn one read-only subagent per available category, all in one message so they run in parallel. Build each prompt from [references/investigator-prompt.md](references/investigator-prompt.md), with that category's section from `other-sources.md` and everything you found in git. Follow [delegate to subagents](../engineering-principles/references/delegate-to-subagents.md). Record each category you couldn't search, and why.

Read the investigators' findings yourself, merge duplicates, and keep contradictions visible. Spot-check any citation you rely on. Never invent a PR, ticket, or quote.

## 4. Answer

**For a narrow question,** the first sentence is the answer with its grade and source: "[Direct] It's capped at 100 because the upstream API rejects larger values (PR #412, description)." Then the supporting evidence, anything inferred (hedged, with the reasoning), and briefly what couldn't be found.

**For a broad investigation,** use these sections:

- **The question,** restated in a sentence or two.
- **The code:** paths, line ranges, key symbols.
- **What we found:** Direct and Supported claims, each with its citation.
- **What we can reasonably infer:** hedged claims, each with its chain of reasoning.
- **Competing hypotheses,** when the evidence fits more than one story: each with the evidence for and against.
- **What we don't know:** the specific questions left open, the searches that found nothing, and the people who would likely know.
- **Sources consulted:** one line per category, including the ones not searched and why.
- **Confidence summary:** one or two sentences.

**If the question comes before a change,** end with what the history implies for it:

- **Preserve:** what the original reasons still require.
- **Change:** what no longer applies.
- **Avoid:** what was tried before and failed.
- **Risk:** what could break if the history is misread.
