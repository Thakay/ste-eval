**You do not need to move immediately based on those numbers alone.** I’d keep SQLite while it meets your latency and reliability targets, and plan a Postgres migration before adding a second app server that accesses the same database.

SQLite in WAL mode can comfortably serve many small SaaS applications. Readers can run alongside a writer, but **only one write transaction runs at a time**. Fifty writes per second may be perfectly manageable when transactions are short and storage is fast. Long transactions, bursts, and slow disk commits matter more than the user count.

| Consideration | SQLite with WAL | Postgres |
|---|---|---|
| Write concurrency | Writers take turns; contention can cause delays or “database locked” errors. | Independent writes can proceed concurrently; conflicting writes still wait. |
| Operations | Simple deployment and fewer services to maintain. | Requires service maintenance, connection management, and more memory. |
| Reads | Excellent for many workloads, with little connection overhead. | More flexibility for complex queries and growing workloads; migration alone doesn’t guarantee faster reads. |
| Multiple app servers | Local database file makes access from separate hosts awkward. | Designed for multiple servers connecting to one database. |
| Availability | Your VPS remains a single point of failure. | Running Postgres on that same VPS leaves the same failure point. |

For the second app server, **don’t put the SQLite WAL database on a shared network filesystem**. WAL relies on coordination between processes on the same host. Postgres is the straightforward choice when both app servers need direct database access.

For now, watch write latency, lock errors, transaction duration, and WAL/checkpoint behavior during peaks. Keep write transactions short, avoid external API calls inside them, configure a sensible busy timeout, and use WAL-aware backups with tested restores. A timeout can absorb brief contention; it cannot create more write capacity.

Move sooner if lock contention already affects requests, background jobs compete heavily with request writes, or multiple servers become a firm near-term requirement. Your VPS is a reasonable starting place for Postgres with sensible memory and connection limits; a separate database server is optional.

Django makes migration easier, but rehearse it: SQLite’s permissive typing can conceal data problems that Postgres rejects. Validate the data, test representative queries, and prepare a cutover and rollback procedure.