---
name: my-review-code
description: Reviews a code change in one pass for design flaws, architectural problems, code smells, and bugs, confirming each finding against the code before reporting it. Reviews uncommitted changes by default, then the branch. Use when the user invokes /my-review-code or $my-review-code.
disable-model-invocation: true
---

# Code review

This is an architectural and code-quality review, not a line-by-line review of style. Focus on decisions with lasting impact on structure, maintainability, and correctness. Find fundamental design flaws, architectural anti-patterns, structural issues, code smells, and actual bugs. Ignore minor style and formatting.

## What to review

If the user said what to review, after the skill name or in the conversation, review that, and concentrate on anything they asked you to. Otherwise, in order:

1. Uncommitted changes in the current directory.
2. If there are none, the current branch's changes compared with `main`.
3. If neither applies, ask.

## Rules

- **Don't change anything.** Don't modify code, create or edit files, commit, or open pull requests unless the user asks.
- **Don't run the test suite, linters, or type checkers,** not even to confirm a finding. They ran before the review reached you, and on a real project they're slow. To confirm a finding, run only what demonstrates that one finding: a single test, a failing input, a one-off command, or a short script.
- **Confirm every finding before you report it.** Read the actual code path and cite the file and line. For a suspected bug, show it where you can: run a failing input, a one-off command, a single test, or a short script that proves the behavior. A design finding is confirmed by pointing at the code that shows the problem. If you can't confirm a finding, still report it, labeled unconfirmed, with what would confirm it. Never drop a finding because you couldn't confirm it.

## Review lenses

These are thinking tools, not a checklist. Apply the ones that surface real issues for this code. A lens with nothing to say is not a gap in the review. For every issue, state its consequence in system or user terms (what breaks, degrades, or becomes hard to change), not only the mechanism. The mechanism explains it to an engineer. The consequence is what makes it worth raising, and it's what readers later rely on.

- **Design fundamentals.** Does each component have one clear responsibility? Can behavior be extended without modifying existing code? Do high-level modules depend on abstractions rather than implementations? Are interfaces focused rather than forcing unnecessary dependencies? Are abstractions at the right level, exposing only what's necessary with clear contracts?
- **Coupling and cohesion.** Are modules loosely coupled with clear boundaries? Is related functionality grouped together? Can components be tested, modified, or replaced independently? Which changes would ripple across several components, and who owns which lifecycle?
- **State and side effects.** Is state management explicit and controlled? Are side effects isolated and predictable? Does this create or modify global state inappropriately? Is mutability used where immutability would be safer?
- **Error handling and resilience.** Are error conditions handled, or do they fail silently? Do errors propagate clearly? Are failure modes considered, with recovery or cleanup where needed? What breaks, and how does it surface?
- **Compatibility.** Flag every change that breaks existing callers, stored data, or a public API, and say whether the plan, commit messages, or a data migration show the break was intended. Treat an unintended break as critical.
- **Test adequacy.** Do the tests exercise the behavior that matters: core paths, the edge cases and error conditions the code is exposed to, and the failure modes found under the other lenses? Where is coverage missing on something risky, and where is it present but shallow (the happy path asserted, the hard cases untested)? Name the specific high-value tests that are missing, the ones that would catch a real defect or a likely regression, rather than listing every untested function. Trivial, well-bounded code doesn't need tests called out. Risky or central code with weak tests does.
- **Ecosystem integration.** How do established libraries in this space solve this? What's idiomatic, and what fights the ecosystem? Does this invent conventions where conventions exist, or conflict with common user setups?
- **Performance and scalability.** Are there O(n²) algorithms where O(n) is feasible? Will this pattern bottleneck under load? Are connections, memory, and threads managed appropriately? Do costs scale reasonably with usage? Be specific: "holds the full result set in memory, so it fails past about N rows", not "might not scale".

### Code-level hygiene

An architectural focus doesn't mean skipping low-level issues. A code smell that points to a design problem or a latent bug is worth raising: it compounds over time and is cheap to fix early. Examples, not a checklist: functions whose return value every caller discards, dead parameters threaded through call sites but never read, duplicated logic that has subtly diverged, names that suggest different behavior than what happens, catch blocks that silently swallow context, functions quietly handling several unrelated concerns. Use judgment to spot patterns that smell wrong even if they aren't listed.

### Latent assumptions

For anything not obviously correct, ask what it assumes and whether that will hold as the system changes. What assumptions could become problems later? If this fails or needs to change, what else is affected?

## Depth

**Go deep on** core abstractions and boundaries, global state and lifecycle management, public APIs and contracts, error paths and failure modes, the points where the code meets its ecosystem, and patterns that repeat across the codebase. A repeated good pattern is worth affirming so it's preserved. A repeated bad one is worth naming once as systemic, not flagging every instance.

**Skim past** formatting and style that don't affect correctness, well-understood standard patterns used correctly, and isolated internal logic that is clearly correct and well-bounded.

## What to raise

**Raise it if** it would be expensive to change later but is trivial to address now, it will push future decisions in a bad direction, it violates a principle that matters in this context, it conflicts with common ecosystem usage, it introduces a bug or an error-prone pattern, a code smell points to a design issue or latent bug, or a clearly better alternative exists.

**Skip it if** it's a stylistic preference without a clear advantage, "could be done differently" without a meaningful benefit, a micro-optimization without demonstrated need, or personal taste on a subjective matter.

When you raise an issue, include the recommended alternative: criticism plus direction, not criticism alone.

## Reporting

Lead with what matters most. Group everything about one issue together. If a bug and a design concern share a root cause, address them together rather than splitting them. Don't repeat an issue across sections.

A complete review accounts for, but isn't rigidly templated by: what works well (strong patterns worth preserving or extending), critical issues (fundamental problems that need to change, each with its recommended alternative), design concerns (questionable patterns worth discussing even if not clearly wrong), code smells, actual bugs, and the context that explains why an issue matters here specifically. Mark each finding as confirmed or unconfirmed. Organize all of this however serves clarity. The goal is a useful review, not a filled-in template. Leave out categories that have nothing substantive behind them rather than padding to cover each one.
