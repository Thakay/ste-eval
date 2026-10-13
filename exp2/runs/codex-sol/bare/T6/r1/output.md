The **31G temporary-upload directory is the main opportunity**. Releasing all of it would bring disk usage to roughly **79%**. Deleting Git branches usually saves very little space: branch references are tiny, and Git can retain their history afterward.

After authorization, I would:

1. Run read-only checks to verify the upload path, identify cleanup candidates and active uploads, and inspect the repository’s deployment branch, merge status, and worktrees.
2. Show the proposed deletions and estimated space savings.
3. Clean eligible temporary files using the app’s cleanup mechanism where available. Preserve the directory and its permissions. If active uploads cannot be reliably excluded, arrange an approved pause of upload processing.
4. Delete approved local branches using `git branch -d`, protecting deployment, release, rollback, and worktree branches. Branches with unmerged work need individual review.
5. Verify reclaimed space and application health. Deleted files held open by running processes may delay space recovery.

Before running **anything**, I need:

- **Access and inspection approval:** the server connection details and authorization for the initial read-only checks.
- **Temporary-file policy:** confirmation that these files are disposable, the retention cutoff, and how to recognize active uploads. Also, whether anything needs preserving before deletion.
- **Branch policy:** the deployment/main branch, what qualifies as “old,” and which branches must be retained. A sensible default is old local branches already merged into the agreed base.
- **Deletion authorization:** approval of the resulting candidate list or a precise cleanup rule.

The Docker directory’s size alone does not establish what is safe to delete; Docker cleanup would require its own inventory and scope.