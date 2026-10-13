The setup has three parts: a dump script, a systemd timer that runs it at 02:30 each night, and a restore test in a separate container.

## 1. Create the backup folder

```bash
sudo install -d -m 700 -o root -g root /var/backups/postgres
```

Only root can read this folder. The dumps contain all your data.

## 2. Create the backup script

Create `/usr/local/bin/pg-backup-app.sh` with this content:

```bash
#!/usr/bin/env bash
set -euo pipefail
umask 077

BACKUP_DIR=/var/backups/postgres
FILE="$BACKUP_DIR/app_$(date +%F_%H%M).dump"

# If the dump fails, remove the partial file so it never looks like a good dump.
trap 'rm -f "$FILE.partial"' EXIT

docker exec app-db pg_dump -U app -d app -Fc > "$FILE.partial"
mv "$FILE.partial" "$FILE"

# This line runs only after a good dump, so a failed run never deletes old dumps.
find "$BACKUP_DIR" -name 'app_*.dump' -mtime +6 -delete
```

Make the script executable:

```bash
sudo chmod 700 /usr/local/bin/pg-backup-app.sh
```

- `-Fc` writes the compressed custom format. `pg_restore` reads this format.
- Do not add `-t` or `-it` to `docker exec`. A TTY corrupts the binary dump.
- The official image trusts local socket connections, so `pg_dump` usually needs no password. If it asks for one, add `-e PGPASSWORD=...` to `docker exec`.

## 3. Create the systemd service and timer

Create `/etc/systemd/system/pg-backup-app.service`:

```ini
[Unit]
Description=Nightly pg_dump of the app database
After=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/pg-backup-app.sh
```

Create `/etc/systemd/system/pg-backup-app.timer`:

```ini
[Unit]
Description=Run pg-backup-app every night

[Timer]
OnCalendar=*-*-* 02:30:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable the timer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pg-backup-app.timer
```

`Persistent=true` runs a missed backup after the server boots. The timer uses the server time zone. Run `timedatectl` to check it.

## 4. Run the first backup now

1. Start the service: `sudo systemctl start pg-backup-app.service`
2. Check the file: `sudo ls -lh /var/backups/postgres`
3. Check the log: `sudo journalctl -u pg-backup-app.service -n 20`
4. Check the schedule: `systemctl list-timers pg-backup-app.timer`

`-mtime +6` deletes dumps that are 7 or more days old, so you usually see 7 or 8 dumps. Make sure the disk has space for 8 dumps.

## 5. Test a restore

Do this test now, then once a month. The test uses a throwaway container and does not touch `app-db`.

1. Become root:
   ```bash
   sudo -i
   ```
2. Find the image that `app-db` uses:
   ```bash
   docker inspect -f '{{.Config.Image}}' app-db
   ```
3. Select the newest dump:
   ```bash
   LATEST=$(ls -1t /var/backups/postgres/app_*.dump | head -n 1); echo "$LATEST"
   ```
4. Start a test container. If step 2 showed a different image, use that image instead of `postgres:17`.
   ```bash
   docker run -d --name app-db-restoretest \
     -e POSTGRES_USER=app -e POSTGRES_DB=app -e POSTGRES_PASSWORD=test \
     postgres:17
   ```
   The test container publishes no ports, so it does not conflict with `app-db`.
5. Wait until the server is ready:
   ```bash
   until docker exec app-db-restoretest pg_isready -h 127.0.0.1 -U app; do sleep 1; done
   ```
   `-h 127.0.0.1` makes the loop wait for the final server, not the temporary setup server.
6. Restore the dump:
   ```bash
   docker exec -i app-db-restoretest pg_restore -U app -d app --no-owner < "$LATEST"
   ```
   A clean restore prints nothing. If `pg_restore` prints errors, read each one.
7. Compare the live database with the restored database. Replace `your_main_table` with an important table.
   ```bash
   for c in app-db app-db-restoretest; do
     echo "== $c"
     docker exec "$c" psql -U app -d app -Atc \
       "SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema');"
     docker exec "$c" psql -U app -d app -Atc "SELECT count(*) FROM your_main_table;"
   done
   ```
   The table counts must match. Small row differences are normal, because the live database got new writes after the dump.
8. Remove the test container:
   ```bash
   docker rm -f -v app-db-restoretest
   ```
   **Warning:** Type the container name exactly. If you type `app-db`, you remove the production container.

## Suggested improvements

- **Copy the dumps to a second location.** Now the dumps are on the same server as the database. If the disk or server fails, you lose both. A nightly `restic` or `rclone` copy to object storage fixes this.
- **Add a failure alert.** Now a failed run shows only in the journal. Add a ping to a service like healthchecks.io at the end of the script, or add `OnFailure=` to the service.
- **Back up roles if you have more than `app`.** `pg_dump` does not save roles. If the database uses other roles, add a `pg_dumpall -U app --globals-only` line to the script.
- **Know the data-loss window.** A nightly dump can lose up to 24 hours of data. If that is too much, use WAL archiving with pgBackRest or WAL-G.

Hold the vault, keeper of the night watch.