These steps make a backup each day at 02:00 UTC. The database can stay in use during the backup.

Docker must be installed, and `app-db` must be running. Database user `app` must have permission to read all database data.

1. Open a root shell.

   ```bash
   sudo -i
   ```

2. Create the backup directory and script.

   ```bash
   install -d -m 0700 /var/backups/app-db

   cat > /usr/local/sbin/backup-app-db <<'EOF'
   #!/bin/bash
   set -euo pipefail
   umask 077

   backup_dir=/var/backups/app-db
   backup_file="$backup_dir/app-$(date -u +%Y%m%dT%H%M%SZ).dump"
   temporary_file=$(mktemp "$backup_dir/.app-XXXXXX")
   trap 'rm -f -- "$temporary_file"' EXIT

   docker exec app-db pg_dump \
     --username=app \
     --dbname=app \
     --format=custom \
     > "$temporary_file"

   mv -- "$temporary_file" "$backup_file"

   find "$backup_dir" -maxdepth 1 -type f \
     -name 'app-*.dump' -mtime +6 -delete
   EOF

   chmod 0700 /usr/local/sbin/backup-app-db
   ```

   The script saves each completed backup before it removes backups that are at least 7 days old.

   The command uses a local database connection inside the container. If authentication requires a password, use a `.pgpass` file in the container. Put it in the home directory of the operating system user that runs `pg_dump`. Set its file mode to `0600`.

3. Create the service and timer.

   ```bash
   cat > /etc/systemd/system/app-db-backup.service <<'EOF'
   [Unit]
   Description=Back up the app database
   Requires=docker.service
   After=docker.service

   [Service]
   Type=oneshot
   ExecStart=/usr/local/sbin/backup-app-db
   EOF

   cat > /etc/systemd/system/app-db-backup.timer <<'EOF'
   [Unit]
   Description=Start the app database backup each day

   [Timer]
   OnCalendar=*-*-* 02:00:00 UTC
   Persistent=true

   [Install]
   WantedBy=timers.target
   EOF

   systemctl daemon-reload
   ```

   If the server is off at the scheduled time, the timer starts a backup after the next server start.

4. Make the first backup and examine the log.

   ```bash
   systemctl start app-db-backup.service
   journalctl -u app-db-backup.service -n 30 --no-pager
   ```

   Make sure that the service completed without errors before you continue.

5. Restore the backup into a separate test container.

   Select the latest backup. Use the same Docker image as `app-db`.

   ```bash
   backup=$(find /var/backups/app-db -maxdepth 1 -type f \
     -name 'app-*.dump' -print | sort | tail -n 1)

   test_image=$(docker inspect --format '{{.Image}}' app-db)

   docker run --detach --rm \
     --name app-db-restore-test \
     --network none \
     -e POSTGRES_USER=app \
     -e POSTGRES_DB=app \
     -e POSTGRES_PASSWORD=restore-test-only \
     "$test_image"
   ```

   This container uses separate database storage. Its password is for the test only.

   Repeat this command until it returns exit code `0`:

   ```bash
   docker exec app-db-restore-test \
     pg_isready -h 127.0.0.1 -U app -d app
   ```

   Restore the backup:

   ```bash
   docker exec -i app-db-restore-test pg_restore \
     --username=app \
     --dbname=app \
     --no-owner \
     --no-privileges \
     --exit-on-error \
     < "$backup"

   echo $?
   ```

   The restore command must return exit code `0`. If it returns another value, examine the error before you continue.

   Examine the tables:

   ```bash
   docker exec app-db-restore-test \
     psql -U app -d app -c '\dt'
   ```

   Check the data. Replace `public.YOUR_TABLE` with an application table:

   ```bash
   docker exec app-db-restore-test \
     psql -U app -d app \
     -c 'SELECT count(*) FROM public.YOUR_TABLE;'
   ```

   Check known records with application queries. Compare the results with expected values for the time of the backup.

   This test checks database structure and data. It skips object owners and access permissions. To test those settings, create the required roles and omit `--no-owner` and `--no-privileges`.

   Remove the test container and its test data:

   ```bash
   docker stop app-db-restore-test
   ```

6. Start the timer after the checks pass.

   ```bash
   systemctl enable --now app-db-backup.timer
   systemctl list-timers app-db-backup.timer
   exit
   ```

Repeat the restore test at regular intervals. `pg_dump` does not save server roles. Save role definitions separately if you need them for recovery.