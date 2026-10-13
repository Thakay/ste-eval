Use `pg_dump` for a consistent backup while the database stays online. The steps below run nightly at **02:00 server time** and retain completed backups for seven days.

They assume `app` can read every table and authenticate locally inside `app-db`. If authentication requires a password, configure a protected `.pgpass` file for the container user running `pg_dump`.

1. **Prepare the server.**

   ```bash
   sudo apt-get update
   sudo apt-get install -y cron
   sudo systemctl enable --now cron
   sudo install -d -m 0700 /var/backups/app-db
   ```

2. **Create the backup script.**

   Save this as `/usr/local/sbin/backup-app-db`, using `sudo` to edit it:

   ```bash
   #!/bin/bash
   set -euo pipefail
   umask 077

   dir=/var/backups/app-db
   backup="$dir/app-$(date -u +%Y%m%dT%H%M%SZ).dump"
   tmp=$(mktemp "$dir/.backup.XXXXXX")
   trap 'rm -f -- "$tmp"' EXIT

   docker exec app-db pg_dump \
     --username=app \
     --dbname=app \
     --no-password \
     --format=custom > "$tmp"

   # Publish the file only after pg_dump succeeds.
   mv -- "$tmp" "$backup"

   # Remove completed backups at least seven days old.
   find "$dir" -maxdepth 1 -type f \
     -name 'app-*.dump' -mtime +6 -delete

   printf 'Backup complete: %s\n' "$backup"
   ```

   Make it executable and create the first backup:

   ```bash
   sudo chmod 0700 /usr/local/sbin/backup-app-db
   sudo /usr/local/sbin/backup-app-db
   sudo ls -lh /var/backups/app-db
   ```

   Custom-format dumps contain the database schema and data and are restored with `pg_restore`.

3. **Schedule the nightly backup.**

   Save this as `/etc/cron.d/app-db-backup`:

   ```cron
   SHELL=/bin/bash
   PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

   0 2 * * * root /usr/bin/flock -n /run/lock/app-db-backup.lock /usr/local/sbin/backup-app-db >> /var/log/app-db-backup.log 2>&1
   ```

   Ensure the file ends with a newline, then set its permissions:

   ```bash
   sudo chown root:root /etc/cron.d/app-db-backup
   sudo chmod 0644 /etc/cron.d/app-db-backup
   ```

   `flock` prevents overlapping scheduled runs. Check `/var/log/app-db-backup.log` after the first scheduled backup.

4. **Test restoration in a separate container.**

   Create a disposable PostgreSQL 17 instance with no published ports:

   ```bash
   sudo docker run -d \
     --name app-db-restore-test \
     --network none \
     -e POSTGRES_USER=app \
     -e POSTGRES_PASSWORD=restore-test-only \
     -e POSTGRES_DB=app \
     postgres:17
   ```

   If production uses extensions, use a test image containing the same extensions.

   Check readiness, repeating this command until it reports `accepting connections`:

   ```bash
   sudo docker exec app-db-restore-test \
     pg_isready -h 127.0.0.1 -U app -d app
   ```

   Select the latest backup and restore it:

   ```bash
   set -o pipefail

   BACKUP=$(sudo find /var/backups/app-db -maxdepth 1 \
     -type f -name 'app-*.dump' -printf '%p\n' | sort | tail -n 1)

   sudo cat "$BACKUP" | sudo docker exec -i app-db-restore-test \
     pg_restore \
       --username=app \
       --dbname=app \
       --exit-on-error \
       --no-owner \
       --no-privileges
   ```

   Require this command to exit successfully. The restore flags make `app` own the restored objects and omit original access grants.

   Inspect the restored tables:

   ```bash
   sudo docker exec app-db-restore-test \
     psql -U app -d app -v ON_ERROR_STOP=1 -c '\dt'
   ```

   Then check important table counts and known records. For example, replace `your_main_table` below with a real table:

   ```bash
   sudo docker exec app-db-restore-test \
     psql -U app -d app -v ON_ERROR_STOP=1 \
       -c 'SELECT count(*) FROM public.your_main_table;'
   ```

   Compare the results with what you expect at the backup’s timestamp. Repeat this restore test periodically.

5. **Remove the disposable test instance.**

   ```bash
   sudo docker rm -f -v app-db-restore-test
   ```

These dumps cover `app`. Cluster-wide roles require a separate `pg_dumpall --globals-only` backup. Keep another copy off the server so a server or disk failure cannot destroy every backup.

Godspeed, Spartan.