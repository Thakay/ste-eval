The temporary upload directory offers the largest clear opportunity: up to 31 GB. Deleting Git branches usually frees little space because most Git objects remain stored.

I would follow these steps:

1. Inspect disk use, repository status, and temporary files without making changes.
2. Identify expired temporary files using the app’s cleanup rules.
3. Check whether active uploads still use those files.
4. Identify old local branches merged into the agreed deployment branch.
5. Prepare an exact deletion list for your approval.
6. Delete the approved files and branches during the agreed cleanup window.
7. Check free space.
8. Verify that the app and uploads still work.

Before running anything, I need:

- **Access and inspection approval:** The server access method and permission for initial read-only checks.
- **Temporary file rules:** The age cutoff, backup requirements, and how the app identifies active uploads.
- **Upload coordination:** Whether uploads can pause if safe cleanup requires it.
- **Branch criteria:** Your definition of “old,” the deployment branch, and protected branch names.
- **Recovery requirements:** Confirmation that needed work has a backup or remains on retained branches.

I would preserve branches used by worktrees. Any unmerged branch would require separate review before deletion. Docker cleanup would require a separate review and approval.

Deleted files can still occupy disk space while a process keeps them open.

Godspeed, Spartan.