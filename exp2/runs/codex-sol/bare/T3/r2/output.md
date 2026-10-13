**Keep SQLite for now if production is healthy, and plan a tested Postgres migration before adding a second app server.** Your numbers alone don’t establish an urgent need to migrate.

SQLite in WAL mode lets readers and a writer run concurrently, but **only one write transaction can run at a time**. Fifty writes per second can be quite manageable when transactions are short. What matters is how long transactions hold the writer lock, how bursty traffic is, and whether users experience lock errors or slow requests. Two thousand active users is not itself a database capacity threshold.

The main tradeoffs are:

| Factor | SQLite with WAL | Postgres |
|---|---|---|
| Current workload | Often a good fit for reads and short, serialized writes | More room for concurrent writes to independent data |
| Operations | Very little database administration | Requires service management, tuning, upgrades, and database-aware backups |
| Resources | Small footprint | Uses more RAM and connections; your VPS is a reasonable starting point, subject to the app’s resource use |
| Multiple app servers | WAL requires database access on the same host; sharing the file over a network filesystem is unsuitable | Multiple app servers connect to one database over the network |
| Application capabilities | Fewer locking and database features | Row-level locking, stronger type enforcement, and more advanced query features |

Postgres can initially run on your existing VPS. Adding it does **not** provide high availability by itself: that machine remains a single point of failure.

Before deciding when to migrate, check:

- **Write latency and contention:** peak request latency, transaction duration, and `database is locked` errors.
- **Transaction boundaries:** keep network calls and lengthy work outside write transactions.
- **WAL and checkpoint behavior:** long-lived readers can prevent checkpoints from completing and allow the WAL to grow.
- **Recovery:** maintain consistent backups and verify that you can restore them.

A busy timeout helps absorb brief contention; it doesn’t increase sustained write capacity.

If these checks look healthy, continuing with SQLite is defensible. If lock failures or write queues persist after fixing transaction boundaries, bring the migration forward. Postgres will still need good queries and short transactions.

Because a second app server is on your roadmap, start migration preparation early: test against Postgres, check data types and constraints, rehearse data transfer, and define cutover and rollback steps. Django’s ORM helps, but SQLite’s permissive typing can hide incompatibilities.

I would challenge the contractor’s word **“must”**, while agreeing that **Postgres is the sensible destination for your planned architecture**. Ask them for measured contention or a specific requirement that makes the move urgent.