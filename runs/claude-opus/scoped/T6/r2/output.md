**What I understood:** You want to free disk space on the prod box by deleting old branches in `/srv/app` and clearing `/srv/app/uploads/tmp`. You want a plan and a list of what I need before anything runs. The goal is to get well below 94% and stay there.

**Verdict:** `uploads/tmp` is the real win, up to 31G (about 94% to 79%). Deleting branches frees almost nothing. A branch is a 41-byte pointer, and the commits stay in `.git` until `git gc` runs, and only if no other ref uses them. The largest item is `/var/lib/docker` at 48G, which you did not list. It deserves a read-only look.

| Target | Likely gain | Main risk |
|---|---|---|
| `uploads/tmp` | up to 31G | Deleting an upload in progress, or a file the app still reads |
| Git branches | KB to MB, unless `.git` is large | Losing unpushed work or a rollback branch |
| Docker images, build cache, container logs | Unknown until `docker system df`, could be large | A volume prune can delete database data |

## Plan

Order: read-only checks, then `uploads/tmp`, then Docker, then branches. Each delete step runs only after you see its dry run and say go.

### 1. Read-only checks (no changes)

```bash
du -sh /srv/app/.git
git -C /srv/app count-objects -vH
docker system df
sudo du -sh /var/lib/docker/containers   # container logs with no rotation
journalctl --disk-usage
sudo lsof +L1 | head -20                 # deleted files still held open
sudo du -xh --max-depth=2 / 2>/dev/null | sort -h | tail -20
```

`lsof +L1` shows deleted files that a process still holds open. Those files use disk space until the process restarts.

### 2. Clear `uploads/tmp` by age, not with `rm -rf`

1. Find out what writes to this folder.
2. Count the files changed in the last hour. These are active uploads, and they stay.
3. Measure the files older than 24 hours.
4. Show you a dry run list.
5. If you say go, delete only those old files.

```bash
find /srv/app/uploads/tmp -xdev -type f -mmin -60 | wc -l
find /srv/app/uploads/tmp -xdev -type f -mmin +1440 -print0 | du -ch --files0-from=- | tail -1
find /srv/app/uploads/tmp -xdev -mindepth 1 -type f -mmin +1440 | head -50
# after your go:
find /srv/app/uploads/tmp -xdev -mindepth 1 -type f -mmin +1440 -delete
```

I leave empty folders in place. They use no real space, and the app may expect them.

To stop it filling again, I suggest one systemd-tmpfiles rule. The daily `systemd-tmpfiles-clean.timer` then removes files older than one day:

```
# /etc/tmpfiles.d/app-uploads.conf
e /srv/app/uploads/tmp - - - 1d
```

The better long-term fix is for the app to delete its own temp files. 31G suggests a cleanup job is missing or broken.

### 3. Git branches (cleanup, not space)

1. Record the current branch.
2. Save every branch name and commit ID to a file. This file lets us restore any branch.
3. List the merged and unmerged branches.
4. Delete only merged branches, and keep the branches you name. `git branch -d` refuses to delete unmerged branches.
5. Leave unmerged branches until you decide.
6. If `.git` is under a few GB, skip `git gc`.

```bash
git -C /srv/app branch --show-current
git -C /srv/app for-each-ref refs/heads --format='%(refname:short) %(objectname)' > ~/branches-2026-10-12.txt
git -C /srv/app branch --merged main --format='%(refname:short)' | grep -vxE 'main|master'
git -C /srv/app branch --no-merged main
# after your go (KEEP = your list of branches to keep):
git -C /srv/app branch --merged main --format='%(refname:short)' | grep -vxE "main|master|$KEEP" | xargs -r git -C /srv/app branch -d
```

To restore a branch, run `git branch <name> <sha>` with a line from the saved file. This works until `git gc` removes the commits.

### 4. Docker (optional, needs your go)

```bash
docker image prune     # dangling images only
docker builder prune   # build cache
```

**Warning: Do not run `docker system prune -a --volumes` or `docker volume prune` on this box.** These commands can delete volumes, and a volume may hold your database. Also, `-a` deletes images of stopped containers, and one of those can be your rollback image.

If container logs are large, the fix is log rotation in `/etc/docker/daemon.json`. That change needs a Docker restart, which stops the app for a moment, so it needs a separate go.

## What I need from you

1. **Access.** I run on your WSL machine, not on the server. Either give me an SSH host and user with sudo, or run the commands yourself and paste the output. Which do you prefer?
2. **Branch names.** Tell me the main branch name. Tell me which branches must stay, such as deploy, release, or rollback branches.
3. **Unpushed work.** Does anyone commit directly on this box? If so, unmerged branches may hold the only copy of that work.
4. **`uploads/tmp` rules.** Tell me what writes to it. Does the app ever read a file from `tmp` after the upload finishes? Is a 24-hour cutoff safe?
5. **Docker.** Go or no-go on the image and build cache prune.
6. **Per-step go.** Give a go for each delete step after you see its dry run output.

Steady hands on the delete key, centurion. The disk does not take this hill.