## Working rules

- NEVER REMOVE OR SKIP TESTS OR FUNCTIONALITY TO GET TESTS TO PASS
- Commit in small, logical commits and push after each one. Check the diff for secrets before committing.
- On any machine, including this one, never run a command that prints secret values: `printenv`, `env`, `cat .env`, or anything that dumps credentials. To check whether a variable is set, print only its name.
- Never add AI attribution to commit messages: no "Co-Authored-By" lines naming an AI, no "Generated with" footers.
- Commit messages: an imperative title under 50 characters with no trailing period, then a body saying what changed and why, in bullets when there are several changes. Don't hard-wrap lines.
- Never commit or push to `main` or `master` unless I say so or the repo's instructions allow it. If you're on one when it's time to commit, stop and ask. Never force-push.
- Never open, merge, or close pull requests, and never merge into `main`. Merging `main` into the working branch is fine.
- When merging `main` into a branch, merge the remote's latest (`origin/main`), not the local copy. Resolve only trivial conflicts, where both sides' intent is clear and compatible. For any other conflict, stop, explain what each side was trying to do, and ask.
- After a merge, run the tests before pushing.
- When a change would break existing callers, stored data, or a public API, ask whether backward compatibility is required. Don't assume either way.

## Shared infrastructure

- Treat shared systems (staging or production databases, deployed services, log systems) as read-only.
- Before any write, deploy, or job on a shared system, show the exact command and wait for my approval.

## Python

- Do not import inside functions or classes unless absolutely necessary
- always use type hints on functions, including unit tests
