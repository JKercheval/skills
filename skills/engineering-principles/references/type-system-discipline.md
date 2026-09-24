# Type system discipline

Use the type checker to rule out impossible states, mixed-up values, and unhandled cases before the code runs.

- **Make illegal states unrepresentable.** Model variants as separate types (tagged unions, sealed classes, enums with data) rather than one record with optional fields whose valid combinations live in a comment. `{done: bool, done_at: date | None}` allows `done` with no date. Derive the flag from the date, or use two variants.
- **Give meaningful primitives their own type** when two could be swapped by mistake, such as a user ID and an order ID that are both strings. Validate once where the value is created.
- **Parse external data at the boundary** into typed models (see [validate at the boundaries](validate-at-boundaries.md)).
- **Don't lie to the type checker.** Casts, `Any`, and suppression comments are latent crashes. If the checker can't prove something, validate it or improve the model.
- **Handle every variant exhaustively,** so adding a new variant makes the checker point at every place that needs a new case.
- **Derive types from the source of truth** (a schema, an API spec, a database model) instead of hand-writing a parallel type that can drift.
- **Tighten a type only where it prevents a failure.** An assertion or a "should never happen" error marks a type that is too loose. Don't make types more precise just for the sake of it.

**The tests:**
- Could you write a comment explaining which field combinations are valid? Then the type is too loose.
- Do two parameters share a primitive type but mean different things? Give them distinct types.
- If a variant is added next month, will the checker show where to handle it?
