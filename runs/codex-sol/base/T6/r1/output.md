The 31 GB in `uploads/tmp` is the main opportunity. If all of it is safely reclaimable from `/`, usage would fall from roughly 94% to 79%. Git branch count tells us little about disk usage.

I would:

1. **Inspect first using read-only checks.** Confirm the host and filesystem, measure `.git`, and identify temporary files, active uploads, and files held open by running processes.
2. **Prepare a cleanup list.** Select temporary files using the app’s retention rules. Identify old local branches that are merged into the intended mainline and unused by deployments or worktrees.
3. **Delete the approved candidates.** Preserve the temporary directory and its permissions. Preserve protected branches and branches containing unmerged work.
4. **Verify reclaimed space and app health.** Deleted files held open by processes may continue consuming disk space until those processes release them.

Deleting branch references usually frees very little directly. Git object cleanup would need separate assessment. Likewise, Docker’s 48 GB total does not establish how much is disposable.

Before running anything, I need:

- **The production host and access method**, including the account to use.
- **The temporary-file lifecycle:** what writes there, when files become disposable, and whether uploads or workers are currently active. If unknown, the first step is investigation.
- **The branch policy:** what “old” means, which branches are protected, and which mainline determines whether work is merged.
- **Approval of the concrete deletion list after inspection**, with a recovery plan for anything that needs preserving.

I have not run commands or looked anything up.

Godspeed, Spartan.