**Understood:** you want real free space on the prod box (94% full) by deleting old branches in `/srv/app` and emptying `/srv/app/uploads/tmp`, without breaking the live app.

**Verdict:** `uploads/tmp` (31G) is the real win. Deleting branches alone frees close to nothing, because a branch is a tiny pointer file. Docker (48G) is likely the bigger lever you didn't mention, and about 109G is still unaccounted for. I have not run anything. I'm on your local WSL machine, so I can't reach the prod box yet.

## Plan

**Step 0: look first (read-only, safe)**
```
du -xh --max-depth=1 / | sort -h          # where the other ~109G lives
du -sh /srv/app/.git                      # is the repo even worth cleaning
docker system df                          # how much of the 48G is reclaimable
find /srv/app/uploads/tmp -type f -mmin -60 | head      # files being written right now
find /srv/app/uploads/tmp -type f -mtime +1 | wc -l     # files older than 1 day
lsof +D /srv/app/uploads/tmp              # which process uses it (can be slow)
```

**Step 1: uploads/tmp**
- Delete by age, not `rm -rf`, so uploads in progress survive:
  ```
  find /srv/app/uploads/tmp -mindepth 1 -type f -mtime +1 -delete
  find /srv/app/uploads/tmp -mindepth 1 -type d -empty -delete
  ```
- Then run `lsof +L1`. Deleted files that a process still holds open keep using disk until it lets go, which may mean an app restart.
- Stop the refill: add a daily cleanup (systemd-tmpfiles rule or cron running the same `find`). Also worth finding out why the app leaves 31G behind.

**Step 2: git branches**
- Keep `main`, the branch prod is checked out on, and any release branches.
- Delete only branches already merged:
  ```
  git -C /srv/app branch --merged main      # review this list with you first
  git -C /srv/app branch -d <names>         # -d refuses unmerged branches
  ```
- Unmerged branches go on a list for you to decide on. No `-D`.
- Space only comes back if `.git` is large. Git also keeps unreachable objects for a grace period of weeks. Forcing it now (`git reflog expire --expire-unreachable=now --all && git gc --prune=now`) makes the deletion permanent. This is only worth doing if Step 0 shows `.git` is several GB.

**Step 3 (my suggestion, not in your ask): Docker**
```
docker image prune      # dangling images only
docker builder prune    # build cache
```
I would never run `docker system prune -a --volumes` on prod, because volumes may hold your database. This step needs its own go.

## What I need from you

1. **Access.** The SSH host and user, and whether I have sudo. Or you run the commands and paste me the output.
2. **uploads/tmp.** What writes there? Is it ever the only copy of a user's upload, for example files waiting on a processing job that failed? How old must a file be before it's safe to delete: 1 day, 7 days?
3. **Branches.** Which ones to keep (`main`, the deployed branch, `release/*`?). Is the remote the source of truth, meaning all work worth keeping is already pushed?
4. **Docker.** Go or no-go on Step 3, and do you keep old images for rollback?
5. **Timing.** Is it OK to run during traffic, or should we wait for a quiet window? Deleting 31G and running `git gc` both put load on the disk.

Nothing on this box can be undone once deleted. There is no recycle bin. Before each delete I'll show you the exact list and size, then wait for your go.

Hold the line, disk-warden. We reclaim the ground byte by byte.