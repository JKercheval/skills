# Prove it works

Before calling a task done, check the real result directly. Not a proxy, not a self-report, not "it compiles".

**Why:** Unverified work has unknown correctness. Indirect checks (a file's modification time, a cached value, a subagent's summary, "the tests I wrote pass") feel cheaper than looking at the real thing, but acting on a wrong inference costs far more.

- Run the feature the way a user would, and look at what it actually does.
- Read the actual value, not a cached or derived copy of it.
- Review the actual diff or output of delegated work, not its summary.
- When a check fails unexpectedly, suspect the check before the system. When it passes too easily, suspect it too.
- A new check, test, or validator counts only after you've seen it fail on a known-bad input. A check that has never failed may not be checking anything.
- Prefer a check you can script and rerun over a one-time look (see [script the work](script-the-work.md)). Keep its output so a reviewer can see it.
