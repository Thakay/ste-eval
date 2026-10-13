**Answer:** a small script runs `pg_dump` inside `app-db` every night from root's cron. It keeps the newest 7 dumps on the host. A second script restores the newest dump into a throwaway container once a week and checks it. One gap matters more than the rest: these backups sit on the same server as the database, so add an offsite copy (see the end).

## 1. Backup script

Save as `/usr/local/bin/pg-backup-app.sh`:

```bash
#!/usr/bin/env bash
# Nightly logical backup of the "app" database from the app-db container.
set -euo pipefail
umask 077

BACKUP_DIR=/var/backups/postgres/app
KEEP=7
FILE="$BACKUP_DIR/app_$(date +%F_%H%M).dump"

mkdir -p "$BACKUP_DIR"
trap 'rm -f "$FILE.partial"' EXIT

# Run pg_dump inside the container so its version matches the server (17).
# Write to .partial first so a failed run never looks like a good backup.
docker exec app-db pg_dump -U app -d app -Fc > "$FILE.partial"

# Cheap integrity check: the archive's table of contents must be readable.
docker exec -i app-db pg_restore --list < "$FILE.partial" > /dev/null

mv "$FILE.partial" "$FILE"

# Keep the newest $KEEP dumps. Only reached if everything above succeeded.
ls -1 "$BACKUP_DIR"/app_*.dump | sort | head -n -"$KEEP" | xargs -r rm --

echo "$(date -Is) backup ok: $FILE ($(du -h "$FILE" | cut -f1))"
```

Notes:
- `-Fc` (custom format) is compressed and lets you restore single tables later.
- Never add `-t` to `docker exec` here. A TTY corrupts binary output.
- No password is needed: the official Postgres image trusts local socket connections inside the container. If you changed `pg_hba.conf`, add `-e PGPASSWORD=...` to the `docker exec` calls.
- Retention counts files instead of age. If some nights fail, you still keep 7 good copies instead of fewer.

## 2. Restore test script

Save as `/usr/local/bin/pg-restore-test-app.sh`:

```bash
#!/usr/bin/env bash
# Restores the newest dump into a throwaway container and checks it.
set -euo pipefail

BACKUP_DIR=/var/backups/postgres/app
TEST=app-db-restoretest
IMAGE=$(docker inspect -f '{{.Config.Image}}' app-db)   # same image, same extensions
LATEST=$(ls -1 "$BACKUP_DIR"/app_*.dump | sort | tail -n 1)

trap 'docker rm -fv "$TEST" >/dev/null 2>&1 || true' EXIT

docker run -d --name "$TEST" \
  -e POSTGRES_USER=app -e POSTGRES_DB=app -e POSTGRES_PASSWORD=restoretest \
  "$IMAGE" > /dev/null

# Wait on TCP: the temporary server used during first-time init only listens on the socket.
timeout 120 bash -c "until docker exec $TEST pg_isready -h 127.0.0.1 -U app -q; do sleep 2; done"

docker exec -i "$TEST" pg_restore -U app -d app --exit-on-error < "$LATEST"

q="select count(*) from information_schema.tables where table_schema not in ('pg_catalog','information_schema')"
want=$(docker exec app-db psql -U app -d app -Atc "$q")
got=$(docker exec "$TEST" psql -U app -d app -Atc "$q")
[ "$got" = "$want" ] || { echo "$(date -Is) restore test FAIL: $got tables restored, live db has $want"; exit 1; }
# Add a row-count check on a table you care about, e.g. users or orders.

echo "$(date -Is) restore test ok: $LATEST ($got tables)"
```

Notes:
- It never touches the live database. It only reads the table count from it.
- If your schema has roles other than `app`, the restore fails on GRANT/OWNER lines. Either add `--no-owner --no-privileges` or create those roles in the test container first.
- A table-count mismatch right after a deploy that added tables is expected. Re-run the test after the next nightly dump.

## 3. Install and run once by hand

```bash
sudo chmod 700 /usr/local/bin/pg-backup-app.sh /usr/local/bin/pg-restore-test-app.sh
sudo /usr/local/bin/pg-backup-app.sh
sudo ls -lh /var/backups/postgres/app
sudo /usr/local/bin/pg-restore-test-app.sh
```

Check that the dump size looks plausible and that the restore test prints `ok`. Also check free disk space: you need room for about 8 dumps (7 kept plus the one being written).

## 4. Schedule

Create `/etc/cron.d/pg-backup-app` (owned by root, mode 644, must end with a newline):

```
30 2 * * * root /usr/local/bin/pg-backup-app.sh >> /var/log/pg-backup-app.log 2>&1
0 4 * * 0  root /usr/local/bin/pg-restore-test-app.sh >> /var/log/pg-backup-app.log 2>&1
```

This runs the backup nightly at 02:30 and the restore test Sundays at 04:00, in server local time (check with `timedatectl`). The restore test uses CPU and disk, so keep it off-peak.

## 5. Real restore (when you need it)

**Warning: this overwrites the live `app` database.** Stop the app first, and make a fresh dump of the current state if it might still be useful.

```bash
docker exec -i app-db pg_restore -U app -d app --clean --if-exists --exit-on-error \
  < /var/backups/postgres/app/app_2026-10-11_0230.dump
```

## Gaps worth closing

- **Offsite copy (most important).** If the disk or server dies, the backups die with it. After the `mv` line, push the dump to another machine or to object storage (for example `rclone copy "$FILE" remote:app-backups`). Give that copy its own retention.
- **Failure alerts.** Cron fails silently. Add a ping to a dead-man's switch service (such as healthchecks.io) as the last line of each script. It alerts you when a ping does not arrive.
- **7 days may be short.** Bad data or a broken migration is often noticed after a week. Keeping one weekly dump for 4 weeks is cheap insurance.
- **Data-loss window.** Nightly dumps mean you can lose up to about 24 hours of data. If that is not acceptable, look at continuous WAL archiving (pgBackRest or WAL-G), but only if you need it.

Walls raised, sentries posted. March on, Centurion.