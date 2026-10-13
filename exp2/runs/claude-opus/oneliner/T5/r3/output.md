## Cause

**1. `localhost` is the wrong host in a container.**

In a container, `localhost` is that container. It is not your computer, and it is not the `db` container.

With `npm run dev`, the API is on your computer. PostgreSQL is on port 5432 of your computer, so `localhost:5432` is correct.

In Compose, the API is in the `api` container. There is no PostgreSQL server in the `api` container. Thus, the connection to `127.0.0.1:5432` gets `ECONNREFUSED`.

Compose puts all services on one network. The DNS name of each service is the same as its service name. Thus, the API must connect to the host `db`.

**2. `depends_on` does not wait for PostgreSQL.**

`depends_on` only makes Compose start `db` before `api`. It does not make Compose wait until PostgreSQL is ready. Your log shows this: the `api` container stopped, and then PostgreSQL became ready. If you only correct the host name, the API can still connect too early.

## Correction

1. In `DATABASE_URL`, change `localhost` to `db`.
2. Add a `healthcheck` to the `db` service.
3. Change `depends_on` so that `api` waits until `db` is healthy.

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

4. Start the services again:

```
docker compose up --build
```

## Notes

- Do not change the database URL for `npm run dev`. On your computer, `localhost` is correct.
- You do not need `ports:` on `db` for this connection. Containers on the same Compose network connect directly. Add `ports: ["5432:5432"]` only if a tool on your computer must connect to this database.