---
name: my-tdd
description: Writes a failing test before changing production code, confirms it fails for the right reason, then makes the smallest fix and reruns it. Skips the new test when a good one would be impractical, and uses the closest executable check instead. Use when fixing a bug that has a cheap local test path, or when the user asks for TDD, a regression test, a failing test first, or to reproduce a bug in a test.
license: MIT. Adapted from pstack by Lauren Tan. See sources/pstack-LICENSE.txt in the skills repo
metadata:
  source: "cursor/plugins pstack/skills/tdd @ 12d587d"
---

# Test first

Make the intended behavior executable before changing production code. The goal is a focused test that fails before the change and passes after it.

This applies to bug fixes with a clear, cheap test path, and to any change where the user asks for TDD. Don't force a test when it would be impractical: if a test would need broad harness setup, brittle mocks, slow end-to-end infrastructure, production-only state, vague reproduction steps, or large unrelated fixture changes, skip the new test and use the closest useful check instead (see below).

## Workflow

1. **Understand the target.** For a bug: the intended behavior, the current behavior, the affected code path, and the smallest reproduction. For a new behavior: what a caller should observe.
2. **Choose the narrowest executable check.** Use the kind of test the project already has for that code path: unit, component, integration, or regression. If there is no practical test path, don't build one from scratch just to follow this workflow.
3. **Write the failing test.** The smallest focused test that would have caught the bug, or that pins the new behavior. It asserts what a caller observes, not how the code does it (see [test behavior, not implementation](../my-engineering-principles/references/test-behavior-not-implementation.md)).
4. **Run it before changing anything.** Confirm it fails, and fails for the intended reason. If it passes, or fails for an unrelated reason, fix the test or the reproduction before touching the implementation.
5. **Make the change.** The smallest production change that produces the intended behavior while keeping nearby contracts intact.
6. **Rerun the test.** Confirm it passes, then run the nearby tests too.

## If a failing test is impractical

Use the closest executable check instead: a targeted script, a reproduction command, browser automation, a snapshot comparison, a log assertion, or a focused integration check.

Prefer no new test over a bad test. A bad test mostly tests mocks, encodes implementation details, depends on timing or unrelated global state, needs expensive infrastructure for a small fix, or would be deleted right after proving the fix.

## Guardrails

- Don't change a test to match a wrong implementation.
- Don't weaken an existing assertion unless the expected behavior has genuinely changed, and say why.
- Keep the new test focused on this bug or behavior. Avoid broad fixture churn and unrelated coverage.
- If the bug is flaky, make the test deterministic where possible, and say which signal it locks down.
- If the bug belongs to a broader class of failures, land the focused test first, then consider tests for the siblings.

## Report

Report the evidence, not just the outcome:

- The test or check that failed before the change, and the failure it produced.
- The run that passed after the change, and any nearby tests you ran.
- If you couldn't show a failure before the change, say why, and what check you used instead.
