#!/bin/bash
echo "🔄 Switching traffic to BLUE environment"

# Copy blue template to active config
cp nginx.blue.conf nginx.conf

# Copy to nginx container
docker cp nginx.conf nginx-proxy:/etc/nginx/nginx.conf

# Reload nginx
docker exec nginx-proxy nginx -s reload

echo "✅ Traffic switched to BLUE"
echo "🌐 Access your app at: http://localhost:8080"