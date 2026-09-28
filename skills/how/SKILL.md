---
name: how
description: Explains how code works by tracing it, from a single function up to a whole subsystem, with parallel read-only explorers for large questions. Also answers where code should live and which module owns something. Use when the user asks how something works, wants a walkthrough of code, is about to change code they don't know, or asks where something should live or which layer owns it.
license: MIT. Adapted from pstack by Lauren Tan. See LICENSE.txt
metadata:
  source: "cursor/plugins pstack/skills/how @ 12d587d"
---

# How

Answer "how does X work?" at the level a senior engineer needs to start working in the code: a working mental model, not annotated source.

## 1. Assess the question

State your reading of the question if it's ambiguous, then proceed. The user can redirect.

- **Simple:** one function, one module, a small utility, or a narrow question ("how does `parse_config` handle defaults?"). Read the code yourself and answer. No subagents.
- **Complex:** a subsystem spanning several files or services, a cross-cutting feature, or an architectural overview. Explore in parallel first (step 2).

When in doubt, treat it as simple.

## 2. Explore in parallel (complex questions only)

Split the question into 2 to 4 angles, each a distinct slice of the subsystem. For example, for "how do runs get cancelled?": the API entry point and request handling, the cancellation state machine, and the worker side that stops execution.

Spawn one read-only subagent per angle, all in one message so they run in parallel. Build each prompt from [references/explorer-prompt.md](references/explorer-prompt.md), with the question and that explorer's angle filled in. Follow [delegate to subagents](../engineering-principles/references/delegate-to-subagents.md).

When the explorers return, reconcile their findings. Merge overlaps, and resolve contradictions by reading the code yourself. Fill gaps by reading code, not by guessing.

## 3. Answer

**If the question is specific** (yes or no, where, which, does X happen), the first sentence answers it, with the `file:line` that shows it. For example: "Yes, cancelling runs has an N+1: `cancel_runs` in `runs.py:88` loads each run separately inside the loop." The explanation follows.

**If the question is about placement** ("where should this live", "which package owns this", "is this the right layer"), end with one recommendation and the reason for it.

**For an explanation**, use these sections, and drop any that don't apply:

- **Overview.** One or two paragraphs: what this is, what it does, and why it exists. A reader who stops here should know whether to keep reading.
- **Key concepts.** The types, services, or abstractions needed to follow the rest. Brief definitions only.
- **How it works.** The longest section. What triggers it, what happens step by step, where data goes, and where the decisions are. Use prose, not pseudocode. Name the specific functions and files so the reader knows where to look. Include a code snippet only when it's essential. When several components talk to each other, or data changes shape through stages, add a diagram (Mermaid for structured flows, ASCII for simple relationships). Skip the diagram if the prose already makes the flow clear.
- **Where things live.** A short map of the files and directories someone needs to start working here.
- **Gotchas.** Surprising behavior, historical leftovers, and easy mistakes. Skip it if there's nothing worth calling out.

Say plainly what you couldn't trace or aren't sure of. Don't paper over gaps.
