# Git Conflict Resolution Guide

This document outlines the process for identifying and resolving Git conflicts that may occur during `merge`, `rebase`, or `cherry-pick` operations.

## Identifying Conflicts

Git marks conflicts directly within the affected files using conflict markers:

```diff
<<<<<<< HEAD
# Code from the current branch (HEAD)
print("Hello from current branch")
=======
# Code from the incoming branch
print("Hello from incoming branch")
>>>>>>> incoming-branch-name
```

**Commands to identify conflicted files:**

*   `git status`: Lists files with unmerged paths.
*   `git diff`: Shows the conflict markers and differences in detail.

## Resolving Conflicts

The goal is to edit the conflicted file(s) to contain the final desired code, removing the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).

**Methods:**

1.  **Manual Editing:**
    *   Open the conflicted file(s) in an editor.
    *   Locate the conflict markers.
    *   Decide which code block to keep (HEAD, incoming, or a combination/modification of both).
    *   Delete the unwanted code block(s) and the conflict markers.
    *   Save the file.

2.  **Using Merge Strategies (Choosing one side entirely):**
    *   To keep the version from the *current* branch (where the merge/rebase was initiated):
        ```bash
        git checkout --ours path/to/conflicted/file.ext
        ```
    *   To keep the version from the *incoming* branch:
        ```bash
        git checkout --theirs path/to/conflicted/file.ext
        ```
    *   **Note:** After using `checkout --ours/--theirs`, the file is automatically staged.

3.  **Using Merge Tools:**
    *   Configure and use a visual merge tool:
        ```bash
        git mergetool
        ```
    *   Follow the tool's instructions to resolve conflicts.

## Completing the Operation

After resolving conflicts in *all* affected files:

1.  **Stage the resolved files:**
    ```bash
    git add path/to/resolved/file.ext
    # Repeat for all resolved files (or use git add .)
    ```
    *(Skip this step if you used `git checkout --ours/--theirs`)*

2.  **Continue the original operation:**
    *   If merging: `git merge --continue`
    *   If rebasing: `git rebase --continue`
    *   If cherry-picking: `git cherry-pick --continue`

## Aborting Operations

If conflicts are too complex or you wish to abandon the operation:

*   Abort merge: `git merge --abort`
*   Abort rebase: `git rebase --abort`
*   Abort cherry-pick: `git cherry-pick --abort`

This will return the repository to the state it was in before the operation began.

## Git Manager Usage

*   **Attempt Simple Resolution:** For straightforward conflicts (e.g., choosing one version over another), use `git checkout --ours/--theirs` or manual editing, followed by `git add` and `--continue`.
*   **Escalate Complex Conflicts:** If conflicts involve intricate code changes, require domain knowledge, or are numerous, **abort** the operation (`--abort`) and escalate to the user or a relevant specialist. Do not attempt complex resolutions automatically.
*   **Log Actions:** Clearly log whether conflicts were encountered, how they were resolved (or if aborted), and the final outcome.