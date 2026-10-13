## What `git rebase main` does

### Example

Your feature branch has 3 commits: A, B, and C. You made the branch from commit M1 on `main`. After that, other developers added commits M2 and M3 to `main`.

```
     A---B---C        feature
    /
  M1---M2---M3        main
```

### The steps that Git does

When you run `git rebase main` on your feature branch, Git does these steps:

1. Git finds the commit where your branch started (M1).
2. Git keeps a copy of the changes from each of your 3 commits.
3. Git moves your branch to the last commit on `main` (M3).
4. Git applies your changes again, one commit at a time: A, then B, then C.
5. For each change, Git makes a new commit (A', B', C').

### The result

```
                A'--B'--C'   feature
               /
  M1---M2---M3               main
```

- Your branch now starts from the last commit on `main`.
- The history is one straight line. It has no merge commit.
- A', B', and C' have the same changes as A, B, and C. But they are new commits with new commit IDs (hashes).
- The old commits A, B, and C are not on your branch now. Git keeps them for some time. You can find them with `git reflog`.

**Important:** Git does not move the old commits. Git makes new commits and moves the branch to them.

### If a conflict occurs

A conflict occurs when your commit and a commit on `main` change the same lines. Git then stops the rebase. Do these steps:

1. Run `git status` to find the files with conflicts.
2. Open each file and correct the conflict.
3. Run `git add <file>`.
4. Run `git rebase --continue`.

Git applies your commits one at a time. Thus, you can get a conflict in A, then in B, then in C.

To stop the rebase and go back to the condition before the rebase, run `git rebase --abort`.

### After the rebase: push

If you pushed the branch before the rebase, the remote branch has the old commits. Git does not accept a normal `git push`. Use this command:

```
git push --force-with-lease
```

Do not use `git push --force`. The `--force-with-lease` option stops the push if another person added commits to the remote branch. This prevents the loss of their work.

## When you must not use rebase

> **WARNING:** DO NOT REBASE COMMITS THAT OTHER PERSONS USE. A REBASE REPLACES COMMITS. OTHER PERSONS CAN LOSE WORK OR GET MANY CONFLICTS.

Do not use rebase in these conditions:

- **Other developers use your branch.** They have the old commits. After your rebase, their history and your history are different. When they pull, they can get two copies of the same changes and many conflicts.
- **The branch is `main` or another public branch.** Never rebase these branches. Many persons use them.
- **Your team uses merge.** Some teams want to keep the real history and the merge commits. Follow the rules of your team.
- **The rebase gives too many conflicts.** A rebase can show the same conflict in each commit. A merge shows all conflicts one time. In this condition, `git merge main` is easier.
- **You are not sure about the result.** Make a backup branch before the rebase: `git branch feature-backup`.

### A simple rule

Rebase only a branch that only you use. For all other branches, use `git merge main`. A merge adds one merge commit. It does not change the old commits.