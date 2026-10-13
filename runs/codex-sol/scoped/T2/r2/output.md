When you run `git rebase main` from your feature branch, Git replays your three commits on top of your local `main`.

For example:

```text
Before:
A---B---C             main
 \
  F1---F2---F3         feature

After:
A---B---C             main
         \
          F1'---F2'---F3'   feature
```

Git applies each commit’s changes in order. The replayed commits get new IDs because their parent commits change. Your feature branch points to `F3'`. Git leaves `main` unchanged.

If your branch already contains the current `main`, Git usually has nothing to change. The command uses your local `main`; it does not fetch updates.

If Git finds a conflict, it pauses:

1. Resolve the conflict in the affected files.
2. Stage the resolved files with `git add <file>`.
3. Run `git rebase --continue`.

Git can pause again for later commits. If you want to cancel, run `git rebase --abort`.

Avoid rebase when:

- **Other developers depend on those commits.** Rewriting shared history can disrupt their work. Coordinate any rewrite with them first.
- **You must preserve the original branch and merge history.** A normal rebase rewrites commits and removes merge commits from the replayed history.

For a shared feature branch, `git merge main` is often safer because it preserves existing commits.

Onward, Spartan.