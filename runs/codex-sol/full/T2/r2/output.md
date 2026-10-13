Suppose your feature branch contains three commits, and `main` gained a new commit after the branches separated.

Before:

```text
A---B---C             main
     \
      F1---F2---F3    feature
```

When you run `git rebase main` from your feature branch, Git:

1. Uses commit `C` as the new starting point.
2. Replays the changes from `F1`, `F2`, and `F3`, in that order.
3. Creates replacement commits with new commit IDs because their parents changed.

After:

```text
A---B---C                   main
         \
          F1'---F2'---F3'    feature
```

Your feature branch now includes the newer changes from `main`. Git does not change `main`. The history looks as if you started your feature work from commit `C`.

If Git finds a conflict, it stops. Resolve the conflict. Stage the affected files with `git add`. Then run `git rebase --continue`. Use `git rebase --abort` to cancel the rebase and restore your branch.

Here, `main` means your local branch. The command does not fetch updates from the remote.

Avoid rebase when:

- **Other developers depend on those commits.** Rewriting commit IDs can disrupt their work. Use `git merge main` unless everyone agrees to rewrite the shared history.
- **You need to preserve the branch’s merge history.** A normal rebase removes merge commits and makes the history linear.

Rebase usually suits a private feature branch. Merge usually suits shared history.

Godspeed, Spartan.