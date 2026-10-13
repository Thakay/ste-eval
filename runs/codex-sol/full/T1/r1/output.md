Use a systemd timer to create a backup each night at 02:00, using the server’s local time.

1. **Open a root shell. Create a private backup directory. Check database access.**

   Run all subsequent commands in this root shell.

   ```bash
   sudo -i
   install -d -m 0700 /var/backups/app-db

   docker exec app-db psql --no-password -U app -d app \
     -c 'SELECT current_database(), current_user, version();'
   ```

   If authentication fails, configure `.pgpass` for the OS user that `docker exec` uses. Set its permissions to `0600`.

2. **Create the backup script.**

   `pg_dump` creates a consistent database snapshot while the database runs. The script deletes backups aged seven days or more after a successful dump.

   ```bash
   cat > /usr/local/sbin/backup-app-db <<'EOF'
   #!/bin/bash
   set -euo pipefail
   umask 077

   backup_dir=/var/backups/app-db
   backup_file="$backup_dir/app-$(date -u +%Y%m%dT%H%M%SZ).dump"
   temporary_file=$(mktemp "$backup_dir/.app-XXXXXX.partial")

   trap 'rm -f -- "$temporary_file"' EXIT

   /usr/bin/docker exec app-db \
     pg_dump --no-password --format=custom --username=app --dbname=app \
     > "$temporary_file"

   test -s "$temporary_file"
   mv -- "$temporary_file" "$backup_file"

   find "$backup_dir" -maxdepth 1 -type f \
     -name 'app-*.dump' -mtime +6 -delete

   printf 'Created backup: %s\n' "$backup_file"
   EOF

   chmod 0700 /usr/local/sbin/backup-app-db
   ```

3. **Create the service and timer.**

   ```bash
   cat > /etc/systemd/system/app-db-backup.service <<'EOF'
   [Unit]
   Description=Back up the app PostgreSQL database
   Requires=docker.service
   After=docker.service

   [Service]
   Type=oneshot
   User=root
   ExecStart=/usr/local/sbin/backup-app-db
   EOF

   cat > /etc/systemd/system/app-db-backup.timer <<'EOF'
   [Unit]
   Description=Run the app database backup each night

   [Timer]
   OnCalendar=*-*-* 02:00:00
   Persistent=true

   [Install]
   WantedBy=timers.target
   EOF
   ```

   `Persistent=true` starts a missed backup when the timer next becomes active.

4. **Create the first backup. Check the result.**

   ```bash
   systemctl daemon-reload
   systemctl start app-db-backup.service
   journalctl -u app-db-backup.service -n 20 --no-pager
   ls -lh /var/backups/app-db
   ```

   Continue only if the service succeeds and creates a `.dump` file.

5. **Test a restore in a separate container.**

   The test uses the same image as `app-db`. It assumes the image supports the official PostgreSQL `POSTGRES_*` variables.

   Replace `public.your_table` with an application table before you run this code. Check the printed table list and row count.

   The test restores schema and data. It skips saved owners and permissions. The test removes its container and volume when it ends.

   ```bash
   (
     set -euo pipefail

     backup_file=$(find /var/backups/app-db -maxdepth 1 -type f \
       -name 'app-*.dump' -printf '%p\n' | sort | tail -n 1)
     test -n "$backup_file"

     test_container="app-db-restore-test-$$"
     image_id=$(docker inspect --format '{{.Image}}' app-db)

     docker run --detach --name "$test_container" \
       --network none \
       --env POSTGRES_USER=app \
       --env POSTGRES_DB=app \
       --env POSTGRES_PASSWORD=restore-test-only \
       "$image_id" >/dev/null

     trap 'docker rm -f -v "$test_container" >/dev/null' EXIT

     ready=0
     for attempt in {1..60}; do
       if docker exec "$test_container" pg_isready \
           -h 127.0.0.1 -U app -d app >/dev/null 2>&1; then
         ready=1
         break
       fi
       sleep 1
     done

     if [ "$ready" -ne 1 ]; then
       docker logs "$test_container"
       exit 1
     fi

     docker exec -i "$test_container" pg_restore \
       --exit-on-error --single-transaction \
       --no-owner --no-privileges \
       --username=app --dbname=app < "$backup_file"

     docker exec "$test_container" psql \
       -X -v ON_ERROR_STOP=1 -U app -d app -c '\dt'

     docker exec "$test_container" psql \
       -X -v ON_ERROR_STOP=1 -U app -d app \
       -c 'SELECT count(*) FROM public.your_table;'

     printf 'Restore succeeded: %s\n' "$backup_file"
   )
   ```

   `--exit-on-error` makes restoration errors fail the test. Add queries for known records to check application data.

6. **Enable the nightly schedule after the restore succeeds.**

   ```bash
   systemctl enable --now app-db-backup.timer
   systemctl list-timers app-db-backup.timer
   ```

   Repeat the restore test regularly. Check backup results with:

   ```bash
   journalctl -u app-db-backup.service --since yesterday --no-pager
   ```

   Copy backups to separate storage for recovery after server disk failure. Save required cluster roles and server settings separately.

   Leave the root shell with `exit`.

Godspeed, Spartan.