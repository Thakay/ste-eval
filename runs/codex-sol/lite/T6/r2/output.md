The temporary directory is the main target. Recovering all 31 GB would reduce disk use to about 79%. Deleting Git branches usually frees little space because branches only reference Git objects.

I would proceed in this order:

1. Check disk use, temporary files, upload jobs, and the repository state.
2. Identify expired temporary files using the app’s retention rules.
3. Use the app’s cleanup procedure, if available. Otherwise, delete confirmed disposable files in small batches.
4. Record approved branch names and commit IDs outside this server.
5. Delete approved local branches merged into the agreed target. Preserve branches required for deployment or rollback.
6. Check free space and verify that uploads and the app still work.

Deleted files can still occupy disk space while a process holds them open. I would check this if the expected space does not become available.

Before any command, I need:

- The production hostname and approved access method.
- The temporary-file retention rule and confirmation that expired files are disposable.
- How uploads and background jobs use that directory.
- Your definition of “old branches,” the merge target, and branches required for deployment or rollback.
- Whether you allow a brief upload pause if cleanup requires one.

Godspeed, Spartan.