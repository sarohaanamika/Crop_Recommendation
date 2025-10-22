#!/bin/bash
echo "🔄 Switching traffic to GREEN environment"

# Copy green template to active config
cp nginx.green.conf nginx.conf

# Copy to nginx container
docker cp nginx.conf nginx-proxy:/etc/nginx/nginx.conf

# Reload nginx
docker exec nginx-proxy nginx -s reload

echo "✅ Traffic switched to GREEN"
echo "🌐 Access your app at: http://localhost:8080"