# What `git rebase main` does

## The start condition

Your feature branch starts at commit B. After that, other developers add commits C and D to `main`.

```
main:     A---B---C---D
               \
feature:        E---F---G
```

## The rebase procedure

When you run `git rebase main` on the feature branch, Git does these steps:

1. Git finds the last commit that the two branches have. This commit is the "merge base." Here, it is B.
2. Git keeps a temporary copy of the changes in your 3 commits (E, F, and G).
3. Git moves your branch to the last commit on `main` (D).
4. Git applies your 3 changes again, one commit at a time, in the same order.

## The result

```
main:     A---B---C---D
                       \
feature:                E'--F'--G'
```

E', F', and G' are new commits. They have the same changes and the same messages as E, F, and G. But they have different commit IDs.

The old commits are not on your branch now. Git keeps them in the reflog for a period of time. You can use `git reflog` to find them.

## If a conflict occurs

Git applies each commit separately. Thus, a conflict can occur at each of the 3 commits. When a conflict occurs, Git stops. Do these steps:

1. Fix the conflict in the files.
2. Run `git add <file>`.
3. Run `git rebase --continue`.

To stop the rebase and go back to the state before the rebase, run `git rebase --abort`.

## Why developers use rebase

- The history is a straight line. It is easy to read.
- Git does not add a merge commit.
- Your branch gets the new changes from `main` before you open a pull request.

# When you must not use rebase

> **CAUTION:** Do not rebase commits that other developers already have. Rebase changes the commit IDs. The history of the other developers and your history become different. They can get conflicts and two copies of the same changes.

Do not use rebase in these conditions:

- Other developers pull from your branch or push to your branch.
- The branch is a branch that all developers use, for example `main` or `develop`.
- The branch has many commits, and each commit has conflicts. With rebase, you can fix the same conflict many times. With merge, you fix the conflicts one time.
- The rules of your team tell you to use merge.

# If you already pushed your branch

If only you use the branch, you can rebase it. After the rebase, a usual push does not operate. You must do a force push:

```
git push --force-with-lease
```

Use `--force-with-lease`. Do not use `--force`. The `--force-with-lease` option stops the push if the remote branch has commits that you do not have.

# Simple rule

Rebase your local work. Do not rebase work that other developers have.