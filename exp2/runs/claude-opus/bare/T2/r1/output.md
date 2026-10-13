# What `git rebase main` does

## The starting point

Say you branched off `main` at commit `E`, made 3 commits (`A`, `B`, `C`), and meanwhile other people merged `F` and `G` into `main`:

```
          A---B---C      feature (you are here)
         /
    D---E---F---G        main
```

## What Git does, step by step

When you run `git rebase main` while on `feature`:

1. **Finds the common ancestor.** Git sees that `feature` and `main` diverged at `E`.
2. **Collects your commits.** It identifies the commits on `feature` that aren't on `main`: `A`, `B`, `C`.
3. **Moves to the tip of main.** It temporarily checks out `G`.
4. **Replays your commits one at a time.** It applies the *changes* from `A` on top of `G`, making a new commit `A'`. Then `B` on top of `A'` to get `B'`, then `C'`.
5. **Moves your branch label.** `feature` now points at `C'`.

```
                  A'--B'--C'   feature
                 /
    D---E---F---G              main
```

**Key point:** `A'`, `B'`, `C'` are *new commits*. They have the same messages and the same changes, but **different hashes**, because their parent changed. You haven't moved your commits. You've rewritten them. The originals still exist for a while (you can find them with `git reflog`), but your branch no longer points to them.

The result is a linear history, as if you'd started your work from the latest `main`.

## When there are conflicts

Because Git replays commits one at a time, a conflict can stop it partway through, for example at `B`. When that happens:

```bash
# fix the conflicted files, then:
git add <fixed-files>
git rebase --continue   # move on to the next commit

git rebase --abort      # give up, go back to exactly how things were before
git rebase --skip       # drop this commit entirely (rarely what you want)
```

You might resolve conflicts several times, once per commit that touches the conflicting code.

**Gotcha:** during a rebase, "ours" and "theirs" are the opposite of what you'd expect. "Ours" is `main` (the base you're building on), and "theirs" is *your* commit being replayed. Keep this in mind if you use `git checkout --ours/--theirs`.

## Practical tips

- **Rebase onto the up-to-date main.** `git rebase main` uses your *local* `main`, which may be stale. Either `git pull` on main first, or do:
  ```bash
  git fetch origin
  git rebase origin/main
  ```
- **If you'd already pushed the branch**, the remote still has the old `A`, `B`, `C`, so a normal push will be rejected. Use:
  ```bash
  git push --force-with-lease
  ```
  Prefer `--force-with-lease` over `--force`. It refuses to overwrite the remote if someone else pushed to it since you last fetched.
- **Run your tests afterward.** Your replayed commits are now sitting on code they've never been tested against.
- **Undo button:** if a finished rebase went wrong, `git reflog` shows where your branch was before, and `git reset --hard <that-hash>` gets you back.

---

# When you should NOT rebase

**1. Don't rebase commits that other people have based work on.** This is the golden rule. If a teammate pulled your branch and built on it, rebasing rewrites the commits they depend on. When you force-push, their history and yours diverge. They end up with duplicate commits and confusing conflicts. If the branch is shared, merge instead.

**2. Never rebase `main` (or `develop`, release branches, etc.).** Those are public, shared history. Rewriting them breaks everyone.

**3. Don't rebase when the true history matters.** Some teams want to see exactly when a branch was integrated, or need an audit trail of what was tested when. A merge commit records that. A rebase erases it.

**4. Think twice on long-lived branches with many commits.** If your branch has 40 commits and `main` changed the same files heavily, you may resolve the same conflict over and over, once per commit. A single `git merge main` resolves it once. (Alternatively, squash your commits first, or enable `git rerere`, which remembers conflict resolutions.)

**5. Follow your team's convention.** Some teams require merge commits, some require rebased/linear history, and some squash-merge PRs (in which case rebasing your branch mostly doesn't matter). Ask before force-pushing to a branch under review, because some reviewers lose their place in the diff when commits are rewritten.

## Rule of thumb

> **Rebase your own private work to keep it tidy and up to date. Merge when the work is shared.**

If the branch only exists on your machine, or it's your own PR branch that nobody else touches, rebase freely. If anyone else might have those commits, don't rewrite them.