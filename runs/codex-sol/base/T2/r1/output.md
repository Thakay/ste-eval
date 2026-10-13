Running `git rebase main` while you are on your feature branch takes your branch’s commits and replays them on top of your local `main`.

Suppose `main` has gained two commits since you branched, and your feature branch has three:

```text
Before:
A---B---C          main
 \
  F1---F2---F3     feature

After:
A---B---C          main
         \
          F1'---F2'---F3'   feature
```

Git:

1. Finds the commits on your feature branch that are not on `main`.
2. Starts from the latest commit on `main`, here `C`.
3. Applies your three commits one at a time, in order.

The replayed commits have **new commit IDs**, because their history has changed. Your feature branch now includes `main`’s changes. **`main` itself stays unchanged.** The command uses your local `main`; it does not download updates.

If a commit conflicts with changes on `main`, Git pauses. Resolve the conflict, stage the fixed files with `git add`, then run `git rebase --continue`. You may encounter conflicts again with later commits. To cancel and restore your original branch history, run `git rebase --abort`.

Avoid rebase when:

- **Other people have pulled or built work on those commits.** Rewriting their IDs can disrupt your teammates’ work. Use `git merge main` to incorporate updates while preserving existing history.
- **You need to preserve the original branch and merge history.** A normal rebase can flatten that history.
- **You have uncommitted work you have not protected.** Commit or stash it first.

A useful rule: rebase your own unpublished feature work; merge when preserving shared history matters.

Godspeed Spartan.