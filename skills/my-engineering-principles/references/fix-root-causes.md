# Fix root causes

When debugging, trace each problem to its cause and fix it there, not where the symptom shows up.

**Why:** Symptom fixes accumulate. Each workaround makes the system harder to reason about, and the real bug stays.

- **Reproduce the reported failure** with a command you can rerun, and check that it fails with the symptom that was reported, not a different one nearby. Reading the code first is often how you learn to reproduce it. A fix you haven't shown working against a reproduction is a guess, so say when a fix is unconfirmed.
- **When the cause isn't clear, shrink the reproduction.** Remove inputs, steps, and configuration while it still fails, so that everything left is needed for the failure.
- **Ask "why" until you reach the cause.**
- **When the cause isn't obvious, name more than one possible cause before testing any,** and say what you would see if each were true. A cause with no prediction can't be tested.
- **Don't add a guard just to silence a failure,** such as a null check that hides a crash. Find out why the value is null.
- **A workaround that needs a long comment to justify it** usually means the code is wrong. Fix the code.
- **Look for the pattern, not just the instance.** Search for the same mistake elsewhere and fix every occurrence.
- **When stuck, add instrumentation instead of guessing:** logging, the full error, a debugger.
- **If it fails only sometimes,** find a way to make it fail more often, such as repeating the trigger, adding load, or narrowing the timing. A rare failure can't show whether a fix worked.
- **If something fails only after a restart,** suspect stale persistent state first: caches, lock files, config, saved state.
- **If two or more fixes built on the same assumption have failed,** stop fixing. Write the assumption down and test it directly before trying another fix.
