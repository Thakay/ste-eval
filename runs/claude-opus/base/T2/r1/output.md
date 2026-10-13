**Short version:** `git rebase main` lifts your 3 commits off the feature branch, moves the branch to the tip of `main`, and replays the 3 commits on top, one by one. You get the same changes as brand-new commits in a straight line. Don't do it on a branch other people also use.

## What happens, step by step

Say you branched from `main` at commit B and made 3 commits. Meanwhile, teammates added D and E to `main`:

```
main:      A---B---D---E
                \
feature:         F1---F2---F3
```

When you run `git rebase main` while on `feature`:

1. **Find the split point.** Git finds the last commit both branches share (B).
2. **Set your commits aside.** It saves the changes that F1, F2 and F3 each made.
3. **Jump to the new base.** It moves to the tip of `main` (E).
4. **Replay one at a time.** It applies F1's changes on top of E and makes a new commit, then does the same for F2, then F3.
5. **Move the label.** The `feature` branch now points at the last replayed commit.

```
main:      A---B---D---E
                        \
feature:                 F1'---F2'---F3'
```

Things to understand about the result:

- **These are new commits.** F1' has the same message, author and changes as F1, but a different parent, so it gets a different hash. You have rewritten your branch's history.
- **The old commits still exist for a while.** Nothing points to F1, F2, F3 anymore, but `git reflog` can find them (kept about 30 days by default). Right after a rebase, `ORIG_HEAD` points to the old tip, so `git reset --hard ORIG_HEAD` undoes it.
- **`main` is not touched.** Only your branch moves.
- **It uses your local `main`.** If you haven't pulled lately, you're rebasing onto an old version. Safer habit: `git fetch` then `git rebase origin/main`.

## When there's a conflict

Git replays commits one at a time, so it can stop at any of the 3 if that commit changes the same lines as D or E.

- Fix the files, then `git add <file>` and `git rebase --continue`.
- `git rebase --abort` puts everything back exactly as it was before you started.
- `git rebase --skip` throws away the current commit. Rarely what you want.

Two gotchas:

- You can hit conflicts up to 3 times, and sometimes the same conflict comes back in a later commit.
- "ours" and "theirs" are flipped compared to a merge. During a rebase, "ours" is `main` (what you're building on) and "theirs" is your own commit being replayed.

## After the rebase

If you had already pushed `feature`, a normal `git push` gets rejected, because the remote still has F1 to F3 and your branch no longer contains them. Use:

```
git push --force-with-lease
```

This is the safe form of `--force`: it refuses if someone else pushed to the branch since your last fetch, so you don't wipe out their work.

Also rerun your tests. Your code now sits on top of D and E, a combination nobody has tested yet.

## When NOT to rebase

1. **The branch is shared.** This is the big one. If teammates have pulled your branch or built on it, their copies still have F1 to F3 while yours has F1' to F3'. When they pull, Git sees two versions of the same work: duplicate commits, confusing conflicts, and sometimes lost work. Never rebase `main`, `develop`, or any branch others commit to.
2. **Your team prefers merge commits.** Some teams want a merge commit that records "feature X landed here". Follow the team's convention.
3. **A PR is in the middle of review.** Force-pushing can mark review comments as outdated and makes it harder for reviewers to see what changed since their last look. Ask first, or wait until review is done.
4. **A long-lived branch with many commits and lots of conflicts.** You may resolve the same conflict once per commit. A merge resolves it once. Alternative: squash your commits first with `git rebase -i`, then rebase.
5. **You're nervous about it.** Make a backup first with `git branch feature-backup`. It costs nothing.

## Rebase vs merge in one line

`git merge main` keeps your original commits and adds one merge commit (safe, but a busier history). `git rebase main` rebuilds your commits on top of `main` (clean straight-line history, but rewrites history). Rule of thumb: **rebase your own private branches freely, merge anything shared.**

Steady hands on the reins, recruit. The history is yours to shape, but never another soldier's to rewrite.