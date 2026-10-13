Keep SQLite for now if it meets your requirements for response time and reliability. Plan to use PostgreSQL before you add a second application server. Your user count and write rate do not prove that an immediate change is necessary.

WAL permits reads during writes, but SQLite permits only one write transaction at a time. At 50 writes per second, short transactions can give satisfactory performance. Long transactions can cause write delays and lock errors. Transaction duration and disk performance matter more than user count alone.

The main differences are:

- **SQLite:** Fewer components, less memory use, and simple operation on one VPS. Writes must wait for other write transactions. Long read transactions can delay checkpoints and cause WAL growth.
- **PostgreSQL:** Concurrent write transactions and a central database that several application servers can use. Writes to the same rows can still wait for locks. PostgreSQL adds memory use, server configuration, and maintenance. Both databases need tested backups.

Your VPS can be sufficient for PostgreSQL with this load, but test it with Django on the same machine. PostgreSQL on that VPS does not protect you from a VPS failure.

Before you decide, test with a load above your expected peak. Measure write transaction duration, lock waits, database errors, and response times. Check WAL growth and test backup recovery.

Move sooner if write delays exceed your limits after you correct long transactions. If the second application server becomes a firm requirement, schedule the change before you add it. Standard SQLite WAL requires all database access processes to use the same host. Do not share its database through a network filesystem.

The contractor has a good reason to recommend PostgreSQL for future expansion. These figures alone do not support a requirement to move now.