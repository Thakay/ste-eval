## Cause

The `api` container uses `localhost` in `DATABASE_URL`. In a container, `localhost` is that container. It is not your computer and it is not the `db` container. PostgreSQL does not operate in the `api` container, so the connection to port 5432 is refused.

With `npm run dev`, the API operates directly on your computer. Your local PostgreSQL is on the same computer, so `localhost` is correct there.

## Fix

1. Change the host in `DATABASE_URL` from `localhost` to `db`. Compose gives each service a network name that is the same as the service name.
2. Add a health check to the `db` service. `depends_on` starts `db` first, but it does not make sure that PostgreSQL is ready.
3. Set `condition: service_healthy` on the dependency. Then Compose starts `api` only after PostgreSQL is ready.

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
      interval: 2s
      timeout: 5s
      retries: 10
```

4. Run `docker compose up` again. You do not have to rebuild the image, because `DATABASE_URL` is set when the container starts.

## Note

Step 1 is the primary fix. Step 2 and step 3 prevent a second error: the API can start before PostgreSQL is ready.