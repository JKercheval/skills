# Minimize reader load

Maintainability is the work a reader must do to understand the code. Track two things:

1. **Layers to trace:** how many indirections sit between a question and its answer.
2. **State to hold:** how much hidden or mutable context the reader must keep in mind.

**Why:** Code is read far more often than it is written. Line counts and complexity metrics are proxies. The two axes are independent: a flat file full of globals can be as hard to follow as a six-layer stack of adapters.

- **Collapse layers that cost more than they save:** wrappers with one caller, adapters with a single implementation, indirection that was never needed.
- **Each layer should change the abstraction.** A layer that repeats the same methods and arguments as the one below adds reading without adding meaning.
- **Prefer narrow interfaces that hide real decisions** over broad ones that hide little.
- **Shrink the scope of state:** return values over mutation, locals over fields, fields over module state, module state over globals. Derive values instead of keeping copies in sync.
- **State an invariant once, at the boundary,** not in every consumer.
- Before adding a layer or a piece of state, ask whether it removes at least as much reading somewhere else.

**The test:** can a new reader answer "where does X come from?" and "what can change X?" quickly? If not, cut layers or cut state.
