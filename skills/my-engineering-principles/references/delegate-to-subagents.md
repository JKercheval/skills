# Delegate to subagents

When work is split across subagents, each one starts with nothing but its brief and returns only its report. Write the brief so it can't be misread, and treat the report as a claim to check.

**Why:** A subagent can't ask what you meant, and it tends to report success. A vague brief produces work on the wrong thing, and a trusted summary hides work that wasn't done.

- **Make each brief stand alone:** the goal, the scope, the worker's exact slice, how to verify its work, and what to report. Include the facts it needs, such as the commit or files to use, rather than assuming it knows them. Give every file it should read as an absolute path: a relative link in a skill's files means nothing inside a subagent's prompt.
- **Read-only by default.** Give write access only to workers whose job is to change something, and give each writer its own output location: a separate file, directory, branch, or worktree (see [avoid shared mutable state](avoid-shared-mutable-state.md)).
- **Ask for a verdict with evidence:** `PASS`, `ISSUES`, or `BLOCKED`. A worker that finds problems lists every one it can prove, not just the first.
- **A missing or incomplete result is a gap, never a pass.** If a report lacks what the brief required, rerun that worker once with the gap named. If it's still missing, report the gap.
- **Check the real output, not the summary.** Read the diff, the file, or the command output a worker produced before relying on it (see [prove it works](prove-it-works.md)).
- **Merge the results into one report:** a compact table, one line per issue with its evidence, and explicit gaps. Don't paste raw worker output.

**Before fanning out,** ask whether a script could do the job in one pass. A deterministic script beats parallel agents doing the same thing by hand (see [script the work](script-the-work.md)).
