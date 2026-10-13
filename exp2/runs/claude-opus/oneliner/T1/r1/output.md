# Nightly backup of the PostgreSQL 17 database `app`

## Data

| Item | Value |
|---|---|
| Container | `app-db` |
| Database | `app` |
| Database user | `app` |
| Backup directory | `/var/backups/postgres` |
| Backup time | 02:30, each night |
| Retention | 7 days |

## Procedure 1: Make the backup directory

1. Make the directory. Only root can read it.

   ```bash
   sudo install -d -m 700 /var/backups/postgres
   ```

**CAUTION:** Make sure that the disk has space for 8 backup files. For a short time, the new file and 7 old files are on the disk.

## Procedure 2: Write the backup script

1. Make the file `/usr/local/bin/pg-backup.sh` with this content:

   ```bash
   #!/usr/bin/env bash
   # Nightly backup of the database "app" in the container "app-db".
   set -euo pipefail
   umask 077

   CONTAINER=app-db
   DB_NAME=app
   DB_USER=app
   BACKUP_DIR=/var/backups/postgres
   KEEP_DAYS=7

   FILE="$BACKUP_DIR/${DB_NAME}_$(date +%Y-%m-%d_%H%M%S).dump"
   TMP="$FILE.part"
   trap 'rm -f "$TMP"' EXIT

   # Do not use "-t". A TTY changes the binary output.
   docker exec "$CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "$TMP"

   # Read the full archive. This step finds a damaged file.
   docker exec -i "$CONTAINER" pg_restore -f /dev/null < "$TMP"

   mv "$TMP" "$FILE"

   # Remove backups (and old partial files) that are KEEP_DAYS days old or older.
   find "$BACKUP_DIR" -maxdepth 1 -type f -name "${DB_NAME}_*.dump*" \
     -mtime +$((KEEP_DAYS - 1)) -delete

   echo "Backup OK: $FILE ($(du -h "$FILE" | cut -f1))"
   ```

2. Make the script executable for root:

   ```bash
   sudo chmod 700 /usr/local/bin/pg-backup.sh
   ```

3. Start the script one time:

   ```bash
   sudo /usr/local/bin/pg-backup.sh
   sudo ls -lh /var/backups/postgres
   ```

4. Make sure that the directory has one `.dump` file. Make sure that its size is more than zero.

**NOTE:** The script removes backups that are 7 days old or older. Thus, 7 backups stay on the disk: the backup of today and the backups of the 6 days before.

**NOTE:** The script uses the custom format (`-Fc`). This format is compressed. You must use `pg_restore` to restore it. You cannot use `psql`.

**NOTE:** The official `postgres` image accepts socket connections in the container without a password. If your container asks for a password, the script fails. In that case, add `-e PGPASSWORD` to each `docker exec` command. Read the password into `PGPASSWORD` from a file that only root can read.

## Procedure 3: Start the backup each night with a systemd timer

A systemd timer is better than cron here. If the server is off at 02:30, systemd starts the backup when the server starts again. The output goes into the journal.

1. Make the file `/etc/systemd/system/pg-backup.service`:

   ```ini
   [Unit]
   Description=Backup of the app database (container app-db)
   Requires=docker.service
   After=docker.service

   [Service]
   Type=oneshot
   ExecStart=/usr/local/bin/pg-backup.sh
   ```

2. Make the file `/etc/systemd/system/pg-backup.timer`:

   ```ini
   [Unit]
   Description=Nightly backup of the app database

   [Timer]
   OnCalendar=*-*-* 02:30:00
   Persistent=true

   [Install]
   WantedBy=timers.target
   ```

