Set up a root-owned cron job that creates a backup at **02:00 every night**, using the server’s timezone. PostgreSQL’s custom dump format is compressed and supports restoration with `pg_restore`.

1. **Prepare the server and check database access.**

   Run these commands in a root Bash shell:

   ```bash
   sudo -i
   apt-get update
   apt-get install -y cron
   systemctl enable --now cron

   install -d -m 0700 /var/backups/postgresql/app

   docker exec --user postgres app-db pg_dump --version
   docker exec --user postgres app-db \
     psql --no-password -U app -d app -c 'SELECT current_database(), current_user;'
   ```

   Confirm `pg_dump` reports version 17. The second command checks access through the container’s local Unix socket.

   If authentication requires a password, configure a persistent `.pgpass` file inside the container for its `postgres` OS user, with permission `0600`. Its entry should be:

   ```text
   localhost:5432:app:app:YOUR_DATABASE_PASSWORD
   ```

   Place it in that user’s home directory, or add `--env PGPASSFILE=/path/to/.pgpass` to the `docker exec` commands. Keep passwords out of the backup script and cron entry.

2. **Create the backup script.**

   ```bash
   cat > /usr/local/sbin/backup-app-db <<'EOF'
   #!/bin/bash
   set -euo pipefail
   umask 077

   PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
   backup_dir=/var/backups/postgresql/app

   # Prevent overlapping runs.
   exec 9>/run/lock/app-db-backup.lock
   flock -n 9 || exit 0

   timestamp=$(date -u +%Y%m%dT%H%M%SZ)
   backup="$backup_dir/app_${timestamp}.dump"
   tmp=$(mktemp "$backup_dir/.app_XXXXXX.part")
   trap 'rm -f -- "$tmp"' EXIT

   docker exec --user postgres app-db \
     pg_dump --no-password --username=app --dbname=app \
     --format=custom > "$tmp"

   # Publish the file only after pg_dump succeeds.
   mv -- "$tmp" "$backup"

   # Delete completed backups at least seven days old.
   find "$backup_dir" -maxdepth 1 -type f \
     -name 'app_*.dump' -mtime +6 -delete

   printf '%s Backup completed: %s\n' "$(date -Is)" "$backup"
   EOF

   chmod 0700 /usr/local/sbin/backup-app-db
   ```

   Retention runs only after a successful backup. `-mtime +6` means at least seven complete 24-hour periods old.

3. **Run it manually, then schedule it.**

   ```bash
   /usr/local/sbin/backup-app-db
   ls -lh /var/backups/postgresql/app

   cat > /etc/cron.d/app-db-backup <<'EOF'
   0 2 * * * root /usr/local/sbin/backup-app-db >> /var/log/app-db-backup.log 2>&1
   EOF

   chmod 0644 /etc/cron.d/app-db-backup
   ```

   Check `/var/log/app-db-backup.log` after the first scheduled run. Arrange an alert for failed or missing nightly backups.

4. **Restore a backup into a separate test container.**

   Use the same PostgreSQL 17 image and extensions as production. This example uses the standard image, publishes no ports, and disables external networking.

   ```bash
   set -e

   BACKUP=$(find /var/backups/postgresql/app -maxdepth 1 \
     -type f -name 'app_*.dump' -printf '%p\n' | sort | tail -n 1)
   test -n "$BACKUP"

   docker run -d --name app-db-restore-test \
     --network none \
     -e POSTGRES_USER=app \
     -e POSTGRES_DB=app \
     -e POSTGRES_PASSWORD=restore-test-only \
     postgres:17

   # Wait up to two minutes for the final server to start.
   for attempt in {1..60}; do
     if docker exec app-db-restore-test \
       pg_isready -h 127.0.0.1 -U app -d app >/dev/null 2>&1; then
       break
     fi
     sleep 2
   done

   docker exec app-db-restore-test \
     pg_isready -h 127.0.0.1 -U app -d app

   docker exec -i app-db-restore-test \
     pg_restore --username=app --dbname=app \
     --no-owner --no-privileges \
     --exit-on-error --single-transaction < "$BACKUP"

   docker exec app-db-restore-test \
     psql --no-password -U app -d app \
     -v ON_ERROR_STOP=1 -c '\dt'
   ```

   `--exit-on-error` makes restoration failures visible. Ownership and permission restoration are skipped for this isolated test.

   Verify actual data, too: query important tables, check known records and expected totals, and run representative application queries against the restored database. For example, replace `your_table` before running:

   ```bash
   docker exec app-db-restore-test \
     psql --no-password -U app -d app -v ON_ERROR_STOP=1 \
     -c 'SELECT count(*) FROM public.your_table;'
   ```

   After validation, remove the test container and its disposable volume:

   ```bash
   docker rm -fv app-db-restore-test
   ```

Repeat restoration tests regularly. These dumps contain the database schema and data; cluster roles and server configuration require separate backups. Keep an off-server copy for recovery after server or disk loss.

Godspeed, Spartan.