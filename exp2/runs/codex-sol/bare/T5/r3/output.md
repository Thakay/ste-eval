Inside the API container, `localhost` means **the API container itself**. On your machine, it means your machine. Compose services reach each other using their service names, so the database hostname must be **`db`**.

There’s also a startup timing issue: plain `depends_on` starts the database container first but doesn’t wait until PostgreSQL accepts connections. Fix both with:

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

No published port is needed for the API container to access `db:5432`. If you also want your locally running API to use this database, add `ports: ["5432:5432"]` to `db` and keep `localhost:5432` in your local development configuration.

The health check handles initial readiness; application-level connection retries help if the database restarts later.