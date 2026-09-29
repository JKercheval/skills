---
name: project-plan
description: Writes a milestone-by-milestone plan for any multi-step project, with or without code, detailed enough for other agents to review and for each milestone to be planned in depth later, and saves it to a file. Use when the user types /project-plan or $project-plan.
argument-hint: "[path] [extra context]"
disable-model-invocation: true
---

# Project plan

Write a plan for a multi-step project, based on our discussion. The project may involve code, tools, configuration, documents, or people. The plan is for two readers who weren't part of the discussion: an agent reviewing it, and an agent that will later plan each milestone in more depth.

If the whole project is changes to one codebase, the user's `implementation-plan` prompt (in Tiddly) fits better. Say so and ask which the user wants.

**Where it goes.** If the user gave a file path when invoking this skill, write the plan there. Treat anything else they typed as extra context. With no path, use the location for plans that the project already has, if any, and otherwise ask where to save it.

**Open decisions first.** If the discussion left a decision open that would change the milestones, ask before writing the plan.

## Core principle

A plan records decisions and their reasons, not a task list. Make each milestone detailed enough that a reviewer can judge whether it's the right step, done the right way, and that an agent can plan it in depth without guessing at a decision from our discussion. Don't decide what the person doing the milestone will know better at the time.

Match the plan to the problem. Don't add goals, steps, or flexibility we didn't discuss. When you find yourself recommending something beyond the discussion, stop and ask rather than building it in.

## Sections

1. **Goal and success.** What the project is for, and what will be true when it succeeds, stated so someone could check it. "We can tell whether a prompt change made answers better or worse, with scores we trust" can be checked. "Better evals" can't.
2. **Constraints that shape decisions:** tools, access, budget, deadlines, people, and anything already fixed. Include a constraint only if it changes a choice in the plan.
3. **Decided and open.** Two separate lists. For each decision, one line on why. For each open question, what it blocks.
4. **Milestones,** in dependency order (the structure is below).
5. **Out of scope:** what this project deliberately won't do, so reviewers don't raise it and the scope doesn't creep.

Mark each claim about a tool or system as verified (you checked it, or the docs say so), from a source (name it), or assumed. A plan that relies on a tool feature nobody checked should say so, because that's the first thing a reviewer should test.

## Milestone structure

Each milestone has the parts below. Compress a small milestone, and don't manufacture ceremony.

- **Outcome:** what exists or works when it's finished, stated so the user can confirm the direction without judging the method.
- **Approach:** the steps, the tools, and the decisions that come from our discussion, each with its reason and, where we weighed alternatives, what it was chosen over.
- **Depends on:** the earlier milestones or outside inputs it needs.
- **Done when:** evidence someone can observe or check, not "it's set up". For example: "Baseline scores exist for all 50 cases, and two people agree with the judge on at least 45 of them." (See [prove it works](../engineering-principles/references/prove-it-works.md).)
- **Risks and unknowns:** what could make this milestone fail or change shape.
- **Questions for reviewers:** where you're least sure, so a reviewer knows where to push. Leave it out if there's nothing real to ask.
- **Next level of detail:** whether the milestone needs its own detailed plan before work starts. If it involves code, that's the user's `implementation-plan` prompt (in Tiddly) for this milestone. Otherwise, `/project-plan` again, scoped to this milestone.

The test for the whole plan: could a reviewer who wasn't in our discussion judge whether each milestone is the right step, and could an agent plan any milestone in depth without guessing at a decision the plan left out? If yes, it's complete. If it also dictates details the person doing the work should decide, it's over-specified.

Write the plan by the rules in [technical-writing](../technical-writing/SKILL.md). It will be read cold.
