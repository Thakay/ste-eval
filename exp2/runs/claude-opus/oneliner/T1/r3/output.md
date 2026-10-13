# Nightly backup of the database `app` (Postgres 17 in Docker)

Do all the steps as the root user. To open a root shell, use `sudo -i`.

## 1. Prepare the server

1. Make sure that the container `app-db` operates:
   ```bash
   docker ps --filter name=app-db
   ```
2. Make sure that `pg_dump` can connect to the database:
   ```bash
   docker exec app-db pg_dump -U app -d app --schema-only | head -n 5
   ```
   The output must show SQL lines. The command must not ask for a password. If it asks for a password, see Note 3.
3. Find the size of the database:
   ```bash
   docker exec app-db psql -U app -d app -Atc "SELECT pg_size_pretty(pg_database_size('app'))"
   df -h /var/backups
   ```
   The backup file is compressed, so it is usually much smaller than the database. Make sure that the disk has space for a minimum of 8 backup files.

## 2. Write the backup script

1. Write the script:
   ```bash
   cat > /usr/local/bin/pg-backup-app.sh <<'EOF'
   #!/usr/bin/env bash
   # Make a backup of the database "app" in the container "app-db".
   # Remove backups that are older than KEEP_DAYS days.
   set -euo pipefail

   CONTAINER="app-db"
   DB_NAME="app"
   DB_USER="app"
   BACKUP_DIR="/var/backups/postgres/app"
   KEEP_DAYS=7

   umask 077
   mkdir -p "$BACKUP_DIR"

   STAMP="$(date +%Y-%m-%d_%H%M%S)"
   FINAL_FILE="$BACKUP_DIR/${DB_NAME}_${STAMP}.dump"
   PART_FILE="$FINAL_FILE.part"

   # If the script stops before the end, remove the incomplete file.
   trap 'rm -f "$PART_FILE"' EXIT

   # Write the dump in custom format (compressed, for pg_restore).
   docker exec "$CONTAINER" \
     pg_dump -U "$DB_USER" -d "$DB_NAME" --format=custom > "$PART_FILE"

   # Make sure that the file is not empty and that pg_restore can read it.
   test -s "$PART_FILE"
   docker exec -i "$CONTAINER" pg_restore --list < "$PART_FILE" > /dev/null

   mv "$PART_FILE" "$FINAL_FILE"
   echo "Backup OK: $FINAL_FILE ($(du -h "$FINAL_FILE" | cut -f1))"

   # Remove backup files that are KEEP_DAYS days old or older.
   find "$BACKUP_DIR" -maxdepth 1 -type f -name "${DB_NAME}_*.dump" \
     -mtime +$((KEEP_DAYS - 1)) -print -delete
   EOF
   chmod 700 /usr/local/bin/pg-backup-app.sh
   ```

2. Read these facts about the script:
   - The script uses the `pg_dump` in the container. Thus, the `pg_dump` version is always the same as the server version.
   - The script writes to a `.part` file first. It changes the file name only after a successful dump. Thus, each `.dump` file is from a successful `pg_dump`.
   - The script removes old files only after a successful backup. If a backup is not successful, the old backups stay.
   - The backup directory and the files are available only to root (`umask 077`).

> **CAUTION:** Do not add the `-t` option to `docker exec`. The `-t` option makes a terminal. The terminal can change the binary data, and then `pg_restore` cannot read the file.

## 3. Make the systemd service and timer

1. Write the service file:
   ```bash
   cat > /etc/systemd/system/pg-backup-app.service <<'EOF'
   [Unit]
   Description=Backup of Postgres database app (container app-db)
   Requires=docker.service
   After=docker.service

   [Service]
   Type=oneshot
   ExecStart=/usr/local/bin/pg-backup-app.sh
   EOF
   ```
   **NOTE:** If you installed Docker from the snap package, replace `docker.service` with `snap.docker.dockerd.service`.

2. Write the timer file. This timer starts the backup each night at 02:30:
   ```bash
   cat > /etc/systemd/system/pg-backup-app.timer <<'EOF'
   [Unit]
   Description=Nightly backup of Postgres database app

   [Timer]
   OnCalendar=*-*-* 02:30:00
   Persistent=true

   [Install]
   WantedBy=timers.target
   EOF
   ```
   With `Persistent=true`, the backup starts after the next boot if the server was off at 02:30.

3. Load the files and start the timer:
   ```bash
   systemctl daemon-reload
   systemctl enable --now pg-backup-app.timer
   systemctl list-timers pg-backup-app.timer
   ```
   The `NEXT` column must show the next 02:30.

## 4. Test the backup and the 7-day limit

1. Start a backup now:
   ```bash
   systemctl start pg-backup-app.service
   ```
2. Examine the log:
   ```bash
   journalctl -u pg-backup-app.service -n 20 --no-pager
   ```
   The log must show `Backup OK`.
3. Examine the backup directory:
   ```bash
   ls -lh /var/backups/postgres/app/
   ```
