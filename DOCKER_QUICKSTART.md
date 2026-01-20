# 🚀 Docker Quick Start Guide - Uzhathunai Farming Platform

## Prerequisites
- Docker installed on your system
- Docker Compose installed

## Setup Steps

### 1. Create .env File (IMPORTANT - Do this first!)
Create a `.env` file in the project root with the following content:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/uzhathunai_db_v2

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-change-this-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Settings
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
APP_NAME=Uzhathunai Farming Platform
API_V1_PREFIX=/api/v1

# CORS Settings
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Email Configuration (Optional)
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=noreply@uzhathunai.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=Uzhathunai Platform
```

### 2. Run the Application

**Single Command to Start Everything:**
```bash
docker-compose up --build
```

**Or run in detached mode (background):**
```bash
docker-compose up --build -d
```

### 3. Access the Application

Once running, you can access:
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Root Endpoint**: http://localhost:8000/

### 4. Stop the Application

```bash
docker-compose down
```

**To stop and remove all data (including database):**
```bash
docker-compose down -v
```

## What Docker Does Automatically

1. ✅ Starts PostgreSQL with PostGIS extension
2. ✅ Starts Redis for caching
3. ✅ Builds the FastAPI application
4. ✅ Waits for database to be ready
5. ✅ Runs all database migration scripts automatically:
   - `001_uzhathunai_ddl.sql` - Creates all tables
   - `002_create_refresh_tokens_table.sql` - Auth tables
   - `003_audit_module_changes.sql` - Audit system
   - `a01_uzhathunai_dml.sql` - Initial data
   - `a02_uzhathunai_dml_RBAC.sql` - Roles & permissions
   - `a03_uzhathunai_dml_input_items.sql` - Input items data
6. ✅ Starts the FastAPI server on port 8000

## Useful Docker Commands

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs db
docker-compose logs redis

# Follow logs (live)
docker-compose logs -f web
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild After Code Changes
```bash
docker-compose up --build
```

### Access Database Directly
```bash
docker exec -it farm_db psql -U postgres -d uzhathunai_db_v2
```

### Access Application Container
```bash
docker exec -it farm_backend bash
```

## Troubleshooting

### Port Already in Use
If port 8000, 5432, or 6379 is already in use, modify the ports in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001 (or any available port)
```

### Database Connection Issues
Check if the database container is running:
```bash
docker-compose ps
```

View database logs:
```bash
docker-compose logs db
```

### Reset Everything
```bash
docker-compose down -v
docker-compose up --build
```

## Architecture

The Docker setup includes:
- **web**: FastAPI application (backend)
- **db**: PostgreSQL 15 with PostGIS 3.3
- **redis**: Redis 7 (Alpine)

All connected via Docker network with persistent data storage for PostgreSQL.
