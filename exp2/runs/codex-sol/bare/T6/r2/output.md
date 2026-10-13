I’d prioritize `/srv/app/uploads/tmp`: it contains 31G. Deleting Git branches usually frees negligible space because branches are small references and their commits may remain retained.

What I would do:

1. Run read-only checks to verify the host, filesystem, repository state, and application use of the temporary directory.
2. Inventory temporary files, then delete only those covered by an agreed retention rule. Preserve the directory and its permissions; coordinate with upload workers so active uploads or jobs aren’t disrupted.
3. List local branches merged into your designated integration branch, exclude protected branches and branches used by deployments or worktrees, then delete approved candidates using `git branch -d`.
4. Check disk usage afterward. Deleted files held open by processes won’t release space until those handles close.

If all 31G is disposable and reclaimable on `/`, usage could drop from 94% to roughly 79%. Docker’s 48G would require a separate assessment because it can include live application data.

Before running anything, I need:

- **Target and access:** the production hostname and approved access method.
- **Temporary-file rules:** whether everything under `uploads/tmp` is disposable, or the retention period; whether workers use it and how cleanup can safely coordinate with them.
- **Branch rules:** what “old” means, the integration branch, protected/deployment branches, and whether you mean local branches only. Unmerged work needs an explicit retention decision.
- **Go-ahead:** authorization for the read-only checks and cleanup within those agreed rules.