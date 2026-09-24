# Migrate callers, then delete the old API

When a new internal API replaces an old one, and nothing outside the codebase depends on the old one, move every caller and delete the old API in the same change. Don't keep both.

**Why:** Keeping old and new side by side doubles the paths to understand and test. Temporary adapters tend to become permanent, and the codebase starts to feel append-only.

- List the callers, migrate them, and delete the old API.
- Update tests to check the new contract. Delete tests that only protected the old implementation.
- A temporary adapter is the exception. Give it a clear removal point.

**Doesn't apply** when outside users depend on the old API: a published library, a public HTTP API, a shared database schema. Those need a deprecation path.
