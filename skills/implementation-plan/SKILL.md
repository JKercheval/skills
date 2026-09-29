---
name: implementation-plan
description: Writes a milestone-by-milestone implementation plan, based on the current discussion, for an AI coding agent that wasn't part of it, and saves it to a file. Use when the user types /implementation-plan or $implementation-plan, usually after the approach has been agreed in conversation or with /architect.
argument-hint: "[path] [extra context]"
metadata:
  source: "The user's Tiddly prompt implementation-plan-instructions"
disable-model-invocation: true
---

# Implementation plan

Write a detailed implementation plan for an AI coding agent, based on our discussion.

**Where it goes.** If the user gave a file path when invoking this skill, write the plan there. Treat anything else they typed as extra context for the plan. With no path, use the repo's existing location for plans if it has one, and otherwise ask where to save it.

**Open decisions first.** If the discussion left a decision open that would change the milestones, ask before writing the plan. List any remaining open decisions at the top of the plan, separate from what's decided.

## Core principle

Match complexity to the problem: neither over-engineered nor under-built. Account for error handling, edge cases, and testing because the problem requires them. Don't add speculative features, abstractions, or flexibility that wasn't discussed and isn't yet needed. When you find yourself recommending something beyond what we discussed, stop and ask rather than building it in.

If the cleanest design breaks existing callers, stored data, or a public API, say so in the plan and ask whether backward compatibility is required. Don't decide it silently. A breaking change that serves the discussed goal can be right. One that serves an imagined future goal is the over-engineering this principle forbids. When the two pull against each other, "matched to the problem" wins.

## Plan construction

- Break the work into milestones, each covering a single coherent component or module, ordered by dependency.
- Establish shared patterns, interfaces, and conventions in the earliest milestone that needs them, and state them explicitly so later milestones reuse them rather than reinvent them. A plan where milestone 4 invents a parallel pattern to milestone 2 has failed.
- Explain what changes and why: goals and rationale, not just mechanics. Make the rationale for non-obvious decisions explicit in the plan, and say it must survive into the code (comments, docstrings, ADRs, or commit messages) rather than evaporate during implementation.
- List the documentation URLs we discussed or that you found relevant, and state that the implementing agent must read them before starting.
- The plan is read cold by an agent that wasn't in this conversation. Write it by the rules in [technical-writing](../technical-writing/SKILL.md).

## Milestone structure

Each milestone has the three parts below. If a milestone is genuinely small (an isolated config or signature change, for example), compress it and say so briefly. Don't manufacture ceremony.

1. **Goal and outcome.** The overall objective, then a bullet list of functional outcomes: what the user or system can do once the milestone is complete. This is the main alignment mechanism. The reader validates the plan by confirming the outcomes are right, not by auditing implementation choices. Write it so someone who knows the domain but not the engineering work can confirm or correct the direction. Implementation soundness is delegated to the implementing agent.

2. **Implementation outline.** What changes, in what order, and why. This section is a handoff to an agent that will read the relevant code before acting but wasn't part of this conversation. Calibrate to exactly that reader.

   Transmit every decision that depends on our discussion and can't be recovered from the codebase: the chosen approach (and what it was chosen over, if we weighed alternatives), component boundaries, the contract or interface each piece exposes, sequencing where order is load-bearing, and the specific edge cases or constraints we identified. These are the planner's decisions. If they're missing, the agent will guess, and may guess wrong.

   Don't specify what the agent will get right by reading the code: naming, local structure, which existing helper to reuse, or how to match surrounding patterns and style. Dictating those bloats the plan and overrides judgment better made against the actual code. Trust the code review step.

   Include a code snippet only where a contract or non-obvious pattern is clearer shown than described. Never a full implementation. The test for this section: could a competent agent, having read the relevant code but not this conversation, implement the milestone as intended (same approach, same boundaries, same contracts) without guessing at any decision that depends on the discussion? If yes, it's complete. If it specifies more than that, it's over-specified.

3. **Definition of done.** What "done" means beyond "the code runs": the specific unit and integration tests to write (core behavior, edge cases, and error conditions), the documentation to update, and any known limitations, either resolved or explicitly recorded. Include how to check the real result, not only the tests (see [prove it works](../engineering-principles/references/prove-it-works.md)). Match test depth to risk: thorough where failure is costly, light where it isn't. Prefer meaningful tests to coverage theater.
