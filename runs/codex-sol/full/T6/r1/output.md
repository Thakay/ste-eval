The temporary uploads offer the largest likely saving. Deleting Git branches alone usually frees very little space because branches reference shared Git objects.

I would:

1. Check disk usage, repository status, and the deployed branch. Inspect temporary files and the app’s cleanup process.
2. Identify disposable temporary files. File age alone does not prove that a file is unused.
3. Coordinate cleanup with the app to prevent deletion of active uploads. Delete the selected files while preserving the directory and its permissions.
4. Delete local branches that meet your retention rule and are merged into the agreed target branch. Preserve protected branches and unmerged work.
5. Check free space again. Measure Git storage before considering garbage collection, which requires care while other Git processes run.

If all 31 GB is disposable, deleting it could reduce disk use to about 79%.

Before any commands, I need:

- An approved connection to the correct production server.
- The rules for temporary uploads: which files are disposable, their retention period, and how the app identifies active uploads.
- Permission for a brief pause in uploads if safe cleanup requires one.
- Your definition of an “old” branch, the merge target, and the protected branches.

Godspeed, Spartan.