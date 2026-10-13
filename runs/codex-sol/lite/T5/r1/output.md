`localhost` points to the API container itself in Compose. PostgreSQL runs in the separate `db` container. With `npm run dev`, `localhost` points to your machine.

The API must connect to `db:5432`. There is also a possible startup race. Plain `depends_on` controls startup order, but does not wait for PostgreSQL to accept connections.

This configuration fixes the hostname. It also makes the API wait for database readiness:

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

`127.0.0.1` is correct in the health check because it runs inside the database container. You do not need to publish the database port for communication between these services.

The API also needs connection retries to handle later database restarts.

Godspeed, Spartan.