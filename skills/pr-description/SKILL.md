---
name: pr-description
description: Writes or revises a pull request title and description that a reader with no context understands on the first read, covering what the PR does and why, the decisions that shaped it, what to look at, and how it was tested. Use when the user asks for a PR description, a PR title, or a PR body, or when a pull request is about to be opened.
---

# PR description

A pull request description is a short briefing for two readers: the reviewer, who has the diff open, and whoever finds the PR months later. Neither was in the conversation that produced the change. The diff shows what the code does. The description says what the change does for a person, why it was made, which decisions shaped it, and what the reviewer should check.

## Before writing

Read the diff and the commits first. The diff is the PR or branch the user names, or else the current branch against its base. Then check three things:

- If the diff does something that the user's request or the commit messages don't mention, tell the user before writing.
- If anything in the diff looks like a secret, a token, or personal data, tell the user before writing. None of it belongs in the PR text.
- If the diff holds unrelated changes, tell the user. If they stay in one PR, give each change its own problem and outcome under the first heading.

## Title

The title is an imperative sentence that says specifically what the PR does, in plain words. It has to stand on its own in a list of PRs. "Retry failed webhook deliveries instead of dropping them" works. "Fix webhook bug" does not. Give the title separately from the body. If the user asks for only the title or only the body, give only that.

## Body

The body has four sections, in the order below, each written as bullets. Leave out a section that has nothing to say. A fix that involved no decision and has nothing to flag gets no headings at all: write the problem, the change, and how it was checked as prose.

### What this PR does and why

Start with what was wrong or missing, for a reader who was not there. Then say what a person can do or see now, and anything that stops working or that a caller or operator must change. For a change with no visible effect, such as a refactor, say what it makes easier and that behavior is unchanged.

### Decisions

List the choices that were in question while the change was built, so a reader who would have chosen differently sees the reason. A choice was in question when one of three things happened: someone asked about it and the answer settled it, the plan or the issue settled it, or the author tried more than one approach and kept one. A choice that was never in question doesn't belong here, however many alternatives it had.

Write each decision as one bullet that states the choice made, with a sub-bullet for the reason and for what was tried or rejected instead.

### Notes for the reviewer

Include only what changes how the reviewer reads the diff: the part where a mistake would matter most and what it would break, anything that was not verified, and anything the request or the issue asked for that this PR doesn't do.

### How it was tested

Say what was run, the command, and what it showed, including whether the check fails without the change. When the results are not your own, say whose they are: the commit's, CI's, or the user's. If nothing was run, say the PR is untested rather than guess.

A capture is evidence only when the diff can't show what a person sees: a layout or a position, motion, a flow across several screens, or how a page renders. A change to text or a value that the diff shows whole, such as a help message or a label, gets no capture; the diff is the evidence. When a capture is needed, it is a screenshot of the state that changed, or a short recording when the change is a flow that one still image can't show. Make it with the browser or terminal tool you have, look at it before you present it, and keep it out of the repository in a folder the description names. Reference each capture in the description by its local path with alt text, as `![what it shows](path)`, so that opening the PR with `gh pr create --attach <path>` uploads it in place. A capture that shows account details or other private data is not attached; say so instead. For a change with nothing to see, such as a refactor or a backend change, the tests and their output are the evidence. [capturing-evidence.md](references/capturing-evidence.md) lists the tools and the attach command.

## Writing the sentences

- The title says what the PR does. The body opens with what was wrong or missing, then what a person sees now.
- Don't walk through the diff or paste the commit log. The diff shows how the code works. The Decisions section says why the change is shaped as it is.
- Write for a reader who knows the product but was not in the conversation and hasn't read the issue. Use plain words. Define a project term in the sentence where it first appears, then use it. Say in a clause what each linked issue is about.
- Expand every ticket ID, milestone label, or codename the first time it appears. Link the issue the PR closes, and the PR it reverts or depends on.
- Leave out speculation about future work, a list of every file, and any measurement other than the ones the change set out to move.
- Follow the rules in [technical-writing](../technical-writing/SKILL.md) for every sentence.

## Example

A made-up PR for a web app that sends webhook events to customers' servers.

Title: Retry failed webhook deliveries instead of dropping them

Body:

```markdown
## What this PR does and why

- When a customer's endpoint was down, even for a few seconds, each event was sent once and then dropped. Customers found out from missing data, and support re-sent events by hand from the admin console.
- A delivery that fails now retries for up to 24 hours, with the gap between attempts doubling from 30 seconds to a maximum of one hour. After that it is marked dead and listed on the endpoint's page with a Retry button.
- Operators must run this PR's migration before deploying it, because the worker reads the two new columns on every delivery.

## Decisions

- Retries stop after 24 hours instead of continuing until the endpoint recovers.
  - Without a cutoff, every customer who deleted their server but not their endpoint would build a backlog that grows forever. A dead delivery can still be retried by hand from the endpoint's page.
- A response with a 4xx status other than 408 or 429 is not retried.
  - The endpoint rejected the request, so sending it again gives the same answer. The issue asked for retries on any failure; this PR narrows that, and the issue now says so.
- Retry state lives in two new columns on the deliveries table, not in a separate retry queue.
  - Both were tried. A separate queue was a second place to look when a delivery went missing, and the deliveries table already has the index on endpoint and time that the worker's query needs.

## Notes for the reviewer

- The worker's claim query, which picks the next deliveries to send, is where a mistake would matter most: two workers claiming the same row would send a customer a duplicate event. It uses `FOR UPDATE SKIP LOCKED`; the transaction boundary around it is the thing to check.
- Not verified: what happens when the database becomes unreachable in the middle of a retry. The worker logs the error and exits, and what the supervisor does after that was not tested.
- The issue also asked for a per-endpoint retry limit. This PR uses one limit for every endpoint and does not add the setting.

## How it was tested

- `make test` passes, with 14 new tests in `test/webhooks/retry_test.py` for the backoff schedule, the 24-hour cutoff, the 4xx rule, and two workers claiming at once.
- Without the change, the two-workers test fails with a duplicate delivery, and the cutoff test fails because the delivery is never marked dead.
- Ran the worker against a local endpoint that returned 503 for two minutes and then 200. The delivery went through on the fifth attempt, and the endpoint's page listed each attempt: `![The endpoint's page listing five attempts, the last one delivered](evidence/webhook-retries/attempts.png)`.
```
