A shell script runs `pg_dump` inside `app-db` every night at 02:30 through cron. It writes one compressed backup file to `/var/backups/postgres` and keeps 7 days of backup files. A separate test restores the newest backup file into a temporary container and compares it with the live database.

## 1. Create the backup script

1. Open a root shell: `sudo -i`
2. Create the backup folder:
   ```bash
   install -d -m 700 /var/backups/postgres
   ```
3. Create the file `/usr/local/bin/pg-backup-app.sh` with this content:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   umask 077

   BACKUP_DIR=/var/backups/postgres
   FILE="$BACKUP_DIR/app_$(date +%Y-%m-%d_%H%M).dump"
   TMP="$FILE.partial"
   trap 'rm -f "$TMP"' EXIT

   # Custom format (-Fc): compressed, and pg_restore can read it
   docker exec app-db pg_dump -U app -d app -Fc > "$TMP"

   # Make sure the file is a readable archive before we keep it
   docker exec -i app-db pg_restore --list < "$TMP" > /dev/null
   mv "$TMP" "$FILE"

   # Delete old backup files only after a good backup
   find "$BACKUP_DIR" -name 'app_*.dump' -mtime +6 -delete

   echo "$(date -Is) OK $FILE $(du -h "$FILE" | cut -f1)"
   ```
4. Make the script executable: `chmod 700 /usr/local/bin/pg-backup-app.sh`
5. Run the script one time: `/usr/local/bin/pg-backup-app.sh`
6. Make sure that the output shows `OK` and a file name.
7. If `pg_dump` asks for a password, add `-e PGPASSWORD=yourpassword` after `docker exec` on the `pg_dump` line.

How the script works:
- The official Postgres image trusts local socket connections, so usually no password is necessary.
- The script writes to a `.partial` file first. It renames the file only after `pg_restore --list` can read it.
- If a backup fails, the script stops before the delete step. The old backup files stay.
- `-mtime +6` deletes backup files that are 7 days old or older.

**Warning:** Do not add `-t` to the `docker exec` commands. A terminal (TTY) changes the binary output and corrupts the backup file.

## 2. Schedule the nightly run

1. Create the file `/etc/cron.d/pg-backup-app` with this line:
   ```
   30 2 * * * root /usr/local/bin/pg-backup-app.sh >> /var/log/pg-backup-app.log 2>&1
   ```
2. Make sure that the file ends with a newline. Cron ignores a last line that has no newline.
3. Set the permissions: `chmod 644 /etc/cron.d/pg-backup-app`
4. To see the server time zone for the 02:30 run, run `timedatectl`.
5. On the next morning, read the log: `tail /var/log/pg-backup-app.log`
6. Make sure that a new backup file exists: `ls -lh /var/backups/postgres`

**Warning:** Do not put a dot in the cron file name. Cron ignores files in `/etc/cron.d` that have a dot in the name.

## 3. Test a restore

Do this test after the first backup. Then do it one time each month.

**Warning:** Do not restore into `app-db` for this test. `pg_restore` can change or overwrite the live data.

1. Open a root shell: `sudo -i`
2. Find the newest backup file:
   ```bash
   LATEST=$(ls -1t /var/backups/postgres/app_*.dump | head -n 1); echo "$LATEST"
   ```
3. Find the image that `app-db` uses:
   ```bash
   IMAGE=$(docker inspect -f '{{.Config.Image}}' app-db); echo "$IMAGE"
   ```
   The same image gives the same Postgres version and the same extensions.
4. Start a test container:
   ```bash
   docker run -d --name app-db-restore-test \
     -e POSTGRES_USER=app -e POSTGRES_PASSWORD=test -e POSTGRES_DB=app \
     "$IMAGE"
   ```
   This container publishes no port, so it does not conflict with `app-db`.
5. Wait until the test server is ready:
   ```bash
   until docker exec app-db-restore-test pg_isready -h 127.0.0.1 -U app; do sleep 2; done
   ```
   The check uses `127.0.0.1` on purpose. During setup, the image runs a temporary server that does not listen on TCP.
6. Restore the backup file:
   ```bash
   docker exec -i app-db-restore-test pg_restore -U app -d app --no-owner --exit-on-error < "$LATEST"
   ```
7. Make sure that the command shows no errors.
8. Compare the test container with `app-db`. Replace `users` with an important table in your app:
   ```bash
   for c in app-db app-db-restore-test; do
     echo "== $c"
     docker exec "$c" psql -U app -d app -Atc "SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema');"
     docker exec "$c" psql -U app -d app -Atc "SELECT count(*) FROM users;"
   done
   ```
9. Make sure that the table counts are equal. The row count on `app-db` can be a little higher because of new rows since the backup.
10. Remove the test container and its data volume:
    ```bash
    docker rm -f -v app-db-restore-test
    ```

**Warning:** Make sure that the name is `app-db-restore-test`, not `app-db`. This command deletes the container and its anonymous volumes with no prompt.

## Suggestions

- **Off-site copy.** The backups and the database share one disk now. If the server or disk fails, you lose both. A nightly `rsync` or `rclone copy` of `/var/backups/postgres` to another host or bucket fixes this, and it is the biggest gap in this setup.
- **Failure alert.** Cron fails silently. A ping to a dead-man's-switch service (for example healthchecks.io) at the end of the script alerts you when a night has no ping.
- **Roles.** `pg_dump` does not save roles. If the database uses only the role `app`, the container environment recreates it and you are fine. If other roles exist, also save `pg_dumpall --globals-only` each night, or the restore in step 6 fails on missing roles.
- **Disk space.** Seven backup files need about 7 times the size of one. Check with `df -h /var/backups` after the first week.

Hold the gate, Keeper of the Seven Nights.