## Why it fails

Inside a container, `localhost` means **that container itself**, not your machine and not the other services. When you run `npm run dev` on your host, Postgres is listening on your host's `localhost:5432`, so it works. In Compose, the `api` container looks for Postgres on its own loopback interface, where nothing is listening, and gets `ECONNREFUSED 127.0.0.1:5432`.

Compose puts both services on a shared network where each one is reachable **by its service name**. Postgres is at `db:5432`.

There's also a second problem in your log. `db-1 ... ready to accept connections` appears *after* `api-1 exited`. `depends_on` only waits for the `db` container to **start**, not for Postgres to be **ready**. Even with the hostname fixed, the API can still lose that race on a cold start.

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

What changed:

1. **`localhost` → `db`** in `DATABASE_URL`. This fixes the `ECONNREFUSED`.
2. **A `healthcheck` on `db`** using `pg_isready`, which ships in the postgres image.
3. **`condition: service_healthy`**, so `api` only starts once Postgres actually accepts connections.

Notes:

- The `app` database will exist because `POSTGRES_DB` defaults to `POSTGRES_USER`.
- Keep `npm run dev` working by leaving `localhost` in your local `.env` and letting Compose override `DATABASE_URL`, as it does here.
- If you also want to reach this Postgres from your host (for example with `psql` or a GUI), add `ports: ["5432:5432"]` to `db`. The `api` container doesn't need that, since it talks to `db` over the internal network. If you already run a local Postgres on 5432, map it to a different port, like `"5433:5432"`.
- For extra resilience, give the API's DB connection some retry logic, or add `restart: on-failure` to `api`. Postgres can restart or be briefly unavailable after startup too.