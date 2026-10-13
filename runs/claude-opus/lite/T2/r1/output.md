**Short answer:** Rebase takes your 3 commits, moves the start of your branch to the latest commit on `main`, and applies the 3 commits again. Do not rebase commits that other people already pulled.

## What happens

Before the rebase, your branch started from `main` at commit `C`. Since then, `main` got 2 new commits.

```
A---B---C---D---E          main
         \
          X---Y---Z        feature
```

When you run `git rebase main` on `feature`, Git does these steps:

1. Git finds the last commit that both branches share. Here, that is `C`.
2. Git saves the changes from your 3 commits: `X`, `Y`, and `Z`.
3. Git moves your branch to the latest commit on `main`, which is `E`.
4. Git applies the saved changes again, one commit at a time, in the same order.
5. Each applied change becomes a new commit with a new hash: `X'`, `Y'`, `Z'`.
6. Git moves the `feature` label to `Z'`.

```
A---B---C---D---E          main
                 \
                  X'--Y'--Z'   feature
```

Important points:

- `main` does not change. Only your branch changes.
- Your history is now a straight line. Git does not make a merge commit.
- The new commits get new hashes because their parent commits changed. The changes inside them can be identical.
- Git keeps the old commits for some time. If the rebase goes wrong, `git reflog` shows them, and you can go back.

## If Git finds a conflict

Git stops at the commit that has the conflict. With 3 commits, you can get up to 3 separate stops.

1. Run `git status` to see the conflicted files.
2. Open each file and fix the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
3. Run `git add <file>` for each fixed file.
4. Run `git rebase --continue`.

If you want to cancel, run `git rebase --abort`. Git then puts your branch back to how it was before the rebase.

Caution: during a rebase, "ours" means the `main` side and "theirs" means your commit. This is the opposite of a merge.

## After the rebase

1. Run your tests again. Your commits now use new code from `main`, so they can break even with no conflict.
2. If you already pushed the branch, run `git push --force-with-lease`.

**Warning:** Use `--force-with-lease`, not `--force`. Plain `--force` can delete commits that a teammate pushed to the same branch.

## When not to rebase

- **Other people use the branch.** If a teammate pulled your commits or built on them, do not rebase. Rebase gives the commits new hashes, so their copies no longer match yours. They then get duplicate commits and confusing conflicts.
- **The branch is `main` or another public branch.** Never rebase these. Everyone depends on their history.
- **You must keep the true history.** Some teams need a record of when and how work came together, for audits or debugging. Use `git merge` for this.
- **The rebase gives many conflicts.** Rebase can make you fix conflicts commit by commit, sometimes the same conflict more than once. A merge makes you fix all conflicts one time.
- **Your team uses a merge workflow.** Follow the team rule.

**Simple rule:** Rebase work that only you use, even after you push it. Merge work that other people share.

Go forth, legionnaire. Keep your history straight and your shield wall tight.