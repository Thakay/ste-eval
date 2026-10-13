Use `pg_dump` inside `app-db`, store each successful dump on the host, and schedule it with cron. The custom dump format is compressed and supports `pg_restore`.

**1. Prepare the server and authentication**

Run these commands on the Ubuntu host:

```bash
sudo apt-get update
sudo apt-get install -y cron
sudo systemctl enable --now cron
sudo install -d -m 0700 -o root -g root /var/backups/postgres/app
```

The database user `app` must be able to read all data being backed up. Verify authentication:

```bash
sudo docker exec app-db \
  psql --username=app --dbname=app --no-password -c 'SELECT 1;'
```

If this fails because a password is required, configure a protected `.pgpass` file inside the container, readable by the OS user running `pg_dump`, with mode `0600`. Avoid putting the password in the cron command or script.

**2. Create the backup script**

Create `/usr/local/sbin/backup-app-db` as root with this content:

```bash
#!/bin/bash
set -euo pipefail
umask 077
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

backup_dir=/var/backups/postgres/app

# Prevent overlapping runs.
exec 9>/run/lock/backup-app-db.lock
flock -n 9 || exit 0

stamp=$(date -u +%Y-%m-%dT%H%M%SZ)
backup="$backup_dir/app-$stamp.dump"
tmp=$(mktemp "$backup_dir/.app-backup.XXXXXX")
trap 'rm -f -- "$tmp"' EXIT

# No TTY: preserve the binary dump exactly.
docker exec app-db \
  pg_dump --username=app --dbname=app \
  --format=custom --no-password > "$tmp"

test -s "$tmp"
mv -- "$tmp" "$backup"

# Delete completed backups at least seven days old,
# only after the new backup succeeds.
find "$backup_dir" -maxdepth 1 -type f \
  -name 'app-*.dump' -mtime +6 -delete

printf '%s Created %s\n' "$(date -u --iso-8601=seconds)" "$backup"
```

Then secure it:

```bash
sudo chown root:root /usr/local/sbin/backup-app-db
sudo chmod 0700 /usr/local/sbin/backup-app-db
```

Temporary files are removed on failure; completed backups appear only after `pg_dump` succeeds. `pg_dump` takes a consistent snapshot while the database remains online.

**3. Schedule it nightly**

Create `/etc/cron.d/app-db-backup`, owned by root, with mode `0644` and a trailing newline:

```cron
0 2 * * * root /usr/local/sbin/backup-app-db >> /var/log/app-db-backup.log 2>&1
```

This runs at **02:00 in the server’s configured timezone**.

Run it manually once:

```bash
sudo /usr/local/sbin/backup-app-db
sudo ls -lh /var/backups/postgres/app
```

Monitor scheduled runs and failures; redirected output alone does not provide alerts.

**4. Test an actual restore**

Use a separate, disposable Postgres 17 container. If production uses additional extensions, use an image containing those same extensions.

```bash
sudo docker run -d \
  --name app-db-restore-test \
  --network none \
  -e POSTGRES_DB=app \
  -e POSTGRES_USER=app \
  -e POSTGRES_PASSWORD=restore-test-only-password \
  postgres:17
```

Wait until this reports “accepting connections”:

```bash
sudo docker exec app-db-restore-test \
  pg_isready --username=app --dbname=app
```

Select an actual backup filename and restore it. The root shell below can read the protected backup directory:

```bash
sudo bash
backup=/var/backups/postgres/app/app-REPLACE-WITH-TIMESTAMP.dump

docker exec -i app-db-restore-test \
  pg_restore --username=app --dbname=app \
  --clean --if-exists \
  --no-owner --no-privileges \
  --exit-on-error --single-transaction < "$backup"

exit
```

A successful restore must exit with status `0`. Then inspect tables and run meaningful checks against the restored data:

```bash
sudo docker exec app-db-restore-test \
  psql --username=app --dbname=app -c '\dt'

# Replace important_table with a real application table.
sudo docker exec app-db-restore-test \
  psql --username=app --dbname=app \
  -c 'SELECT count(*) FROM public.important_table;'
```

Check representative records and important application queries against expected results. Merely listing the dump’s contents does not prove it can be restored.

Remove the test container and its disposable volume afterward:

```bash
sudo docker rm -f -v app-db-restore-test
```

Repeat restore tests periodically. This test skips original ownership and grants; verify those separately if production recovery depends on them. `pg_dump` backs up `app`, while cluster roles and tablespaces require a separate `pg_dumpall --globals-only` backup. Keep an additional backup copy off the server to cover server or disk loss.