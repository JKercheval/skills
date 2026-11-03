# Validate at the boundaries

Put validation, parsing, and defensive error handling where data enters the system. Inside, trust the types.

**Why:** Validation scattered through the code is noisy and redundant, and it gives false confidence. Keeping business logic out of framework and I/O code also makes it testable on its own.

- **At boundaries** (command-line arguments, config files, environment variables, network requests, external APIs, database rows): validate, parse into typed domain objects, and handle bad input explicitly.
- **Inside the system:** pass typed data, propagate errors, and don't re-validate what the boundary already checked.
- **Across a boundary:** expose domain concepts, not the transport's or storage layer's internal representation.
- Keep business logic in plain functions with no framework dependencies. The outer layer is thin and mechanical: it parses input, calls the logic, and formats output.

**The tests:**
- "Is this data crossing a boundary right now?" If not, more validation is probably redundant.
- "Could this be a plain function that the outer layer calls?" If so, extract it.
