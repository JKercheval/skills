# Avoid shared mutable state

When several workers, processes, or agents might write the same thing, first ask whether they need to share it at all. Remove the sharing if you can. Add locking only when one shared target is a real requirement.

**Why:** Concurrent writes to shared state cause race conditions that are intermittent, hard to reproduce, and expensive to debug.

1. **Find the shared mutable state:** files several actors write, branches several agents push to, keys several jobs update.
2. **Default: give each actor its own target.** Separate files, keys, branches, or directories, merged only when results are read. Two workers writing their own fields into one shared JSON file still share it. Two separate files don't.
3. **If one shared target is truly required, enforce access structurally:** a lock, sequential phases, a single writer, or an atomic compare-and-swap. Instructions and conventions are not concurrency control.

Treat "we need a lock" as a prompt to check the design, not as the default answer.
