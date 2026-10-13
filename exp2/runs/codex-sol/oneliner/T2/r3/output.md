Assume that your feature branch has three commits that are not on `main`: `F1`, `F2`, and `F3`.

If `main` has new commits, `git rebase main` does these steps:

1. Uses the last commit on `main` as the new starting point.
2. Applies the changes from `F1`, then `F2`, then `F3`.
3. Moves your feature branch to the last new commit.

The replacement commits have new commit IDs. Your feature branch now includes the changes from `main` and your three commits. The `main` branch does not change.

The command uses your **local** `main` branch. It does not get new commits from the remote repository.

If a conflict occurs, Git stops. Correct the files, run `git add <file>`, then run `git rebase --continue`. Use `git rebase --abort` to return to the state before the rebase.

Do not use rebase in these conditions:

- Other developers use your commits as the starting point for their work, unless you agree on how to update their branches.
- You must keep the original commit IDs or the original branch history.

In these conditions, use `git merge main`. It keeps the existing commits. Rebase is useful for a private feature branch before you share its commits.