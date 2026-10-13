**Cause:** Inside the `api` container, `localhost` is the `api` container itself. Postgres runs in a different container, so nothing listens on `127.0.0.1:5432` inside `api`. With `npm run dev`, the API runs on your host, and Postgres is reachable on your host's `localhost`.

**Fix:** Use the service name `db` as the host. Compose puts both services on one default network. On that network, each service name resolves to its container.

There is a second problem. `depends_on` only waits for the `db` container to start. It does not wait for Postgres to accept connections. Your log shows this: `api` failed before `db` printed "ready to accept connections". Add a healthcheck and make `api` wait for it.

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
      test: ["CMD", "pg_isready", "-h", "127.0.0.1", "-U", "app", "-d", "app"]
      interval: 2s
      timeout: 3s
      retries: 15
```

Notes:

- The `127.0.0.1` in the healthcheck is correct, because the check runs inside the `db` container.
- The check uses TCP on purpose. On the first run, Postgres initializes with only its Unix socket open. A socket check can pass too early during that step.
- If you also want `npm run dev` to use this database, add `ports: ["5432:5432"]` to `db`. If Postgres already runs on your host, use `"5433:5432"` to prevent a port conflict.

Raise your shield and sail the containers, dockhand.