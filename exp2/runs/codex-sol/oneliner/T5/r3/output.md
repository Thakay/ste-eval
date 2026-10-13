On your machine, `localhost` is your machine. In the API container, `localhost` is the API container. Use `db` as the database host.

Your `depends_on` setting starts the database container first. It does not wait until PostgreSQL is ready. Add a health check:

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

The API will connect to `db:5432` after the database health check passes.