You want to free space on the prod box. You asked for two actions: delete old branches in `/srv/app` and empty `/srv/app/uploads/tmp`. This is a plan only, and I run nothing before your go. The goal is a disk well below 94% with no harm to the live app.

## Verdict

- **`uploads/tmp` (31G) is the real win.** Delete only files older than 24h. That way, in-progress uploads stay safe.
- **Deleting git branches frees almost no space.** A branch is a tiny ref file. Git keeps the commits for about 90 days through reflogs, until `gc` prunes them. Do it to tidy up, and only after we confirm that no branch has unpushed work.
- **Docker (48G) is a bigger target that you did not list.** Dangling images, build cache, and container logs are usually safe to remove.
- **About 109G is not explained** (188G used, minus 31G and 48G). We must find it before we decide on anything else.
- **The cause stays unless we fix it.** Something fills `uploads/tmp` and nothing cleans it. It will fill again.

## Plan

**Phase 1: Read-only checks (no changes)**

1. Find the biggest directories:
   `sudo du -xh --max-depth=2 / 2>/dev/null | sort -h | tail -25`
2. Find deleted files that a process still holds open: `sudo lsof +L1`
3. Show Docker usage: `docker system df -v`
4. Measure container logs: `sudo sh -c 'du -ch /var/lib/docker/containers/*/*-json.log | tail -1'`
5. Count recent files in tmp: `find /srv/app/uploads/tmp -xdev -type f -mmin -1440 | wc -l`
6. Measure the old files in tmp:
   `find /srv/app/uploads/tmp -xdev -type f -mmin +1440 -printf '%s\n' | awk '{s+=$1} END {printf "%.1f GB\n", s/1e9}'`
7. Measure the repo: `du -sh /srv/app/.git`
8. Show the remote and the current branch: `git -C /srv/app remote -v` and `git -C /srv/app rev-parse --abbrev-ref HEAD`
9. Count local commits that are not on any remote: `git -C /srv/app log --branches --not --remotes --oneline | wc -l`

**Phase 2: Clear `uploads/tmp` (after your go)**

1. Delete files older than 24h:
   `ionice -c3 find /srv/app/uploads/tmp -xdev -type f -mmin +1440 -delete`
2. Delete the empty subdirectories:
   `find /srv/app/uploads/tmp -xdev -mindepth 1 -type d -empty -delete`
3. Check the result: `df -h /`

Do not use `rm -rf /srv/app/uploads/tmp/*`. It can delete uploads that are in progress, and it fails on very large file lists. Keep the `tmp` directory itself, because the app may need it to exist with its current permissions.

**Phase 3: Docker safe prune (after your go)**

1. Remove dangling images: `docker image prune -f`
2. Remove the build cache: `docker builder prune -f`
3. If one container log is very large, truncate it: `sudo truncate -s 0 <path-to-json.log>`

Do not run `docker system prune -a --volumes`. Volumes can hold the database. The `-a` flag also removes the images that a rollback needs.

**Phase 4: Git branches (after your go)**

1. Save each branch and its SHA, for a cheap undo:
   `git -C /srv/app for-each-ref --format='%(refname:short) %(objectname)' refs/heads > ~/branches-2026-10-12.txt`
2. Delete the merged branches:
   `git -C /srv/app branch --merged main | grep -vE '^\*|^ *main$' | xargs -r git -C /srv/app branch -d`
3. If Phase 1 step 9 shows 0, delete the unmerged branches too. Otherwise, list them for you to review first.

I use `-d` and not `-D`, so git refuses to delete unmerged branches. I skip `git gc --prune=now` unless `.git` is many GB. That step is not reversible.

**Phase 5: Stop the repeat**

1. Add a daily cron job or systemd timer that runs the Phase 2 `find` command.
2. Set `max-size` and `max-file` for logs in `/etc/docker/daemon.json`.
3. Add a disk alert at 85%.

Step 2 needs a Docker restart, and the new log settings apply only to new containers. Plan it as a separate change in a maintenance window.

## What I need from you

1. **Access.** I cannot reach the prod box from this session. Give me SSH access (host, user, sudo), or run Phase 1 yourself and paste the output.
2. **Git facts.** Tell me the trunk branch name (`main` or `master`) and the branch the server deploys. Confirm that the remote has every branch you care about, and list the branches to keep.
3. **What uses `uploads/tmp`.** Tell me which process writes there, and if a later job reads files from it. Confirm that 24h is a safe age.
4. **Docker scope.** Confirm that I can prune dangling images and the build cache. I do not touch volumes or running containers in any case.
5. **Backup state.** Tell me if a recent backup or snapshot exists. Phase 2 does not need one, but any work on stateful data does.
6. **A go for each phase.** Phase 1 is read-only. Phases 2 to 5 change prod, so each needs its own go.

Raise the shield wall, Centurion. The disk yields one `find` at a time.