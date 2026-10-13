# Nightly Postgres 17 Backups for `app-db` with 7-Day Retention

This setup uses `pg_dump` inside the container, a systemd timer, and a restore test that runs against a throwaway container.

## 1. Check that you can dump from the container

```bash
docker exec app-db pg_dump -U app -d app --schema-only | head
```

If this prints SQL, you're set. The official `postgres` image trusts local socket connections inside the container, so no password is needed. If yours prompts for one, put a `.pgpass` file inside the container rather than passing `PGPASSWORD` on the command line.

> Never use `docker exec -t` for dumps. A TTY rewrites line endings and corrupts the binary output.

## 2. Create the backup script

`/usr/local/bin/pg-backup.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

CONTAINER=app-db
DB=app
DB_USER=app
BACKUP_DIR=/var/backups/postgres
RETENTION_DAYS=7

umask 077
mkdir -p "$BACKUP_DIR"

STAMP=$(date +%Y-%m-%d_%H%M%S)
FINAL="$BACKUP_DIR/${DB}_${STAMP}.dump"
TMP="$FINAL.partial"
trap 'rm -f "$TMP"' EXIT

# Custom format (-Fc): compressed, and lets pg_restore pick objects selectively
docker exec "$CONTAINER" pg_dump -U "$DB_USER" -d "$DB" -Fc > "$TMP"

# Cheap integrity check: the archive's table of contents must be readable
docker exec -i "$CONTAINER" pg_restore --list < "$TMP" > /dev/null

mv "$TMP" "$FINAL"
echo "Backup OK: $FINAL ($(du -h "$FINAL" | cut -f1))"

# Prune only after a successful backup, so repeated failures never delete good dumps
find "$BACKUP_DIR" -type f -name "${DB}_*.dump" -mtime +$((RETENTION_DAYS - 1)) -delete
find "$BACKUP_DIR" -type f -name "*.partial" -mtime +1 -delete
```

```bash
sudo chmod 750 /usr/local/bin/pg-backup.sh
```

How the design protects you:
- The dump is written to `.partial` and renamed only after it passes the check. A half-written file never looks like a valid backup.
- `set -e` stops the script before the prune step if anything fails.
- `-mtime +6` deletes files at least 7 days old. Because pruning runs after each new dump, you always keep the 7 most recent nightly backups.

## 3. Schedule it with a systemd timer

`/etc/systemd/system/pg-backup.service`:

```ini
[Unit]
Description=Nightly pg_dump of app database
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/pg-backup.sh
```

`/etc/systemd/system/pg-backup.timer`:

```ini
[Unit]
Description=Run pg-backup nightly

[Timer]
OnCalendar=*-*-* 02:30:00
RandomizedDelaySec=10m
Persistent=true

[Install]
WantedBy=timers.target
```

`Persistent=true` makes a missed run happen at the next boot if the server was off at 02:30.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pg-backup.timer
systemctl list-timers pg-backup.timer
```

If you'd rather use cron, this line does the same job:

```
30 2 * * * root /usr/local/bin/pg-backup.sh >> /var/log/pg-backup.log 2>&1
```

Put it in `/etc/cron.d/pg-backup`.

## 4. Run it once now and check the result

```bash
sudo systemctl start pg-backup.service
journalctl -u pg-backup.service -n 20 --no-pager
sudo ls -lh /var/backups/postgres/
```

## 5. Test that a backup actually restores

A dump that `pg_restore --list` can read is not proof that it restores. This script loads the dump into a throwaway container that uses **the same image as production**, so extensions like PostGIS or pgvector are available.

`/usr/local/bin/pg-restore-test.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR=/var/backups/postgres
DUMP="${1:-$(ls -1t "$BACKUP_DIR"/app_*.dump | head -n1)}"
TEST=pg-restore-test
IMAGE=$(docker inspect -f '{{.Config.Image}}' app-db)

echo "Testing restore of: $DUMP (image: $IMAGE)"

