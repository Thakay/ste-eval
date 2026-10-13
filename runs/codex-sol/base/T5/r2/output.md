When you run locally, `localhost` points to your machine. Inside Compose, it points to the **API container itself**, where PostgreSQL is not running. Use the database service name, `db`, as the hostname.

There is also a startup race: `depends_on` starts the database container first but does not wait for PostgreSQL to accept connections. Fix both with:

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
      test: ["CMD-SHELL", "pg_isready -h 127.0.0.1 -U app -d app"]
      interval: 5s
      timeout: 5s
      retries: 10
```

The health check runs inside the database container, so its `127.0.0.1` is correct. Compose provides networking between services automatically; no published database port is needed for this connection.

For resilience after startup, also add database connection retries in the API.

Godspeed, Spartan.