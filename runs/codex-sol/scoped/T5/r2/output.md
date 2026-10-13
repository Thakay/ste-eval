`localhost` means the machine or container running the API. With `npm run dev`, it points to your machine. In Compose, it points to the API container, which has no PostgreSQL server.

The database address must use the Compose service name: `db:5432`.

There is also a startup timing issue. Plain `depends_on` starts the database container first, but does not wait until PostgreSQL accepts connections.

This configuration fixes both issues:

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
      timeout: 5s
      retries: 10
```

Compose resolves `db` on the shared network. You do not need to publish port `5432` for the API to reach it.

Connection retries in the API also help it recover from later database restarts.

Godspeed, Spartan.