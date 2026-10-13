Inside Compose, `localhost` points to the `api` container itself. PostgreSQL runs in the separate `db` container. Your local run uses your machine’s `localhost`, so it can reach your local database.

Use the Compose service name, `db`, as the database hostname. Also, plain `depends_on` controls startup order but does not wait for PostgreSQL to accept connections.

1. Replace `docker-compose.yml` with this configuration:

   ```yaml
   services:
     api:
       build: .
       environment:
         DATABASE_URL: postgres://app:secret@db:5432/app
       depends_on:
         db:
           condition: service_healthy

     db:
       image: postgres:17
       environment:
         POSTGRES_USER: app
         POSTGRES_PASSWORD: secret
       healthcheck:
         test: ["CMD-SHELL", "pg_isready -h 127.0.0.1 -U app -d app"]
         interval: 5s
         timeout: 5s
         retries: 10
   ```

2. Recreate the containers with `docker compose up --build`.

The health check runs inside `db`, where `127.0.0.1` is correct. Container communication uses `db:5432` without a published port.

The API should also retry temporary connection failures to recover if PostgreSQL restarts later.

Godspeed, Spartan.