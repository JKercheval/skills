---
name: my-create-git-worktree
description: Creates a git worktree for a new branch in a folder next to the repo, starting from the latest remote state of a base branch (main by default), with no upstream until the first push. Use when the user invokes /my-create-git-worktree or $my-create-git-worktree.
disable-model-invocation: true
---

# Create a git worktree

Create a git worktree for a new branch. After the skill name, the user gives the new branch name, and may also give the base branch and the worktree path.

- **New branch name:** required. Ask if it is missing.
- **Base branch:** `main` when not given.
- **Worktree path:** when not given, derive it in step 3.

## Steps

1. **Fetch first, so the base is current:**

   ```
   git fetch origin
   ```

2. **Resolve the base ref.** Avoid stale local branches.
   - Prefer the remote's latest: `origin/<base>`.
   - If there's no remote branch (a local-only branch), fall back to the local branch `<base>`. In that case, make sure the latest work on it is committed, because the worktree starts from the branch's tip.

3. **Resolve the worktree path.**
   - If the user gave a path, use it exactly.
   - Otherwise use a folder next to the main repo, named `<repo folder>-<new branch>`. For example, a repo at `~/repos/myproj` and branch `ui-updates` give `~/repos/myproj-ui-updates`.
   - Never nest the worktree inside the repo: no `.claude/worktrees/`, and no path under the repo root.

4. **Create the worktree with a new branch** (`-b`). Never check out the base branch itself into the worktree, which would collide with it being checked out in the main worktree.

   ```
   git worktree add -b <new branch> <worktree path> <base ref>
   ```

5. **Leave the new branch tracking nothing,** so a bare `git push` can't target the base branch. If creating it from `origin/<base>` set an upstream, clear it:

   ```
   git branch --unset-upstream <new branch>
   ```

6. **Verify and report.** Run `git worktree list` and confirm:
   - the new worktree is at the expected path;
   - it has `<new branch>` checked out, not the base branch;
   - the branch has no upstream (`git rev-parse --abbrev-ref <new branch>@{upstream}` fails).

   Tell the user the path, and that the first push should set the upstream:

   ```
   git push -u origin <new branch>
   ```

   This session stays in the original repo. To work in the new worktree, the user opens a new session in that folder.
