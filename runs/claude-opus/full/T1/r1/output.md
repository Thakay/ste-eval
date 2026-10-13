**TL;DR:** A root cron job runs a script at 02:30 each night. The script runs `pg_dump` inside `app-db`, writes one compressed file, and deletes files older than 7 days. Each month, restore the newest file into a temporary container to check that it works.

## 1. Make the backup folder

```bash
sudo mkdir -p /var/backups/postgres
sudo chmod 700 /var/backups/postgres
```

The backup files contain all the data in the database. Only root can read this folder.

## 2. Write the backup script

Create `/usr/local/bin/pg-backup.sh`:

```bash
#!/usr/bin/env bash
# Nightly dump of the "app" database in the app-db container.
set -euo pipefail
umask 077

BACKUP_DIR=/var/backups/postgres
CONTAINER=app-db
DB=app
DB_USER=app
KEEP_DAYS=7

FILE="$BACKUP_DIR/${DB}_$(date +%F_%H%M).dump"
trap 'rm -f "$FILE.tmp"' EXIT

# Write to a temp name first. A failed dump never gets the final name.
docker exec "$CONTAINER" pg_dump -U "$DB_USER" -d "$DB" -Fc > "$FILE.tmp"
mv "$FILE.tmp" "$FILE"

# Delete old dumps. This line runs only after a good dump.
find "$BACKUP_DIR" -name "${DB}_*.dump" -mtime +"$((KEEP_DAYS - 1))" -delete

echo "$(date -Is) OK $FILE"
```

Make the script executable:

```bash
sudo chmod 700 /usr/local/bin/pg-backup.sh
```

What the script does:

- `-Fc` writes the custom format. This format is compressed, and `pg_restore` can read it.
- The script does not use `docker exec -t`. A TTY changes the binary output and breaks the file.
- If `pg_dump` fails, the script stops. It does not delete old files, so your last good backups stay.
- `-mtime +6` deletes files that are 7 or more days old. You keep about 7 nightly files.
- `pg_dump` connects through the socket inside the container. The official `postgres` image trusts socket connections by default, so it needs no password. If your container asks for a password, add `-e PGPASSWORD=...` to the `docker exec` line.

## 3. Run the script once by hand

```bash
sudo /usr/local/bin/pg-backup.sh
sudo ls -lh /var/backups/postgres
```

Check that a new `app_<date>_<time>.dump` file exists. Check that its size is more than zero.

## 4. Schedule the script each night

Create `/etc/cron.d/pg-backup` with this line:

```
30 2 * * * root /usr/local/bin/pg-backup.sh >> /var/log/pg-backup.log 2>&1
```

- The job runs at 02:30 in the server time zone. Run `timedatectl` to see the time zone.
- Do not put a dot in the file name. Cron ignores files in `/etc/cron.d` that have a dot in the name.
- The file must end with a newline.
- The job writes one `OK` line per good run, and all errors, to `/var/log/pg-backup.log`.

## 5. Test a restore

Do this test now. Then do it again each month. A backup that you never restored is not a known good backup.

Run all commands as root, because only root can read the backup folder:

```bash
sudo -i

# Use the same image as production, so the Postgres version and extensions match.
IMAGE=$(docker inspect -f '{{.Config.Image}}' app-db)
LATEST=$(ls -t /var/backups/postgres/app_*.dump | head -n 1)
echo "Testing $LATEST"

# Start a temporary server. It publishes no port.
docker run -d --name restore-test \
  -e POSTGRES_USER=app -e POSTGRES_PASSWORD=test -e POSTGRES_DB=app \
  "$IMAGE"

# Wait for the real server. During init, the image listens only on the socket.
until docker exec restore-test pg_isready -h 127.0.0.1 -U app; do sleep 1; done

# Restore. Stop at the first error. Skip owners and grants, so a missing role does not stop the test.
docker exec -i restore-test pg_restore -U app -d app \
  --no-owner --no-acl --exit-on-error < "$LATEST"
echo "pg_restore exit code: $?"
```

Compare the restored data with production:

```bash
docker exec restore-test psql -U app -d app -c '\dt+'
docker exec app-db       psql -U app -d app -c '\dt+'

docker exec restore-test psql -U app -d app -c 'SELECT count(*) FROM your_main_table;'
docker exec app-db       psql -U app -d app -c 'SELECT count(*) FROM your_main_table;'
```

The restore passes when these three conditions are true:

1. The `pg_restore` exit code is 0.
2. The table list in the test container matches the table list in production.
3. The row counts are near the production counts. Production received new rows after the backup, so its counts can be a little higher.

Delete the test container and its data volume:

```bash
docker rm -f -v restore-test
exit
```

## Gaps to close

1. **No off-site copy.** This is the largest gap. If the server disk fails, you lose the database and all 7 backups at the same time. Copy each file to a second location, for example with `restic` or `rclone` to object storage. Add the copy as the last step of the script.
2. **No failure alert.** You see a failure only if you read the log. Add a ping to a dead-man's-switch service, such as healthchecks.io, at the end of the script. The service alerts you when a ping does not arrive.
3. **No roles in the dump.** `pg_dump` does not save roles. For a full rebuild on a new server, also save roles each night with `pg_dumpall --globals-only`.

Your vault is sealed and the night watch is posted. Hold the gate, Warden of the Dumps.