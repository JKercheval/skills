---
name: my-technical-writing
description: Writes documents a reader will see cold, without the conversation behind them, so they understand on the first read. Adds what only documents need (the cold-reader test, document types, current state over history, and commit, ticket, and TLDR formats) to the writing rules in the global instructions. Use when writing or substantially revising a README, docs, an RFC or design doc, a commit message, a ticket, a plan, or a review write-up. For PR titles and descriptions, use my-pr-description.
license: MIT. Sentence and document-type rules adapted from pstack by Lauren Tan. See sources/pstack-LICENSE.txt in the skills repo
metadata:
  source: "cursor/plugins pstack/skills/my-technical-writing @ 12d587d, merged with the user's agent-to-human-explanation rules"
---

# Technical writing

The writing rules in your global instructions, under "How to write", apply to every document. This skill adds what only documents need.

**The test:** read each sentence as someone who has never seen this conversation or the system. If it only makes sense after reading the details below it, it's a label, not a sentence.

## Pick the document type first

One document, one type. Two questions pick it: does it help the reader act or understand, and is the reader learning or working?

- **Tutorial (learning by doing).** Say what the reader will build. Every step produces a visible result, and you tell them what they should see. Keep explanation to a clause and a link.
- **How-to (steps to a goal).** Solve a problem the reader has. Assume competence. Steps only, with forks where needed ("If you want X, do Y"). Name it by the task: "How to rotate the API key".
- **Reference (facts for lookup).** Describe, and only describe: facts, options, limits, errors, with no opinion. Mirror the structure of the thing described. Generate it from code where possible.
- **Explanation (understanding and why).** One bounded topic: context, design decisions, constraints, alternatives. Opinion belongs here and nowhere else.

Don't mix types. Split the document and link the parts instead.

## Rules only documents need

- Describe the current state, not its history. When updating a doc, rewrite the section as if writing it fresh: no "no longer", "changed from", "instead of", or "we decided to". A change description (PR, commit, changelog) is the exception, because the change is its subject.
- Talk to the reader as "you", in the present tense.
- Write instructions as commands. Put the condition before the instruction: "To delete the file, run `rm`." Put the common case first.
- Mark a table of values that don't exist yet as illustrative.

## Commit messages, tickets, and TLDRs

A commit message: an imperative title under 50 characters with no trailing period ("Add retry to deploy", not "Added retry"), then what changed and why, in bullets when there are several changes. Don't hard-wrap lines.

A ticket intro or a TLDR goes in this order: the change, the problem with one concrete instance, "X now does Y instead of Z", what stays the same, and what a person will see differently.

## Final pass

Reread the finished document against "How to write" in the global instructions, as the unslop skill does.

## Example

Before:

> Configuration of the proto import ratchet budget script parameters is performed via budget.json. Note that it's important to remember that running with --write, which updates the committed budget to reflect the current count, should only be done when lowering it. If exceeded, CI fails.

After:

> `budget.mjs` reads the committed budget from `budget.json` and counts the files that import protos. If the count exceeds the budget, CI fails. Run `budget.mjs --write` only to lower the budget.
