**Echo back:** You want to free disk space on the prod box. You asked for a plan and a list of what I need first. I run nothing until you give the go.

**TL;DR:** Clear only the old files in `uploads/tmp`. Look at Docker next, because it is the largest item at 48G. Branch deletion gives almost no space, so treat it as cleanup, not as a fix.

| Target | Likely gain | Main risk |
|---|---|---|
| `/srv/app/uploads/tmp` | Up to 31G | Uploads in progress break. Some files may be the only copy. |
| Docker images, build cache, container logs | Unknown. `docker system df` shows it. | Volumes hold data. I will not touch volumes. |
| Git branches | Close to 0 | Unpushed work on a branch is lost. |

A branch is a 41-byte file. Its commits stay in `.git/objects` until the reflog expires and `git gc` runs. Shared commits stay always.

## Plan

**Phase 1: read-only checks (no changes)**
1. Measure the git store: `du -sh /srv/app/.git`. If it is small, skip `git gc`.
2. Find unpushed work: `git -C /srv/app log --branches --not --remotes --oneline`.
3. List merged branches: `git -C /srv/app branch --merged main`.
4. Count new files: `find /srv/app/uploads/tmp -type f -mmin -1440 | wc -l`.
5. Find open files: `lsof +D /srv/app/uploads/tmp`.
6. Search the app config and code for `uploads/tmp` to find what writes there.
7. Show Docker usage: `docker system df -v`.
8. Find large container logs: `du -sh /var/lib/docker/containers/*/*-json.log | sort -h | tail`.
9. Find deleted files that a process still holds open: `lsof +L1`.

**Phase 2: delete (only after your go)**
1. Save a file list: `find /srv/app/uploads/tmp -type f > /root/uploads-tmp-2026-10-12.txt`.
2. Delete old files: `find /srv/app/uploads/tmp -type f -mmin +1440 -delete`. The age filter keeps uploads in progress safe.
3. Remove empty folders: `find /srv/app/uploads/tmp -mindepth 1 -type d -empty -delete`.
4. Remove dangling images and build cache: `docker image prune` and `docker builder prune`.
5. If you approve, empty the large container logs with `truncate -s 0 <log>`.
6. Delete merged branches that also exist on the remote. Use `git branch -d`, which refuses unmerged branches.
7. Check the result: `df -h /`.
8. If the space does not come back, find the holder with `lsof +L1`. I ask you before I restart any process.

I will not run `docker volume prune`, `docker system prune --volumes`, `rm -rf` on the folder itself, or `git branch -D` in bulk.

**Phase 3: stop the growth (separate go)**
1. Add a daily systemd timer that deletes `uploads/tmp` files older than your age limit.
2. Set log rotation in `/etc/docker/daemon.json`. This needs a Docker restart, and the setting applies only to containers that you create again.
3. Find out why `uploads/tmp` grew to 31G. Failed uploads that the app does not clean up are a likely cause.

## What I need from you

1. **Access.** I cannot reach the server from here. Give me SSH host, user, and sudo. Or run the commands and paste the output.
2. **`uploads/tmp` rules.** Tell me what writes there. Confirm that no file there is the only copy. Pick the age limit. I suggest 24 hours.
3. **Docker rollback.** I plan to remove dangling images only. `docker image prune -a` frees more but deletes old tagged images. Tell me if you use those for rollback.
4. **Branches.** Tell me which branches to keep. My default is to keep all unpushed branches.
5. **Go.** Give an explicit go for Phase 2. Phase 3 needs its own go.

Hold the shield wall, keeper of the disk.