---
description: Deploy Themis stack using Docker Compose
---

Deploy the full Themis stack with Docker:

**Pre-flight Checks:**
1. Verify `.env` file exists with required variables:
   - ANTHROPIC_API_KEY
   - THEMIS_API_KEY
   - POSTGRES_PASSWORD

2. Check Docker is running:
```bash
docker --version
docker-compose --version
```

**Deployment Steps:**

1. **Build and Start Services:**
```bash
docker-compose up -d
```

2. **Verify Services:**
```bash
docker-compose ps
docker-compose logs -f themis-api
```

3. **Run Health Checks:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

4. **Access Services:**
   - Themis API: http://localhost:8000/docs
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin)

5. **Run Tests in Container:**
```bash
docker-compose exec themis-api pytest tests/ -v
```

**Monitoring:**
- Check logs: `docker-compose logs -f`
- View metrics: http://localhost:9090
- Grafana dashboards: http://localhost:3000

**Shutdown:**
```bash
docker-compose down
# Or keep data: docker-compose down --volumes
```

If $ARGUMENTS is "status", show current deployment status.
If $ARGUMENTS is "logs", tail all service logs.
