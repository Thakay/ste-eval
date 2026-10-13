Inside the API container, `localhost` refers to that container. PostgreSQL runs in the `db` container, so the API must connect to `db:5432`.

There is also a startup issue. Your current `depends_on` setting starts `db` first, but does not wait until PostgreSQL accepts connections.

Use this configuration to fix both:

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
      test: ["CMD-SHELL", "pg_isready -h 127.0.0.1 -U app -d app"]
      interval: 5s
      timeout: 5s
      retries: 10
```

Then run `docker compose up --build` to recreate the API with the corrected configuration.

Godspeed, Spartan.