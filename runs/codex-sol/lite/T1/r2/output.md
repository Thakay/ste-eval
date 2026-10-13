This setup runs nightly at 02:00, using the server’s local time. It removes completed backups that are at least seven days old.

1. Open a root shell.

   ```bash
   sudo -i
   ```

2. Install cron.

   ```bash
   apt-get update
   apt-get install -y cron
   ```

3. Enable cron.

   ```bash
   systemctl enable --now cron
   ```

4. Create a private backup directory.

   ```bash
   install -d -m 0700 /var/backups/postgresql
   ```

5. Store the current password for database user `app`.

   The backup connects through TCP inside `app-db`. An empty password works only if that connection permits authentication without a password.

   ```bash
   install -m 0600 /dev/null /etc/app-db-backup.password
   read -r -s -p 'Existing password for app: ' backup_password
   printf '\n'
   printf '%s\n' "$backup_password" > /etc/app-db-backup.password
   unset backup_password
   ```

6. Create an executable backup script.

   ```bash
   cat > /usr/local/sbin/backup-app-postgres <<'EOF'
   #!/bin/bash
   set -euo pipefail
   export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
   umask 077

   exec 9>/run/lock/app-postgres-backup.lock
   flock -n 9 || exit 0

   backup_dir=/var/backups/postgresql
   timestamp=$(date -u +%Y%m%dT%H%M%SZ)
   backup_file="$backup_dir/app-$timestamp.dump"
   temporary=$(mktemp "$backup_dir/.app.XXXXXX")
   trap 'rm -f -- "$temporary"' EXIT

   IFS= read -r PGPASSWORD < /etc/app-db-backup.password
   export PGPASSWORD

   docker exec --env PGPASSWORD app-db pg_dump \
     --host=127.0.0.1 \
     --username=app \
     --dbname=app \
     --format=custom \
     --no-password > "$temporary"

   mv -- "$temporary" "$backup_file"

   find "$backup_dir" -maxdepth 1 -type f \
     -name 'app-*.dump' -mtime +6 -delete

   printf 'Created %s\n' "$backup_file"
   EOF

   chmod 0700 /usr/local/sbin/backup-app-postgres
   ```

   The script uses PostgreSQL 17 tools from `app-db`. It creates compressed archives with consistent database snapshots.

   Failed dumps do not replace completed backups. Cleanup runs only after a successful dump. `-mtime +6` selects files at least seven days old.

7. Create the first backup.

   ```bash
   /usr/local/sbin/backup-app-postgres
   ```

8. Start a separate PostgreSQL 17 container for the restore test.

   This container has no external network connection or published ports. Applications that use additional extensions need a test image containing those extensions.

   ```bash
   docker run --detach \
     --name app-db-restore-test \
     --network none \
     --env POSTGRES_USER=app \
     --env POSTGRES_DB=app \
     --env POSTGRES_PASSWORD="$(cat /proc/sys/kernel/random/uuid)" \
     postgres:17
   ```

9. Wait for the test database to start.

   ```bash
   timeout 60 bash -c '
     until docker exec app-db-restore-test \
       pg_isready --host=127.0.0.1 --username=app --dbname=app \
       >/dev/null 2>&1
     do
       sleep 1
     done
   '
   ```

   A timeout indicates that the test database did not become ready.

10. Restore the newest backup into the test database.

    ```bash
    backup_file=$(find /var/backups/postgresql \
      -maxdepth 1 -type f -name 'app-*.dump' -printf '%p\n' |
      sort | tail -n 1)

    test -n "$backup_file" &&
    docker exec -i app-db-restore-test pg_restore \
      --username=app \
      --dbname=app \
      --exit-on-error \
      --single-transaction \
      --no-owner \
      --no-privileges < "$backup_file"
    ```

    A successful restore returns exit code zero. These options restore data and schema under `app`; they skip original ownership and grants.

11. Check the restored tables and expected application records.

    In this example, `public.your_table` represents an actual application table.

    ```bash
    docker exec app-db-restore-test psql \
      --username=app --dbname=app \
      --set=ON_ERROR_STOP=1 \
      --command='\dt'

    docker exec app-db-restore-test psql \
      --username=app --dbname=app \
      --set=ON_ERROR_STOP=1 \
      --command='SELECT count(*) FROM public.your_table;'

    docker exec app-db-restore-test psql \
      --username=app --dbname=app \
      --set=ON_ERROR_STOP=1 \
      --command='SELECT * FROM public.your_table LIMIT 5;'
    ```

    Expected records and successful application queries provide stronger evidence than a table list alone. Live database counts can change after the backup.

12. Remove the test container and its temporary data.

    ```bash
    docker rm --force --volumes app-db-restore-test
    ```

13. If the restore test passes, create the nightly schedule.

    ```bash
    install -m 0600 /dev/null /var/log/app-postgres-backup.log

    cat > /etc/cron.d/app-postgres-backup <<'EOF'
    SHELL=/bin/bash
    PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
    0 2 * * * root /usr/local/sbin/backup-app-postgres >> /var/log/app-postgres-backup.log 2>&1
    EOF

    chmod 0644 /etc/cron.d/app-postgres-backup
    ```

14. Check the log after the first scheduled backup.

    ```bash
    tail -n 50 /var/log/app-postgres-backup.log
    ```

These backups cover `app` data and schema. Database roles and server configuration need separate backups. A copy outside this server protects against server loss.

Godspeed Spartan.