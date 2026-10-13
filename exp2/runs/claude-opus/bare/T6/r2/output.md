# Plan to free disk space on the prod box

## The short version

- **Deleting the git branches won't free meaningful space.** A branch is a ~41-byte ref file. The commits it points to stay on disk until reflog expiry and `git gc`, and only if nothing else references them. On most repos the whole `.git` is well under a few GB. Removing 212 branches is tidying, not a disk fix.
- **`uploads/tmp` (31G) is a real target**, but on prod I'd delete by age only, after confirming nothing still reads those files.
- **Docker (48G) is probably the biggest easy win**, and you didn't mention it. Build cache, dangling images and runaway container logs are common culprits.

I'm running locally (WSL), not on the prod server. So either you run the commands below and paste the output, or you give me access.

## Step 1: Read-only checks (nothing deleted)

```bash
# uploads/tmp: how much is old, and is anything active?
find /srv/app/uploads/tmp -type f -mtime +7 -printf '%s\n' | awk '{s+=$1} END {print s/1e9 " GB older than 7d"}'
find /srv/app/uploads/tmp -type f -mmin -60 | wc -l      # files touched in the last hour
sudo lsof 2>/dev/null | grep /srv/app/uploads/tmp | head
crontab -l; systemctl list-timers                         # was there a cleanup job that stopped?

# git: what it actually costs
git -C /srv/app count-objects -vH
du -sh /srv/app/.git
git -C /srv/app branch --merged main | wc -l

# docker
docker system df -v
sudo du -sh /var/lib/docker/{overlay2,containers,volumes}
sudo find /var/lib/docker/containers -name '*-json.log' -size +500M -exec ls -lh {} \;

# other cheap wins
journalctl --disk-usage; sudo du -sh /var/log /var/cache/apt
```

## Step 2: Deletions (only after you confirm)

1. **uploads/tmp**
   - Run `find /srv/app/uploads/tmp -type f -mtime +N -print` first and review the list.
   - Then run the same command with `-delete`, plus `find ... -mindepth 1 -type d -empty -delete`.
   - Keep the directory itself so ownership and permissions stay as the app expects.
   - Check `df` afterwards. If space didn't come back, a process is holding deleted files open (`lsof +L1`).
2. **Docker**
   - Safe: `docker builder prune` and `docker image prune` (dangling images only).
   - Only with your OK: `docker image prune -a`, since it removes old images you might need for rollback.
   - Never: `docker volume prune` without inspecting the volumes first, because they may hold DB data.
   - Truncate oversized container logs.
3. **Git**
   - Use `git branch -d` on branches already merged into main. It refuses to delete unmerged branches.
   - I'll list the unmerged ones for you to decide on.
   - I'd skip `reflog expire --expire=now` / `gc --prune=now` unless `.git` turns out to be large. It's irreversible and only pays off then.
4. **Prevent a repeat**
   - Add a cron job or systemd timer for tmp cleanup.
   - Set Docker log limits (`max-size`/`max-file` in `daemon.json`). This needs a Docker restart, which means app downtime, so it needs a maintenance window.

## What I need from you

1. **Access:** will you run the commands and paste the output, or give me a way onto the box?
2. **uploads/tmp:** what writes there, and does anything read those files later (resumable uploads, background jobs)? What age cutoff is safe: 24h, 7d?
3. **Branches:** is the goal space or tidiness? Local branches only, or also on the remote? Is the main branch `main` or `master`? May I delete unmerged branches, or only merged ones?
4. **Docker:** may I include it? Do you roll back by redeploying old image tags? Do any volumes hold persistent data?
5. **Safety net:** is there a recent backup or snapshot of the box? When is a restart window acceptable, if we need one?