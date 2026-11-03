# Git history

The most complete and trustworthy source, because it's tied directly to the code: commit messages, diffs, pull request descriptions and review threads, code comments, tests, decision records, and changelogs.

## Find the commits

```bash
# Who last changed each line, and when
git blame -L <start>,<end> <file>

# The file's full history, through renames
git log --follow --oneline -- <file>

# Commits that added or removed an exact string
git log -S '<exact string from the code>' -- <file>

# Commits whose changes match a pattern
git log -G '<regex>' -- <file>

# The full message and diff of one commit
git show <hash>
```

## Read the pull requests

```bash
# The PR number is usually in the commit message, as (#1234)
git log -1 --format=%B <hash>

# The description, review comments, and linked issues
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews,files
```

The review comments are often where the real reasoning is: alternatives debated, concerns raised, a reviewer asking "why not X?".

## Look nearby

```bash
# Decision records, if the repo keeps them
rg -l -i 'decision record|architecture decision' --glob '*.md'

# Comments and TODOs near the target
rg -n -C2 '(TODO|FIXME|HACK|XXX|NOTE)' <file>

# Tests that exercise the target. Test names often state the case that motivated the code.
rg -l '<symbol>' --glob '*test*'
```

## Good evidence here

- A PR description that explains the problem, not just the change.
- A review thread where alternatives were debated.
- A comment next to the target line explaining a constraint.
- A test like `test_handles_empty_batch_after_retry` that reveals the motivating case.
- A commit message that references a ticket or incident.

## Pitfalls

- **Squash merges** lose the branch's individual commits. Rely on the PR description and comments.
- **Misleading messages.** "Small refactor" sometimes hides a deliberate behavior change. Read the diff, not just the message.
- **Copied patterns.** The author may have copied a pattern without knowing why it existed. Find where it first appeared and investigate that commit.
- **Bot commits** (dependency updates, automated backports) rarely carry a reason. Skip them.
- **The latest commit is rarely the answer.** Trace back to the commit that introduced the shape.

## Record

For each commit, PR, or comment that bears on the question: the exact quoted text, the hash, PR number, or `file:line`, the author and date, and whether it answers the question directly or only circumstantially.
