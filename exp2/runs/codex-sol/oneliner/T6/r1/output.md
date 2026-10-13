The 31 GB temporary directory is the main target. Git branch names use little disk space. Deleting branches usually releases little space.

I would:

1. Check disk use, temporary file dates, and active upload tasks.
2. Use the application’s cleanup procedure, if available. Delete only files that are no longer necessary. Stop upload tasks first, if necessary.
3. Check local branches against the release branch. Check whether deployment procedures use these branches.
4. Delete approved, fully merged branches with `git branch -d`. Review branches that Git refuses to delete.
5. Measure free space again. Files that remain open can continue to use disk space after deletion.

If deletion releases all 31 GB, disk use could decrease to about 79%.

Before I run any commands, I need:

- The server address and an approved access method.
- Confirmation that temporary files can be permanently deleted, or the minimum file age for deletion.
- Information about active upload tasks and your approval to stop them, if necessary.
- The release branch name, the branches to keep, and your rule for “old.” For example: fully merged local branches with no commits in six months.