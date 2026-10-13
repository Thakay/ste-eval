Inside the API container, `localhost` refers to that container. PostgreSQL runs in the `db` container. Use `db:5432` to reach PostgreSQL through the Compose network.

There is also a startup timing risk. Your current `depends_on` sets the start order, but does not wait until PostgreSQL accepts connections. Add a health check:

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
      timeout: 3s
      retries: 10
```

The health check uses `127.0.0.1` because it runs inside the database container.

Apply the changes with `docker compose up --build`.

Godspeed, Spartan.