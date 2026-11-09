---
name: my-project-plan
description: Writes a milestone-by-milestone plan for any multi-step project, with or without code, detailed enough for other agents to review and for each milestone to be planned in depth later, and saves it to a file. Use when the user invokes /my-project-plan or $my-project-plan.
disable-model-invocation: true
---

# Project plan

Write a plan for a multi-step project, based on our discussion. The project may involve code, tools, configuration, documents, or people. The plan is for two readers who weren't part of the discussion: an agent reviewing it, and an agent that will later plan each milestone in more depth.

If the whole project is changes to one codebase, the [my-implementation-plan](../my-implementation-plan/SKILL.md) skill fits better. Say so and ask which the user wants.

**Where it goes.** If the user gave a path after the skill name, write the plan there. Otherwise use the location for plans that the project already has, if any, and otherwise ask where to save it. Treat anything else the user typed after the skill name as extra context for the plan.

**How to read this plan.** Open every plan with this note, so the agents that review it and plan its milestones know how settled it is:

> **How to read this plan.** Agents wrote and reviewed this plan. A person approved the direction and the decisions raised to them, not each detail. The agents settled the rest. Treat the details as working assumptions: challenge one when you find new evidence, as described under working assumptions, and don't treat it as settled because it is written here.

**Open decisions first.** Before writing, check each decision that would change the milestones, whether you discussed it with the user or with whoever briefed you:

- **Not yet discussed:** don't guess. Raise it with whoever asked for the plan, with the options, your recommendation, and what each option would change. Write the plan once it has been discussed.
- **Discussed and settled:** write it into the plan as a working assumption, with its reason. Challenge it only with new evidence: something found while doing the work, a check's result, or an outside requirement that the discussion didn't have, and that would make the assumption wrong or force a workaround. Report what you found, why it matters, and what you would do instead, and wait for an answer before changing the plan. Don't challenge it over a preference or a different taste, and don't quietly work around it.
- **Discussed and left open on purpose:** write the plan using the agreed assumed answer, and list the decision with who owns it (a team or a person), by when it has to be made (for example, before a given milestone starts), and which milestones change if the answer is different.

Where an assumption rests on something read or run, say what. Tell the reader the same rule for challenging working assumptions.

## Core principle

A plan records decisions and their reasons, not a task list. Make each milestone detailed enough that a reviewer can judge whether it's the right step, done the right way, and that an agent can plan it in depth without guessing at a decision from our discussion. Don't decide what the person doing the milestone will know better at the time.

Match the plan to the problem. Don't add goals, steps, or flexibility we didn't discuss. When you find yourself recommending something beyond the discussion, stop and ask rather than building it in.

## Sections

1. **Goal and success.** What the project is for, and what will be true when it succeeds, stated so someone could check it. "We can tell whether a prompt change made answers better or worse, with scores we trust" can be checked. "Better evals" can't.
2. **Constraints that shape decisions:** tools, access, budget, deadlines, people, and anything already fixed. Include a constraint only if it changes a choice in the plan.
3. **Decided and open.** Two separate lists, sorted as under Open decisions first. The decided list holds the working assumptions, each with one line on why. The open list holds the decisions left open on purpose, each with its owner, when it has to be made, and the milestones it changes.
4. **Milestones,** in dependency order (the structure is below).
5. **Out of scope:** what this project deliberately won't do, so reviewers don't raise it and the scope doesn't creep.

Mark each claim about a tool or system as verified (you checked it, or the docs say so), from a source (name it), or assumed. A plan that relies on a tool feature nobody checked should say so, because that's the first thing a reviewer should test.

## Milestone structure

Each milestone has the parts below. Compress a small milestone, and don't manufacture ceremony.

- **Outcome:** what exists or works when it's finished, stated so the user can confirm the direction without judging the method.
- **Approach:** the steps, the tools, and the decisions that come from our discussion, each with its reason and, where we weighed alternatives, what it was chosen over.
- **Depends on:** the earlier milestones or outside inputs it needs.
- **Done when:** evidence someone can observe or check, not "it's set up". For example: "Baseline scores exist for all 50 cases, and two people agree with the judge on at least 45 of them." (See "Prove it works" below.)
- **Risks and unknowns:** what could make this milestone fail or change shape.
- **Questions for reviewers:** where you're least sure, so a reviewer knows where to push. Leave it out if there's nothing real to ask.
- **Next level of detail:** whether the milestone needs its own detailed plan before work starts. If it involves code, that's the `my-implementation-plan` skill for this milestone. Otherwise, the `my-project-plan` skill again, scoped to this milestone.

The test for the whole plan: could a reviewer who wasn't in our discussion judge whether each milestone is the right step, and could an agent plan any milestone in depth without guessing at a decision the plan left out? If yes, it's complete. If it also dictates details the person doing the work should decide, it's over-specified.

Write the plan by the rules in the [my-technical-writing](../my-technical-writing/SKILL.md) skill: load that skill by name before writing. It will be read cold.

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
