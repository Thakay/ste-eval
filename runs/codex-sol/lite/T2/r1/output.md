On your feature branch, `git rebase main` replays your three commits on top of your local `main`.

Suppose `main` gained two commits after you created your branch:

```text
Before:

A---B---C              main
 \
  F1---F2---F3          feature

After:

A---B---C              main
         \
          F1'---F2'---F3'  feature
```

Git applies the changes from `F1`, `F2`, and `F3` after `C`, in order. The new commits get different IDs because their parent history changed. Your feature branch now points to `F3'`. The `main` branch stays at `C`. Rebase does not create a merge commit.

If a commit causes a conflict, Git pauses. To continue:

1. Resolve the conflicts in the affected files.
2. Stage those files with `git add`.
3. Run `git rebase --continue`.

If you want to cancel, run `git rebase --abort`. Git restores your branch to its state before the rebase.

Rebase works well for cleaning up your own feature branch before sharing it. Do not rebase commits that teammates already use unless everyone agrees to coordinate the history change. Their work can still refer to the old commits.

If you must preserve existing commit IDs or merge history, use `git merge main` instead.

If `main` has not advanced, a normal rebase usually makes no changes. The command uses your local `main`; it does not download remote updates.

Godspeed, Spartan.