4. Test the removal of old files. Make a test file with a date of 8 days ago:
   ```bash
   touch -d '8 days ago' /var/backups/postgres/app/app_2000-01-01_000000.dump
   systemctl start pg-backup-app.service
   ls /var/backups/postgres/app/
   ```
   The test file must not be in the list. The log shows the name of each file that the script removes.

## 5. Test a restore

A backup is not useful if you cannot restore it. Do this test now. Then do it again each month.

1. Find the newest backup file:
   ```bash
   BACKUP=$(ls -1t /var/backups/postgres/app/app_*.dump | head -n 1)
   echo "$BACKUP"
   ```

2. Find the image of `app-db`:
   ```bash
   IMAGE=$(docker inspect --format '{{.Config.Image}}' app-db)
   echo "$IMAGE"
   ```
   Use the same image for the test. Then the test server has the same Postgres version and the same extensions.

3. Start a test container:
   ```bash
   docker run -d --name app-db-restore-test \
     -e POSTGRES_USER=app -e POSTGRES_DB=app -e POSTGRES_PASSWORD=restore-test \
     "$IMAGE"
   ```
   The test container does not publish a port. Thus, it is not available from the network.

4. Wait until the test server is ready:
   ```bash
   until docker exec app-db-restore-test pg_isready -h 127.0.0.1 -U app -d app > /dev/null 2>&1; do
     sleep 1
   done
   ```
   **NOTE:** Use `-h 127.0.0.1`. At the first start, the image starts a temporary server on the Unix socket only. Then it stops that server and starts the real server. The TCP test shows "ready" only for the real server.

5. Restore the backup into the test database:
   ```bash
   docker exec -i app-db-restore-test \
     pg_restore -U app -d app --single-transaction --exit-on-error < "$BACKUP" \
     && echo "RESTORE OK"
   ```
   The output must show `RESTORE OK`. With `--single-transaction`, `pg_restore` makes no changes if an error occurs. Thus, you can correct the cause and do this step again.
   - If the error is `role "..." does not exist`, the database uses more roles than `app`. Make each role in the test container, for example: `docker exec app-db-restore-test psql -U app -d app -c 'CREATE ROLE readonly;'`
   - If the error is `... already exists`, the image has init scripts that make objects. Make an empty database with `docker exec app-db-restore-test createdb -U app app_restored`. Then restore with `-d app_restored`.

6. Compare the tables and the row counts. Write the query file:
   ```bash
   cat > /root/row-counts.sql <<'EOF'
   SELECT table_schema || '.' || table_name AS table_name,
          (xpath('/row/c/text()',
             query_to_xml(format('SELECT count(*) AS c FROM %I.%I', table_schema, table_name),
                          false, true, '')))[1]::text::bigint AS row_count
   FROM information_schema.tables
   WHERE table_type = 'BASE TABLE'
     AND table_schema NOT IN ('pg_catalog', 'information_schema')
   ORDER BY 1;
   EOF
   ```
   Run the query on the two databases and compare the results:
   ```bash
   docker exec -i app-db psql -X -U app -d app -At -F ' ' < /root/row-counts.sql > /root/rows-prod.txt
   docker exec -i app-db-restore-test psql -X -U app -d app -At -F ' ' < /root/row-counts.sql > /root/rows-restore.txt
   diff -y --suppress-common-lines /root/rows-prod.txt /root/rows-restore.txt
   ```
   The list of tables must be the same. Row counts can be a little different, because the production database changed after the backup. A missing table or a large difference shows a problem.

   > **CAUTION:** The query counts all rows in all tables. On a large production database, do this step at a time of low load.

7. Examine the newest data in the restored database. For example:
   ```bash
   docker exec app-db-restore-test psql -U app -d app -c "SELECT max(created_at) FROM orders;"
   ```
   Replace `orders` and `created_at` with a table and a column from your application. The result must be near the time of the backup.

8. Remove the test container and its data:
   ```bash
   docker rm -f -v app-db-restore-test
   rm -f /root/rows-prod.txt /root/rows-restore.txt
   ```
   The `-v` option removes the anonymous volume with the test data. Keep `/root/row-counts.sql` for the next test.

## Notes

1. **WARNING:** The backups are on the same server as the database. If the server or its disk has a failure, you can lose the database and the backups. Copy the backup directory to a different location each day. For example, use `restic` or `rclone` to object storage, or `rsync` to a different server.

2. The timer does not send an alert if a backup is not successful. Add an alert. For example, add `OnFailure=` to the service file to start a unit that sends a message. Or, set your monitoring system to examine the age of the newest backup file.

3. If `pg_dump` asks for a password, put the password in a file that only root can read:
   ```bash
   install -m 600 /dev/null /root/.app-db-password
   # Write the password into /root/.app-db-password.
   ```
   In the script, add this line before the first `docker exec`:
   ```bash
   export PGPASSWORD="$(cat /root/.app-db-password)"
   ```
   Then add `-e PGPASSWORD` to each `docker exec` command. If `-e` has no value, Docker copies the value from the environment. Thus, the password is not on the command line.

4. The dump has the database `app` only. It does not have the roles and their passwords. To keep the roles too, also keep the output of `pg_dumpall -U app --globals-only`. This command must use a superuser.