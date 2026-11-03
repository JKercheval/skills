---
name: implementation-plan-execute
description: Carries out an implementation plan one milestone at a time, after listing its open questions and waiting for the user's answers, stopping for the user's review after each milestone and committing only what they approve. Use when the user invokes /implementation-plan-execute or $implementation-plan-execute.
disable-model-invocation: true
---

# Execute an implementation plan

**The plan.** If the user gave a file path after the skill name, read the plan from it. If they pasted the plan, use that. With neither, ask for it.

Work only from the plan, the code, and the documentation the plan links. Don't rely on anything you remember from earlier in the conversation: the plan is the contract, and what isn't in it has to be surfaced, not assumed.

## Review and surface (required, before any code)

Do all of the following, in order:

1. **Read the plan fully:** every milestone, its dependencies, its definition of done, and how the milestones relate. Don't read only the first milestone. Later ones constrain earlier ones.
2. **Read the codebase:** the current architecture, the patterns already in use, and the specific code each milestone will touch. The plan's statements about existing patterns are claims. Verify them against the actual code.
3. **Read the linked documentation:** anything the plan provides or references.
4. **Surface everything, sorted by who owns the decision.** Two kinds of unknowns come out of this review, and they go to different places:
   - **The user's call: ask, and wait.** Anything that affects what the system does, what users experience, what's in scope, or the order of milestones. Product and outcome questions ("should deletes be soft or hard?", "is this milestone's outcome X or Y?"), scope questions, and anything where a wrong guess produces the wrong thing rather than a worse implementation of the right thing. List these explicitly. You can't resolve them yourself: a wrong guess here is a wrong milestone.
   - **Your call: decide it yourself, and surface it only if it's consequential.** Purely technical decisions where the right answer follows from the codebase's existing patterns, the language's conventions, or the development guidelines below: which library, how to structure a module, naming, local design. Decide these against the code and don't ask about them. The exception: if a technical decision is large, irreversible, or would shape later milestones, surface it as a flagged decision with your recommendation, not an open question, so the user can confirm it quickly.

   Also surface contradictions or gaps in the plan, places where the plan conflicts with what the code actually does, and risks the plan didn't address.

**Then stop and wait.** What comes back is a review: your questions answered, your flagged decisions confirmed or redirected, possibly with more comments. Treat it as authoritative. Before implementing, check it against everything you raised. If something is still unresolved, say so and wait again rather than proceeding on an assumption. Don't start until every question that's the user's call is answered.

## Execute the milestones

One milestone at a time, fully, in dependency order.

For each milestone:

- **Re-orient** to this milestone's requirements and the code it touches. This is a focused refresh, not a re-read of everything.
- **Implement** it to the plan's specification, following the development guidelines below.
- **Test.** Write the tests the plan calls for, plus any it missed that meaningfully cover this milestone's behavior, edge cases, and error paths. Run the full suite. It must pass before the milestone is done. Later review steps assume you ran the tests and won't re-run them.
- **Check the real result.** Run the feature the way a user would and look at what it does, not only whether the tests pass (see "Prove it works" below). For an app, Claude Code's built-in `/verify` does this.
- **Report** briefly: what changed, the decisions you made on your own, and anything the user should know.
- **Stop and wait for the user's review. Leave the milestone uncommitted** so the review sees exactly this milestone's changes. When the user approves it, commit it following their commit rules, then start the next milestone.

Scale this to the milestone. A genuinely small one (an isolated config or signature change) gets a brief version of each step, not manufactured ceremony.

### Stop immediately and report if

- Tests fail in a way you can't resolve cleanly.
- The implementation would need a hack, a workaround, or something the development guidelines forbid.
- A non-trivial deviation from the plan becomes necessary.
- A change would break existing callers, stored data, or a public API in a way the plan didn't already decide.
- A question comes up that the review phase didn't surface and that's the user's call, not yours.

Stopping to report is cheaper than finishing a milestone on a wrong assumption. When in doubt, stop.

## Development guidelines

These set the bar. Match quality to what the code is: neither slogan-following nor gold-plating.

- **Design.** Architect first: prefer a clean, coherent design over incremental patching, within the plan's scope. Don't over-engineer: no speculative abstraction or flexibility for needs that aren't real yet. Removing code is fine where the plan calls for it. Breaking compatibility is not your call unless the plan decided it.
- **Architecture.** Clear module and API boundaries. Composition over inheritance. Single responsibility. Side effects isolated and explicit.
- **Code.** Follow the conventions already in this codebase, not generic ones. Descriptive names. Small, cohesive functions. Delete code you make unused instead of commenting it out.
- **Performance.** Reasonable efficiency: avoid needless allocations, repeated work, or O(n²) where O(n) is straightforward. Not a license to micro-optimize.
- **Error handling.** Fail fast with actionable messages. Explicit error types. Never put secrets in logs or error text.
- **Testing.** Test behavior, not implementation details. Cover edge cases and error paths. Keep tests deterministic. Match depth to risk: thorough where failure is costly, light where it isn't. Skip trivial tests written only for coverage.
- **Comments and rationale.** A comment says what the reader can't see in the code: an outside constraint, an invariant, or what breaks if the line changes, in one or two sentences. The rationale for a decision is one clause there ("clamp to 100: the upstream API rejects larger values"); the alternatives, the argument, and the history go in the commit message. Never narrate the change in a comment. Remove stale comments, and shrink ones that break these rules even if you didn't write them.

## Prove it works

Before calling a task done, check the real result directly. Not a proxy, not a self-report, not "it compiles". Unverified work has unknown correctness. Indirect checks (a file's modification time, a cached value, a subagent's summary, "the tests I wrote pass") feel cheaper than looking at the real thing, but acting on a wrong inference costs far more.

- Run the feature the way a user would, and look at what it actually does.
- Check the side effects too (files written, rows inserted, messages sent), not only what's visible.
- Don't trust a dry-run or test mode by its name. Observe what it actually skips: some still touch the network or write files.
- Read the actual value, not a cached or derived copy of it.
- Review the actual diff or output of delegated work, not its summary.
- When a check fails unexpectedly, suspect the check before the system. When it passes too easily, suspect it too.
- A new check, test, or validator counts only after you've seen it fail on a known-bad input. A check that has never failed may not be checking anything.
- Prefer a check you can script and rerun over a one-time look. Keep its output so a reviewer can see it.
