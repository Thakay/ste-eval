# Recommendation

**Do not move to Postgres now.** Your current load does not make the move necessary. But the contractor is correct that you will need Postgres. Plan the move as a scheduled project, and complete it **before** you add the second app server.

# Why SQLite is sufficient now

- In WAL mode, many readers can operate at the same time as one writer. Your traffic is mostly reads.
- 50 writes per second is a low load for SQLite on a local SSD. SQLite can do thousands of short write transactions per second.
- SQLite runs in the Django process, so each query has no network delay. Many small queries stay fast.
- One VPS with 4 vCPU and 8 GB RAM is sufficient for this load.

# The real limit: the second app server

- SQLite is not safe on a network file system. WAL mode uses shared memory on one host.
- Two app servers cannot safely write to one SQLite file.
- When you add a second app server, you must have a database server. For Django, Postgres is the correct choice.

First, find out why you want the second server:

- **For more capacity:** a larger VPS costs less and is easier. SQLite continues to work.
- **For high availability:** you must have Postgres. But one Postgres instance on one VPS is also a single point of failure. You must also have a replica or a managed Postgres service.

# Postgres: advantages

- Many writers can operate at the same time. SQLite has one writer for the full database.
- `select_for_update()` locks rows. On SQLite, Django ignores it.
- Many app servers can connect over the network.
- It has replication, point-in-time recovery, and managed services.
- It applies strict data types. SQLite accepts incorrect types in a column.
- It has better tools for large queries, full-text search, and JSON.

# Postgres: disadvantages

- You must operate one more service. This includes upgrades, settings, backups, and monitoring.
- It uses RAM. On an 8 GB VPS, Postgres and Django share the memory.
- Each query has more overhead (socket or network). Code with many small queries (N+1) becomes slower.
- You must manage connections. Set `CONN_MAX_AGE`. Later, you can add PgBouncer.
- The move itself can cause problems (see below).

# Possible problems in the move

- SQLite data can contain incorrect types, for example text in integer columns or bad dates. Postgres rejects this data. Clean the data before the move.
- On SQLite, the Django `contains` lookup ignores case for ASCII text. On Postgres, it does not ignore case. Search results can change.
- After you load the data, reset the sequences. Use `manage.py sqlsequencereset`.
- Change all raw SQL that uses SQLite-specific syntax.
- `dumpdata` and `loaddata` are slow for large data. `pgloader` is faster.

# Do these steps now on SQLite

1. Keep write transactions short. Do not do network calls or slow work in a transaction.
2. If you use Django 5.1 or later, set these options:

   ```python
   "OPTIONS": {
       "timeout": 20,
       "transaction_mode": "IMMEDIATE",
       "init_command": "PRAGMA synchronous=NORMAL;",
   }
   ```

   `IMMEDIATE` prevents `database is locked` errors when a read transaction changes to a write transaction.
3. Back up the database continuously with Litestream. As an alternative, run `VACUUM INTO` on a schedule.
4. Do a test restore of the backup.
5. Monitor `database is locked` errors and the write latency at peak.

# Prepare for the move

1. Run your test suite against Postgres in CI now. This finds code that is not compatible.
2. Remove SQLite-specific raw SQL.
3. Do the move in two steps. This makes each step smaller and safer:
   - **Step 1:** Install Postgres on the same VPS. Connect with a Unix socket. Move the data.
   - **Step 2:** Later, add the second app server. Then move Postgres to its own server or a managed service.

# When to move earlier

Move earlier if one of these conditions occurs:

- `database is locked` errors continue after you apply the settings above.
- Write latency increases at peak.
- You must run long write jobs (imports, batch jobs) at the same time as user traffic.
- You must have high availability.

Also, if your team has free time now, a move now is acceptable. The data is small now, so the move is easier now than later. But your current load does not make it urgent.