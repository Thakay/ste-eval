**TL;DR:** Clearing `uploads/tmp` frees up to 31G. Deleting branches frees almost no space. Docker uses 48G and is the bigger target, but I will not touch it without your go.

**What I understood:** The single prod box is at 94% disk. You want space back by deleting old branches in `/srv/app` and by clearing `/srv/app/uploads/tmp`. The goal is a safe disk level without breaking the live app.

## Problems with the plan as written

- **Branches are tiny.** A branch is a 41-byte pointer. Git frees space only after `git gc` removes objects that no branch and no reflog points to. The reflog keeps objects for 90 days by default. 212 branches can free a few MB, or almost nothing.
- **`uploads/tmp` can hold active uploads.** If I delete a file while the app writes it, that upload fails. I will delete only files older than a cut-off age, not the whole folder.
- **Deleted files can still use space.** If a process keeps a deleted file open, the disk does not get the space back. `lsof +L1` shows these files.
- **31G in a tmp folder means the cleanup is broken or missing.** If we do not fix the cause, the disk fills again.
- **About 109G is in other places.** 31G plus 48G is 79G of 188G used. A quick survey will show where the rest is.

## Plan

**Phase 1: read-only checks.** These change nothing.

1. Find the big folders: `sudo du -xh --max-depth=2 / 2>/dev/null | sort -h | tail -30`
2. Measure the repo: `du -sh /srv/app/.git` and `git -C /srv/app count-objects -vH`
3. List branches with their upstream state: `git -C /srv/app branch -vv`
4. List branches merged into main: `git -C /srv/app branch --merged main`
5. Measure old tmp files: `find /srv/app/uploads/tmp -type f -mmin +1440 -printf '%s\n' | awk '{s+=$1} END {print s/1e9 " GB"}'`
6. Find deleted files that processes still hold open: `sudo lsof +L1`
7. Find the job that must clean `uploads/tmp`. Look in cron, systemd timers, and the app config.
8. See how Docker uses its space: `docker system df`

Then I send you the numbers and the exact delete commands for your go.

**Phase 2: delete steps.** I run these only after your go.

9. Delete tmp files older than 24 hours: `find /srv/app/uploads/tmp -type f -mmin +1440 -delete`
10. Remove the empty folders: `find /srv/app/uploads/tmp -mindepth 1 -type d -empty -delete`
11. If `.git` is big, delete merged branches only. `-d` refuses unmerged branches and the checked-out branch:
    ```
    git -C /srv/app branch --merged main --format='%(refname:short)' | grep -vxE 'main|master' | xargs -r git -C /srv/app branch -d
    ```
12. If you want the branch space back now, run `git -C /srv/app reflog expire --expire=now --all`, then `git -C /srv/app gc --prune=now`.
13. If you add Docker to the scope, run `docker image prune` and `docker builder prune`.

**Warnings:**

- Do not run step 12 unless you accept the risk. After it, you cannot recover deleted branches from this repo.
- Do not run `docker system prune --volumes` or `docker volume prune`. Volumes can hold database data.
- I will not delete unmerged branches. I will list them, and you decide.

## What I need from you

1. **Access.** Do I get SSH with sudo? Or do you run the commands and paste the output to me?
2. **Tmp rules.** What writes to `uploads/tmp`? Does anything read those files later? Is a 24-hour cut-off safe?
3. **Branch rules.** What is "old" for you: merged into main, or no commits for N days? What is the main branch name? Which branches must stay?
4. **Repo role.** Is `/srv/app` the live deploy checkout? Do the branches also exist on a remote?
5. **Docker scope.** Do you want me to include Docker?
6. **Timing.** Can I run Phase 2 while the app is live, or do you want a maintenance window?

Steady hands on the hilt, Vanguard. Clear the field.