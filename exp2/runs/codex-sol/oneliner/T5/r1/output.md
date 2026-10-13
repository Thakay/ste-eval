In the API container, `localhost` refers to that container. PostgreSQL runs in the separate `db` container. With `npm run dev`, `localhost` refers to your machine.

Use `db` as the database host. Also add a health check: your current `depends_on` controls the start sequence, but does not wait until PostgreSQL is ready.

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
      interval: 5s
      timeout: 5s
      retries: 10
```

The API can use `db:5432` through the Compose network. You do not need to publish the database port for this connection.

Keep `localhost` in your local development settings. Add connection retries to the API to handle later database restarts.