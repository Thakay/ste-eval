Running `git rebase main` while you’re on your feature branch moves your feature work onto the tip of your local `main`.

Suppose your branches look like this:

```text
A---B---C          main
 \
  F1---F2---F3     feature
```

Git takes the changes from your three feature commits and replays them, in order, after `C`:

```text
A---B---C---F1'---F2'---F3'     feature
        ^
       main
```

Your feature branch now includes the changes from `main`, followed by your work. The three feature commits remain separate—rebase doesn’t automatically squash them—but they get **new commit IDs** because their history has changed. `main` itself stays unchanged.

If a replayed commit conflicts with changes on `main`, Git pauses. Resolve the conflicts, stage the resolved files with `git add`, and run `git rebase --continue`. You can use `git rebase --abort` to return to the state before the rebase.

Also, `main` means your **local** branch; this command doesn’t download updates from the remote.

Avoid rebase when:

- **Other developers have pulled or built work on those commits.** Rewriting them can disrupt their history and require a force push. Coordinate explicitly if your team needs to do this.
- **You need to preserve the original branch and merge history.** A normal rebase rewrites commits and usually flattens merge structure.

Rebase is useful for tidying your own feature work before sharing it. For commits others already depend on, `git merge main` is usually the safer choice.