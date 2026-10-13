# What `git rebase main` does

## The starting point

You branched off `main` a while ago and made 3 commits. Meanwhile, teammates merged other work into `main`:

```
          C1---C2---C3        ← feature (you are here)
         /
A---B---D---E                 ← main
```

Your branch is based on `B`, but `main` has moved on to `E`.

## What Git does, step by step

When you run `git rebase main` while on `feature`:

1. **Finds the common ancestor.** Git sees that `feature` and `main` split at `B`.
2. **Collects your commits.** It finds the commits on `feature` that aren't on `main`: `C1`, `C2`, `C3`. It saves them as a list of changes.
3. **Moves to the tip of `main`.** Git temporarily checks out `E`.
4. **Replays your commits one at a time.** It applies the changes from `C1` on top of `E`, then `C2`, then `C3`. Each one becomes a **brand-new commit** (`C1'`, `C2'`, `C3'`). The changes and messages are the same, but the commits have a different parent, so they get **different hashes**.
5. **Moves your branch label.** `feature` now points at `C3'`.

```
A---B---D---E                 ← main (unchanged)
             \
              C1'--C2'--C3'   ← feature
```

The result looks as if you'd started your work from the latest `main`. History is linear, with no merge commit.

**Key points:**
- `main` itself is not touched. Only your branch moves.
- Your old commits (`C1`, `C2`, `C3`) still exist for a while. If something goes wrong, `git reflog` can find them, and `git reset --hard ORIG_HEAD` right after a rebase undoes it.

## If there are conflicts

Because Git replays your commits one by one, it can stop at **each** of the 3 commits if that commit conflicts with what's in `main`. When it stops:

```bash
# fix the conflicted files, then:
git add <files>
git rebase --continue    # move on to the next commit

git rebase --abort       # or: bail out and restore everything to how it was
```

⚠️ **Gotcha:** during a rebase, "ours" and "theirs" are the **reverse** of what you'd expect. "Ours" is `main` (the base you're building on), and "theirs" is your commit being replayed. Keep this in mind when using `git checkout --ours/--theirs` or reading your editor's conflict labels.

## Two practical tips

- **Your local `main` may be stale.** `git rebase main` uses *your copy* of `main`, which may be days old. Usually you want:
  ```bash
  git fetch origin
  git rebase origin/main
  ```
- **If you already pushed the branch,** a normal `git push` will be rejected, because your branch's history changed. Use:
  ```bash
  git push --force-with-lease
  ```
  This is safer than `--force`. It refuses to push if someone else pushed to the branch since you last fetched, so you won't silently wipe out their work.

---

# When you should NOT rebase

### 1. When other people have built on your commits (the golden rule)
**Don't rebase commits that other people have pulled and are working from.** Rebasing replaces commits with new ones. If a teammate based work on your old `C2`, their history no longer matches yours, and they'll face confusing duplicate commits and conflicts. Never rebase `main`, `develop`, release branches, or any branch several people push to.

Rebasing **your own** feature branch, even one that's pushed for a PR, is generally fine **as long as nobody else is committing to it**. If a reviewer or pair partner has checked it out, give them a heads-up.

### 2. When the branch is long-lived and conflicts are heavy
Rebase replays commits one at a time, so with a big branch you can end up resolving the **same conflict over and over**, once per commit that touches that code. A merge makes you resolve conflicts once. If a rebase turns into a slog, `git rebase --abort` and merge instead.

### 3. When commit hashes are referenced elsewhere
If commit IDs appear in tickets, deploy logs, release notes, or signed/audited records, rebasing breaks those references because the hashes change.

### 4. When your team's workflow prefers merges
Some teams want merge commits so history shows exactly when and how a branch was integrated. Follow the team's convention. Check the contributing guide or ask.

### 5. When you're unsure what state you're in
If you have uncommitted changes, are mid-merge, or don't understand why Git is complaining, stop and sort that out first. Commit or stash your work before you rebase.

---

## Rule of thumb

> **Rebase to tidy up your own private work. Merge to combine shared work.**

If only you have touched the branch, rebasing onto `main` is a great way to keep history clean and your PR easy to review. If anyone else depends on those commits, merge instead.