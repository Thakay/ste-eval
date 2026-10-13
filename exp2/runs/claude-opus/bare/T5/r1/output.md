## Why it fails

Inside a container, `localhost` means **that container**, not your machine and not the other services. Your API connects to `127.0.0.1:5432` inside the `api` container, where nothing is listening, so it gets `ECONNREFUSED`.

It works with `npm run dev` because there the API runs on your host, and Postgres is reachable on the host's `localhost:5432`.

In Compose, each service is reachable from the others **by its service name** on the default network. Your database's hostname is `db`.

## Fix

```yaml
services:
  api:
    build: .
    environment:
      DATABASE_URL: postgres://app:secret@db:5432/app   # localhost -> db
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
      retries: 15
```

The essential fix is changing `localhost` to `db`. The healthcheck change fixes a second problem you would probably hit next:

- **`depends_on` with a plain list only waits for the `db` container to *start*.** It does not wait for Postgres to be ready to accept connections. Postgres takes a few seconds to initialize, especially on the first run, so the API can still lose that race and crash.
- With `condition: service_healthy`, Compose waits until `pg_isready` succeeds before it starts `api`.

(`POSTGRES_DB` defaults to `POSTGRES_USER`, so the `app` database exists, and `/app` in your URL is fine.)

## Optional

If you also want to keep running `npm run dev` on your host against the Compose database, publish the port:

```yaml
  db:
    ports:
      - "5432:5432"
```

Your local `.env` can then keep using `localhost:5432`, while the containerized API uses `db:5432`. If you already have a Postgres running locally on 5432, map it to a different host port instead, such as `"5433:5432"`.