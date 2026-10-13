The 31 GB temporary directory is the first cleanup candidate. If all its contents are disposable, disk usage could fall to about 79%.

Deleting Git branches usually frees little space. It removes references, but it does not immediately remove the stored Git objects.

I would:

1. Use read-only checks to confirm paths, file ages, active uploads, repository size, and branch merge status.
2. Prepare exact lists of temporary files and branches for your review.
3. Prevent upload processes from using cleanup candidates during deletion.
4. Delete approved temporary files and approved local branches. Use normal Git deletion without forcing removal of unmerged branches.
5. Check disk usage again. Deleted files can still occupy space while a process holds them open.

Before I run anything, I need:

- The server address, SSH username, and an approved access method.
- The temporary-file retention rule. I also need to know how the app identifies files that uploads still need.
- Whether we can briefly pause upload workers if necessary.
- Your definition of “old branches,” the branch they must be merged into, and the branches to protect.

After the checks, I would request approval for the exact deletion lists. The supplied sizes do not establish which files or branches are safe to delete.

Godspeed, Spartan.