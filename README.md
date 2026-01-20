# AggroConnect Backend

**Version**: 2.0.0  
**Type**: Agricultural Supply Chain & Farm Management API

## Overview

AggroConnect Backend is a comprehensive agricultural management platform designed to streamline farming operations, supply chain management, and service provider coordination. Built with modern technologies and scalable architecture.

## Features

### Core Capabilities
- 🌾 **Farm Management** - Complete farm and plot lifecycle management
- 📊 **Crop Tracking** - Real-time crop monitoring and yield analytics
- 🤝 **Service Provider Network** - Connect with agricultural service providers
- 📅 **Schedule Management** - Plan and track farming activities
- 📋 **Work Order System** - Manage tasks and assignments
- 🔍 **Farm Audit System** - Comprehensive farm inspection and compliance
- 💰 **Financial Tracking** - Monitor expenses and revenues
- 📱 **Multi-tenant Architecture** - Support for multiple organizations

### Technical Features
- RESTful API with OpenAPI documentation
- JWT-based authentication
- Role-based access control (RBAC)
- Multi-language support (English, Tamil, Malayalam)
- Geospatial data support with PostGIS
- Real-time notifications
- File upload and management
- Video consultation integration

## Technology Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15 with PostGIS
- **Cache**: Redis 7
- **Authentication**: JWT tokens
- **Documentation**: Swagger UI / ReDoc
- **Deployment**: Docker & Docker Compose

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ with PostGIS (if not using Docker)

### Running with Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd aggroconnect-backend

# Start all services
docker compose up -d

# View logs
docker compose logs -f web

# Stop services
docker compose down
```

### Access Points

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **API Base**: http://localhost:8000/api/v1

## Project Structure

```
aggroconnect-backend/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Core configuration
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── main.py           # Application entry point
├── docker-compose.yml    # Docker services
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## API Modules

### Authentication & Users
- User registration and login
- JWT token management
- Password management
- Organization switching

### Organization Management
- Multi-tenant organization support
- Member management
- Role assignments
- Organization approval workflow

### Farm Operations
- Farm CRUD operations
- Plot management
- Crop lifecycle tracking
- Yield recording
- Photo documentation

### Service Provider Network
- FSP service listings
- Marketplace browsing
- Service booking
- Document management

### Work Management
- Work order creation
- Schedule templates
- Task actuals
- Change log tracking

### Farm Audit
- Audit templates
- Parameter management
- Response collection
- Report generation

### Financial Management
- Category management
- Transaction tracking
- Budget monitoring

## Configuration

Key environment variables (create `.env` file):

```bash
# Application
APP_NAME=AggroConnect Backend
APP_VERSION=2.0.0
ENVIRONMENT=development

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/aggroconnect_db

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Development

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

## API Authentication

All protected endpoints require JWT authentication:

```bash
# Login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Use token in requests
curl -X GET http://localhost:8000/api/v1/farms/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Deployment

### Docker Production

```bash
# Build production image
docker build -t aggroconnect-backend:latest .

# Run with production settings
docker compose -f docker-compose.prod.yml up -d
```

### Environment-Specific Configs

- Development: `docker-compose.yml`
- Production: `docker-compose.prod.yml`
- Testing: `docker-compose.test.yml`

## Support & Documentation

- **API Docs**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Health Status**: http://localhost:8000/health

## License

Proprietary - All rights reserved

## Version History

### v2.0.0 (Current)
- Complete platform rewrite
- Multi-tenant architecture
- Enhanced farm audit system
- FSP marketplace integration
- Video consultation support

---

**Built with ❤️ for the agricultural community**
