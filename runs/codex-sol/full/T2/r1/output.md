On your feature branch, `git rebase main` replays your three commits after the latest commit on your local `main`.

Suppose your feature branch started at `A`, and `main` later gained `B` and `C`:

```text
Before:
A---B---C             main
 \
  F1---F2---F3        feature

After:
A---B---C---F1'---F2'---F3'   feature
        ^
        main
```

Git applies each feature commit’s changes in order. The replacement commits get new IDs because their history changes. Your feature branch points to `F3'`. The `main` branch stays unchanged.

Git can skip a commit if `main` already contains its changes. If no rebase is necessary, Git can leave your branch unchanged.

If Git finds a conflict, it pauses:

1. Resolve the conflict in the affected files.
2. Stage the corrected files with `git add`.
3. Run `git rebase --continue`.

Conflicts can occur again for later commits. Use `git rebase --abort` to cancel the rebase and restore the original branch state.

Avoid rebase when other developers use your branch or base their work on its commits, unless everyone agrees to rewrite that history. Changed commit IDs can disrupt their work. Use `git merge main` instead.

Also prefer merge when your project requires the original commit history or merge commits.

The command uses local `main`. It does not fetch updates from the remote.

Godspeed, Spartan.