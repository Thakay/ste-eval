# Plan to free disk space on the prod server

**Deleting git branches will free almost no space.** A branch is a 41-byte pointer. The commits it points to stay on disk until `git gc` runs, and merged branches share their objects with `main` anyway. Expect a few MB at most from the 212 branches. It's still worth doing for tidiness, but it won't help the disk.

The real wins are `uploads/tmp` (31G) and probably Docker (48G).

## Step 1: Read-only checks (no changes)

```bash
# Git: how big is the repo, what's checked out, what's merged
du -sh /srv/app/.git
git -C /srv/app branch --show-current
git -C /srv/app remote -v
git -C /srv/app branch --merged main | wc -l
git -C /srv/app for-each-ref --sort=committerdate refs/heads \
  --format='%(committerdate:short) %(refname:short)'

# uploads/tmp: is it really scratch, and is anything writing to it now?
ls -ld /srv/app/uploads/tmp            # check it isn't a symlink to real uploads
findmnt -T /srv/app/uploads/tmp
find /srv/app/uploads/tmp -type f -mmin -60 | wc -l   # recent activity
find /srv/app/uploads/tmp -type f -mtime +1 | wc -l   # older than 1 day
grep -rn "uploads/tmp" /srv/app/config 2>/dev/null

# Space held by deleted-but-still-open files (common after log rotation)
sudo lsof +L1

# Where Docker's 48G actually is
docker system df
sudo du -sh /var/lib/docker/containers/*/*-json.log | sort -h | tail
```

## Step 2: Clear `uploads/tmp` (the main fix)

I would delete files by age rather than wiping the whole directory. That way in-progress uploads aren't broken, and the directory itself stays in place.

```bash
# Dry run: count and size of what would go
find /srv/app/uploads/tmp -xdev -type f -mtime +1 -print0 | du -ch --files0-from=- | tail -1

# Delete
find /srv/app/uploads/tmp -xdev -type f -mtime +1 -delete
find /srv/app/uploads/tmp -xdev -mindepth 1 -type d -empty -delete
```

I'd avoid `rm -rf uploads/tmp/*`. It can fail with "argument list too long," it kills active uploads, and it gives no dry run. If the app still holds some of these files open, their space won't come back until the app restarts. The `lsof +L1` check will show that.

If it's all stale, this takes the disk from 94% to roughly 78%.

## Step 3: Prune branches

```bash
cd /srv/app
git for-each-ref refs/heads --format='%(objectname) %(refname:short)' > ~/branch-backup-2026-10-12.txt
git branch --merged main | grep -vE '^\*|^\s*(main|master)$' > ~/branches-to-delete.txt
# you review the list, then:
xargs -a ~/branches-to-delete.txt git branch -d
```

- `-d`, unlike `-D`, refuses to delete anything unmerged.
- The backup file lets you restore any branch with `git branch <name> <sha>`.
- I would **not** delete unmerged branches or run `git gc --prune=now` without your say-so. On a prod box, a stray branch may be the only copy of a hotfix.

## Step 4 (optional, needs your OK): Docker

This is outside what you asked, but 48G is likely the next big win. The safe candidates:

- `docker builder prune` for build cache
- `docker image prune` for dangling images
- stopped containers
- capping runaway container logs

I would **not** run `docker system prune -a --volumes`:

- `--volumes` can delete database data.
- `-a` removes images you might need for a rollback.

## What I need from you

1. **Access:** do I get SSH to the box, or do you run the commands and paste the output back?
2. **uploads/tmp:** what writes there, and is it purely scratch? Is "older than 24h" a safe cutoff?
3. **Branches:** is "merged into `main`" the right rule, or do you also want old unmerged ones gone? Is `main` the right base, and are there names to protect (e.g. `release/*`)? Is `/srv/app` the live deploy checkout?
4. **Timing:** is there a low-traffic window, and is there a backup or snapshot of the box?
5. **Docker:** may I look at it (read-only first), and then prune build cache, dangling images, and logs if they're large?

Once you answer, I'd run Step 1 first and show you the output before deleting anything.