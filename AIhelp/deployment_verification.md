# Deployment & Verification Guide

I successfully implemented an automated database initialization system. However, I was unable to verify it locally because the Docker daemon in this environment is currently unreachable.

The code is complete and ready for your AWS deployment.

## What has been done?

1.  **`scripts/init_db.py`**: A Python script that:

    - Waits for the database to be ready.
    - Checks if the schema exists. If not, runs `001_uzhathunai_ddl.sql`.
    - Checks if seed data exists. If not, runs `a01`, `a02`, `a03` DML scripts.
    - Checks if `Super Admin` user exists. If not, creates it with your specified credentials:
      - Email: `superadmin@uzhathunai.com`
      - Password: `SuperSecure@Admin123`

2.  **`scripts/entrypoint.sh`**: A wrapper script that runs `init_db.py` before starting the application server.

3.  **`Dockerfile`**: Updated to use `entrypoint.sh` as the container entrypoint.

## How to Verify on AWS

Since I couldn't run it locally, please perform the following steps on your AWS EC2 instance:

1.  **Pull the latest code**:

    ```bash
    git pull origin main
    ```

2.  **Rebuild the Backend Container**:

    ```bash
    docker compose up -d --build web
    ```

    _(The `--build` flag is critical to update the Docker image with the new entrypoint)_

3.  **Check Logs**:
    Watch the logs to see the initialization in action:

    ```bash
    docker compose logs -f web
    ```

    You should see output like:

    ```
    Starting Uzhathunai Backend Entrypoint...
    Running Database Initialization (init_db.py)...
    Waiting for database connection...
    ...
    Successfully executed 001_uzhathunai_ddl.sql
    ...
    Creating Super Admin user: superadmin@uzhathunai.com
    Super Admin created successfully...
    Initialization complete. Starting uvicorn...
    ```

4.  **Verify Super Admin Login**:
    Use Swagger (`/docs`) or Postman to login:
    - **Endpoint**: `POST /api/v1/auth/login`
    - **Email**: `superadmin@uzhathunai.com`
    - **Password**: `SuperSecure@Admin123`

This setup ensures that any fresh deployment (even if you wipe the DB volume) will automatically self-heal and re-initialize.
