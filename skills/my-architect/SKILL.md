---
name: my-architect
description: Designs the shape of new code before implementing it. Proposes two or three genuinely different designs as real types and function signatures, starting from how callers will use them, screens them against design red flags, and recommends one with its tradeoffs and rejected alternatives. Stops for review unless asked to implement. Use when the user invokes /my-architect or $my-architect.
license: MIT. Adapted from pstack by Lauren Tan. See sources/pstack-LICENSE.txt in the skills repo
metadata:
  source: "cursor/plugins pstack/skills/architect @ 12d587d"
disable-model-invocation: true
---

# Architect

Settle the shape of new code (its types, signatures, and module boundaries) before writing the logic. Compare genuinely different designs, recommend one, and stop for review.

If the user asked to implement too ("architect and implement", "then build it"), continue to step 6 after step 5 instead of stopping.

## 1. Ground

Build a real model of the code the new design touches. Find the entry points, trace the flow, read the key types, and find the boundaries with the rest of the system. Naming files isn't grounding: know what the code does.

If the design would change who owns something or which layer does what, read the git history of that code (`git log`, `git blame`, the PRs behind the relevant commits) so the reasons for its current shape become constraints, not guesses.

Skip this step only for genuinely new code with no surrounding system.

## 2. Propose different shapes

Write two or three candidate shapes, one short paragraph each. They must differ in structure, not be variations of one idea. Real differences look like:

- where the state lives, or which module owns a decision;
- one type with flags versus separate variants;
- a call-based flow versus an event- or queue-based one;
- a small deep interface versus several shallow ones.

If the constraints leave only one viable shape, say so and why, and sketch just that one.

## 3. Sketch each shape

For each candidate, write:

- **The caller's view first:** a README-style snippet and two or three realistic call sites, showing what the caller imports, calls, and gets back.
- **Then the code shape derived from it:** types, function signatures, and module layout, with bodies that raise "not implemented" and short pseudocode for tricky logic. If the usage and the types disagree, change the types to fit the usage.

For more than a small design, spawn one subagent per candidate, all in one message so they run in parallel. Build each prompt from [references/candidate-prompt.md](references/candidate-prompt.md), with that candidate's shape paragraph, your grounding notes, a separate scratch location for its files (a temporary directory or its own git worktree), and the absolute path of the principles folder: `../my-engineering-principles/references` resolved from this skill's folder. Follow [delegate to subagents](../my-engineering-principles/references/delegate-to-subagents.md). For a small design, sketch the candidates yourself.

## 4. Screen and choose

1. Check every candidate against [references/design-red-flags.md](references/design-red-flags.md). Revise or reject shallow modules, information leakage, modules organized by execution order, and pass-through methods.
2. Compare interface depth: what complexity each public interface hides, and what it still makes callers handle. Prefer the design that hides more behind a smaller, simpler interface.
3. Pick the base design, and borrow any clearly better idea from the others. Rework each borrowed idea into the base so the result still reads as one design, rather than pasting parts together.

If the candidates all converge on the same shape, that's a strong signal: say so and use it. If they diverge wildly, the problem was under-specified. Go back to step 1.

## 5. Present, then stop

Reply with the rationale, shaped by [references/rationale-template.md](references/rationale-template.md), including the key types and signatures of the chosen design inline. Say where the full sketch files are.

Don't write the sketch into the codebase yet. Stop here for the user to review. If they push back on the shape, treat that as new grounding: revisit steps 1 to 4 rather than patching the design.

## 6. Implement against the sketch (only when asked)

Write the chosen stubs into the codebase, then replace the "not implemented" bodies with real code. The sketch is the contract.

A deviation from the sketch is a signal to surface, not friction to absorb. If a function needs a parameter the sketch didn't have, ask whether the sketch was wrong, a requirement was missed, or the implementation is overreaching.

**Scrap the design when implementation keeps fighting it.** The signal is a pattern, not a single instance:

- the same kind of workaround appearing in unrelated places;
- several unrelated edge cases each needing a special-case branch;
- types that need casts, `Any`, or optional fields that are always set in practice;
- a sudden need for a lock where the design said the state wasn't shared;
- callers needing to know the abstraction's internals to use it;
- two or more independent deviations of the same kind.

A few edge cases don't condemn a design, and complex data isn't a complex design. When you do scrap it: re-trace what's been built, redesign as if the new constraints had been known from the start, make the new sketch smaller than the old one before it grows, and return to step 2.
