# What occurs when you use `git rebase main`

## The start condition

You are on your feature branch. The branch has 3 commits: A, B, and C. You made the branch from `main` at commit M1. After that, other persons added 2 commits to `main`: M2 and M3.

```
          A---B---C          feature (you are here)
         /
    ---M1---M2---M3          main
```

## The steps that Git does

When you use the command `git rebase main`, Git does these steps:

1. Git finds the last commit that is on both branches. Here, this commit is M1.
2. Git finds the changes in A, B, and C.
3. Git moves your branch to the last commit on `main`. Here, this commit is M3.
4. Git applies the changes from A after M3. This makes a new commit, A'.
5. Git applies the changes from B, and then from C. This makes B' and C'.

The result:

```
                     A'--B'--C'   feature
                    /
    ---M1---M2---M3               main
```

## Important facts about the result

- A', B', and C' are new commits. They have new commit IDs (hashes).
- The code changes in A', B', and C' are the same as in A, B, and C. The parent commits and the IDs are different.
- Your history is a straight line. Git does not make a merge commit.
- The old commits A, B, and C are not on your branch now. Git keeps them for some time. You can find them with `git reflog`.

## If a conflict occurs

Git applies the commits one at a time. Thus, a conflict can occur at A, B, or C. If a conflict occurs, Git stops. Do these steps:

1. Repair the conflict in each file that Git shows.
2. Use `git add <file>` for each file that you repaired.
3. Use `git rebase --continue`. Git then applies the next commit.

Do not use `git commit` at this step. The command `git rebase --continue` makes the commit for you.

To stop the rebase and go back to the condition before the rebase, use `git rebase --abort`.

## Before you start

1. Make sure that you committed all your changes.
2. Make sure that your local `main` has the last commits from the remote. On `main`, use `git pull`. Then go back to your feature branch.

# When you must not use rebase

**CAUTION: DO NOT REBASE COMMITS THAT OTHER PERSONS HAVE.**

Rebase changes the commit IDs. Other persons have the old commits. When they pull, their history and your history do not agree. Git can show the same changes in two different commits. Git can also show many conflicts. The other persons must then do work to repair their history.

Do not use rebase in these conditions:

1. **Other persons use the branch.** Examples: `main`, `develop`, or a feature branch that two or more developers use. Use `git merge` on these branches.
2. **You pushed the commits, and other persons possibly pulled them.**
3. **Your project wants merge commits.** Some projects keep the exact history. They use merge commits to show when a branch went into `main`. Read the rules of your project.
4. **The rebase has many conflicts.** Git applies each commit one at a time. Thus, you can get the same conflict at each commit. With many commits, `git merge` can be easier. With a merge, you repair all conflicts one time.

# When rebase is safe

- Only you use the branch.
- You did not push the commits, or only you use the remote branch.

If you pushed the branch before the rebase, you must push again with force. Use `git push --force-with-lease`. Do not use `git push --force`. The `--force-with-lease` option stops the push if another person pushed new commits to the branch.

# A simple rule

| Condition | Rebase |
|---|---|
| Your local commits that only you have | Safe |
| Commits that other persons have | Not safe |

If you are not sure, make a backup branch first: `git branch backup-feature`. If you have a problem after the rebase, you can go back to the backup branch.