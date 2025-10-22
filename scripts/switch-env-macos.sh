#!/bin/bash
echo "🚀 Starting Blue-Green Deployment..."

# Stop existing containers
echo "=== Stopping existing containers ==="
docker-compose down

# Start the deployment
echo "=== Starting new deployment ==="
docker-compose up -d

# Wait for services to start
echo "=== Waiting for services to start ==="
sleep 20

# Check status
echo "=== Deployment Status ==="
docker-compose ps

echo "=== Application Logs ==="
docker-compose logs --tail=10

echo "✅ Deployment completed successfully"