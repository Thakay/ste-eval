The 31 GB temporary directory offers the largest clear opportunity. Deleting Git branches releases little space because Git keeps the stored data.

I would:

1. Check disk use and identify temporary files that the application no longer needs.
2. Check which local branches are merged into the agreed base branch. Keep current, protected, and unmerged branches.
3. Prepare a deletion list for your approval.
4. Delete the approved files and branches, then check free space again.

Files that are open can continue to use disk space after deletion. Git garbage collection needs a separate check because it can remove commit data.

Before I run anything, I need:

- The server access method.
- The temporary-file deletion rules, including the age limit and how to identify files still in use.
- The branch age limit, base branch, and branches to keep.
- Confirmation that the request applies only to local branches.
- Whether files selected for deletion need a backup.
- Whether a short application stop is permitted if necessary to stop temporary-file writes.