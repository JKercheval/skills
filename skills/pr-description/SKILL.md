---
name: pr-description
description: Writes or revises a pull request title and description that a reader with no context understands on the first read, starting with why the change exists and what it does before how. Use when the user asks for a PR description, a PR title, or a PR body, or when a pull request is about to be opened.
---

# PR description

The reader is a reviewer, or someone who finds the PR months later, who was not in the conversation that produced it. They should know what the PR changes and why from the opening, without reading the code.

Read the diff and the commits first: the PR or branch the user names, or else this branch against its base. Describe what the diff does. If it differs from what the user intended, or anything in it looks like a secret, token, or personal data, tell the user before writing; neither belongs in the PR text.

Size it to the change. A one-line fix gets two or three sentences and no headings. A small PR gets Summary and What changes as one short paragraph. Use the headings below where they help, and leave out any that would be empty.

Give the title separately from the body: the change in a few words, under about 70 characters. If the user asks for only the title or only the body, give only that.

```markdown
## Summary

<A reader who stops here knows what this PR changes and why, in words someone outside the project would follow. The spirit is "replaces X with Z because Y", not that sentence: a one-line fix gets one sentence, a change like a model migration gets a short paragraph that names what is replaced, what replaces it, and the reason. Reasons that need explaining, and obstacles met along the way, belong under How.>

## What changes

- <What a user, caller, or system can do or will see now, before and after. For a change with no visible effect, such as a refactor, what it makes easier.>

## How

- <Only what a reviewer can't get from the outcomes or the diff: a decision and its reason, a contract or data shape that changed, an obstacle the change ran into. Grouped by area, not by file.>

## Impact

<Only when there is something to say: a breaking change, a migration, a deployment step, a new dependency, or a part that was not verified. How it was tested, briefly.>
```

- Say each thing once. How adds detail to the outcomes; it does not restate them.
- Expand every ticket ID, milestone label, or codename on first use, and link the issue the PR closes.
- Leave out speculation about future work and a list of every file. Mention a rejected alternative only when a reviewer would otherwise propose it.

Write the sentences by the rules in [technical-writing](../technical-writing/SKILL.md).
