---
name: review-adversarial
description: Adversarial code review of a diff, branch, or pull request. Parallel read-only reviewers each attack the change from a different angle (correctness and security, design, code quality), then a lead review filters their findings into Act on, Consider, Noted, and Dismissed. Use when the user asks for an adversarial, multi-angle, or stress-test review of code changes, a branch, or a pull request.
license: MIT. Adapted from pstack by Lauren Tan. See LICENSE.txt
metadata:
  source: "cursor/plugins pstack/skills/interrogate @ 12d587d"
disable-model-invocation: true
---

# Adversarial review

Spawn parallel read-only reviewers to attack a code change, then judge their findings as the lead reviewer. The deliverable is a verdict. Do not change any code, and do not post anything to the pull request.

Each reviewer gets a different lens, so their findings overlap only where a problem is real. If the environment lets you run reviewers on different models, you can spread them across models too, but don't depend on it.

## Step 1. Determine scope

- If the user names files, a diff, or a branch, review that.
- If the user names a pull request, get it with `gh pr view <number>` and `gh pr diff <number>`, or check it out with `gh pr checkout <number>` so reviewers can read the surrounding code.
- On a feature branch with no other target, review `git diff <base>...HEAD`, where `<base>` is the branch it will merge into (usually `main`).

Record how a reviewer gets the diff: the exact command, the base and head refs, and the list of changed files with line counts (`git diff --stat`). Reviewers run the command themselves. Do not paste a large diff into their prompts.

**Large changes.** If one reviewer can't read the whole diff with care (many subsystems, or thousands of changed lines), split the changed files into two or three areas along module boundaries, and run the lenses per area. Keep the total at about six reviewers. Tell the user how you split it before you spawn anyone.

## Step 2. State the intent

Write one paragraph stating what the change is meant to do. Take it from the user's message, the PR title and description, linked issues, commit messages, and the code itself. Reviewers judge the execution against this intent, never the intent itself.

If you are unsure of the intent, ask the user before continuing.

## Step 3. Spawn reviewers

Launch all reviewers in one message so they run in parallel, as read-only subagents: they read files and run read-only commands, and they edit nothing.

| Reviewer | Lens file |
|---|---|
| Correctness and security | `references/lens-correctness.md` |
| Design | `references/lens-design.md` |
| Code quality | `references/lens-code-quality.md` |

Build each prompt from `references/reviewer-prompt.md`. Fill in the intent, how to get the diff, and the absolute path of the reviewer's lens file inside this skill's folder, so the reviewer reads the lens itself. When you split a large change, add that reviewer's area and file list.

## Step 4. Synthesize

As results come back:

1. Parse every finding.
2. Merge duplicates. Different reviewers describe the same issue differently. Note which reviewers raised it.
3. Mark consensus. A finding raised independently by two or more reviewers, from different lenses, is the strongest signal.
4. Note disagreements, where one reviewer flags something another explicitly considered fine.

## Step 5. Lead judgment

You are the lead reviewer: a pragmatic senior engineer, not a neutral aggregator. Read `references/lead-judgment.md` and apply it. Check each finding against the code yourself before you keep it.

Put every finding in one bucket:

- **Act on.** Real issues affecting correctness, security, or maintainability given the actual goals. These would block a real PR.
- **Consider.** Legitimate points where you're not sure the benefit outweighs the cost right now.
- **Noted.** Technically valid but not actionable: context-dependent, premature, or low impact at this stage.
- **Dismissed.** Wrong, nitpicky, or missing context. Say why in one line.

For each finding, include which reviewers raised it, its bucket, and a one-line reason for the bucket.

## Output

### Intent
> The intent paragraph from Step 2.

### Reviewers
One line per reviewer: its lens (and area, if split) and its number of findings.

### Act on
Each finding: what's wrong with `file:line`, which reviewers raised it, and why it matters.

### Consider
Each finding: what it is, which reviewers raised it, and the tradeoff.

### Noted
A brief list.

### Dismissed
Each rejected finding with a one-line reason.

### Agreement map
Where reviewers agreed, where they diverged, and what that pattern says about the change.
