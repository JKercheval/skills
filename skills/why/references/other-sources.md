# Other sources

Use these when git history doesn't answer the question. Search a category only if a connected tool covers it: look at the tools and MCP servers available in this session. The examples name common products; use whichever one is connected.

## Ticket tracker (Jira, Linear, GitHub Issues)

Where product and business reasons usually live: "the customer asked for this", "this is for the compliance initiative".

1. Fetch the tickets referenced in commits and PRs first, and read each one in full, including comments.
2. Search by the feature name, key symbol, and business terms. Try several phrasings.
3. Walk up from a sub-task to its parent. Sub-tasks are tactical, and parents often hold the reason.
4. Read specs attached to the ticket or its project.
5. Check labels (`customer-request`, `incident`, `compliance`, `perf`) and milestones, which hint at the kind of motivation and its deadline.

## Documents (Confluence, Notion, Google Docs)

Where the reasoning is written out before it becomes code: design docs, RFCs, specs, postmortems.

1. Open the docs linked from PRs and tickets first.
2. Search by feature name, symbol, and error strings, and for "design", "RFC", "proposal", or "postmortem" together with the feature name.
3. Check the date: a design doc may describe a plan that changed before it shipped. Compare it with what was actually built.

## Team chat (Slack, Teams)

Where decisions get made without reaching a doc, which matters most when the PR and ticket trail is thin.

1. Search for the PR or ticket link, the feature name, and error strings, in the weeks around when the code was written.
2. Read whole threads, not single messages. The reason is often a few replies in.
3. Note who decided, not only what was said.

## Observability (Datadog, Grafana, New Relic)

For code that reacts to runtime conditions: timeouts, retries, rate limits, circuit breakers. Look for incidents, monitors, and dashboards around the date the code was added, and whether a metric changed after it shipped.

## Error tracking (Sentry, Rollbar)

For defensive code: catch blocks, null guards, retries. Look for errors whose stack traces run through the target, and whose first-seen and last-seen dates line up with the change.

## Analytics (Databricks, Snowflake, BigQuery)

For flag-gated code, experiment-driven launches, and "where did this number come from?". Look for the experiment or event data behind a threshold, and for usage before and after the change.

## Incident history

Not a separate source, but an angle to take in every source when the code looks defensive: retries, timeouts, null checks, rate limits, feature flags. Incidents often lead to defensive code ("we added this check after the outage").

- Search each source for incident and postmortem records mentioning the target file, feature, or error.
- In git, look for messages like "fix for incident", "add defensive check", or a revert followed by a re-apply.
- If you find an incident, read the whole postmortem. Its action items often map directly to code changes.
