`git rebase main` takes the commits unique to your feature branch and replays their changes on top of your **local `main` branch**.

Suppose your branch has three commits, and `main` has advanced since you branched:

```text
Before:
A---B---C  main
 \
  F1---F2---F3  feature

After:
A---B---C---F1'---F2'---F3'  feature
        ^
        main
```

Git applies the changes from `F1`, then `F2`, then `F3` after `C`. The resulting commits have **new commit IDs**, because they have different parents. Your feature branch now includes the newer changes from `main`, and `main` itself stays unchanged.

If Git encounters a conflict, it pauses. Resolve the conflicting files, stage them with `git add`, and run `git rebase --continue`. You may need to repeat this for multiple commits. To cancel and return to where you started, run `git rebase --abort`.

Also, `git rebase main` does **not** download updates: it uses whatever your local `main` currently contains.

Avoid rebase when:

- **Other people depend on the commits you would rewrite**, especially on a shared branch. Changing commit IDs can disrupt their work. Use `git merge main` instead, unless everyone has coordinated the rewrite.
- **You need to preserve the original history**, including existing merge structure. Rebase changes that history and normally flattens merges.

A useful rule: rebase your own unpublished feature work; merge when updating history that others rely on.