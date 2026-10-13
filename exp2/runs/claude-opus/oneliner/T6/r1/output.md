# Plan to make disk space available on the prod server

I did not do any commands. I do not have access to the prod server from this session.

## Important: the git branches give almost no space

A git branch is a very small pointer file. 212 branches use less than 1 MB. The commits on these branches stay on the disk until `git gc` removes them. The reflog also keeps these commits for 90 days by default. Thus, the branch removal will make the list smaller, but it will not free much disk space.

The large items are `/srv/app/uploads/tmp` (31G) and `/var/lib/docker` (48G).

## Step 1: Measure first (these commands do not change data)

```
du -sh /srv/app/.git
git -C /srv/app branch --show-current
git -C /srv/app status --short
docker system df
find /srv/app/uploads/tmp -type f -mmin -60 | wc -l
find /srv/app/uploads/tmp -type f -printf '%TY-%Tm\n' | sort | uniq -c
```

These commands show:
- The size of the git data.
- The branch that is deployed now. Do not remove this branch.
- If the app writes files to `uploads/tmp` now.
- The age of the files in `uploads/tmp`.
- The quantity of docker space that you can recover.

## Step 2: Remove old files from `uploads/tmp`

Do not remove all the files. The app can use some files now, for example uploads that are not complete. Remove only old files:

```
find /srv/app/uploads/tmp -type f -mtime +2 | head -50     # examine the list first
find /srv/app/uploads/tmp -type f -mtime +2 -delete
find /srv/app/uploads/tmp -mindepth 1 -type d -empty -delete
```

**CAUTION:** You cannot recover the removed files. Make sure that the app does not keep permanent data in this directory.

If a process keeps a removed file open, the disk space does not become free. Use `lsof +L1` to find that process.

31G in a tmp directory usually shows that a clean-up job does not operate correctly. Find the cause. If you do not find the cause, the disk will become full again.

## Step 3: Remove the merged git branches

Remove only the branches that are merged into the main branch:

```
git -C /srv/app branch --merged main --format='%(refname:short)' \
  | grep -vxE 'main|master|<DEPLOYED_BRANCH>'                 # examine the list first
# then add: | xargs -r git -C /srv/app branch -d
```

The `-d` flag does not remove a branch that has unmerged commits. I will not use `-D` without your permission.

Do not do `git gc` during high load. It uses CPU and disk on the prod server.

## Step 4: Docker (not in your request, but the largest possible gain)

I will do this step only if you tell me to do it.

```
docker image prune      # removes only dangling images
docker builder prune    # removes the build cache
```

**CAUTION:** Do not use `docker system prune -a --volumes`. Volumes can contain database data. The `-a` flag also removes old images that you can use for a rollback.

## What I need from you

1. **Access.** Tell me how to operate on the server. Do I use SSH, or do you do the commands and send me the output?
2. **Branch names.** Tell me the name of the main branch and the deployed branch.
3. **"Old" branches.** I will remove merged branches only. Tell me what to do with the unmerged branches. Does the remote have a copy of them?
4. **`uploads/tmp`.** Tell me which process writes to this directory. Tell me the age limit for removal. I recommend 2 days.
5. **Backup.** Tell me if a backup or a disk snapshot of the server is available.
6. **Docker.** Tell me if I can do Step 4.
7. **Time.** Tell me a time with low load. The `find` and `git gc` commands put a load on the disk.