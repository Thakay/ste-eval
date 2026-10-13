Running `git rebase main` while you are on your feature branch tells Git: **reapply my feature commits on top of `main`.**

Suppose your feature has three commits, `A`, `B`, and `C`, and `main` has gained two commits since you branched:

```text
Before:
O---D---E           main
 \
  A---B---C         feature

After:
O---D---E           main
        \
         A'---B'---C'  feature
```

Git finds where the branches split, then reapplies the changes from `A`, `B`, and `C`, one commit at a time, after `E`.

Your feature branch now includes the latest changes from your **local** `main`. Git does not fetch updates automatically. `main` itself stays unchanged.

The replayed commits normally get **new commit IDs**, shown above with apostrophes, because their history has changed. Rebase does not create a merge commit. If your branch already sits on top of `main`, Git may have nothing to do.

If Git encounters a conflict, it pauses. Fix the conflicting files, stage them with `git add`, and run `git rebase --continue`. You might need to repeat this for several commits. Use `git rebase --abort` to return to the state before the rebase.

Avoid rebase when:

- **Other people are already using those commits.** Rewriting shared history can disrupt their work. Prefer merging unless the team explicitly agrees to the rewrite.
- **You need to preserve the original branch and merge history.** Rebase changes that history.
- **You have uncommitted work you need to protect.** Commit or stash it first.

A useful rule: rebase your private feature work to keep history tidy; merge shared work when preserving history matters.

Hold the line, Spartan.