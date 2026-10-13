**I would keep SQLite for now if production is healthy, and plan a move to Postgres before adding a second app server.** Your numbers alone do not justify “must migrate now.”

The important limit is concurrent write transactions, not registered or active users. SQLite WAL lets readers and a writer work concurrently, but only one transaction can write at a time. Fifty writes per second can be quite manageable when transactions are short. Bursts, slow storage, or transactions that hold the write lock while doing other work can turn that into a queue.

| Tradeoff | SQLite in WAL mode | Postgres |
|---|---|---|
| Writes | One writer at a time; sensitive to transaction duration | Concurrent writers, though writes to the same rows can still contend |
| Read-heavy workload | Often efficient with suitable indexes | Also strong; performance still depends on queries and indexes |
| Operations | Simple deployment and low overhead | Adds a database service, connection management, upgrades, and tuning |
| Multiple app servers | Direct WAL access requires clients on the same host | Designed for multiple servers accessing one shared database |

Before deciding, look at production evidence:

- **Write latency and failures:** Track p95/p99 latency, lock waits, and `database is locked` errors during peaks.
- **Headroom:** Test realistic overlapping Django requests and bursts above today’s peak. Average throughput alone can hide contention.
- **Transaction length:** Keep write transactions short, with network calls and expensive computation outside them.
- **Recovery:** Use SQLite-aware backups and test restores. Copying just the database file while WAL is active can miss committed data. Long-running reads can also delay checkpoint progress and grow the WAL.

**Move sooner** if lock contention already hurts requests, latency rises sharply during bursts, or fixing contention requires substantial application work. Increasing SQLite’s timeout may reduce immediate errors, but it does not increase write capacity.

If the second app server becomes a firm plan, migrate ahead of that change. Sharing a SQLite WAL database across machines through a network filesystem is unsupported. Postgres provides the shared database those app servers need.

Postgres can initially run on your current VPS, subject to resource measurements. That keeps infrastructure costs down, but both setups retain the VPS as a single point of failure. A separate or managed database changes the cost and operational tradeoffs.

The contractor should demonstrate the bottleneck or architectural requirement. Meanwhile, a staged Postgres migration rehearsal would make next year’s choice much easier.

Hold the line, Spartan.