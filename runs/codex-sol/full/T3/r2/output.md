**Keep SQLite for now if peak traffic meets your latency targets and writes do not fail because of lock contention.** Plan a Postgres migration before a second app server needs direct access to the same database.

Your numbers alone do not justify an immediate migration. Active user count tells you little about database capacity. Transaction duration, simultaneous writes, and storage speed matter more.

SQLite in WAL mode lets readers and a writer operate together. It still permits only one writer at a time. Fifty writes per second can be reasonable with short transactions. Bursts and long transactions can cause queues, lock errors, and high latency.

| Factor | SQLite with WAL | Postgres |
|---|---|---|
| Concurrent writes | One writer at a time. | Multiple writers. Conflicting writes can still wait or fail. |
| Two app servers | Processes that access the database must share one host. WAL does not support sharing files over a network filesystem. | Both servers connect to one database over the network. |
| Operations | Fewer services to maintain. | Requires more setup, monitoring, and maintenance. |
| Recovery | Supports consistent backups with suitable methods. | Supports backups and recovery to a specific time when configured. |
| Migration effort | No immediate migration work. | Requires data transfer, query checks, and a plan for downtime. |

Before deciding, check these during peak traffic:

- Request latency, especially the slowest 1% of requests.
- `SQLITE_BUSY` and “database is locked” errors.
- Write transaction duration and WAL checkpoint delays.

Keep write transactions short. Avoid network calls inside them. Use a consistent backup method and test restores.

**Move sooner** if lock contention causes failed writes or unacceptable latency despite short transactions. An earlier move also makes sense if the second server becomes a firm near-term plan or you need Postgres recovery features.

Postgres can run on your current VPS, subject to database size and workload. It will compete with Django for RAM and CPU. That move alone does not remove the VPS as a single point of failure.

I would challenge “must move now,” but budget for Postgres before you add a second app server. SQLite remains a reasonable choice while the current system meets measured targets.

Godspeed, Spartan.