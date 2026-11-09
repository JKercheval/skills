---
name: my-implementation-plan
description: Writes a milestone-by-milestone implementation plan, based on the current discussion, for an AI coding agent that wasn't part of it, and saves it to a file. Use when the user invokes /my-implementation-plan or $my-implementation-plan, after the approach has been agreed in conversation.
disable-model-invocation: true
---

# Implementation plan

Write a detailed implementation plan for an AI coding agent, based on our discussion.

**Where it goes.** If the user gave a path after the skill name, write the plan there. Otherwise use the repo's existing location for plans if it has one, and otherwise ask where to save it. Treat anything else the user typed after the skill name as extra context for the plan.

**Two readers.** The plan has two readers, and each section is written for one of them. The approver knows the domain but not the engineering work, and confirms or corrects the direction. The implementer is a coding agent that will read the relevant code before acting but was not in this conversation.

**Open decisions first.** Before writing, check each decision that would change the milestones, whether you discussed it with the user or with whoever briefed you:

- **Not yet discussed:** don't guess. Raise it with whoever asked for the plan, with the options, your recommendation, and what each option would change. Write the plan once it has been discussed.
- **Discussed and settled:** write it into the plan as a working assumption, with its reason. Challenge it only with new evidence: something found in the code, a test result, or an outside requirement that the discussion didn't have, and that would make the assumption wrong or force a workaround. Report what you found, why it matters, and what you would do instead, and wait for an answer before changing the plan. Don't challenge it over a preference or a different design taste, and don't quietly build around it.
- **Discussed and left open on purpose:** write the plan using the agreed assumed answer, and list the decision at the top of the plan with who owns it (a team or a person), by when it has to be made (for example, before a given milestone starts, before merging, or before production), and which milestones change if the answer is different.

Where an assumption rests on something read or run, say what. Tell the implementer the same rule for challenging working assumptions.

## Core principle

Match complexity to the problem: neither over-engineered nor under-built. Account for error handling, edge cases, and testing to the degree the problem requires. Don't add speculative features, abstractions, or flexibility that wasn't discussed and isn't yet needed. When you find yourself recommending something beyond what we discussed, stop and ask rather than building it in.

If the cleanest design breaks existing callers, stored data, or a public API, say so in the plan and ask whether backward compatibility is required. Don't decide it silently. A breaking change that serves the discussed goal can be right. One that serves an imagined future goal is the over-engineering this principle forbids.

## Plan construction

- Break the work into milestones, each a single coherent piece of work, ordered by dependency. Each milestone ends with the build passing, the existing tests passing, and its own tests passing, so it can be reviewed and committed on its own. It need not finish the feature end to end.
- Establish shared patterns, interfaces, and conventions in the earliest milestone that needs them, and state them explicitly so later milestones reuse them rather than reinvent them. A plan where milestone 4 invents a parallel pattern to milestone 2 has failed.
- Explain what changes and why: goals and rationale, not just mechanics. Make the rationale for non-obvious decisions explicit in the plan, and say where it must survive: one clause in a code comment at the line it constrains, and the rest in the commit message, the PR description, or a decision record in the form the repo already uses. Never a paragraph of justification in the code.
- If the plan rests on a claim about how the system behaves today (a diagnosis, a bottleneck, a cause), say whether it was verified by running and how, or that it is unverified and what would verify it.
- List the documentation URLs we discussed or that you found relevant, and state that the implementer must read them before starting.
- When the plan says to add something to an existing place (a table, a list, a schedule, a config file, a document), open that place first and confirm it can take the new thing. Say in the plan what you found there that the plan depends on. A place the plan names without opening is a guess.
- Write it by the rules in the [my-technical-writing](../my-technical-writing/SKILL.md) skill: load that skill by name before writing. If you don't have that skill, write for a reader who starts cold: define each term where it first appears, and say what a thing does for a person before what the code does.

## Milestone structure

Each milestone has the three parts below. If a milestone is genuinely small (an isolated config or signature change, for example), compress it and say so briefly. Don't manufacture ceremony.

1. **Goal and outcome.** For the approver. The overall objective, then a bullet list of functional outcomes: what the user or system can do once the milestone is complete. This is how the approver checks the plan: by confirming the outcomes are right, not by auditing implementation choices. Implementation soundness is delegated to the implementer.

2. **Implementation outline.** For the implementer. What changes, in what order, and why.

   Transmit every decision that depends on our discussion and can't be recovered from the codebase: the chosen approach (and what it was chosen over, if we weighed alternatives), component boundaries, the contract or interface each piece exposes, sequencing where order matters, and the specific edge cases or constraints we identified. These are decided. If they're missing, the implementer will guess, and may guess wrong.

   Don't specify what the implementer will get right by reading the code: naming, local structure, which existing helper to reuse, or how to match surrounding patterns and style. Dictating those bloats the plan and overrides judgment better made against the actual code. Trust the code review step.

   Include a code snippet only where a contract or non-obvious pattern is clearer shown than described. Never a full implementation. The test for this section: could the implementer, having read the relevant code but not this conversation, implement the milestone as intended (same approach, same boundaries, same contracts) without guessing at any decision that depends on the discussion? If yes, it's complete. If it specifies more than that, it's over-specified.

3. **Definition of done.** For both readers. What "done" means beyond "the code runs": the specific unit and integration tests to write (core behavior, edge cases, and error conditions), the documentation to update, and any known limitations, either resolved or explicitly recorded. Include how to check the real result, not only the tests, by the rules in "Prove it works" below: state those rules once in the plan, and list in each milestone only that milestone's checks. Match test depth to risk: thorough where failure is costly, light where it isn't. Prefer tests that catch a real failure to tests written for the count.

## Prove it works

The definition of done tells the implementer to check the real result directly before calling a task done. Not a proxy, not a self-report, not "it compiles". Unverified work has unknown correctness. Indirect checks (a file's modification time, a cached value, a subagent's summary, "the tests I wrote pass") feel cheaper than looking at the real thing, but acting on a wrong inference costs far more. The rules the plan passes on:

- Run the feature the way a user would, and look at what it actually does.
- Check the side effects too (files written, rows inserted, messages sent), not only what's visible. Check an outward effect (a message, an email, a write to a shared system) against a test double or a sandbox; never trigger a real one without asking.
- Don't trust a dry-run or test mode by its name. Observe what it actually skips: some still touch the network or write files.
- Read the actual value, not a cached or derived copy of it.
- Review the actual diff or output of delegated work, not its summary.
- When a check fails unexpectedly, suspect the check before the system. When it passes too easily, suspect it too.
- A new check, test, or validator counts only after you've seen it fail on a known-bad input. A check that has never failed may not be checking anything.
- A check of new behavior says what wrong result it would catch, and its expected value comes from somewhere other than the result: the spec, a known input with a known correct answer, or the input itself. A check that only compares parts of one output with each other (a total against the sum of its lines) catches inconsistency, not wrongness, so it does not stand alone. For a change meant to preserve behavior, the earlier output is the right expected value. For anything else, an earlier output counts as correct only after it was checked independently of the code that produced it: by a person, or against a reference implementation.
- Prefer a check you can script and rerun over a one-time look. Keep the command and the lines that show its result in the report so a reviewer can see it.
