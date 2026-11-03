# Smallest change

Get the most result from the least code and complexity.

**Why:** Every line added is a line someone has to read, test, and maintain. Adding to a complex system compounds its complexity. Removing first leaves less to reason about and often makes the next step obvious.

- **Remove before you add.** When changing a system, first delete dead code, unused paths, and redundant checks, then build on the simpler base.
- **Make the smallest diff that solves the problem.** Fewer lines beat elaborate boilerplate.
- **Build for observed needs, not speculative ones.** No options, parameters, validators, or code paths for cases that don't exist yet.
- **Every feature and option has to earn its place.** A half-finished feature is worse than a missing one.
- **Keep one source of truth for each decision.** Don't repeat the same choice in several places.
- **Question threading a new value through many layers.** If a change needs a new field passed through types, schemas, and several function signatures, look for a more direct path first.
- **Delete, don't stub.** Remove an unused reference or document rather than leaving a placeholder.

**The test:** would a maintainer find this code tiring to work with? If so, it's not the smallest good solution.

Related: [minimize reader load](minimize-reader-load.md).
