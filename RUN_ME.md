# ⚡ QUICK START - Just Run This!

## The Single Command You Need:

```bash
docker-compose up --build
```

That's it! This command will:
- ✅ Start PostgreSQL database with PostGIS
- ✅ Start Redis cache
- ✅ Build your FastAPI application
- ✅ Run all database migrations automatically
- ✅ Start the server on http://localhost:8000

## Access Your Application:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## To Stop:
```bash
docker-compose down
```

## Run in Background (Detached Mode):
```bash
docker-compose up --build -d
```

## View Logs While Running in Background:
```bash
docker-compose logs -f web
```

---

**For detailed documentation, see `DOCKER_QUICKSTART.md`**
