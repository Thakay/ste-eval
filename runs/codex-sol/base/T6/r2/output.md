The main opportunity is `uploads/tmp`: reclaiming all 31 GB could bring disk usage to roughly 79%. Deleting Git branches usually frees very little space because branches are pointers to shared Git objects.

I would:

1. Inspect disk usage and list cleanup candidates using read-only checks.
2. Use the app’s cleanup mechanism if available, or delete only temporary files confirmed disposable and unused by active uploads or jobs.
3. Delete local branches confirmed merged into the agreed release branch, preserving current/deployment branches and unmerged or unpushed work. Branch age alone is insufficient.
4. Check actual space reclaimed. Deleted files held open by processes can continue occupying disk space.

Before running anything, I need:

- **Access:** the server address and approved SSH access method.
- **Temporary-file rules:** what uses this directory, the retention period, and how to identify files still in use. If that cannot be established, whether uploads and background jobs can be paused.
- **Branch rules:** the release branch to check against, protected branch names, and confirmation that cleanup concerns local branches only.
- **Recovery requirements:** whether these files are disposable and whether any branch history must be preserved elsewhere.

After inspection, I would present the specific deletion candidates for your approval.

Stand firm, Spartan.