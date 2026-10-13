Before anything runs, three things change the plan. Deleting branches frees almost no space on its own. Docker (48G), which you showed but didn't ask about, is probably the biggest safe win. And about 109G of the 188G used is not explained by anything you listed yet.

**What I understood:** free space on the prod box by deleting old branches in `/srv/app` and clearing `/srv/app/uploads/tmp`. You want the plan and my questions first, with nothing run yet.

## The options

| Target | Likely gain | Risk | My take |
|---|---|---|---|
| `uploads/tmp` | up to 31G | Breaks uploads still in progress. The folder may hold files that aren't really temporary. | Do it, but only for files older than 24h |
| Docker | often 10 to 30G from unused images and build cache | Removing images you need for a rollback. Removing volumes deletes data. | Recommend it. Never touch volumes. |
| Git branches | close to 0 | Losing work that exists only on prod. `gc` can't be undone. | Only if `.git` turns out to be large |

**Why branches barely help:** a branch is a 41-byte pointer. Disk space only comes back after you expire the reflog and run `git gc`. Even then, you only get back commits that no other branch points to. Check `du -sh /srv/app/.git` first. If it's a few GB or less, skip this step.

## Plan

**1. Look around first (read-only, safe):**
```bash
du -xh --max-depth=1 / 2>/dev/null | sort -h | tail -15   # where is the other ~109G
du -sh /srv/app/.git
docker system df                                           # what is reclaimable
find /srv/app/uploads/tmp -type f -mmin -60 | wc -l        # files touched in the last hour
sudo lsof +D /srv/app/uploads/tmp | head                   # files open right now
sudo lsof +L1 | head                                       # deleted files still holding space
```

**2. `uploads/tmp`:** list the files first, then delete only old ones. I'd keep the folder itself, since the app may expect it to exist with its current owner and permissions.
```bash
find /srv/app/uploads/tmp -type f -mtime +0 | head -50    # preview
find /srv/app/uploads/tmp -type f -mtime +0 -delete
find /srv/app/uploads/tmp -mindepth 1 -type d -empty -delete
```
After that, fix the root cause. Something let this folder grow to 31G. Add a cleanup rule, either a daily cron `find` or a `systemd-tmpfiles` entry.

**3. Docker (if you approve):**
```bash
docker builder prune --filter until=168h
docker image prune -a --filter until=168h   # unused images older than 7 days
```
- No `docker system prune --volumes`, ever, on this box.
- Also check container logs under `/var/lib/docker/containers/*/*-json.log`. If they're large, set `max-size` and `max-file` in `daemon.json`.

**4. Git (only if `.git` is large):**
- Delete merged branches with `git branch -d`, which refuses to delete unmerged work.
- Then run `git reflog expire --expire=now --all && git gc --prune=now`. This step can't be undone.

**5. Verify:** run `df -h /` again. Also re-run `lsof +L1`. A process holding a deleted file open keeps that space in use until the process is restarted.

## What I need from you

1. **Access.** I can't reach prod from this WSL session. Either give me the SSH host and user with sudo, or run the commands yourself and paste the output back.
2. **`uploads/tmp`.**
   - What writes to this folder?
   - Is everything in it truly temporary?
   - Is a 24h age cutoff OK?
   - Is there a low-traffic window to do this in?
3. **Branches.**
   - What counts as "old": merged into main, or older than some date?
   - Which branches must stay? For example main, the branch currently deployed, and `release/*`.
   - Are all branches pushed to a remote, or is prod the only copy of some of them?
4. **Docker.** Is it OK to prune build cache and unused images older than 7 days? If you roll back by re-running old image tags, tell me how far back I need to keep.
5. **Backup.** Is there a recent snapshot of the box or volume, in case something goes wrong?

Send me the read-only output from step 1 together with your answers, and I'll turn this into exact commands with real numbers.

Clear the armory crate by crate, quartermaster. Nothing burns until you give the word.