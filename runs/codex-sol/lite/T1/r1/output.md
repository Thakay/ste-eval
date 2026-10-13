Use a systemd timer to run the backup at 02:00 each night, using the server’s local time. `pg_dump` creates a consistent backup while the database runs.

These commands assume Docker works with `sudo` and local authentication permits database user `app`. Password authentication requires a `.pgpass` file with mode `0600` in the container user’s home directory.

1. **Create a protected backup directory.**

   ```bash
   sudo install -d -m 0700 /var/backups/postgres/app
   ```

2. **Install the backup script.**

   ```bash
   sudo tee /usr/local/sbin/backup-app-db >/dev/null <<'EOF'
   #!/bin/bash
   set -euo pipefail
   export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
   umask 077

   backup_dir=/var/backups/postgres/app
   backup_file="$backup_dir/app-$(date -u +%Y%m%dT%H%M%SZ).dump"
   temp_file=$(mktemp "$backup_dir/.app-XXXXXX")

   trap 'rm -f -- "$temp_file"' EXIT

   docker exec app-db pg_dump \
     --username=app \
     --dbname=app \
     --format=custom \
     --no-password > "$temp_file"

   mv -- "$temp_file" "$backup_file"

   find "$backup_dir" -maxdepth 1 -type f \
     -name 'app-*.dump' -mmin +10080 -delete

   printf 'Created %s\n' "$backup_file"
   EOF
   ```

   The script publishes the backup file only after `pg_dump` succeeds. After each successful backup, it deletes completed backups older than seven days.

3. **Set the script permissions.**

   ```bash
   sudo chmod 0750 /usr/local/sbin/backup-app-db
   ```

4. **Create the systemd service.**

   ```bash
   sudo tee /etc/systemd/system/app-db-backup.service >/dev/null <<'EOF'
   [Unit]
   Description=Back up the app PostgreSQL database
   Requires=docker.service
   After=docker.service

   [Service]
   Type=oneshot
   User=root
   ExecStart=/usr/local/sbin/backup-app-db
   EOF
   ```

5. **Create the nightly timer.**

   ```bash
   sudo tee /etc/systemd/system/app-db-backup.timer >/dev/null <<'EOF'
   [Unit]
   Description=Run the app database backup nightly

   [Timer]
   OnCalendar=*-*-* 02:00:00
   Persistent=true

   [Install]
   WantedBy=timers.target
   EOF
   ```

   `Persistent=true` runs a missed backup when the timer becomes active again.

6. **Load the systemd files.**

   ```bash
   sudo systemctl daemon-reload
   ```

7. **Enable the timer.**

   ```bash
   sudo systemctl enable --now app-db-backup.timer
   ```

8. **Create the first backup.**

   ```bash
   sudo systemctl start app-db-backup.service
   ```

9. **Check the backup result.**

   ```bash
   sudo journalctl -u app-db-backup.service -n 20 --no-pager
   sudo systemctl list-timers app-db-backup.timer
   sudo ls -lh /var/backups/postgres/app
   ```

   A successful run reports `Created` followed by the backup path.

10. **Start a separate restore test container.**

    ```bash
    sudo docker run --detach \
      --name app-db-restore-test \
      --network none \
      --env POSTGRES_USER=app \
      --env POSTGRES_DB=app \
      --env POSTGRES_PASSWORD=restore-test-only \
      postgres:17
    ```

    This container uses separate storage. Databases with extra extensions require a test image that contains those extensions.

11. **Wait for the test database to become ready.**

    ```bash
    sudo timeout 120s bash -c '
      until docker exec app-db-restore-test \
        pg_isready -h 127.0.0.1 -U app -d app
      do
        sleep 2
      done
    '
    ```

    If this command times out, inspect the container logs before continuing.

12. **Select the newest completed backup.**

    ```bash
    backup_file=$(sudo find /var/backups/postgres/app \
      -maxdepth 1 -type f -name 'app-*.dump' -print |
      sort | tail -n 1)

    printf '%s\n' "$backup_file"
    ```

    If the path is empty, resolve the backup failure before continuing.

13. **Copy the backup into the test container.**

    ```bash
    sudo docker cp "$backup_file" app-db-restore-test:/tmp/app.dump
    ```

14. **Restore the backup.**

    ```bash
    sudo docker exec app-db-restore-test pg_restore \
      --username=app \
      --dbname=app \
      --single-transaction \
      --exit-on-error \
      --no-owner \
      --no-privileges \
      /tmp/app.dump
    ```

    Any restore error causes this command to fail. This test restores schema and data but skips object ownership and permissions.

15. **Check important application data in the restored database.**

    ```bash
    sudo docker exec -it app-db-restore-test \
      psql -U app -d app -v ON_ERROR_STOP=1
    ```

    These example queries use `public.your_table` as a placeholder for a real application table:

    ```sql
    \dt
    SELECT count(*) FROM public.your_table;
    SELECT * FROM public.your_table LIMIT 5;
    \q
    ```

    Known records and correct application query results provide stronger evidence than a table listing alone. Counts can differ from production because production changes after the backup.

16. **Remove the test container and its temporary storage.**

    ```bash
    sudo docker rm --force --volumes app-db-restore-test
    ```

A database dump excludes cluster roles and server configuration. Complete recovery also needs required roles, settings, and extensions.

These backups remain on the server. A separate backup copy protects against server loss.

Godspeed Spartan.