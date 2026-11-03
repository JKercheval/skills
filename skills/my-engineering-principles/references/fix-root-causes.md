# Fix root causes

When debugging, trace each problem to its cause and fix it there, not where the symptom shows up.

**Why:** Symptom fixes accumulate. Each workaround makes the system harder to reason about, and the real bug stays.

- **Reproduce first.** A fix you can't show working against a reproduction is a guess.
- **Ask "why" until you reach the cause.**
- **Don't add a guard just to silence a failure,** such as a null check that hides a crash. Find out why the value is null.
- **A workaround that needs a long comment to justify it** usually means the code is wrong. Fix the code.
- **Look for the pattern, not just the instance.** Search for the same mistake elsewhere and fix every occurrence.
- **When stuck, add instrumentation instead of guessing:** logging, the full error, a debugger.
- **If something fails only after a restart,** suspect stale persistent state first: caches, lock files, config, saved state.
- **If two or more fixes built on the same assumption have failed,** stop fixing. Write the assumption down and test it directly before trying another fix.
