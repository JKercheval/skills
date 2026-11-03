---
name: my-review-cross-check
description: Checks another reviewer's findings on a change you already reviewed, confirming or refuting each one against the code, giving your own severity, and saying whether your own findings still stand. Use when the user invokes /my-review-cross-check or $my-review-cross-check.
disable-model-invocation: true
---

# Cross-check another reviewer's findings

You reviewed a change, and now you have another reviewer's findings on the same change, usually forwarded, with the orchestrator's questions after them. Your reply goes to an orchestrator who settles the findings for an engineer and doesn't read code. Nobody in this conversation will act on the findings; the change's author does that. So your reply says what is true, how you know, and how much each finding matters, and leaves out what an implementer would need.

**The findings.** Use the report forwarded or pasted in this message or earlier in this conversation. With none, ask.

**Don't change anything.** Don't modify code, create or edit files, commit, or write to GitHub. Don't run the test suite, linters, or type checkers. To check a finding, run only what shows that one finding: a single test, a one-off command, or a short script kept outside the repo folder and deleted afterwards.

## Two failure modes, equally bad

1. **Defending your own review.** Keeping a finding or a severity because you wrote it. A fact the other reviewer established is evidence against your findings as much as for them.
2. **Rubber-stamping the other reviewer.** Accepting a point because it is stated with confidence. Reviews by AI agents contain real mistakes, overreach, and misjudged severity.

Weigh each point on its merits, not on who raised it.

## Check each of the other reviewer's findings

Take them in the order given. For each one:

- **Verdict:** Confirmed, Refuted, or Couldn't check. Confirmed and Refuted cite the file and line, or the command and what it printed. Couldn't check says what would settle it. Never drop a finding because you couldn't check it.
- **Severity:** critical, major, or minor, with the reason in system or user terms: what happens, to whom, and how often. When yours differs from the other reviewer's, say what the difference rests on.
- **Overlap:** whether it duplicates one of your own findings, and which.

Keep each one short. Describe a fix only when the other reviewer's proposed fix is wrong or incomplete; the author chooses the fix.

## Answer the orchestrator's questions

The questions follow the forwarded report. Each is a disagreement between the two reviews or a fact a severity depends on. Answer each with evidence. When the answer depends on something outside the code, such as who reads a channel or whether a feature is released, say what it depends on and who would know.

## Revisit your own findings

Go through every finding in your own review, in its order. Each one stands, changes severity (from what, to what, and why), or is withdrawn (why). Add any finding the other review showed you missed, marked as new.

## What to send back

1. The other reviewer's findings, each with its verdict, your severity, and its overlap with yours.
2. The answers to the questions.
3. Your own findings, each with its status.
4. What you read and ran, with the commands, and for any other repository the commit you read it at.

Never quote a credential (a token, an API key, a password, a connection string with credentials), even one that looks like a test value.
