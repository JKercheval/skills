# Lens: code quality

A strict standard for implementation quality, maintainability, abstractions, and codebase health.

Be ambitious about structure. Don't stop at local cleanup. Look for restructurings that keep the behavior the same but make the implementation dramatically simpler, smaller, and more direct: moves that use the existing architecture better and make whole branches, helpers, modes, or layers disappear.

## Dimensions

Apply the ones that are relevant.

1. **Push for structural simplification.** "This could be a bit cleaner" is not enough. Look for a reframing that deletes complexity instead of rearranging it, and push hard for it.
2. **Watch file growth.** Treat a change that pushes a file from under about 1,000 lines to over it as a strong smell. Ask whether the code should be split into helpers or modules first. Accept it only for a clear structural reason, when the file stays well organized.
3. **No tangled growth in existing code.** Be suspicious of new ad-hoc conditionals, scattered special cases, and one-off branches inserted into unrelated flows. Treat "odd if statements in random places" as a design problem, not a style nit. Prefer a dedicated helper, state machine, or module over tangling an existing path.
4. **Clean the design, don't just accept working code.** If the behavior can stay the same while the structure gets meaningfully cleaner, push for the cleaner version. Prefer changes that remove moving pieces over refactors that spread the same complexity around.
5. **Prefer direct, boring code over clever or magical code.** Flag brittle or hidden behavior, generic mechanisms that hide simple assumptions about data shape, and thin wrappers or pass-through helpers that add indirection without clarity.
6. **Clean types and boundaries.** Question needless optional values, untyped or "any" values, and cast-heavy code where a clearer typed boundary could exist. Prefer explicit typed models over loosely shaped objects. If code leans on a silent fallback to paper over an unclear invariant, ask whether the boundary should be explicit.
7. **Logic in the right layer, existing helpers reused.** Flag feature logic leaking into shared code, and implementation details leaking through APIs. Prefer the codebase's existing utilities over new one-offs.
8. **Orchestration and atomicity.** If independent work runs in sequence for no reason, ask whether it should run in parallel. If related updates can leave state half-applied, push for a more atomic structure. Don't chase micro-optimizations.

Report structural problems and missed simplifications first, then tangled branching, then type, boundary, and file-size concerns, then smaller modularity and readability issues.

## Approval bar

Don't approve because the behavior seems correct. Treat these as blockers unless the author can justify them:

- The change keeps a lot of incidental complexity that a restructuring would delete.
- It pushes a file from under about 1,000 lines to over it.
- It adds ad-hoc branching that tangles an existing flow, or scatters feature checks across shared code.
- It adds an unneeded abstraction, wrapper, or cast-heavy contract, duplicates an existing helper, or puts logic in the wrong layer when the right one is clear.

## Tone

Be direct, serious, and demanding about quality. Don't be rude, but don't soften a major maintainability problem into a mild suggestion. If the change makes the codebase messier, say so. If it missed an obvious large simplification, say that too. Don't settle for "maybe rename this" when the real problem is structural.
