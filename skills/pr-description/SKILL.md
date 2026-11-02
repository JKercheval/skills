---
name: pr-description
description: Writes or revises a pull request title and description that a reader with no context understands on the first read, starting with why the change exists and what it does before how. Use when the user asks for a PR description, a PR title, or a PR body, or when a pull request is about to be opened.
---

# PR description

The reader is a person deciding whether to merge, or someone who finds the PR months later. Neither was in the conversation that produced it, and the first may not read the diff, since agents review the code. The description lets them judge two things: whether the behavior is right, and whether the shape of the change is right.

Read the diff and the commits first: the PR or branch the user names, or else this branch against its base. Describe what the diff does. If it differs from what the user intended, or anything in it looks like a secret, token, or personal data, tell the user before writing; neither belongs in the PR text.

Size it to the change. A one-line fix gets two or three sentences and no headings. A small PR gets Summary only. Use the headings below where they help, and leave out any that would be empty. Include what a reviewer needs to judge the behavior and the shape of the change, and nothing that is there only to show the work was thorough.

Give the title separately from the body: the change in a few words, under about 70 characters. If the user asks for only the title or only the body, give only that.

```markdown
## Summary

- <Bullets that say what the PR does; the problem it solves, with one concrete instance; and what a person sees differently. A reader outside the project who stops here knows what this PR changes and why, at a glance. Reasons that need explaining, and obstacles met along the way, belong under How.>

## What changes

- <What a user, caller, or system can do or will see now, before and after, including a default, a limit, or a failure mode that changed. For a change with no visible effect, such as a refactor, what it makes easier.>

## How

- <The decisions a person should sign off on, each with its reason: a new abstraction or dependency, a changed contract or data shape, anything hard to reverse, and an obstacle the change ran into. Not a retelling of the code. Grouped by area, not by file.>

## Impact

<Only when there is something to say: a breaking change, a migration, a deployment step, a new dependency, or a part that was not verified. How it was tested, briefly.>
```

- Say what a person sees before what the code does, in every section. Name a selector, class, function, or value only when the reader must go there to judge the change.
- Say each thing once. How adds detail to the outcomes; it does not restate them.
- Expand every ticket ID, milestone label, or codename on first use, and link the issue the PR closes.
- Leave out speculation about future work, a list of every file, and measurements or tables a reviewer would not ask for. Mention a rejected alternative only when a reviewer would otherwise propose it.

Write the sentences by the rules in [technical-writing](../technical-writing/SKILL.md).

A Summary that does this, for a fix to how checkboxes in a list line up:

```markdown
## Summary

- In reading mode, a checkbox in a list now sits in the same column as its siblings' bullets, so a nested list reads the way the markdown says.
- Before, each checkbox sat where its text starts, one level deeper than its siblings. In the issue's example, the "Line 1" checkbox read as a child of the item above it.
- Fixes shane-kercheval/tiddly#174.
```
