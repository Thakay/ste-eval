# Nightly Postgres 17 Backups for `app-db` (Docker, Ubuntu 24.04)

The script runs `pg_dump` **inside** the container, so the client version always matches the server (17). It writes a compressed custom-format dump to the host and deletes dumps older than 7 days. A systemd timer runs it every night.

> **Assumption:** `app-db` uses the official `postgres:17` image, which trusts local socket connections inside the container. That means `docker exec app-db pg_dump -U app app` needs no password. If yours prompts for one, see the note at the end.

---

## 1. Create the backup directory

```bash
sudo install -d -m 700 -o root -g root /var/backups/postgres
```

## 2. Create the backup script

`/usr/local/bin/pg-backup-app.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

CONTAINER=app-db
DB=app
DB_USER=app
BACKUP_DIR=/var/backups/postgres
RETENTION_DAYS=7

umask 077
TS=$(date +%Y-%m-%d_%H%M%S)
OUT="$BACKUP_DIR/${DB}_${TS}.dump"
TMP="$OUT.partial"
trap 'rm -f "$TMP"' EXIT

# Custom format (-Fc): compressed, and restorable with pg_restore.
# Do NOT use `docker exec -t`: a TTY corrupts binary output.
docker exec "$CONTAINER" pg_dump -U "$DB_USER" -d "$DB" -Fc > "$TMP"

# Sanity checks: file is non-empty and its table of contents is readable
[ -s "$TMP" ]
docker exec -i "$CONTAINER" pg_restore --list < "$TMP" > /dev/null

mv "$TMP" "$OUT"
echo "Backup OK: $OUT ($(du -h "$OUT" | cut -f1))"

# Retention: only reached if the backup above succeeded, so a run of
# failures never deletes your last good backups.
find "$BACKUP_DIR" -type f -name "${DB}_*.dump" -mtime +$((RETENTION_DAYS - 1)) -delete
```

```bash
sudo chmod 700 /usr/local/bin/pg-backup-app.sh
sudo /usr/local/bin/pg-backup-app.sh        # run it once by hand
ls -lh /var/backups/postgres
```

Some details about how it behaves:
- It writes to a `.partial` file and renames it only on success, so a half-written dump never looks like a good backup.
- `-mtime +6` deletes files that are 7 or more days old. You'll normally have 7 (occasionally 8) dumps on disk.

## 3. Schedule it with a systemd timer

`/etc/systemd/system/pg-backup-app.service`:

```ini
[Unit]
Description=Nightly pg_dump of the app database
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/pg-backup-app.sh
```

`/etc/systemd/system/pg-backup-app.timer`:

```ini
[Unit]
Description=Run app database backup nightly

[Timer]
OnCalendar=*-*-* 02:30:00
RandomizedDelaySec=10m
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pg-backup-app.timer
systemctl list-timers pg-backup-app.timer      # shows next run time
sudo systemctl start pg-backup-app.service     # test the service path now
journalctl -u pg-backup-app.service -n 20      # check the log
```

Notes:
- `OnCalendar` uses the server's local timezone. Check it with `timedatectl`; Ubuntu servers are often set to UTC.
- `Persistent=true` makes a missed run happen at the next boot.
- If you prefer cron instead, put this in `/etc/cron.d/pg-backup-app`:
  ```
  30 2 * * * root /usr/local/bin/pg-backup-app.sh >> /var/log/pg-backup-app.log 2>&1
  ```

## 4. Test that a backup actually restores

The test restores the newest dump into a throwaway container that uses the **same image as production**, so any extensions such as PostGIS are present. It then runs sanity checks and deletes the container. Production is never touched.

