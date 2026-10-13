I would start with `/srv/app/uploads/tmp`, which uses 31 GB. Git branch deletion alone will free little space.

I would:

1. Check disk use, the Git repository, and how the app uses temporary files.
2. Prepare a list of files and local branches to delete. Keep active upload files, deployment branches, and branches with unmerged commits.
3. Give you the list for approval.
4. Delete the approved items. Then check free space and app operation.

Before any command, I need:

- The server address and the account to use.
- Your definition of “old branches,” and the branches required for deployment or recovery.
- The temporary-file retention rule, including how to identify files that the app still needs.
- An approved maintenance time if uploads must stop for safe deletion.

Clearing the full temporary directory while uploads are active can cause upload failures. I would use the app’s cleanup procedure if one is available.