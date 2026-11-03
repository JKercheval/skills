## Working rules

- A rule here that says to ask me first, or not to do something unless I say so, limits what you do on your own, not what you propose. Recommend the best approach, mark the step that needs my approval, and wait for it.
- NEVER REMOVE OR SKIP TESTS OR FUNCTIONALITY TO GET TESTS TO PASS
- Commit in small, logical commits and push after each one. Check the diff for secrets before committing.
- On any machine, including this one, never run a command that prints secret values: `printenv`, `env`, `cat .env`, or anything that dumps credentials. To check whether a variable is set, print only its name.
- Never add AI attribution to commit messages: no "Co-Authored-By" lines naming an AI, no "Generated with" footers.
- Commit messages: an imperative title under 50 characters with no trailing period, then a body saying what changed and why, in bullets when there are several changes. Don't hard-wrap lines.
- Never commit or push to `main` or `master` unless I say so or the repo's instructions allow it. If you're on one when it's time to commit, stop and ask. Never force-push.
- Don't open, merge, or close a pull request, or merge into `main`, until I say so for that one. Propose it when it's the next step. Merging `main` into the working branch needs no approval.
- When merging `main` into a branch, merge the remote's latest (`origin/main`), not the local copy. Resolve only trivial conflicts, where both sides' intent is clear and compatible. For any other conflict, stop, explain what each side was trying to do, and ask.
- After a merge, run the tests before pushing.
- When a change would break existing callers, stored data, or a public API, ask whether backward compatibility is required. Don't assume either way.

## Writing

- Before writing or substantially revising a document (a README, design doc, plan, ticket, review write-up, or commit message), load the my-technical-writing skill.

## Code comments

- A comment says what a reader of this code can't see in it: an outside constraint, an invariant, or what breaks if the line changes. One or two sentences. Don't restate the code.
- Rationale for a decision is one clause in the comment ("clamp to 100: the upstream API rejects larger values"). Alternatives considered, the argument for the choice, and history belong in the commit message or PR description, never in the code.
- Never narrate the change in a comment: what was added, removed, or replaced, or which review asked for it. Git has that.
- When editing code, delete stale comments and shrink ones that break these rules, even ones you didn't write.

## Shared infrastructure

- Treat shared systems (staging or production databases, deployed services, log systems) as read-only.
- Before any write, deploy, or job on a shared system, show the exact command and wait for my approval.

## Improving the instructions

- When a skill, these rules, or a prompt led you wrong or left out something you needed, suggest the edit in your reply: the change, and the mistake it prevents.
- Never edit a skill or these global instructions unless I ask.
- Agent memory may keep a lesson, but a lesson that should change how agents work also goes in a suggestion, because memory doesn't reach other tools or machines.

## Python

- Do not import inside functions or classes unless absolutely necessary
- always use type hints on functions, including unit tests
