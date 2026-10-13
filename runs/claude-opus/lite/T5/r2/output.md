**Answer:** Inside the `api` container, `localhost` is the `api` container itself. Postgres runs in a different container, so nothing listens on port 5432 in `api`. With `npm run dev`, Postgres listens on your machine's `localhost`, so that setup works.

Compose puts all services on one shared network. Each service gets a DNS name that is the same as its service name. Thus, the `api` container can reach Postgres at `db:5432`.

Your log also shows a second problem. `depends_on` only waits for the `db` container to start. It does not wait for Postgres to accept connections. In your log, Postgres became ready after the API exited. If you only fix the host, the API can still crash on a cold start.

## Fix

1. Change the host in `DATABASE_URL` from `localhost` to `db`.
2. Add a healthcheck to `db` that uses `pg_isready`.
3. Set `depends_on` to wait until `db` is healthy.

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

The `-h localhost` in the healthcheck is correct, because the check runs inside the `db` container. It makes the check use TCP. During first-time setup, Postgres starts a temporary server on the Unix socket only. A socket check can report "ready" too early in that window.

## Optional improvements

- **Retry in the app.** Add a short retry loop around the first DB connect. The healthcheck only helps at startup, and a DB restart later can still crash the API.
- **Keep `localhost` for local dev.** Leave `localhost` in your local `.env` for `npm run dev`. Compose sets `DATABASE_URL` in the container environment. By default, `dotenv` does not replace a variable that already exists.
- **Host access to the compose DB.** If you want `npm run dev` to use the compose Postgres, add `ports: ["5432:5432"]` to `db`. If a local Postgres already uses port 5432, this mapping fails. In that case, map a different host port, such as `"5433:5432"`.

Shields locked, legionnaire. Hold the line.