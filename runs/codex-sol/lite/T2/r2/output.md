`git rebase main` replays your feature commits on top of your local `main`.

Suppose your feature branch has commits `A`, `B`, and `C`. Meanwhile, `main` gained commits `D` and `E`:

```text
Before:
main:     O--D--E
feature:  O--A--B--C

After:
main:     O--D--E
feature:  O--D--E--A'--B'--C'
```

Git applies each feature commit in order. The new versions have new commit IDs because their parents changed. Your feature branch now includes the changes from `main`. Git does not change `main` or create a merge commit.

The command uses your **local** `main`. It does not download changes from the remote repository. If `main` has no new commits, Git usually has nothing to change.

If Git finds a conflict, it stops:

1. Resolve the conflict in the affected files.
2. Stage the resolved files with `git add`.
3. Run `git rebase --continue`.
4. If another conflict occurs, repeat these steps.

If you want to cancel, run `git rebase --abort`. Git restores your branch to its state before the rebase.

Rebase suits a private feature branch when you want a straight commit history. **Avoid rebasing commits that other developers use as a base for their work.** Changing their IDs can disrupt those developers’ branches.

`git merge main` is safer for shared history because it preserves existing commits. Merge also suits teams that want to preserve the record of branch merges.

Godspeed, Spartan.