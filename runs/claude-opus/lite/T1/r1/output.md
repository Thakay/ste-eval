A root script dumps `app` at 02:30 each night and deletes dumps older than 7 days. A throwaway container proves that the newest dump restores.

## 1. Set up the nightly backup

1. Create the backup folder. Only root can read it, because the dumps hold all your data.
   ```bash
   sudo install -d -m 700 /var/backups/app-db
   ```
2. Create `/usr/local/bin/backup-app-db.sh` with this content:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   umask 077

   BACKUP_DIR=/var/backups/app-db
   FILE="$BACKUP_DIR/app-$(date +%F_%H%M).dump"

   # Remove the partial file if the dump fails.
   trap 'rm -f "$FILE.tmp"' EXIT

   # -Fc: compressed custom format. Do not add -t: a TTY corrupts binary output.
   docker exec app-db pg_dump -U app -d app -Fc > "$FILE.tmp"
   mv "$FILE.tmp" "$FILE"

   # Delete dumps older than 7 days. This runs only after a good dump.
   find "$BACKUP_DIR" -name 'app-*.dump' -mtime +6 -delete

   echo "$(date -Is) OK $FILE $(du -h "$FILE" | cut -f1)"
   ```
3. Make the script executable:
   ```bash
   sudo chmod 700 /usr/local/bin/backup-app-db.sh
   ```
4. Run the script one time by hand. Then make sure the dump file exists and is not empty.
   ```bash
   sudo /usr/local/bin/backup-app-db.sh
   sudo ls -lh /var/backups/app-db
   ```
   The official image trusts socket connections inside the container, so the script needs no password. If the dump fails with a password error, replace the `docker exec` line with this one:
   ```bash
   docker exec app-db sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -U app -d app -Fc' > "$FILE.tmp"
   ```
5. Add the cron job:
   ```bash
   echo '30 2 * * * root /usr/local/bin/backup-app-db.sh >> /var/log/app-db-backup.log 2>&1' | sudo tee /etc/cron.d/app-db-backup
   ```
   Cron uses the server time zone. Run `timedatectl` to see it.
6. On the next day, look for an `OK` line in the log:
   ```bash
   sudo tail /var/log/app-db-backup.log
   ```

## 2. Test a restore

Do this test now. Do it again one time each month.

1. Open a root shell, so you can read the dumps:
   ```bash
   sudo -i
   ```
2. Start a throwaway container from the same image as `app-db`. It has no volume and no published port.
   ```bash
   IMAGE=$(docker inspect app-db --format '{{.Config.Image}}')
   docker run -d --name app-db-restore-test \
     -e POSTGRES_USER=app -e POSTGRES_PASSWORD=test -e POSTGRES_DB=app \
     "$IMAGE"
   ```
   The same image gives the same Postgres version and the same extensions (for example PostGIS or pgvector).
3. Wait until the server is ready:
   ```bash
   until docker exec app-db-restore-test pg_isready -h localhost -U app; do sleep 1; done
   ```
   Keep `-h localhost`. On first start, the image runs a temporary server on the socket only. The TCP check waits for the real server.
4. Restore the newest dump:
   ```bash
   LATEST=$(ls -1t /var/backups/app-db/app-*.dump | head -n 1)
   docker exec -i app-db-restore-test pg_restore -U app -d app --exit-on-error < "$LATEST"
   ```
   The command must finish with no errors. If it fails on a missing role, see "Back up roles" below.
5. Compare the row count of an important table in both databases. Replace `your_table` with a real table name.
   ```bash
   docker exec app-db-restore-test psql -U app -d app -c 'SELECT count(*) FROM your_table;'
   docker exec app-db psql -U app -d app -c 'SELECT count(*) FROM your_table;'
   ```
   The restored count can be a little lower, because the live table got new rows after the dump. Also run `\dt` in the test container to see all tables.
6. Remove the test container and exit the root shell:
   ```bash
   docker rm -f app-db-restore-test
   exit
   ```
   **Warning:** Type `app-db-restore-test` exactly. If you type `app-db`, you stop and remove the live database container.

## Gaps to close

- **Copy the dumps off the server.** This is the largest gap. The dumps are on the same disk as the database. If the disk or the server fails, you lose both. Copy them to another machine or to object storage, for example with `restic` or `rclone`.
- **Get an alert when a run fails.** Now a failure only goes to the log file. Add a ping to a check service at the end of the script.
- **Back up roles.** `pg_dump` does not save roles. If objects use roles other than `app`, also save `docker exec app-db pg_dumpall -U app --globals-only`.
- **Plan disk space for 8 dumps.** The `-mtime +6` rule keeps 7 or 8 files, based on small timing differences.
- **Automate the restore test.** Put Part 2 in a second script and run it each month from cron.

Your data has a rearguard now. Hold the line, quartermaster.