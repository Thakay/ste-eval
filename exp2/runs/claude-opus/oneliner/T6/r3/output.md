# Plan to get disk space on the prod server

## Removing branches gives almost no disk space

A git branch is a small file of approximately 41 bytes. If you remove 200 branches, you get less than 1 MB. Git keeps the commits in `.git/objects`. Only `git gc` removes them, and only if no other branch or reflog uses them. If you merged the branches into `main`, then `main` still uses those commits.

The large items are `uploads/tmp` (31 GB) and Docker (48 GB). Start with these two items.

## What I need from you

1. **Access.** This session cannot connect to the prod server. You must run the commands and send me the output. Or, tell me a different method of access.
2. **uploads/tmp.** Tell me:
   - Which part of the app writes files to this directory?
   - Does the app use a file after the upload is complete? An example is a processing queue.
   - Which file age is safe to remove? I suggest files older than 2 days.
3. **Branches.** Tell me:
   - The name of the main branch (`main` or `master`).
   - The branches that we must keep, for example `release/*` or `production`.
   - Does a remote, for example GitHub, have a copy of all branches? If the prod repo has the only copy of a branch, a removal can cause loss of work.
4. **Docker.** Tell me if I can clean Docker data. Tell me which old images are necessary for a rollback.
5. **Time.** When you remove many files, the disk load increases. Tell me a time with low traffic.

## Step 1: Examine the server

These commands only read data. They do not change data.

```bash
# Size of the git data
du -sh /srv/app/.git

# Number of branches that you merged into main
git -C /srv/app branch --merged main | wc -l

# Files in uploads/tmp: number of new files, and size of old files
find /srv/app/uploads/tmp -type f -mtime -2 | wc -l
find /srv/app/uploads/tmp -type f -mtime +1 -printf '%s\n' | awk '{s+=$1} END {printf "%.1f GB\n", s/1e9}'

# Processes that have files open in uploads/tmp (stop with Ctrl+C if too slow)
lsof +D /srv/app/uploads/tmp

# Removed files that a process keeps open. These files still use disk space.
lsof +L1

# Docker disk use
docker system df

# Container logs. "docker system df" does not show these.
du -sh /var/lib/docker/containers/*/*-json.log | sort -h | tail
```

## Step 2: Clean uploads/tmp

```bash
# Remove files older than 2 days, with low disk priority
ionice -c3 nice -n19 find /srv/app/uploads/tmp -type f -mtime +1 -delete

# Remove empty subdirectories, but keep the tmp directory
find /srv/app/uploads/tmp -mindepth 1 -type d -empty -delete

df -h /
```

Do not use `rm -rf /srv/app/uploads/tmp`. This command also removes the directory, and the app can fail. It also removes uploads that are in progress. With many files, `rm -rf /srv/app/uploads/tmp/*` can fail with "Argument list too long".

If `df` does not show more free space, a process keeps the removed files open. `lsof +L1` shows that process. Restart the process to release the space.

## Step 3: Clean Docker (only if you agree)

```bash
docker container prune    # stopped containers
docker image prune        # images without a tag
docker builder prune      # build cache
docker system df
```

Do not use `docker system prune -a --volumes`. Volumes can contain database data. The `-a` option also removes old images that are necessary for a rollback.

If the container logs are large, set a log size limit in `/etc/docker/daemon.json`. I will send you the settings.

## Step 4: Remove git branches (for order, not for disk space)

```bash
cd /srv/app

# Save all branch names and commits. With this file, you can restore a branch.
git for-each-ref --format='%(refname:short) %(objectname)' refs/heads/ > ~/branches-2026-10-12.txt

# Make a list of merged branches. Keep the important branches.
git for-each-ref --merged=main --format='%(refname:short)' refs/heads/ \
  | grep -vxE 'main|master|production|release/.*' > ~/branches-to-remove.txt

# Examine the list before you continue
cat ~/branches-to-remove.txt

# Remove the branches. "-d" removes only merged branches.
xargs -r git branch -d < ~/branches-to-remove.txt
```

To restore a branch, use `git branch <name> <commit>` with a line from the saved file.

I do not use `git branch -D`. That option also removes branches that are not merged. I do not run `git gc` on prod. It gives little disk space, and it uses CPU and temporary disk space.

## After the cleanup

The app does not clean `uploads/tmp`. Thus, the problem will occur again. Add a daily cleanup with `systemd-tmpfiles` or `cron`. I can write this rule after you answer the questions.