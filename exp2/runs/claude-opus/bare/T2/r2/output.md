# What `git rebase main` does

## The starting point

You branched off `main` and made 3 commits. Meanwhile, others merged 2 new commits into `main`:

```
          A---B---C   feature (you are here)
         /
    D---E---F---G     main
```

`E` is the **merge base**, the last commit both branches share.

## Step by step

When you run `git rebase main` while on `feature`:

1. **Git finds the merge base** (`E`) and identifies the commits that exist only on your branch: `A`, `B`, `C`.
2. **It sets those commits aside** as a list of changes (diffs).
3. **It moves your branch to the tip of `main`** (`G`), so temporarily it looks like you have no work.
4. **It replays your changes one at a time** on top of `G`: first `A`, then `B`, then `C`. Each one becomes a new commit.
5. **It points `feature` at the last new commit.**

The result:

```
                  A'--B'--C'   feature
                 /
    D---E---F---G              main
```

Notice the `'` marks. **`A'`, `B'`, and `C'` are brand-new commits** with new hashes. They have the same changes and messages as the originals, but different parents, so Git treats them as different commits. The originals still exist briefly but nothing points to them anymore. This is the key point behind every rebase warning.

## If there's a conflict

Because commits are replayed one by one, Git can stop on any of them:

- Fix the conflicted files.
- Run `git add <file>`.
- Run `git rebase --continue` to move on to the next commit.
- Or run `git rebase --abort` to cancel everything and return to where you started.

You might resolve conflicts up to 3 times (once per commit). With `merge` you'd resolve them once.

## Practical tips

- **`git rebase main` uses your *local* `main`**, which may be out of date. Run `git fetch` first and use `git rebase origin/main`, or pull `main` before rebasing.
- **If you mess up, your work isn't lost.** Run `git reflog`, find the commit from before the rebase, and run `git reset --hard <that-hash>`. Right after a rebase, `ORIG_HEAD` also points to where you were.
- **If you already pushed the branch**, the remote still has the old `A-B-C`, so a normal push will be rejected. Use `git push --force-with-lease`, not plain `--force`. It refuses to overwrite the remote if someone else pushed to it in the meantime.

---

# When *not* to rebase

### 1. A branch other people are working on (the golden rule)
If a teammate has pulled your branch and built on `B`, and you rebase it into `B'`, their history no longer matches yours. When they pull, they'll get duplicate commits, confusing conflicts, or they'll accidentally bring the old commits back. **Only rebase branches that only you use.**

### 2. Shared, long-lived branches like `main`, `develop`, or release branches
Never rebase these. Everyone depends on their history staying stable. (Rebasing your feature branch *onto* `main` is fine. Rebasing `main` itself is not.)

### 3. When your team's workflow says to merge
Some teams want the real history preserved, including when a branch started and when it was merged in. Follow the convention. Mixing styles makes history harder to read.

### 4. When the rebase becomes painful
For a long-running branch with many commits that keep conflicting with `main`, you may end up resolving the same conflict over and over. A single `git merge main` can be easier. (`git rerere` can help if you stick with rebasing.)

### 5. When you're unsure what state you're in
Don't start a rebase with uncommitted changes, or in the middle of another merge or rebase. Commit or stash first.

---

## Rule of thumb

> **Rebase your own local or private work to keep it clean. Merge anything that's shared.**

Rebasing `feature` onto `main` before opening a PR is a common and good habit. Rebasing a branch that a teammate has checked out is how you ruin their afternoon.