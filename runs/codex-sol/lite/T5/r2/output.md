`localhost` points to the API container when the API runs in Compose. With `npm run dev`, it points to your machine. In Compose, the API must connect to `db:5432`, using the PostgreSQL service name.

Your current `depends_on` controls startup order. It does not wait for PostgreSQL to accept connections.

1. Replace your configuration with this:

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

2. Apply the configuration:

   ```bash
   docker compose up --build
   ```

The host change fixes the reported connection failure. The health check prevents the API from starting before PostgreSQL is ready.

Godspeed, Spartan.