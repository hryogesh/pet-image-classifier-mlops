#!/usr/bin/env bash
set -euo pipefail

# Installs podman/buildah on EL-based systems via dnf and optionally runs a smoke test
# Usage: ./scripts/install_podman.sh [test]

if ! command -v dnf >/dev/null 2>&1; then
  echo "dnf not found; this script targets RHEL/CentOS/Fedora systems."
  exit 2
fi

if ! sudo -n true 2>/dev/null; then
  echo "sudo requires a password or is unavailable; aborting."
  exit 2
fi

echo "Installing podman and buildah..."
sudo dnf -y install podman buildah podman-docker || true

echo "Enabling podman socket/service (if available)..."
if systemctl --user status podman.socket >/dev/null 2>&1; then
  systemctl --user enable --now podman.socket || true
else
  sudo systemctl enable --now podman || true || true
fi

echo "Podman version:"
podman --version || true

echo "Done installing podman."

if [ "${1:-}" = "test" ]; then
  echo "Running smoke test: build image and run container with podman..."
  IMAGE_NAME="catsdogs:local"
  CONTAINER_NAME="catsdogs_test"
  HOST_PORT=8000
  SAMPLE=data/raw/PetImages/Cat/7157.jpg

  echo "Building image..."
  podman build -t "$IMAGE_NAME" .

  echo "Starting container..."
  podman run -d --name "$CONTAINER_NAME" -p ${HOST_PORT}:8000 -v "$(pwd)/models:/app/models" -e MODEL_PATH=/app/models/model.pt "$IMAGE_NAME"

  echo "Waiting for /health (30s timeout)..."
  for i in {1..30}; do
    if curl -sS "http://127.0.0.1:${HOST_PORT}/health" >/dev/null 2>&1; then
      echo "service up"; break
    fi
    sleep 1
    if [ "$i" -eq 30 ]; then
      echo "timed out waiting for service"; podman logs "$CONTAINER_NAME" || true; podman stop "$CONTAINER_NAME" || true; exit 3
    fi
  done

  echo "Health response:"
  curl -sS "http://127.0.0.1:${HOST_PORT}/health" || true

  if [ -f "$SAMPLE" ]; then
    echo "Predict response:"
    curl -sS -X POST "http://127.0.0.1:${HOST_PORT}/predict" -F "file=@${SAMPLE}" || true
  else
    echo "Sample image not found; skipping predict test"
  fi

  echo "Stopping container..."
  podman stop "$CONTAINER_NAME" || true
  podman rm "$CONTAINER_NAME" || true
  echo "Smoke test complete."
fi
