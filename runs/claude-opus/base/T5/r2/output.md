**Inside a container, `localhost` means that container itself, not your machine.** The API is looking for Postgres inside its own container, finds nothing on 5432, and gets `ECONNREFUSED`. With `npm run dev` it works because Postgres really is on your machine's localhost. In compose, each service is reachable by its **service name** on the shared network, so the host should be `db`.

There's also a second issue waiting behind the first: `depends_on: [db]` only waits for the db container to *start*, not for Postgres to *accept connections*. Your API can still lose that race on a fresh volume, where first-time init takes a few seconds. A healthcheck fixes it.

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
      test: ["CMD-SHELL", "pg_isready -h localhost -U app -d app"]
      interval: 2s
      timeout: 3s
      retries: 15
```

Notes:
- `-h localhost` makes the check use TCP. During first-time init, Postgres runs a temporary server that accepts only socket connections, so a socket-based check can report "ready" too early.
- If you also want `npm run dev` on your machine to use this same container, add `ports: ["5432:5432"]` under `db`. Keep `localhost` in your local `.env` and `db` in compose.

Hold the line, connection warden.