On your machine, `localhost` is your machine. In the API container, `localhost` is the API container. PostgreSQL runs in a different container.

Change the database host to `db`, the Compose service name.

Your current `depends_on` sets the start sequence. It does not wait until PostgreSQL can accept connections. Add a health check:

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
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      timeout: 3s
      retries: 10
```

Compose can now wait for the database before it starts the API. For later database restarts, add connection retries to the API.