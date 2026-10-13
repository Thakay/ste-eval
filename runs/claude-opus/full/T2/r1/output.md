**Short answer:** `git rebase main` removes your 3 commits from their old starting point and applies them again, one by one, on the newest commit of `main`. You get a straight-line history, but all 3 commits receive new hashes (commit IDs). Do not rebase commits that other people already have.

## The starting point

You created `feature` from `main` at commit M1. Then you made commits A, B, and C. Meanwhile, other people added M2 and M3 to `main`.

```
     A---B---C   feature
    /
M1---M2---M3     main
```

## What Git does, step by step

1. Git finds the last commit that both branches share. Here, that is M1.
2. Git stores your 3 commits (A, B, C) as a temporary list of changes.
3. Git moves `feature` so that it points at M3, the newest commit on `main`.
4. Git applies A on top of M3 and makes a new commit, A'. Then it does the same for B and C.
5. Git moves `feature` to the last new commit, C'.

```
M1---M2---M3---A'---B'---C'   feature
          ^
          main
```

A', B', and C' contain the same changes as A, B, and C. But each one has a different parent, so each one has a different hash. Git treats them as new commits.

## If a conflict happens

Git stops at the commit that conflicts and shows you the files with the conflict. Then you choose one of these options:

- Fix the files, run `git add <file>`, then run `git rebase --continue`.
- Run `git rebase --skip` to drop that one commit.
- Run `git rebase --abort` to stop and return your branch to its state before the rebase.

You may need to fix conflicts more than once, because Git applies each commit separately.

## Three habits that prevent trouble

- **Update `main` first.** `git rebase main` uses your local `main`. If your local copy is old, you rebase onto old code. Run `git fetch`, then `git rebase origin/main`.
- **Push with care after a rebase.** If you already pushed `feature`, a normal push now fails, because the history changed. Use `git push --force-with-lease`. It refuses to overwrite commits that someone else pushed in the meantime. Do not use plain `--force`.
- **Know the way back.** Git keeps your old commits for a while. `git reflog` lists them. Directly after a rebase, `git reset --hard ORIG_HEAD` returns your branch to the old state. This command also deletes any uncommitted changes.

## When not to use rebase

- **Other people share the branch.** If teammates pulled your branch or based work on it, a rebase breaks their copies. Their history no longer matches yours. Use `git merge main` instead.
- **The branch is `main` or another public branch.** Never rebase these. Other people build their work on that history.
- **The branch is old and has many conflicts.** Rebase makes you fix conflicts commit by commit, sometimes the same conflict several times. A merge lets you fix all conflicts once.
- **Your team rules require merges.** Some teams want merge commits, so the history shows when each branch joined `main`. Follow the team rule.
- **A review is in progress.** A force push can make it harder for reviewers to see what changed since their last review. Ask the reviewer first, or rebase after the review.

**Rule of thumb:** Rebase your own work that nobody else has. Merge when other people share the branch.

Forge a straight history and guard the reflog, legionnaire.