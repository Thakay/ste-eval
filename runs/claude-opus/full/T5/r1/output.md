**Answer:** In the container, `localhost` is the `api` container itself, not the database. Postgres runs in the separate `db` container, so nothing listens on port 5432 inside `api`. With `npm run dev`, `localhost` works because a Postgres server probably runs on your own machine.

There are two fixes.

**1. Use the service name as the host.** Compose puts all services on one network, and each service name works as a hostname.

```yaml
DATABASE_URL: postgres://app:secret@db:5432/app
```

**2. Wait until Postgres is ready.** The short `depends_on` form waits only until the `db` container starts. It does not wait until Postgres accepts connections. Your log suggests this race: `api` exited before `db` printed "ready to accept connections". Add a healthcheck and make `api` wait for it:

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
      retries: 10
```

The healthcheck runs inside the `db` container, so `localhost` is correct there. The `-h localhost` flag forces a TCP check. Without it, `pg_isready` can pass early against the temporary server that Postgres runs during its first setup.

Hold the line, shield-bearer.