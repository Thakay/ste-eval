**Answer:** Inside the `api` container, `localhost` points to the `api` container itself, not to your machine or the `db` container. Nothing listens on port 5432 in the `api` container, so the connection fails. On your machine, `localhost` works because Postgres runs on that same machine.

The log also shows a second problem: `db` reports "ready" after `api` already exited. A plain `depends_on` list only waits for the `db` container to start. It does not wait until Postgres accepts connections. So even with the correct host, `api` can still fail on a cold start.

**Fix:**

1. In `DATABASE_URL`, change the host from `localhost` to `db`. Compose gives each service a DNS name that is the same as the service name.
2. Add a healthcheck to the `db` service.
3. Set `api` to wait until `db` is healthy.

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
      retries: 15
```

**Two related points:**

- **Local dev against this database.** If you want `npm run dev` to use the compose database, add `ports: ["5432:5432"]` to `db`. Keep `localhost` in your local `.env`, because your machine reaches the container through the published port.
- **Data persistence.** `db` has no volume. If you run `docker compose down`, the data is lost. To keep the data, add `volumes: ["pgdata:/var/lib/postgresql/data"]` to `db` and a top-level `volumes: { pgdata: {} }`.

Raise your shield and run `docker compose up` again, hoplite.