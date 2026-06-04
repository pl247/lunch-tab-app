#!/usr/bin/env bash
set -euo pipefail

echo "Stopping and removing LunchTab containers..."
docker compose down

echo "To also remove the stored data volume, run: ./deploy/cleanup.sh -v"
echo "Or manually: docker compose down -v"

# If -v flag passed, remove volume
if [[ "${1:-}" == "-v" ]]; then
  echo "Removing data volume..."
  docker compose down -v
  echo "Data volume removed."
fi
