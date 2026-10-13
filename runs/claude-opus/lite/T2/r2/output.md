**TL;DR:** `git rebase main` moves your 3 commits so that they start from the newest commit on `main`. Git makes 3 new commits with new hashes to do this. Rebase is safe on a branch that only you use. Do not rebase a branch that other people already pulled.

## What happens

Before the rebase:

```
A---B---C---D---E          main
         \
          F1---F2---F3     feature
```

You created `feature` from commit C. After that, other people added D and E to `main`.

When you run `git rebase main` on `feature`, Git does these steps:

1. Git finds the commit where `feature` split from `main`. Here, that is C.
2. Git collects your commits after C: F1, F2, and F3.
3. Git goes to E, the newest commit on your local `main`.
4. Git applies the changes from F1 on top of E. This makes a new commit, F1'.
5. Git applies F2 and then F3 in the same way. This makes F2' and F3'.
6. Git moves the `feature` branch to F3'.

After the rebase:

```
A---B---C---D---E                   main
                 \
                  F1'---F2'---F3'   feature
```

Important facts:

- F1' has the same message and changes as F1, but it has a different hash. The hash changes because the parent commit changed.
- `main` does not change. Rebase only changes the branch that you are on.
- Your old commits still exist for some time. `git reflog` shows them, so you can recover from a bad rebase.

## How to do it safely

1. Commit or stash your changes. Git does not start a rebase if tracked files have uncommitted changes.
2. Run `git fetch origin`.
3. Run `git rebase origin/main`.

This uses the newest `main` from the remote. Plain `git rebase main` uses your local `main`, and that copy can be old.

## If Git finds a conflict

If one of your commits changes the same lines as `main`, Git stops at that commit. Then do these steps:

1. Open each file with a conflict and fix it.
2. Run `git add <file>` for each fixed file.
3. Run `git rebase --continue`. Git then applies the next commit.
4. If you want to stop and go back to the start, run `git rebase --abort`.

Git can stop more than once, because it applies each of the 3 commits separately. During a rebase, "ours" means `main` plus your commits that Git already applied. "Theirs" means the commit that Git applies now. This is the opposite of a merge.

## If you already pushed the branch

After the rebase, a normal `git push` fails. The remote has F1 to F3, but your branch has F1' to F3'. Use `git push --force-with-lease`. This command stops if the remote branch has commits that you did not fetch.

**Do not use plain `git push --force`.** It can delete other people's commits on the remote branch without a warning.

## When not to use rebase

- **Do not rebase a branch that other people pulled or work on.** Their copies keep the old commits. When they pull, Git mixes the old and new commits. They can get duplicate commits and conflicts.
- **Do not rebase `main` or other shared branches.** The same problem then affects everyone on the team.
- **Do not rebase if your team requires merge commits.** Some teams want a record of when each branch came in. Check your team rules first.
- **Do not rebase a branch with merge commits that you want to keep.** By default, rebase removes merge commits and makes the history a straight line.
- **Think before you rebase a long branch with many conflicts.** Rebase can make you fix the same conflict in several commits. A merge makes you fix it only once.

In these cases, use `git merge origin/main` instead. It adds the new `main` commits to your branch with one merge commit. It does not change your existing commits, so it is safe on shared branches.

**Simple rule:** If only you use the branch, rebase. If other people use the branch, merge.

Rebase in private, merge in the open. March well, legionnaire.