**Short answer:** Git takes your 3 commits off your branch and puts them back on top of the newest commit on `main`. Your branch then looks like you started it from today's `main`. The 3 commits get new IDs (hashes), so git treats them as new commits.

## What happens

You started `feature` from commit E. After that, other people added F and G to `main`.

```
      A---B---C        feature (your 3 commits)
     /
D---E---F---G          main
```

When you run `git rebase main` while you are on `feature`, git does this:

1. Git finds the last commit that both branches share (E).
2. Git saves the changes from A, B, and C.
3. Git moves `feature` to G, the newest commit on `main`.
4. Git applies the changes from A on top of G and makes a new commit, A'.
5. Git does the same for B, and then for C.

After the rebase:

```
              A'--B'--C'   feature
             /
D---E---F---G              main
```

What to know:

- `main` does not change. Rebase moves only the branch that you are on.
- A', B', and C' have the same changes and messages as A, B, and C. They have new hashes because they have a new parent.
- Git does not delete the old A, B, and C immediately. If something goes wrong, you can find them with `git reflog`.
- Rebase uses your local `main`. If your local `main` is old, you rebase onto old code.

## If git stops with a conflict

Git applies each commit separately, so it can stop on any of the 3 commits. You may have to fix conflicts up to 3 times.

1. Open the files that git lists as conflicted.
2. Fix the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
3. Run `git add <file>` for each file that you fixed.
4. Run `git rebase --continue`.

To cancel, run `git rebase --abort`. Git puts your branch back to how it was before the rebase.

## A safe routine

1. Run `git fetch origin`.
2. Run `git rebase origin/main`.
3. If git stops with a conflict, fix it as shown above.
4. Run your tests.
5. If you pushed the branch before, run `git push --force-with-lease`.

A normal push fails in step 5 because the remote still has the old commits.

## When not to use rebase

The main rule: rebase only commits that only you have.

- **Do not rebase a branch that other people also use.** Their copies still have the old commits. When they pull, git mixes the old and new commits. They get duplicate commits and confusing conflicts.
- **Do not rebase `main` or any other shared branch.** The history of every person on the team will stop matching.
- **Do not use `git push --force` after a rebase. Use `--force-with-lease`.** Plain `--force` can remove commits that a teammate pushed. `--force-with-lease` refuses to push if the remote has commits that you did not fetch.
- **If a teammate started a branch from your branch, ask them before you rebase.** Their branch still points to your old commits.

Cases where `git merge main` is often the better choice:

- If your branch has many commits that conflict with `main`, merge is easier. You fix all conflicts once, in one merge commit, instead of once for each commit.
- If a reviewer is in the middle of a review of your pull request, tell them before you force-push, because some tools lose track of old comments.
- If your team requires merge commits, follow the team rule.

The tradeoff in one line: rebase gives you a clean, straight history, and merge keeps the real history and never changes commits that already exist.

Go forth, branch warden. May your history stay straight and your conflicts few.