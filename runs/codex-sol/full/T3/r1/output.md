I recommend keeping SQLite for now **if it meets your latency targets without recurring lock errors**. Plan a PostgreSQL migration before adding a second app server on another host.

Your user count and peak write rate do not prove that you need PostgreSQL now. SQLite can support 50 writes per second with short transactions and suitable storage. Transaction duration and concurrent writers matter more than the write count alone.

| Area | SQLite in WAL mode | PostgreSQL |
|---|---|---|
| Reads | Readers can continue during writes. Suits many workloads where reads dominate. | Also suits these workloads. Offers more options for complex queries and indexing. |
| Writes | Only one writer can operate at a time. Long transactions can delay other writers. | Supports concurrent writers, although writes to the same rows can still conflict. |
| Operations | Fewer components and lower resource use. Backups must account for WAL. | Requires more setup, monitoring, upgrades, and backup work. |
| Multiple servers | Direct WAL access requires database clients on the same host. | App servers can connect from different hosts. |

For your current system:

- Measure write latency during peak traffic, lock errors, transaction duration, and disk activity.
- Keep write transactions short. Avoid network calls inside them.
- Check WAL growth and checkpoint behavior. Long read transactions can prevent checkpoints from completing.
- Use a backup method that supports a live SQLite database. Test recovery.

A longer lock timeout can reduce some errors, but it cannot increase write capacity. It can also turn errors into longer waits.

Move sooner if writes regularly miss your latency targets, lock errors recur, or necessary transactions create contention. PostgreSQL offers more room for concurrent writes and future growth.

PostgreSQL does not require another VPS. You can initially run it beside Django if memory and disk capacity permit. Both services would still depend on that VPS.

If the second app server becomes likely, schedule the migration before the expansion. Do not share a SQLite WAL database over NFS between app servers. Django helps with the migration, but test existing data, constraints, custom SQL, and query behavior.

Godspeed, Spartan.