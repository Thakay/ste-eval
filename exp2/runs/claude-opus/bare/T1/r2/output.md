# Nightly Postgres 17 Backups for a Docker Container (Ubuntu 24.04)

**Assumptions:**
- `app-db` runs the official `postgres:17` image.
- The `app` user was created with `POSTGRES_USER=app`, so it's the superuser.
- Local socket connections inside the container are trusted, which is the image default.
- Everything below runs as root.

The approach is to run `pg_dump` *inside* the container with `docker exec` and stream the output to the host. That way the client version always matches the server.

## 1. Create the backup directory

```bash
sudo install -d -m 700 -o root -g root /var/backups/postgres/app
```

## 2. Create the backup script

`/usr/local/bin/pg-backup-app.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

CONTAINER=app-db
DB=app
DB_USER=app
BACKUP_DIR=/var/backups/postgres/app
KEEP_DAYS=7

umask 077
ts=$(date +%Y-%m-%d_%H%M%S)
dump="$BACKUP_DIR/app_${ts}.dump"
globals="$BACKUP_DIR/globals_${ts}.sql"

# Write to .partial first so a failed run never leaves a file that looks complete
trap 'rm -f -- "$dump.partial" "$globals.partial"' EXIT

# Custom format (-Fc): compressed, and supports selective/parallel restore.
# Do NOT add -t to docker exec; a TTY corrupts binary output.
docker exec "$CONTAINER" pg_dump -U "$DB_USER" -d "$DB" -Fc > "$dump.partial"

# pg_dump doesn't include roles; capture them separately
docker exec "$CONTAINER" pg_dumpall -U "$DB_USER" --globals-only > "$globals.partial"

# Cheap integrity check: the archive's table of contents must be readable
docker exec -i "$CONTAINER" pg_restore --list < "$dump.partial" > /dev/null

mv -- "$dump.partial" "$dump"
mv -- "$globals.partial" "$globals"

# Prune only after a successful backup, so failing backups never eat your history
find "$BACKUP_DIR" -maxdepth 1 -type f \( -name 'app_*.dump' -o -name 'globals_*.sql' \) \
  -mtime +$((KEEP_DAYS - 1)) -delete

echo "Backup OK: $dump ($(du -h "$dump" | cut -f1))"
```

```bash
sudo chmod 700 /usr/local/bin/pg-backup-app.sh
```

**Notes:**
- **If `app` is not a superuser:** add `--no-role-passwords` to the `pg_dumpall` line. Otherwise it fails reading `pg_authid`.
- **If the container asks for a password:** pass it with `docker exec -e PGPASSWORD=...`. A better option is a `.pgpass` file inside the container.
- **Retention:** `-mtime +6` deletes files at least 7 full days old. With nightly runs you keep 7 (occasionally 8) backups.

## 3. Schedule it with a systemd timer

A systemd timer is preferable to cron here for two reasons. Missed runs catch up after downtime (`Persistent=true`), and output goes to the journal.

`/etc/systemd/system/pg-backup-app.service`:

```ini
[Unit]
Description=pg_dump of app database
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/pg-backup-app.sh
```

`/etc/systemd/system/pg-backup-app.timer`:

```ini
[Unit]
Description=Nightly app database backup

[Timer]
OnCalendar=*-*-* 02:30:00
Persistent=true
RandomizedDelaySec=10m

[Install]
WantedBy=timers.target
```

Enable the timer and do a first run by hand:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pg-backup-app.timer
sudo systemctl start pg-backup-app.service      # run once now
journalctl -u pg-backup-app.service -n 20       # should end with "Backup OK"
ls -lh /var/backups/postgres/app
systemctl list-timers pg-backup-app.timer       # confirm next run time
```

If you'd rather use cron, use this one-liner in `/etc/cron.d/pg-backup-app` instead:
`30 2 * * * root /usr/local/bin/pg-backup-app.sh >> /var/log/pg-backup-app.log 2>&1`

## 4. Get copies off the server, and alert on failure

- **Off-site copies:** backups on the same disk as the database won't survive disk failure, server loss, or ransomware. Sync `/var/backups/postgres/app` to another machine or to object storage, for example with `restic` or `rclone` to S3 or B2. Ideally the target is append-only or versioned.
- **Alerting:** a failed run only shows up in the journal. Add an `OnFailure=` unit that notifies you. Alternatively, add a dead-man's-switch ping (e.g. a healthchecks.io URL via `curl`) as the script's last line, so silence triggers an alert.

## 5. Test that a backup actually restores

The test restores the newest backup into a throwaway container with the same image. It then checks the result and compares row counts with production. Run it now, then schedule it weekly.

`/usr/local/bin/pg-restore-test-app.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR=/var/backups/postgres/app
TEST=app-db-restore-test
IMAGE=$(docker inspect app-db --format '{{.Config.Image}}')

