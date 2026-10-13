## Cause

Each container has its own network. In the `api` container, `localhost` (127.0.0.1) is the `api` container. It is not the `db` container. No database is available on port 5432 in the `api` container. This causes the `ECONNREFUSED` error.

On your machine, `localhost` is correct because Postgres is on the same machine.

There is a second problem. The short form of `depends_on` only waits until the `db` container starts. It does not wait until Postgres can accept connections. In your log, the `db` "ready" message comes after the `api` error.

## Procedure

1. In `DATABASE_URL`, change `localhost` to `db`. Compose gives each service a DNS name that is the same as the service name.
2. Add a healthcheck to the `db` service.
3. Change `depends_on` so that `api` waits for the `service_healthy` condition.

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

4. Start the services again with `docker compose up --build`.

## Notes

- If you set `DATABASE_URL` in a local file for `npm run dev`, keep `localhost` in that file.
- If you must connect to the `db` container from your machine, add `ports: ["5432:5432"]` to the `db` service.