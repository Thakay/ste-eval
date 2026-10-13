When you run `git rebase main` on your feature branch, Git:

1. Finds the common commit between your feature branch and `main`.
2. Uses the last commit on your local `main` branch as the new starting point.
3. Applies the changes from your 3 feature commits, one at a time, in their original order.

This usually creates 3 new commits with new commit IDs. Your feature branch now includes the changes from `main`, followed by your changes. The `main` branch does not change. This command does not get updates from the remote repository.

If Git finds a conflict, it stops. Correct the files, use `git add`, then run `git rebase --continue`. To cancel the operation, run `git rebase --abort`.

Do not use rebase when other developers have used your commits as the basis for their work. The new commit IDs can cause problems when you combine the branches. Use `git merge main` instead.

Also, do not use rebase if your team must keep the original commit history.