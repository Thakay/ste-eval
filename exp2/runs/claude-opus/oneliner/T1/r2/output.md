# Nightly backup of the `app` database

## 1. Make the backup directory

Make a directory that only root can read:

```bash
sudo install -d -m 700 -o root -g root /var/backups/postgres
```

## 2. Write the backup script

Write this script to `/usr/local/bin/pg-backup-app.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
umask 077

CONTAINER=app-db
DB=app
DB_USER=app
BACKUP_DIR=/var/backups/postgres
KEEP_DAYS=7

FILE="$BACKUP_DIR/${DB}_$(date +%Y-%m-%d_%H%M%S).dump"
trap 'rm -f "$FILE.partial"' EXIT

# Do not use "docker exec -t". It changes the binary data.
docker exec "$CONTAINER" pg_dump -U "$DB_USER" -d "$DB" -Fc > "$FILE.partial"

# Read all of the file. Stop if the file has damage.
docker exec -i "$CONTAINER" pg_restore -f /dev/null < "$FILE.partial"

mv "$FILE.partial" "$FILE"

find "$BACKUP_DIR" -maxdepth 1 -type f -name "${DB}_*.dump" \
  -mtime +$((KEEP_DAYS - 1)) -delete

echo "Backup complete: $FILE ($(du -h "$FILE" | cut -f1))"
```

Set the permissions:

```bash
sudo chmod 700 /usr/local/bin/pg-backup-app.sh
```

How the script operates:

- `pg_dump` operates in the container. Thus, the `pg_dump` version is the same as the server version (17).
- `-Fc` makes a compressed file in the custom format. You must use `pg_restore` to restore this format.
- The script writes to a `.partial` file first. A dump that is not complete never gets the `.dump` name.
- `pg_restore -f /dev/null` reads all of the data. If the file has damage, the script stops with an error.
- `-mtime +6` removes files that are 7 days old or more. Thus, approximately 7 backups stay in the directory.

**Note:** The official `postgres` image does not ask for a password on the local socket. If your container asks for a password, add `-e PGPASSWORD` to the two `docker exec` commands. Then put `PGPASSWORD=...` in a root-only file. Add `EnvironmentFile=` with that file to the service in step 4.

**Note:** `pg_dump` does not copy roles or role passwords. If you have roles other than `app`, also keep a copy of the roles. Add this line to the script:

```bash
docker exec "$CONTAINER" pg_dumpall -U "$DB_USER" --globals-only > "$BACKUP_DIR/globals.sql"
```

This command operates only if `app` is a superuser. In the official image, the `POSTGRES_USER` role is a superuser.

## 3. Do a test of the script

```bash
sudo /usr/local/bin/pg-backup-app.sh
sudo ls -lh /var/backups/postgres
```

Make sure that the script shows `Backup complete`. Make sure that the file is not empty.

## 4. Make a systemd timer

On Ubuntu 24.04, a systemd timer is better than cron. The timer writes the output to the journal. If the server is off at the start time, the timer starts the backup when the server starts again.

Write `/etc/systemd/system/pg-backup-app.service`:

```ini
[Unit]
Description=Backup of Postgres database app
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/pg-backup-app.sh
```

Write `/etc/systemd/system/pg-backup-app.timer`:

```ini
[Unit]
Description=Start pg-backup-app each night

[Timer]
OnCalendar=*-*-* 02:30:00
Persistent=true

[Install]
WantedBy=timers.target
```

Load the units and start the timer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pg-backup-app.timer
systemctl list-timers pg-backup-app.timer
```

Make sure that the timer shows the next start time.

**Note:** `OnCalendar` uses the time zone of the server. To see the time zone, type `timedatectl`.

Start the service one time. Then examine the result:

```bash
sudo systemctl start pg-backup-app.service
systemctl status pg-backup-app.service
journalctl -u pg-backup-app.service -n 20
```

To get an alert when a backup has an error, add `OnFailure=` to the service. You can also use an external monitor.

## 5. Copy the backups to a different location

Backups on the same disk are not safe. If the server or the disk has damage, the backups are also not available. Copy the dump files to a different server or to object storage each day. For example, add an `rsync` or `rclone` command to the end of the script.

## 6. Do a test of a restore

A backup is good only if you can restore it. Do this test at regular intervals, for example one time each month. Also do the test after you change the script or the Postgres version.

**CAUTION:** Do not restore the test into `app-db`. The restore can change production data. Always use a temporary container.

Do these steps as root (`sudo -i`). Only root can read the backup directory.

**1. Find the image of `app-db` and the newest dump file:**

```bash
IMAGE=$(docker inspect --format '{{.Config.Image}}' app-db)
LATEST=$(ls -1t /var/backups/postgres/app_*.dump | head -n 1)
echo "$IMAGE  $LATEST"
```

Use the same image as `app-db`. Then the same extensions (for example, PostGIS) are available.

**2. Start a temporary container:**

```bash
docker run -d --name app-db-restoretest \
  -e POSTGRES_USER=app -e POSTGRES_DB=app -e POSTGRES_PASSWORD=restoretest \
  "$IMAGE"
```

This container has no published port. Thus, it is not available from the network.

**3. Wait until the server accepts connections:**

```bash
until docker exec app-db-restoretest pg_isready -h 127.0.0.1 -U app -d app; do sleep 2; done
```

**Note:** Use `-h 127.0.0.1`. During the first start, the image starts a temporary server without TCP. With `-h 127.0.0.1`, the command waits for the real server.

**4. Restore the dump:**

```bash
docker exec -i app-db-restoretest \
  pg_restore -U app -d app --no-owner --no-privileges \
  --exit-on-error --single-transaction < "$LATEST"
echo "pg_restore exit code: $?"
```

Make sure that the exit code is `0`. `--exit-on-error` and `--single-transaction` stop the restore at the first error. `--no-owner` and `--no-privileges` prevent errors from roles that are not in the test container.

**5. Compare the tables and the row counts with production:**

```bash
QUERY="SELECT table_schema || '.' || table_name || ' ' ||
  (xpath('/row/c/text()', query_to_xml(format('SELECT count(*) AS c FROM %I.%I',
    table_schema, table_name), false, true, '')))[1]::text
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
  AND table_type = 'BASE TABLE'
ORDER BY 1;"

docker exec app-db             psql -U app -d app -Atc "$QUERY" > /tmp/counts-prod.txt
docker exec app-db-restoretest psql -U app -d app -Atc "$QUERY" > /tmp/counts-restore.txt
diff /tmp/counts-prod.txt /tmp/counts-restore.txt
```

Data can change after the backup. Thus, small differences in active tables are usual. If a table is not in the restored database, the backup is not satisfactory. If a table is empty only in the restored database, the backup is also not satisfactory.

**CAUTION:** This query counts all rows. On large tables, it can put a high load on production. Do it when the load is low.

**6. Do a query that your application uses.** For example, find the newest row in an important table:

```bash
docker exec app-db-restoretest psql -U app -d app -c "SELECT max(created_at) FROM orders;"
```

Replace `orders` and `created_at` with a table and a column from your database. Make sure that the time is near the time of the backup.

**7. Remove the test container and its volume:**

```bash
docker rm -f -v app-db-restoretest
```

**Optional:** Put steps 1 to 7 in a script. Start the script from a second timer each week. Then the restore test also occurs automatically.