## Why it fails

Inside a container, `localhost` means **that container itself**, not your machine and not the other services. When the API runs on your host, `localhost:5432` reaches a Postgres listening on your host. In compose, the `api` container has nothing on port 5432, so the connection is refused.

Compose puts all services on a shared network where each one is reachable **by its service name**. Your database's hostname is `db`.

There's also a second problem, visible in the log order. The API crashed *before* Postgres logged "ready to accept connections." Plain `depends_on` only waits for the `db` container to **start**, not for Postgres to be ready. So even with the right hostname, you can hit a race on a cold start.

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
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 2s
      timeout: 5s
      retries: 10
```

The changes:
1. **`localhost` → `db`** in `DATABASE_URL`. This is the actual cause of the `ECONNREFUSED`.
2. **A `healthcheck` on `db` plus `condition: service_healthy`**, so `api` doesn't start until `pg_isready` succeeds.

## Optional

- **Retry in the app.** Healthchecks only cover startup. If Postgres restarts later, the API will still crash. A few connection retries with backoff in your db setup makes it more robust.
- **Keeping `npm run dev` working against the compose DB.** Add `ports: ["5432:5432"]` to `db`. Then your host can reach it at `localhost:5432`, and containers still use `db:5432`. Keep the two URLs separate, e.g. `localhost` in a local `.env` and `db` in compose.