docker rm -f "$TEST" >/dev/null 2>&1 || true
trap 'docker rm -f "$TEST" >/dev/null 2>&1 || true' EXIT

# No ports published; this container is unreachable from outside
docker run -d --name "$TEST" \
  -e POSTGRES_USER=app -e POSTGRES_DB=app -e POSTGRES_PASSWORD=throwaway \
  "$IMAGE" >/dev/null

# Check over TCP: during init, the image runs a temporary socket-only server,
# so this only succeeds once the real server is up
ready=0
for _ in $(seq 60); do
  if docker exec "$TEST" pg_isready -h 127.0.0.1 -U app -d app -q; then ready=1; break; fi
  sleep 1
done
[[ $ready == 1 ]] || { echo "Test container never became ready" >&2; exit 1; }

# --no-acl skips GRANTs to roles that don't exist in the fresh container
docker exec -i "$TEST" pg_restore -U app -d app --no-acl --exit-on-error < "$DUMP"
echo "pg_restore completed without errors"

COUNT_SQL="
SELECT table_schema || '.' || table_name AS tbl,
       (xpath('/row/c/text()', query_to_xml(
          format('SELECT count(*) AS c FROM %I.%I', table_schema, table_name),
          false, true, '')))[1]::text::bigint AS row_count
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY 1;"

echo "--- Row counts in restored copy ---"
docker exec "$TEST" psql -U app -d app -c "$COUNT_SQL"

# Schema check: restored table list should match production
TABLES_SQL="SELECT table_schema||'.'||table_name FROM information_schema.tables
            WHERE table_type='BASE TABLE'
              AND table_schema NOT IN ('pg_catalog','information_schema') ORDER BY 1;"
if diff <(docker exec app-db psql -U app -d app -Atc "$TABLES_SQL") \
        <(docker exec "$TEST" psql -U app -d app -Atc "$TABLES_SQL"); then
  echo "Table list matches production"
else
  echo "Table list differs from production (expected only if a migration ran since the backup)" >&2
  exit 1
fi

# Freshness check: edit to use a table you know gets daily writes
# docker exec "$TEST" psql -U app -d app -Atc "SELECT max(created_at) FROM orders;"
```

Run it:

```bash
sudo chmod 750 /usr/local/bin/pg-restore-test.sh
sudo /usr/local/bin/pg-restore-test.sh                              # newest backup
sudo /usr/local/bin/pg-restore-test.sh /var/backups/postgres/app_X.dump  # specific file
```

A passing test means all of the following:
- `pg_restore` exits with no errors.
- The table list matches production.
- Row counts roughly match production. They won't be identical, since production has kept changing since the dump.
- Your freshness query, once you uncomment it, returns a timestamp from shortly before the backup time.

**Automate it weekly.** Copy the service and timer from step 3 as `pg-restore-test.service` and `pg-restore-test.timer`. Point `ExecStart` at the test script and use `OnCalendar=Sun *-*-* 04:00:00`. An untested backup isn't a backup.

## 6. Restoring for real (for reference)

```bash
# Stop the app containers that write to the DB first
docker exec -i app-db pg_restore -U app -d app --clean --if-exists --exit-on-error \
  < /var/backups/postgres/app_YYYY-MM-DD_HHMMSS.dump
```

## 7. Gaps you should close

- **Off-site copy.** All 7 backups currently sit on the same disk as the database, so losing the server loses both. Add a step that syncs `/var/backups/postgres` elsewhere with `restic`, `rclone`, or similar.
- **Failure alerts.** Nothing tells you if the nightly job fails. Add `OnFailure=` to the service with a notifier unit, or ping a healthcheck URL such as healthchecks.io at the end of the script.
- **Roles.** `pg_dump` doesn't include roles or passwords. If you have roles beyond `app`, also save them each night with `docker exec app-db pg_dumpall -U app --globals-only > .../globals_$STAMP.sql`. This needs superuser, which `app` is if it was created through `POSTGRES_USER`.
- **Disk space.** Keep room for about 8 dumps: the 7 kept ones plus the one being written.