dump=$(ls -1t "$BACKUP_DIR"/app_*.dump | head -n1)
globals=$(ls -1t "$BACKUP_DIR"/globals_*.sql | head -n1)
echo "Testing restore of $dump using $IMAGE"

trap 'docker rm -f "$TEST" >/dev/null 2>&1 || true' EXIT

# No published ports; the test DB is reachable only via docker exec
docker run -d --name "$TEST" \
  -e POSTGRES_USER=app -e POSTGRES_DB=app -e POSTGRES_PASSWORD=throwaway \
  "$IMAGE" >/dev/null

# Wait on TCP: the image's init-phase server only listens on the socket,
# so a socket check can succeed before the real server is up
for _ in $(seq 60); do
  docker exec "$TEST" pg_isready -h 127.0.0.1 -U app >/dev/null 2>&1 && break
  sleep 2
done
docker exec "$TEST" pg_isready -h 127.0.0.1 -U app

# Roles first ("role app already exists" is expected and harmless)
docker exec -i "$TEST" psql -U app -d postgres -q < "$globals" > /dev/null

# The real test: any error fails the script
docker exec -i "$TEST" pg_restore -U app -d app --exit-on-error < "$dump"

COUNTS_SQL="select table_schema||'.'||table_name,
  (xpath('/row/c/text()', query_to_xml(format('select count(*) as c from %I.%I',
    table_schema, table_name), false, true, '')))[1]::text
  from information_schema.tables
  where table_type='BASE TABLE' and table_schema not in ('pg_catalog','information_schema')
  order by 1"

tables=$(docker exec "$TEST" psql -U app -d app -At -c \
  "select count(*) from information_schema.tables
   where table_type='BASE TABLE' and table_schema not in ('pg_catalog','information_schema')")
[ "$tables" -gt 0 ] || { echo "FAIL: restored database has no tables"; exit 1; }

echo "Row count differences vs. production (small drift on busy tables is expected):"
diff <(docker exec app-db "psql" -U app -d app -At -c "$COUNTS_SQL") \
     <(docker exec "$TEST" psql -U app -d app -At -c "$COUNTS_SQL") || true

echo "RESTORE TEST PASSED: $tables tables restored from $(basename "$dump")"
```

```bash
sudo chmod 700 /usr/local/bin/pg-restore-test-app.sh
sudo /usr/local/bin/pg-restore-test-app.sh
```

**What counts as a pass:**
- `pg_restore` completes with no errors.
- The tables exist.
- Row counts match production, apart from rows written since the dump.

Also add a query or two that your app depends on, for example the latest row in your main table. A restore that "succeeds" but has an empty critical table is still a failure.

Two caveats:
- The exact `count(*)` comparison scans every table in production. On a large database, restrict it to a few key tables or run it off-peak.
- Run the test on a host with enough free disk for a second copy of the database.

To run the test weekly, create `pg-restore-test-app.service` and `.timer` the same way as in step 3. Use `ExecStart=/usr/local/bin/pg-restore-test-app.sh` and `OnCalendar=Sun *-*-* 04:00:00`, then `systemctl enable --now pg-restore-test-app.timer`. Hook its failures into the same alerting as the backup.

## 6. Restoring for real (when you need it)

1. Stop the application so nothing writes during the restore.
2. Restore into a fresh database, then swap names. This keeps the broken database around until you've verified the new one:

```bash
docker exec app-db createdb -U app app_restored
docker exec -i app-db pg_restore -U app -d app_restored --exit-on-error \
  < /var/backups/postgres/app/app_YYYY-MM-DD_HHMMSS.dump
docker exec app-db psql -U app -d postgres -c "ALTER DATABASE app RENAME TO app_broken"
docker exec app-db psql -U app -d postgres -c "ALTER DATABASE app_restored RENAME TO app"
```

3. If you're rebuilding on a new server, restore the `globals_*.sql` file first, as the test script does.