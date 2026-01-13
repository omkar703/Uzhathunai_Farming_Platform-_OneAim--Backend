# Uzhathunai Farming Platform v2.0 - Backend

FastAPI-based backend for the Uzhathunai multi-tenant farming and FSP management platform.

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 14+ with PostGIS extension
- Redis 6+
- Virtual environment tool (venv or virtualenv)

### Database Setup

1. Create the database:
```sql
CREATE DATABASE uzhathunai_db_v2;
```

2. Enable required extensions:
```sql
\c uzhathunai_db_v2
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

3. Run the DDL script:
```bash
psql -U postgres -d uzhathunai_db_v2 -f db_scripts/001_uzhathunai_ddl.sql
```

4. (Optional) Run the DML script for sample data:
```bash
psql -U postgres -d uzhathunai_db_v2 -f db_scripts/a01_uzhathunai_dml.sql
```

### Backend Setup

1. Create and activate virtual environment:
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

4. Update `.env` with your configuration:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/uzhathunai_db_v2
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
```

5. Run the application:
```bash
# Development mode with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py directly
python app/main.py
```

6. Access the API:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Root: http://localhost:8000/

## Project Structure

```
backend/
├── app/
│   ├── core/              # Core infrastructure
│   │   ├── config.py      # Configuration settings
│   │   ├── database.py    # Database connection
│   │   ├── logging.py     # Structured logging
│   │   ├── exceptions.py  # Custom exceptions
│   │   ├── security.py    # Auth & security utilities
│   │   └── cache.py       # Redis caching
│   ├── models/            # SQLAlchemy models (to be added)
│   ├── schemas/           # Pydantic schemas (to be added)
│   ├── services/          # Business logic (to be added)
│   ├── api/               # API routes (to be added)
│   │   └── v1/
│   └── main.py            # FastAPI application
├── db_scripts/            # Database scripts
│   ├── 001_uzhathunai_ddl.sql
│   └── a01_uzhathunai_dml.sql
├── tests/                 # Test files (to be added)
├── .env.example           # Environment variables template
├── .gitignore
├── requirements.txt       # Python dependencies
└── README.md
```

## Development Workflow

### Vertical Slice Approach

Build each feature end-to-end before moving to the next:

1. **Phase 1: Foundation** ✅ (Current)
   - Project setup
   - Core infrastructure
   - Database connection
   - Health check endpoint

2. **Phase 2: Authentication & Authorization** (Next)
   - User registration/login
   - JWT tokens
   - RBAC system

3. **Phase 3+: Feature Development**
   - Organizations
   - Farms & Plots
   - Crops
   - Schedules
   - FSP Marketplace
   - Audits
   - etc.

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## Key Features

- **Multi-tenant Architecture**: Row-level security with organization isolation
- **Comprehensive RBAC**: Roles, permissions, and org-level overrides
- **Offline Sync Support**: (Phase 2) Mobile offline-first capabilities
- **Multilingual**: Full translation support for reference data
- **Observability**: Structured logging, metrics, and monitoring
- **Feature Flags**: Gradual rollout and A/B testing support

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (generate with `openssl rand -hex 32`)
- `REDIS_URL`: Redis connection string
- `DEBUG`: Enable debug mode (True/False)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -U postgres -d uzhathunai_db_v2 -c "SELECT version();"

# Check if PostGIS is installed
psql -U postgres -d uzhathunai_db_v2 -c "SELECT PostGIS_version();"
```

### Redis Connection Issues

```bash
# Test Redis connection
redis-cli ping

# Should return: PONG
```

### Import Errors

```bash
# Ensure you're in the backend directory
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. ✅ Project setup complete
2. ⏳ Implement authentication endpoints
3. ⏳ Implement organization management
4. ⏳ Implement farm management
5. ⏳ Continue with vertical slices...

## Reference

- Specification: `docs/uzhathunai_ver2.0.md`
- Database Design: `db_design_evolution_reference/`
- v1.0 Reference: `old_app_reference/backend/`

## Support

For issues or questions, refer to the comprehensive development guide in `docs/uzhathunai_ver2.0.md`.
