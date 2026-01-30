# Uzhathunai Farming Platform - Backend

This repository contains the backend API services for the Uzhathunai Farming Platform v2.0. It is built using Python (FastAPI), PostgreSQL (PostGIS), and Redis, containerized with Docker.

## Prerequisites

Before you begin, ensure you have the following installed on your Ubuntu system:

1.  **Git**: To clone the repository.
2.  **Docker**: To run the containers.
3.  **Docker Compose**: To orchestrate the services.

### Installing Docker & Docker Compose on Ubuntu

If you don't have them installed, run the following commands:

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Set up the repository
echo \
  "deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
sudo docker run hello-world

# Manage Docker as a non-root user (Optional but recommended)
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

## Getting Started

### 1. Clone the Repository

Clone the project to your local machine:

```bash
git clone https://github.com/omkar703/Uzhathunai_Farming_Platform-_OneAim--Backend.git
cd Uzhathunai_Farming_Platform-_OneAim--Backend
```

### 2. Configure Environment Variables

The project comes with a default `.env` file. You can modify it if needed, but the defaults should work for local development.

```bash
cat .env
```

### 3. Build and Run Services

Start the backend, database, and redis services:

```bash
# Build and start in detached mode
docker compose up --build -d

# Check the logs to ensure everything started correctly
docker compose logs -f backend
```

*Note: The backend service is named `aggroconnect_backend` in the container list.*

### 4. Seed the Database

Once the containers are up and running, you need to populate the database with initial data (Master Data, FSP, Farms, Templates).

Execute the seed scripts inside the backend container:

```bash
# 1. Seed Master Data (Parameters, Roles, Crops, etc.)
docker compose exec web python seed_master_data.py

# 2. Seed FSP and Farm Data (Organizations, Users, Plots)
docker compose exec web python seed_farm_fsp_full.py

# 3. Seed Templates (Audit Checklists)
docker compose exec web python seed_liomonk_templates.py
```

### 5. Access the Application

*   **API Documentation (Swagger UI):** Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.
*   **ReDoc:** Open [http://localhost:8000/redoc](http://localhost:8000/redoc).

### 6. Common Commands

```bash
# Stop all services
docker compose down

# Restart backend service only (useful after code changes)
docker compose restart web

# Access the database shell
docker compose exec db psql -U postgres -d farm_db
```

## Troubleshooting

*   **"no such service: aggroconnect_backend"**: When using `docker compose logs`, use the service name defined in `docker-compose.yml` (which is `web`), or use the container name with `docker logs aggroconnect_backend`.
*   **Database connection failed**: Ensure the `db` container is healthy. It may take a few seconds to initialize on the first run.
