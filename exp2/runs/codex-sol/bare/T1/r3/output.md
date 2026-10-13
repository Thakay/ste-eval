Use `pg_dump` inside `app-db` so the backup uses the container’s PostgreSQL 17 tools. These steps assume Docker already works and `app` can read everything in the database.

1. **Prepare the host.**

   ```bash
   sudo apt update
   sudo apt install -y cron util-linux
   sudo systemctl enable --now cron

   sudo install -d -m 0700 /var/backups/app-postgres
   sudo install -m 0600 /dev/null /var/log/app-postgres-backup.log
   ```

2. **Create the backup script.**

   Save this as `/usr/local/sbin/backup-app-postgres`, owned by root:

   ```bash
   #!/bin/bash
   set -euo pipefail
   umask 077
   export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

   backup_dir=/var/backups/app-postgres

   # Prevent overlapping runs.
   exec 9>/run/lock/app-postgres-backup.lock
   flock -n 9 || {
       echo "Another backup is running" >&2
       exit 1
   }

   stamp=$(date -u +%Y%m%dT%H%M%SZ)
   tmp=$(mktemp "$backup_dir/.app-XXXXXX")
   trap 'rm -f "$tmp"' EXIT

   # Custom-format archive; do not allocate a terminal with docker exec -t.
   docker exec app-db pg_dump \
       --username=app \
       --dbname=app \
       --format=custom \
       --no-password > "$tmp"

   test -s "$tmp"
   mv "$tmp" "$backup_dir/app-$stamp.dump"

   # Delete backups aged seven days or more, after a successful backup.
   find "$backup_dir" -maxdepth 1 -type f \
       -name 'app-*.dump' -mtime +6 -delete

   echo "Backup completed: app-$stamp.dump"
   ```

   Make it executable and run it once:

   ```bash
   sudo chown root:root /usr/local/sbin/backup-app-postgres
   sudo chmod 0750 /usr/local/sbin/backup-app-postgres
   sudo /usr/local/sbin/backup-app-postgres
   ```

   `--no-password` makes unattended authentication failures fail immediately. If the container requires a password, configure a protected `.pgpass` file for the operating-system account used by `docker exec`, with mode `0600`, then repeat the manual run.

3. **Schedule it nightly at 02:00 in the server’s timezone.**

   ```bash
   sudo tee /etc/cron.d/app-postgres-backup >/dev/null <<'EOF'
   0 2 * * * root /usr/local/sbin/backup-app-postgres >> /var/log/app-postgres-backup.log 2>&1
   EOF

   sudo chown root:root /etc/cron.d/app-postgres-backup
   sudo chmod 0644 /etc/cron.d/app-postgres-backup
   ```

   Check `/var/log/app-postgres-backup.log` after the first scheduled run. Arrange monitoring for failed or missing backups.

4. **Test a real restore into a disposable PostgreSQL 17 container.**

   This container has separate storage and no network access. If production uses additional extensions, use an image containing the same extensions instead of plain `postgres:17`.

   ```bash
   sudo bash <<'EOF'
   set -euo pipefail

   backup=$(find /var/backups/app-postgres -maxdepth 1 \
       -type f -name 'app-*.dump' | sort | tail -n 1)
   test -n "$backup"

   docker run -d --rm \
       --name app-db-restore-test \
       --network none \
       -e POSTGRES_USER=app \
       -e POSTGRES_DB=app \
       -e POSTGRES_PASSWORD="$(openssl rand -hex 24)" \
       postgres:17

   # --rm also removes this container's anonymous data volume.
   trap 'docker stop app-db-restore-test >/dev/null' EXIT

   timeout 60 bash -c '
       until docker exec app-db-restore-test \
           pg_isready -h 127.0.0.1 -U app -d app >/dev/null 2>&1
       do
           sleep 1
       done
   '

   docker exec -i app-db-restore-test pg_restore \
       --username=app \
       --dbname=app \
       --exit-on-error \
       --single-transaction < "$backup"

   docker exec app-db-restore-test psql \
       -U app -d app -v ON_ERROR_STOP=1 -c '\dt'

   # Add checks against your actual application tables here:
   # docker exec app-db-restore-test psql \
   #     -U app -d app -v ON_ERROR_STOP=1 \
   #     -c 'SELECT count(*) FROM public.your_important_table;'

   echo "Restore succeeded: $backup"
   EOF
   ```

   A successful restore proves the archive can be loaded. Also verify expected tables, representative records, and application queries; a table listing alone cannot prove the data is complete. Repeat this test periodically.

`pg_dump` includes database schema and data, but not PostgreSQL role definitions or server configuration. Preserve those separately; recreate any additional roles needed by ownership or grants before restoring. Keep an off-server copy as well for recovery from server or disk loss.