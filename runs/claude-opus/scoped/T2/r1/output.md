**Short answer:** Git takes your 3 commits off the old starting point and moves your branch to the newest commit on `main`. Then it replays the 3 commits on top, one at a time. The result looks as if you started your work today. Do not rebase commits that other people already have.

## What happens

Say you made your branch from `main` at commit B. Since then, `main` got two new commits (C and D), and you made F1, F2, F3.

```
Before:
      F1---F2---F3   feature
     /
A---B---C---D        main

After `git rebase main`:
              F1'--F2'--F3'   feature
             /
A---B---C---D                 main
```

Git does this:

1. It finds the merge base: B, the last commit that both branches share.
2. It sets aside the changes from F1, F2, and F3.
3. It moves `feature` to point at D, the tip of `main`.
4. It applies F1's changes on D and makes a new commit, F1'. Then it does the same for F2 and F3.
5. If a change conflicts with what is now in `main`, it stops and waits for you.

## Things that surprise people

- **The commits are new.** F1' has the same message and changes as F1, but a different hash, because its parent changed.
- **`main` does not move.** Only your branch moves.
- **Git uses your local `main`.** If you did not pull for a week, you rebase onto week-old code. Use `origin/main` after a fetch.
- **Conflicts come one commit at a time.** You can fix conflicts in the same file up to 3 times, once for each commit.
- **"Ours" and "theirs" swap.** During a rebase, "ours" is the `main` side and "theirs" is your commit. This is the opposite of a merge.
- **A normal push fails after a rebase** if you pushed the branch before, because the history changed. You must force push.
- **Your old commits still exist for a while.** `git reflog` shows them, so you can recover from a bad rebase.

## How to rebase safely

1. Commit or stash your uncommitted changes.
2. Run `git fetch origin`.
3. Run `git rebase origin/main`.
4. If git stops on a conflict, fix the conflicted files.
5. Run `git add <file>` for each fixed file.
6. Run `git rebase --continue`.
7. Repeat steps 4 to 6 until the rebase finishes.
8. Run your tests.
9. If you pushed the branch before, run `git push --force-with-lease`.

To stop in the middle, run `git rebase --abort`. Git puts your branch back as it was. To undo a finished rebase, run `git reset --hard ORIG_HEAD` right after it. If you ran other commands since then, find the old commit in `git reflog` instead.

Use `--force-with-lease`, not `--force`. It refuses to push if someone else pushed to the branch since your last fetch, so you do not delete their work.

## When not to rebase

> **Warning:** Do not rebase a branch that other people pulled or work on. Their copies still have the old commits. When they sync, they can get duplicate commits or lose work.

| Situation | Why rebase is a bad fit | Do this instead |
|---|---|---|
| Other people pulled your branch or build on it | You rewrite history that they have | `git merge main` |
| `main`, release branches, any shared branch | Same problem, but for the whole team | Never rewrite these |
| Team rules want merge commits or block force push | The push gets rejected, or you break the team's history style | Follow the team rule |
| The same conflict comes back in many commits | You fix it once per commit | Merge once, or squash your commits first with `git rebase -i` |
| Your branch has merge commits you want to keep | A plain rebase flattens them away | `git merge main` |

**Simple rule:** rebase is safe for commits that only you have. When other people have them, merge.

Rewrite only your own history, legionnaire. Hold the line. 🛡️