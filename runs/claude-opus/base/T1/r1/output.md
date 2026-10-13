Here is a setup that uses a small script plus a systemd timer. It dumps nightly in `pg_dump` custom format (compressed, restorable with `pg_restore`), keeps 7 days of backups, and tests restores in a throwaway container.

## 1. Backup script

Create `/usr/local/bin/pg-backup-app.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

CONTAINER=app-db
DB=app
DB_USER=app
BACKUP_DIR=/var/backups/postgres
KEEP_DAYS=7

umask 077                      # dumps contain all your data: root-only
mkdir -p "$BACKUP_DIR"

FILE="$BACKUP_DIR/${DB}_$(date +%F_%H%M).dump"
trap 'rm -f "$FILE.partial"' EXIT   # a failed run leaves no half-written file

# Runs pg_dump inside the container, so the client version always matches the server (17).
# No -t flag: a TTY would corrupt the binary output.
docker exec "$CONTAINER" pg_dump -U "$DB_USER" -d "$DB" -Fc > "$FILE.partial"
mv "$FILE.partial" "$FILE"

# Prune only after a successful dump, so a broken job never deletes the good backups.
find "$BACKUP_DIR" -name "${DB}_*.dump" -mtime +$((KEEP_DAYS - 1)) -delete

echo "Backup OK: $FILE ($(du -h "$FILE" | cut -f1))"
```

```bash
sudo chmod 700 /usr/local/bin/pg-backup-app.sh
sudo /usr/local/bin/pg-backup-app.sh      # run once by hand to confirm it works
```

The official Postgres image trusts socket connections from inside the container, so no password is needed. If yours asks for one, add `-e PGPASSWORD=...` to the `docker exec`.

## 2. Nightly schedule (systemd timer)

I picked systemd over cron for two reasons: the output goes to the journal, and `Persistent=true` runs a missed backup after a reboot.

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
Description=Nightly pg_dump of app database

[Timer]
OnCalendar=*-*-* 02:30:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pg-backup-app.timer
systemctl list-timers pg-backup-app.timer        # shows the next run
sudo systemctl start pg-backup-app.service       # trigger one run now
journalctl -u pg-backup-app.service -n 20        # check the result
```

`OnCalendar` uses server local time. Check the timezone with `timedatectl`.

## 3. Test that a backup restores

Restore the latest dump into a throwaway container built from the same image as `app-db`, so any extensions are present:

```bash
LATEST=$(ls -1t /var/backups/postgres/app_*.dump | head -n1)
IMAGE=$(docker inspect -f '{{.Config.Image}}' app-db)

docker run -d --name app-db-restore-test \
  -e POSTGRES_USER=app -e POSTGRES_DB=app -e POSTGRES_PASSWORD=throwaway \
  "$IMAGE"

# Check over TCP: during init the image runs a temporary socket-only server that would fool a socket check
until docker exec app-db-restore-test pg_isready -h 127.0.0.1 -U app -d app -q; do sleep 1; done

time docker exec -i app-db-restore-test \
  pg_restore -U app -d app --exit-on-error < "$LATEST"
```

`--exit-on-error` makes any problem fail loudly. Without it, `pg_restore` keeps going and only prints "errors ignored". The `time` output tells you how long a real recovery would take.

Next, compare the restore against production:

```bash
for c in app-db app-db-restore-test; do
  echo "== $c"
  docker exec "$c" psql -U app -d app -Atc \
    "SELECT count(*) FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema');"
  docker exec "$c" psql -U app -d app -Atc "SELECT count(*) FROM users;"   # swap in your key tables
done
```

Table counts should match exactly. Row counts should be close but not equal, because production has kept changing since the dump.

Clean up (`-v` also removes the container's anonymous data volume):

```bash
docker rm -f -v app-db-restore-test
```

Run this test now, then monthly. A real restore uses the same `pg_restore` command against `app-db`, after you stop the app and drop and recreate the `app` database.

## Gaps worth closing

- **Off-site copy (biggest gap).** All 7 backups sit on the same disk as the database, so losing the server loses both. Add an `rclone` or `rsync` step to another host or to object storage.
- **Failure alerts.** Right now a failure only shows up in the journal. Add a ping to a dead-man's-switch service (healthchecks.io or similar) as the last line of the script. It alerts both when the job fails and when it silently stops running.
- **Roles.** `pg_dump` does not include roles. That is fine if `app` is the only role, since `POSTGRES_USER` recreates it. If the restore test fails on a missing role, also save `pg_dumpall -U app --globals-only` nightly.
- **7 days is short.** A bad deploy that deletes rows and goes unnoticed for 8 days is unrecoverable. A cheap fix is to also keep Sunday dumps for 4 weeks.

Hold the line, guardian of the WAL.