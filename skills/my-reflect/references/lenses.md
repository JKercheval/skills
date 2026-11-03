# Reviewer lenses

Give each reviewer one of these sections as its lens.

## Judgment

Your strength is judgment: naming the durable principle behind a specific incident, the one that saves future agents real time.

Look for:

- mistakes made, and corrections the user gave;
- the user's preferences and ways of working;
- knowledge gained about the codebase: architecture, gotchas, patterns;
- decisions and the reasons for them;
- friction in following a skill, or in delegating to subagents;
- manual steps repeated enough to automate or encode.

## Tooling

Your strength is concrete tooling detail: the command, flag, path, or quirk that a future agent would otherwise have to rediscover.

Look for:

- commands and flags the agent had to discover by trial;
- library, framework, and package-manager quirks: configuration, lock files, environment variables, version behavior;
- file and path conventions that aren't obvious from the code;
- test commands, and how to reproduce a failure locally;
- where logs land and how to capture a trace.

Also flag every moment the user supplied context the agent could have fetched itself with a connected tool or a skill: a pasted ticket title, a described CI failure, a linked thread, "this is from PR #X". For each, say what the agent should have looked up, and which skill or workflow should do it next time.

## Divergent

Your strength is the angle the other two will miss: second-order effects, what didn't happen but should have, and the lesson beneath the obvious one. If the other reviewers will probably surface lesson X, look for the lesson Y that complicates or contradicts it.

Look for:

- decisions that worked for the wrong reasons, or passed only because the test path was lucky;
- verifications that were skipped, deferred, or taken from a self-report instead of the real result;
- local fixes that missed an effect on callers or other consumers;
- design problems that a quick fix papered over;
- skills that should have been used but weren't, or were used too late;
- assumptions about scope, side effects, or what the user actually wanted.
