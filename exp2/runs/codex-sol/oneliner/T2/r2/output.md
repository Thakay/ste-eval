`git rebase main` uses your local `main` branch as the base for your feature branch. Git applies the changes from your three commits in their original order.

For example, suppose `main` has two new commits:

```text
Before:

A--M1--M2             main
 \
  F1--F2--F3         feature

After:

A--M1--M2            main
         \
          F1'--F2'--F3'  feature
```

`F1'`, `F2'`, and `F3'` contain your feature changes. They have new commit IDs because their position in the commit history has changed. Your feature branch now includes the changes from `main`.

You stay on your feature branch. The command does not download changes from the remote repository. If `main` has no new commits, the command can leave your branch without changes.

If Git finds a conflict, it stops. Correct the affected files. Use `git add` to mark each corrected file. Then run `git rebase --continue`. To cancel the operation and return to the previous branch state, run `git rebase --abort`.

Do not use rebase in these conditions:

- Other developers already use those commits. New commit IDs can cause problems when they combine their work with yours.
- You must keep the original commit IDs or the original branch history.

In these conditions, use `git merge main` to include changes from `main` and keep your original commits.