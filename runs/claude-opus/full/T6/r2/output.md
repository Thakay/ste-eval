**What I understood:** You want more free space on the prod box (one Ubuntu server, live app). You named two targets: old git branches in `/srv/app` and the files in `/srv/app/uploads/tmp`. The goal is a disk well below 94% with no harm to the app. I run nothing until you answer the questions below.

**TL;DR:** `uploads/tmp` gives the real gain (31G). Branch deletion gives almost no space. Docker (48G) is probably the second big gain, but it is not on your list, so I need your go for it.

### Where the space is

| Target | Size | Expected gain | Risk |
|---|---|---|---|
| `uploads/tmp` | 31G | Up to 31G | Medium. An upload in progress can break. |
| `/var/lib/docker` | 48G | Unknown until `docker system df` | Low without volumes. High with volumes. |
| Git branches | 212 refs | Close to 0. A branch is a 41-byte file. | Low for merged branches. Unmerged work is lost. |
| Not yet known | about 109G | Unknown | I must look first. |

### Plan

1. **Look first (read-only, no deletes).**
   ```
   du -xh --max-depth=2 / 2>/dev/null | sort -h | tail -30
   docker system df
   du -sh /srv/app/.git
   find /srv/app/uploads/tmp -type f -mmin -1440 | wc -l   # files from the last 24 h
   lsof +D /srv/app/uploads/tmp                          # files the app has open now
   lsof +L1                                              # deleted files that a process still keeps open
   journalctl --disk-usage
   ```
   I show you the numbers before any delete.

2. **Clear `uploads/tmp`, old files only.** I delete files older than an age you choose. Uploads in progress keep a fresh timestamp, so they stay.
   ```
   find /srv/app/uploads/tmp -type f -mmin +1440 -delete
   find /srv/app/uploads/tmp -mindepth 1 -type d -empty -delete
   ```
   If `df` shows no gain after this, a process keeps the deleted files open. A restart of that process releases the space. The restart needs your go.

3. **Delete merged git branches only (local, never the remote).**
   ```
   git -C /srv/app branch --merged main | grep -vE '^\*|^\s*(main|master)$' | xargs -r git -C /srv/app branch -d
   ```
   `-d` refuses to delete a branch with unmerged work. This step gives order, not space. Disk space returns only after the reflog entries expire and `git gc` runs. I do not run `git gc` on prod unless `.git` is large.

4. **Docker (only with your go).**
   ```
   docker builder prune -f
   docker image prune -f      # dangling images only
   ```
   I never use `--volumes`, because volumes can hold database data. `docker image prune -a` also removes the image you need for a rollback, so I use it only on your word.

### Suggestions

- **Stop the regrowth.** 31G in a tmp folder means nothing removes old files there. A systemd-tmpfiles rule fixes that with one line in `/etc/tmpfiles.d/app-uploads.conf`: `e /srv/app/uploads/tmp - - - 1d`.
- **Find the source of the 212 branches.** If a deploy script makes one branch per deploy, the count grows again.

### What I need from you

1. **Access.** SSH host, user, and sudo rights. Or tell me that you prefer to run the commands and paste the output.
2. **`uploads/tmp` rules.** Which part of the app writes there? Does the app read a file from there after the upload ends? Which age is safe to delete: 24 hours, 7 days, or a different value?
3. **Branches to keep.** The name of the main branch and the branch prod runs on now. Tell me if I may also delete unmerged branches, or only merged ones.
4. **Docker.** Go or no-go for the build cache and dangling images. Name any old image or stopped container that you keep for a rollback.
5. **Backup.** Confirm that `uploads/` has a backup, in case `tmp` holds a file that exists nowhere else.
6. **Target.** The free-space level that is enough for you (for example, below 80%).

Hold the line, keeper of the disk. The gates open on your word.