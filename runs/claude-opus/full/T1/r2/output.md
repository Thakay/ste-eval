**Result:** two scripts and one cron file do the job.
- `pg-backup.sh` runs `pg_dump` inside `app-db` each night. It deletes dumps that are 7 or more days old.
- `pg-restore-test.sh` restores the newest dump into a temporary container. Then it compares row counts with the live database.

**Assumptions:**
- Docker runs on the host. The dumps go to `/var/backups/postgres` on the host.
- The scripts run as root.
- `app-db` uses the official `postgres:17` image, or an image built on it. In that image, local socket connections inside the container need no password.

## 1. Create the backup folder

```bash
sudo install -d -m 700 /var/backups/postgres
```

Mode 700 lets only root read the dumps. The dumps contain all your data.

## 2. Create the backup script

Save this as `/usr/local/bin/pg-backup.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
umask 077

CONTAINER=app-db
DB=app
DB_USER=app
BACKUP_DIR=/var/backups/postgres
KEEP_DAYS=7

FILE="$BACKUP_DIR/${DB}_$(date +%F_%H%M%S).dump"
TMP="$FILE.part"
trap 'rm -f "$TMP"' EXIT

# Custom format (-Fc): compressed, restore with pg_restore.
# No -t on docker exec: a TTY damages binary output.
docker exec "$CONTAINER" pg_dump -U "$DB_USER" -d "$DB" -Fc > "$TMP"
mv "$TMP" "$FILE"

# Delete dumps that are KEEP_DAYS or more days old.
find "$BACKUP_DIR" -name "${DB}_*.dump" -mtime +$((KEEP_DAYS - 1)) -delete

echo "$(date -Is) OK $FILE $(du -h "$FILE" | cut -f1)"
```

```bash
sudo chmod 700 /usr/local/bin/pg-backup.sh
```

How the script works:
- `pg_dump` runs inside the container. Thus the `pg_dump` version always matches the server version (17).
- The script writes to a `.part` file first. A failed dump never gets the final `.dump` name.
- The delete step runs only after a good dump. If backups fail for a week, the old dumps stay.

## 3. Run the script once by hand

```bash
sudo /usr/local/bin/pg-backup.sh
ls -lh /var/backups/postgres
```

If `pg_dump` asks for a password, the container does not trust local connections. In that case, add `-e PGPASSWORD=...` to the `docker exec` command.

## 4. Schedule the backup each night

Create `/etc/cron.d/pg-backup`:

```
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin
30 2 * * * root /usr/local/bin/pg-backup.sh >> /var/log/pg-backup.log 2>&1
```

- The job runs at 02:30 server time.
- Cron ignores files in `/etc/cron.d` that have a dot in the name.
- The file must end with a newline.

On the next morning, read the log:

```bash
tail /var/log/pg-backup.log
```

## 5. Test a restore

Save this as `/usr/local/bin/pg-restore-test.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR=/var/backups/postgres
LIVE=app-db
TEST=pg-restore-test
IMAGE=$(docker inspect -f '{{.Config.Image}}' "$LIVE")
LATEST=$(ls -1t "$BACKUP_DIR"/app_*.dump | head -n 1)

echo "Testing $LATEST with image $IMAGE"

trap 'docker rm -f "$TEST" > /dev/null 2>&1 || true' EXIT

docker run -d --name "$TEST" \
  -e POSTGRES_USER=app -e POSTGRES_PASSWORD=restore-test -e POSTGRES_DB=app \
  "$IMAGE" > /dev/null

# Wait for the final server. The init server does not listen on TCP.
timeout 120 bash -c "until docker exec $TEST pg_isready -h 127.0.0.1 -q; do sleep 1; done"

docker exec -i "$TEST" pg_restore -U app -d app --exit-on-error < "$LATEST"
echo "Restore OK"

# Exact row count per table. This reads every row.
COUNTS="SELECT table_schema || '.' || table_name,
  (xpath('/row/c/text()', query_to_xml(format('SELECT count(*) AS c FROM %I.%I', table_schema, table_name), false, true, '')))[1]::text
FROM information_schema.tables
WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY 1;"

if diff <(docker exec "$LIVE" psql -U app -d app -tAc "$COUNTS") \
        <(docker exec "$TEST" psql -U app -d app -tAc "$COUNTS"); then
  echo "Row counts match"
else
  echo "Row counts differ (< live, > restored)"
fi
```

```bash
sudo chmod 700 /usr/local/bin/pg-restore-test.sh
sudo /usr/local/bin/pg-restore-test.sh
```

The script does these steps:
1. It finds the newest dump.
2. It starts a temporary container from the same image as `app-db`. The same image gives the same extensions.
3. It restores the dump with `--exit-on-error`. Any error stops the test.
4. It compares the row count of each table with the live database.
5. It removes the temporary container, also when a step fails.

How to read the result:
- `Restore OK` and `Row counts match`: the backup is good.
- Small differences on busy tables are normal. The live tables got new rows after the backup ran.
- Missing tables or large differences: the test failed.
- `role "x" does not exist`: the live server has more roles than `app`. See the suggestions below.

On very large tables, the count query is slow and loads the live server. In that case, count only a few key tables.

To run the test each Sunday at 04:00, add this line to `/etc/cron.d/pg-backup`:

```
0 4 * * 0 root /usr/local/bin/pg-restore-test.sh >> /var/log/pg-restore-test.log 2>&1
```

## Real restore (disaster only)

**Warning:** this command replaces the data in the live `app` database. Stop the app first. Run the restore test on the same file first.

```bash
docker exec -i app-db pg_restore -U app -d app --clean --if-exists --single-transaction \
  < /var/backups/postgres/app_YYYY-MM-DD_HHMMSS.dump
```

`--single-transaction` makes the restore all or nothing. If one step fails, Postgres keeps the old data.

## Suggestions

- **Copy the dumps to a second location.** Dumps on the same disk do not survive a disk failure or a lost server. Copy `/var/backups/postgres` each night to another machine or to object storage, for example with `rclone` or `restic`.
- **Get an alert when a backup fails.** A failed cron job makes no noise. Add a ping to a monitor such as healthchecks.io at the end of `pg-backup.sh`. The monitor alerts you when the ping does not arrive.
- **Save the roles if you have more than `app`.** `pg_dump` saves one database, not the roles. Save the roles with `pg_dumpall --globals-only`.

Stand your watch, Vault Warden. Each night, a new shield.