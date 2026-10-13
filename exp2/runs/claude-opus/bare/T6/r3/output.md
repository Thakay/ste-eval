# Plan to free disk space on the prod server

## The main point first

- **Deleting git branches will free almost no space.** A branch is a 41-byte ref file, so 212 of them total a few KB. The commits they point to stay on disk until reflog expiry and `git gc --prune` remove them, and that also removes your ability to undo. I'd still clean up branches if you want a tidier repo, but don't count on it for disk space.
- **`uploads/tmp` (31G) is the real win**, as long as it really is temporary data.
- **About 109G is unaccounted for.** 188G is used, and uploads/tmp plus Docker cover only 79G. Before deleting anything, I'd run `du -xh --max-depth=2 / | sort -h | tail -30` to see where the rest is. Docker (48G) is likely the next-best target, but you didn't ask for it, so I'd only report on it.

## What I'd run first (read-only)

```bash
# uploads/tmp: what is it, how old, is anything using it
findmnt -T /srv/app/uploads/tmp; ls -la /srv/app/uploads/ | grep tmp   # mount point or symlink?
find /srv/app/uploads/tmp -xdev -type f -printf '%TY-%Tm\n' | sort | uniq -c   # age distribution
find /srv/app/uploads/tmp -xdev -type f -mmin -1440 | wc -l                    # files from the last 24h
sudo lsof +D /srv/app/uploads/tmp 2>/dev/null | head                           # open handles

# git: size and branch state
git -C /srv/app count-objects -vH
git -C /srv/app branch --show-current
git -C /srv/app branch -vv            # spot branches with no upstream or "ahead"
git -C /srv/app branch --merged main | wc -l
```

## What I'd then do (after your OK)

**uploads/tmp**
- Delete only files older than the cutoff you approve, and keep the directory itself so its ownership and permissions stay intact:
  `find /srv/app/uploads/tmp -xdev -mindepth 1 -type f -mmin +1440 -delete`, then remove empty subdirectories.
- Check `df -h /` afterward. Then run `lsof +L1`: if the app still holds deleted files open, their space isn't released until the app restarts.

**Branches**
- Back up every ref first: `git for-each-ref --format='%(refname) %(objectname)' > ~/branch-backup-2026-10-12.txt`.
- Delete with `git branch -d`, which refuses to drop unmerged work. Skip `main`, the checked-out branch, and any branches you name.
- Give you a list of unmerged or unpushed branches to decide on yourself.
- No `gc --prune` unless you want it. It frees little and makes the deletions permanent.

## What I need from you

1. **Access.** Should I SSH in (which host and user, and is sudo allowed), or should I give you commands to run and you paste back the output?
2. **uploads/tmp.** What writes there, and is it ever used as permanent storage? Can I delete files older than 24 hours, or do you want a different cutoff? Are in-progress uploads, such as multipart chunks, stored there?
3. **Branches.** Which ones must stay (release branches, the deployed branch)? Is this repo just a deploy clone where everything also exists on the remote? Should unmerged branches be deleted too, or only merged ones?
4. **Backups.** Is there a recent snapshot or backup of this box?
5. **Timing.** Is now okay, or should this wait for a low-traffic window? Running `find` over 31G and any `gc` will add I/O load.
6. **Docker and the missing ~109G.** Do you want me to investigate and propose cleanup? It would be report-only, and I would never use `--volumes`, since volumes may hold database data.

Once these are fixed, I'd suggest a `systemd-tmpfiles` rule or a cron job that ages out `uploads/tmp` automatically so this doesn't come back.