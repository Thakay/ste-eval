Inside the API container, `localhost` means **the API container itself**. Postgres is in another container, reachable by its Compose service name: **`db`**. Change the URL to `postgres://app:secret@db:5432/app`.

There is also a startup race: plain `depends_on` starts the database container first but does not wait for Postgres to accept connections. Add a health check and wait for it:

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

Your local development setup can keep using `localhost`; Compose needs `db`. No published database port is required for communication between these services.

For resilience during database restarts, also add bounded connection retries in the API.

Godspeed, Spartan.