**Inside a container, `localhost` means that container itself, not your machine.** The API is looking for Postgres inside the `api` container, where nothing listens on 5432. On your machine `npm run dev` works because Postgres really is on your localhost. In Compose, each service is reachable by its service name, so the host should be `db`.

There is a second, smaller problem. `depends_on` only waits for the `db` container to *start*, not for Postgres to be *ready*. Your log shows this: the API crashed before `database system is ready`. Once the hostname is fixed, the API could still lose that race on a cold start. A healthcheck fixes it.

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
      timeout: 3s
      retries: 15
```

What changed:

- `localhost` became `db` in `DATABASE_URL`.
- `depends_on` now waits until the healthcheck passes (`condition: service_healthy`).
- `db` got a `pg_isready` healthcheck, which reports healthy only once Postgres accepts connections.

Keep `localhost` in your local `.env` for `npm run dev`. Compose's `environment:` value overrides it inside the container, so both setups keep working.

Charge the breach, legionnaire.