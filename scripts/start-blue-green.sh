#!/bin/bash
echo "🚀 Starting Blue/Green deployment environment..."

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Start all services
echo "🐳 Starting all services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

# Initial traffic to blue using macOS script
echo "🔀 Setting initial traffic to BLUE..."
./scripts/switch-to-blue-macos.sh

echo "✅ Blue/Green environment ready!"
echo "🌐 Access your app at: http://localhost:8080"
echo "🔵 Blue direct: http://localhost:5002/health"
echo "🟢 Green direct: http://localhost:5003/health"