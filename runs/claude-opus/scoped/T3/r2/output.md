**Verdict:** The contractor is right about the direction and wrong about the urgency. SQLite in WAL mode handles your current load with a lot of room to spare. The second app server is what really forces Postgres, so plan the move as a calm project before you add that server. It does not need to be an emergency now.

**Why SQLite is fine today**
- 50 writes per second is low for SQLite. With short transactions, one writer can do thousands of writes per second on an SSD. WAL lets reads run while a write is in progress.
- SQLite runs inside your app process, so each query is very cheap. Postgres adds a round trip to every query, which makes N+1 query patterns cost more.
- Ask the contractor what symptom they see. "Database is locked" errors and slow pages usually come from settings or long transactions, and those are cheap to fix.

**What does force the move**
- Two app servers cannot safely share one SQLite file. WAL needs shared memory on one host, and SQLite over NFS can corrupt data. LiteFS or libSQL can work around this, but they add more moving parts than Postgres does.
- Schema changes on large tables get slow. SQLite rebuilds the whole table for many column changes and blocks writes while it runs. How much this matters depends on your data size, which I don't know.

**Tradeoffs**

| | SQLite | Postgres |
|---|---|---|
| Concurrent writes | One writer at a time. Fine at your load. | Many writers at once |
| Second app server | Not safe | Works |
| Ops work | A file. Almost none. | A service to tune, back up, upgrade, and monitor |
| Query latency | In process, very low | Socket or network round trip |
| RAM on the 8 GB box | Uses the OS page cache | Needs its own memory budget |
| Backups | Litestream or `.backup`. Never copy the live file. | `pg_dump`, point-in-time recovery, managed options |
| Data checks | Loose: ignores `max_length`, weak types | Strict types and constraints |
| Features | Basic. `select_for_update` does nothing. | Full-text search, row locks, rich JSON, online index builds |

Postgres will reject data that SQLite accepted, such as strings longer than `max_length`. Find this data in a rehearsal, not during the cutover.

**Do now**
1. Set `"timeout": 20` in the SQLite `OPTIONS`. Writers then wait for the lock instead of failing.
2. If you run Django 5.1 or later, set `"transaction_mode": "IMMEDIATE"`. This stops instant lock errors when a read transaction turns into a write.
3. Do not set `IMMEDIATE` if `ATOMIC_REQUESTS` is on. Every request then takes the write lock, including reads.
4. Keep write transactions short. Do not call external APIs or send email inside `atomic()`.
5. Set up Litestream to copy the database to object storage. Test a restore.
6. Log lock errors and p95 write time. You then have data for the decision.

**Before the second app server (start 1 to 2 months ahead)**
1. Decide what the second server is for. If it is for capacity, a bigger VPS is cheaper and simpler.
2. If it is for uptime, plan a separate database host or managed Postgres. One Postgres box is still a single point of failure.
3. Run your test suite against Postgres in CI.
4. Fix the failures. Common ones are case-sensitive lookups, strings that are too long, and NULL sort order.
5. Copy production data into Postgres with pgloader. Compare row counts.
6. If the copy tool did not reset sequences, run `manage.py sqlsequencereset`.
7. Rehearse the cutover and time it.
8. Cut over in a short maintenance window. Keep the SQLite file for rollback.
9. Add the second app server only after Postgres runs stable. Do not change both at once.

Postgres can live on the current VPS at first, and the new app server connects to it over the private network. Use the Django 5.1 `"pool"` option with psycopg 3, or `CONN_MAX_AGE`, so each request does not open a new connection.

Hold the gate, Shieldwarden. 🛡️