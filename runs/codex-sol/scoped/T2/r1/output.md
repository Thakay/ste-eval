When you run `git rebase main` from your feature branch, Git moves your feature work onto your local `main`.

Suppose your branch has three commits, `A`, `B`, and `C`, and `main` has two new commits:

```text
Before:
O---D---E       main
 \
  A---B---C     feature

After:
O---D---E---A'---B'---C'     feature
        ^
        main
```

Git applies the changes from `A`, `B`, and `C`, one commit at a time, after `E`. The recreated commits get new commit IDs because their history has changed.

Rebase normally keeps your three commits separate. It does not squash them or create a merge commit. Your feature branch moves; `main` stays unchanged.

If Git finds a conflict, it pauses. You must resolve the conflict before it can continue. You can also cancel with `git rebase --abort`.

The command uses your **local** `main`. It does not fetch updates from the remote repository.

Avoid rebase when:

- **Other developers depend on your branch’s commits.** Rebase changes commit IDs and can disrupt their work. Use merge unless everyone agrees to rewrite the history.
- **You must preserve existing history or merge commits.** A normal rebase rewrites history and does not preserve merge commits.
- **Your team requires merges.** Follow the team’s workflow.

Rebase is usually useful for updating a private feature branch before sharing it.

Godspeed, Spartan.