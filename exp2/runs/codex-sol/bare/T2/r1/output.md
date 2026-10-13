`git rebase main` moves your current feature branch onto the latest commit of your **local `main` branch**, then replays your feature commits one at a time.

Suppose `main` has gained two commits since you branched off:

```text
Before:
A──B──C          main
 \
  F1──F2──F3     feature

After:
A──B──C          main
       \
        F1'──F2'──F3'  feature
```

Git takes the changes from `F1`, `F2`, and `F3` and applies them after `C`. Normally, you still have three feature commits, but they get **new commit IDs** because their history has changed. `main` itself stays unchanged.

If a change conflicts with something on `main`, Git pauses. Fix the files, stage them with `git add`, and run `git rebase --continue`. To cancel and return to where you started, run `git rebase --abort`.

Also, `git rebase main` does **not** download updates: it uses the `main` you already have locally.

Avoid rebase when:

- **Other people depend on the commits you would rewrite**, especially on shared branches such as `main`. Replacing those commits can disrupt their work and often requires a force push.
- **You need to preserve the original branch and merge history.** A normal rebase rewrites commits and usually removes merge commits; use a merge to preserve that history.

A useful rule: rebase your own unpublished feature work; merge when preserving shared history matters.