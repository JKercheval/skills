---
name: blast-radius
description: Finds what a code change could break outside its own diff, and proves the one or two facts its safety depends on by running real code. Not a general code review. Use when the user asks what a change could break, for the blast radius of a change, whether a change is safe, or wants a small diff they don't trust checked before merging.
license: MIT. Adapted from pstack by Lauren Tan. See LICENSE.txt
metadata:
  source: "cursor/plugins pstack/skills/blast-radius @ 12d587d"
---

# Blast radius

Find what a change breaks somewhere else, before it ships.

Listing the callers is not the job. Anyone can search for those in seconds. The job is the breakage a search won't show you.

## Don't trust your own write-up

A blast-radius write-up that sounds right is worthless on its own, because it sounds just as convincing when it's wrong. So don't hand back only a write-up. Find the one or two facts the change's safety depends on, and prove them by running code.

For each fact the safety depends on, get it as far down this list as is cheap, and say where it stopped:

1. **You said so.** Worthless on its own.
2. **You pointed at the line.** A real `file:line`, or the library's own source.
3. **You showed the failure can't happen.** You walked the failure path step by step, and it can't be reached.
4. **You ran it.** A script or test that calls the real code and fails loudly if you're wrong.
5. **You reproduced it in the running app.**

Level 4 is usually one small script that imports the same library version the app uses and calls the exact function you're worried about.

## Steps

1. **Read the change.** Get the diff (`git diff <base>...HEAD`, or `gh pr view <number>` and `gh pr diff <number>` for a pull request) and the commit messages. List the symbols it adds, changes, and deletes, and what it now does differently, including anything the diff doesn't spell out.
2. **Find the fact it's safe because of.** Most changes that look risky are safe because of one or two facts, such as "this call only drops cache entries that are already expired, and does nothing else". Find those facts. If they hold, most of the risky cases are cleared at once. Spend your time here, not on a long list of maybes.
3. **Look where a search stops.**
   - Read the source of any library the change calls, at the version the project pins, including local patches.
   - Work out when things run: async ordering, callbacks, lifecycle hooks, teardown, retries.
   - Follow the paths a symbol search misses: the JSON an API returns, a database column, a wire or file format, another service or language reading the same data, a feature flag, and code a few hops downstream.
4. **Be honest about each risk.** Give it a realistic likelihood and a realistic cost. Keep the confirmed risks, and list the risks you checked and cleared separately. Cite a real `file:line` for every claim. A search that finds nothing is still an answer: say what you searched for. Never invent a caller or an API.
5. **Prove the key fact.** Write a script or test that runs the real code, run it, and paste what happened. Put scratch scripts in a temporary directory outside the repo. Don't change product code, and don't add files to the repo unless the user asks.
6. **For a large or wide change,** split it into areas along module boundaries, and spawn one read-only subagent per area, all in one message so they run in parallel. Each returns its risks with `file:line` evidence and its safety facts. Merge their results, and check the key facts yourself.

## What to hand back

- **What it does.** What changed, including the part that isn't obvious.
- **What it's safe because of.** The one or two facts, the level each reached on the list above, and the proof. If you couldn't prove one, write "unproven".
- **Risks.** For each: how it breaks, the `file:line`, how likely and how bad, and how to check it. Paste the proof for the ones that matter.
- **Cleared.** What you checked and why it's fine.
- **Before you merge.** The cheapest test or reproduction that would catch the real bug, including the script you wrote.

Leave out anything private before the write-up goes anywhere public, such as a pull request comment.
