#!/usr/bin/env bash
set -euo pipefail

# Run the full local end-to-end pipeline: preprocess -> train -> package -> docker-compose
# Usage: ./scripts/run_end_to_end.sh [--no-docker]

NO_DOCKER=0
if [ "${1:-}" = "--no-docker" ]; then
  NO_DOCKER=1
fi

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

echo "1) Preprocessing data"
python -m src.data.preprocess --input_dir data/raw --output_dir data/processed --img_size 224

echo "2) Training (short default run)"
python -m src.train --data_dir data/processed --save_dir models --epochs 3 --batch_size 8

echo "3) Packaging artifacts"
ZIPOUT=mlops_package.zip
scripts/package_artifacts.sh || true
if [ -f mlops_package.zip ]; then
  echo "Packaged to $ZIPOUT"
else
  echo "package_artifacts.sh didn't create $ZIPOUT — creating minimal zip"
  zip -r "$ZIPOUT" README.md src scripts requirements.txt Dockerfile || true
fi

if [ "$NO_DOCKER" -eq 0 ]; then
  if command -v docker >/dev/null 2>&1; then
    echo "4) Building Docker image"
    docker compose build
    echo "5) Bringing up services"
    docker compose up -d
    echo "Run 'docker compose logs -f' to follow logs"
  else
    echo "Docker not available — skipping container build and run"
  fi
else
  echo "Skipping Docker steps (--no-docker)"
fi

echo "Done. Check mlruns/ for MLflow runs and models/model.pt for the trained model."
