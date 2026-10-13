**Verdict:** Do not migrate now. SQLite in WAL mode handles your current load with a lot of room. Move to Postgres before a second app server goes live, because two hosts cannot share one SQLite file. Use the time until then to make the move cheap and calm.

## Why SQLite is fine today

- 50 writes per second is a low load for SQLite. On an SSD with short transactions, SQLite can do thousands of small writes per second.
- WAL mode lets readers continue while one writer writes. Your load is mostly reads, so this fits well.
- SQLite allows only one writer at a time. The real risk is long write transactions, not the number of writes. For example, a background job that holds a write transaction for 3 seconds blocks all other writes for 3 seconds.

The contractor is right about the destination. The contractor is wrong about "now", unless you see the signals in the "Migrate earlier" section.

## Where the contractor is right

- A second app server forces the move. Do not put the SQLite file on a network file system (NFS, SMB). WAL needs shared memory on one host, and a network file system can corrupt the database.
- Tools like LiteFS or rqlite can share SQLite across hosts. I do not recommend them for you. They add more complexity than Postgres does.

## Tradeoffs

| | Stay on SQLite now | Move to Postgres now |
|---|---|---|
| Concurrent writes | One writer at a time. Fine at 50/s with short transactions. | Many writers, with row-level locks. |
| Operations work | One file. Continuous backup with Litestream. | A server to tune, back up, and upgrade. Uses about 1 to 2 GB of your 8 GB RAM. |
| Query latency | In-process, very low. | Local socket, small overhead on each query. |
| Schema migrations | Django rebuilds the table for many `ALTER` changes. This blocks writes on large tables. | Most `ALTER` changes are fast. Some still take locks. |
| Second app server | Not possible. | Possible. |
| Features | Basic. | JSONB, full-text search, strict types and constraints. |
| Migration cost | You pay later, with a bigger database. | You pay now, with a smaller database. |

## What to do now

1. Harden the SQLite settings (Django 5.1 or later):

   ```python
   DATABASES = {
       "default": {
           "ENGINE": "django.db.backends.sqlite3",
           "NAME": BASE_DIR / "db.sqlite3",
           "OPTIONS": {
               "transaction_mode": "IMMEDIATE",
               "timeout": 5,
               "init_command": (
                   "PRAGMA journal_mode=WAL;"
                   "PRAGMA synchronous=NORMAL;"
                   "PRAGMA mmap_size=134217728;"
               ),
           },
       }
   }
   ```

2. Set up Litestream to stream the database to object storage. Test one full restore.
3. Keep write transactions short. Move slow work (HTTP calls, file processing) outside `atomic()` blocks.
4. Run your test suite against Postgres in CI. This finds SQLite-only behavior early.
5. Log "database is locked" errors and write latency.

Caveats on these settings:

- If you use `ATOMIC_REQUESTS = True`, do not use `transaction_mode: IMMEDIATE`. Every request then takes the write lock, and all requests run one at a time.
- `synchronous=NORMAL` can lose the last few committed transactions on a power loss. It does not corrupt the database.

## Migrate earlier if you see these signals

- "database is locked" errors in the logs, even with the busy timeout set.
- p95 write latency (the time that 95% of writes finish within) grows at peak.
- Schema migrations on big tables block writes for too long.
- You need Postgres features, such as full-text search or JSONB queries.
- You decide to add the second app server. Start the migration then, with a few weeks of lead time.

## Ask why you need a second app server

- If you need it for capacity, a bigger VPS is simpler and cheaper. You can keep SQLite.
- If you need it for availability, one database is still one point of failure. You then need managed Postgres with a standby server, or the second app server gives little value.

## Migration problems to plan for

- SQLite does not enforce `CharField` `max_length`. Postgres does. Find values that are too long before you load the data.
- On SQLite, `__contains` ignores case for ASCII text. On Postgres it does not. Check your search queries.
- SQLite accepts wrong types in a column. Postgres rejects them.
- After you load the data, run `sqlsequencereset`. If you do not, new inserts fail with duplicate keys.
- Use pgloader for a large database. `dumpdata` and `loaddata` are fine for a small one.

I do not know your database size or your longest write transactions. Either of these can change the answer, so check them first.

Hold the line, keeper of the single file. The phalanx moves when the scouts say so, not before.