3. Load and start the timer:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now pg-backup.timer
   ```

4. Make sure that the timer shows a time in the `NEXT` column:

   ```bash
   systemctl list-timers pg-backup.timer
   ```

5. Start the service one time. Then read the log:

   ```bash
   sudo systemctl start pg-backup.service
   sudo journalctl -u pg-backup.service -n 20 --no-pager
   ```

6. Make sure that the log shows `Backup OK`.

**NOTE:** To receive a message when a backup fails, add `OnFailure=<your-alert-unit>.service` to the `[Unit]` section of `pg-backup.service`.

## Procedure 4: Test a restore

Do this test after the first backup. Do it again at regular intervals, for example one time each month. Only a restore test shows that a backup is good.

1. Start a root shell. Only root can read the backup directory.

   ```bash
   sudo -i
   ```

2. Find the newest backup and the image of the production container:

   ```bash
   LATEST=$(ls -1t /var/backups/postgres/app_*.dump | head -n 1)
   IMAGE=$(docker inspect -f '{{.Config.Image}}' app-db)
   echo "$LATEST  $IMAGE"
   ```

3. Start a test container from the same image. The same image has the same extensions. The container has no network. Thus, no application can connect to it by mistake.

   ```bash
   docker run -d --name pg-restore-test --network none \
     -e POSTGRES_USER=app \
     -e POSTGRES_PASSWORD=restore-test \
     -e POSTGRES_DB=app \
     -v /var/backups/postgres:/backups:ro \
     "$IMAGE"
   ```

4. Wait until the server is ready:

   ```bash
   until docker exec pg-restore-test pg_isready -h 127.0.0.1 -U app -q; do sleep 1; done
   ```

   **NOTE:** Use `-h 127.0.0.1`. At the first start, the image starts a temporary server for initialization. That server accepts only socket connections. A socket test can show "ready" too early.

5. Restore the backup:

   ```bash
   docker exec pg-restore-test pg_restore -U app -d app \
     --no-owner --no-privileges --exit-on-error \
     "/backups/$(basename "$LATEST")" \
     && echo "RESTORE OK" || echo "RESTORE FAILED"
   ```

6. Make sure that the output shows `RESTORE OK`.

   **NOTE:** The test container has only the role `app`. The options `--no-owner` and `--no-privileges` prevent errors from roles that are not in the test container.

7. Write a query file that counts the rows in each table:

   ```bash
   cat > rowcount.sql <<'EOF'
   SELECT table_schema || '.' || table_name AS tbl,
          (xpath('/row/c/text()',
                 query_to_xml(format('SELECT count(*) AS c FROM %I.%I',
                                     table_schema, table_name),
                              false, true, '')))[1]::text::bigint AS n_rows
   FROM information_schema.tables
   WHERE table_type = 'BASE TABLE'
     AND table_schema NOT IN ('pg_catalog', 'information_schema')
   ORDER BY 1;
   EOF
   ```

8. Use the query on the production database and on the restored database. Then compare the results:

   ```bash
   docker exec -i app-db          psql -U app -d app -At -F ' ' < rowcount.sql > prod.txt
   docker exec -i pg-restore-test psql -U app -d app -At -F ' ' < rowcount.sql > restore.txt
   diff prod.txt restore.txt && echo "Row counts are the same"
   ```

   **CAUTION:** The query reads all rows of all tables. On a large database, do this step at a time of low load.

9. Examine the result of the comparison:
   - The two files must show the same tables.
   - The production data changes after the backup. Thus, some counts in `prod.txt` can be a little higher.
   - A table that is not in `restore.txt` is a problem. A large difference in counts is also a problem.

10. Examine the newest data. Replace `orders` and `created_at` with a table and a column from your database. The result must be near the time of the backup.

    ```bash
    docker exec pg-restore-test psql -U app -d app -c 'SELECT max(created_at) FROM orders;'
    ```

11. Remove the test container and the result files. Then close the root shell.

    ```bash
    docker rm -f pg-restore-test
    rm -f prod.txt restore.txt
    exit
    ```

## Recommendation: Copy the backups to a different location

**CAUTION:** The backups are on the same server as the database. If the server or its disk fails, you lose the database and the backups. Copy the backups each night to a different server or to object storage. For example, use `restic` or `rclone`.