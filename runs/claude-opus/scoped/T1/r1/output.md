**TL;DR:** A script runs `pg_dump` inside `app-db` every night at 02:30 through a systemd timer. It writes compressed dump files to `/var/backups/app-db` and deletes dump files that are 7 days old or older. You test the restore in a throwaway container, so the test never touches production.

## Part 1: Create the backup script

1. Open a root shell. Use this shell for all steps in this guide.
   ```bash
   sudo -i
   ```
2. Create the file `/usr/local/bin/backup-app-db.sh` with this content:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail

   BACKUP_DIR=/var/backups/app-db
   KEEP_DAYS=7
   FILE="$BACKUP_DIR/app_$(date +%F_%H%M).dump"

   umask 077
   mkdir -p "$BACKUP_DIR"
   trap 'rm -f "$FILE.partial"' EXIT

   # Dump to a temp name first, so a failed run never leaves a file that looks complete.
   docker exec app-db pg_dump -U app -d app -Fc > "$FILE.partial"
   mv "$FILE.partial" "$FILE"

   # Delete dumps that are KEEP_DAYS days old or older. Runs only if the dump succeeded.
   find "$BACKUP_DIR" -name 'app_*.dump' -mtime +$((KEEP_DAYS - 1)) -delete
   ```
3. Let only root read and run the script.
   ```bash
   chmod 700 /usr/local/bin/backup-app-db.sh
   ```
4. Run the script one time by hand.
   ```bash
   /usr/local/bin/backup-app-db.sh
   ```
5. Make sure that a new dump file exists and that its size is more than 0.
   ```bash
   ls -lh /var/backups/app-db
   ```
6. If the script stops with a password error, replace the `pg_dump` line with this line:
   ```bash
   docker exec app-db sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -U app -d app -Fc' > "$FILE.partial"
   ```

> **Warning:** Do not add the `-t` option to `docker exec`. A terminal (TTY) can change bytes in the binary dump and make it useless.

## Part 2: Run the backup every night

1. Create the file `/etc/systemd/system/app-db-backup.service` with this content:
   ```ini
   [Unit]
   Description=Nightly pg_dump of the app database
   After=docker.service

   [Service]
   Type=oneshot
   ExecStart=/usr/local/bin/backup-app-db.sh
   ```
2. Create the file `/etc/systemd/system/app-db-backup.timer` with this content:
   ```ini
   [Unit]
   Description=Run app-db-backup every night at 02:30

   [Timer]
   OnCalendar=*-*-* 02:30:00
   Persistent=true

   [Install]
   WantedBy=timers.target
   ```
   `OnCalendar` uses the server's local time zone. `Persistent=true` runs a missed backup after the next boot if the server was off at 02:30.
3. Tell systemd to read the new files.
   ```bash
   systemctl daemon-reload
   ```
4. Enable the timer and start it.
   ```bash
   systemctl enable --now app-db-backup.timer
   ```
5. Make sure that the timer shows a next run time.
   ```bash
   systemctl list-timers app-db-backup.timer
   ```
6. Start the service one time to test the full run through systemd.
   ```bash
   systemctl start app-db-backup.service
   ```
7. Read the service log. If a run fails, the error shows here.
   ```bash
   journalctl -u app-db-backup.service -n 20 --no-pager
   ```

## Part 3: Test that a backup restores

> **Warning:** Do not run `pg_restore` against `app-db`. The command writes into the live database. Use only the test container `app-db-restore-test`.

Do this test now. Then do it every month and after each Postgres upgrade.

1. Find the newest dump file and save its path.
   ```bash
   LATEST=$(ls -t /var/backups/app-db/app_*.dump | head -n 1)
   echo "$LATEST"
   ```
2. Find the image that `app-db` uses.
   ```bash
   docker inspect app-db --format '{{.Config.Image}}'
   ```
3. Start a test container. If step 2 showed an image other than `postgres:17`, use that image in the command.
   ```bash
   docker run -d --name app-db-restore-test \
     -e POSTGRES_USER=app -e POSTGRES_PASSWORD=restore-test -e POSTGRES_DB=app \
     postgres:17
   ```
   The command publishes no port, so nothing outside the server can connect to the test container.
4. Wait until the test server accepts connections.
   ```bash
   until docker exec app-db-restore-test pg_isready -U app -h 127.0.0.1; do sleep 2; done
   ```
   The `-h 127.0.0.1` check waits for the real server. Without it, the check can pass on the short setup server that the image starts first.
5. Restore the dump file into the test container.
   ```bash
   docker exec -i app-db-restore-test pg_restore -U app -d app --exit-on-error < "$LATEST"
   ```
   If this command shows an error, the backup failed the test. Find the cause before you trust the backups.
6. Compare the number of tables in the two databases. The two numbers must be the same.
   ```bash
   Q="SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema');"
   docker exec app-db psql -U app -d app -tAc "$Q"
   docker exec app-db-restore-test psql -U app -d app -tAc "$Q"
   ```
7. Compare the row count of one or two important tables. Replace `<table>` with a real table name.
   ```bash
   docker exec app-db psql -U app -d app -tAc "SELECT count(*) FROM <table>;"
   docker exec app-db-restore-test psql -U app -d app -tAc "SELECT count(*) FROM <table>;"
   ```
   The counts can differ a little, because production changed after the backup. A count of 0 or a large gap means the test failed.
8. Remove the test container and its data volume.
   ```bash
   docker rm -f -v app-db-restore-test
   ```
   The `-v` option removes the anonymous volume that holds the test data. Without `-v`, the volume stays on disk.

## Suggested improvements

- **Copy the dump files off the server.** This is the biggest gap. The dump files sit on the same server as the database, so a disk failure, a lost server, or ransomware takes both. Add one line at the end of the script that copies the new file to object storage or another host, for example with `rclone` or `restic`.
- **Get an alert when a backup fails.** A backup that fails without a sound is the most common way to lose data. Add `OnFailure=` to the service, or ping a check-in service such as healthchecks.io at the end of the script. That service alerts you when the ping does not arrive.
- **Save roles if you have more than `app`.** `pg_dump` saves one database, not roles or passwords. If other roles exist, also save them with `docker exec app-db pg_dumpall -U app --globals-only`.
- **Keep free disk space for 8 dump files.** The script writes the new file before it deletes the oldest one, so 8 files exist for a short time.

Hold the line, Keeper of the Vault. 🛡️