This setup runs nightly at 02:00 UTC. It removes backups at least seven days old after each successful backup.

The commands assume local database authentication works inside `app-db`. Password authentication requires a `.pgpass` file with mode `0600` for the container’s operating system user.

1. Open a root shell.

   ```bash
   sudo -i
   ```

2. Create a private backup directory.

   ```bash
   install -d -m 0700 /var/backups/postgresql/app
   ```

3. Create the backup script.

   ```bash
   cat > /usr/local/sbin/backup-app <<'EOF'
   #!/usr/bin/env bash
   set -euo pipefail
   umask 077

   backup_dir=/var/backups/postgresql/app
   timestamp=$(date -u +%Y-%m-%dT%H%M%SZ)
   backup_file="$backup_dir/app-$timestamp.dump"
   temporary_file=$(mktemp "$backup_dir/.app-XXXXXX")

   trap 'rm -f -- "$temporary_file"' EXIT

   /usr/bin/docker exec app-db pg_dump \
     --username=app \
     --dbname=app \
     --format=custom \
     --no-password > "$temporary_file"

   test -s "$temporary_file"
   mv -- "$temporary_file" "$backup_file"

   find "$backup_dir" -maxdepth 1 -type f \
     -name 'app-*.dump' -mtime +6 -delete

   printf 'Saved %s\n' "$backup_file"
   EOF
   ```

   `pg_dump` creates a consistent backup while the database runs. The script publishes the backup only after `pg_dump` succeeds.

   `-mtime +6` selects files at least seven full days old. A failed backup leaves existing backups untouched.

4. Protect the backup script.

   ```bash
   chmod 0700 /usr/local/sbin/backup-app
   ```

5. Create the systemd service.

   ```bash
   cat > /etc/systemd/system/app-db-backup.service <<'EOF'
   [Unit]
   Description=Back up PostgreSQL database app

   [Service]
   Type=oneshot
   User=root
   ExecStart=/usr/local/sbin/backup-app
   TimeoutStartSec=infinity
   EOF
   ```

6. Create the nightly timer.

   ```bash
   cat > /etc/systemd/system/app-db-backup.timer <<'EOF'
   [Unit]
   Description=Nightly backup of PostgreSQL database app

   [Timer]
   OnCalendar=*-*-* 02:00:00 UTC
   Persistent=true

   [Install]
   WantedBy=timers.target
   EOF
   ```

   `Persistent=true` triggers a missed backup after the server starts again.

7. Load the new systemd files.

   ```bash
   systemctl daemon-reload
   ```

8. Run the first backup.

   ```bash
   systemctl start app-db-backup.service
   ```

   If this command fails, inspect the service log:

   ```bash
   journalctl -u app-db-backup.service -n 50 --no-pager
   ```

9. If the backup succeeds, enable the nightly timer.

   ```bash
   systemctl enable --now app-db-backup.timer
   ```

10. Check the next scheduled run.

    ```bash
    systemctl list-timers app-db-backup.timer
    ```

11. Select the latest backup for a restore test.

    ```bash
    backup=$(find /var/backups/postgresql/app \
      -maxdepth 1 -type f -name 'app-*.dump' \
      -print | sort | tail -n 1)

    test -n "$backup"
    ```

12. Start a separate restore container.

    ```bash
    image=$(docker inspect --format '{{.Image}}' app-db)

    docker run --detach \
      --name app-db-restore-test \
      --network none \
      --mount type=volume,destination=/var/lib/postgresql/data \
      --env POSTGRES_USER=app \
      --env POSTGRES_DB=app_restore \
      --env POSTGRES_PASSWORD=restore-test-only \
      "$image"
    ```

    This container uses the production image and a new volume. It publishes no ports.

    The dump excludes cluster roles and server configuration. Any additional roles referenced by the dump must exist before restoration.

13. Wait for the test database to accept connections.

    ```bash
    docker exec app-db-restore-test sh -c '
      for attempt in $(seq 1 60); do
        if pg_isready -h 127.0.0.1 -U app -d app_restore; then
          exit 0
        fi
        sleep 1
      done
      exit 1
    '
    ```

    If this command fails, inspect `docker logs app-db-restore-test`.

14. If the database is ready, restore the selected backup.

    ```bash
    docker exec -i app-db-restore-test pg_restore \
      --username=app \
      --dbname=app_restore \
      --exit-on-error < "$backup"
    ```

    A zero exit status confirms that PostgreSQL restored the archive without errors.

15. Check important application data in the restored database.

    The example uses `your_table` as a placeholder for a real table.

    ```bash
    docker exec app-db-restore-test psql \
      --username=app \
      --dbname=app_restore \
      --set=ON_ERROR_STOP=1 \
      --command='
        SELECT count(*) FROM public.your_table;
        SELECT * FROM public.your_table LIMIT 5;
      '
    ```

    Expected counts and known records must match the data at backup time. Current production data can differ if the application continues writing.

16. Remove the test container and its volume.

    ```bash
    docker rm --force --volumes app-db-restore-test
    ```

Godspeed Spartan.