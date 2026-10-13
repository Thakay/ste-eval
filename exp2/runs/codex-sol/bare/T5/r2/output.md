Inside the API container, `localhost` points to the API container itself. Postgres is in a separate container, reachable by its Compose service name: **`db`**. Running locally works because `localhost` refers to your machine, where your database is reachable.

Change the URL to `postgres://app:secret@db:5432/app`.

Also, your current `depends_on` controls startup order but doesn’t wait for Postgres to accept connections. Add a health check and require it to pass:

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
      test: ["CMD", "pg_isready", "-h", "127.0.0.1", "-U", "app", "-d", "app"]
      interval: 5s
      timeout: 5s
      retries: 10
```

No published database port is needed for communication between these services. Keep connection retry/backoff in the API as well, so it can recover if the database restarts later.