Use `pg_dump` to make a backup each night at 02:00 UTC. Keep backups for seven days.

These commands require `sudo` access. Container `app-db` must be running.

1. **Make the backup directory and script.**

   ```bash
   sudo install -d -m 0700 /var/backups/app

   sudo tee /usr/local/sbin/backup-app-db >/dev/null <<'SCRIPT'
   #!/bin/bash
   set -euo pipefail
   umask 077
   export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

   backup_dir=/var/backups/app
   exec 9>/run/lock/app-db-backup.lock
   flock -n 9

   stamp=$(date -u +%Y-%m-%dT%H-%M-%SZ)
   temp=$(mktemp "$backup_dir/.app-$stamp.XXXXXX")
   trap 'rm -f -- "$temp"' EXIT

   docker exec app-db pg_dump -U app -d app -Fc >"$temp"
   mv -- "$temp" "$backup_dir/app-$stamp.dump"

   find "$backup_dir" -maxdepth 1 -type f \
     -name 'app-*.dump' -mtime +6 -delete

   printf 'Backup complete: %s\n' "$backup_dir/app-$stamp.dump"
   SCRIPT

   sudo chmod 0700 /usr/local/sbin/backup-app-db
   ```

   The script saves a PostgreSQL archive. It deletes old backups only after `pg_dump` completes without an error.

   `-mtime +6` selects files that are at least seven days old.

   If database access requires a password, configure `.pgpass` inside `app-db` for the user that runs `pg_dump`. Set its permissions to `0600`.

2. **Make the systemd service. Run the first backup.**

   ```bash
   sudo tee /etc/systemd/system/app-db-backup.service >/dev/null <<'SERVICE'
   [Unit]
   Description=Back up database app
   Requires=docker.service
   After=docker.service

   [Service]
   Type=oneshot
   ExecStart=/usr/local/sbin/backup-app-db
   SERVICE

   sudo systemctl daemon-reload
   sudo systemctl start app-db-backup.service
   sudo journalctl -u app-db-backup.service -n 20 --no-pager
   sudo ls -lh /var/backups/app
   ```

   Make sure that the log shows `Backup complete`.

3. **Restore the backup into a separate test container.**

   Make sure that the server has sufficient free disk space for another copy of the database.

   If the database uses extensions, replace `postgres:17` with an image that contains the same extensions.

   The test container has no external network connection. Its database uses local trust authentication.

   ```bash
   sudo bash <<'TEST'
   set -euo pipefail

   backup=$(find /var/backups/app -maxdepth 1 -type f \
     -name 'app-*.dump' -printf '%p\n' | sort | tail -n 1)
   test -n "$backup"

   docker run -d --rm \
     --name app-db-restore-test \
     --network none \
     -e POSTGRES_USER=app \
     -e POSTGRES_DB=app \
     -e POSTGRES_HOST_AUTH_METHOD=trust \
     postgres:17

   trap 'docker rm -f app-db-restore-test >/dev/null 2>&1 || true' EXIT

   ready=false
   for attempt in {1..60}; do
     if docker exec app-db-restore-test \
       pg_isready -h 127.0.0.1 -U app -d app >/dev/null 2>&1; then
       ready=true
       break
     fi
     sleep 1
   done

   if [ "$ready" != true ]; then
     docker logs app-db-restore-test
     exit 1
   fi

   docker cp "$backup" app-db-restore-test:/tmp/app.dump

   docker exec app-db-restore-test \
     pg_restore --exit-on-error -U app -d app /tmp/app.dump

   docker exec -i app-db-restore-test \
     psql -X -v ON_ERROR_STOP=1 -U app -d app <<'SQL'
   SELECT format(
     'SELECT %L AS table_name, count(*) AS row_count FROM %I.%I;',
     schemaname || '.' || tablename, schemaname, tablename
   )
   FROM pg_tables
   WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
   ORDER BY schemaname, tablename
   \gexec
   SQL

   printf 'Restore test complete: %s\n' "$backup"
   TEST
   ```

   Check the table names and row counts against expected values. Add SQL queries for known application records before the closing `SQL` line.

   `pg_restore --exit-on-error` stops if a restore operation fails. The test removes its container and temporary database automatically.

   If other database roles are necessary, create them in the test container before `pg_restore`. Back up those roles separately.

4. **Set the time for the backup.**

   ```bash
   sudo tee /etc/systemd/system/app-db-backup.timer >/dev/null <<'TIMER'
   [Unit]
   Description=Start backup at 02:00 UTC each day

   [Timer]
   OnCalendar=*-*-* 02:00:00 UTC
   Persistent=true
   Unit=app-db-backup.service

   [Install]
   WantedBy=timers.target
   TIMER

   sudo systemctl daemon-reload
   sudo systemctl enable --now app-db-backup.timer
   sudo systemctl list-timers app-db-backup.timer --no-pager
   ```

   `Persistent=true` starts a missed backup when the timer becomes active again.

5. **Check the backups regularly.**

   Read the service log:

   ```bash
   sudo journalctl -u app-db-backup.service --since "7 days ago" --no-pager
   ```

   Repeat the restore test regularly. Copy backups to separate storage to protect them from server failure.