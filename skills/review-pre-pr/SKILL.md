---
name: review-pre-pr
description: Reviews a whole branch before a pull request, looking only at what emerges from the change as a whole (consistency across files, integration between new pieces, leftovers, drifted names and docs, completeness against the plan), after per-change review is done. Use when the user invokes /review-pre-pr or $review-pre-pr.
disable-model-invocation: true
---

# Pre-PR review

This is the final review before a pull request. The per-change review has already happened, usually with the [review-code](../review-code/SKILL.md) skill: issue by issue, judging each change on its own merits. This pass does what that review structurally can't. It treats the entire change as one unit. The question isn't "is each piece well designed?", which has been answered. It's "do the pieces fit together, does the change clear the quality bar this codebase holds as a whole, and is anything left in the tree that shouldn't ship?"

## What to review

After the skill name, the user may give the path of the plan the branch was built from, something narrower than the whole branch to review, or what to concentrate on.

- **By default, the whole branch:** everything on the current branch compared with `main`, plus any uncommitted changes. By PR time most of the work is committed, so a review of only the uncommitted changes would miss it.
- If the user named something narrower, after the skill name or in the conversation, review that.
- If the user gave a plan path, read the plan too, and check completeness against it (see below).

## Division of labor

The per-change review owns whether any individual change is sound: a component's own test coverage, whether a specific handler masks a problem instead of solving it, whether an abstraction is right. Don't re-examine those here. That work is done, and repeating it produces duplicate findings. This review owns only what emerges from the change as a whole and is invisible piece by piece: consistency across files, integration between new components, leftovers across the diff, names and docs that drifted during implementation, and overall completeness. Where a concern has both a per-piece slice and a whole-change slice, only the whole-change slice is yours.

## Rules

- **Don't change anything.** Don't modify code, create or edit files, commit, or open pull requests unless the user asks.
- **Don't run the test suite, linters, or type checkers,** not even to confirm a finding. They ran before the review reached you, and on a real project they're slow. To confirm a finding, run only what demonstrates that one finding: a single test, a failing input, a one-off command, or a short script.
- **Confirm every finding before you report it.** Read the actual code and cite the file and line. For a suspected bug, show it where you can: a failing input, a one-off command, a single test, or a short script. If you can't confirm a finding, still report it, labeled unconfirmed, with what would confirm it. Never drop a finding because you couldn't confirm it.

## Meet the quality bar, without over-engineering

Every change is a chance to meet a quality standard, not just to avoid lowering one. The job is to confirm the change is the best version of itself (decisions, tests, naming, documentation, and patterns all clear the bar) before it enters the permanent record.

This is not a license to over-engineer. Meeting the bar means quality appropriate to what the code is, not maximal quality for its own sake. If something already clears the bar, leave it alone. Suggesting changes without clear benefit is itself a failure to meet the bar.

## Before you start

- Identify the full change.
- Identify the main languages and the kind of code (library, CLI, web service, and so on). That shapes what "the bar" means here.
- Read the change as a whole before commenting on any single file.

For every finding, state its consequence in system or user terms (what breaks, degrades, regresses, or becomes hard to maintain), not only the mechanism.

## What to examine

### Language and ecosystem idioms

- Does this read like an experienced practitioner of this language wrote it, or like someone fluent in another language transliterating into this one?
- Where the language has a natural, established way to express something, is it used, or worked around with an awkward general-purpose construction? For example, manual index loops in a language with strong iteration constructs, or hand-rolled error plumbing where the language has idiomatic propagation. Judge by what's idiomatic for this language, not a fixed list.
- Are the standard library and established ecosystem tools used where they belong, or has something been reinvented?

### Consistency across files

- Are patterns consistent across the change: the same error handling, naming, logging, and async style from file to file?
- Does the change follow patterns already established elsewhere in the codebase, or introduce a new one without justification?
- If it introduces a new pattern, is that deliberate and worth the divergence, and is the pattern applied everywhere it now applies, rather than half-adopted?

### Integration across the change

The per-change review tested each component's own behavior. What it couldn't see is how the new pieces behave together.

- Are the integration points between new components exercised: not each component alone, but the seams where they meet?
- Do the pieces share assumptions that hold only if all of them landed together (ordering, shared state, contract expectations)? Is anything relying on that fragile across the seam?
- Is there a regression path that opens only when these changes combine, which no single-component review would surface?

### Leftovers and deferrals across the diff

Whether a particular handler masks a problem belongs to the per-change review. What's uniquely visible here is what the whole diff leaves behind.

- **Leftovers:** commented-out code, temporary scaffolding, debug prints, unused imports, dead code, vestigial parameters or return values, stale config flags, anywhere in the change.
- **Deferrals:** if something was deferred, is it acknowledged (a TODO with context, a tracked issue) rather than silently absorbed? Are the TODOs durable, or just stalling?
- **Masking across the diff:** not "is this handler a band-aid", but does a pattern of defensive additions across the change, taken together, suggest it's working around something it should have fixed directly?

### Decision rationale

- For non-obvious decisions, is the reason captured where it belongs: one clause in a comment at the line it constrains, and the rest in the commit message, the PR description, or a decision record?
- If a future maintainer asks "why is this here?" or "why this way?", does the change answer them?
- Are tradeoffs explicit, or silently absorbed?
- Flag comments that do a reviewer's job instead of a reader's: longer than the code they explain, listing alternatives considered, arguing for the choice, or narrating what the change added, removed, or replaced. Those belong in the commit message. Flag comments that restate the code.

### Names and documentation

- Do names still describe what things actually do? Names often drift during implementation.
- Are docstrings and comments still accurate, or left behind?
- Is new public-facing surface documented to the standard the codebase uses?

### Completeness and readiness

- Are there obviously related changes that should have been included but weren't, leaving the change half-done (a caller updated but not its callee, a flag added but never read)?
- Flag every change that breaks existing callers, stored data, or a public API, and say whether the plan, commit messages, or a data migration show the break was intended. Treat an unintended break as critical.
- Is new public API surface documented?
- **Against the plan, if the user gave one:** does the branch deliver what each milestone's definition of done promised (its outcomes, the tests it named, documentation updates, and known limitations resolved or recorded)? Report anything promised and missing, and anything built that the plan didn't call for.

**Out of scope. Don't raise it.** How the work is packaged for review: whether to split the change into several PRs or commits, how commits are organized, or whether the branch name describes the diff. That's the author's call. Review the code as one unit regardless of how it will ship. A coherent change that spans two unrelated features is fine. Only flag incoherence that is itself a code problem (a half-applied refactor, an unfinished integration seam), never the mere fact that distinct concerns travel together.

## What to skip

- Anything the per-change review owns: a single component's own test adequacy, a specific handler's masking, an individual abstraction's design. If a finding would be the same with the change reduced to one file, it isn't this review's job.
- Stylistic preferences without clear benefit.
- Speculative concerns about hypothetical future needs.
- Suggestions that don't actually raise the quality of this change.
- PR and commit packaging and branch naming.

## Output

Give findings in priority order, focused on what's actionable:

- **Must address before the PR:** the change doesn't clear the bar here. Shipping as-is would introduce a real regression, bug, or gap.
- **Worth considering:** improvements with clear benefit that aren't blockers. The author decides.
- **Observations:** patterns worth noting, with no action required.

For each finding, say why it matters in this specific change, not as a general principle, state its consequence rather than only its mechanism, and mark it confirmed or unconfirmed. If the change clears the bar, say so plainly. Don't manufacture findings to show diligence.
