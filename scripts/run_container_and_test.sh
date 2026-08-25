#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="catsdogs:local"
CONTAINER_NAME="catsdogs_test"
SAMPLE="${1:-data/raw/PetImages/Cat/7157.jpg}"
HOST_PORT="8000"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found; install Docker or run this on a machine with Docker."
  exit 2
fi

echo "Building Docker image $IMAGE_NAME..."
docker build -t "$IMAGE_NAME" .

echo "Starting container $CONTAINER_NAME..."
docker run --rm -d --name "$CONTAINER_NAME" -p ${HOST_PORT}:8000 -v "$(pwd)/models:/app/models" "$IMAGE_NAME"

# wait for health endpoint
echo "Waiting for /health to become available (30s timeout)..."
for i in {1..30}; do
  if curl -sS "http://127.0.0.1:${HOST_PORT}/health" >/dev/null 2>&1; then
    echo "Service is up"
    break
  fi
  sleep 1
  if [ "$i" -eq 30 ]; then
    echo "Timed out waiting for service; container logs:"
    docker logs "$CONTAINER_NAME" || true
    docker stop "$CONTAINER_NAME" || true
    exit 3
  fi
done

echo "Health check output:"
curl -sS "http://127.0.0.1:${HOST_PORT}/health" || true

if [ ! -f "$SAMPLE" ]; then
  echo "Sample file $SAMPLE not found; skipping predict test"
else
  echo "Running predict with sample $SAMPLE"
  curl -sS -X POST "http://127.0.0.1:${HOST_PORT}/predict" -F "file=@${SAMPLE}" || true
fi

echo "Stopping container..."
docker stop "$CONTAINER_NAME" >/dev/null || true

echo "Done."
