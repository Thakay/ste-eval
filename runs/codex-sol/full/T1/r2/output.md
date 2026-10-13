Use cron to run a backup at 02:00 each night. The script keeps backups for seven days.

1. **Prepare the server.**

   Run these commands as root:

   ```bash
   sudo -i
   apt-get update
   apt-get install -y cron
   install -d -m 0700 /var/backups/postgres/app
   touch /var/log/app-postgres-backup.log
   chmod 0600 /var/log/app-postgres-backup.log
   ```

   Continue in this root shell for the remaining steps.

2. **Create the backup script.**

   ```bash
   cat > /usr/local/sbin/backup-app-postgres <<'EOF'
   #!/bin/bash
   set -euo pipefail

   PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
   export PATH
   umask 077

   backup_dir=/var/backups/postgres/app
   backup="$backup_dir/app-$(date -u +%Y%m%dT%H%M%SZ).dump"
   temporary=$(mktemp "$backup_dir/.app-XXXXXX.tmp")

   trap 'rm -f -- "$temporary"' EXIT

   docker exec app-db pg_dump \
     --username=app \
     --dbname=app \
     --format=custom \
     --no-password > "$temporary"

   mv -- "$temporary" "$backup"

   find "$backup_dir" -maxdepth 1 -type f \
     -name 'app-*.dump' -mtime +6 -delete

   printf '%s Backup created: %s\n' "$(date -u +%FT%TZ)" "$backup"
   EOF

   chmod 0700 /usr/local/sbin/backup-app-postgres
   ```

   The dump uses local socket authentication inside `app-db`. If authentication requires a password, configure a `.pgpass` file for the container user. Give that file mode `0600`.

   The script publishes the backup after `pg_dump` succeeds. It then removes backups that are at least seven days old. If the dump fails, the script keeps existing backups.

3. **Schedule the nightly backup.**

   ```bash
   cat > /etc/cron.d/app-postgres-backup <<'EOF'
   SHELL=/bin/bash
   PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
   0 2 * * * root /usr/local/sbin/backup-app-postgres >> /var/log/app-postgres-backup.log 2>&1
   EOF

   chmod 0644 /etc/cron.d/app-postgres-backup
   systemctl enable --now cron
   ```

   Cron uses the server's local time. Backup filenames use UTC.

4. **Create the first backup.**

   ```bash
   /usr/local/sbin/backup-app-postgres
   ls -lh /var/backups/postgres/app
   ```

   Check the scheduled run's log the next morning:

   ```bash
   tail -n 50 /var/log/app-postgres-backup.log
   ```

5. **Test restoration in a separate container.**

   The test uses the same image as `app-db`. It creates separate storage and disables external network access.

   ```bash
   bash <<'EOF'
   set -euo pipefail

   backup=$(find /var/backups/postgres/app -maxdepth 1 -type f \
     -name 'app-*.dump' | sort | tail -n 1)
   : "${backup:?No backup found}"

   image=$(docker inspect --format '{{.Image}}' app-db)

   docker run --detach \
     --name app-db-restore-test \
     --network none \
     --env POSTGRES_USER=app \
     --env POSTGRES_DB=app \
     --env POSTGRES_PASSWORD=restore-test-only \
     "$image" >/dev/null

   trap 'docker rm --force --volumes app-db-restore-test >/dev/null' EXIT

   ready=0
   for attempt in {1..60}; do
     if docker exec app-db-restore-test \
       pg_isready --host=127.0.0.1 --username=app --dbname=app \
       >/dev/null 2>&1; then
       ready=1
       break
     fi
     sleep 2
   done

   if (( ready == 0 )); then
     docker logs app-db-restore-test
     exit 1
   fi

   docker exec -i app-db-restore-test pg_restore \
     --username=app \
     --dbname=app \
     --exit-on-error \
     --no-owner \
     --no-privileges < "$backup"

   docker exec -i app-db-restore-test \
     psql -X --username=app --dbname=app --set=ON_ERROR_STOP=1 <<'SQL'
   SELECT format(
     'SELECT %L AS table_name, count(*) AS row_count FROM %I.%I;',
     schemaname || '.' || tablename,
     schemaname,
     tablename
   )
   FROM pg_tables
   WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
   ORDER BY schemaname, tablename
   \gexec
   SQL

   printf 'Restore and table reads succeeded: %s\n' "$backup"
   EOF
   ```

   This test restores the backup and reads every user table. It then removes the test container and its temporary storage.

   Compare the row counts with expected values for the backup date. Add SQL checks for records that your application requires. Repeat the restore test regularly.

   The test assigns ownership to `app` and skips permissions. A production restore with original ownership and permissions requires the original roles. `pg_dump` does not save cluster role definitions.

Godspeed, Spartan.