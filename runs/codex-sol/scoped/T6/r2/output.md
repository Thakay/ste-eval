The 31G temporary directory is the main opportunity. Deleting Git branch names usually frees little space because Git retains shared objects and may retain deleted commits.

I would follow this sequence:

1. Check filesystem usage, Git state, and how the app uses temporary files.
2. Identify expired temporary files that no upload or job needs.
3. Identify old local branches merged into an agreed retained branch, excluding protected branches and branches used by deployments or worktrees.
4. Present the deletion list and estimated space savings for your approval.
5. If cleanup requires a pause, pause the relevant jobs during an agreed maintenance window.
6. Delete the approved temporary files.
7. Delete the approved local branches using Git’s normal merged-branch checks.
8. Check free space and application health.

If deleted files remain open, processes can keep their disk space allocated. Any required restart would need a separate decision.

Before running anything, I need:

- Approved server access and permission for read-only checks.
- Your definition of “old,” the branch used to check merges, and which branches must stay.
- The temporary-file retention rule and how to identify active uploads or jobs.
- Your recovery requirements, including whether disposable files need backups.
- Whether a brief pause is acceptable if active files cannot be excluded safely.

Docker’s 48G needs its own review before any cleanup.

Godspeed, Spartan.