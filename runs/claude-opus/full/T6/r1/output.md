**Short answer:** Deleting branches frees almost no space. `uploads/tmp` (31G) and Docker (48G) hold the real space. I run nothing until you answer the questions at the end.

**What I understood:** You want more free disk on the prod box. You asked for two actions: delete old branches in `/srv/app` and clear `/srv/app/uploads/tmp`.

**Why branches do not help:** A branch is a 41-byte pointer file. Git deletes the commits only when `git gc` runs and no other branch, tag, or reflog points to them. 212 branches are probably a few kilobytes.

## Plan

**1. Read-only checks (no change to the server)**

```bash
du -sh /srv/app/.git                                   # is the repo big at all?
docker system df                                       # what Docker can reclaim from the 48G
sudo lsof +L1                                          # deleted files that a process still holds open
find /srv/app/uploads/tmp -type f -mmin -60 | wc -l    # files from the last hour (active uploads)
find /srv/app/uploads/tmp -type f -mtime +1 -printf '%s\n' | awk '{s+=$1} END {printf "%.1f GB\n", s/1e9}'
sudo du -sh /var/lib/docker/containers                 # container logs
sudo journalctl --disk-usage
```

The `lsof +L1` check matters. If the app holds deleted files open, `df` does not show that space as free until the app restarts.

**2. Clear `uploads/tmp` by age**

```bash
find /srv/app/uploads/tmp -type f -mtime +1 -delete
find /srv/app/uploads/tmp -mindepth 1 -type d -empty -delete
```

- This keeps files from the last 24 hours, so active uploads do not break.
- I do not use `rm -rf uploads/tmp/*`. It breaks active uploads, and the shell glob can fail with a very large number of files.
- The `tmp` folder stays, with its owner and permissions.
- This step alone can recover up to 31G (94% to about 79%).

**3. Docker (you did not ask for this, but it is the largest item)**

```bash
docker builder prune      # build cache
docker image prune -a     # images that no container uses
```

- I never prune volumes. Volumes can hold database data.
- `image prune -a` removes old release images. If you revert a release from a local image, the box must pull that image again.

**4. Branches**

```bash
git -C /srv/app for-each-ref --format='%(refname:short) %(objectname)' refs/heads > ~/branches-2026-10-12.txt
git -C /srv/app branch --merged main
git -C /srv/app branch -d <merged branches>
```

- The first command saves every branch name and commit. You can restore any branch with `git branch <name> <sha>` while its commits exist.
- `-d` refuses unmerged branches. I give you that list. I do not use `-D`.
- I skip `git gc` unless `.git` is large. `gc` removes the restore path, and it uses a lot of CPU and disk on prod.

**5. Stop the problem from returning**

31G in a tmp folder means that nothing removes old files. I suggest a daily cron job with the `find` command from step 2. If container logs are large, I suggest log rotation in `/etc/docker/daemon.json`. That change needs a Docker restart, so it needs a maintenance window.

## What I need from you

1. **Access.** How do I run commands on the box? Give me an SSH host and a sudo user, or run the commands yourself and paste the output.
2. **`uploads/tmp` rules.** Which process writes there? Can a file older than 24 hours still be necessary, for example for a job that processes files later? Is 24 hours the correct cutoff?
3. **Meaning of "old branch".** Is "merged into `main`" correct, and is `main` the correct name? Does the remote have all these branches, or is this box the only copy of some? Why does prod have 212 branches? If a deploy script makes one per release, the count grows again.
4. **Docker.** Can I prune build cache and unused images? Do you revert releases from local images?
5. **A "go" for each delete step.** After step 1, I show you the numbers and the exact file and branch lists. I delete only after your "go".

Steady hands, Centurion. We cut only what we have counted.