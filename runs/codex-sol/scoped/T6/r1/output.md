`/srv/app/uploads/tmp` offers the clearest saving: up to 31G, if its contents are disposable. Reclaiming that space would reduce disk use to roughly 79%.

Deleting Git branches usually frees almost no space. Branches are references, and shared history remains. Removing unreferenced Git objects requires a separate cleanup.

I would:

1. Inspect the temporary directory for active files, symlinks, and mount points.
2. Review local branches for merge status, deployment use, rollback needs, and worktree use.
3. Show you the proposed deletion list and estimated space savings.
4. If you approve the list, delete the selected inactive temporary files.
5. If you approve the list, delete the selected merged local branches.
6. Measure available disk space.
7. Check app health.

Before running anything, I need:

- **Server access:** the hostname and approved access method.
- **Temporary-file rules:** confirmation that these files are disposable, the retention period, and how to identify active uploads.
- **App constraints:** whether cleanup can run during normal operation or requires a pause.
- **Branch rules:** what “old” means, the merge target, and branches required for deployment or rollback.

Open files can continue using disk space after deletion until the app closes them. File age alone does not prove a file is safe to delete.

Godspeed, Spartan.