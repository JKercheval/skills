---
name: technical-writing
description: Writes documents a reader will see cold, without the conversation behind them, so they understand on the first read. Covers what to say and in what order, document types, sentence rules, and PR descriptions and commit messages. Use when writing or substantially revising a README, docs, an RFC or design doc, a PR description, a commit message, a ticket, a plan, or a review write-up.
license: MIT. Sentence and document-type rules adapted from pstack by Lauren Tan. See LICENSE.txt
metadata:
  source: "cursor/plugins pstack/skills/technical-writing @ 12d587d, merged with the user's agent-to-human-explanation rules"
---

# Technical writing

Write so a tired engineer who has never seen this conversation or system understands it on the first read.

**The test:** read each sentence as someone who has never seen the system. If it only makes sense after reading the details below it, it's a label, not a sentence.

## What to say, and in what order

1. **Say what it means before how it works.** The heading and first sentence carry the meaning, and the mechanism follows. A reader who stops after the first sentence still knows the point.
2. **Name the literal thing, not an abstraction of it.** "records how far the deploy got" becomes "sends a new `stage` field: the state the deploy was in when the run ended". Watch for vague verbs such as records, captures, tracks, carries, surfaces, observes, and lands in. Replace them with the literal verb: sends, prints, sets, exits with, returns.
3. **Say which side of the line every statement is on:** before or after, problem or fix, done or proposed. State both sides in the same terms with real values: "used to send `outcome: error`, now sends `outcome: incomplete`". Any mechanism you mention (a field, an exit code, a table) says in the same sentence whether it changes.
4. **Give one concrete instance before the general rule:** a specific person, command, input, or response, then the mechanism in one sentence. If a real number or a real row exists, use it.
5. **Put the subject in the first clause.** Which command, which field: "the command caught the failure" becomes "`deploy` caught the failure".
6. **Make each heading a claim, not a label.** Reading only the headings should tell the whole story. "Deploys now retry once" is a claim; "Retry behavior" is a label. A heading can also be the question the section answers: "How many deploys actually fail?"
7. **Keep what would change how the reader understands or acts, and drop what only elaborates.** Conditions, caveats, exact wording, and a number that drives a decision stay. What did not change gets a clause, and only where the reader would otherwise worry. Move a borderline detail down a layer rather than cutting it.
8. **Never say something twice:** not in a heading and its body, not in an intro and its sections, not in prose and the table beside it.
9. **Don't narrate how you know.** "Reading the code shows", "I verified", "as established above", "to clarify", and "the takeaway is" stay out.
10. **No labels invented during the conversation.** "Park it", "finding 3", and "option B" mean nothing to a reader who wasn't there. Say what the thing is.
11. **Define a term in the sentence where it first appears,** or use the plain phrase instead.
12. **Give each thing one name, and keep it.** A document that calls one thing "the gate", "the check", and "the budget" teaches three things.
13. **Say when an example is an example,** and whether it exists in the real system. Mark a table of values that don't exist yet as illustrative.
14. **Don't smooth a real disagreement into agreement.** In a review write-up, say when a position was reversed, is still contested, or rests on a single check.
15. **Describe the current state, not its history.** When updating a doc, rewrite the section as if writing it fresh. No "no longer", "changed from", "instead of", or "we decided to". A change description (PR, commit, changelog) is the exception, because the change is its subject.

## Pick the document type first

One document, one type. Two questions pick it: does it help the reader act or understand, and is the reader learning or working?

- **Tutorial (learning by doing).** Say what the reader will build. Every step produces a visible result, and you tell them what they should see. Keep explanation to a clause and a link.
- **How-to (steps to a goal).** Solve a problem the reader has. Assume competence. Steps only, with forks where needed ("If you want X, do Y"). Name it by the task: "How to rotate the API key".
- **Reference (facts for lookup).** Describe, and only describe: facts, options, limits, errors, with no opinion. Mirror the structure of the thing described. Generate it from code where possible.
- **Explanation (understanding and why).** One bounded topic: context, design decisions, constraints, alternatives. Opinion belongs here and nowhere else.

Don't mix types. Split the document and link the parts instead.

## Sentences

- Use the word the codebase uses: the real symbol, file, flag, or command name, not a synonym or a description of it.
- Cut words that do no work. "In order to" is "to". "It is important to note that" is nothing.
- Prefer the short everyday word: "use" over "utilize", "help" over "facilitate".
- Talk to the reader as "you", in the present tense. Name who does what: "the compiler checks", not "is checked".
- Write instructions as commands. Put the condition before the instruction: "To delete the file, run `rm`." Put the common case first.
- One thought per sentence, but vary the length. Split a sentence that carries two thoughts. Keep a long sentence that carries one thought with its condition or consequence.
- Be specific: not "schema changes can cause issues" but "a column rename fails the build".
- Keep "the" and "a". "Remove backup file" reads two ways, "Remove the backup file" reads one.
- Put "only" and "not" next to the word they change.
- Break up long noun stacks: "the proto import budget check script" becomes "the script that checks the proto-import budget".
- Make every "it", "this", and "they" point at one obvious thing. Repeat the noun when in doubt.
- No em dashes or en dashes. Use a period, a comma, a colon, or parentheses instead.
- Prefer periods to semicolons.
- Headings in sentence case. Code in code font. Numbered lists for sequences, bullets for everything else, and introduce a list with a full sentence.
- Link text says where the link goes. Never "click here".
- When a rule makes a sentence worse, fix the sentence another way or leave it alone. The rules serve the reader.

## PR descriptions and commit messages

A PR description is a briefing a reviewer can read in under a minute. Always use these four headings, in this order. Leave out a section only when it would be empty:

```markdown
## <Title: the change, in a few words>

## Summary

<The change in one sentence. Then the problem it solves, with one concrete instance.>

## Changes

- <Each key change as "X now does Y instead of Z". Group by behavior, not by file.>

## Impact

<Breaking changes, new dependencies, migrations, and deployment steps, or "No breaking changes". What a reviewer or user will see differently. How it was tested, and any area that needs a careful look.>
```

- Flag anything in the diff that looks like a secret, token, or personal data, at the top.
- Expand every ticket ID, milestone label, or codename on first use. A reviewer who wasn't in the working sessions can't decode "ISSUE-123" or "Phase 2".
- Leave out background, rejected options, speculation about future work, and a list of every file. Link logs, long lists of commits, and metric tables instead of pasting them.

The same order works for a ticket intro or a TLDR: the change, the problem with one instance, "X now does Y instead of Z", what stays the same, and what a person will see differently.

A commit message follows the same rules at a smaller size: an imperative title under 50 characters with no trailing period ("Add retry to deploy", not "Added retry"), then what changed and why, in bullets when there are several changes. Don't hard-wrap lines.

## Final pass

Check the wording against [unslop](../unslop/SKILL.md): filler, hedging, chatbot phrases, and other AI-writing patterns.

## Example

Before:

> Configuration of the proto import ratchet budget script parameters is performed via budget.json. Note that it's important to remember that running with --write, which updates the committed budget to reflect the current count, should only be done when lowering it. If exceeded, CI fails.

After:

> `budget.mjs` reads the committed budget from `budget.json` and counts the files that import protos. If the count exceeds the budget, CI fails. Run `budget.mjs --write` only to lower the budget.
