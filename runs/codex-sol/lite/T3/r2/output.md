If peak traffic meets your latency targets without recurring lock errors, keep SQLite for now. Plan a PostgreSQL migration before a second app server needs direct database access.

Your numbers do not establish an urgent need to migrate. SQLite can handle 50 writes per second in many workloads. Transaction duration, disk performance, and query design matter more than the active user count.

WAL allows readers and a writer to work concurrently. SQLite still permits only one writer at a time. Long write transactions can therefore cause delays or lock errors.

| Tradeoff | SQLite with WAL | PostgreSQL |
|---|---|---|
| Writes | Serializes writes; works well when transactions are short. | Supports concurrent writers, though conflicting updates still cause waits. |
| Reads | Efficient local reads with little overhead. | Strong read performance, with connection and server overhead. |
| Operations | Simple deployment and fewer services to maintain. | Requires service management, connection management, upgrades, and backup planning. |
| Multiple app servers | WAL requires direct database users to share one host. | App servers can connect across the network. |
| Resources | Usually needs less memory and administration. | Can run on your existing VPS, subject to workload and memory use. |

PostgreSQL does not automatically provide higher availability. Running it on the same VPS preserves your current single point of failure.

Use these steps to guide the timing:

1. Measure peak request latency, write transaction duration, and database lock errors.
2. Keep network calls and other slow work outside write transactions.
3. Test backups by restoring them.
4. If lock errors or write delays persist after tuning, move to PostgreSQL sooner.
5. Before adding another app server, test the migration with production-like data and traffic.

Do not share a SQLite WAL database between servers through a network filesystem. That setup cannot meet WAL’s shared-memory requirements.

The contractor identifies a useful future direction, but “must move now” needs evidence from your workload. An inexpensive migration now could still be worthwhile if the second server is likely.

Stay ready, Spartan.