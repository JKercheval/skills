---
name: my-requirements-doc
description: Drafts a requirements-and-proposal document for a build with design unknowns, the document that comes before any implementation plan. Covers its structure, the four-part template for each design problem, and keeping who-said-what out of the body. Use when starting a project that needs design decisions, when preparing the agenda for a design conversation, or when an existing plan has become a pile of context-free warnings.
---

# Requirements documents

A requirements document answers, in order: what we need, what exists today, what sits between the two, and what has to be decided to close the gap. A person takes it into a design conversation, so every section has to be followable by a reader with no context from the session that wrote it.

## When to write one

- Before any implementation plan, whenever the build has real design unknowns. A milestone plan written first has no home for design problems, so each one lands as a warning bolted onto a milestone, and the plan becomes unreadable after a review pass or two.
- Skip it when the work is fully specified and the only questions are about sequencing. A plan alone is enough then.

## Structure

1. **Purpose and status.** One or two lines: what the document is for, who it's headed to, and which of its claims are verified.
2. **What we need and why.** The goal in plain language, plus the constraints that shape the design. How we got here goes in the appendix.
3. **The requirements.** The things being built, each with a plain-language definition (a table works well), followed by the conditions each must meet to count as done.
4. **What exists today.** The relevant systems, tables, and events, each in a sentence or two with its gap named. Unverified claims are labelled where they appear.
5. **What we propose to build.** The chosen shape in a paragraph, the alternatives considered and why each was rejected, and a plain description of how it works.
6. **The problems to solve.** The core of the document: one subsection per problem, each in four parts.
   - **What the problem is,** as the section title, in a full sentence: "Churn is invisible in the raw data, because 'stopped paying' has no row."
   - **What goes wrong if it's ignored:** the concrete wrong number or behavior, walked through.
   - **What we know:** established facts and prior work, with their verification status.
   - **What to decide:** the open choice, the default proposal, and the tests that would show it handled.
7. **Open design questions,** numbered so a conversation can refer to them, each with the owner of the decision.
8. **Sequence, and what happens meanwhile:** the order of work, and what explicitly does not wait on it.
9. **Appendix: background and sources.**

## Rules

- **Keep dialogue out of the body.** Never justify a claim by who said it. "X asked for" and quoted remarks read as spec to a later reader, who then builds around what may have been an offhand comment. State what is needed and why on the merits. A person's name appears in the body only as the owner of a decision or dependency.
- **Put provenance in the appendix:** where the mandate came from, quotes, meeting and chat references, and links to the findings that carry per-claim sources.
- **Organize by what the reader needs, not by when things were found.** Fold review findings into the problem section they belong to. If folding one in makes the document harder to read, restructure the document instead of appending a warning.
- **Name silent failures.** Say when a mistake produces a plausible wrong number instead of an error, because that is what makes a problem need a written decision and a test.
- **Give every problem a default proposal.** An open choice with no proposed answer pushes the whole design into the meeting.
- **Write in a technical register.** Use declarative headings, bullets for parallel facts, and numbered lists for procedures. A multi-sentence explanation opens with a bold one-line claim followed by its support.

## Lifecycle

- **While drafting,** keep the document wherever the project lives and edit it in place.
- **When other people need to comment,** move it to wherever the project's shared docs live (the company docs tool, or the repo's docs folder or an issue for open source) and delete the draft copy. Two near-identical copies drift as soon as either is edited. After the move, edit only the shared copy.
- **Moving it to a shared tool is an external write,** and the document goes out under the user's name, so it needs the user's go-ahead and review first.
- **A plan written from a published requirements document transcribes it, never recalls it.** Check each decision the plan restates against the published text, and cite where it came from. Plans restated from memory drift toward simpler rules that produce plausible wrong results.
- **Once the design decisions are recorded,** the requirements document stops changing, and any implementation plan is written after it and references it.
