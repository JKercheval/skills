# Model the domain

Get the data shape right before writing logic, and encode the domain in a data structure instead of scattering it across conditionals.

**Why:** Scattered booleans, repeated assumptions about a data shape, and branching spread across files are accidental complexity. A structure that matches the domain removes branches and makes invalid states impossible to represent. Choosing it up front is cheap. Recovering it later is a refactor that tends to get postponed.

- Define the core types first, and trace how the data will be read and written. Choose structures that fit the common paths.
- A state machine instead of several booleans or phase flags.
- A typed model instead of loose parameters or dictionaries whose shape everyone assumes.
- A lookup table, registry, or tagged union instead of if/else chains spread across files.
- A module organized around one area of knowledge, not around steps like load, validate, transform, save. Order of execution is not ownership.
- The right collection for the access pattern: a queue, cache, index, or tree.

Don't force an abstraction. Plain code is fine when the shape is already clear, local, and unlikely to grow.

**The signs you skipped this:** a new feature adds one more branch to an existing if/else chain, or a second boolean that must stay in sync with the first.

Related: [type system discipline](type-system-discipline.md).
