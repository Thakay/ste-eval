**I would keep SQLite for now if production is healthy, and plan to move to PostgreSQL before adding an app server on a second machine.** Your numbers alone don’t justify “must migrate now.”

SQLite can handle this workload. The key constraint is that **WAL allows readers and a writer to overlap, but there is still only one writer at a time**. Fifty short write transactions per second can be fine; transactions that hold the write lock for longer can cause queues and timeouts. Active-user count and read/write ratio don’t tell us enough to judge that.

The tradeoffs are:

| | SQLite in WAL mode | PostgreSQL |
|---|---|---|
| Concurrent writes | Writes serialize; sensitive to transaction duration | Independent writes can proceed concurrently, though conflicting writes still wait |
| Deployment | Simple and efficient on one machine | App servers on multiple machines can share the database |
| Operations | Little administration; still needs sound backups and monitoring | Adds connection management, resource tuning, upgrades, and database administration |
| Features | Good for straightforward application workloads | Better support for row locking, richer queries, and more complex transactional workflows |
| Reliability | Depends on backups, durability settings, and the host | Offers more replication and recovery options; installing it alone doesn’t provide high availability |

For your current setup, I’d check three things:

- **Peak-hour behavior:** database lock errors, write timeouts, and p95/p99 request and transaction latency.
- **Transaction design:** keep writes short; avoid network calls or lengthy processing inside transactions. Increasing the lock timeout only lets requests wait longer.
- **Operational health:** monitor WAL growth and checkpoints, and test restores using a SQLite-aware backup method. Copying only the live `.db` file can miss committed data in the WAL.

**The second machine is the strongest reason to migrate.** SQLite WAL requires participating processes to be on the same host; putting the database on a network filesystem is not a sound way to share it between app servers. Multiple Django worker processes on your current VPS are fine.

PostgreSQL could initially run on your existing 4-vCPU, 8-GB VPS, subject to available memory and workload. You don’t automatically need another server, although that arrangement still leaves one machine as a single point of failure.

If the second app server is a firm roadmap item, schedule the migration ahead of it and rehearse the data transfer, PostgreSQL-specific behavior, and cutover. If it’s speculative and SQLite is meeting your latency and reliability targets, keeping it is reasonable. **Migrate sooner when you see write contention or need PostgreSQL’s features—not because you crossed an arbitrary user-count threshold.**