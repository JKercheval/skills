---
name: implementation-plan-execute
description: Carries out an implementation plan one milestone at a time, after surfacing open questions, stopping for the user's review after each milestone and committing only what they approve. Use when the user types /implementation-plan-execute or $implementation-plan-execute with a plan file or pasted plan.
argument-hint: "[plan path]"
metadata:
  source: "The user's Tiddly prompt execute-implementation-plan"
disable-model-invocation: true
---

# Execute an implementation plan

**The plan.** If the user gave a file path, read the plan from it. If they pasted the plan, use that. With neither, ask for it.

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
- **Check the real result.** Run the feature the way a user would and look at what it does, not only whether the tests pass (see [prove it works](../engineering-principles/references/prove-it-works.md)). For an app, Claude Code's built-in `/verify` does this.
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
- **Comments and rationale.** Comment why, not what. Capture the reasoning behind non-obvious decisions where it will last (comments, docstrings, commit messages). Remove stale comments. No meta-commentary narrating your changes.
