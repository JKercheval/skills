# Redesign from first principles

When integrating a new requirement, don't bolt it onto the existing design. Ask what you would build if the requirement had been known from the start, and move toward that.

- Read all the affected code and understand the current design first.
- Ask: "if we were writing this from scratch with this requirement, what would we build?"
- Carry the change through everything it touches: types, docs, examples, tests.
- Design the whole change, then deliver it in small verified steps (see [small verifiable steps](small-verifiable-steps.md)).

Balance this against [smallest change](smallest-change.md): redesign when the bolted-on version would leave the design harder to understand, not for every small addition.
