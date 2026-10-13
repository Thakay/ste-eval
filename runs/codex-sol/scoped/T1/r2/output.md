These steps create a backup each night at 02:00, using the server’s time zone. Each backup contains the `app` database’s schema and data. It excludes cluster roles and server settings.

Docker must already run, and `app-db` must contain PostgreSQL 17.

1. Check database access inside the container.

   ```bash
   sudo docker exec app-db psql \
     --username=app --dbname=app --no-password \
     --command='SELECT current_database(), current_user;'
   ```

   If password authentication is required, configure `.pgpass` for the container’s operating system user. The file must have permissions `0600`.

2. Install `cron`.

   ```bash
   sudo apt-get update
   sudo apt-get install -y cron
   ```

3. Configure `cron` to run now and after each reboot.

   ```bash
   sudo systemctl enable --now cron
   ```

4. Create a protected backup directory.

   ```bash
   sudo install -d -o root -g root -m 0700 /var/backups/postgresql
   ```

5. Create the backup script.

   ```bash
   sudo tee /usr/local/sbin/backup-app-db >/dev/null <<'EOF'
   #!/bin/bash
   set -euo pipefail
   umask 077
   export PATH=/usr/sbin:/usr/bin:/sbin:/bin

   backup_dir=/var/backups/postgresql

   exec 9>/run/lock/app-postgres-backup.lock
   flock -n 9 || exit 0

   tmp=$(mktemp "$backup_dir/.app-backup.XXXXXX")
   trap 'rm -f -- "$tmp"' EXIT

   docker exec app-db pg_dump \
     --username=app \
     --dbname=app \
     --no-password \
     --format=custom > "$tmp"

   mv -- "$tmp" "$backup_dir/app-$(date -u +%Y%m%dT%H%M%SZ).dump"

   find "$backup_dir" -maxdepth 1 -type f \
     -name 'app-*.dump' -mtime +6 -delete
   EOF

   sudo chmod 0700 /usr/local/sbin/backup-app-db
   ```

   The script saves a completed backup only when `pg_dump` succeeds. It then deletes backups at least seven days old. Temporary files do not appear as completed backups.

6. Run the script once.

   ```bash
   sudo /usr/local/sbin/backup-app-db
   ```

7. Create the nightly schedule.

   ```bash
   sudo tee /etc/cron.d/app-postgres-backup >/dev/null <<'EOF'
   SHELL=/bin/bash
   PATH=/usr/sbin:/usr/bin:/sbin:/bin
   0 2 * * * root /usr/local/sbin/backup-app-db >> /var/log/app-postgres-backup.log 2>&1
   EOF

   sudo chmod 0644 /etc/cron.d/app-postgres-backup
   ```

8. Select the latest backup for the restore test.

   ```bash
   backup=$(sudo find /var/backups/postgresql -maxdepth 1 -type f \
     -name 'app-*.dump' -print | sort | tail -n 1)

   printf '%s\n' "$backup"
   ```

9. Create an isolated PostgreSQL 17 container for the restore test.

   ```bash
   sudo docker run --detach \
     --name app-db-restore-test \
     --network none \
     --env POSTGRES_USER=app \
     --env POSTGRES_PASSWORD=restore-test-only \
     --env POSTGRES_DB=app \
     postgres:17
   ```

   If `app` uses additional extensions, use a PostgreSQL 17 image that contains those extensions.

10. Wait for the test database to become ready.

    ```bash
    sudo timeout 60s bash -c '
      until docker exec app-db-restore-test pg_isready \
        --host=127.0.0.1 --username=app --dbname=app >/dev/null 2>&1
      do
        sleep 1
      done
    '
    ```

    If this command fails, inspect the container log before continuing.

    ```bash
    sudo docker logs app-db-restore-test
    ```

11. Restore the backup into the test database.

    ```bash
    sudo bash -c '
      docker exec -i app-db-restore-test pg_restore \
        --username=app \
        --dbname=app \
        --no-password \
        --exit-on-error \
        --single-transaction \
        --no-owner \
        --no-privileges < "$1"
    ' _ "$backup"
    ```

    This command must finish without errors. The test skips original ownership and grants. A production restore also needs the required roles and permission checks.

12. Check the restored database with your application’s validation queries.

    ```bash
    sudo docker exec -it app-db-restore-test psql \
      --username=app --dbname=app
    ```

    In `psql`, `\dt` lists tables. Application queries should return expected records, counts, and totals from the backup time. `\q` closes `psql`.

    Successful restoration and correct query results demonstrate that the tested backup is usable.

13. Remove the test container and its temporary database.

    ```bash
    sudo docker rm --force --volumes app-db-restore-test
    ```

14. Check the backup log regularly.

    ```bash
    sudo tail -n 50 /var/log/app-postgres-backup.log
    ```

15. Repeat the restore test periodically.

Stay ready, Spartan.