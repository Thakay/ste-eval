**Verdict:** Stay on SQLite now. Move to Postgres before the second app server goes live, not earlier. Do cheap prep work now so that the later move is small.

**Why SQLite is fine today**

- 50 writes per second is a light load for SQLite in WAL mode on an SSD. SQLite can usually do thousands of short write transactions per second.
- WAL mode lets readers work while one writer writes. Your read-heavy load fits this model well.
- The hard limit is one writer at a time. This limit only hurts when write transactions are long, for example slow code inside `transaction.atomic()`.

**Why the second app server changes the answer**

SQLite in WAL mode needs every process on the same host as the database file. It uses shared memory, so it does not work safely over NFS or other network filesystems. Two app servers cannot share one SQLite file. At that point, Postgres is the simplest correct choice. Tools like LiteFS or rqlite exist, but they add more parts than Postgres does.

**Tradeoffs**

| | Stay on SQLite now | Move to Postgres now |
|---|---|---|
| Ops work | One file. Backups with Litestream or the SQLite backup API. | A server to tune, upgrade, back up, and monitor. Connection settings to manage. |
| Speed at your load | More than enough. No network hop. | More than enough. Small cost per query. |
| Concurrent writes | One writer at a time. | Many writers at a time. |
| Second app server | Not possible without a migration. | Ready. |
| Main risk | You do the migration later, maybe under time pressure. | You take migration risk now for capacity you do not need yet. |

**What to do now**

1. Tune SQLite in Django 5.1 or later. Set `"transaction_mode": "IMMEDIATE"` to prevent most "database is locked" errors. Set `timeout` to 10 to 20 seconds. Set `PRAGMA synchronous=NORMAL` through `init_command`.
2. Keep write transactions short. Do not call external APIs inside a transaction.
3. Run continuous backups and test a restore. Litestream to object storage fits well. Do not copy the live `.db` file with `cp`.
4. Run your test suite against Postgres in CI. This finds SQLite-specific behavior early: raw SQL, case rules in `LIKE`, loose column types, and date handling.
5. Monitor "database is locked" errors and slow write requests.

**Move sooner if one of these occurs**

- "database is locked" errors appear under normal load.
- You add workers (Celery, cron jobs) on another host that write to the database.
- You need point-in-time recovery or a read replica.

**Question the second-server plan**

Ask why you want it. If the reason is capacity, a larger VPS is simpler and keeps SQLite. Your current box probably has room for more users. If the reason is uptime, one Postgres host is still a single point of failure. You would also need a replica or a managed Postgres service. A managed service also removes most of the ops work in the table above.

**For the contractor:** Ask which failure they expect at your current load. "Must move now" needs a specific reason, such as lock errors or a feature that SQLite does not have. Without one, the move costs time and gives no return yet.

Hold the gate, warden.