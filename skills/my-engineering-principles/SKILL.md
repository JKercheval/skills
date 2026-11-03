---
name: my-engineering-principles
description: Index of short engineering principles for design, simplicity, verification, debugging, and testing, with one reference file per principle. Use when the user asks to apply engineering principles or best practices, or when another skill links to a principle.
license: MIT. Adapted from pstack by Lauren Tan. See sources/pstack-LICENSE.txt in the skills repo
metadata:
  source: "cursor/plugins pstack/skills/principle-* @ 12d587d"
disable-model-invocation: true
---

# Engineering principles

Each principle is one short file in `references/`. Read the file in full before applying a principle; the one-line summaries below are only for choosing. When a principle changes a decision, say which principle and what it changed.

## Simplicity

- [Smallest change](references/smallest-change.md). Sizing a change, or tempted to add options, layers, or abstractions. Remove before adding, and build only for observed needs.
- [Minimize reader load](references/minimize-reader-load.md). Shaping or reviewing code that is hard to follow. Cut layers of indirection and shrink the scope of state.
- [Script the work](references/script-the-work.md). Repetitive or hard-to-check work. Build a script or check that does or proves it, instead of working by hand.

## Design

- [Model the domain](references/model-the-domain.md). Before writing logic, or when branching keeps growing. Get the data shape right, and encode the domain in a structure instead of scattered conditionals.
- [Redesign from first principles](references/redesign-from-first-principles.md). Adding a requirement to an existing design. Build what you would have built had it been known from the start.
- [Design it twice](references/design-it-twice.md). A decision with no precedent. Compare two or three genuinely different approaches before committing.
- [Validate at the boundaries](references/validate-at-boundaries.md). Wiring validation or error handling. Validate where data enters, trust types inside, keep business logic free of framework code.
- [Type system discipline](references/type-system-discipline.md). Designing types or signatures. Make illegal states unrepresentable and don't lie to the type checker.
- [Make operations idempotent](references/make-operations-idempotent.md). Operations that can crash, retry, or restart. Rerunning must reach the same end state.
- [Avoid shared mutable state](references/avoid-shared-mutable-state.md). Several workers or agents that could write the same thing. Remove the sharing before adding locks.
- [Migrate callers, then delete the old API](references/migrate-callers-then-delete.md). Replacing an internal API that nothing outside the codebase uses. Move every caller and delete the old one in the same change.

## Verification and debugging

- [Prove it works](references/prove-it-works.md). Before calling anything done. Check the real result, not a proxy or a summary.
- [Fix root causes](references/fix-root-causes.md). Debugging. Reproduce first, fix the cause rather than the symptom, and question the shared assumption after repeated failed fixes.
- [Small verifiable steps](references/small-verifiable-steps.md). Multi-step work. Check each step before starting the next, and order commits so they tell the story.
- [Test behavior, not implementation](references/test-behavior-not-implementation.md). Writing or keeping a test. Assert observable results against literal expected values.
- [Delegate to subagents](references/delegate-to-subagents.md). Splitting work across subagents. Write briefs that stand alone, ask for a verdict with evidence, and treat a missing result as a gap, not a pass.
- [Encode lessons in structure](references/encode-lessons-in-structure.md). The same correction coming up twice. Turn it into a type, lint rule, test, or script instead of another instruction.
