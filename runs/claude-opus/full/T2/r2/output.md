**Short answer:** `git rebase main` saves your 3 commits and moves your branch to the newest commit on `main`. Then Git applies the 3 commits again, one at a time. You get the same changes, but as 3 new commits with new IDs. Do not rebase a branch that other people already pulled or built work on.

## The picture

You started your branch from commit B. Then other people added C and D to `main`.

```
Before:
main:     A---B---C---D
               \
feature:        E---F---G

After `git rebase main`:
main:     A---B---C---D
                       \
feature:                E'--F'--G'
```

E', F', and G' have the same changes as E, F, and G. They are new commits because Git computes each commit ID from the content and the parent commit. A new parent gives a new ID.

## Step by step

1. Git finds the last commit that both branches share (B). This commit is the "merge base".
2. Git saves the commits that exist only on your branch: E, F, and G.
3. Git starts at the tip of `main` (D).
4. Git applies E on D and makes a new commit, E'. Then it does the same for F and G, in order.
5. After all 3 commits apply, Git moves the `feature` label to G'. The rebase is complete.

## If a conflict happens

Git stops at the commit that conflicts and shows the files to fix.

1. Edit the files and remove the conflict markers.
2. Run `git add <file>` for each fixed file.
3. Run `git rebase --continue`. Git applies the next commit.

`git rebase --abort` cancels the full rebase and returns the branch to its old state. Because Git applies each commit separately, you can get a conflict in each of the 3 commits.

## Things juniors often miss

- **`main` is your local copy.** If it is old, you rebase onto old code. Run `git fetch`, then `git rebase origin/main`.
- **A normal push fails after a rebase.** Use `git push --force-with-lease`. This option refuses to push if someone else pushed to the branch since your last fetch. Plain `--force` deletes their work without a warning.
- **The old commits still exist for some time.** `git reflog` lists them, so you can recover. For safety, make a backup branch before a large rebase: `git branch feature-backup`.
- **Git refuses to start with uncommitted changes in tracked files.** Commit or stash them first.

## When to rebase and when not to

| Situation | Rebase? |
|---|---|
| Only you work on the branch, and you did not push it | Yes, safe |
| Only you work on it, and you pushed it for a pull request | Yes, then `git push --force-with-lease` |
| A teammate pulled the branch or started work from it | No. Use `git merge main` |
| `main`, `develop`, or release branches | Never |

Two more cases where merge is often the better choice:

- **Large or repeated conflicts.** Rebase makes you fix conflicts commit by commit. If the same code conflicts in all 3 commits, one `git merge main` is often less work.
- **Team rules.** Some teams want merge commits in the history, or they block force-push. Follow the team rules.

Rule of thumb: rebase your own private history, merge shared history.

Steady hands, clean history. Onward, centurion.