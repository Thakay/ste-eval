Inside the `api` container, `localhost` means **the API container itself**, not your machine or the Postgres container. Compose makes services reachable by their service names, so use **`db:5432`**.

Also, your current `depends_on` starts the database container first but doesn’t wait for PostgreSQL to accept connections. Fix both issues:

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
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "app", "-d", "app"]
      interval: 5s
      timeout: 5s
      retries: 10
```

Run `docker compose up --build` after saving the change. You don’t need to publish Postgres’s port for communication between these containers.

Keep `localhost` in your local development configuration if Postgres is reachable there. For resilience, the API should also retry database connections with backoff, since the database can restart after startup.