1. Install and start `cron`:

   ```bash
   sudo apt-get update
   sudo apt-get install -y cron
   sudo systemctl enable --now cron
   ```

2. Create a backup directory. Only `root` can access this directory.

   ```bash
   sudo install -d -o root -g root -m 0700 /var/backups/app
   ```

3. Run `sudoedit /usr/local/sbin/backup-app-db`. Put this script in the file:

   ```bash
   #!/bin/bash
   set -euo pipefail
   export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
   umask 077

   backup_dir=/var/backups/app
   backup_file="$backup_dir/app-$(date -u +%Y%m%dT%H%M%SZ).dump"
   temporary_file=$(mktemp "$backup_dir/.app-XXXXXX")

   trap 'rm -f -- "$temporary_file"' EXIT

   docker exec app-db pg_dump \
     --username=app \
     --dbname=app \
     --format=custom \
     --no-password > "$temporary_file"

   mv -- "$temporary_file" "$backup_file"

   find "$backup_dir" -maxdepth 1 -type f \
     -name 'app-*.dump' -mtime +6 -delete

   printf 'Backup complete: %s\n' "$backup_file"
   ```

   The database can stay in use during the backup. The custom format includes compression.

   The script saves the final file only after `pg_dump` succeeds. It then deletes backups at least seven days old.

   This command uses a local database connection inside the container. If authentication requires a password, configure a `.pgpass` file for the operating system user that runs `pg_dump`. Set its permissions to `0600`. Keep the password out of the script.

4. Set the script permissions. Then make the first backup:

   ```bash
   sudo chown root:root /usr/local/sbin/backup-app-db
   sudo chmod 0700 /usr/local/sbin/backup-app-db
   sudo /usr/local/sbin/backup-app-db
   ```

   Correct all errors before you set the schedule.

5. Run `sudo crontab -e`. Add this line. Keep the existing lines.

   ```cron
   0 3 * * * /usr/local/sbin/backup-app-db >> /var/log/app-db-backup.log 2>&1
   ```

   The backup runs each night at 03:00 in the server time zone. Check the log each day:

   ```bash
   sudo tail -n 30 /var/log/app-db-backup.log
   ```

6. Test a restore in a separate container.

   List the backups:

   ```bash
   sudo ls -lt /var/backups/app
   ```

   Replace the example file name below with an actual backup file name:

   ```bash
   backup=/var/backups/app/app-YYYYMMDDTHHMMSSZ.dump
   ```

   Start the test container with the same image as `app-db`:

   ```bash
   test_image=$(sudo docker inspect --format '{{.Image}}' app-db)

   sudo docker run --detach \
     --name app-db-restore-test \
     --network none \
     --env POSTGRES_USER=app \
     --env POSTGRES_PASSWORD=restore-test-only \
     --env POSTGRES_DB=app_restore \
     "$test_image"
   ```

   This container has separate database storage. It has no external network connection.

   Run this command until it reports `accepting connections`:

   ```bash
   sudo docker exec app-db-restore-test pg_isready \
     --host=127.0.0.1 --username=app --dbname=app_restore
   ```

   Copy the backup into the test container:

   ```bash
   sudo docker cp "$backup" app-db-restore-test:/tmp/app.dump
   ```

   Restore the backup:

   ```bash
   sudo docker exec app-db-restore-test pg_restore \
     --username=app \
     --dbname=app_restore \
     --exit-on-error \
     --no-owner \
     --no-privileges \
     /tmp/app.dump
   ```

   `pg_restore` must finish with exit status `0`. An error means the restore test failed.

   Examine the restored tables:

   ```bash
   sudo docker exec app-db-restore-test psql \
     --username=app --dbname=app_restore \
     --set=ON_ERROR_STOP=1 --command='\dt'
   ```

   Replace `example_table` with an important table name:

   ```bash
   sudo docker exec app-db-restore-test psql \
     --username=app --dbname=app_restore \
     --set=ON_ERROR_STOP=1 \
     --command='SELECT count(*) FROM public.example_table;'
   ```

   Compare the result with the expected record count at the backup time. Check known records and important application queries.

   This test does not check the original owners or access rights.

7. After the test, remove the test container and its temporary volumes:

   ```bash
   sudo docker rm --force --volumes app-db-restore-test
   ```

The backup contains the database data and objects. It does not contain database roles or server configuration. Keep a second backup copy on another server.