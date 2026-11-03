---
name: my-figure-it-out
description: Runs a medium-sized task that has no written implementation plan, such as a migration across many call sites or a multi-part change, by framing a checkable definition of done, capturing a baseline, and working in small verified units, then reporting results with evidence. Use when the user invokes /my-figure-it-out or $my-figure-it-out.
disable-model-invocation: true
---

# Figure it out

For a task too big to just do and too small to need a written plan: frame it, build the check first, work in small verified units, and hand back results the user can trust without redoing the work.

The task is what the user typed after the skill name, or else what the conversation is about.

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
2. Run the check against the real result, not a proxy (see "Prove it works" below).
3. Keep the change if it moved toward done, and revert it if it didn't.

Don't start the next unit until the current one passes (see "Small verifiable steps" below).

- When the same edit repeats across many places, script it rather than editing by hand (see "Script the work" below).
- When a check passes too easily, suspect the check before trusting the result.
- If you delegate units to subagents, follow "Delegate to subagents" below, and review their actual diffs and outputs, not their summaries.
- If the check itself turns out to be wrong, fix it as its own step instead of working around it.
- Note each decision as you go: what you chose, why, and the evidence.

## 4. Report

- **Done, and the result.** The definition from step 1, and the outcome for each part: **verified**, **not verified**, or **inconclusive**. Inconclusive is not a pass.
- **Evidence.** The before and after comparison, with the commands to rerun it.
- **Decisions.** The choices that shaped the work, each with its reason and evidence. Include anything tried and reverted.
- **Open.** What's left, and anything the user should check.

## Principles referred to above

### Prove it works

Before calling a task done, check the real result directly. Not a proxy, not a self-report, not "it compiles". Indirect checks (a file's modification time, a cached value, a subagent's summary, "the tests I wrote pass") feel cheaper than looking at the real thing, but acting on a wrong inference costs far more.

- Run the feature the way a user would, and look at what it actually does. Check the side effects too (files written, rows inserted, messages sent).
- Don't trust a dry-run or test mode by its name. Observe what it actually skips.
- Read the actual value, not a cached or derived copy. Review the actual diff or output of delegated work, not its summary.
- When a check fails unexpectedly, suspect the check before the system. When it passes too easily, suspect it too.
- A new check counts only after you've seen it fail on a known-bad input.

### Small verifiable steps

Break work into small steps that each end in a state you can check, and don't start the next step until the current one passes. A break caught at the step that caused it is cheap to find. A break found after a batch of changes is buried under more work.

- Put foundations first: anything that helps every later step (test setup, shared types, a baseline measurement) goes before the features that depend on it.
- In a sweep of similar edits, check each change before making the next.
- Order commits so they tell the story: a failing test, then the fix; setup, then the feature. Each commit stands on its own.

### Script the work

When work is repetitive or needs to be checkable, build the tool that does it or proves it (a script, codemod, generator, or rerunnable check) instead of doing it by hand. A script does the work the same way every time, costs nothing to rerun, and turns "trust me" into "run this".

- Do the first unit by hand to learn the recipe, then script it. Check the script by rerunning it on that unit and comparing the result.
- Make the script safe to rerun. Build the smallest script that does the job, never a framework.
- A deterministic script beats parallel agents applying the same edit by hand.
- Skip it when the change is a few obvious edits you can check at a glance.

### Delegate to subagents

Each subagent starts with nothing but its brief and returns only its report. A subagent can't ask what you meant, and it tends to report success.

- Make each brief stand alone: the goal, the scope, the worker's exact slice, how to verify its work, and what to report. Give every file it should read as an absolute path.
- Read-only by default. Give write access only to workers whose job is to change something, each with its own output location.
- Ask for a verdict with evidence: `PASS`, `ISSUES`, or `BLOCKED`. A worker that finds problems lists every one it can prove.
- A missing or incomplete result is a gap, never a pass. Rerun that worker once with the gap named; if it's still missing, report the gap.
- Check the real output, not the summary, before relying on it. Merge results into one report: one line per issue with its evidence, and explicit gaps.
- Before fanning out, ask whether a script could do the job in one pass.
