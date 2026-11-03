---
name: pr-description
description: Writes or revises a pull request title and description that a reader with no context understands on the first read, covering what the PR does and why, the decisions that shaped it, what to look at, and how it was tested. Use when the user asks for a PR description, a PR title, or a PR body, or when a pull request is about to be opened.
---

# PR description

A pull request description is a short briefing for two readers: the reviewer, who has the diff open, and whoever finds the PR months later. Neither was in the conversation that produced the change. The reviewer can read what the code does in the diff. Tell them what the change does for a person, why you made it, which choices were in question, and what to check.

## Before writing

Read the diff and the commits first. The diff is the PR or branch the user names, or else the current branch against the remote's base after a fetch, such as `origin/main`. Then check three things:

- If the diff does something that the user's request or the commit messages don't mention, tell the user before writing.
- If anything in the diff looks like a secret, a token, or personal data, tell the user before writing. None of it belongs in the PR text.
- If the diff holds unrelated changes, tell the user. If they stay in one PR, give each change its own problem and outcome under the first heading.

## Title

The title is an imperative sentence that says specifically what the PR does, in plain words. It has to stand on its own in a list of PRs. "Retry failed webhook deliveries instead of dropping them" works. "Fix webhook bug" does not. Give the title separately from the body. If the user asks for only the title or only the body, give only that.

## Body

The body has four sections, in the order below, each written as bullets. Leave out a section that has nothing to say. When a fix involved no decision and there is nothing to flag for the reviewer, skip the headings: write the problem, the change, and how you checked it as prose.

### What this PR does and why

Start with what was wrong or missing, for a reader who was not there. Then say what a person can do or see now, and anything that stops working or that a caller or operator must change. For a change with no visible effect, such as a refactor, say what it makes easier and that behavior is unchanged.

### Decisions

List the choices that were in question while the change was built, so a reader who would have chosen differently sees the reason. A choice was in question when someone proposed a different choice and the answer settled it, or when the author tried more than one approach and kept one. A question in a brief is not a proposal. A choice that was never in question doesn't belong here, however many alternatives it had. When a plan or an issue already records a decision, link it there instead of restating it.

Write each decision as one bullet that states the choice made, with a sub-bullet for the reason and for what was tried or rejected instead.

### Notes for the reviewer

Tell the reviewer where to look hardest: the part of the change where a mistake would do the most damage, and what it would break. Then say what you did not verify, and what the request or the issue asked for that this PR does not do. Leave out everything else.

### How it was tested

Say what was run, the command, and what it showed, including whether the check fails without the change. When the results are not your own, say whose they are: the commit's, CI's, or the user's. If nothing was run by anyone, say the PR is untested rather than guess. Leave out window sizes, coordinates, and timings unless the change is about them, and list a check once, not again for each width, commit, or reviewer that ran it.

Take a screenshot when the change is in how a page looks: where things sit, their size or color, or what is on the page. Record a short video only when one frame can't show the change: an animation, or a flow that goes through several screens. Otherwise a screenshot of the result is enough, and a recording adds nothing. Don't do either for a changed label, help message, or value; the reviewer reads that in the diff. For a terminal command, paste the command and its output into this section; a screenshot of text shows nothing the text doesn't. For a refactor or a backend change, the test output above is the evidence and there is nothing to capture.

Take screenshots and recordings once, when you write this description, not during the work, with the tools and commands in [capturing-evidence.md](references/capturing-evidence.md). That file also says where to save them (`.pr-evidence/<branch>/`, kept out of git) and how `gh pr create --attach` uploads them. Look at each file before you present it. Reference it in this section by its local path with alt text, as `![what it shows](.pr-evidence/<branch>/<file>)`. If a screenshot shows account details or other private data, don't reference it; say what it would have shown. If you have no tool to take screenshots with, say so here instead of skipping.

## Writing the sentences

- The title says what the PR does. The body opens with what was wrong or missing, then what a person sees now.
- Don't walk through the diff or paste the commit log. The diff shows how the code works. The Decisions section says why the change is shaped as it is.
- Write for a reader who knows the product but was not in the conversation and hasn't read the issue. Use plain words. Define a project term in the sentence where it first appears, then use it. Say in a clause what each linked issue is about.
- Expand every ticket ID, milestone label, or codename the first time it appears. Link the issue the PR closes, the PR it reverts or depends on, and the plan item it implements.
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
- Ran the worker against a local endpoint that returned 503 for two minutes and then 200. The delivery went through on the fifth attempt, and the endpoint's page listed each attempt: ![The endpoint's page listing five attempts, the last one delivered](.pr-evidence/webhook-retries/attempts.png)
```
