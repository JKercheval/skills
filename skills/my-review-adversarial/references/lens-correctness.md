# Lens: correctness and security

## Correctness

Does the code do what the intent says it should?

- Edge cases: empty inputs, null or missing values, boundary values, concurrent access.
- Error handling: are errors caught, propagated, or silently swallowed?
- Off-by-one errors, type coercion, integer overflow, string encoding.
- State management: race conditions, stale closures, dangling references.
- Does the happy path work? Does the failure path work?
- Idempotency: what happens if an operation runs twice, or a previous run crashed halfway? If the answer is "it depends on what state was left behind", a reconciliation step is missing.
- Concurrency: if several actors can touch the same mutable state (files, branches, shared data), is access serialized by structure (locks, sequential phases, exclusive ownership), or by a convention that won't hold?

When you find a potential bug, trace the execution path. Don't just say "this could be null". Show the call chain that makes it null.

## Security

For each security finding, trace the input path through the code and show it.

- User input reaching dangerous sinks (SQL, shell, eval, HTML) without sanitization.
- Authentication or authorization gaps in new endpoints.
- Secrets in code, logs, or error messages.
- Time-of-check to time-of-use gaps in security-critical paths.

## Verification

Can you tell from reading it that this code works?

- Are there tests? Do they test behavior or implementation details?
- Would a test still pass if the code under test returned nothing? Then it checks nothing.
- If this is a bug fix, is there a test for the bug?
- If this touches an integration boundary, is the full path tested?
- Does the code check the real thing, or a proxy? Checking liveness through a file's modification time or a cached value instead of the actual state is a verification gap.
- For delegated or asynchronous work: does the code verify the actual output, or trust a self-report?
