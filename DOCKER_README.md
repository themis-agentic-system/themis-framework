# Docker Deployment - Quick Reference

## One-Command Setup

```bash
# 1. Configure environment
cp .env.docker .env
nano .env  # Set THEMIS_API_KEY, ANTHROPIC_API_KEY, POSTGRES_PASSWORD

# 2. Start everything
docker-compose up -d

# 3. Check health
curl http://localhost:8000/health
```

## Common Commands

```bash
# Start services
docker-compose up -d

# Start with monitoring (Prometheus + Grafana)
docker-compose --profile monitoring up -d

# View logs
docker-compose logs -f api

# Restart API
docker-compose restart api

# Stop everything
docker-compose down

# Stop and delete data (WARNING!)
docker-compose down -v

# Check service status
docker-compose ps

# Execute shell in container
docker-compose exec api bash
```

## Service Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| API | http://localhost:8000 | Themis Orchestrator |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Health Check | http://localhost:8000/health | Service health status |
| Metrics | http://localhost:8000/metrics | Prometheus metrics |
| PostgreSQL | localhost:5432 | Database (internal) |
| Prometheus | http://localhost:9090 | Metrics (with --profile monitoring) |
| Grafana | http://localhost:3000 | Dashboards (with --profile monitoring) |

## Environment Variables

Required in `.env`:

```bash
# API Authentication
THEMIS_API_KEY=your-secret-key-here

# LLM Provider
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Database
POSTGRES_PASSWORD=secure-password

# Optional
LOG_LEVEL=INFO
CACHE_TTL_SECONDS=60
GRAFANA_PASSWORD=admin
```

## Database Management

```bash
# Backup
docker-compose exec postgres pg_dump -U themis themis > backup.sql

# Restore
docker-compose exec -T postgres psql -U themis themis < backup.sql

# Access psql
docker-compose exec postgres psql -U themis -d themis

# View tables
docker-compose exec postgres psql -U themis -d themis -c "\dt"
```

## Troubleshooting

**Container won't start:**
```bash
docker-compose logs api
docker-compose build --no-cache api
```

**Database connection errors:**
```bash
docker-compose ps postgres
docker-compose exec postgres pg_isready -U themis
```

**Check disk space:**
```bash
docker system df
docker system prune -a  # Clean up
```

**Reset everything:**
```bash
docker-compose down -v
docker system prune -a
docker-compose up -d
```

## For Full Documentation

See `DEPLOYMENT_GUIDE.md` for complete deployment instructions, monitoring setup, production checklist, and troubleshooting.
