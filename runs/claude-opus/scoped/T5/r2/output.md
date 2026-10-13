**Inside the `api` container, `localhost` is the container itself, not your machine and not the `db` container.** Nothing listens on port 5432 inside `api`, so the connection fails. On your machine, `localhost` reaches your local Postgres, so `npm run dev` works.

A second problem hides behind the first one. `depends_on: [db]` waits only until the `db` container starts, not until Postgres accepts connections. Your log shows this: `api` crashed before `db` printed "ready to accept connections".

## Fix

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
      test: ["CMD-SHELL", "pg_isready -h localhost -U app -d app"]
      interval: 2s
      timeout: 5s
      retries: 15
```

What changed:

1. Set the host to `db`. Compose gives each service a DNS name on the shared network.
2. Add a `healthcheck` to `db`. Use `pg_isready` to test that Postgres accepts connections.
3. Set `condition: service_healthy` on `api`. Compose then starts `api` only after `db` is healthy.

Notes:

- `-h localhost` in the healthcheck is intentional. The healthcheck runs inside the `db` container, so `localhost` there is correct. It also makes `pg_isready` test TCP, which skips the short-lived init server that the Postgres image starts first.
- The database `app` exists because `POSTGRES_DB` defaults to `POSTGRES_USER`.
- Add connection retries in the API anyway. The healthcheck covers startup only, not a `db` restart later.
- If you want `npm run dev` on your machine to use this same database, add `ports: ["5432:5432"]` to `db`. Keep `localhost` in your local `.env`. This fails if a local Postgres already uses port 5432.

Hold the line, packet-warden.