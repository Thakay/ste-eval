**TL;DR:** `git rebase main` takes your 3 commits off your branch, moves your branch to the tip of `main`, and replays those 3 commits on top one by one as brand new commits. The result is a clean, straight-line history. Do not rebase commits that other people already have, because it rewrites history.

## What happens, step by step

Say your branch looks like this. You branched off at `E`, and since then two new commits (`F`, `G`) landed on `main`:

```
          A---B---C    feature  (your 3 commits)
         /
    D---E---F---G      main
```

When you run `git rebase main` while on `feature`:

1. **Find the split point.** Git finds the last commit both branches share (`E`).
2. **Collect your commits.** It notes the commits that are on `feature` but not on `main`: `A`, `B`, `C`.
3. **Jump to main.** It moves to the tip of `main` (`G`).
4. **Replay one at a time.** It applies the changes from `A` on top of `G` and makes a new commit `A'`. Then `B` on top of `A'` makes `B'`, then `C'`.
5. **Move the branch label.** `feature` now points to `C'`.

```
                  A'--B'--C'    feature
                 /
    D---E---F---G               main
```

Key point: `A'`, `B'`, `C'` are **new commits with new hashes**. Same changes, but different parents, so Git sees them as different commits. The old `A`, `B`, `C` still exist for a while (you can find them with `git reflog`), but your branch no longer points to them.

## If there is a conflict

Because Git replays each commit separately, you can hit a conflict at any of the 3 steps. Git stops and tells you which commit failed. Then you:

- Fix the files, `git add` them, and run `git rebase --continue`.
- Or run `git rebase --abort` to cancel and go back to exactly where you started.

Two traps:

- You may resolve conflicts up to 3 times (once per commit), sometimes in the same spot.
- During a rebase, "ours" and "theirs" are **swapped** compared to a merge. "Ours" is the `main` side you are building on; "theirs" is your own commit being replayed. This confuses almost everyone the first time.

## After the rebase

- **Local `main` only.** `git rebase main` uses your *local* `main`. If you have not pulled lately, you are rebasing onto an old version. Run `git fetch` first and use `git rebase origin/main`, or update `main` first.
- **Pushing.** If you had already pushed `feature`, a normal `git push` will be rejected, because the remote still has the old `A`, `B`, `C`. You need `git push --force-with-lease`. Prefer this over `--force`: it refuses to overwrite if someone else pushed to the branch since you last fetched.
- **Safety net.** Before a scary rebase, run `git branch backup-feature`. If things go wrong, you can get back. `git reflog` also shows where your branch was before.

## When NOT to rebase

| Situation | Why not |
|---|---|
| The branch is shared and others have pulled it or built on it | You rewrite commits they have. Their history no longer matches yours, and they get duplicate commits and painful fixes. This is the golden rule. |
| `main`, `develop`, `release`, or any shared long-lived branch | Never rewrite these. Everyone depends on them. |
| Your team prefers merge commits | Some teams want the real history kept, including when a branch was merged in. Follow the team's rule. |
| A long branch with lots of conflicts | Rebase makes you resolve conflicts commit by commit. A merge makes you resolve them once. |
| The branch contains merge commits you want to keep | A plain rebase flattens them away. |
| You are confused about the current state | Stop, `git rebase --abort`, and ask. Do not force push something you don't understand. |

## When rebase is a good choice

- Your own feature branch that only you work on, to catch up with `main` before opening or updating a pull request.
- Cleaning up your own messy commits before review (`git rebase -i`, the interactive mode, lets you squash, reorder, and reword).

Simple rule to remember: **rebase your own private work, merge shared work.**

Rewrite only what is yours, and the history will remember you kindly. Hold the line, legionary.