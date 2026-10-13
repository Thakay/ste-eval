**Verdict:** Do not move to Postgres now. Plan the move as a calm project before you add the second app server, and prepare for it today. SQLite in WAL mode easily handles your current load. The second host, not the load, forces the change.

## Why SQLite is enough today

- SQLite allows one writer at a time. With short transactions, one writer can do thousands of writes per second. Your 50 per second is a small load.
- In WAL mode, reads do not block writes. Your read-heavy traffic fits this model well.
- The database is a local file. Queries have no network round trip, so reads are very fast.

The hard limit is one machine. WAL mode uses shared memory, so SQLite is not safe over NFS or other network file systems. A second app server needs a real database server.

## Do now (about 1 to 2 days of work)

1. Set `"transaction_mode": "IMMEDIATE"` in the Django `OPTIONS` (Django 5.1 or later). This prevents most "database is locked" errors.
2. Set `"timeout"` to 5 to 10 seconds.
3. Use `init_command` to set `synchronous=NORMAL`, `cache_size`, `mmap_size`, and `temp_store=MEMORY`.
4. Add continuous backups with Litestream to object storage. Without it, a disk failure loses all data since your last backup.
5. Split bulk jobs into small transactions. A long write transaction blocks all other writers.
6. Run your test suite against Postgres in CI. This finds SQLite-only behavior early and keeps the future switch cheap.

## Move to Postgres when one of these is true

- You decide on the second app server. Do the migration first, as a separate release.
- Lock errors or slow writes continue after the tuning above.
- You need Postgres-only features: real `select_for_update`, `JSONB` indexes, full-text search, `contrib.postgres` fields.
- You need failover or a read replica.

## Tradeoffs

| | SQLite (stay) | Postgres (move) |
|---|---|---|
| Write concurrency | One writer. Enough for your load. | Many writers. |
| Read latency | Very low. | A bit higher (socket or network hop). |
| Multiple app servers | No. | Yes. |
| Operations work | Very little. One file. | More: backups, upgrades, vacuum, connection limits. |
| Cost | Zero. | Zero on the same VPS. A monthly fee if managed. |
| RAM on your 8 GB VPS | Small. | Takes 1 to 2 GB if it runs on the same box. |
| Recovery | Litestream restore. No failover. | Managed service gives point-in-time restore and failover. |
| Migration effort | None now. Grows with data and code. | One project, done once. |

## What the contractor gets right

- A planned migration is much easier than one during an outage.
- SQLite accepts loose types, but Postgres rejects bad data. Some old rows may fail on import. Test a full import early with pgloader.
- If the second app server is certain, the migration is certain. Only the timing is open.

## Check the reason for the second app server

If you want more capacity, a bigger VPS is cheaper and simpler. If you want availability, two app servers do not help while one database can fail. In that case, use managed Postgres with failover, not Postgres on one of the app boxes.

**Assumption:** your write transactions are short and the database is a few GB. If requests hold write transactions for long periods, the move becomes more urgent.

Hold the walls, quartermaster. Move the camp when the scouts say so, not when the merchants do.