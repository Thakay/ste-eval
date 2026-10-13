**I would keep SQLite for now if it is meeting your latency and reliability targets, and plan to move to Postgres before adding a second app server.** Your numbers alone do not justify “must migrate now.”

SQLite in WAL mode can serve many readers alongside a writer, but **only one write transaction can run at a time**. Fifty writes per second can be comfortable when transactions are short. It can become troublesome when transactions hold the write lock for longer, arrive in bursts, or include slow work. User count is a weak sizing signal.

| Tradeoff | SQLite with WAL | Postgres |
|---|---|---|
| Operations | Simple deployment, few moving parts | Database service, credentials, upgrades, connections, and memory to manage |
| Concurrent writes | Writers serialize across all tables | Writers can usually work concurrently on different rows; contention still exists |
| Read performance | Often excellent, with little connection overhead | Strong, but migration does not automatically make queries faster |
| Multiple app servers | WAL requires processes to share the database on the same host; a shared network filesystem is unsuitable | Designed for app servers connecting over a network |
| Django concurrency controls | `select_for_update()` has no effect | Supports row locks for workflows that need them |
| Reliability | Can be reliable with sound transactions and backups | Can be reliable too; running it on the same VPS adds no host redundancy |

Before deciding when to migrate, watch these signals during real peak traffic:

- **Lock errors and write latency**, especially tail latency rather than averages.
- **Transaction duration.** Keep transactions short and keep network calls or other slow work outside them. Increasing SQLite’s timeout allows longer waiting; it does not add write capacity.
- **WAL growth and checkpoint behavior.** Long read transactions can prevent checkpoints from completing.
- **Backup recovery.** Use a SQLite-aware backup method and test restores. Copying only the live database file can miss committed data still in the WAL.

Move sooner if lock contention already hurts users, you need row locking for important business workflows, or the second app server is a committed near-term project. Migration is easier while the system has spare capacity.

Your 4 vCPU / 8 GB VPS is a reasonable starting point for Django plus Postgres, subject to actual memory and query usage. Budget for the operational work and validate the migration, including SQLite’s more permissive typing, sequence values, and application behavior.

My recommendation: **measure now, fix any long transactions, and schedule Postgres ahead of multi-server deployment.** Ask the contractor which observed bottleneck or required capability makes migration urgent.

Hold the line, Spartan.