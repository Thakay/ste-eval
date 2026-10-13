Use `pg_dump` inside the container and save its output on the host. It creates a consistent backup while the database stays online.

1. **Create a protected backup directory.**

   ```bash
   sudo install -d -m 0700 /var/backups/app-db
   ```

2. **Create `/usr/local/sbin/backup-app-db` with this content.**

   ```bash
   #!/bin/bash
   set -euo pipefail
   export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
   umask 077

   # Prevent overlapping runs.
   exec 9>/run/lock/app-db-backup.lock
   flock -n 9 || exit 1

   directory=/var/backups/app-db
   timestamp=$(date -u +%Y%m%dT%H%M%SZ)
   backup="$directory/app_$timestamp.dump"
   temporary="$backup.partial"

   trap 'rm -f -- "$temporary"' EXIT

   docker exec app-db \
     pg_dump --username=app --dbname=app \
       --format=custom --no-password > "$temporary"

   test -s "$temporary"
   mv -- "$temporary" "$backup"

   # Delete completed backups at least 7 days old.
   find "$directory" -maxdepth 1 -type f \
     -name 'app_*.dump' -mtime +6 -delete

   printf 'Created %s\n' "$backup"
   ```

   The custom format includes compression and supports `pg_restore`. A failed dump never becomes a completed backup, and retention runs only after a successful backup.

   This uses local socket authentication inside the container. If it requires a password, configure a `.pgpass` file inside the container, owned by the OS user running `pg_dump`, with mode `0600`. Alternatively, configure `PGPASSFILE` for the `docker exec` process. `--no-password` makes unattended runs fail promptly if credentials are missing.

3. **Make it executable and run it once.**

   ```bash
   sudo chown root:root /usr/local/sbin/backup-app-db
   sudo chmod 0700 /usr/local/sbin/backup-app-db
   sudo /usr/local/sbin/backup-app-db
   sudo ls -lh /var/backups/app-db
   ```

4. **Schedule it nightly at 02:00.**

   Open root’s crontab:

   ```bash
   sudo crontab -e
   ```

   Add:

   ```cron
   0 2 * * * /usr/local/sbin/backup-app-db >> /var/log/app-db-backup.log 2>&1
   ```

   This uses the server’s local timezone. Check the log after the first scheduled run and arrange monitoring for failed or missing backups.

5. **Restore a backup into a disposable container.**

   Use the same Postgres 17 image as production, especially if extensions need additional packages. This container has no external networking or published ports.

   ```bash
   IMAGE=$(sudo docker inspect --format '{{.Config.Image}}' app-db)

   sudo docker run -d \
     --name app-db-restore-test \
     --network none \
     -e POSTGRES_USER=app \
     -e POSTGRES_DB=app \
     -e POSTGRES_PASSWORD=temporary-restore-test \
     "$IMAGE"
   ```

   Wait for the final server to start. Checking TCP on loopback avoids mistaking the image’s temporary initialization server for readiness:

   ```bash
   until sudo docker exec app-db-restore-test \
     pg_isready -h 127.0.0.1 -U app -d app >/dev/null 2>&1
   do
     sleep 1
   done
   ```

   If it never becomes ready, inspect `sudo docker logs app-db-restore-test`.

   Set `BACKUP` to an actual completed backup, then restore it:

   ```bash
   BACKUP=/var/backups/app-db/app_YYYYMMDDTHHMMSSZ.dump

   sudo cat "$BACKUP" | sudo docker exec -i app-db-restore-test \
     pg_restore --username=app --dbname=app \
       --exit-on-error --single-transaction \
       --no-owner --no-privileges
   ```

   Require a zero exit status. Then inspect the restored tables:

   ```bash
   sudo docker exec app-db-restore-test \
     psql -U app -d app -v ON_ERROR_STOP=1 -c '\dt'
   ```

   Query important tables for expected row counts and known records, and run representative application queries against the restored database. Repeat this restore test periodically.

   These restore flags verify schema and data while skipping ownership and grants. To verify those too, recreate the production roles and restore without `--no-owner --no-privileges`.

   Remove the test container and its anonymous data volume afterward:

   ```bash
   sudo docker rm -f -v app-db-restore-test
   ```

`pg_dump` does not include cluster roles or server configuration; save those separately. Copy backups to another host or object storage as well, so losing this server does not lose the backups.