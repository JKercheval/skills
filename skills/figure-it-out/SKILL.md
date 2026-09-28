---
name: figure-it-out
description: Runs a medium-sized task that has no written implementation plan, such as a migration across many call sites or a multi-part change, by framing a checkable definition of done, capturing a baseline, and working in small verified units, then reporting results with evidence. Use when the user invokes /figure-it-out or $figure-it-out.
license: MIT. Adapted from pstack by Lauren Tan. See LICENSE.txt
metadata:
  source: "cursor/plugins pstack/skills/figure-it-out @ 12d587d"
disable-model-invocation: true
---

# Figure it out

For a task too big to just do and too small to need a written plan: frame it, build the check first, work in small verified units, and hand back results the user can trust without redoing the work.

## 1. Frame

Before changing anything, read enough of the code to state:

- **Done, as a checkable statement.** Not "migrate the callers" but "every caller uses `AsyncStore`, `SyncStore` is deleted, the test suite passes, and the output snapshots match the baseline".
- **The size of the work.** Rough counts: files, call sites, units. Name any blockers the reading turned up.
- **The rigor it deserves.** Changes that are hard to reverse, or that many things depend on, get more checks. Low-stakes, reversible steps get fewer. Rigor means checks and evidence, not effort.

If the run will take hours rather than minutes, show the user this framing once and wait for a go-ahead. Otherwise, state it and start.

## 2. Build the check first

Capture the current behavior before any change: test results, output snapshots, counts, timings, whatever the definition of done compares against. The final check should read "before versus after", not "looks right".

If there's no practical way to check the result, say so now, not at the end.

## 3. Work in small units

Split the work into units that each end in a checkable state, riskiest unknown first. For each unit:

1. Make the smallest change that advances it.
2. Run the check against the real result, not a proxy (see [prove it works](../engineering-principles/references/prove-it-works.md)).
3. Keep the change if it moved toward done, and revert it if it didn't.

Don't start the next unit until the current one passes (see [small verifiable steps](../engineering-principles/references/small-verifiable-steps.md)).

- When the same edit repeats across many places, script it rather than editing by hand (see [script the work](../engineering-principles/references/script-the-work.md)).
- When a check passes too easily, suspect the check before trusting the result.
- If you delegate units to subagents, follow [delegate to subagents](../engineering-principles/references/delegate-to-subagents.md), and review their actual diffs and outputs, not their summaries.
- If the check itself turns out to be wrong, fix it as its own step instead of working around it.
- Note each decision as you go: what you chose, why, and the evidence.

## 4. Report

- **Done, and the result.** The definition from step 1, and the outcome for each part: **verified**, **not verified**, or **inconclusive**. Inconclusive is not a pass.
- **Evidence.** The before and after comparison, with the commands to rerun it.
- **Decisions.** The choices that shaped the work, each with its reason and evidence. Include anything tried and reverted.
- **Open.** What's left, and anything the user should check.
