# Plan to make disk space available on the prod server

I do not run commands now. This is my plan and the data that I need from you.

## Two important facts

1. **Removal of git branches gives almost no disk space.** A branch is only a small reference file. Git keeps the commits if other branches or the reflog refer to them. Thus, I recommend this step only for order, not for space.
2. **Most of the used space is in other locations.** `uploads/tmp` (31G) plus Docker (48G) is 79G. 188G is in use. Thus, 109G is in other directories. I must find them first.

## Step 1: Examine the server (read-only)

These commands do not change the server.

```bash
sudo du -xh --max-depth=2 / 2>/dev/null | sort -rh | head -30
sudo docker system df -v
sudo journalctl --disk-usage
sudo lsof +L1                                   # removed files that a process keeps open
du -sh /srv/app/.git
sudo lsof +D /srv/app/uploads/tmp | head        # files that the app uses now
find /srv/app/uploads/tmp -type f -mmin -60 | wc -l   # files from the last hour
find /srv/app/uploads/tmp -type f -mtime +7 -printf '%s\n' | awk '{s+=$1} END {print s/1e9 " GB"}'
```

## Step 2: Clean `/srv/app/uploads/tmp`

I do not use `rm -rf /srv/app/uploads/tmp/*`. The app can use some files now, for example an upload that is not complete. I remove only old files.

First, I show you the list:

```bash
find /srv/app/uploads/tmp -xdev -type f -mtime +7 -print | head -50
```

After you agree, I remove the files:

```bash
find /srv/app/uploads/tmp -xdev -type f -mtime +7 -delete
```

`find` does not follow symbolic links. `-xdev` keeps `find` on the same file system.

**CAUTION:** If a process keeps a removed file open, the space does not become available. The `lsof` commands in Step 1 find these processes.

## Step 3: Clean Docker (recommended, largest item)

```bash
sudo docker image prune -a --filter "until=168h"   # images that no container uses, older than 7 days
sudo docker builder prune --filter "until=168h"     # old build cache
```

Container logs can also be large. They are in `/var/lib/docker/containers/*/*-json.log`. The correct repair is a log size limit in `/etc/docker/daemon.json`. I show you the large logs before I do a change.

**CAUTION:** I do not use `docker system prune --volumes`. Volumes can contain database data.

## Step 4: Remove old git branches (for order only)

First, I show you the branches that are merged into the main branch:

```bash
git -C /srv/app branch --merged main | grep -vE '^\*|^\s*(main|master)$'
git -C /srv/app branch -vv     # shows branches with no remote or with commits that are not pushed
```

After you agree, I use `git branch -d`. I do not use `-D`. The `-d` option does not remove a branch that is not merged.

## What I need from you

1. **Step 1:** Tell me that I can run the read-only commands. Or run them and give me the output.
2. **`uploads/tmp`:**
   - Which process writes to this directory?
   - Does a process read files from it later, for example a queue job?
   - Which file age is safe to remove? If you do not give a value, I use 7 days.
   - Is there a backup? If not, the removed files are permanently lost.
3. **Git branches:**
   - What is "old"? Merged into main, or no commit for a number of months?
   - What is the name of the main branch?
   - Is `/srv/app` only a deploy copy? Or do persons do work in it?
   - Do all branches also exist on the remote?
4. **Docker:** Can I include Docker? Do you use old images for rollback? If yes, tell me which tags to keep.
5. **Time:** Can I do this now? The removal of many files causes high disk load. A low-traffic period is better.
6. **Access:** Tell me which user to use, and if I can use `sudo`.

I do each removal step only after you agree to that step.