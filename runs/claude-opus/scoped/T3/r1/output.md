**Verdict:** Do not move now, but plan the move. Your load is well within what SQLite in WAL mode handles on one machine. The real trigger is the second app server, because two machines cannot safely share one SQLite file. So do the Postgres move as a calm, planned project a few months before that server. Spend a few hours now to make the switch cheap and to remove the pain the contractor may be seeing.

## Tradeoffs

| Topic | SQLite (stay) | Postgres (move) |
|---|---|---|
| Write capacity | One writer at a time. Short transactions on SSD still give hundreds to thousands of writes per second. 50/s is fine. | Many writers at once, with row-level locks. |
| Second app server | Not possible. Network file systems break SQLite locking, and WAL needs shared memory on one host. | Supported. This is the main reason to move. |
| Operations | One file, no service, almost no tuning. | A service to run, upgrade, tune, and back up. Managed Postgres removes most of this for about $15 to $50 a month. |
| Read latency | The database runs in your process, so reads are very fast. | Each query has a socket round trip. N+1 query patterns hurt more. |
| Schema migrations | Django rebuilds the whole table for many ALTERs. On big tables, this blocks all writes during the migration. | Most ALTERs are fast. Some still take locks. |
| Backups | Use Litestream or `.backup`. Never copy the live file. | pg_dump plus WAL archiving, or managed snapshots. |
| Move cost | None. | One-time work: copy data, fix data that SQLite accepted but Postgres rejects, fix raw SQL, and check `LIKE` case behavior. |

## Where the contractor has a point

- **"database is locked" errors.** These are real. But on Django, the usual cause is deferred transactions, and `IMMEDIATE` mode fixes most of them.
- **Long write transactions.** A bulk import or a background job that holds a write transaction blocks every other write. If you have these, SQLite will hurt sooner.
- **You will move anyway.** It is better to move during a quiet period than under pressure. That argues for a planned move soon, not an emergency move now.

I cannot see your write patterns, so if you have long write transactions, the urgency is higher than I state here.

## Question the second app server

Decide why you want it, because the reason changes the plan:

- **For capacity:** a bigger VPS is simpler. Django on 4 vCPU for 2,000 users is probably far from its limit.
- **For uptime:** two app servers with one self-hosted database still have one point of failure. You need managed Postgres with failover to get real redundancy.

## Do now

1. If you run Django older than 5.1, upgrade to 5.1 or later.
2. Set the SQLite options below.
3. Add Litestream to stream backups to object storage.
4. Test a restore from the Litestream backup.
5. Log "database is locked" errors and p95 write latency.
6. Run your test suite against Postgres in CI, and fix the failures.
7. Find data that Postgres will reject, for example strings longer than `max_length`.

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
                "PRAGMA cache_size=-64000;"
            ),
        },
    }
}
```

Caveat: `synchronous=NORMAL` in WAL mode can lose the last few commits on a power loss. It does not corrupt the database.

## Move to Postgres when any of these is true

- You commit to the second app server.
- Lock errors or write latency still rise after the tuning.
- A migration on a big table needs more downtime than you accept.
- You need a Postgres-only feature, such as strong full-text search.

Hold the line, shieldbearer. Strike only when the field is yours.