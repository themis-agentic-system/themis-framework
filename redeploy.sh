#!/bin/bash
# Redeploy Themis with updated code
# This script stops the old containers, rebuilds with new code, and restarts

set -e

echo "================================"
echo "Themis Redeployment Script"
echo "================================"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH"
    exit 1
fi

# Check if docker-compose or docker compose is available
COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "ERROR: Neither docker-compose nor 'docker compose' is available"
    exit 1
fi

echo "Using Docker Compose command: $COMPOSE_CMD"
echo ""

# Step 1: Show current status
echo "Step 1: Current deployment status"
echo "-----------------------------------"
$COMPOSE_CMD ps
echo ""

# Step 2: Stop and remove old containers
echo "Step 2: Stopping old containers..."
echo "-----------------------------------"
$COMPOSE_CMD down
echo "✓ Old containers stopped"
echo ""

# Step 3: Pull latest code (if in a git repo)
if [ -d .git ]; then
    echo "Step 3: Pulling latest code..."
    echo "-----------------------------------"
    git pull origin $(git branch --show-current)
    echo "✓ Code updated"
    echo ""
else
    echo "Step 3: Skipping git pull (not a git repo)"
    echo ""
fi

# Step 4: Rebuild Docker image with new code
echo "Step 4: Rebuilding Docker images..."
echo "-----------------------------------"
$COMPOSE_CMD build --no-cache api
echo "✓ Docker images rebuilt"
echo ""

# Step 5: Start services
echo "Step 5: Starting services..."
echo "-----------------------------------"
$COMPOSE_CMD up -d
echo "✓ Services started"
echo ""

# Step 6: Wait for services to be healthy
echo "Step 6: Waiting for services to be healthy..."
echo "-----------------------------------"
sleep 5

# Check API health
MAX_RETRIES=12
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ API is healthy!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Waiting for API... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 5
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "⚠ API health check timeout. Check logs with: $COMPOSE_CMD logs -f themis-api"
fi
echo ""

# Step 7: Show deployment status
echo "Step 7: Final deployment status"
echo "-----------------------------------"
$COMPOSE_CMD ps
echo ""

# Step 8: Show service URLs
echo "================================"
echo "Deployment Complete!"
echo "================================"
echo ""
echo "Access your services:"
echo "  • Themis API: http://localhost:8000/docs"
echo "  • Health Check: http://localhost:8000/health"
echo "  • Metrics: http://localhost:8000/metrics"
echo ""
echo "View logs:"
echo "  $COMPOSE_CMD logs -f themis-api"
echo ""
echo "Run tests in container:"
echo "  $COMPOSE_CMD exec themis-api pytest tests/ -v"
echo ""
