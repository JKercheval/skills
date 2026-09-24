# Lens: design

## Root causes versus symptoms

Is the code fixing the actual problem, or papering over a symptom?

Answering this usually means looking beyond the changed files. Read the callers, callees, type definitions, and sibling modules, and understand why the code exists before judging whether the change fixes the right layer.

- Guard clauses that mask a deeper broken invariant.
- Retry logic that hides a broken contract.
- Type casts that silence a modeling error.
- A workaround: why is it needed? What would a proper fix look like?
- A fix in module A that belongs in module B's contract.
- A comment saying "don't do X", or a convention someone has to remember, where a type constraint, lint rule, or runtime check could make the wrong thing impossible.

## Structural integrity

Does the code fit the system it's part of?

- Boundary discipline: is validation at system boundaries, or scattered through business logic? Validate data once where it enters the system, then trust it inside.
- Abstraction level: does the code mix high-level orchestration with low-level detail?
- Coupling: does the change add dependencies that make future changes harder?
- Data model fit: do the data structures match how the data is actually read and written? The right structure makes the code around it obvious. The wrong one fights you everywhere.
- Bolted on or integrated: was the change patched onto the existing design, or does it read as if the design always accounted for it? If the requirement had been known from the start, would the code look like this?
- Old and new paths side by side: does the change add a new API while keeping the old one alive? If nothing outside the codebase depends on the old one, callers should move and the old path should go in the same change.

Don't penalize simple code for lacking abstraction. A premature abstraction is worse than duplication.

## Complexity budget

Is the complexity justified by what the code accomplishes?

- Code that could be simpler without losing correctness or clarity.
- Abstractions that serve one call site.
- Configuration or parameters for cases that don't exist yet.
- Dead code, unused imports, leftover parameters.
- "Just in case" code paths with no current callers.
- Compatibility paths kept alive after a migration finished.
- Does the user benefit justify the complexity? Every feature, option, and setting should earn its place. A half-finished feature is worse than a missing one.

Simpler is better unless simpler is wrong. Three lines of duplication beat a premature abstraction.