`/usr/local/bin/pg-restore-test.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR=/var/backups/postgres
DUMP=${1:-$(ls -1t "$BACKUP_DIR"/app_*.dump | head -n1)}
IMAGE=$(docker inspect -f '{{.Config.Image}}' app-db)
TEST=pg-restore-test

trap 'docker rm -f "$TEST" >/dev/null 2>&1 || true' EXIT

echo "Restoring $DUMP into a throwaway $IMAGE container..."
docker run -d --name "$TEST" -e POSTGRES_PASSWORD=throwaway "$IMAGE" >/dev/null

# Probe over TCP: the image's init-time temporary server listens only on the
# socket, so this waits for the real server instead of the temporary one.
until docker exec "$TEST" pg_isready -h 127.0.0.1 -U postgres -q; do sleep 1; done

docker exec "$TEST" createuser -U postgres app
docker exec "$TEST" createdb -U postgres -O app app
docker exec -i "$TEST" pg_restore -U postgres -d app --exit-on-error < "$DUMP"

docker exec "$TEST" psql -U postgres -d app -v ON_ERROR_STOP=1 -c "
  SELECT count(*) AS tables
  FROM information_schema.tables
  WHERE table_type = 'BASE TABLE'
    AND table_schema NOT IN ('pg_catalog', 'information_schema');"

echo "RESTORE TEST PASSED: $DUMP"
```

```bash
sudo chmod 700 /usr/local/bin/pg-restore-test.sh
sudo /usr/local/bin/pg-restore-test.sh                                   # newest dump
sudo /usr/local/bin/pg-restore-test.sh /var/backups/postgres/app_....dump # a specific one
```

**What "passed" means:** `pg_restore --exit-on-error` completed with no errors, and the table count is what you expect.

**Stronger check: compare row counts with production.** Remove the `trap` line temporarily so the test container stays up, then run this query on both databases and diff the output:

```sql
SELECT table_schema, table_name,
       (xpath('/row/c/text()',
          query_to_xml(format('SELECT count(*) AS c FROM %I.%I', table_schema, table_name),
                       false, true, '')))[1]::text::bigint AS row_count
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY 1, 2;
```

```bash
docker exec -i app-db          psql -U app      -d app -At < counts.sql > prod.txt
docker exec -i pg-restore-test psql -U postgres -d app -At < counts.sql > restored.txt
diff prod.txt restored.txt
docker rm -f pg-restore-test
```

Small differences on busy tables are expected because production has changed since the dump. Big gaps or missing tables are not. Exact counts scan every table, so run this off-peak on large databases. A quick extra check is the newest timestamp in a key table (e.g. `SELECT max(created_at) FROM orders;`), which should be close to the backup time.

**Run the restore test regularly**, not just once. You can reuse the systemd pattern above with a second service and timer pair, e.g. `OnCalendar=Sun 04:00`.

If `pg_restore` fails with `role "xyz" does not exist`, your database grants to roles other than `app`. Create those roles in the test container before restoring, and see the roles note below.

---

## Important notes

- **Get a copy off the server.** Backups on the same disk don't survive disk loss, server compromise, or accidental deletion of the VM. Sync `/var/backups/postgres` nightly to another machine or object storage with `rsync` or `rclone`, ideally with versioning or immutability enabled.
- **Alert on failure.** A silent failure is the usual way backups die. Two options:
  - Add `OnFailure=` to the service pointing at a notification unit.
  - Add `curl -fsS https://hc-ping.com/<uuid>` (healthchecks.io or similar) as the last line of the script. You'll be alerted when the ping *doesn't* arrive.
- **Roles and passwords aren't in `pg_dump`.** If you need to rebuild roles, also dump them:
  ```bash
  docker exec app-db pg_dumpall -U app --globals-only > "$BACKUP_DIR/globals_${TS}.sql"
  ```
  This requires `app` to be a superuser, which it is if the container was created with `POSTGRES_USER=app`.
- **If pg_dump asks for a password**, pass it through without putting it on the command line:
  ```bash
  docker exec -e PGPASSWORD app-db pg_dump ...
  ```
  Here `PGPASSWORD` is exported in the script from a root-only file.
- **Check disk space.** 7 dumps plus one in progress need roughly 8× the compressed dump size.
- **Real restore into production** (destructive, so stop the app first):
  ```bash
  docker exec -i app-db pg_restore -U app -d app --clean --if-exists --exit-on-error < /var/backups/postgres/app_<timestamp>.dump
  ```