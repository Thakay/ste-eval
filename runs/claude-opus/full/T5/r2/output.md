`localhost` inside the `api` container means the `api` container itself, not your machine. Postgres runs in the separate `db` container, so nothing listens on `127.0.0.1:5432` from where `api` sits. On your machine, `npm run dev` works because the API and Postgres run on the same host.

Compose puts all services on one shared network. Each service is reachable by its service name, so the host for Postgres is `db`.

There is also a second problem. A plain `depends_on` list only waits for the `db` container to start. It does not wait for Postgres to accept connections. Your log shows this: the `db` "ready" line comes after `api` exits. A healthcheck makes `api` wait until Postgres is ready.

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

Then run `docker compose up` again.

Optional: if you want `npm run dev` on your machine to use this same database, add `ports: ["5432:5432"]` to `db`. Keep `localhost` in the URL that `npm run dev` uses. If a local Postgres already uses port 5432, map a different host port, such as `"5433:5432"`.

Hold the gate, Centurion. The legion marches at dawn.