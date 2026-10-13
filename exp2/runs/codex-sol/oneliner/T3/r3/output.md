Keep SQLite for now if peak response times meet your limits and database locks do not cause failed requests. Plan to move to PostgreSQL before you add an app server on another machine. These numbers alone do not require an immediate move.

The main differences are:

- **SQLite:** It requires less maintenance. WAL mode lets reads and a write occur at the same time, but only one write transaction can run at a time. Fifty writes per second can be acceptable if transactions are short. Long write transactions cause other writers to wait. Long read transactions can delay WAL cleanup and let the WAL file grow.
- **PostgreSQL:** It can process writes at the same time when they affect different rows. Several app servers can connect to one database over a network. You must maintain another service, manage connections, monitor resource use, and maintain backups. The move also requires data transfer and application tests.
- **Your VPS:** PostgreSQL can run on the current VPS. Check available CPU and memory capacity before the move. PostgreSQL on the same VPS gives no protection against a VPS failure.
- **A second app server:** Several app processes on the current VPS can use SQLite. SQLite WAL requires all processes that access the database file to run on the same machine. Do not share that file between machines through a network file system.

Measure peak response times, database lock errors, write transaction times, and WAL file size. Test database backup and restore procedures.

Move sooner if lock errors or slow writes continue after you shorten transactions. If current operation is satisfactory, use the time to test PostgreSQL with your Django application and prepare the migration.