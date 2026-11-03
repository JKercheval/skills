# Candidate prompt template

Build each candidate subagent's prompt from the text below the line, filling in the placeholders.

---

You are sketching one candidate design for a new piece of code. Other subagents are sketching genuinely different shapes in parallel. Develop yours as well as it can be done. Don't hedge toward a safe middle: the differences between candidates are what make the comparison useful.

## The problem

{PROBLEM}

## Grounding

What the surrounding code does, and the constraints the design must respect:

{GROUNDING_NOTES}

## Your shape

{SHAPE_PARAGRAPH}

## Where to write

Write your files only in `{SCRATCH_DIR}`. Don't edit the project's files.

## What to produce

1. **The caller's view, first.** A README-style snippet and two or three realistic call sites: what the caller imports, what they call, and what comes back.
2. **The code shape, derived from that usage.** Types, function signatures, and module layout. Bodies raise "not implemented". Use short pseudocode for tricky logic, and a docstring or comment stating each function's intent and invariants. A reader should be able to trace data from input to output from the types and signatures alone. If the usage and the types disagree, change the types.
3. **A short rationale:** the key decisions, what the public interface hides and what it still exposes to callers, the tradeoffs you accept, and anything you're unsure of.

## Design discipline

Read these principle files and apply the ones that fit:

- `{PRINCIPLES_DIR}/model-the-domain.md`: get the data shape right first, and trace each main access pattern through it.
- `{PRINCIPLES_DIR}/type-system-discipline.md`: encode invariants in types rather than runtime checks or comments.
- `{PRINCIPLES_DIR}/validate-at-boundaries.md`: parse external data into domain types at the boundary, and keep transport or storage types off the public interface.
- `{PRINCIPLES_DIR}/avoid-shared-mutable-state.md`: if two actors could write the same thing, give each its own state.
- `{PRINCIPLES_DIR}/make-operations-idempotent.md`: ask what happens if an operation runs twice or crashes halfway.
- `{PRINCIPLES_DIR}/minimize-reader-load.md`: prefer a small interface that hides real complexity, and short call chains.

Keep one source of truth for each invariant, and derive values instead of keeping copies in sync.
