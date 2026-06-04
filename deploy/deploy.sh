#!/usr/bin/env bash
set -euo pipefail

# Verify docker
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not installed or the daemon is not reachable."
  echo "Please install Docker Engine on Ubuntu:"
  echo "  sudo apt-get update"
  echo "  sudo apt-get install -y ca-certificates curl gnupg"
  echo "  sudo install -m 0755 -d /etc/apt/keyrings"
  echo "  sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc"
  echo "  sudo chmod a+r /etc/apt/keyrings/docker.asc"
  echo "  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null"
  echo "  sudo apt-get update"
  echo "  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin"
  exit 1
fi

# Check port 8723
if ss -ltn | grep -q ':8723 '; then
  echo "Error: Port 8723 is already in use."
  echo "Please stop the service using port 8723 or change the PORT environment variable."
  exit 1
fi

# Build and start
echo "Building and starting LunchTab..."
docker compose up -d --build

# Wait for health endpoint
echo "Waiting for application to be ready..."
for i in {1..30}; do
  if response=$(curl -s http://localhost:8723/health) && [[ "$response" == *'{"status":"ok"'* ]]; then
    echo "Application is ready!"
    echo "Live URL: http://localhost:8723"
    exit 0
  fi
  sleep 1
done

echo "Error: Application did not become ready within 30 seconds."
docker compose logs
exit 1
